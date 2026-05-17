# DailyPlus AI - New Architecture Plan
## Complete Replacement: Streamlit → HTML/CSS/JS SPA

**Date**: 2026-05-17  
**Status**: Planning Phase  
**Objective**: Replace Streamlit application with custom Single Page Application

---

## 🎯 Architecture Overview

### Current State (Streamlit)
```
Browser → Streamlit Server (Python) → AI Processing → Gemini API
```

### New State (Custom SPA)
```
Browser (HTML/CSS/JS) → REST API (Flask/FastAPI) → AI Processing → Gemini API
```

---

## 📋 Design Specifications

### Color Palette (Grey & White Theme)
- **Background**: Pure White `#ffffff`
- **Main Text**: Dark Grey `#333333`
- **Muted Text**: Medium Grey `#666666`
- **Borders/Dividers**: Light Grey `#e0e0e0`
- **Accent/Cards**: Very Light Grey `#f4f4f4`

### Typography
- **Font Stack**: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`
- **Logo**: Bold, `-0.5px` letter spacing
- **Clean, minimal aesthetic**

### Animations
- **Fade-in**: `0.3s` smooth transition
- **Slide-up**: Slight upward movement on tab switch
- **Hover**: `-5px` translate-Y on cards

### Layout
- **Max Width**: `1200px` centered
- **Padding**: `4rem 5%`
- **Header**: Sticky navigation
- **Footer**: Simple centered copyright

---

## 🏗️ Application Structure

### Frontend (Single HTML File)

#### Navigation Tabs (4 sections)
1. **Overview** - "Intelligence, Simplified"
2. **Capabilities** - "Core Capabilities"
3. **Architecture** - "System Architecture"
4. **Connect** - Contact form

#### Tab Content Details

**Tab 1: Overview**
- Heading: "Intelligence, Simplified."
- Description: Streamlines complex workflows through intuitive ML
- Layout: 2-column grid
- Cards: "Data Cleaning", "Predictive Modeling"

**Tab 2: Capabilities**
- Heading: "Core Capabilities"
- Description: Infrastructure for performance and stability
- Layout: 3-column grid
- Cards: "Exploratory Analysis", "Two-Way Validation", "Scalable Queries"

**Tab 3: Architecture**
- Heading: "System Architecture"
- Content: Two paragraphs on "less is more" philosophy
- Emphasis: Data-driven, minimal UI, scalable

**Tab 4: Connect**
- Heading: "Connect with Us"
- Form Fields:
  - Name (text input)
  - Email Address (email input)
  - Project Details (textarea)
- Submit Button: Dark grey with white text
- Action: JavaScript alert on submission

### Backend (Python REST API)

#### Technology Choice
**Recommended**: FastAPI (modern, async, auto-documentation)
**Alternative**: Flask (simpler, more established)

#### API Endpoints

```
POST /api/process-briefing
- Input: Daily context data
- Output: AI-processed morning briefing
- Uses: src/ai/processor.py

GET /api/load-data
- Input: None
- Output: Mock daily context
- Uses: src/ingest/loader.py

POST /api/generate-draft
- Input: Draft context and requirements
- Output: AI-generated draft
- Uses: src/ai/processor.py

POST /api/contact
- Input: Name, email, message
- Output: Success/failure status
- Action: Send email or store inquiry
```

---

## 📁 New File Structure

```
DailyPlus_AI/
├── frontend/
│   └── index.html              # Single HTML file (all CSS/JS inline)
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI/Flask app
│   │   ├── routes.py          # API endpoints
│   │   └── middleware.py      # CORS, security
│   └── requirements.txt       # API dependencies
├── src/                       # Existing AI logic (preserved)
│   ├── ai/
│   │   ├── processor.py
│   │   └── prioritizer.py
│   └── ingest/
│       ├── loader.py
│       └── sanitizer.py
├── config/                    # Existing config (preserved)
│   └── settings.py
├── data/                      # Existing data (preserved)
│   └── mock_daily_context.json
└── docs/
    └── NEW_ARCHITECTURE_PLAN.md
