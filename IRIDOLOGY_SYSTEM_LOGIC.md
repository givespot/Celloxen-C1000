# IRIDOLOGY SYSTEM - COMPLETE LOGIC DOCUMENTATION
**Date:** 17 November 2025
**Status:** PRODUCTION - OPERATIONAL

---

## 🎯 SYSTEM OVERVIEW

The Iridology Analysis System uses AI (Claude API & GPT-4 Vision) to analyze iris images and generate comprehensive wellness reports for patients. The system operates in a multi-step workflow from image upload to report generation.

---

## 📊 WORKFLOW SEQUENCE

### STEP 1: PATIENT SELECTION
**Frontend:** Iridology section in main dashboard
**User Action:** Select patient from dropdown or search
**Backend API:** `GET /api/v1/clinic/patients`
**Data Retrieved:** 
- Patient ID
- Patient name
- Patient number (CLX-ABD-XXXXX)
- Date of birth
- Medical history

---

### STEP 2: START ANALYSIS SESSION
**User Action:** Click "Start New Analysis" button
**Backend API:** `POST /api/v1/iridology/start?patient_id={id}&disclaimer_accepted=true`

**Backend Process:**
```python
1. Verify patient exists
2. Create new iridology_analyses record:
   - analysis_number: Format "IR-{CLINIC_CODE}-{YEAR}-{SEQUENCE}"
   - patient_id: Foreign key to patients table
   - clinic_id: Foreign key to clinics table
   - status: 'pending'
   - created_at: Current timestamp
3. Return analysis_id for subsequent steps
```

**Database Table:** `iridology_analyses`
```sql
CREATE TABLE iridology_analyses (
    analysis_id SERIAL PRIMARY KEY,
    analysis_number VARCHAR(50) UNIQUE,
    patient_id INTEGER REFERENCES patients(id),
    clinic_id INTEGER REFERENCES clinics(clinic_id),
    practitioner_id INTEGER REFERENCES users(user_id),
    status VARCHAR(20), -- 'pending', 'uploading', 'analyzing', 'completed'
    left_eye_image_path TEXT,
    right_eye_image_path TEXT,
    constitutional_type VARCHAR(50),
    constitutional_strength VARCHAR(20),
    combined_analysis JSONB,
    report_text TEXT,
    confidence_score DECIMAL(5,2),
    gp_referral_recommended BOOLEAN,
    gp_referral_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

**Response:**
```json
{
    "analysis_id": 123,
    "analysis_number": "IR-ABD-2025-00015",
    "status": "pending"
}
```

---

### STEP 3: UPLOAD IRIS IMAGES
**User Action:** Upload left eye image, then right eye image
**Backend API:** `POST /api/v1/iridology/{analysis_id}/upload-images`

**Request Format (multipart/form-data):**
```
left_eye_image: File (JPEG/PNG)
right_eye_image: File (JPEG/PNG)
```

**Backend Process:**
```python
1. Validate images:
   - File format: JPEG or PNG
   - File size: < 10MB
   - Image dimensions: Minimum 500x500px recommended

2. Generate unique filenames:
   - Format: "iris_{analysis_id}_left_{timestamp}.jpg"
   - Format: "iris_{analysis_id}_right_{timestamp}.jpg"

3. Save images to disk:
   - Path: /var/www/celloxen-portal/backend/iris_images/
   - Store both original and potentially resized versions

4. Convert images to base64:
   - Required for AI API calls
   - Store temporarily in memory

5. Update database:
   - left_eye_image_path: Full path to saved file
   - right_eye_image_path: Full path to saved file
   - status: 'uploading' → 'ready_for_analysis'

