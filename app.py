from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image
import io
import re
from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import pytz
import json
import os
import platform

app = Flask(__name__)
CORS(app)

# Try to set Tesseract path for Windows
if platform.system() == 'Windows':
    # Common Tesseract installation paths on Windows
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

# Timezone for normalization
TZ = pytz.timezone('Asia/Kolkata')

# Department mapping
DEPARTMENT_MAP = {
    'dentist': 'Dentistry',
    'dental': 'Dentistry',
    'doctor': 'General Medicine',
    'physician': 'General Medicine',
    'cardiology': 'Cardiology',
    'cardiac': 'Cardiology',
    'orthopedic': 'Orthopedics',
    'ortho': 'Orthopedics',
    'dermatology': 'Dermatology',
    'dermatologist': 'Dermatology',
    'ophthalmology': 'Ophthalmology',
    'eye': 'Ophthalmology',
    'neurology': 'Neurology',
    'psychiatry': 'Psychiatry',
    'psychologist': 'Psychiatry',
}

def extract_text_from_image(image_file):
    """Step 1: OCR/Text Extraction from image"""
    try:
        # Reset file pointer in case it was already read
        image_file.seek(0)
        image = Image.open(io.BytesIO(image_file.read()))
        
        # Try to get Tesseract path (Windows common locations)
        try:
            text = pytesseract.image_to_string(image)
        except Exception as tesseract_error:
            # Check if Tesseract is installed
            error_msg = str(tesseract_error)
            if 'tesseract' in error_msg.lower() or 'not found' in error_msg.lower():
                raise Exception(f"Tesseract OCR not found. Please install Tesseract OCR. Error: {error_msg}")
            else:
                raise tesseract_error
        
        confidence = 0.90  # Simplified confidence score
        extracted_text = text.strip()
        
        if not extracted_text:
            return None, 0.0, "No text could be extracted from the image. The image might be too blurry or contain no readable text."
        
        return extracted_text, confidence, None
    except Exception as e:
        error_message = str(e)
        return None, 0.0, error_message

def extract_entities(text):
    """Step 2: Entity Extraction - Extract date/time phrase and department"""
    text_lower = text.lower()
    
    # Extract department
    department = None
    department_phrase = None
    for key, value in DEPARTMENT_MAP.items():
        if key in text_lower:
            department = value
            department_phrase = key
            break
    
    # Extract time phrases (patterns like "3pm", "3 pm", "15:00", "at 3pm", "@ 3pm")
    time_patterns = [
        r'@?\s*(\d{1,2}\s*(?:am|pm|AM|PM))',
        r'@?\s*(\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)?)',
        r'at\s+(\d{1,2}\s*(?:am|pm|AM|PM))',
        r'at\s+(\d{1,2}:\d{2})',
    ]
    
    time_phrase = None
    for pattern in time_patterns:
        match = re.search(pattern, text_lower)
        if match:
            time_phrase = match.group(1).strip()
            break
    
    # Extract date phrases (patterns like "next Friday", "tomorrow", "next week", etc.)
    date_patterns = [
        r'(next\s+\w+)',
        r'(tomorrow)',
        r'(today)',
        r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*)',
    ]
    
    date_phrase = None
    for pattern in date_patterns:
        match = re.search(pattern, text_lower)
        if match:
            date_phrase = match.group(1).strip()
            break
    
    entities = {
        "date_phrase": date_phrase,
        "time_phrase": time_phrase,
        "department": department_phrase
    }
    
    # Calculate confidence based on what we found
    found_count = sum(1 for v in entities.values() if v is not None)
    confidence = 0.85 if found_count >= 2 else 0.60
    
    return entities, confidence

def normalize_datetime(date_phrase, time_phrase):
    """Step 3: Normalization - Map phrases to ISO date/time in Asia/Kolkata"""
    now = datetime.now(TZ)
    
    # Parse date phrase
    target_date = None
    
    if date_phrase:
        date_lower = date_phrase.lower()
        
        # Handle "next [day]" pattern
        if date_lower.startswith('next '):
            day_name = date_lower.replace('next ', '').strip()
            days_map = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                'friday': 4, 'saturday': 5, 'sunday': 6
            }
            if day_name in days_map:
                target_day = days_map[day_name]
                current_day = now.weekday()
                days_ahead = target_day - current_day
                if days_ahead <= 0:
                    days_ahead += 7
                target_date = now + timedelta(days=days_ahead)
        
        # Handle "tomorrow"
        elif date_lower == 'tomorrow':
            target_date = now + timedelta(days=1)
        
        # Handle "today"
        elif date_lower == 'today':
            target_date = now
        
        # Handle day names without "next"
        elif date_lower in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            days_map = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                'friday': 4, 'saturday': 5, 'sunday': 6
            }
            target_day = days_map[date_lower]
            current_day = now.weekday()
            days_ahead = target_day - current_day
            if days_ahead <= 0:
                days_ahead += 7
            target_date = now + timedelta(days=days_ahead)
        
        # Try dateutil parser for other formats
        else:
            try:
                parsed = parser.parse(date_phrase, default=now)
                if parsed.tzinfo is None:
                    parsed = TZ.localize(parsed)
                target_date = parsed
            except:
                pass
    
    # Default to next week if no date found
    if target_date is None:
        target_date = now + timedelta(days=7)
    
    # Parse time phrase
    target_time = None
    
    if time_phrase:
        time_lower = time_phrase.lower().strip()
        
        # Handle "3pm", "3 pm" format
        if 'am' in time_lower or 'pm' in time_lower:
            time_str = re.sub(r'[^\d:apm\s]', '', time_lower)
            try:
                if ':' in time_str:
                    time_part = time_str.split()[0]
                    am_pm = time_str.split()[1] if len(time_str.split()) > 1 else ''
                else:
                    time_part = re.sub(r'[^\d]', '', time_str)
                    am_pm = 'pm' if 'pm' in time_lower else 'am'
                
                hour = int(time_part.split(':')[0]) if ':' in time_part else int(time_part)
                minute = int(time_part.split(':')[1]) if ':' in time_part else 0
                
                if am_pm == 'pm' and hour != 12:
                    hour += 12
                elif am_pm == 'am' and hour == 12:
                    hour = 0
                
                target_time = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            except:
                pass
        
        # Handle "15:00" format
        elif ':' in time_lower:
            try:
                hour, minute = map(int, time_lower.split(':'))
                target_time = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            except:
                pass
    
    # Default to 9 AM if no time found
    if target_time is None:
        target_time = target_date.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Ensure timezone awareness
    if target_time.tzinfo is None:
        target_time = TZ.localize(target_time)
    
    normalized = {
        "date": target_time.strftime("%Y-%m-%d"),
        "time": target_time.strftime("%H:%M"),
        "tz": "Asia/Kolkata"
    }
    
    confidence = 0.90 if date_phrase and time_phrase else 0.70
    
    return normalized, confidence

