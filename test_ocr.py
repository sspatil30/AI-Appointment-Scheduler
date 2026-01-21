"""Quick test script to verify OCR setup"""
import pytesseract
from PIL import Image
import os
import platform

print("Testing OCR Setup...")
print("=" * 50)

# Try to find Tesseract in common Windows locations
if platform.system() == 'Windows':
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
    ]
    found = False
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"Found Tesseract at: {path}")
            found = True
            break
    
    if not found:
        print("Tesseract not found in common locations.")
        print("Checking system PATH...")

# Check Tesseract installation
try:
    version = pytesseract.get_tesseract_version()
    print("[OK] Tesseract OCR is installed")
    print(f"  Version: {version}")
except Exception as e:
    print("[ERROR] Tesseract OCR not found")
    print(f"  Error: {e}")
    print("\nPlease install Tesseract OCR from:")
    print("https://github.com/UB-Mannheim/tesseract/wiki")
    print("\nAfter installation, make sure to:")
    print("1. Add Tesseract to your system PATH, OR")
    print("2. Update the path in app.py")
    exit(1)

# Check Tesseract path
if hasattr(pytesseract.pytesseract, 'tesseract_cmd'):
    print(f"  Path: {pytesseract.pytesseract.tesseract_cmd}")
else:
    print("  Path: Using system PATH")

# Check if PIL/Pillow works
try:
    from PIL import Image
    print("[OK] Pillow (PIL) is installed")
except Exception as e:
    print(f"[ERROR] Pillow not found: {e}")
    exit(1)

print("\n" + "=" * 50)
print("OCR setup looks good! You can now test image uploads.")
print("=" * 50)