6. Return confirmation with preview URLs
```

**Response:**
```json
{
    "success": true,
    "left_eye_uploaded": true,
    "right_eye_uploaded": true,
    "ready_for_analysis": true
}
```

---

### STEP 4: AI ANALYSIS (MOST COMPLEX STEP)
**User Action:** Click "Analyze" button
**Backend API:** `POST /api/v1/iridology/{analysis_id}/analyse`

**Backend File:** `/var/www/celloxen-portal/backend/iridology_analyzer.py`
**AI Service:** Anthropic Claude API (claude-sonnet-4-20250514)

**Analysis Process:**

#### 4.1 INDIVIDUAL EYE ANALYSIS (Both Eyes Separately)

**For LEFT EYE:**
```python
def analyze_single_eye(image_base64, patient_info, eye_side):
    """
    Analyzes a single iris image using Claude AI
    
    Args:
        image_base64: Base64-encoded iris image
        patient_info: {name, age, gender, concerns}
        eye_side: "left" or "right"
    
    Returns:
        JSON analysis result
    """
    
    # Construct AI prompt
    prompt = f"""
    You are an expert iridology practitioner analyzing a {eye_side} iris.
    
    PATIENT: {patient_info['name']}, Age {patient_info['age']}
    
    Analyze this iris image and provide:
    
    1. CONSTITUTIONAL TYPE:
       - Lymphatic (blue iris)
       - Haematogenic (brown iris)  
       - Mixed (green/hazel iris)
    
    2. CONSTITUTIONAL STRENGTH:
       - Strong / Moderate / Weak
    
    3. IRIS CHARACTERISTICS:
       - Fiber density and pattern
       - Color variations
       - Structural integrity
    
    4. BODY SYSTEM ZONES (by clock position):
       - Digestive: 6-8 o'clock
       - Circulatory: 2-3 o'clock (left), 9-10 o'clock (right)
       - Nervous: Throughout (nerve rings)
       - Musculoskeletal: Outer periphery
       - Endocrine/Metabolic: 7 o'clock (left), 5 o'clock (right) - PANCREATIC ZONE
    
    5. SIGNIFICANT MARKINGS:
       - Lacunae (open lesions)
       - Crypts (closed lesions)
       - Nerve rings (stress indicators)
       - Pigmentation spots
       - Radii solaris
       - Scurf rim
    
    6. WELLNESS ASSESSMENT:
       Rate each body system: Excellent / Good / Fair / Needs Support
    
    CRITICAL AREAS TO CHECK:
    - PANCREATIC ZONE (diabetes risk)
    - NERVE RINGS (stress levels)
    - Any patterns requiring GP consultation
    
    Use BRITISH ENGLISH only.
    Focus on wellness patterns, NOT medical diagnosis.
    Return structured JSON.
    """
    
    # Call Claude API
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_base64
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }]
    )
    
    # Extract and parse JSON response
    analysis_json = json.loads(response.content[0].text)
    
    return analysis_json
```

**LEFT EYE Analysis Result Structure:**
```json
{
    "eye_side": "left",
    "constitutional_type": "Mixed",
    "constitutional_strength": "Moderate",
    "iris_characteristics": {
        "fiber_density": "Medium-tight weave",
        "color": "Green-hazel with brown pigmentation",
        "structural_integrity": "Good overall"
    },
    "body_systems": {
        "digestive": {
            "rating": "Fair",
            "findings": "Density variations in stomach zone",
            "recommendations": "Digestive enzyme support"
        },
        "circulatory": {
            "rating": "Good",
            "findings": "Even iris density, good circulation indicators"
        },
        "nervous": {
            "rating": "Needs Support",
            "findings": "Multiple nerve rings present - stress adaptation",
            "recommendations": "C-107 Stress therapy recommended"
        },
        "musculoskeletal": {
            "rating": "Good",
            "findings": "Strong structural integrity"
        },
        "endocrine_metabolic": {
            "rating": "Needs Support",
            "findings": "Pancreatic zone (7 o'clock) shows density changes",
            "recommendations": "C-108 Metabolic therapy + GP consultation for HbA1c test",
            "urgent": true
        }
    },
    "significant_markings": {
        "nerve_rings": {
            "count": 3,
            "prominence": "Moderate to pronounced",
            "interpretation": "Significant stress adaptation pattern"
        },
        "pancreatic_zone": {
            "location": "7 o'clock",
            "findings": "Textural variations, density changes",
            "clinical_significance": "Warrants metabolic evaluation"
        },
        "lacunae": [],
        "pigmentation": ["Brown spots at 3 o'clock position"]
    },
    "gp_referral": {
        "recommended": true,
        "reason": "Pancreatic zone patterns suggest metabolic assessment needed",
        "urgency": "Within 2-4 weeks",
        "tests_suggested": ["HbA1c", "Fasting Glucose", "Metabolic Panel"]
    }
}
```

**RIGHT EYE:** Same process, different findings

---

#### 4.2 BILATERAL SYNTHESIS (Combining Both Eyes)

**Backend Process:**
```python
def synthesize_bilateral_analysis(left_analysis, right_analysis, patient_info):
    """
    Combines left and right eye analyses into comprehensive report
    
    Returns:
        - Comprehensive wellness report (markdown text)
        - Overall constitutional assessment
        - Therapy priorities
        - Wellness recommendations
    """
    
    synthesis_prompt = f"""
    Based on bilateral iris analyses, create comprehensive wellness report.
    
    LEFT EYE FINDINGS:
    {json.dumps(left_analysis, indent=2)}
    
    RIGHT EYE FINDINGS:
    {json.dumps(right_analysis, indent=2)}
    
    PATIENT: {patient_info['name']}, Age {patient_info['age']}
    
    Create a 7-10 page comprehensive wellness report with:
    
    1. EXECUTIVE SUMMARY
    2. CONSTITUTIONAL ANALYSIS (both eyes)
    3. BODY SYSTEMS ASSESSMENT (all 5 systems)
    4. SIGNIFICANT FINDINGS
    5. CELLOXEN THERAPY PRIORITIES (C-102 to C-108)
    6. WELLNESS RECOMMENDATIONS
    7. GP REFERRAL (if needed)
    8. NEXT STEPS
    
    Use 100% BRITISH ENGLISH.
    Focus on wellness support, NOT medical diagnosis.
    Use analogies for accessibility.
    
    Return markdown-formatted report.
    """
    
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": synthesis_prompt
        }]
    )
    
    report_text = response.content[0].text
    
    return report_text
