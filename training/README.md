# 🧠 Training Workspace (พื้นที่สำหรับเตรียมข้อมูลและเทรนโมเดลใหม่)

โฟลเดอร์นี้รวบรวมเครื่องมือ สคริปต์ และสมุดงาน (Notebook) สำหรับการเทรนโมเดลจำแนกระดับความสุกของมังคุดสำหรับชิป **ESP32-S3 (TensorFlow Lite Micro)**

---

## 🗂️ รายการไฟล์ในโฟลเดอร์นี้

| ไฟล์ | หน้าที่และการใช้งาน |
| :--- | :--- |
| `colab_notebook.ipynb` | **Google Colab Notebook:** เหมาะสำหรับการเทรนบนคลาวด์โดยใช้ GPU ฟรี (T4 GPU) |
| `colab_notebook_code.txt` | **Text Code:** สำเนาโค้ดข้อความล้วน สำหรับคัดลอกโค้ดไปวางใน Colab ได้สะดวกรวดเร็ว |
| `train_edge_model.py` | **Local Training Script:** สคริปต์เทรนบนเครื่องคอมพิวเตอร์ของคุณ พร้อม Full INT8 Quantization และส่งออกไฟล์ C++ อัตโนมัติ |
| `augment_and_save_dataset.py` | **Dataset Augmentation Tool:** เครื่องมือช่วยสร้างภาพสังเคราะห์เพิ่มให้คลาสที่มีภาพน้อย เพื่อสร้างความสมดุลให้ Dataset |

---

## 🚀 ลำดับขั้นตอนการเทรนโมเดลใหม่ (Quick Start)

### ขั้นตอนที่ 1: เตรียมชุดข้อมูล (Dataset)
นำภาพถ่ายผลมังคุดใส่ในโฟลเดอร์ `dataset/` ที่รูทของโปรเจกต์:
- `dataset/train/` (`overripe`, `ripe`, `unripe`)
- `dataset/val/` (`overripe`, `ripe`, `unripe`)
- `dataset/test/` (`overripe`, `ripe`, `unripe`)

*(อ่านข้อแนะนำในการถ่ายและเตรียมภาพเพิ่มเติมได้ที่ [`dataset/README.md`](../dataset/README.md))*

---

### ขั้นตอนที่ 2: เริ่มการเทรนโมเดล (เลือกวิธีใดวิธีหนึ่ง)

#### ทางเลือก ก: เทรนบน Google Colab (แนะนำ — มี GPU ฟรี ไม่เปลืองทรัพยากรเครื่อง)
1. เปิด [Google Colab](https://colab.research.google.com/) แล้วอัปโหลดไฟล์ `colab_notebook.ipynb`
2. เปลี่ยน Runtime เป็น GPU (`Runtime` -> `Change runtime type` -> `T4 GPU`)
3. Zip โฟลเดอร์ `dataset` แล้วอัปโหลดขึ้น Colab หรือวางใน Google Drive
4. รันโค้ดตามลำดับจนถึงขั้นตอนส่งออกโมเดล `.tflite`
5. ดาวน์โหลดไฟล์โมเดล `.tflite` นำมาวางไว้ในโฟลเดอร์ `models/` ของโปรเจกต์นี้

#### ทางเลือก ข: เทรนบนเครื่องคอมพิวเตอร์ของคุณ (Local)
เปิด Terminal ที่รูทโปรเจกต์แล้วรัน:
```bash
python training/train_edge_model.py
```
*(สคริปต์จะทำการโหลดภาพ, เพิ่มความสมดุลข้อมูล, เทรนโมเดล MobileNetV2, ทำ Full INT8 Quantization, และส่งออกไฟล์โมเดลไปยังโฟลเดอร์ `models/` และ `src/` ให้อัตโนมัติทันที)*

---

### ขั้นตอนที่ 3: คอมไพล์และแฟลชลงบอร์ด ESP32-S3
เมื่อได้ไฟล์โมเดลมาอยู่ในโฟลเดอร์ `models/` เรียบร้อยแล้ว ให้รัน:
```bash
python setup.py
```
*(หรือดับเบิลคลิก `setup.bat` บน Windows)*  
สคริปต์จะแปลงโมเดลลง C++ Header/Source, ตรวจสอบพอร์ตเชื่อมต่อ, และคอมไพล์แฟลชลงบอร์ด ESP32-S3 ให้พร้อมใช้งานทันที!