def check_guardrails(entities, normalized):
    """Check for ambiguous inputs"""
    if not entities.get('department'):
        return {"status": "needs_clarification", "message": "Ambiguous department"}
    
    if not entities.get('date_phrase'):
        return {"status": "needs_clarification", "message": "Ambiguous date/time"}
    
    if not entities.get('time_phrase'):
        return {"status": "needs_clarification", "message": "Ambiguous time"}
    
    return None

@app.route('/api/ocr', methods=['POST'])
def ocr_endpoint():
    """Step 1: OCR/Text Extraction endpoint"""
    if 'text' in request.json:
        text = request.json['text']
        return jsonify({
            "raw_text": text,
            "confidence": 0.90
        })
    
    if 'image' in request.files:
        image_file = request.files['image']
        text, confidence, error_msg = extract_text_from_image(image_file)
        if text is None:
            error = error_msg if error_msg else "Failed to extract text from image"
            return jsonify({"error": error}), 400
        return jsonify({
            "raw_text": text,
            "confidence": confidence
        })
    
    return jsonify({"error": "No text or image provided"}), 400

@app.route('/api/entities', methods=['POST'])
def entities_endpoint():
    """Step 2: Entity Extraction endpoint"""
    if 'text' not in request.json:
        return jsonify({"error": "No text provided"}), 400
    
    text = request.json['text']
    entities, confidence = extract_entities(text)
    
    return jsonify({
        "entities": entities,
        "entities_confidence": confidence
    })

@app.route('/api/normalize', methods=['POST'])
def normalize_endpoint():
    """Step 3: Normalization endpoint"""
    if 'entities' not in request.json:
        return jsonify({"error": "No entities provided"}), 400
    
    entities = request.json['entities']
    normalized, confidence = normalize_datetime(
        entities.get('date_phrase'),
        entities.get('time_phrase')
    )
    
    return jsonify({
        "normalized": normalized,
        "normalization_confidence": confidence
    })

@app.route('/api/appointment', methods=['POST'])
def appointment_endpoint():
    """Step 4: Complete appointment processing pipeline"""
    # Get input
    text = None
    
    # Check if request has JSON content
    if request.is_json and request.json:
        if 'text' in request.json:
            text = request.json['text']
    
    # Check for image upload
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file.filename:
            text, _, error_msg = extract_text_from_image(image_file)
            if text is None:
                error = error_msg if error_msg else "Failed to extract text from image"
                return jsonify({"error": error}), 400
    
    # Check for form data with text
    if not text and request.form and 'text' in request.form:
        text = request.form['text']
    
    if not text:
        return jsonify({"error": "No text or image provided"}), 400
    
    # Step 1: OCR (already done if image, or use text directly)
    raw_text = text
    ocr_confidence = 0.90
    
    # Step 2: Entity Extraction
    entities, entities_confidence = extract_entities(raw_text)
    
    # Step 3: Normalization
    normalized, norm_confidence = normalize_datetime(
        entities.get('date_phrase'),
        entities.get('time_phrase')
    )
    
    # Step 4: Guardrails
    guardrail_check = check_guardrails(entities, normalized)
    if guardrail_check:
        return jsonify(guardrail_check)
    
    # Step 5: Final Appointment
    department = DEPARTMENT_MAP.get(entities.get('department', '').lower(), 'General Medicine')
    
    appointment = {
        "department": department,
        "date": normalized["date"],
        "time": normalized["time"],
        "tz": normalized["tz"]
    }
    
    return jsonify({
        "appointment": appointment,
        "status": "ok",
        "raw_text": raw_text,
        "entities": entities,
        "normalized": normalized
    })

@app.route('/api/test-ocr', methods=['GET'])
def test_ocr():
    """Test endpoint to check if Tesseract OCR is available"""
    try:
        # Try to get Tesseract version
        version = pytesseract.get_tesseract_version()
        return jsonify({
            "status": "ok",
            "tesseract_installed": True,
            "version": str(version),
            "tesseract_cmd": pytesseract.pytesseract.tesseract_cmd if hasattr(pytesseract.pytesseract, 'tesseract_cmd') else "default"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "tesseract_installed": False,
            "error": str(e),
            "message": "Tesseract OCR is not installed or not found in PATH. Please install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki"
        }), 500

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='127.0.0.1')
