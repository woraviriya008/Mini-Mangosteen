/**
 * Mangosteen Ripeness Classifier with High-Res (240x240) Wi-Fi Dashboard
 * Board: LilyGO T-SIMCAM (ESP32-S3)
 * Access: Connect Wi-Fi "Mangosteen-AI" (pass: 12345678), browse http://192.168.4.1
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include "esp_camera.h"
#include "img_converters.h"

// TensorFlow Lite Micro Headers
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "mangosteen_model_data.h"

// ==============================================================================
// 1. PIN CONFIGURATION FOR LILYGO T-SIMCAM (ESP32-S3)
// ==============================================================================
#define PWR_ON_PIN       1

#define PWDN_GPIO_NUM   -1
#define RESET_GPIO_NUM  -1
#define XCLK_GPIO_NUM   14
#define SIOD_GPIO_NUM    4
#define SIOC_GPIO_NUM    5

#define Y9_GPIO_NUM     15
#define Y8_GPIO_NUM     16
#define Y7_GPIO_NUM     17
#define Y6_GPIO_NUM     12
#define Y5_GPIO_NUM     10
#define Y4_GPIO_NUM      8
#define Y3_GPIO_NUM      9
#define Y2_GPIO_NUM     11
#define VSYNC_GPIO_NUM   6
#define HREF_GPIO_NUM    7
#define PCLK_GPIO_NUM   13

// ==============================================================================
// 2. MODEL GLOBALS
// ==============================================================================
static const char *kClassNames[3] = {
    "overripe",  // Class 0
    "ripe",      // Class 1
    "unripe"     // Class 2
};

constexpr size_t kTensorArenaSize = 2048 * 1024;
uint8_t *tensor_arena = nullptr;

const tflite::Model* model = nullptr;
tflite::MicroInterpreter* interpreter = nullptr;
TfLiteTensor* input = nullptr;
TfLiteTensor* output = nullptr;

// ==============================================================================
// 3. WEB SERVER & SOFTAP CONFIGURATION
// ==============================================================================
const char *ap_ssid = "Mangosteen-AI";
const char *ap_pass = "12345678";
WebServer server(80);

// Embedded Web Dashboard (HTML5 + CSS3 + Vanilla JS)
static const char PROGMEM INDEX_HTML[] = R"rawliteral(
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>🍃 Mangosteen AI Inspector</title>
  <style>
    :root {
      --bg: #0a0e17;
      --card: #131b2e;
      --card-inner: #0d1424;
      --border: #22304d;
      --border-light: rgba(56, 189, 248, 0.25);
      --text: #f8fafc;
      --subtext: #94a3b8;
      --primary: #38bdf8;
      --primary-gradient: linear-gradient(135deg, #38bdf8, #0284c7);
      --ripe: #10b981;
      --unripe: #f59e0b;
      --overripe: #ef4444;
      --radius: 16px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans Thai', sans-serif; -webkit-tap-highlight-color: transparent; }
    body { background: var(--bg); color: var(--text); display: flex; flex-direction: column; align-items: center; min-height: 100vh; min-height: 100dvh; padding: 16px 18px 32px; }
    
    /* Header */
    .header { text-align: center; margin-bottom: 18px; width: 100%; max-width: 940px; }
    .header h1 { font-size: 1.45rem; font-weight: 800; display: flex; align-items: center; justify-content: center; gap: 10px; color: #fff; letter-spacing: -0.2px; }
    .header p { font-size: 0.82rem; color: var(--subtext); margin-top: 3px; }
    
    /* Balanced 2-Column Dashboard Layout */
    .dashboard-layout {
      width: 100%;
      max-width: 940px;
      display: grid;
      grid-template-columns: 1fr 1.15fr;
      gap: 20px;
      align-items: start;
    }
    
    /* Mobile Responsive Fallback */
    @media (max-width: 768px) {
      .dashboard-layout {
        grid-template-columns: 1fr;
        gap: 14px;
      }
    }
    
    /* Columns */
    .col-prediction, .col-camera {
      display: flex;
      flex-direction: column;
      gap: 14px;
      width: 100%;
    }
    
    /* Common Cards */
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      box-shadow: 0 8px 24px -6px rgba(0,0,0,0.45);
    }
    .card-title {
      font-size: 0.96rem;
      font-weight: 800;
      color: var(--primary);
      display: flex;
      align-items: center;
      gap: 8px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 10px;
      letter-spacing: 0.2px;
    }

    /* Left Column: Prediction Results */
    .winner-box {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: var(--card-inner);
      padding: 12px 16px;
      border-radius: 12px;
      border: 1px solid var(--border);
    }
    .badge {
      font-size: 1.15rem;
      font-weight: 800;
      padding: 6px 14px;
      border-radius: 10px;
      background: #1e293b;
      color: #fff;
      letter-spacing: 0.2px;
    }
    .badge.ripe { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }
    .badge.unripe { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }
    .badge.overripe { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
    .badge.thinking { background: rgba(99, 102, 241, 0.2); color: #a5b4fc; border: 1px solid #6366f1; animation: pulse 0.7s infinite alternate; }
    @keyframes pulse { from { opacity: 0.6; } to { opacity: 1; } }
    .conf-val { font-size: 1.5rem; font-weight: 900; color: var(--primary); font-family: monospace; }

    /* 3 Probability Gauge Bars */
    .bars-container { display: flex; flex-direction: column; gap: 10px; }
    .bar-row {
      background: var(--card-inner);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 10px 12px;
      transition: all 0.25s ease;
    }
    .bar-row.winner {
      border-color: var(--primary);
      background: rgba(56, 189, 248, 0.08);
      box-shadow: 0 0 14px rgba(56, 189, 248, 0.25);
      transform: scale(1.01);
    }
    .bar-meta { display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; font-weight: 700; margin-bottom: 6px; }
    .bar-name { display: flex; align-items: center; gap: 6px; }
    .bar-track { width: 100%; height: 10px; background: #1e293b; border-radius: 6px; overflow: hidden; }
    .bar-val { height: 100%; width: 0%; border-radius: 6px; transition: width 0.35s ease; }
    .bar-overripe .bar-val { background: linear-gradient(90deg, #f87171, #ef4444); }
    .bar-ripe .bar-val { background: linear-gradient(90deg, #34d399, #10b981); }
    .bar-unripe .bar-val { background: linear-gradient(90deg, #fbbf24, #f59e0b); }

    /* Latency & Stats Chips */
    .stats-row { display: flex; gap: 10px; }
    .stat-chip { flex: 1; background: var(--card-inner); border: 1px solid var(--border); border-radius: 10px; padding: 8px 12px; display: flex; flex-direction: column; }
    .stat-label { font-size: 0.65rem; color: var(--subtext); text-transform: uppercase; font-weight: 700; letter-spacing: 0.4px; }
    .stat-num { font-size: 0.98rem; font-weight: 800; font-family: monospace; color: #fff; margin-top: 2px; }
    .stat-num.highlight { color: var(--primary); }

    .tip-box {
      background: rgba(56, 189, 248, 0.05);
      border: 1px dashed var(--border-light);
      border-radius: 12px;
      padding: 10px 12px;
      font-size: 0.78rem;
      color: var(--subtext);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    /* Right Column: Camera & Photo View */
    .camera-wrapper {
      position: relative;
      width: 100%;
      max-width: 320px;
      aspect-ratio: 1/1;
      margin: 0 auto;
      background: #000;
      border-radius: 18px;
      overflow: hidden;
      border: 2px solid var(--border);
      box-shadow: 0 12px 30px -8px rgba(0,0,0,0.7);
    }
    #cam-canvas { width: 100%; height: 100%; object-fit: cover; display: block; }
    .reticle {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 72%;
      height: 72%;
      border: 2px dashed rgba(56, 189, 248, 0.85);
      border-radius: 20px;
      pointer-events: none;
      transition: opacity 0.2s;
    }
    .reticle-label {
      position: absolute;
      bottom: 8px;
      width: 100%;
      text-align: center;
      font-size: 0.72rem;
      color: var(--primary);
      font-weight: 600;
      text-shadow: 0 1px 4px rgba(0,0,0,0.9);
    }

    /* Buttons */
    .btn-group { width: 100%; display: flex; flex-direction: column; gap: 8px; }
    .btn-row { width: 100%; display: flex; gap: 8px; }
    button {
      flex: 1;
      min-height: 48px;
      padding: 12px 14px;
      border-radius: 12px;
      border: none;
      font-size: 0.98rem;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.18s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }
    .btn-main { background: var(--primary-gradient); color: #0f172a; box-shadow: 0 4px 14px rgba(56, 189, 248, 0.35); }
    .btn-main:active { transform: scale(0.98); opacity: 0.9; }
    .btn-secondary { background: #1e293b; color: var(--text); border: 1px solid var(--border); }
    .btn-secondary:active { background: #334155; }
    .btn-save { background: #065f46; color: #a7f3d0; border: 1px solid #059669; }
    .btn-save:active { background: #047857; }
    .btn-settings-toggle { background: transparent; color: var(--subtext); border: 1px dashed var(--border); min-height: 38px; font-size: 0.85rem; font-weight: 600; }
    .btn-settings-toggle:hover { color: var(--text); border-color: var(--subtext); }

    /* Switch Rows */
    .toggle-row {
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 14px;
      background: var(--card-inner);
      border: 1px solid var(--border);
      border-radius: 12px;
      font-size: 0.88rem;
      font-weight: 600;
    }
    .switch { position: relative; display: inline-block; width: 46px; height: 26px; }
    .switch input { opacity: 0; width: 0; height: 0; }
    .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #334155; transition: .25s; border-radius: 26px; }
    .slider:before { position: absolute; content: ""; height: 20px; width: 20px; left: 3px; bottom: 3px; background-color: white; transition: .25s; border-radius: 50%; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
    input:checked + .slider { background-color: var(--primary); }
    input:checked + .slider:before { transform: translateX(20px); }

    /* Settings Panel */
    .settings-panel {
      width: 100%;
      background: var(--card-inner);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px;
      display: none;
      flex-direction: column;
      gap: 12px;
      animation: slideDown 0.25s ease;
    }
    @keyframes slideDown { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: translateY(0); } }
    .settings-panel.open { display: flex; }
    .settings-title { font-size: 0.9rem; font-weight: 700; color: var(--primary); display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
    .ctrl-item { display: flex; flex-direction: column; gap: 4px; }
    .ctrl-header { display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--subtext); font-weight: 600; }
    .ctrl-slider { width: 100%; accent-color: var(--primary); height: 6px; border-radius: 3px; cursor: pointer; }
    .ctrl-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
    .ctrl-chip { display: flex; justify-content: space-between; align-items: center; background: var(--bg); padding: 8px 10px; border-radius: 8px; border: 1px solid var(--border); font-size: 0.78rem; font-weight: 600; }

    .fps-meta { font-size: 0.75rem; color: var(--subtext); text-align: center; font-family: monospace; }
    .footer { margin-top: 18px; font-size: 0.75rem; color: #64748b; text-align: center; width: 100%; max-width: 940px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>🍃 Mangosteen AI Inspector</h1>
    <p>ESP32-S3 Edge AI | Separable CNN (96x96 INT8 Dual-Pane Dashboard)</p>
  </div>

  <div class="dashboard-layout">
    <!-- ======================================================== -->
    <!-- LEFT COLUMN: รูปที่ถ่าย & กล้อง (Camera View & Controls)  -->
    <!-- ======================================================== -->
    <div class="col-camera">
      <div class="card">
        <div class="card-title">
          <span>📷</span> ภาพถ่ายจากกล้อง (Camera Viewport)
        </div>

        <!-- Camera Viewport Canvas -->
        <div class="camera-wrapper">
          <canvas id="cam-canvas" width="240" height="240"></canvas>
          <div class="reticle" id="reticle">
            <div class="reticle-label">จัดตำแหน่งมังคุดให้อยู่ในกรอบ</div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="btn-group">
          <button class="btn-main" id="btn-action" onclick="onActionClick()">
            <span>📸</span> ถ่ายภาพ & Predict
          </button>

          <div class="btn-row" id="row-post-snap" style="display:none;">
            <button class="btn-secondary" onclick="onResumeClick()">
              <span>🔄</span> ดูภาพสด (Live)
            </button>
            <button class="btn-save" onclick="onSaveClick()">
              <span>💾</span> บันทึกรูปภาพ
            </button>
          </div>

          <button class="btn-settings-toggle" onclick="toggleSettings()">
            <span>⚙️</span> ตั้งค่ากล้อง (Camera Settings)
          </button>
        </div>

        <!-- Auto-AI Toggle -->
        <div class="toggle-row">
          <span>⚡ วิเคราะห์สดต่อเนื่อง (Auto-AI)</span>
          <label class="switch">
            <input type="checkbox" id="chk-auto" onchange="onAutoToggle()">
            <span class="slider"></span>
          </label>
        </div>

        <!-- Camera Settings Panel -->
        <div class="settings-panel" id="settings-panel">
          <div class="settings-title">
            <span>⚙️ ปรับแต่งเซนเซอร์กล้อง (OV2640)</span>
            <button style="flex:none; padding:3px 8px; min-height:26px; font-size:0.75rem;" class="btn-secondary" onclick="onResetCamera()">🔁 คืนค่า</button>
          </div>

          <div class="ctrl-item">
            <div class="ctrl-header">
              <span>☀️ ความสว่าง (Brightness)</span>
              <span id="val-bright">0</span>
            </div>
            <input type="range" min="-2" max="2" value="0" class="ctrl-slider" id="sld-bright" onchange="onCamChange('brightness', this.value, 'val-bright')">
          </div>

          <div class="ctrl-item">
            <div class="ctrl-header">
              <span>🌓 คอนทราสต์ (Contrast)</span>
              <span id="val-contrast">1</span>
            </div>
            <input type="range" min="-2" max="2" value="1" class="ctrl-slider" id="sld-contrast" onchange="onCamChange('contrast', this.value, 'val-contrast')">
          </div>

          <div class="ctrl-item">
            <div class="ctrl-header">
              <span>🎨 ความอิ่มสี (Saturation)</span>
              <span id="val-satur">1</span>
            </div>
            <input type="range" min="-2" max="2" value="1" class="ctrl-slider" id="sld-satur" onchange="onCamChange('saturation', this.value, 'val-satur')">
          </div>

          <div class="ctrl-grid">
            <div class="ctrl-chip">
              <span>🔄 กลับหัว (V-Flip)</span>
              <label class="switch" style="width:36px; height:20px;">
                <input type="checkbox" id="chk-vflip" onchange="onCamChange('vflip', this.checked ? 1 : 0)">
                <span class="slider" style="border-radius:20px;"></span>
              </label>
            </div>
            <div class="ctrl-chip">
              <span>🪞 ซ้ายขวา (Mirror)</span>
              <label class="switch" style="width:36px; height:20px;">
                <input type="checkbox" id="chk-hmirror" onchange="onCamChange('hmirror', this.checked ? 1 : 0)">
                <span class="slider" style="border-radius:20px;"></span>
              </label>
            </div>
          </div>
        </div>

        <div class="fps-meta" id="lbl-fps">
          ⏱️ Live Stream: -- FPS | Resolution: 240x240 RGB565
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- RIGHT COLUMN: ผลทำนาย (Prediction Results & 3 Gauges)    -->
    <!-- ======================================================== -->
    <div class="col-prediction">
      <div class="card">
        <div class="card-title">
          <span>📊</span> ผลการวิเคราะห์ (Prediction Results)
        </div>

        <!-- Winner Classification Box -->
        <div class="winner-box">
          <span class="badge" id="lbl-class">[ รอถ่ายภาพ ]</span>
          <span class="conf-val" id="lbl-conf">--%</span>
        </div>

        <!-- 3 Visual Probability Bars -->
        <div class="bars-container">
          <!-- 1. Overripe -->
          <div class="bar-row bar-overripe" id="row-overripe">
            <div class="bar-meta">
              <span class="bar-name">🍇 สุกงอม (Overripe)</span>
              <span id="pct-overripe">0.0%</span>
            </div>
            <div class="bar-track">
              <div class="bar-val" id="fill-overripe"></div>
            </div>
          </div>

          <!-- 2. Ripe -->
          <div class="bar-row bar-ripe" id="row-ripe">
            <div class="bar-meta">
              <span class="bar-name">🍃 สุกพอดีกิน (Ripe)</span>
              <span id="pct-ripe">0.0%</span>
            </div>
            <div class="bar-track">
              <div class="bar-val" id="fill-ripe"></div>
            </div>
          </div>

          <!-- 3. Unripe -->
          <div class="bar-row bar-unripe" id="row-unripe">
            <div class="bar-meta">
              <span class="bar-name">🍋 ดิบ/ห่าม (Unripe)</span>
              <span id="pct-unripe">0.0%</span>
            </div>
            <div class="bar-track">
              <div class="bar-val" id="fill-unripe"></div>
            </div>
          </div>
        </div>

        <!-- Latency & Timing Chips -->
        <div class="stats-row">
          <div class="stat-chip">
            <span class="stat-label">🧠 Model Thinking</span>
            <span class="stat-num" id="val-model-delay">-- ms</span>
          </div>
          <div class="stat-chip">
            <span class="stat-label">⏱️ Total Delay</span>
            <span class="stat-num highlight" id="val-total-delay">-- ms</span>
          </div>
        </div>

        <div class="tip-box">
          <span>💡</span>
          <span>จัดตำแหน่งมังคุดตรงกลางกรอบเล็งเป้า และหมุนวงแหวนหน้าเลนส์เพื่อปรับระยะโฟกัส</span>
        </div>
      </div>
    </div>
  </div>

  <div class="footer">
    เชื่อมต่อ: Mangosteen-AI (192.168.4.1) | ซ้าย=กล้อง ขวา=หลอดวัดผลทำนาย
  </div>

  <script>
    const canvas = document.getElementById('cam-canvas');
    const ctx = canvas.getContext('2d');
    const reticle = document.getElementById('reticle');
    const btnAction = document.getElementById('btn-action');
    const rowPostSnap = document.getElementById('row-post-snap');
    const chkAuto = document.getElementById('chk-auto');
    const lblClass = document.getElementById('lbl-class');
    const lblConf = document.getElementById('lbl-conf');
    const valModelDelay = document.getElementById('val-model-delay');
    const valTotalDelay = document.getElementById('val-total-delay');
    const lblFps = document.getElementById('lbl-fps');
    const settingsPanel = document.getElementById('settings-panel');

    // 3 Gauge Bar Elements
    const fillOverripe = document.getElementById('fill-overripe');
    const fillRipe = document.getElementById('fill-ripe');
    const fillUnripe = document.getElementById('fill-unripe');
    const pctOverripe = document.getElementById('pct-overripe');
    const pctRipe = document.getElementById('pct-ripe');
    const pctUnripe = document.getElementById('pct-unripe');
    const rowOverripe = document.getElementById('row-overripe');
    const rowRipe = document.getElementById('row-ripe');
    const rowUnripe = document.getElementById('row-unripe');

    let isStreaming = true;
    let isPaused = false;
    let isPredicting = false;
    let streamAbortController = null;
    let fpsCount = 0;
    let lastFpsTime = Date.now();
    let currentFps = "0";

    function toggleSettings() {
      settingsPanel.classList.toggle('open');
    }

    async function onCamChange(param, val, labelId) {
      if (labelId) {
        document.getElementById(labelId).textContent = val;
      }
      try {
        await fetch(`/camera?var=${param}&val=${val}&t=${Date.now()}`);
      } catch (e) {
        console.error("Camera set error:", e);
      }
    }

    async function onResetCamera() {
      document.getElementById('sld-bright').value = 0;
      document.getElementById('val-bright').textContent = 0;
      document.getElementById('sld-contrast').value = 1;
      document.getElementById('val-contrast').textContent = 1;
      document.getElementById('sld-satur').value = 1;
      document.getElementById('val-satur').textContent = 1;
      document.getElementById('chk-vflip').checked = false;
      document.getElementById('chk-hmirror').checked = false;
      try {
        await fetch(`/camera?var=reset&val=0&t=${Date.now()}`);
      } catch (e) {}
    }

    async function fetchFrame(predict = 0, clickStartTime = null) {
      if (isPaused && predict === 0) return;

      const reqStart = clickStartTime || performance.now();
      if (streamAbortController && predict === 1) {
        streamAbortController.abort();
      }
      streamAbortController = new AbortController();

      try {
        const url = `/snapshot?predict=${predict}&t=${Date.now()}`;
        const res = await fetch(url, { signal: streamAbortController.signal });
        if (!res.ok) throw new Error("Capture failed");

        const predClass = res.headers.get("X-Prediction");
        const conf = parseFloat(res.headers.get("X-Confidence") || "0");
        const latency = parseFloat(res.headers.get("X-Latency") || "0");
        const scores = (res.headers.get("X-Scores") || "0,0,0").split(",");

        const blob = await res.blob();
        const img = new Image();
        img.onload = () => {
          ctx.drawImage(img, 0, 0, 240, 240);
          URL.revokeObjectURL(img.src);

          const totalDelay = Math.round(performance.now() - reqStart);

          fpsCount++;
          const now = Date.now();
          if (now - lastFpsTime >= 1000) {
            currentFps = (fpsCount * 1000 / (now - lastFpsTime)).toFixed(1);
            fpsCount = 0;
            lastFpsTime = now;
          }

          if (predict === 1 || chkAuto.checked) {
            updateUI(predClass, conf, latency, totalDelay, scores);
            if (isPaused) {
              btnAction.style.display = "none";
              rowPostSnap.style.display = "flex";
              isPredicting = false;
            }
          } else {
            lblFps.textContent = `⏱️ Live Stream: ${currentFps} FPS | Resolution: 240x240`;
          }

          if (isStreaming && !isPaused) {
            const nextPredict = chkAuto.checked ? 1 : 0;
            setTimeout(() => fetchFrame(nextPredict), nextPredict ? 120 : 50);
          }
        };
        img.src = URL.createObjectURL(blob);
      } catch (err) {
        if (err.name !== "AbortError") {
          if (isPaused) {
            btnAction.disabled = false;
            btnAction.innerHTML = "<span>📸</span> ลองใหม่อีกครั้ง";
            lblClass.textContent = "[ ถ่ายภาพไม่สำเร็จ ]";
            lblClass.className = "badge";
            isPredicting = false;
          }
          if (isStreaming && !isPaused) {
            setTimeout(() => fetchFrame(chkAuto.checked ? 1 : 0), 400);
          }
        }
      }
    }

    function updateUI(cls, conf, latency, totalDelay, scores) {
      if (!cls) return;
      
      let thaiName = cls === "ripe" ? "สุก" : (cls === "unripe" ? "ดิบ" : "สุกงอม");
      lblClass.textContent = `🎯 ${thaiName} (${cls.toUpperCase()})`;
      lblClass.className = `badge ${cls}`;
      lblConf.textContent = `${conf.toFixed(1)}%`;

      if (valModelDelay) valModelDelay.textContent = `${latency.toFixed(1)} ms`;
      if (valTotalDelay) valTotalDelay.textContent = `${totalDelay} ms (${(totalDelay/1000).toFixed(2)}s)`;

      if (scores.length === 3) {
        const pOver = Math.max(0, Math.min(100, parseFloat(scores[0]) || 0));
        const pRipe = Math.max(0, Math.min(100, parseFloat(scores[1]) || 0));
        const pUnripe = Math.max(0, Math.min(100, parseFloat(scores[2]) || 0));

        fillOverripe.style.width = `${pOver}%`;
        pctOverripe.textContent = `${pOver.toFixed(1)}%`;

        fillRipe.style.width = `${pRipe}%`;
        pctRipe.textContent = `${pRipe.toFixed(1)}%`;

        fillUnripe.style.width = `${pUnripe}%`;
        pctUnripe.textContent = `${pUnripe.toFixed(1)}%`;

        rowOverripe.classList.toggle('winner', cls === "overripe");
        rowRipe.classList.toggle('winner', cls === "ripe");
        rowUnripe.classList.toggle('winner', cls === "unripe");
      }
    }

    function onActionClick() {
      if (chkAuto.checked || isPredicting) return;

      isPredicting = true;
      isPaused = true;
      btnAction.disabled = true;
      btnAction.innerHTML = "<span>⏳</span> บอร์ดกำลังคิด... (3-4 วิ)";
      reticle.style.opacity = "0";

      lblClass.textContent = "🧠 กำลังคิดโมเดล AI...";
      lblClass.className = "badge thinking";
      lblConf.textContent = "--%";
      valModelDelay.textContent = "กำลังคำนวณ...";
      valTotalDelay.textContent = "กำลังจับเวลา...";

      fetchFrame(1, performance.now());
    }

    function onResumeClick() {
      isPaused = false;
      isPredicting = false;
      btnAction.disabled = false;
      btnAction.innerHTML = "<span>📸</span> ถ่ายภาพ & Predict";
      btnAction.style.display = "flex";
      rowPostSnap.style.display = "none";
      reticle.style.opacity = "1";

      lblClass.textContent = "[ รอถ่ายภาพ ]";
      lblClass.className = "badge";
      lblConf.textContent = "--%";

      fetchFrame(0);
    }

    function onSaveClick() {
      const link = document.createElement('a');
      link.download = `mangosteen_${new Date().toISOString().slice(0,19).replace(/[-:]/g,"")}.jpg`;
      link.href = canvas.toDataURL("image/jpeg", 0.95);
      link.click();
    }

    function onAutoToggle() {
      if (chkAuto.checked) {
        isPaused = false;
        btnAction.innerHTML = "<span>⚡</span> วิเคราะห์สดตลอดเวลา...";
        btnAction.disabled = true;
        btnAction.style.display = "flex";
        rowPostSnap.style.display = "none";
        reticle.style.opacity = "0";
      } else {
        btnAction.innerHTML = "<span>📸</span> ถ่ายภาพ & Predict";
        btnAction.disabled = false;
        reticle.style.opacity = "1";
      }
    }

    // Start Live Preview
    fetchFrame(0);
  </script>
</body>
</html>
)rawliteral";

// ==============================================================================
// 4. CAMERA INITIALIZATION (240x240 RGB565 DUAL BUFFER)
// ==============================================================================
bool initCamera() {
    pinMode(PWR_ON_PIN, OUTPUT);
    digitalWrite(PWR_ON_PIN, HIGH);
    delay(100);

    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_RGB565;
    config.frame_size = FRAMESIZE_240X240;   // 240x240 Sharp Square Frame (6.25x pixels)
    config.jpeg_quality = 12;
    config.fb_count = 2;
    config.grab_mode = CAMERA_GRAB_LATEST;
    config.fb_location = CAMERA_FB_IN_PSRAM;

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("[Camera] Init Failed with error 0x%x\r\n", err);
        return false;
    }

    sensor_t *s = esp_camera_sensor_get();
    if (s) {
        s->set_brightness(s, 0);
        s->set_contrast(s, 1);       // Rich contrast
        s->set_saturation(s, 1);     // Vibrant colors
        s->set_sharpness(s, 1);      // Edge sharpness
        s->set_whitebal(s, 1);       // Auto White Balance
        s->set_awb_gain(s, 1);
        s->set_exposure_ctrl(s, 1);  // Auto Exposure
    }

    Serial.print("[Camera] Dual buffer OV2640 initialized at 240x240.\r\n");
    return true;
}

// ==============================================================================
// 5. TENSORFLOW LITE MICRO INITIALIZATION
// ==============================================================================
bool initTFLite() {
    if (g_mangosteen_model_data_len == 0) {
        Serial.print("[TFLite] ERROR: No model loaded! Please train your model following TRAINING_GUIDE.md\r\n");
        return false;
    }
    Serial.print("[TFLite] Loading model...\r\n");
    model = tflite::GetModel(g_mangosteen_model_data);
    if (model->version() != TFLITE_SCHEMA_VERSION) {
        Serial.printf("[TFLite] Schema mismatch! Model: %d, Runtime: %d\r\n",
                      model->version(), TFLITE_SCHEMA_VERSION);
        return false;
    }

    if (psramFound()) {
        tensor_arena = (uint8_t*)ps_malloc(kTensorArenaSize);
    }
    if (!tensor_arena) {
        tensor_arena = (uint8_t*)malloc(kTensorArenaSize);
    }
    if (!tensor_arena) {
        Serial.print("[TFLite] ERROR: Failed to allocate Tensor Arena!\r\n");
        return false;
    }

    static tflite::MicroErrorReporter micro_error_reporter;
    static tflite::ErrorReporter* error_reporter = &micro_error_reporter;
    static tflite::AllOpsResolver resolver;
    static tflite::MicroInterpreter static_interpreter(model, resolver, tensor_arena, kTensorArenaSize, error_reporter);
    interpreter = &static_interpreter;

    if (interpreter->AllocateTensors() != kTfLiteOk) {
        Serial.print("[TFLite] ERROR: AllocateTensors() failed!\r\n");
        return false;
    }

    input = interpreter->input(0);
    output = interpreter->output(0);

    Serial.printf("[TFLite] Ready! Arena: %u / %u bytes\r\n",
                  interpreter->arena_used_bytes(), (unsigned)kTensorArenaSize);
    return true;
}

// ==============================================================================
// 6. HTTP REQUEST HANDLERS
// ==============================================================================
void handleRoot() {
    server.send_P(200, "text/html", INDEX_HTML);
}

void handleSnapshot() {
    bool do_predict = server.hasArg("predict") && server.arg("predict") == "1";

    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        server.send(500, "text/plain", "Camera grab failed");
        return;
    }

    int64_t t_board_start = esp_timer_get_time();
    float latency_ms = 0.0f;
    float board_delay_ms = 0.0f;
    int best_class = 0;
    float max_score = -1.0f;
    float scores[3] = {0};

    // If predict requested, downsample 240x240 to 96x96 INT8 for MobileNetV2
    if (do_predict && interpreter) {
        uint16_t *pixels = (uint16_t*)fb->buf;
        int8_t *input_buf = input->data.int8;
        int idx = 0;

        // Downsample 240x240 -> 96x96 (2.5x step)
        for (int y = 0; y < 96; y++) {
            int src_y = (y * 240) / 96;
            int row_offset = src_y * 240;
            for (int x = 0; x < 96; x++) {
                int src_x = (x * 240) / 96;
                uint16_t p = pixels[row_offset + src_x];
                p = (p >> 8) | (p << 8);

                uint8_t r = ((p >> 11) & 0x1F) << 3;
                uint8_t g = ((p >> 5) & 0x3F) << 2;
                uint8_t b = (p & 0x1F) << 3;

                input_buf[idx++] = (int8_t)((int16_t)r - 128);
                input_buf[idx++] = (int8_t)((int16_t)g - 128);
                input_buf[idx++] = (int8_t)((int16_t)b - 128);
            }
        }

        int64_t t_start = esp_timer_get_time();
        TfLiteStatus status = interpreter->Invoke();
        int64_t t_end = esp_timer_get_time();

        if (status == kTfLiteOk) {
            latency_ms = (float)(t_end - t_start) / 1000.0f;
            for (int i = 0; i < 3; i++) {
                scores[i] = (static_cast<float>(output->data.int8[i]) - output->params.zero_point) * output->params.scale;
                if (scores[i] > max_score) {
                    max_score = scores[i];
                    best_class = i;
                }
            }
        }

        board_delay_ms = (float)(esp_timer_get_time() - t_board_start) / 1000.0f;
        Serial.printf("[AI] Predicted: %s (%.1f%%) | Model Thinking: %.1f ms | Total Board Time: %.1f ms\r\n",
                      kClassNames[best_class], max_score * 100.0f, latency_ms, board_delay_ms);
    }

    // Convert 240x240 RGB565 to sharp JPEG
    uint8_t *jpg_buf = NULL;
    size_t jpg_len = 0;
    bool ok = fmt2jpg((uint8_t*)fb->buf, fb->len, fb->width, fb->height, PIXFORMAT_RGB565, 80, &jpg_buf, &jpg_len);
    esp_camera_fb_return(fb);

    if (!ok || !jpg_buf) {
        server.send(500, "text/plain", "JPEG convert failed");
        return;
    }

    server.sendHeader("Access-Control-Allow-Origin", "*");
    server.sendHeader("Access-Control-Expose-Headers", "X-Prediction, X-Confidence, X-Latency, X-Board-Delay, X-Scores");
    server.sendHeader("X-Prediction", kClassNames[best_class]);
    server.sendHeader("X-Confidence", String(max_score * 100.0f, 1));
    server.sendHeader("X-Latency", String(latency_ms, 1));
    server.sendHeader("X-Board-Delay", String(board_delay_ms, 1));
    server.sendHeader("X-Scores", String(scores[0] * 100.0f, 1) + "," + String(scores[1] * 100.0f, 1) + "," + String(scores[2] * 100.0f, 1));

    server.setContentLength(jpg_len);
    server.send(200, "image/jpeg", "");
    WiFiClient client = server.client();
    client.write(jpg_buf, jpg_len);

    free(jpg_buf);
}

void handleCameraControl() {
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        server.send(500, "text/plain", "Camera sensor not ready");
        return;
    }

    if (!server.hasArg("var") || !server.hasArg("val")) {
        server.send(400, "text/plain", "Missing var or val parameter");
        return;
    }

    String var = server.arg("var");
    int val = server.arg("val").toInt();
    int res = 0;

    if (var == "brightness") {
        res = s->set_brightness(s, val);
    } else if (var == "contrast") {
        res = s->set_contrast(s, val);
    } else if (var == "saturation") {
        res = s->set_saturation(s, val);
    } else if (var == "vflip") {
        res = s->set_vflip(s, val);
    } else if (var == "hmirror") {
        res = s->set_hmirror(s, val);
    } else if (var == "whitebal") {
        res = s->set_whitebal(s, val);
    } else if (var == "reset") {
        s->set_brightness(s, 0);
        s->set_contrast(s, 1);
        s->set_saturation(s, 1);
        s->set_vflip(s, 0);
        s->set_hmirror(s, 0);
        s->set_whitebal(s, 1);
        res = 0;
    } else {
        server.send(404, "text/plain", "Unknown parameter");
        return;
    }

    server.sendHeader("Access-Control-Allow-Origin", "*");
    if (res == 0) {
        server.send(200, "text/plain", "OK");
    } else {
        server.send(500, "text/plain", "Failed");
    }
}

// ==============================================================================
// 7. SETUP & MAIN LOOP
// ==============================================================================
void setup() {
    Serial.begin(115200);
    delay(2000);

    Serial.print("\r\n=======================================================\r\n");
    Serial.print(" LilyGO T-SIMCAM: 240x240 Wi-Fi SoftAP Inspector\r\n");
    Serial.print("=======================================================\r\n");

    if (!initCamera() || !initTFLite()) {
        Serial.print("[HALT] Init failed.\r\n");
        while (1) delay(1000);
    }

    // Setup Wi-Fi SoftAP
    IPAddress local_ip(192, 168, 4, 1);
    IPAddress gateway(192, 168, 4, 1);
    IPAddress subnet(255, 255, 255, 0);
    WiFi.softAPConfig(local_ip, gateway, subnet);
    WiFi.softAP(ap_ssid, ap_pass);

    Serial.print("\r\n[Wi-Fi] SoftAP Started!\r\n");
    Serial.printf("[Wi-Fi] SSID: %s\r\n", ap_ssid);
    Serial.printf("[Wi-Fi] Password: %s\r\n", ap_pass);
    Serial.printf("[Wi-Fi] Web Dashboard URL: http://%s\r\n\r\n", WiFi.softAPIP().toString().c_str());

    server.on("/", HTTP_GET, handleRoot);
    server.on("/snapshot", HTTP_GET, handleSnapshot);
    server.on("/camera", HTTP_GET, handleCameraControl);
    server.begin();
    Serial.print("[Web] HTTP Server listening on port 80.\r\n");
}

void loop() {
    server.handleClient();
}
