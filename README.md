# 🎯 AI Career Guide Agent

> **Supports SDG 8: Decent Work and Economic Growth**  
> Helping skilled youth in Tier-2/3 cities of India find the right career path.

---

## 📁 Project Structure

```
ai_career_guide/
│
├── app.py                      ← Main Streamlit app (run this)
├── requirements.txt            ← Python dependencies
│
├── data/
│   ├── job_roles.json          ← Dataset: 20 job roles with skills, resources, city data
│   └── feedback_log.csv        ← Auto-created: stores user feedback ratings
│
└── utils/
    ├── matcher.py              ← Skill-to-job matching engine (weighted scoring)
    ├── resume_generator.py     ← ATS-friendly PDF resume builder (ReportLab)
    └── translations.py         ← Hindi + English bilingual strings
```

---

## ⚙️ Setup & Run (5 minutes)

### Prerequisites
- Python 3.9 or higher
- pip

### Step 1 — Clone / download the project
```bash
cd ai_career_guide
```

### Step 2 — Create a virtual environment (recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Run the app
```bash
streamlit run app.py
```

The app opens automatically at **http://localhost:8501**

---

## 🌐 Features

| Feature | Description |
|---|---|
| 🗣️ Bilingual | Full Hindi + English support |
| 💬 Chat UI | Conversational profile builder (6 questions) |
| 🎯 Job Matching | Weighted scoring across 20 career paths |
| 📌 Skill Gap | Shows what you have vs what you need |
| 📚 Roadmap | Free resources: IBM SkillsBuild, NPTEL, YouTube |
| 📍 Local Jobs | City-specific job availability notes |
| 📄 Resume PDF | ATS-friendly, downloadable resume |
| ⭐ Feedback | 1–5 rating logged for success metrics |

---

## 🎤 Demo Script (for Presentation)

> Use this exact flow for a live demo

### 1️⃣ Open the app
```
http://localhost:8501
```

### 2️⃣ Welcome Screen
- Show the SDG 8 badge
- Switch language to **हिंदी** → switch back to **English**
- Click **"Start →"**

### 3️⃣ Chat — Answer these 6 questions (copy-paste for speed)
| Question | Demo Answer |
|---|---|
| Education | `B.Tech` |
| Skills | `Python, Excel, SQL, Communication` |
| Interests | `computers, data, analysis` |
| City | `Indore` |
| Experience | `fresher` |
| Work type | `remote` |

### 4️⃣ Analysing Screen
- Point out the 4-step progress indicator
- "The engine is scoring 20 career roles against Priya's profile in real time"

### 5️⃣ Results Screen — highlight 3 key points
1. **"Look — Data Analyst is a 72% match because she has Python, Excel, and SQL"**
2. **"Skill Gap: She only needs to learn Power BI"**
3. **"Local note: Banks and hospitals in Indore are hiring data analysts right now"**
4. Click on the **IBM SkillsBuild** link to show real resources

### 6️⃣ Resume Builder
- Enter name: `Priya Sharma`
- Enter phone: `+91 98765 43210`
- Click **"Download Resume as PDF"**
- Open the downloaded PDF and show it is clean and ATS-ready

### 7️⃣ Feedback
- Give rating: **5 stars**
- Show: "This rating is saved to feedback_log.csv for our success metrics"

### 8️⃣ Closing Lines
> "In under 3 minutes, Priya went from confused to having a career plan, a skill roadmap, and a resume — all for free, in her own language, from Indore."

---

## 📊 Success Metrics Tracked

| Metric | How tracked |
|---|---|
| Users guided | Session counter in session_state |
| Analyses completed | Counter incremented after job matching |
| Resumes generated | Counter incremented after PDF creation |
| Feedback ratings | Saved to `data/feedback_log.csv` |

---

## 🗂️ Job Roles Dataset (20 roles)

Web Developer, Data Analyst, Graphic Designer, Digital Marketer, Python Developer,
Cybersecurity Analyst, ML/AI Engineer, Content Writer, Accountant/Tally Operator,
Mobile App Developer, HR Executive, Electrical/Electronics Technician, Cloud Engineer,
Sales Executive, Network Engineer, Video Editor/Content Creator, Customer Support Executive,
Teacher/Online Educator, Civil Engineer, UI/UX Designer

---

## 🔮 Future Scope (Out of MVP)

- Live job listings API (Naukri, LinkedIn)
- Voice input in Hindi
- Regional languages: Tamil, Telugu, Bengali, Marathi
- Mock interview simulator
- Mentor connection marketplace
- WhatsApp chatbot version

---

## 🙏 Credits

- **IBM SkillsBuild** — free certification resources included
- **NPTEL** — free Indian engineering and management courses
- **SDG 8** — United Nations Sustainable Development Goal 8
- Built with Streamlit, ReportLab, and pure Python

---

*AI Career Guide — Empowering India's Tier-2/3 youth, one career at a time.*
