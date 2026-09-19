# -*- coding: utf-8 -*-
import os
import base64
import subprocess
import shutil

def main():
    print("Reading images and HTML template...")
    curves_path = 'training/training_vs_validation_curves_light.png'
    cm_path = 'training/confusion_matrix_light.png'
    html_file = 'Mangosteen_Model_Development_Report.html'
    pdf_file = 'Mangosteen_Model_Development_Report.pdf'

    with open(curves_path, 'rb') as f:
        curves_b64 = base64.b64encode(f.read()).decode('utf-8')

    with open(cm_path, 'rb') as f:
        cm_b64 = base64.b64encode(f.read()).decode('utf-8')

    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    html_content = html_content.replace('__CURVES_B64__', f'data:image/png;base64,{curves_b64}')
    html_content = html_content.replace('__CM_B64__', f'data:image/png;base64,{cm_b64}')

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Injected base64 images into {html_file}. Size: {len(html_content)} bytes")

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

    print("Running Edge headless print-to-pdf...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("Edge return code:", res.returncode)

    if os.path.exists(pdf_file):
        size_kb = os.path.getsize(pdf_file) / 1024
        print(f"SUCCESS: Generated PDF at {pdf_file} ({size_kb:.2f} KB)")
        
        artifact_dir = r'C:\Users\worav\.gemini\antigravity\brain\9192bf78-d227-49e9-9d25-71d27894c193'
        if os.path.exists(artifact_dir):
            target_art = os.path.join(artifact_dir, 'Mangosteen_Model_Development_Report.pdf')
            shutil.copyfile(pdf_file, target_art)
            print("Copied PDF to artifact directory:", target_art)
    else:
        print("ERROR: PDF was not generated.")
        print("Stdout:", res.stdout)
        print("Stderr:", res.stderr)

if __name__ == '__main__':
    main()
