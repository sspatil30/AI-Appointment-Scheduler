# AI-Powered Appointment Scheduler Assistant

A complete backend service that parses natural language or document-based appointment requests and converts them into structured scheduling data. The system handles both typed text and noisy image inputs (e.g., scanned notes, emails) with OCR, entity extraction, normalization, and guardrails for ambiguity.

## 📋 Table of Contents

- [Problem Statement](#problem-statement)
- [Architecture](#architecture)
- [Features](#features)
- [Installation & Setup](#installation--setup)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Evaluation Criteria Coverage](#evaluation-criteria-coverage)

## 🎯 Problem Statement

Build a backend service that parses natural language or document-based appointment requests and converts them into structured scheduling data. The system should handle both typed text and noisy image inputs (e.g., scanned notes, emails). The pipeline includes:

1. **OCR/Text Extraction** - Handle typed requests or photos of notes/emails
2. **Entity Extraction** - Extract date/time phrase and department
3. **Normalization** - Map phrases to ISO date/time in Asia/Kolkata timezone
4. **Guardrails** - Detect ambiguous inputs and request clarification

## 🏗️ Architecture

```
┌─────────────────┐
│   User Input    │
│  (Text/Image)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Step 1: OCR    │
│ Text Extraction │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 2: Entity  │
│   Extraction    │
│ (Date/Time/Dept)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 3:         │
│ Normalization   │
│ (ISO Format)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 4:         │
│  Guardrails     │
│  Validation     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Final JSON      │
│   Response      │
└─────────────────┘
```

### Technology Stack

- **Backend**: Flask (Python)
- **OCR**: Tesseract OCR via pytesseract
- **Image Processing**: Pillow (PIL)
- **Date/Time Parsing**: python-dateutil, pytz
- **NLP**: Regex-based entity extraction with spaCy support
- **Frontend**: HTML/CSS/JavaScript (Simple UI for testing)

## ✨ Features

1. **Multi-Input Support**
   - Text input via JSON or form data
   - Image upload with OCR text extraction
   - Handles noisy/scanned documents

2. **Intelligent Entity Extraction**
   - Date phrases: "next Friday", "tomorrow", "Monday", etc.
   - Time phrases: "3pm", "15:00", "@ 2:30pm", etc.
   - Department mapping: "dentist" → "Dentistry", "doctor" → "General Medicine", etc.

3. **Timezone Normalization**
   - All dates/times normalized to Asia/Kolkata timezone
   - ISO 8601 format output (YYYY-MM-DD, HH:MM)

4. **Guardrails & Error Handling**
   - Detects ambiguous date/time inputs
   - Validates department presence
   - Returns clear error messages for clarification

5. **RESTful API**
   - Individual endpoints for each step
   - Combined endpoint for complete pipeline
   - CORS enabled for frontend integration

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Tesseract OCR (for image processing)
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd Appointment
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install Tesseract OCR

#### Windows (using winget):
```powershell
winget install --id UB-Mannheim.TesseractOCR --accept-package-agreements --accept-source-agreements
```

**Important**: After installation, **restart your terminal** or refresh PATH:
```powershell
# Refresh PATH in current session
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

#### Alternative: Manual Installation
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer
3. Check "Add to PATH" during installation
4. Default location: `C:\Program Files\Tesseract-OCR\`

#### macOS:
```bash
brew install tesseract
```

#### Linux:
```bash
sudo apt-get install tesseract-ocr
```

### Step 4: Verify Installation

```bash
python test_ocr.py
```

Expected output:
```
[OK] Tesseract OCR is installed
  Version: 5.4.0
[OK] Pillow (PIL) is installed
```

### Step 5: Run the Application

```bash
python app.py
```

The server will start on `http://127.0.0.1:5001`

### Step 6: Access the Web UI

Open your browser and navigate to:
```
http://127.0.0.1:5001
```

## 📚 API Documentation

### Base URL
```
http://127.0.0.1:5001
```

### Endpoints

#### 1. OCR/Text Extraction
**POST** `/api/ocr`

Extract text from input (text or image).

**Request (Text):**
```json
{
  "text": "Book dentist next Friday at 3pm"
}
```

**Request (Image):**
```
Content-Type: multipart/form-data
image: <file>
```

**Response:**
```json
{
  "raw_text": "Book dentist next Friday at 3pm",
  "confidence": 0.90
}
```

#### 2. Entity Extraction
**POST** `/api/entities`

Extract entities (date, time, department) from text.

**Request:**
```json
{
  "text": "Book dentist next Friday at 3pm"
}
```

**Response:**
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

#### 3. Normalization
**POST** `/api/normalize`

Normalize date/time phrases to ISO format.

**Request:**
```json
{
  "entities": {
    "date_phrase": "next Friday",
    "time_phrase": "3pm"
  }
}
```

**Response:**
```json
{
  "normalized": {
    "date": "2025-01-24",
    "time": "15:00",
    "tz": "Asia/Kolkata"
  },
  "normalization_confidence": 0.90
}
```

#### 4. Complete Appointment Processing
**POST** `/api/appointment`

Complete pipeline: OCR → Entity Extraction → Normalization → Guardrails → Final JSON

**Request (Text):**
```json
{
  "text": "Book dentist next Friday at 3pm"
}
```

**Request (Image):**
```
Content-Type: multipart/form-data
image: <file>
```

**Success Response:**
```json
{
  "appointment": {
    "department": "Dentistry",
    "date": "2025-01-24",
    "time": "15:00",
    "tz": "Asia/Kolkata"
  },
  "status": "ok",
  "raw_text": "Book dentist next Friday at 3pm",
  "entities": {
    "date_phrase": "next Friday",
    "time_phrase": "3pm",
    "department": "dentist"
  },
  "normalized": {
    "date": "2025-01-24",
    "time": "15:00",
    "tz": "Asia/Kolkata"
  }
}
```

**Guardrail Response (Ambiguous Input):**
```json
{
  "status": "needs_clarification",
  "message": "Ambiguous date/time or department"
}
```

**Error Response:**
```json
{
  "error": "No text or image provided"
}
```

#### 5. Test OCR Installation
**GET** `/api/test-ocr`

Check if Tesseract OCR is properly installed.

**Response:**
```json
{
  "status": "ok",
  "tesseract_installed": true,
  "version": "5.4.0",
  "tesseract_cmd": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
}
```

## 🧪 Testing

### Using cURL

#### Test 1: Text Input
```bash
curl -X POST http://127.0.0.1:5001/api/appointment \
  -H "Content-Type: application/json" \
  -d '{"text": "Book dentist next Friday at 3pm"}'
```

#### Test 2: Image Upload
```bash
curl -X POST http://127.0.0.1:5001/api/appointment \
  -F "image=@/path/to/image.png"
```

#### Test 3: Step-by-Step Pipeline
```bash
# Step 1: OCR
curl -X POST http://127.0.0.1:5001/api/ocr \
  -H "Content-Type: application/json" \
  -d '{"text": "Schedule appointment with doctor tomorrow at 10am"}'

# Step 2: Entity Extraction
curl -X POST http://127.0.0.1:5001/api/entities \
  -H "Content-Type: application/json" \
  -d '{"text": "Schedule appointment with doctor tomorrow at 10am"}'

# Step 3: Normalization
curl -X POST http://127.0.0.1:5001/api/normalize \
  -H "Content-Type: application/json" \
  -d '{"entities": {"date_phrase": "tomorrow", "time_phrase": "10am"}}'
```

### Using Postman

1. **Import Collection**: Create a new collection with the following requests:

   - **Text Appointment Request**
     - Method: POST
     - URL: `http://127.0.0.1:5001/api/appointment`
     - Headers: `Content-Type: application/json`
     - Body (raw JSON):
       ```json
       {
         "text": "Book dentist next Friday at 3pm"
       }
       ```

   - **Image Appointment Request**
     - Method: POST
     - URL: `http://127.0.0.1:5001/api/appointment`
     - Body: form-data
     - Key: `image` (type: File)
     - Value: Select an image file

   - **Test OCR**
     - Method: GET
     - URL: `http://127.0.0.1:5001/api/test-ocr`

### Example Test Cases

#### Valid Inputs:
```json
{"text": "Book dentist next Friday at 3pm"}
{"text": "Schedule appointment with doctor tomorrow at 10am"}
{"text": "Need to see cardiologist on Monday @ 2:30pm"}
{"text": "Appointment with ortho next week Tuesday at 9:00"}
```

#### Ambiguous Inputs (Should Trigger Guardrails):
```json
{"text": "Book appointment"}  // Missing date/time
{"text": "Next week"}  // Missing department and time
{"text": "3pm"}  // Missing date and department
```

### Web UI Testing

1. Navigate to `http://127.0.0.1:5001`
2. Enter text in the text area or upload an image
3. Click "Process Appointment"
4. View results for each step:
   - Raw Text
   - Extracted Entities
   - Normalized Date/Time
   - Final Appointment JSON

## 📁 Project Structure

```
Appointment/
├── app.py                 # Flask backend API (main application)
├── requirements.txt       # Python dependencies
├── test_ocr.py           # OCR installation test script
├── run.bat               # Windows startup script
├── README.md             # This file
├── .gitignore            # Git ignore rules
└── static/
    └── index.html        # Web UI for testing
```

### Key Files

- **app.py**: Main Flask application with all API endpoints and processing logic
- **static/index.html**: Simple web UI for testing the appointment scheduler
- **test_ocr.py**: Utility script to verify Tesseract OCR installation
- **requirements.txt**: All Python package dependencies

## ✅ Evaluation Criteria Coverage

### 1. Correctness of API Responses and Adherence to JSON Schemas ✅

- **All endpoints return valid JSON** with proper structure
- **Response schemas match** the problem statement requirements:
  - Step 1: `{"raw_text": "...", "confidence": 0.90}`
  - Step 2: `{"entities": {...}, "entities_confidence": 0.85}`
  - Step 3: `{"normalized": {...}, "normalization_confidence": 0.90}`
  - Step 4: `{"appointment": {...}, "status": "ok"}`
- **Error responses** follow consistent format with clear messages

### 2. Handling of Both Text and Image Inputs with OCR ✅

- **Text Input**: Direct JSON or form-data support
- **Image Input**: Multipart form-data with OCR processing
- **OCR Integration**: Tesseract OCR with automatic path detection
- **Error Handling**: Clear messages when OCR fails or Tesseract not installed
- **Fallback**: Text input works even without OCR installed

### 3. Implementation of Guardrails and Error Handling ✅

- **Guardrail Function**: `check_guardrails()` validates:
  - Department presence
  - Date phrase presence
  - Time phrase presence
- **Error Responses**: Returns `{"status": "needs_clarification", "message": "..."}` for ambiguous inputs
- **Input Validation**: Checks for empty/null inputs at each step
- **OCR Error Handling**: Handles Tesseract not found, image processing failures
- **Graceful Degradation**: Clear error messages guide users

### 4. Code Organization, Clarity, and Reusability ✅

- **Modular Functions**:
  - `extract_text_from_image()` - OCR processing
  - `extract_entities()` - Entity extraction
  - `normalize_datetime()` - Date/time normalization
  - `check_guardrails()` - Validation logic
- **Separation of Concerns**: Each endpoint handles one responsibility
- **Documentation**: Docstrings for all functions
- **Configuration**: Centralized department mapping, timezone settings
- **Reusable Components**: Functions can be used independently or in pipeline

### 5. Effective Use of AI for Chaining and Validation ✅

- **Pipeline Chaining**: `/api/appointment` chains all steps sequentially
- **Intelligent Entity Extraction**: Regex patterns + keyword matching for dates/times/departments
- **Context-Aware Normalization**: Handles relative dates ("next Friday", "tomorrow") with current date context
- **Smart Defaults**: Provides reasonable defaults when information is missing (e.g., 9 AM if no time specified)
- **Confidence Scoring**: Each step provides confidence metrics
- **Validation Logic**: Multi-level validation (syntax, semantics, completeness)

## 🔧 Configuration

### Supported Departments

The system recognizes and maps the following departments:

- `dentist`, `dental` → Dentistry
- `doctor`, `physician` → General Medicine
- `cardiology`, `cardiac` → Cardiology
- `orthopedic`, `ortho` → Orthopedics
- `dermatology`, `dermatologist` → Dermatology
- `ophthalmology`, `eye` → Ophthalmology
- `neurology` → Neurology
- `psychiatry`, `psychologist` → Psychiatry

### Timezone

All dates and times are normalized to **Asia/Kolkata** timezone as specified in the problem statement.

## 🐛 Troubleshooting

### Tesseract OCR Not Found

**Error**: `TesseractNotFoundError: tesseract is not installed`

**Solution**:
1. Verify installation: `python test_ocr.py`
2. Check PATH: `where tesseract` (Windows) or `which tesseract` (Linux/Mac)
3. Restart terminal after installation
4. Manually set path in `app.py` if needed

### Port Already in Use

**Error**: `An attempt was made to access a socket in a way forbidden`

**Solution**: Change port in `app.py`:
```python
app.run(debug=True, port=5001, host='127.0.0.1')  # Change 5001 to another port
```

### Image Upload Fails

**Error**: `Failed to extract text from image`

**Possible Causes**:
- Image is too blurry or has no text
- Unsupported image format
- Tesseract OCR not installed

**Solution**: 
- Use clear, high-contrast images
- Supported formats: PNG, JPG, JPEG, GIF, BMP
- Verify OCR installation: `GET /api/test-ocr`

## 📝 License

This project is created for educational/demonstration purposes.

## 👤 Author

Created as part of an AI-powered appointment scheduler assignment.

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify all dependencies are installed
3. Test OCR installation: `python test_ocr.py`
4. Check server logs for detailed error messages

---

**Note**: This is a development/demo version. For production use, consider:
- Using a production WSGI server (Gunicorn, uWSGI)
- Adding authentication/authorization
- Implementing rate limiting
- Adding logging and monitoring
- Using a more robust NLP library for entity extraction
- Database integration for appointment storage