```

**Synthesis Result:**
```json
{
    "constitutional_summary": {
        "left_eye": "Mixed - Moderate strength",
        "right_eye": "Haematogenic - Moderate strength",
        "overall_strength": "Moderate - Good foundation with areas needing support"
    },
    "therapy_priorities": [
        {
            "priority": 1,
            "therapy": "C-108 Metabolic Balance",
            "reason": "Pancreatic zone patterns in both eyes"
        },
        {
            "priority": 2,
            "therapy": "C-107 Stress Support",
            "reason": "Pronounced nerve rings indicating stress adaptation"
        },
        {
            "priority": 3,
            "therapy": "C-105 Circulation",
            "reason": "General wellness enhancement"
        }
    ],
    "gp_referral_recommended": true,
    "gp_referral_reason": "Bilateral pancreatic zone patterns warrant metabolic evaluation",
    "confidence_score": 85.0,
    "report_text": "# COMPREHENSIVE IRIS WELLNESS REPORT\n\n..."
}
```

---

#### 4.3 DATABASE STORAGE

**Update iridology_analyses table:**
```sql
UPDATE iridology_analyses SET
    status = 'completed',
    constitutional_type = 'Mixed/Haematogenic',
    constitutional_strength = 'Moderate',
    combined_analysis = '{...JSON...}',
    report_text = '# COMPREHENSIVE IRIS WELLNESS REPORT...',
    confidence_score = 85.0,
    gp_referral_recommended = true,
    gp_referral_reason = 'Metabolic patterns require evaluation',
    completed_at = CURRENT_TIMESTAMP
