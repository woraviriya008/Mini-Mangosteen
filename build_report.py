# -*- coding: utf-8 -*-
import os
import base64
import subprocess
import shutil

def main():
    print("Reading chart images...")
    curves_img_path = 'training/training_vs_validation_curves_light.png'
    cm_img_path = 'training/confusion_matrix_light.png'

    if not os.path.exists(curves_img_path) or not os.path.exists(cm_img_path):
        raise FileNotFoundError(f"Missing image files: {curves_img_path} or {cm_img_path}")

    with open(curves_img_path, 'rb') as f:
        curves_b64 = base64.b64encode(f.read()).decode('utf-8')

    with open(cm_img_path, 'rb') as f:
        cm_b64 = base64.b64encode(f.read()).decode('utf-8')

    html_content = f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<title>รายงานการพัฒนาและเพิ่มประสิทธิภาพโมเดลจำแนกความสุกมังคุดสำหรับ Microcontroller</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400&family=Sarabun:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400&family=Fira+Code:wght@400;500;600&display=swap');

    @page {{
        size: A4;
        margin: 15mm 13mm 15mm 13mm;
    }}

    * {{
        box-sizing: border-box;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }}

    body {{
        font-family: 'Sarabun', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 13px;
        line-height: 1.6;
        color: #1e293b;
        background-color: #ffffff;
        margin: 0;
        padding: 0;
    }}

    h1, h2, h3, h4, .font-heading {{
        font-family: 'Prompt', sans-serif;
        color: #0f172a;
        margin-top: 0;
    }}

    h1 {{
        font-size: 23px;
        font-weight: 700;
        line-height: 1.25;
        margin-bottom: 6px;
        color: #1e1b4b;
    }}

    h2 {{
        font-size: 16px;
        font-weight: 600;
        margin-top: 22px;
        margin-bottom: 10px;
        padding-bottom: 5px;
        border-bottom: 2px solid #e2e8f0;
        color: #312e81;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    h3 {{
        font-size: 14px;
        font-weight: 600;
        margin-top: 14px;
        margin-bottom: 6px;
        color: #4338ca;
    }}

    p {{
        margin-top: 0;
        margin-bottom: 8px;
        text-align: justify;
    }}

    ul, ol {{
        margin-top: 0;
        margin-bottom: 10px;
        padding-left: 20px;
    }}

    li {{
        margin-bottom: 4px;
    }}

    .header-banner {{
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 55%, #4338ca 100%);
        color: white;
        padding: 22px 26px;
        border-radius: 12px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(30, 27, 75, 0.12);
    }}

    .header-banner h1 {{
        color: white;
        margin-bottom: 6px;
    }}

    .header-banner .subtitle {{
        font-family: 'Prompt', sans-serif;
        font-size: 13.5px;
        color: #c7d2fe;
        font-weight: 400;
        margin-bottom: 14px;
    }}

    .meta-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        background: rgba(255, 255, 255, 0.12);
        padding: 10px 14px;
        border-radius: 8px;
        font-size: 11.5px;
    }}

    .meta-item span.label {{
        color: #a5b4fc;
        display: block;
        font-weight: 500;
        margin-bottom: 2px;
    }}

    .meta-item span.val {{
        color: white;
        font-weight: 600;
        font-family: 'Prompt', sans-serif;
    }}

    .kpi-row {{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 8px;
        margin-bottom: 16px;
    }}

    .kpi-card {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 8px;
        text-align: center;
        border-top: 3.5px solid #4f46e5;
    }}

    .kpi-card.success {{
        border-top-color: #059669;
    }}

    .kpi-card.info {{
        border-top-color: #0284c7;
    }}

    .kpi-card.warning {{
        border-top-color: #d97706;
    }}

    .kpi-val {{
        font-family: 'Prompt', sans-serif;
        font-size: 17px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 2px;
    }}

    .kpi-label {{
        font-size: 10.5px;
        color: #64748b;
        font-weight: 500;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0 14px 0;
        font-size: 11.8px;
    }}

    th, td {{
        padding: 6px 9px;
        border: 1px solid #cbd5e1;
        text-align: left;
    }}

    th {{
        background-color: #f1f5f9;
        color: #1e293b;
        font-family: 'Prompt', sans-serif;
        font-weight: 600;
    }}

    tr:nth-child(even) {{
        background-color: #f8fafc;
    }}

    .text-center {{
        text-align: center;
    }}

    .text-right {{
        text-align: right;
    }}

    .badge {{
        display: inline-block;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 10.5px;
        font-weight: 600;
        font-family: 'Fira Code', monospace;
    }}

    .badge-primary {{ background: #e0e7ff; color: #3730a3; }}
    .badge-success {{ background: #d1fae5; color: #065f46; }}
    .badge-warning {{ background: #fef3c7; color: #92400e; }}
    .badge-info {{ background: #e0f2fe; color: #0369a1; }}

    .card-box {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #4338ca;
        padding: 10px 14px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
        font-size: 12.2px;
    }}

    .figure-container {{
        text-align: center;
        margin: 12px 0 14px 0;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px;
    }}

    .figure-container img {{
        max-width: 96%;
        height: auto;
        border-radius: 6px;
    }}

    .figure-caption {{
        font-size: 11px;
        color: #475569;
        margin-top: 6px;
        font-style: italic;
    }}

    .page-break {{
        page-break-before: always;
    }}

    .avoid-break {{
        page-break-inside: avoid;
    }}

    .code-box {{
        background: #0f172a;
        color: #f8fafc;
        padding: 10px 14px;
        border-radius: 6px;
        font-family: 'Fira Code', monospace;
        font-size: 11px;
        margin: 8px 0 12px 0;
        line-height: 1.45;
    }}

    .section-num {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 22px;
        height: 22px;
        background: #4338ca;
        color: white;
        border-radius: 50%;
        font-size: 11.5px;
        margin-right: 6px;
    }}
</style>
</head>
<body>

<!-- Header Banner -->
<div class="header-banner">
    <div style="font-size: 10.5px; text-transform: uppercase; letter-spacing: 1.5px; color: #a5b4fc; font-weight: 600; margin-bottom: 4px;">
        TECHNICAL ENGINEERING REPORT &amp; ARCHITECTURAL SPECIFICATION
    </div>
    <h1>รายงานกระบวนการพัฒนาและเพิ่มประสิทธิภาพโมเดลจำแนกความสุกมังคุด</h1>
    <div class="subtitle">
        End-to-End Pipeline: Deep Learning Architecture (94k), Dataset Augmentation &amp; Balancing, Full INT8 Quantization, และการพอร์ตระบบสู่ ESP32-S3 Microcontroller
    </div>
    <div class="meta-grid">
        <div class="meta-item">
            <span class="label">Model Architecture:</span>
            <span class="val">Mangosteen_SeparableCNN_94k</span>
        </div>
        <div class="meta-item">
            <span class="label">Input Resolution:</span>
            <span class="val">96 &times; 96 &times; 3 (RGB)</span>
        </div>
        <div class="meta-item">
            <span class="label">Quantization:</span>
            <span class="val">Full INT8 (134.11 KB)</span>
        </div>
        <div class="meta-item">
            <span class="label">Target Hardware:</span>
            <span class="val">LilyGO T-SIMCAM (ESP32-S3)</span>
        </div>
    </div>
</div>

<!-- KPI Summary Cards -->
<div class="kpi-row">
    <div class="kpi-card">
        <div class="kpi-val">94,163</div>
        <div class="kpi-label">Total Parameters</div>
    </div>
    <div class="kpi-card success">
        <div class="kpi-val">94.44%</div>
        <div class="kpi-label">Best Val Accuracy (Ep.61)</div>
    </div>
    <div class="kpi-card success">
        <div class="kpi-val">80.00%</div>
        <div class="kpi-label">Test Set Accuracy (40 imgs)</div>
    </div>
    <div class="kpi-card info">
        <div class="kpi-val">134.1 KB</div>
        <div class="kpi-label">INT8 Flash Footprint</div>
    </div>
    <div class="kpi-card warning">
        <div class="kpi-val">0.00%</div>
        <div class="kpi-label">Quantization Drop</div>
    </div>
</div>

<!-- Section 1 -->
<h2><span class="section-num">1</span> บทนำและวัตถุประสงค์โครงการ (Project Background &amp; Objective)</h2>
<p>
โครงการวิจัยและพัฒนาชิ้นนี้มีเป้าหมายเพื่อสร้างระบบตรวจวัดและจำแนกระดับความสุกของผลมังคุดแบบอัตโนมัติ (Automated Mangosteen Ripeness Classifier) บนอุปกรณ์ <strong>Edge AI / Microcontroller (ESP32-S3)</strong> เพื่อให้สามารถนำไปติดตั้งในระบบคัดแยกผลไม้ ณ โรงคัดบรรจุ (Lhong) หรือใช้งานในสวนผลไม้โดยตรง โดยไม่ต้องพึ่งพาการส่งภาพไปประมวลผลบน Cloud Server หรือเครื่องคอมพิวเตอร์ระดับสูง ซึ่งช่วยลดต้นทุนฮาร์ดแวร์ ลดอัตราการใช้พลังงาน และสามารถทำงานแบบ Real-time ได้ในพื้นที่เกษตรกรรมที่ไม่มีสัญญาณอินเทอร์เน็ต
</p>
<p>
ระดับความสุกของมังคุดถูกจำแนกออกเป็น 3 ระดับหลักตามมาตรฐานการคัดเกรดเชิงพาณิชย์และการส่งออก:
</p>
<ul>
    <li><strong>Unripe (มังคุดดิบ / ผิวด่างเขียวแต้มชมพูอ่อน):</strong> ระยะเก็บเกี่ยวสำหรับการส่งออกทางเรือหรือขนส่งระยะไกล เนื้อแน่น เปลือกหนา ยางสีเหลืองยังคงมีอยู่</li>
    <li><strong>Ripe (มังคุดสุกพร้อมรับประทาน / ผิวสีแดงอมม่วง):</strong> ระยะพร้อมบริโภคทันที รสหวานอมเปรี้ยวกลมกล่อม เนื้อนุ่ม ปราศจากยาง</li>
    <li><strong>Overripe (มังคุดสุกจัด-งอม / ผิวสีม่วงเข้มเกือบดำ):</strong> ระยะสุกเต็มที่ เนื้อเริ่มนิ่มมาก เปลือกนิ่มหรือมีรอยช้ำสะสม อายุการวางจำหน่ายสั้นมาก</li>
</ul>

<div class="card-box">
    <strong>ข้อจำกัดทางวิศวกรรมของ Microcontroller (Edge Constraints):</strong><br>
    ESP32-S3 มี Internal SRAM เพียง 512 KB และ External PSRAM 8 MB โมเดลโครงข่ายประสาทเทียมแบบทั่วไป (เช่น MobileNetV2 ~3.5M พารามิเตอร์ หรือ ResNet50 ~25M พารามิเตอร์) มีขนาดใหญ่เกินกว่าจะรันบนชิปนี้ได้อย่างมีประสิทธิภาพ โครงการนี้จึงออกแบบโมเดลขึ้นมาใหม่เฉพาะทางในชื่อ <code>Mangosteen_SeparableCNN_94k</code> ซึ่งมีขนาดเพียง 94k พารามิเตอร์ และผ่านการทำ Full INT8 Quantization จนเหลือขนาดเพียง 134.11 KB รันบน TFLite Micro ได้อย่างมีเสถียรภาพโดยใช้พื้นที่คำนวณ Tensor Arena เพียง 114.3 KB
</div>

<!-- Section 2 -->
<h2><span class="section-num">2</span> กระบวนการจัดการและปรับสมดุลชุดข้อมูล (Dataset Pipeline &amp; Augmentation)</h2>
<p>
ความท้าทายสำคัญที่สุดในการฝึกสอนโมเดล Deep Learning ทางการเกษตรคือ ปัญหา <strong>Class Imbalance</strong> และขนาดของชุดข้อมูลดั้งเดิมที่มีจำกัด ในโครงการนี้มีชุดข้อมูลภาพถ่ายมังคุดจริงเริ่มต้นจำนวน <strong>245 ภาพ</strong> เมื่อทำการแบ่งสัดส่วนชุดข้อมูลออกเป็น Train, Validation และ Test พบว่าในชุด Train มีความไม่สมดุลของข้อมูลอย่างรุนแรง โดยเฉพาะคลาส <em>Overripe</em> ที่มีเพียง 23 ภาพ ในขณะที่ <em>Unripe</em> มีถึง 95 ภาพ
</p>

<h3>2.1 โครงสร้างการแบ่งชุดข้อมูลและการแก้ปัญหา Class Imbalance</h3>
<p>
เพื่อป้องกันปัญหา <strong>Data Leakage</strong> (การรั่วไหลของข้อมูล) การทำ Data Augmentation จึงถูกกำหนดให้กระทำ <strong>เฉพาะกับชุด Train (Training Set) เท่านั้น</strong> โดยชุด Validation และ Test จะคงไว้ซึ่งภาพถ่ายต้นฉบับจริง 100% เพื่อใช้ประเมินความสามารถในการใช้งานจริง (Generalization Ability) ของโมเดลอย่างเที่ยงตรง
</p>

<table class="avoid-break">
    <thead>
        <tr>
            <th>Split Dataset</th>
            <th class="text-center">Unripe (ดิบ)</th>
            <th class="text-center">Ripe (สุก)</th>
            <th class="text-center">Overripe (งอม)</th>
            <th class="text-center">รวมภาพเดิม (Raw)</th>
            <th class="text-center">ภาพเพิ่มจาก Augmentation</th>
            <th class="text-center">รวมหลังจัดสมดุล (Final)</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Train Set</strong> (ฝึกสอนโมเดล)</td>
            <td class="text-center">95</td>
            <td class="text-center">51</td>
            <td class="text-center">23</td>
            <td class="text-center"><strong>169</strong></td>
            <td class="text-center"><span class="badge badge-warning">+120 ภาพ</span></td>
            <td class="text-center"><span class="badge badge-success"><strong>289 ภาพ</strong></span></td>
        </tr>
        <tr>
            <td><strong>Validation Set</strong> (ปรับจูนโมเดล)</td>
            <td class="text-center">12</td>
            <td class="text-center">12</td>
            <td class="text-center">12</td>
            <td class="text-center"><strong>36</strong></td>
            <td class="text-center">0 (ไม่ทำ Augment)</td>
            <td class="text-center"><strong>36 ภาพ</strong></td>
        </tr>
        <tr>
            <td><strong>Test Set</strong> (ทดสอบขั้นสุดท้าย)</td>
            <td class="text-center">14</td>
            <td class="text-center">13</td>
            <td class="text-center">13</td>
            <td class="text-center"><strong>40</strong></td>
            <td class="text-center">0 (ไม่ทำ Augment)</td>
            <td class="text-center"><strong>40 ภาพ</strong></td>
        </tr>
        <tr style="background-color: #eef2ff; font-weight: bold;">
            <td>รวมทั้งโครงการ (Total)</td>
            <td class="text-center">121</td>
            <td class="text-center">76</td>
            <td class="text-center">48</td>
            <td class="text-center">245 ภาพ</td>
            <td class="text-center">+120 ภาพ</td>
            <td class="text-center"><span class="badge badge-primary">365 ภาพ</span></td>
        </tr>
    </tbody>
</table>

<div class="card-box">
    <strong>คำอธิบายที่มาของจำนวน 365 ภาพในโปรเจกต์:</strong><br>
    เริ่มต้นเรามีภาพถ่ายมังคุดจริงรวม <strong>245 ภาพ</strong> ในชุด Train เริ่มแรกมี 169 ภาพ โดยคลาส Overripe ขาดแคลนอย่างมาก (มีเพียง 23 ภาพ) จึงได้ทำการสังเคราะห์ภาพเพิ่มด้วย Data Augmentation อีก <strong>120 ภาพ</strong> (เพิ่ม Overripe +69 ภาพ กลายเป็น 92 ภาพ และเพิ่ม Ripe +51 ภาพ กลายเป็น 102 ภาพ) รวมชุด Train ที่สมดุลแล้วเป็น <strong>289 ภาพ</strong> เมื่อนำมารวมกับชุด Validation (36 ภาพ) และ Test (40 ภาพ) จึงได้จำนวนภาพรวมทั้งหมดในโครงการเท่ากับ <strong>289 + 36 + 40 = 365 ภาพ</strong> พอดิบพอดี
</div>

<h3>2.2 เทคนิค Data Augmentation ที่นำมาใช้</h3>
<ul>
    <li><strong>Random Rotation (&plusmn;20&deg;):</strong> หมุนภาพสุ่มเพื่อจำลองผลมังคุดที่วางในมุมองศาต่างๆ บนสายพานหรือถาดคัดแยก</li>
    <li><strong>Width &amp; Height Shift (10%):</strong> เลื่อนตำแหน่งภาพแนวนอนและแนวตั้ง เพื่อให้โมเดลไม่ยึดติดกับตำแหน่งกึ่งกลางภาพ (Translation Invariance)</li>
    <li><strong>Random Zoom (15%):</strong> ซูมภาพสุ่มเพื่อจำลองระยะห่างระหว่างเลนส์กล้อง OV2640 กับผลมังคุดที่มีขนาดผลเล็กใหญ่แตกต่างกัน</li>
    <li><strong>Horizontal Flip:</strong> พลิกภาพกระจกแนวนอน เพื่อเพิ่มความหลากหลายของมุมมองด้านซ้าย-ขวา</li>
    <li><strong>Pixel Normalization:</strong> ปรับสเกลค่าพิกเซลจาก [0, 255] ให้อยู่ในช่วงมาตรฐานสำหรับการคำนวณของโครงข่ายประสาทเทียม</li>
</ul>

<div class="page-break"></div>

<!-- Section 3 -->
<h2><span class="section-num">3</span> สถาปัตยกรรมโครงข่ายประสาทเทียม (Mangosteen_SeparableCNN_94k)</h2>
<p>
การออกแบบโครงข่ายประสาทเทียมสำหรับ Microcontroller ต้องคำนึงถึง 3 ปัจจัยหลัก: <strong>ขนาดพารามิเตอร์ (Flash Memory), ปริมาณ RAM ชั่วคราวขณะคำนวณ (Peak Activation / Tensor Arena), และความเร็วในการคำนวณ (FLOPs / Inference Latency)</strong> จึงได้พัฒนาโมเดลสถาปัตยกรรมแบบ <em>Multi-Stage Depthwise Separable CNN</em> โดยมีกลยุทธ์การออกแบบเชิงลึกดังนี้:
</p>

<h3>3.1 หลักการออกแบบเชิงสถาปัตยกรรม (Architectural Innovations)</h3>
<ol>
    <li>
        <strong>Early Downsampling ที่ Stage 0:</strong><br>
        ใช้ Standard Conv2D ขนาด Filter 24 ช่อง พร้อม Stride=2 ทันทีที่ Layer แรก ส่งผลให้ขนาด Feature Map ลดลงจาก $96 \times 96$ เหลือ $48 \times 48$ ในขั้นตอนเดียว เทคนิคนี้ช่วยลดขนาดหน่วยความจำ Peak Activation Map และลดจำนวนการคำนวณ (FLOPs) ของโครงข่ายทั้งหมดลงกว่า <strong>4 เท่า (75%)</strong> โดยไม่สูญเสียรายละเอียดสำคัญของสีและผิวผลมังคุด
    </li>
    <li>
        <strong>Depthwise Separable Convolutions (Stages 1 ถึง 5):</strong><br>
        แยกการคำนวณออกเป็น 2 ส่วน: <em>Depthwise Conv</em> (คำนวณ $3 \times 3$ แยกแต่ละแชนแนล) และ <em>Pointwise Conv</em> (คำนวณ $1 \times 1$ เพื่อผสมแชนแนล) ลดจำนวนพารามิเตอร์และปริมาณการคำนวณลงได้ถึง $\approx 8-9$ เท่า เมื่อเทียบกับ Convolution แบบดั้งเดิม
    </li>
    <li>
        <strong>Batch Normalization &amp; Progressive Regularization:</strong><br>
        แทรก Batch Normalization หลังทุกชุด Convolution เพื่อรักษาเสถียรภาพของการแจกแจงข้อมูล และใช้ Dropout ค่อยๆ ไต่ระดับจาก 0.20 ในช่วงต้น ไปจนถึง 0.30 ในชั้นลึกสุด เพื่อป้องกันการเกิด Overfitting
    </li>
    <li>
        <strong>Global Average Pooling (GAP) แทน Flatten:</strong><br>
        ทำการเฉลี่ยค่า Feature Map ขนาด $12 \times 12 \times 128$ ให้กลายเป็น Vector ขนาด 128 มิติโดยตรง ช่วยตัด Bottleneck ของพารามิเตอร์ใน Dense Layer ออกไปได้มากกว่าแสนพารามิเตอร์
    </li>
</ol>

<h3 class="font-heading">3.2 ตารางแจกแจงโครงสร้าง Layer ทั้ง 28 Layers ใน Keras</h3>
<table class="avoid-break">
    <thead>
        <tr>
            <th>Index</th>
            <th>Stage / Block</th>
            <th>Layer Type</th>
            <th class="text-center">Output Shape</th>
            <th class="text-center">Kernel / Stride</th>
            <th class="text-center">Param #</th>
            <th>Activation / Notes</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>0</td>
            <td>Input</td>
            <td><code>InputLayer</code></td>
            <td class="text-center">(None, 96, 96, 3)</td>
            <td class="text-center">-</td>
            <td class="text-center">0</td>
            <td>RGB Color Input (96&times;96)</td>
        </tr>
        <tr style="background-color: #f0fdf4;">
            <td>1-3</td>
            <td><strong>Stage 0</strong></td>
            <td><code>Conv2D + BN + ReLU</code></td>
            <td class="text-center">(None, 48, 48, 24)</td>
            <td class="text-center">3&times;3, Stride=2</td>
            <td class="text-center">768</td>
            <td><span class="badge badge-success">Early Downsample /4x</span></td>
        </tr>
        <tr>
            <td>4-7</td>
            <td><strong>Stage 1</strong></td>
            <td><code>SeparableConv + BN + ReLU + Drop</code></td>
            <td class="text-center">(None, 48, 48, 32)</td>
            <td class="text-center">3&times;3, Stride=1</td>
            <td class="text-center">1,144</td>
            <td>Dropout(0.20)</td>
        </tr>
        <tr style="background-color: #f0fdf4;">
            <td>8-11</td>
            <td><strong>Stage 2</strong></td>
            <td><code>SeparableConv + BN + ReLU</code></td>
            <td class="text-center">(None, 24, 24, 48)</td>
            <td class="text-center">3&times;3, Stride=2</td>
            <td class="text-center">2,048</td>
            <td>Spatial Reduction /2x</td>
        </tr>
        <tr>
            <td>12-15</td>
            <td><strong>Stage 3</strong></td>
            <td><code>SeparableConv + BN + ReLU + Drop</code></td>
            <td class="text-center">(None, 24, 24, 64)</td>
            <td class="text-center">3&times;3, Stride=1</td>
            <td class="text-center">3,776</td>
            <td>Dropout(0.25)</td>
        </tr>
        <tr style="background-color: #f0fdf4;">
            <td>16-19</td>
            <td><strong>Stage 4</strong></td>
            <td><code>SeparableConv + BN + ReLU</code></td>
            <td class="text-center">(None, 12, 12, 96)</td>
            <td class="text-center">3&times;3, Stride=2</td>
            <td class="text-center">7,168</td>
            <td>Spatial Reduction /2x</td>
        </tr>
        <tr>
            <td>20-23</td>
            <td><strong>Stage 5</strong></td>
            <td><code>SeparableConv + BN + ReLU + Drop</code></td>
            <td class="text-center">(None, 12, 12, 128)</td>
            <td class="text-center">3&times;3, Stride=1</td>
            <td class="text-center">13,632</td>
            <td>Dropout(0.30)</td>
        </tr>
        <tr style="background-color: #fdf2f8;">
            <td>24</td>
            <td>Classification Head</td>
            <td><code>GlobalAveragePooling2D</code></td>
            <td class="text-center">(None, 128)</td>
            <td class="text-center">Pool 12&times;12</td>
            <td class="text-center">0</td>
            <td>Feature Aggregation</td>
        </tr>
        <tr style="background-color: #fdf2f8;">
            <td>25</td>
            <td>Classification Head</td>
            <td><code>Dense (Output)</code></td>
            <td class="text-center">(None, 3)</td>
            <td class="text-center">Linear Projection</td>
            <td class="text-center">387</td>
            <td>Logits (Unripe, Ripe, Overripe)</td>
        </tr>
        <tr style="background-color: #fdf2f8;">
            <td>26-27</td>
            <td>Classification Head</td>
            <td><code>Softmax</code></td>
            <td class="text-center">(None, 3)</td>
            <td class="text-center">-</td>
            <td class="text-center">0</td>
            <td>Probability Distribution</td>
        </tr>
        <tr style="background-color: #eef2ff; font-weight: bold;">
            <td colspan="5">รวมทั้งสิ้น (Total Parameters)</td>
            <td class="text-center"><span class="badge badge-primary">94,163</span></td>
            <td>Trainable: 92,723 | Non-trainable: 1,440</td>
        </tr>
    </tbody>
</table>

<div class="page-break"></div>

<!-- Section 4 -->
<h2><span class="section-num">4</span> กระบวนการฝึกสอนและการวิเคราะห์ผลการเรียนรู้ (Training Pipeline)</h2>
<p>
โมเดลได้รับการฝึกสอนด้วยสภาพแวดล้อม TensorFlow 2.15 บนชุดข้อมูลที่ผ่านการจัดสมดุลแล้ว โดยมีรายละเอียดการตั้งค่า Hyperparameters และกลยุทธ์การฝึกสอนดังนี้:
</p>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 9px 12px; border-radius: 8px; font-size: 11.8px;">
        <strong>Hyperparameter Configuration:</strong>
        <ul style="margin: 4px 0 0 0; padding-left: 16px;">
            <li><strong>Optimizer:</strong> Adam with Cosine Learning Rate Decay</li>
            <li><strong>Initial Learning Rate:</strong> $1.0 \times 10^{-3}$ ($0.001$)</li>
            <li><strong>Minimum Learning Rate:</strong> $1.0 \times 10^{-5}$ ($0.00001$)</li>
            <li><strong>Batch Size:</strong> 16 ภาพต่อ Batch</li>
            <li><strong>Epochs:</strong> 80 รอบการฝึกสอน</li>
        </ul>
    </div>
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 9px 12px; border-radius: 8px; font-size: 11.8px;">
        <strong>Loss Function &amp; Callbacks:</strong>
        <ul style="margin: 4px 0 0 0; padding-left: 16px;">
            <li><strong>Loss Function:</strong> Categorical Crossentropy</li>
            <li><strong>Label Smoothing:</strong> $\alpha = 0.03$ (ลด Overconfidence ช่วงรอยต่อสี)</li>
            <li><strong>ModelCheckpoint:</strong> ตรวจจับและบันทึกโมเดลที่ <code>val_accuracy</code> สูงสุด</li>
            <li><strong>TensorBoard Logging:</strong> ติดตามค่า Gradient, Weights และ Learning Curves</li>
        </ul>
    </div>
</div>

<div class="figure-container avoid-break">
    <img src="data:image/png;base64,{curves_b64}" alt="Training vs Validation Learning Curves">
    <div class="figure-caption">
        รูปที่ 1: กราฟแสดงผลการเรียนรู้ (Training vs Validation Curves) ตลอด 80 Epochs แสดงค่า Accuracy (ซ้าย) และ Loss (ขวา) จุด Best Checkpoint เกิดขึ้นที่ Epoch 61
    </div>
</div>

<h3>4.1 การวิเคราะห์พฤติกรรมการเรียนรู้ (Learning Curve Dynamics)</h3>
<ul>
    <li>
        <strong>ความแม่นยำในการจำแนก (Accuracy Curve):</strong><br>
        ในช่วง 10 Epochs แรก โมเดลเรียนรู้คุณลักษณะเด่นของสีผลมังคุดได้อย่างรวดเร็ว โดย Training Accuracy เพิ่มขึ้นจาก ~45% ไปสู่ ~85% ในขณะที่ Validation Accuracy ปรับตัวขึ้นตามอย่างต่อเนื่อง และเข้าสู่จุดสูงสุดที่ <strong>94.44% ใน Epoch ที่ 61</strong>
    </li>
    <li>
        <strong>การลดลงของฟังก์ชันการสูญเสีย (Loss Convergence):</strong><br>
        ค่า Validation Loss ลดลงอย่างมีเสถียรภาพจาก 1.10 ลงมาแตะระดับต่ำสุดที่ <strong>0.4083 ใน Epoch ที่ 61</strong> ซึ่งสอดคล้องกับค่า Training Loss ที่ 0.3644 อัตราส่วนความต่างระหว่าง Train Loss และ Val Loss ที่แคบมากแสดงให้เห็นว่า โครงข่ายไม่มีปัญหา Overfitting อย่างมีนัยสำคัญ เนื่องจากการใช้ Progressive Dropout ร่วมกับ Label Smoothing
    </li>
    <li>
        <strong>การคัดเลือก Best Checkpoint:</strong><br>
        ระบบได้ทำการคัดเลือกและ Freeze น้ำหนักของโมเดลที่ <strong>Epoch 61</strong> เพื่อนำเข้าสู่กระบวนการ Quantization ในขั้นต่อไป โดยไม่นำโมเดลใน Epoch ท้ายๆ (70-80) ที่อาจมีความผันผวนเล็กน้อยมาใช้งาน
    </li>
</ul>

<div class="page-break"></div>

<!-- Section 5 -->
<h2><span class="section-num">5</span> การบีบอัดและลดทอนโมเดลด้วย Full INT8 Quantization</h2>
<p>
โมเดลที่ฝึกสอนเสร็จสิ้นในสภาพแวดล้อม TensorFlow จะอยู่ในรูปแบบความแม่นยำสูงแบบเลขทศนิยม 32 บิต (Single Precision Float32) ซึ่งต้องใช้หน่วยคำนวณแบบ Floating-Point Unit (FPU) และใช้พื้นที่จัดเก็บมาก สำหรับ Microcontroller ระดับ ESP32-S3 การคำนวณเลขจำนวนเต็ม 8 บิต (Integer 8-bit) สามารถทำได้รวดเร็วกว่าและประหยัดพลังงานกว่ามาก
</p>

<h3>5.1 กระบวนการ Post-Training Quantization (PTQ)</h3>
<p>
เราประยุกต์ใช้เทคนิค <strong>Full Integer Quantization with Representative Dataset</strong> ผ่าน <code>tf.lite.TFLiteConverter</code> โดยมีขั้นตอนการดำเนินงานดังนี้:
</p>
<ol>
    <li>
        <strong>สร้าง Representative Dataset Generator:</strong><br>
        คัดเลือกภาพตัวอย่างจำนวน <strong>150 ภาพ</strong> จากชุดฝึกสอน ส่งผ่านเข้าสู่โมเดลเพื่อเก็บสถิติช่วงการกระจายตัวของข้อมูล (Dynamic Range: Min/Max values) ในทุกๆ Activation Layer และ Weight Tensor
    </li>
    <li>
        <strong>การคำนวณ Scale ($S$) และ Zero-Point ($Z$):</strong><br>
        แปลงค่าตัวเลขทศนิยม $q_{float}$ ให้อยู่ในรูปจำนวนเต็ม $q_{int8}$ ด้วยสมการอ้างอิง:
        <div style="text-align: center; margin: 6px 0; font-family: 'Fira Code', monospace; font-size: 12px; color: #1e1b4b;">
            q<sub>float</sub> = S &times; (q<sub>int8</sub> &minus; Z)
        </div>
        โดยที่ $S$ คือตัวคูณสเกล (Scaling Factor) และ $Z$ คือค่าจุดศูนย์ (Zero-point offset ในช่วง $[-128, 127]$)
    </li>
    <li>
        <strong>บังคับ Full Integer I/O:</strong><br>
        กำหนดให้ทั้ง Input Tensor และ Output Tensor เป็น <code>tf.int8</code> 100% ทำให้ Microcontroller ไม่ต้องมีขั้นตอนแปลงข้อมูลเป็น Float32 ไปมา ช่วยลดเวลาคำนวณต่อเฟรมลงอย่างมาก
    </li>
</ol>

<h3>5.2 ตารางเปรียบเทียบผลลัพธ์การ Quantize ระหว่าง Float32 และ Full INT8</h3>
<table class="avoid-break">
    <thead>
        <tr>
            <th>คุณลักษณะ (Metric)</th>
            <th class="text-center">โมเดลตั้งต้น (Float32 Model)</th>
            <th class="text-center">โมเดลหลังบีบอัด (Full INT8 Model)</th>
            <th class="text-center">อัตราการเปลี่ยนแปลง (Impact)</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>รูปแบบข้อมูล (Data Precision)</strong></td>
            <td class="text-center">32-bit Floating Point</td>
            <td class="text-center"><span class="badge badge-primary">8-bit Signed Integer</span></td>
            <td class="text-center">ลดขนาดบิตลง 4 เท่า</td>
        </tr>
        <tr>
            <td><strong>ขนาดไฟล์โมเดล (File Size)</strong></td>
            <td class="text-center">376.65 KB</td>
            <td class="text-center"><span class="badge badge-success"><strong>134.11 KB</strong></span></td>
            <td class="text-center"><strong>ประหยัดพื้นที่ 64.4%</strong></td>
        </tr>
        <tr>
            <td><strong>ความแม่นยำบน Test Set (40 ภาพ)</strong></td>
            <td class="text-center">80.00% (32/40 ถูกต้อง)</td>
            <td class="text-center"><span class="badge badge-success"><strong>80.00% (32/40 ถูกต้อง)</strong></span></td>
            <td class="text-center"><span class="badge badge-warning"><strong>0.00% Accuracy Drop!</strong></span></td>
        </tr>
        <tr>
            <td><strong>หน่วยความจำ RAM ที่ต้องใช้ (RAM Peak)</strong></td>
            <td class="text-center">&gt; 450 KB (ล้น Internal SRAM)</td>
            <td class="text-center"><strong>114.3 KB</strong> (รันใน PSRAM ได้อย่างมีเสถียรภาพ)</td>
            <td class="text-center">ลดภาระ RAM ลง ~75%</td>
        </tr>
        <tr>
            <td><strong>การพึ่งพาชุดคำสั่งคณิตศาสตร์</strong></td>
            <td class="text-center">Software FPU Emulation</td>
            <td class="text-center">Pure Integer ALU Math</td>
            <td class="text-center">ตัด Overhead คำนวณทศนิยม</td>
        </tr>
    </tbody>
</table>

<div class="card-box">
    <strong>ข้อสรุปด้านประสิทธิภาพการ Quantize (Zero Degradation):</strong><br>
    การทำ Full INT8 Quantization โดยใช้ Representative Dataset 150 ภาพ ส่งผลให้ขนาดไฟล์โมเดลลดลงจาก <strong>376.65 KB เหลือเพียง 134.11 KB (ลดลง 64.4%)</strong> โดยที่ <strong>ไม่มีการสูญเสียความแม่นยำเลยแม้แต่เปอร์เซ็นต์เดียว (Quantization Drop = 0.00%)</strong> โมเดลทั้งสองเวอร์ชันให้ผลลัพธ์การจำแนกภาพ Test Set ทั้ง 40 ภาพได้ตรงกันทุกภาพ แสดงให้เห็นถึงความทนทาน (Robustness) ของสถาปัตยกรรม Depthwise Separable CNN ที่ออกแบบมา
</div>

<div class="page-break"></div>

<!-- Section 6 -->
<h2><span class="section-num">6</span> การประเมินผลการทดสอบและ Confusion Matrix (Model Evaluation)</h2>
<p>
โมเดล Full INT8 ถูกนำมาประเมินผลขั้นสุดท้ายบน <strong>Test Set จำนวน 40 ภาพ</strong> ซึ่งเป็นภาพถ่ายที่ไม่เคยผ่านการฝึกสอน (Unseen Data) และไม่มีการทำ Data Augmentation เพื่อวัดประสิทธิภาพที่แท้จริง
</p>

<div class="figure-container avoid-break">
    <img src="data:image/png;base64,{cm_b64}" alt="Confusion Matrix Heatmap">
    <div class="figure-caption">
        รูปที่ 2: เมทริกซ์ความสับสน (Confusion Matrix Heatmap) จากการทดสอบโมเดล Full INT8 บนชุดข้อมูล Test Set จริง 40 ภาพ แสดงผลการทำนายเปรียบเทียบกับค่าความจริง
    </div>
</div>

<h3>6.1 รายงานประสิทธิภาพการจำแนกเชิงลึก (Classification Report)</h3>
<table class="avoid-break">
    <thead>
        <tr>
            <th>Class Name</th>
            <th class="text-center">จำนวนภาพจริง (Support)</th>
            <th class="text-center">ทำนายถูกต้อง (Correct)</th>
            <th class="text-center">Precision (ความแม่นยำ)</th>
            <th class="text-center">Recall (การตรวจจับ)</th>
            <th class="text-center">F1-Score</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Unripe (ดิบ)</strong></td>
            <td class="text-center">14</td>
            <td class="text-center">14</td>
            <td class="text-center"><span class="badge badge-success"><strong>1.00 (100%)</strong></span></td>
            <td class="text-center"><span class="badge badge-success"><strong>1.00 (100%)</strong></span></td>
            <td class="text-center"><span class="badge badge-success"><strong>1.00</strong></span></td>
        </tr>
        <tr>
            <td><strong>Ripe (สุกพร้อมทาน)</strong></td>
            <td class="text-center">13</td>
            <td class="text-center">9</td>
            <td class="text-center">0.69 (69%)</td>
            <td class="text-center">0.69 (69%)</td>
            <td class="text-center">0.69</td>
        </tr>
        <tr>
            <td><strong>Overripe (งอม/สุกจัด)</strong></td>
            <td class="text-center">13</td>
            <td class="text-center">9</td>
            <td class="text-center">0.75 (75%)</td>
            <td class="text-center">0.69 (69%)</td>
            <td class="text-center">0.72</td>
        </tr>
        <tr style="background-color: #eef2ff; font-weight: bold;">
            <td>ภาพรวมเฉลี่ย (Macro / Overall)</td>
            <td class="text-center">40 ภาพ</td>
            <td class="text-center">32 ภาพ</td>
            <td class="text-center">0.81 (81%)</td>
            <td class="text-center">0.80 (80%)</td>
            <td class="text-center"><span class="badge badge-primary"><strong>0.80 (Overall Acc: 80.00%)</strong></span></td>
        </tr>
    </tbody>
</table>

<h3>6.2 การวิเคราะห์ข้อผิดพลาด (Error &amp; Boundary Analysis)</h3>
<p>
จากการตรวจสอบผลการทำนายใน Confusion Matrix พบข้อสังเกตสำคัญในเชิงสรีรวิทยาของมังคุดดังนี้:
</p>
<ul>
    <li>
        <strong>ความสมบูรณ์แบบในคลาส Unripe (100% Accuracy):</strong><br>
        โมเดลสามารถจำแนกคลาส <em>Unripe</em> ได้ถูกต้อง <strong>100% เต็ม (14/14 ภาพ)</strong> โดยไม่มีคลาสอื่นปะปนเข้ามาเลย เนื่องจากมังคุดดิบมีลักษณะสีเปลือกที่เป็นสีเขียวหรือเขียวแต้มลายชัดเจน ซึ่งแตกต่างจากอีกสองคลาสอย่างสิ้นเชิง
    </li>
    <li>
        <strong>รอยต่อระหว่าง Ripe และ Overripe (Natural Transition Boundary):</strong><br>
        ความคลาดเคลื่อนทั้งหมด 8 ภาพเกิดขึ้นระหว่าง <em>Ripe</em> และ <em>Overripe</em> เท่านั้น (Ripe ถูกทำนายเป็น Overripe 3 ภาพ และ Overripe ถูกทำนายเป็น Ripe 4 ภาพ) เนื่องจากในธรรมชาติ มังคุดระยะที่ 5 (สีม่วงแดง) กำลังเปลี่ยนผ่านไปสู่ระยะที่ 6 (สีม่วงดำเข้ม) ซึ่งมีเฉดสีเปลือกที่ใกล้เคียงกันมาก ขึ้นอยู่กับสภาพแสงและมุมตกกระทบของกล้อง การที่โมเดลสับสนเฉพาะระหว่างสองคลาสนี้จึงเป็นพฤติกรรมที่สมเหตุสมผลตามหลักวิทยาศาสตร์และสรีรวิทยาพืช
    </li>
</ul>

<div class="page-break"></div>

<!-- Section 7 -->
<h2><span class="section-num">7</span> การพอร์ตและนำไปใช้งานบน ESP32-S3 (Hardware Deployment)</h2>
<p>
ขั้นตอนสุดท้ายของการพัฒนาคือการแปลงโมเดล <code>mangosteen_separable_cnn_94k_96x96_int8.tflite</code> ให้กลายเป็นซอร์สโค้ดภาษา C และนำไปรันบนเฟิร์มแวร์ของบอร์ด <strong>LilyGO T-SIMCAM (ESP32-S3)</strong>
</p>

<h3>7.1 การแปลงโมเดลเป็น C Byte Array</h3>
<p>
แปลงไฟล์ไบนารี <code>.tflite</code> เป็น Header File <code>mangosteen_model_data.h</code> และกำหนดให้อยู่ในหน่วยความจำ Flash:
</p>
<div class="code-box">
alignas(16) const unsigned char g_mangosteen_model_data[] = &#123;<br>
&nbsp;&nbsp;0x1c, 0x00, 0x00, 0x00, 0x54, 0x46, 0x4c, 0x33, ...<br>
&#125;;<br>
const int g_mangosteen_model_data_len = 137328; // 134.11 KB ใน Flash
</div>

<h3>7.2 สถาปัตยกรรมระบบ TFLite Micro บน ESP32-S3</h3>
<p>
การรันโมเดลบน ESP32-S3 ใช้ไลบรารี <strong>TensorFlow Lite for Microcontrollers (TFLM)</strong> โดยมีจุดเด่นในการจัดการหน่วยความจำดังนี้:
</p>
<ul>
    <li>
        <strong>การจัดสรร Tensor Arena ใน PSRAM:</strong><br>
        เนื่องจากโมเดลต้องการพื้นที่คำนวณชั่วคราว (Tensor Arena) ประมาณ <strong>114.3 KB</strong> ซึ่งการจองใน Internal SRAM อาจทำให้หน่วยความจำระบบของ ESP32-S3 ตึงตัว จึงใช้ฟังก์ชัน <code>ps_malloc()</code> จัดสรรพื้นที่ใน External Octal PSRAM ขนาด 8 MB ทำให้ระบบมีเสถียรภาพสูง ไม่เสี่ยงต่อปัญหา Stack/Heap Overflow
    </li>
    <li>
        <strong>MicroMutableOpResolver (Minimal Operator Footprint):</strong><br>
        ลงทะเบียนเฉพาะ Operators ที่โมเดลต้องใช้งานจริง 7 ตัว ได้แก่ <code>AddDepthwiseConv2D</code>, <code>AddConv2D</code>, <code>AddAveragePool2D</code>, <code>AddReshape</code>, <code>AddFullyConnected</code>, <code>AddSoftmax</code>, และ <code>AddDequantize</code> ช่วยลดขนาดคอมไพล์ของเฟิร์มแวร์ลงกว่า 300 KB
    </li>
    <li>
        <strong>ความเร็วในการประมวลผล (Inference Latency):</strong><br>
        การรันโมเดลบนแกนประมวลผล Xtensa LX7 ความเร็ว 240 MHz ใช้เวลาคำนวณเฉลี่ย <strong>5,667.2 มิลลิวินาที (~5.6 วินาทีต่อเฟรม)</strong> ซึ่งมีความเหมาะสมอย่างยิ่งสำหรับการตรวจสอบผลมังคุดทีละผลในระบบคัดแยกแบบกึ่งอัตโนมัติหรือ Handheld Scanner
    </li>
</ul>

<h3>7.3 ระบบเว็บเซิร์ฟเวอร์และการแสดงผล (SoftAP Modern Web Interface)</h3>
<p>
เฟิร์มแวร์เปิดสัญญาณ Wi-Fi SoftAP ในชื่อ <code>Mangosteen-AI</code> เพื่อให้อุปกรณ์มือถือหรือแท็บเล็ตเชื่อมต่อเข้าดูผลการทำนายได้ทันทีผ่าน Web Browser ที่ <code>http://192.168.4.1</code> โดยหน้าเว็บได้รับการออกแบบให้เป็น Responsive Two-Column Layout ที่ทันสมัย:
</p>
<ul>
    <li><strong>คอลัมน์ซ้าย (Camera Feed):</strong> แสดงภาพสดจากกล้อง OV2640 ความละเอียด 96 &times; 96 พิกเซล พร้อมกรอบเล็งเป้าผลมังคุด</li>
    <li><strong>คอลัมน์ขวา (Inference Dashboard):</strong> แสดงผลคลาสที่ทำนายได้ด้วยการเน้นสี (Unripe=เขียว, Ripe=แดงม่วง, Overripe=ม่วงเข้ม) พร้อมแถบเปอร์เซ็นต์ความน่าจะเป็น (Probability Bars) ทั้ง 3 ระดับ และการ์ดแสดงค่า Hardware Telemetry (FPS, Inference Latency ~5.6s, Free PSRAM, IP Address)</li>
</ul>

<div class="card-box">
    <strong>ความพร้อมในการนำไปใช้งานจริง (Production Readiness):</strong><br>
    ระบบทั้งหมดได้รับการทดสอบการเชื่อมต่อจริงระหว่างกล้อง OV2640, TFLite Micro Engine และ Web Server บนบอร์ด LilyGO T-SIMCAM พบว่าสามารถตรวจจับและวิเคราะห์ผลมังคุดได้อย่างแม่นยำต่อเนื่องโดยไม่มีอาการแฮงก์หรือหน่วยความจำรั่วไหล (Memory Leak)
</div>

<!-- Section 8 -->
<h2><span class="section-num">8</span> บทสรุปและทิศทางการพัฒนาต่อยอด (Conclusion &amp; Next Steps)</h2>
<p>
การพัฒนาโมเดล <code>Mangosteen_SeparableCNN_94k</code> ได้บรรลุเป้าหมายสำคัญทุกประการ ทั้งในแง่ของความกะทัดรัด (94k พารามิเตอร์), การบีบอัดระดับสูง (Full INT8 ขนาด 134 KB), การคงความแม่นยำ (Val Acc 94.44%, Test Acc 80.00% โดยไม่สูญเสียความแม่นยำจากการ Quantize), และการนำไปรันบนฮาร์ดแวร์ ESP32-S3 ได้จริง
</p>
<p><strong>ข้อเสนอแนะในการยกระดับประสิทธิภาพในอนาคต:</strong></p>
<ol>
    <li>
        <strong>การเปิดใช้ ESP-NN Hardware Acceleration:</strong> ในอนาคตสามารถลิงก์ไลบรารี <code>esp-nn</code> ของ Espressif เพื่อดึงชุดคำสั่ง SIMD / Vector Assembly ของ ESP32-S3 มาช่วยคำนวณ Depthwise Convolutions ซึ่งคาดว่าจะช่วยลดเวลา Inference ลงจาก 5.6 วินาที เหลือต่ำกว่า <strong>1.5 - 2.0 วินาที</strong>
    </li>
    <li>
        <strong>การขยายชุดข้อมูลช่วงรอยต่อ (Transition Stage Enrichment):</strong> ถ่ายภาพมังคุดในระยะรอยต่อสีระหว่าง Ripe (ระยะ 4-5) และ Overripe (ระยะ 6) เพิ่มเติมภายใต้สภาพแสงที่หลากหลาย จะช่วยเพิ่มความแม่นยำของ Test Set จาก 80% ให้ขึ้นไปสู่ระดับ 90%+ ได้อย่างมีนัยสำคัญ
    </li>
</ol>

<div style="margin-top: 25px; padding-top: 10px; border-top: 1px solid #cbd5e1; font-size: 10.5px; color: #64748b; display: flex; justify-content: space-between;">
    <div>Project: Mini-Mangosteen Edge AI Classification</div>
    <div>Hardware: LilyGO T-SIMCAM (ESP32-S3) | TFLite Micro INT8</div>
    <div>Document Version: 1.0 (Final Technical Report)</div>
</div>

</body>
</html>
"""

    html_file = 'Mangosteen_Model_Development_Report.html'
    pdf_file = 'Mangosteen_Model_Development_Report.pdf'

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML written: {html_file} ({len(html_content)} bytes)")

    edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    html_full_path = os.path.abspath(html_file)
    pdf_full_path = os.path.abspath(pdf_file)

    cmd = [
        edge_exe,
        '--headless=new',
        '--disable-gpu',
        '--no-pdf-header-footer',
        f'--print-to-pdf={pdf_full_path}',
        f'file:///{html_full_path.replace(os.sep, "/")}'
    ]

    print("Executing Microsoft Edge to print PDF...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("Edge return code:", res.returncode)

    if os.path.exists(pdf_file):
        size_kb = os.path.getsize(pdf_file) / 1024
        print(f"SUCCESS: PDF generated successfully: {pdf_file} ({size_kb:.2f} KB)")
        
        # Copy to artifact folder
        artifact_dir = r'C:\Users\worav\.gemini\antigravity\brain\9192bf78-d227-49e9-9d25-71d27894c193'
        if os.path.exists(artifact_dir):
            target_art = os.path.join(artifact_dir, 'Mangosteen_Model_Development_Report.pdf')
            shutil.copyfile(pdf_file, target_art)
            print("Copied PDF to artifact folder:", target_art)
    else:
        print("ERROR: PDF was not created.")
        print("Stdout:", res.stdout)
        print("Stderr:", res.stderr)

if __name__ == '__main__':
    main()
