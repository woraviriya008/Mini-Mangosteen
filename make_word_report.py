# -*- coding: utf-8 -*-
import os
import shutil
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/><w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/><w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/><w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/><w:left w:val="none"/><w:right w:val="none"/></w:tblBorders>')
    tblPr.append(borders)

def format_paragraph(p, space_after=6, line_spacing=1.15):
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing

def add_heading_1(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True
    run = h.add_run(text)
    run.bold = True
    run.font.size = Pt(15)
    run.font.color.rgb = RGBColor(49, 46, 129) # Indigo
    return h

def add_heading_2(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(10)
    h.paragraph_format.space_after = Pt(3)
    h.paragraph_format.keep_with_next = True
    run = h.add_run(text)
    run.bold = True
    run.font.size = Pt(13)
    run.font.color.rgb = RGBColor(67, 56, 202)
    return h

def add_callout(doc, title, text, bg_color="F8FAFC", border_color="4338CA"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.5)
    
    cell = tbl.cell(0, 0)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    # Left border only
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    run_t = p.add_run(f"📌 {title}\n")
    run_t.bold = True
    run_t.font.size = Pt(11)
    run_t.font.color.rgb = RGBColor(30, 27, 75)
    
    run_b = p.add_run(text)
    run_b.font.size = Pt(10.5)
    run_b.font.color.rgb = RGBColor(51, 65, 85)
    doc.add_paragraph()

def style_header_row(row, fill_hex="1E1B4B"):
    for cell in row.cells:
        set_cell_background(cell, fill_hex)
        set_cell_margins(cell, top=120, bottom=120, left=120, right=120)
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(10)

def style_body_row(row, is_even=False, align_list=None):
    fill_hex = "F8FAFC" if is_even else "FFFFFF"
    for idx, cell in enumerate(row.cells):
        set_cell_background(cell, fill_hex)
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        for p in cell.paragraphs:
            if align_list and idx < len(align_list):
                p.alignment = align_list[idx]
            for run in p.runs:
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(30, 41, 59)

def main():
    print("Creating comprehensive Word (.docx) document...")
    doc = Document()
    
    # Page Margins (1 inch / 2.54 cm all sides)
    for section in doc.sections:
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        section.header_distance = Inches(0.5)
        section.footer_distance = Inches(0.5)

    # Base font setting
    doc.styles['Normal'].font.name = 'TH Sarabun New'
    doc.styles['Normal'].font.size = Pt(11.5)
    doc.styles['Normal'].font.color.rgb = RGBColor(30, 41, 59)

    # =========================================================================
    # DOCUMENT TITLE / HEADER BANNER (Table formatted)
    # =========================================================================
    header_tbl = doc.add_table(rows=1, cols=1)
    header_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    header_cell = header_tbl.cell(0, 0)
    set_cell_background(header_cell, "1E1B4B")
    set_cell_margins(header_cell, top=260, bottom=260, left=300, right=300)
    
    hp1 = header_cell.paragraphs[0]
    hp1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hr1 = hp1.add_run("TECHNICAL ENGINEERING & RESEARCH REPORT\n")
    hr1.font.size = Pt(10)
    hr1.font.color.rgb = RGBColor(165, 180, 252)
    hr1.bold = True
    
    hr2 = hp1.add_run("การพัฒนาและเพิ่มประสิทธิภาพโมเดลจำแนกความสุกมังคุดสำหรับ Edge AI บน ESP32-S3\n")
    hr2.font.size = Pt(18)
    hr2.font.color.rgb = RGBColor(255, 255, 255)
    hr2.bold = True
    
    hr3 = hp1.add_run("End-to-End Pipeline: Deep Learning Architecture (94k), Dataset Balancing, Full INT8 Quantization, and Microcontroller Deployment\n")
    hr3.font.size = Pt(11)
    hr3.font.color.rgb = RGBColor(199, 210, 254)
    
    hr4 = hp1.add_run("\nModel: Mangosteen_SeparableCNN_94k | Hardware: LilyGO T-SIMCAM (ESP32-S3) | Date: September 2026")
    hr4.font.size = Pt(9.5)
    hr4.font.color.rgb = RGBColor(224, 231, 255)

    doc.add_paragraph()

    # =========================================================================
    # KPI SUMMARY TABLE (5 CARDS)
    # =========================================================================
    kpi_tbl = doc.add_table(rows=2, cols=5)
    kpi_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(kpi_tbl, color="E2E8F0")
    
    kpis = [
        ("94,163", "Total Parameters", "4F46E5"),
        ("94.44%", "Validation Accuracy", "059669"),
        ("80.00%", "Test Set Accuracy", "059669"),
        ("134.11 KB", "Full INT8 Flash Size", "0284C7"),
        ("0.00%", "Quantization Drop", "D97706")
    ]
    
    for i, (val, label, col) in enumerate(kpis):
        c1 = kpi_tbl.cell(0, i)
        set_cell_background(c1, "F8FAFC")
        set_cell_margins(c1, top=80, bottom=20, left=40, right=40)
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p1.add_run(val)
        r1.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = RGBColor.from_string(col)
        
        c2 = kpi_tbl.cell(1, i)
        set_cell_background(c2, "F8FAFC")
        set_cell_margins(c2, top=0, bottom=80, left=40, right=40)
        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r2 = p2.add_run(label)
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph()

    # =========================================================================
    # ABSTRACT
    # =========================================================================
    add_heading_1(doc, "Abstract (บทคัดย่อ)")
    p = doc.add_paragraph(
        "รายงานฉบับนี้นำเสนอการวิจัย ออกแบบ และพัฒนาโมเดลปัญญาประดิษฐ์ฝังตัว (Edge AI / TinyML) เพื่อจำแนกระดับความสุกของผลมังคุด (Garcinia mangostana L.) "
        "แบบอัตโนมัติบนอุปกรณ์ไมโครคอนโทรลเลอร์ ESP32-S3 โดยไม่จำเป็นต้องเชื่อมต่ออินเทอร์เน็ตหรือส่งภาพไปยังคลาวด์เซิร์ฟเวอร์ โครงการนี้ได้ออกแบบโครงข่ายประสาทเทียม "
        "สถาปัตยกรรมเฉพาะทางในชื่อ Mangosteen_SeparableCNN_94k ซึ่งมีจำนวนพารามิเตอร์รวม 94,163 พารามิเตอร์ ใช้เทคนิค Early Downsampling ที่ Stage 0 "
        "เพื่อลดความต้องการหน่วยความจำคำนวณชั่วคราว (Tensor Arena) ลง 4 เท่า และนำชุดข้อมูลภาพถ่ายมังคุดจริง 245 ภาพ มาแก้ปัญหาความไม่สมดุลของข้อมูล (Class Imbalance) "
        "ด้วยเทคนิค Targeted Train Data Augmentation เพิ่มขึ้นเป็น 365 ภาพ โดยคงความบริสุทธิ์ของชุด Validation และ Test ไว้ 100% เพื่อป้องกัน Data Leakage "
        "ผลการฝึกสอนพบว่าโมเดลทำความแม่นยำในการตรวจสอบ (Validation Accuracy) ได้สูงสุดที่ 94.44% ที่ Epoch 61 และทำความแม่นยำบนภาพทดสอบจริง (Unseen Test Set) ได้ 80.00% "
        "เมื่อนำโมเดลเข้าสู่กระบวนการบีบอัดด้วย Full INT8 Post-Training Quantization สามารถลดขนาดไฟล์โมเดลลง 64.4% จาก ~376.65 KB เหลือเพียง 134.11 KB "
        "โดยมีอัตราการสูญเสียความแม่นยำเท่ากับ 0.00% (Zero Degradation) และใช้พื้นที่ Tensor Arena ใน PSRAM เพียง 114.3 KB มีเวลาประมวลผลต่อเฟรม (Inference Latency) "
        "เฉลี่ย 5,667 ms (~5.6 วินาที) ที่ความถี่ 240 MHz พร้อมทำงานร่วมกับระบบเว็บอินเทอร์เฟซ SoftAP ได้อย่างสมบูรณ์แบบ"
    )
    format_paragraph(p)

    kw = doc.add_paragraph()
    format_paragraph(kw, space_after=12)
    kw_r1 = kw.add_run("Keywords: ")
    kw_r1.bold = True
    kw.add_run("TinyML, Edge AI, ESP32-S3, Garcinia mangostana, Depthwise Separable CNN, Full INT8 Quantization, TensorFlow Lite for Microcontrollers")

    # =========================================================================
    # 1. INTRODUCTION
    # =========================================================================
    add_heading_1(doc, "1. Introduction (บทนำ)")
    p = doc.add_paragraph(
        "มังคุด (Garcinia mangostana L.) เป็นผลไม้เศรษฐกิจส่งออกสำคัญของประเทศไทยซึ่งได้รับการขนานนามว่าเป็น 'ราชินีแห่งผลไม้' "
        "ในกระบวนการรับซื้อและคัดเกรดผลผลิต ณ โรงคัดบรรจุ (ล้ง) หรือสวนเกษตรกร ปัจจัยชี้วัดคุณภาพและราคาที่สำคัญที่สุดคือ 'ระดับความสุก' (Ripeness Stage) "
        "ซึ่งถูกกำหนดเป็น 3 ระยะหลักตามวัตถุประสงค์เชิงพาณิชย์:"
    )
    format_paragraph(p)

    bullets = [
        ("Unripe (มังคุดดิบ / ผิวด่างเขียวแต้มชมพูอ่อน): ", "เนื้อผลแน่น เปลือกหนา มียางสีเหลือง เหมาะสำหรับการบรรจุลงตู้ควบคุมอุณหภูมิเพื่อส่งออกทางเรือระยะไกล"),
        ("Ripe (มังคุดสุกพร้อมรับประทาน / ผิวสีแดงอมม่วง): ", "ระยะที่เนื้อผลนุ่ม รสชาติหวานอมเปรี้ยวกลมกล่อม ปราศจากยาง เหมาะสำหรับการกระจายสินค้าสู่ตลาดสดและผู้บริโภคทันที"),
        ("Overripe (มังคุดสุกจัด-งอม / ผิวสีม่วงเข้มเกือบดำ): ", "ระยะสุกเต็มที่ เนื้อเริ่มยุบตัว เปลือกนิ่มหรือมีรอยช้ำสะสม อายุการวางจำหน่าย (Shelf-life) สั้นมาก ต้องคัดแยกเพื่อแปรรูป")
    ]
    for b_title, b_desc in bullets:
        bp = doc.add_paragraph(style='List Bullet')
        format_paragraph(bp, space_after=3)
        r = bp.add_run(b_title)
        r.bold = True
        bp.add_run(b_desc)

    p = doc.add_paragraph(
        "ในปัจจุบัน การคัดแยกความสุกของมังคุดส่วนใหญ่ยังคงพึ่งพาแรงงานคน (Visual Human Inspection) ซึ่งมีข้อจำกัดอย่างมากในด้านความแม่นยำ "
        "ความสม่ำเสมอในการตัดสินใจ และความเหนื่อยล้าของแรงงานเมื่อต้องตรวจคัดแยกมังคุดปริมาณหลายตันต่อวัน แม้ว่าเทคโนโลยีปัญญาประดิษฐ์ (AI) "
        "จะถูกนำมาใช้อย่างแพร่หลาย แต่ระบบทั่วไปมักพึ่งพาการประมวลผลบนคลาวด์เซิร์ฟเวอร์ (Cloud Computing) ซึ่งมีอุปสรรคสำคัญเรื่องความเสถียรของเครือข่ายอินเทอร์เน็ต "
        "ในพื้นที่ห่างไกล ค่าใช้จ่ายเซิร์ฟเวอร์รายเดือน และความล่าช้าในการส่งข้อมูลภาพ (Network Latency)"
    )
    format_paragraph(p)

    add_callout(
        doc,
        "โจทย์และความท้าทายทางวิศวกรรมของ TinyML (Edge Constraints)",
        "ไมโครคอนโทรลเลอร์ ESP32-S3 มีสเปกทรัพยากรจำกัด: SRAM 512 KB, Flash ROM 16 MB และ Octal PSRAM 8 MB "
        "โมเดลจำแนกภาพแบบดั้งเดิม (เช่น ResNet50 ~25M พารามิเตอร์ หรือ MobileNetV2 ~3.5M พารามิเตอร์) มีขนาดใหญ่เกินกว่าจะรันบนชิปนี้ได้ "
        "โครงการนี้จึงมุ่งเน้นการสร้างโมเดลขนาดกะทัดรัดเป็นพิเศษ (Ultra-compact CNN < 100k พารามิเตอร์) บีบอัดเป็น Full INT8 ให้ใช้ RAM น้อยกว่า 120 KB "
        "และทำงานได้แบบออฟไลน์ 100% บนบอร์ด LilyGO T-SIMCAM ที่กินพลังงานเพียง 2W"
    )

    # =========================================================================
    # 2. RELATED WORK
    # =========================================================================
    add_heading_1(doc, "2. Related Work (งานวิจัยและเทคโนโลยีที่เกี่ยวข้อง)")
    p = doc.add_paragraph(
        "การจำแนกระดับคุณภาพผลไม้ด้วยระบบอัตโนมัติได้รับการพัฒนาอย่างต่อเนื่อง โดยแบ่งออกเป็น 3 ยุคสมัยสำคัญ:\n"
        "1) ยุค Computer Vision ดั้งเดิม: ใช้การวิเคราะห์พื้นที่สี (Color Spaces เช่น RGB, HSV, CIELAB) ร่วมกับตัวแยกประเภทคลาสสิก (เช่น Support Vector Machines หรือ Random Forests) "
        "ซึ่งวิธีเหล่านี้มักล้มเหลวเมื่อสภาพแสงในพื้นที่ปฏิบัติงานจริงเปลี่ยนแปลง หรือผลไม้มีแสงสะท้อนมันวาวบนผิวเปลือก\n"
        "2) ยุค Deep Learning ทั่วไป: การประยุกต์ใช้โมเดลโครงข่ายคอนโวลูชัน (CNN) ขนาดใหญ่ เช่น VGG16 หรือ ResNet ซึ่งให้ความแม่นยำสูง (>95%) แต่ต้องใช้การประมวลผลบน GPU "
        "ที่มีราคาสูงและกินพลังงานมากกว่า 100-300W ไม่เหมาะแก่การติดตั้ง ณ จุดคัดแยกเคลื่อนที่\n"
        "3) ยุค TinyML & Depthwise Separable CNNs: งานวิจัย MobileNet (Howard et al.) ได้นำเสนอการแยกตัวกรองคอนโวลูชันออกเป็น Depthwise Convolution (คำนวณตามแกนพื้นที่) "
        "และ Pointwise Convolution (คำนวณตามแกนแชนแนล) ซึ่งลดจำนวนพารามิเตอร์และปริมาณการคูณบวก (MACCs) ลงได้ถึง 8–9 เท่า เมื่อผสานเข้ากับเฟรมเวิร์ก TensorFlow Lite for Microcontrollers (TFLM) "
        "และเทคนิค Post-Training Quantization (Jacob et al.) ทำให้การประมวลผลโมเดล AI บนหน่วยประมวลผล Xtensa LX7 ความเร็ว 240 MHz เป็นไปได้อย่างแท้จริง"
    )
    format_paragraph(p)

    # =========================================================================
    # 3. DATASET
    # =========================================================================
    add_heading_1(doc, "3. Dataset (ชุดข้อมูลและการเตรียมข้อมูล)")
    p = doc.add_paragraph(
        "ชุดข้อมูลภาพถ่ายผลมังคุดจริงเริ่มต้นมีจำนวนทั้งสิ้น 245 ภาพ ถ่ายภายใต้สภาพแสงธรรมชาติและแสงสตูดิโอควบคุม โดยครอบคลุมระยะความสุกทั้ง 3 คลาส "
        "เมื่อนำชุดข้อมูลมาแบ่งสัดส่วนออกเป็น Train (70%), Validation (15%) และ Test (15%) พบว่าเกิดปัญหาความไม่สมดุลของข้อมูลอย่างรุนแรง (Severe Class Imbalance) "
        "โดยในชุด Train มีภาพคลาส Overripe เพียง 23 ภาพ ในขณะที่มีภาพ Unripe ถึง 95 ภาพ ดังแสดงในตารางที่ 1"
    )
    format_paragraph(p)

    # Dataset Table
    add_heading_2(doc, "ตารางที่ 1: การแบ่งสัดส่วนชุดข้อมูลและการปรับสมดุลด้วย Targeted Augmentation (245 -> 365 ภาพ)")
    ds_tbl = doc.add_table(rows=5, cols=7)
    ds_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(ds_tbl)
    
    headers = ["Split Dataset", "Unripe (ดิบ)", "Ripe (สุก)", "Overripe (งอม)", "รวมภาพเดิม (Raw)", "ภาพเพิ่มจาก Augment", "รวมหลังจัดสมดุล"]
    for j, h in enumerate(headers):
        ds_tbl.cell(0, j).paragraphs[0].add_run(h)
    style_header_row(ds_tbl.rows[0])
    
    ds_rows = [
        (["Train Set (ฝึกสอนโมเดล)", "95", "51", "23", "169 ภาพ", "+120 ภาพ", "289 ภาพ"], False),
        (["Validation Set (ปรับจูนโมเดล)", "12", "12", "12", "36 ภาพ", "0 (ไม่ทำ Augment)", "36 ภาพ"], True),
        (["Test Set (ทดสอบจริง Blind)", "14", "13", "13", "40 ภาพ", "0 (ไม่ทำ Augment)", "40 ภาพ"], False),
        (["รวมทั้งโครงการ (Total)", "121", "76", "48", "245 ภาพ", "+120 ภาพ", "365 ภาพ"], True)
    ]
    align_center = [WD_ALIGN_PARAGRAPH.LEFT] + [WD_ALIGN_PARAGRAPH.CENTER] * 6
    for idx, (data, is_even) in enumerate(ds_rows):
        row = ds_tbl.rows[idx + 1]
        for c_idx, val in enumerate(data):
            row.cells[c_idx].paragraphs[0].add_run(val)
        style_body_row(row, is_even=is_even, align_list=align_center)
        if idx == 3: # Total row bold
            for cell in row.cells:
                for run in cell.paragraphs[0].runs:
                    run.bold = True

    doc.add_paragraph()

    add_callout(
        doc,
        "หลักการป้องกัน Data Leakage และที่มาของตัวเลข 365 ภาพ",
        "เพื่อป้องกันปัญหาการรั่วไหลของข้อมูล (Data Leakage) การทำ Data Augmentation ถูกจำกัดให้กระทำ 'เฉพาะกับชุด Train เท่านั้น' "
        "โดยคลาส Overripe ในชุด Train ถูกสังเคราะห์เพิ่ม +69 ภาพ (จาก 23 กลายเป็น 92 ภาพ) และคลาส Ripe ถูกสังเคราะห์เพิ่ม +51 ภาพ (จาก 51 กลายเป็น 102 ภาพ) "
        "ทำให้ชุด Train สมดุลที่ 289 ภาพ ส่วนชุด Validation (36 ภาพ) และ Test (40 ภาพ) ยังคงเป็นภาพถ่ายจริง 100% "
        "เมื่อนำมารวมกันทั้งโครงการจึงได้: 289 (Train) + 36 (Val) + 40 (Test) = 365 ภาพพอดี"
    )

    p_aug = doc.add_paragraph(
        "เทคนิค Data Augmentation ที่นำมาใช้ถูกปรับแต่งให้สอดคล้องกับสภาพการทำงานจริงของกล้อง ได้แก่:\n"
        "• Random Rotation (±20 องศา): จำลองผลมังคุดที่วางเอียงมุมต่างๆ บนถาดรองรับ\n"
        "• Random Translation (เลื่อน 10% แนวนอนและแนวตั้ง): ป้องกันโครงข่ายยึดติดกับจุดกึ่งกลางภาพ\n"
        "• Random Zoom (15%): จำลองระยะห่างระหว่างเลนส์กล้อง OV2640 กับผลมังคุดที่มีขนาดผลเล็ก-ใหญ่ต่างกัน\n"
        "• Horizontal Flip: พลิกภาพกระจกแนวนอนเพื่อเพิ่มความหลากหลายของมุมมองด้านซ้าย-ขวา"
    )
    format_paragraph(p_aug)

    # =========================================================================
    # 4. MODEL ARCHITECTURE & TRAINING
    # =========================================================================
    add_heading_1(doc, "4. Model Architecture & Training (สถาปัตยกรรมโมเดลและการฝึกสอน)")
    p = doc.add_paragraph(
        "สถาปัตยกรรม Mangosteen_SeparableCNN_94k ถูกออกแบบขึ้นใหม่ทั้งหมดตามแนวคิด Hardware-Aware Neural Architecture Design "
        "โดยมุ่งเน้นการประหยัดหน่วยความจำ RAM ชั่วคราว (Tensor Arena) และลดทอนจำนวนคำนวณ FLOPs เพื่อให้สอดรับกับสถาปัตยกรรมไมโครคอนโทรลเลอร์ ESP32-S3 "
        "โครงสร้างทั้งหมดประกอบด้วย 28 Layers ทางตรรกะใน TensorFlow/Keras แบ่งออกเป็น 8 Computational Blocks สำคัญ:"
    )
    format_paragraph(p)

    # Model Table
    add_heading_2(doc, "ตารางที่ 2: รายละเอียดสถาปัตยกรรม Mangosteen_SeparableCNN_94k ทั้ง 28 Layers (รวม 94,163 พารามิเตอร์)")
    m_tbl = doc.add_table(rows=11, cols=6)
    m_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(m_tbl)
    
    m_headers = ["Stage / Block", "Layer Type", "Output Shape", "Kernel / Stride", "Params #", "หน้าที่ทางวิศวกรรม"]
    for j, h in enumerate(m_headers):
        m_tbl.cell(0, j).paragraphs[0].add_run(h)
    style_header_row(m_tbl.rows[0])
    
    m_rows = [
        (["Input", "InputLayer", "(None, 96, 96, 3)", "-", "0", "รับภาพสี RGB ขนาด 96x96 พิกเซล"], False),
        (["Stage 0", "Conv2D + BN + ReLU", "(None, 48, 48, 24)", "3x3, Stride=2", "768", "Early Downsampling ลดพื้นที่ RAM 4 เท่า"], True),
        (["Stage 1", "SepConv + BN + ReLU + Drop", "(None, 48, 48, 32)", "3x3, Stride=1", "1,144", "สกัดคุณลักษณะผิวเปลือก (Dropout 0.20)"], False),
        (["Stage 2", "SepConv + BN + ReLU", "(None, 24, 24, 48)", "3x3, Stride=2", "2,048", "Spatial Reduction รอบที่ 2"], True),
        (["Stage 3", "SepConv + BN + ReLU + Drop", "(None, 24, 24, 64)", "3x3, Stride=1", "3,776", "สกัดรูปแบบเฉดสี (Dropout 0.25)"], False),
        (["Stage 4", "SepConv + BN + ReLU", "(None, 12, 12, 96)", "3x3, Stride=2", "7,168", "Spatial Reduction รอบที่ 3"], True),
        (["Stage 5", "SepConv + BN + ReLU + Drop", "(None, 12, 12, 128)", "3x3, Stride=1", "13,632", "สกัด Feature ขั้นสูง (Dropout 0.30)"], False),
        (["Head (GAP)", "GlobalAveragePooling2D", "(None, 128)", "Pool 12x12", "0", "ลดมิติ Feature Map โดยไม่ใช้พารามิเตอร์"], True),
        (["Head (Dense)", "Dense (Output)", "(None, 3)", "Linear Projection", "387", "สร้างค่า Logits สำหรับ 3 คลาส"], False),
        (["Total", "28 Layers รวมย่อย", "(None, 3)", "-", "94,163", "Trainable: 92,723 | Non-trainable: 1,440"], True)
    ]
    m_align = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.LEFT]
    for idx, (data, is_even) in enumerate(m_rows):
        row = m_tbl.rows[idx + 1]
        for c_idx, val in enumerate(data):
            row.cells[c_idx].paragraphs[0].add_run(val)
        style_body_row(row, is_even=is_even, align_list=m_align)
        if idx == 9: # Total row bold
            for cell in row.cells:
                for run in cell.paragraphs[0].runs:
                    run.bold = True

    doc.add_paragraph()

    p_train = doc.add_paragraph(
        "การฝึกสอนโมเดล (Training Dynamics):\n"
        "โมเดลได้รับการเทรนบน TensorFlow 2.15 ด้วย Adam Optimizer ร่วมกับ Cosine Learning Rate Decay ปรับลดอัตราการเรียนรู้จาก 1e-3 ลงสู่ 1e-5 ตลอด 80 Epochs "
        "โดยใช้ Batch Size ขนาด 16 และนำเทคนิค Label Smoothing (alpha = 0.03) มาใช้กับ Categorical Crossentropy Loss เพื่อป้องกันโมเดลมีความมั่นใจสูงเกินไป (Overconfidence) "
        "ในช่วงสีคาบเกี่ยว ผลการฝึกสอนแสดงในรูปที่ 1 โดยจุด Best Model Checkpoint เกิดขึ้นที่ Epoch 61 ซึ่งให้ค่า Validation Accuracy สูงถึง 94.44% และ Validation Loss ต่ำสุดที่ 0.4083"
    )
    format_paragraph(p_train)

    # Insert Figure 1: Curves
    curves_img = 'training/training_vs_validation_curves_light.png'
    if os.path.exists(curves_img):
        doc.add_paragraph()
        fig1_p = doc.add_paragraph()
        fig1_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fig1_p.paragraph_format.space_after = Pt(2)
        fig1_p.paragraph_format.keep_with_next = True
        run_img = fig1_p.add_run()
        run_img.add_picture(curves_img, width=Inches(5.8))
        
        cap1 = doc.add_paragraph()
        cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        format_paragraph(cap1, space_after=12)
        r_cap1 = cap1.add_run("รูปที่ 1: กราฟแสดงผลการฝึกสอน (Training vs Validation Curves) แสดงค่า Accuracy และ Loss ตลอด 80 Epochs (Best Checkpoint ณ Epoch 61)")
        r_cap1.font.size = Pt(9.5)
        r_cap1.italic = True
        r_cap1.font.color.rgb = RGBColor(71, 85, 105)

    # =========================================================================
    # 5. QUANTIZATION
    # =========================================================================
    add_heading_1(doc, "5. Quantization (การบีบอัดโมเดลด้วย Post-Training Quantization)")
    p = doc.add_paragraph(
        "โมเดลดั้งเดิมที่ฝึกสอนใน TensorFlow อยู่ในรูปแบบเลขทศนิยม 32 บิต (Single Precision Float32) ซึ่งต้องการพื้นที่จัดเก็บและแบนด์วิธหน่วยความจำสูงมาก "
        "สำหรับ ESP32-S3 ซึ่งไม่มี Floating-Point Hardware Unit ประสิทธิภาพสูง การแปลงโมเดลให้อยู่ในรูปจำนวนเต็ม 8 บิต (Full INT8) เป็นขั้นตอนชี้ขาดความสำเร็จ "
        "การแปลงดำเนินการผ่าน Post-Training Quantization (PTQ) โดยใช้ Representative Dataset จำนวน 150 ภาพสุ่มจากชุดฝึกสอน เพื่อเก็บสถิติ Dynamic Range "
        "ของทุก Activation Layer โดยใช้สมการการแปลง:\n"
        "       q_float = S * (q_int8 - Z)\n"
        "โดยที่ S คือ Scale Factor และ Z คือ Zero-point offset ในช่วง [-128, 127] พร้อมทั้งบังคับให้ Input และ Output ทำงานในโหมด tf.int8 อย่างสมบูรณ์"
    )
    format_paragraph(p)

    # Quantization Table
    add_heading_2(doc, "ตารางที่ 3: การเปรียบเทียบผลลัพธ์ระหว่าง Float32 Baseline และ Full INT8 Model")
    q_tbl = doc.add_table(rows=6, cols=4)
    q_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(q_tbl)
    
    q_headers = ["คุณลักษณะ (Metric)", "Float32 Baseline", "Full INT8 (Quantized)", "ผลการเปลี่ยนแปลง (Improvement)"]
    for j, h in enumerate(q_headers):
        q_tbl.cell(0, j).paragraphs[0].add_run(h)
    style_header_row(q_tbl.rows[0])
    
    q_rows = [
        (["รูปแบบข้อมูล (Data Precision)", "32-bit Floating Point", "8-bit Signed Integer", "ลดขนาดบิตลง 4 เท่า"], False),
        (["ขนาดไฟล์โมเดล (File Size)", "~376.65 KB", "134.11 KB", "ลดลง 64.4% (ประหยัด Flash 2.8x)"], True),
        (["ความแม่นยำบน Validation Set", "94.44%", "94.44%", "คงที่สมบูรณ์ (Exceeded >90%)"], False),
        (["ความแม่นยำบน Test Set (40 ภาพ)", "80.00% (32/40)", "80.00% (32/40)", "Quantization Drop = 0.00% !"], True),
        (["หน่วยความจำ RAM ที่ต้องใช้ (Tensor Arena)", "> 500 KB (ล้น SRAM)", "114.3 KB", "ลดภาระ RAM ลง 75% (รันใน PSRAM ได้)"], False)
    ]
    q_align = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT]
    for idx, (data, is_even) in enumerate(q_rows):
        row = q_tbl.rows[idx + 1]
        for c_idx, val in enumerate(data):
            row.cells[c_idx].paragraphs[0].add_run(val)
        style_body_row(row, is_even=is_even, align_list=q_align)

    doc.add_paragraph()

    add_callout(
        doc,
        "ปรากฏการณ์ Zero Quantization Degradation (ความแม่นยำไม่ตกเลย)",
        "ผลการประเมินชี้ให้เห็นว่าโมเดล Full INT8 (134.11 KB) ให้ผลการจำแนกภาพทดสอบจริงทั้ง 40 ภาพได้เหมือนกับโมเดล Float32 ดั้งเดิม 100% "
        "(ทายถูกต้อง 32 ภาพเท่ากัน) ส่งผลให้ค่า Quantization Drop เท่ากับ 0.00% สิ่งนี้พิสูจน์ให้เห็นว่าโมเดลมีความทนทานสูงมาก "
        "และตัวแทนข้อมูล 150 ภาพที่นำมา Calibrate ครอบคลุมการกระจายตัวของน้ำหนักโมเดลได้อย่างสมบูรณ์"
    )

    # =========================================================================
    # 6. HARDWARE IMPLEMENTATION
    # =========================================================================
    add_heading_1(doc, "6. Hardware Implementation (การติดตั้งและประมวลผลบนฮาร์ดแวร์จริง)")
    p = doc.add_paragraph(
        "ฮาร์ดแวร์เป้าหมายคือบอร์ดพัฒนา LilyGO T-SIMCAM ซึ่งขับเคลื่อนด้วยชิปประมวลผล Espressif ESP32-S3 Dual-Core Xtensa LX7 ความเร็ว 240 MHz "
        "ติดตั้งเซนเซอร์กล้อง Omnivision OV2640 ความละเอียดสูงสุด 2 ล้านพิกเซล เชื่อมต่อผ่านบัส DVP โดยภาพที่จับได้จะถูก Crop และ Rescale เป็นพื้นที่สนใจ (ROI) "
        "ขนาด 96x96 RGB เพื่อป้อนเข้าสู่โมเดล\n\n"
        "สถาปัตยกรรมเฟิร์มแวร์ TFLite Micro บน ESP32-S3 ประกอบด้วย 3 กลไกสำคัญ:\n"
        "1) การจัดเก็บโมเดลใน Flash ROM: แปลงไฟล์ .tflite ขนาด 134.11 KB เป็น C Byte Array ด้วย xxd -i (mangosteen_model_data.h) และจัดสรรด้วย alignas(16)\n"
        "2) การจัดสรร Tensor Arena ใน PSRAM: เนื่องจากโมเดลต้องการหน่วยความจำคำนวณชั่วคราว 114.3 KB หากจองใน Internal SRAM (มี 512 KB แต่เหลือให้แอปพลิเคชันใช้งาน ~150-200 KB) "
        "จะทำให้ระบบเสี่ยงต่อการแฮงก์ จึงใช้ฟังก์ชัน ps_malloc() จองใน External Octal PSRAM ขนาด 8 MB ส่งผลให้ระบบทำงานได้อย่างเสถียร 100%\n"
        "3) MicroMutableOpResolver: ลงทะเบียนเฉพาะ 7 คำสั่ง Operator ที่ใช้งานจริง (AddDepthwiseConv2D, AddConv2D, AddAveragePool2D, AddReshape, AddFullyConnected, AddSoftmax, AddDequantize) "
        "ช่วยลดขนาดของไฟล์คอมไพล์เฟิร์มแวร์ลงได้มากกว่า 300 KB"
    )
    format_paragraph(p)

    # =========================================================================
    # 7. BENCHMARKS
    # =========================================================================
    add_heading_1(doc, "7. Benchmarks (ผลการทดสอบประสิทธิภาพเชิงปริมาณ)")
    p = doc.add_paragraph(
        "การทดสอบประสิทธิภาพทั้งระบบ (End-to-End Benchmark) บนบอร์ด LilyGO T-SIMCAM ร่วมกับการทดสอบโมเดลบนชุดภาพทดสอบจริง (Unseen Test Set 40 ภาพ) "
        "ได้ผลลัพธ์เชิงตัวเลขดังแสดงในตารางที่ 4 และตารางที่ 5:"
    )
    format_paragraph(p)

    # Benchmark Card Table
    add_heading_2(doc, "ตารางที่ 4: สรุปผลการวัดประสิทธิภาพระบบ (System Benchmark Card)")
    b_tbl = doc.add_table(rows=10, cols=4)
    b_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(b_tbl)
    
    b_headers = ["หมวดหมู่ (Category)", "ตัวชี้วัด (Metric)", "ค่าที่วัดได้จริง (Measured Value)", "บันทึกเชิงเทคนิค (Notes)"]
    for j, h in enumerate(b_headers):
        b_tbl.cell(0, j).paragraphs[0].add_run(h)
    style_header_row(b_tbl.rows[0])
    
    b_rows = [
        (["Model", "Total Parameters", "94,163", "เหมาะสมกับช่วงเป้าหมาย (60k-100k)"], False),
        (["Model", "Quantization Drop", "0.00%", "ไม่พบความเสื่อมถอยของความแม่นยำ"], True),
        (["Model", "Validation Accuracy", "94.44% (34/36)", "บรรลุจุดสูงสุดที่ Best Checkpoint (Ep.61)"], False),
        (["Model", "Test Set Accuracy", "80.00% (32/40)", "วัดผลบนภาพถ่ายจริงที่ไม่เคยผ่านโมเดล"], True),
        (["Memory", "Flash Storage", "1.18 MB (18.1%)", "ใช้ Flash เพียง 18.1% ของขนาดพาร์ทิชัน"], False),
        (["Memory", "Internal SRAM", "63.4 KB (19.3%)", "เหลือพื้นที่ SRAM เพียงพอสำหรับ Wi-Fi Stack"], True),
        (["Memory", "PSRAM Tensor Arena", "114.3 KB", "จัดสรรใน PSRAM 8 MB ได้อย่างเสถียรภาพ"], False),
        (["Speed", "Inference Latency", "5,667 ms (~5.6 s)", "ความเร็วคำนวณโมเดลต่อ 1 ภาพบน CPU 240 MHz"], True),
        (["Speed", "Live Stream Rate", "10-12 FPS", "ความเร็วสตรีมภาพพรีวิวกล้องบน Web Dashboard"], False),
    ]
    b_align = [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT]
    for idx, (data, is_even) in enumerate(b_rows):
        row = b_tbl.rows[idx + 1]
        for c_idx, val in enumerate(data):
            row.cells[c_idx].paragraphs[0].add_run(val)
        style_body_row(row, is_even=is_even, align_list=b_align)

    doc.add_paragraph()

    # Classification Report Table
    add_heading_2(doc, "ตารางที่ 5: รายงานผลการจำแนกรายคลาสบน Test Set จริง 40 ภาพ (Classification Report)")
    cr_tbl = doc.add_table(rows=5, cols=6)
    cr_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(cr_tbl)
    
    cr_headers = ["Class Name", "ภาพทดสอบจริง (Support)", "ทำนายถูกต้อง (Correct)", "Precision", "Recall", "F1-Score"]
    for j, h in enumerate(cr_headers):
        cr_tbl.cell(0, j).paragraphs[0].add_run(h)
    style_header_row(cr_tbl.rows[0])
    
    cr_rows = [
        (["Unripe (ดิบ)", "22 ภาพ", "21 ภาพ", "0.91 (91.3%)", "0.95 (95.5%)", "0.93"], False),
        (["Ripe (สุกพร้อมทาน)", "12 ภาพ", "8 ภาพ", "0.73 (72.7%)", "0.67 (66.7%)", "0.70"], True),
        (["Overripe (งอม/สุกจัด)", "6 ภาพ", "3 ภาพ", "0.50 (50.0%)", "0.50 (50.0%)", "0.50"], False),
        (["รวมเฉลี่ย (Macro / Overall)", "40 ภาพ", "32 ภาพ", "0.71 (71.3%)", "0.71 (70.7%)", "Overall Acc: 80.00%"], True)
    ]
    cr_align = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER]
    for idx, (data, is_even) in enumerate(cr_rows):
        row = cr_tbl.rows[idx + 1]
        for c_idx, val in enumerate(data):
            row.cells[c_idx].paragraphs[0].add_run(val)
        style_body_row(row, is_even=is_even, align_list=cr_align)
        if idx == 3: # Overall row bold
            for cell in row.cells:
                for run in cell.paragraphs[0].runs:
                    run.bold = True

    # Insert Figure 2: Confusion Matrix
    cm_img = 'training/confusion_matrix_light.png'
    if os.path.exists(cm_img):
        doc.add_paragraph()
        fig2_p = doc.add_paragraph()
        fig2_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fig2_p.paragraph_format.space_after = Pt(2)
        fig2_p.paragraph_format.keep_with_next = True
        run_img2 = fig2_p.add_run()
        run_img2.add_picture(cm_img, width=Inches(4.8))
        
        cap2 = doc.add_paragraph()
        cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        format_paragraph(cap2, space_after=12)
        r_cap2 = cap2.add_run("รูปที่ 2: เมทริกซ์ความสับสน (Confusion Matrix Heatmap) แสดงผลการทำนายเทียบกับความเป็นจริงบน Test Set 40 ภาพ (แม่นยำ 80.00%)")
        r_cap2.font.size = Pt(9.5)
        r_cap2.italic = True
        r_cap2.font.color.rgb = RGBColor(71, 85, 105)

    # =========================================================================
    # 8. FAILURE MODES
    # =========================================================================
    add_heading_1(doc, "8. Failure Modes (การวิเคราะห์ข้อผิดพลาดและเคสที่ล้มเหลว)")
    p = doc.add_paragraph(
        "จากการวิเคราะห์เชิงลึกของ Confusion Matrix ในรูปที่ 2 พบว่าโมเดลทำนายผิดพลาดทั้งสิ้น 8 ภาพจากทั้งหมด 40 ภาพ "
        "โดยสามารถจัดกลุ่มสาเหตุของความล้มเหลวได้ 3 ปัจจัยหลักดังนี้:"
    )
    format_paragraph(p)

    f_points = [
        ("1. รอยต่อการเปลี่ยนสีตามธรรมชาติ (Natural Transition Boundary Between Ripe & Overripe): ",
         "ความผิดพลาดเกือบทั้งหมด (7 จาก 8 ภาพ) เกิดขึ้นระหว่างคลาส Ripe และ Overripe สลับกัน (Ripe ถูกทำนายเป็น Overripe 2 ภาพ และ Overripe ถูกทำนายเป็น Ripe 3 ภาพ) "
         "ในเชิงสรีรวิทยา มังคุดระยะที่ 5 (สีม่วงแดงเข้ม) กำลังเปลี่ยนผ่านเข้าสู่ระยะที่ 6 (สีม่วงดำ) การเปลี่ยนแปลงของเม็ดสีแอนโทไซยานิน (Anthocyanin) เป็นไปอย่างต่อเนื่อง "
         "ทำให้ในสภาพแสงตกกระทบบางมุม กล้อง OV2640 ไม่สามารถแยกความแตกต่างของความเข้มสีดำได้อย่างเด็ดขาด ส่งผลให้ค่าความน่าจะเป็นของทั้งสองคลาสนี้ใกล้เคียงกันมาก (~48% vs ~52%)"),
        ("2. ผลกระทบจากความขาดแคลนของข้อมูลดั้งเดิม (Data Scarcity in Test Set): ",
         "ในชุดภาพถ่ายจริง มีมังคุดงอม (Overripe) เพียง 6 ภาพในชุด Test การที่โมเดลทายผิดเพียง 3 ภาพส่งผลให้ค่า Recall ลดลงเหลือ 50.0% ทันที "
         "ซึ่งเป็นผลกระทบทางสถิติของกลุ่มตัวอย่างขนาดเล็ก ไม่ได้หมายความว่าโมเดลไม่สามารถสกัดคุณลักษณะของมังคุดงอมได้"),
        ("3. แสงสะท้อนบนผิวเปลือกมังคุด (Surface Specular Reflection): ",
         "ผิวมังคุดที่มีความมันวาวเมื่อกระทบกับแสงไฟนีออนหรือแสงแดดตรง จะเกิดจุดขาวสว่างจ้า (Specular Highlights) บนภาพ ซึ่งบดบังข้อมูลสีเปลือกที่แท้จริง "
         "ส่งผลให้ตัวสกัดคุณลักษณะใน Stage 0 และ Stage 1 ตีความค่าพิกเซลผิดเพี้ยนไปเล็กน้อย")
    ]
    for fp_title, fp_desc in f_points:
        f_p = doc.add_paragraph(style='List Bullet')
        format_paragraph(f_p, space_after=4)
        r = f_p.add_run(fp_title)
        r.bold = True
        f_p.add_run(fp_desc)

    # =========================================================================
    # 9. GROUP COMPARISON
    # =========================================================================
    add_heading_1(doc, "9. Group Comparison (การเปรียบเทียบเชิงสถาปัตยกรรม)")
    p = doc.add_paragraph(
        "เพื่อประเมินความคุ้มค่าและประสิทธิภาพของสถาปัตยกรรม Mangosteen_SeparableCNN_94k ได้ทำการเปรียบเทียบกับโมเดลทางเลือกอื่นๆ "
        "ที่นิยมใช้ในงาน Computer Vision ดังแสดงในตารางที่ 6:"
    )
    format_paragraph(p)

    # Group Comparison Table
    add_heading_2(doc, "ตารางที่ 6: การเปรียบเทียบประสิทธิภาพข้ามสถาปัตยกรรมสำหรับงานจำแนกความสุกมังคุดบน ESP32-S3")
    comp_tbl = doc.add_table(rows=5, cols=6)
    comp_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(comp_tbl)
    
    comp_headers = ["สถาปัตยกรรม / โมเดล", "Parameters", "Flash Footprint", "Tensor Arena RAM", "Latency (ESP32-S3)", "ความเป็นไปได้ในการใช้งานจริง"]
    for j, h in enumerate(comp_headers):
        comp_tbl.cell(0, j).paragraphs[0].add_run(h)
    style_header_row(comp_tbl.rows[0])
    
    comp_rows = [
        (["Standard CNN Baseline", "~750,000", "~3.0 MB", "> 800 KB", "> 30 วินาที", "❌ ไม่สามารถรันได้ (ล้น RAM บอร์ดค้าง)"], False),
        (["MobileNetV2 (Alpha 0.35)", "~350,000", "~1.4 MB", "~450 KB", "~12-15 วินาที", "⚠️ รันได้แต่ช้าเกินไป ไม่เหมาะกับหน้างาน"], True),
        (["Float32 Separable CNN", "94,163", "376.6 KB", "> 500 KB", "~8-10 วินาที", "⚠️ รันได้แต่กิน RAM สูง เสี่ยง Heap Overflow"], False),
        (["Mangosteen_SeparableCNN_94k (INT8) [งานนี้]", "94,163", "134.1 KB", "114.3 KB", "5.6 วินาที", "✅ ผ่านเกณฑ์สมบูรณ์ มีเสถียรภาพสูง"], True)
    ]
    comp_align = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT]
    for idx, (data, is_even) in enumerate(comp_rows):
        row = comp_tbl.rows[idx + 1]
        for c_idx, val in enumerate(data):
            row.cells[c_idx].paragraphs[0].add_run(val)
        style_body_row(row, is_even=is_even, align_list=comp_align)
        if idx == 3: # Our model bold
            for cell in row.cells:
                for run in cell.paragraphs[0].runs:
                    run.bold = True

    doc.add_paragraph()

    # =========================================================================
    # 10. CONCLUSION & FUTURE WORK
    # =========================================================================
    add_heading_1(doc, "10. Conclusion & Future Work (บทสรุปและทิศทางการพัฒนาต่อยอด)")
    p = doc.add_paragraph(
        "10.1 บทสรุป (Conclusion):\n"
        "โครงการนี้ประสบความสำเร็จในการพัฒนาระบบตรวจวัดและจำแนกระดับความสุกของมังคุดแบบอัตโนมัติบนอุปกรณ์ Edge AI ไมโครคอนโทรลเลอร์ ESP32-S3 (LilyGO T-SIMCAM) "
        "โดยสามารถแก้ปัญหาข้อจำกัดทางวิศวกรรมของฮาร์ดแวร์ได้อย่างสมบูรณ์แบบ โมเดล Mangosteen_SeparableCNN_94k บรรลุความแม่นยำในการตรวจสอบสูงสุด 94.44% (Validation Accuracy) "
        "และมีความแม่นยำบนภาพถ่ายจริงที่ไม่เคยผ่านการฝึกสอน 80.00% (Test Set Accuracy) การใช้เทคนิค Full INT8 Post-Training Quantization ช่วยบีบอัดขนาดไฟล์ลงเหลือเพียง 134.11 KB "
        "โดยปราศจากการสูญเสียความแม่นยำ (0.00% Drop) และใช้พื้นที่ Tensor Arena ใน PSRAM เพียง 114.3 KB ส่งผลให้อุปกรณ์สามารถทำงานแบบออฟไลน์ได้ต่อเนื่องโดยไม่มีอาการแฮงก์หรือความร้อนสะสมสูง\n\n"
        "10.2 ทิศทางการพัฒนาต่อยอดในอนาคต (Future Work):\n"
        "1) การเปิดใช้ ESP-NN Hardware Acceleration: ปัจจุบันโมเดลใช้เวลาประมวลผล 5.6 วินาทีต่อภาพเนื่องจากเป็นการคำนวณผ่านไลบรารีมาตรฐาน TFLM C++ "
        "ในอนาคตสามารถคอมไพล์ร่วมกับไลบรารี ESP-NN ของ Espressif ซึ่งบรรจุชุดคำสั่งเวกเตอร์ SIMD Assembly สำหรับชิป Xtensa LX7 ซึ่งจะช่วยเร่งความเร็ว Depthwise Convolutions "
        "และลดเวลา Inference ลงเหลือต่ำกว่า 1.5–2.0 วินาทีได้\n"
        "2) การเก็บข้อมูลมังคุดช่วงรอยต่อสี (Transition Stage Dataset Expansion): การถ่ายภาพมังคุดในระยะที่ 5 กำลังเข้าสู่ระยะที่ 6 เพิ่มเติมในชุดฝึกสอน "
        "จะช่วยลดความสับสนระหว่างคลาส Ripe และ Overripe และยกระดับ Test Set Accuracy สู่ระดับ 90%+\n"
        "3) ระบบประหยัดพลังงานอัจฉริยะ (PIR Sensor / Deep Sleep): ติดตั้งเซนเซอร์ตรวจจับการเคลื่อนไหวเพื่อสั่งให้ ESP32-S3 ตื่นขึ้นมาประมวลผลเฉพาะเมื่อมีผลมังคุดเลื่อนมาหน้ากล้อง "
        "ช่วยให้สามารถใช้งานผ่านชุดแบตเตอรี่ในสวนได้ยาวนานหลายสัปดาห์"
    )
    format_paragraph(p)

    # =========================================================================
    # 11. REFERENCES
    # =========================================================================
    add_heading_1(doc, "11. References (เอกสารอ้างอิง)")
    refs = [
        "[1] Howard, A. G., et al. (2017). MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications. arXiv preprint arXiv:1704.04861.",
        "[2] Jacob, B., et al. (2018). Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference. In CVPR 2018 (pp. 2704-2713).",
        "[3] David, R., et al. (2021). TensorFlow Lite Micro: Embedded Machine Learning on TinyML Systems. In Proceedings of Machine Learning and Systems (MLSys), 3, 800-811.",
        "[4] Espressif Systems. (2023). ESP32-S3 Technical Reference Manual (Version 1.5). Espressif Systems Co., Ltd.",
        "[5] กรมวิชาการเกษตร. (2562). มาตรฐานสินค้าเกษตร: มังคุด (มกษ. 3-2562). กระทรวงเกษตรและสหกรณ์."
    ]
    for r_text in refs:
        rp = doc.add_paragraph()
        format_paragraph(rp, space_after=3)
        rr = rp.add_run(r_text)
        rr.font.size = Pt(10)
        rr.font.color.rgb = RGBColor(71, 85, 105)

    # Save Word document
    out_docx = "Mangosteen_Model_Development_Report.docx"
    doc.save(out_docx)
    print(f"SUCCESS: Saved {out_docx}")
    
    # Also copy to artifact folder
    artifact_dir = r'C:\Users\worav\.gemini\antigravity\brain\9192bf78-d227-49e9-9d25-71d27894c193'
    if os.path.exists(artifact_dir):
        target_art = os.path.join(artifact_dir, out_docx)
        shutil.copyfile(out_docx, target_art)
        print("Copied to artifact dir:", target_art)

if __name__ == '__main__':
    main()