WHERE analysis_id = 123;
```

---

### STEP 5: DISPLAY RESULTS
**Frontend:** Show analysis results page
**Data Displayed:**
- Patient information
- Constitutional type and strength
- Confidence score
- GP referral status
- Quick summary

**Actions Available:**
- View Full Report (opens report viewer)
- Download PDF Report (generates PDF)
- Start New Analysis
- Back to Dashboard

---

### STEP 6: VIEW COMPREHENSIVE REPORT
**User Action:** Click "View Full Report" button
**Frontend Page:** `/var/www/celloxen-portal/frontend/iridology_report.html`
**Backend API:** `GET /api/v1/iridology/{analysis_id}/report`

**Report Viewer Process:**
```javascript
// Frontend JavaScript
async function loadReport() {
    // Get analysis ID from URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    const analysisId = urlParams.get('id');
    
    // Fetch report data from API
    const response = await fetch(`/api/v1/iridology/${analysisId}/report`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
    });
    
    const data = await response.json();
    
    // Display patient info
    document.getElementById('patient-name').textContent = data.patient.name;
    document.getElementById('patient-number').textContent = data.patient.patient_number;
    
    // Convert markdown report to HTML
    const reportHtml = markdownToHtml(data.report_text);
    document.getElementById('report-content').innerHTML = reportHtml;
}
```

**Backend API Response:**
```json
{
    "success": true,
    "patient": {
        "name": "Sam Naqvi",
        "patient_number": "CLX-ABD-00003",
        "date_of_birth": "1960-01-01"
    },
    "analysis": {
        "id": 17,
        "analysis_number": "IR-ABD-2025-00013",
        "date": "16 November 2025",
        "constitutional_type": "Mixed/Haematogenic",
        "constitutional_strength": "Moderate",
        "confidence_score": 85.0,
        "gp_referral_recommended": true,
        "gp_referral_reason": "Metabolic patterns require evaluation"
    },
    "report_text": "# COMPREHENSIVE IRIS WELLNESS REPORT\n\n**Patient:** Sam Naqvi..."
}
```

---

### STEP 7: PRINT/SAVE REPORT
**User Action:** Click "Print Report" button
**Frontend:** Uses browser's native print function
**Format:** Clean, printable version (7-10 pages)
**User Can:** Save as PDF from print dialog

---

## 🔧 TECHNICAL COMPONENTS

### BACKEND FILES:
```
/var/www/celloxen-portal/backend/
├── simple_auth_main.py          # Main API routes
├── iridology_analyzer.py        # AI analysis logic
├── iridology_pdf_generator.py   # PDF generation (has bug)
└── iris_images/                 # Stored images directory
```

### FRONTEND FILES:
```
/var/www/celloxen-portal/frontend/
├── index.html                   # Main dashboard (includes iridology UI)
└── iridology_report.html        # Report viewer page
```

### DATABASE TABLES:
```
iridology_analyses              # Main analysis records
└── Links to: patients, clinics, users
```

---

## 📊 THERAPY PRIORITY LOGIC

**How Therapies Are Ranked:**
```python
def prioritize_therapies(body_systems, findings):
    """
    Ranks the 5 Celloxen therapies based on iris findings
    
    Therapies:
    - C-102: Vitality & Energy Support
    - C-104: Comfort & Mobility Support
    - C-105: Circulation & Heart Wellness
    - C-107: Stress & Relaxation Support
    - C-108: Metabolic Balance Support
    """
    
    priorities = []
    
    # RULE 1: Pancreatic zone patterns = C-108 Priority 1
    if findings['pancreatic_zone']['abnormal']:
        priorities.append(('C-108', 'Metabolic Balance', 
                          'Pancreatic zone patterns detected'))
    
    # RULE 2: Nerve rings = C-107 high priority
    if findings['nerve_rings']['count'] >= 3:
        priorities.append(('C-107', 'Stress Support',
                          'Multiple nerve rings indicate stress'))
    
    # RULE 3: Circulation issues = C-105
    if body_systems['circulatory']['rating'] == 'Needs Support':
        priorities.append(('C-105', 'Circulation',
                          'Circulatory system patterns'))
    
    # RULE 4: Joint/mobility = C-104
    if body_systems['musculoskeletal']['rating'] == 'Needs Support':
        priorities.append(('C-104', 'Mobility',
                          'Musculoskeletal support needed'))
    
    # RULE 5: Energy/vitality = C-102
    if body_systems['digestive']['rating'] == 'Needs Support':
        priorities.append(('C-102', 'Vitality',
                          'Digestive and energy support'))
    
    return priorities
```

---

## 🚨 GP REFERRAL LOGIC

**When GP Consultation Is Recommended:**
```python
def assess_gp_referral_needed(analysis_results):
    """
    Determines if GP consultation should be recommended
    
    Returns:
        (boolean, reason_string)
    """
    
    gp_needed = False
    reasons = []
    
    # CRITICAL: Pancreatic zone patterns
    if analysis_results['pancreatic_zone']['patterns_found']:
        gp_needed = True
        reasons.append("Pancreatic zone patterns suggest metabolic assessment needed")
    
    # Severe circulatory indicators
    if analysis_results['sodium_ring']['severe']:
        gp_needed = True
        reasons.append("Pronounced sodium ring warrants cardiovascular evaluation")
    
    # Multiple urgent findings
    urgent_count = sum(1 for system in analysis_results['body_systems'].values() 
                      if system.get('urgent', False))
    if urgent_count >= 2:
        gp_needed = True
        reasons.append("Multiple systems showing urgent patterns")
    
    # Patient age + concerning findings
    if analysis_results['patient_age'] >= 60 and urgent_count >= 1:
        gp_needed = True
        reasons.append("Age and wellness patterns warrant professional evaluation")
    
    reason_text = "; ".join(reasons) if gp_needed else None
    
    return gp_needed, reason_text