```

---

## 🔄 Migration Strategy

### Phase 1: Backend API Development
1. Stop Streamlit server
2. Create FastAPI application structure
3. Implement API endpoints
4. Integrate existing AI processing logic
5. Add CORS and security middleware
6. Test API endpoints with Postman/curl

### Phase 2: Frontend Development
7. Create single HTML file with inline CSS
8. Implement 4-tab navigation structure
9. Add grey/white theme styling
10. Implement vanilla JavaScript for interactivity
11. Add form validation and submission logic

### Phase 3: Integration
12. Connect frontend to backend API using fetch()
13. Implement error handling
14. Add loading states and animations
15. Test complete user flows

### Phase 4: Deployment & Documentation
16. Update deployment instructions
17. Configure production server (Gunicorn/Uvicorn)
18. Set up reverse proxy (Nginx)
19. Document API endpoints
20. Create user guide

---

## 🛠️ Technical Implementation Details

### Backend API (FastAPI Example)

```python
# backend/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.ai.processor import DailyContextProcessor
from src.ingest.loader import load_mock_data

app = FastAPI(title="DailyPlus AI API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/process-briefing")
async def process_briefing(context: dict):
    processor = DailyContextProcessor()
    result = await processor.process(context)
    return result

@app.get("/api/load-data")
async def load_data():
    data = load_mock_data()
    return data

@app.post("/api/generate-draft")
async def generate_draft(draft_context: dict):
    processor = DailyContextProcessor()
    draft = await processor.generate_draft(draft_context)
    return draft

@app.post("/api/contact")
async def contact(name: str, email: str, message: str):
    # Handle contact form submission
    return {"status": "success", "message": "Inquiry submitted"}
```

### Frontend Structure (HTML)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DailyPlus AI</title>
    <style>
        /* Grey & White Theme CSS */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #ffffff;
            color: #333333;
        }
        /* Navigation, tabs, cards, animations... */
    </style>
</head>
<body>
    <header>
        <nav>
            <div class="logo">DailyPlus AI</div>
            <div class="tabs">
                <button class="tab-btn active" data-tab="overview">Overview</button>
                <button class="tab-btn" data-tab="capabilities">Capabilities</button>
                <button class="tab-btn" data-tab="architecture">Architecture</button>
                <button class="tab-btn" data-tab="connect">Connect</button>
            </div>
        </nav>
    </header>
    
    <main>
        <section id="overview" class="tab-content active">
            <!-- Overview content -->
        </section>
        <section id="capabilities" class="tab-content">
            <!-- Capabilities content -->
        </section>
        <section id="architecture" class="tab-content">
            <!-- Architecture content -->
        </section>
        <section id="connect" class="tab-content">
            <!-- Contact form -->
        </section>
    </main>
    
    <footer>
        <p>&copy; 2026 DailyPlus AI. All rights reserved.</p>
    </footer>
    
    <script>
        // Vanilla JavaScript for tab switching and API calls
        const API_BASE = 'http://localhost:8000';
        
        // Tab switching logic
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                // Remove active class from all
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked
                btn.classList.add('active');
                const tabId = btn.getAttribute('data-tab');
                document.getElementById(tabId).classList.add('active');
            });
        });
        
        // Form submission
        document.getElementById('contact-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const response = await fetch(`${API_BASE}/api/contact`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(Object.fromEntries(formData))
            });
            if (response.ok) {
                alert('Inquiry submitted successfully.');
            }
        });
    </script>
</body>
</html>
```

---

## ⚠️ Important Considerations

### Pros of This Approach
✅ Complete control over UI/UX  
✅ Single HTML file (easy deployment)  
✅ No framework dependencies  
✅ Elegant, minimal design  
✅ Fast loading times  

### Cons of This Approach
❌ Loses Streamlit's built-in features (session state, caching, widgets)  
❌ Requires building REST API from scratch  
❌ More complex deployment (frontend + backend)  
❌ Need to reimplement all UI interactions in JavaScript  
❌ No hot-reload during development  

### Complexity Assessment
- **Backend API**: Medium complexity (2-3 days)
- **Frontend SPA**: Low complexity (1-2 days)
- **Integration**: Medium complexity (1-2 days)
- **Testing**: Medium complexity (1-2 days)
- **Total Estimated Time**: 5-9 days

---

## 🚀 Next Steps

1. **Confirm Approach**: User approval of complete Streamlit replacement
2. **Choose Backend Framework**: FastAPI (recommended) or Flask
3. **Develop Backend API**: Create REST endpoints
4. **Create Frontend**: Single HTML file with design specs
5. **Integrate & Test**: Connect frontend to backend
6. **Deploy**: Set up production environment
7. **Document**: Update all documentation

---

## 📝 Notes

- This is a **major architectural change** from Streamlit to custom SPA
- All existing AI processing logic in `src/` will be preserved and reused
- The new architecture separates frontend (HTML/CSS/JS) from backend (Python API)
- Consider if this complexity is necessary vs. adapting design to Streamlit

---

**Status**: Awaiting user confirmation to proceed with implementation