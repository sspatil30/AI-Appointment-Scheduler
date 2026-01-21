# AI-Powered Appointment Scheduler Assistant

A backend service that parses natural language or document-based appointment requests and converts them into structured scheduling data. The system handles both typed text and noisy image inputs (e.g., scanned notes, emails).

## Features

1. **OCR/Text Extraction**: Handles typed requests or photos of notes/emails
2. **Entity Extraction**: Extracts date/time phrases and department from text
3. **Normalization**: Maps phrases to ISO date/time in Asia/Kolkata timezone
4. **Guardrails**: Detects ambiguous inputs and requests clarification
5. **Simple UI**: Web interface for testing the appointment scheduler

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR (required for image processing):
   - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://127.0.0.1:5001
```

## API Endpoints

### 1. OCR/Text Extraction
**POST** `/api/ocr`
- **Body (JSON)**: `{"text": "Book dentist next Friday at 3pm"}`
- **Body (Form-Data)**: `image: <file>`
- **Response**: 
```json
{
  "raw_text": "Book dentist next Friday at 3pm",
  "confidence": 0.90
}
```

### 2. Entity Extraction
**POST** `/api/entities`
- **Body**: `{"text": "Book dentist next Friday at 3pm"}`
- **Response**:
```json
{
  "entities": {
    "date_phrase": "next Friday",
    "time_phrase": "3pm",
    "department": "dentist"
  },
  "entities_confidence": 0.85
}
```

### 3. Normalization
**POST** `/api/normalize`
- **Body**: `{"entities": {"date_phrase": "next Friday", "time_phrase": "3pm"}}`
- **Response**:
```json
{
  "normalized": {
    "date": "2025-09-26",
    "time": "15:00",
    "tz": "Asia/Kolkata"
  },
  "normalization_confidence": 0.90
}
```

### 4. Complete Appointment Processing
**POST** `/api/appointment`
- **Body (JSON)**: `{"text": "Book dentist next Friday at 3pm"}`
- **Body (Form-Data)**: `image: <file>`
- **Response**:
```json
{
  "appointment": {
    "department": "Dentistry",
    "date": "2025-09-26",
    "time": "15:00",
    "tz": "Asia/Kolkata"
  },
  "status": "ok"
}
```

**Guardrail Response** (if ambiguous):
```json
{
  "status": "needs_clarification",
  "message": "Ambiguous date/time or department"
}
```

## Example Inputs

- Text: "Book dentist next Friday at 3pm"
- Text: "Schedule appointment with doctor tomorrow at 10am"
- Text: "Need to see cardiologist on Monday @ 2:30pm"
- Image: Scanned note or email with appointment request

## Supported Departments

- Dentistry
- General Medicine
- Cardiology
- Orthopedics
- Dermatology
- Ophthalmology
- Neurology
- Psychiatry

## Timezone

All dates and times are normalized to **Asia/Kolkata** timezone.

## Project Structure

```
Appointment/
├── app.py              # Flask backend API
├── requirements.txt    # Python dependencies
├── static/
│   └── index.html     # Web UI
└── README.md          # This file
```

## Troubleshooting

### Port Already in Use
If you get a "socket access forbidden" error, the port might be in use. The app is configured to use port 5001. You can change it in `app.py` if needed.

### Tesseract OCR Not Found
If image processing fails, make sure Tesseract OCR is installed and added to your system PATH.