```

---

## 🔐 SECURITY & AUTHENTICATION

**API Authentication:**
- All iridology endpoints require valid JWT token
- Token stored in localStorage on frontend
- Passed in Authorization header: `Bearer {token}`

**Data Access Control:**
- Users can only access analyses for patients in their clinic
- Clinic ID verified on every request
- Patient data never crosses clinic boundaries

**Image Storage:**
- Images stored with unique filenames
- No direct URL access (must go through API)
- Images deleted after 90 days (configurable)

---

## 📈 PERFORMANCE CONSIDERATIONS

**Analysis Time:**
- Individual eye analysis: ~15-20 seconds each
- Bilateral synthesis: ~10-15 seconds
- **Total: 40-55 seconds** for complete analysis

**API Rate Limits:**
- Claude API: Rate limited by Anthropic
- Recommended: Max 10 analyses per hour per clinic

**Image Optimization:**
- Images resized to max 2000x2000 before AI analysis
- Reduces API payload size
- Faster processing times

---

## 🐛 KNOWN ISSUES

### ISSUE 1: PDF Download Button (500 Error)
**File:** `iridology_pdf_generator.py`
**Problem:** Undefined variable `text` around line 176
**Status:** Not fixed yet
**Workaround:** Use "Print to PDF" from report viewer instead

### ISSUE 2: Frontend Button Integration
**Problem:** Adding "View Report" button breaks React JSX structure
**Status:** Needs clean implementation
**Workaround:** Access report via direct URL: `/iridology_report.html?id={analysis_id}`

---

## 🎯 FUTURE ENHANCEMENTS (NOT IMPLEMENTED)

### 10+ Page Comprehensive Report
**Status:** Template ready (`/tmp/comprehensive_report_prompt.txt`)
**Needs:** Careful integration into `iridology_analyzer.py`
**Requirements:**
- Increase max_tokens from 4000 to 8000
- Replace synthesis_prompt at line 211
- Test thoroughly before deployment

### Sections to Include:
1. Executive Summary (1 page)
2. Constitutional Analysis - both eyes (2 pages)
3. Detailed Body Systems - ALL 5 (3 pages)
4. Personality & Constitutional Insights (1 page)
5. Diet & Nutrition Guidance (1.5 pages)
6. Celloxen Therapy Priorities (1 page)
7. Comprehensive Wellness Recommendations (1 page)
8. GP Referral Section
9. The Big Picture Summary (1 page)
10. Next Steps & Follow-up (0.5 pages)

---

## 📝 BRITISH ENGLISH REQUIREMENTS

**All reports must use British English spelling:**
- analyse (not analyze)
- colour (not color)
- fibre (not fiber)
- centre (not center)
- whilst (not while)
- programme (not program)
- optimise (not optimize)
- recognise (not recognize)

**This is enforced in AI prompts and verified in output**

---

## 🔄 DATA FLOW DIAGRAM
```
[User Selects Patient]
        ↓
[Start Analysis] → CREATE iridology_analyses record (status: pending)
        ↓
[Upload Left Eye] → SAVE image, UPDATE record
        ↓
[Upload Right Eye] → SAVE image, UPDATE record (status: ready)
        ↓
[Click Analyze] → AI Analysis Process:
        ├→ Analyze Left Eye (Claude API) → left_analysis.json
        ├→ Analyze Right Eye (Claude API) → right_analysis.json
        └→ Synthesize Both (Claude API) → comprehensive_report.md
        ↓
UPDATE iridology_analyses:
    - combined_analysis (JSON)
    - report_text (Markdown)
    - status: completed
    - constitutional_type
    - confidence_score
    - gp_referral_recommended
        ↓
[Display Results Page]
        ├→ [View Full Report] → iridology_report.html
        └→ [Download PDF] → (currently broken)
```

---

## ✅ TESTING CHECKLIST

**To verify system is working:**
- [ ] Can select patient
- [ ] Can start new analysis
- [ ] Can upload left eye image
- [ ] Can upload right eye image
- [ ] Analysis completes in < 60 seconds
- [ ] Results page displays
- [ ] Constitutional type shown
- [ ] Confidence score displayed
- [ ] Can access report viewer
- [ ] Report displays in British English
- [ ] Print function works
- [ ] Report is 7+ pages when printed

---

**Document Version:** 1.0
**Last Updated:** 17 November 2025
**System Status:** ✅ OPERATIONAL (7-page report version)
