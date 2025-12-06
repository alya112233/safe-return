# عودة آمنة - Safe Return

<div align="center">

🏠 **برنامج دعم إعادة الاندماج للمفرج عنهم**

A Saudi-style reentry support service prototype for people released from prison.

</div>

---

## 📋 Overview

**عودة آمنة (Safe Return)** is a digital service integrated into a simulated government portal (like Absher) that provides:

- **12-month follow-up plans** linked to national ID
- **Monthly check-ins** covering housing, employment, mental state, and family situation
- **Risk assessment** with automatic flagging (🟢 Green / 🟡 Yellow / 🔴 Red)
- **Job recommendations** based on location
- **Support ticket system** for social, psychological, and housing assistance
- **Case worker dashboard** for monitoring and intervention

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```powershell
# 1. Navigate to project directory
cd safe_return_project

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Run migrations
python manage.py migrate

# 4. Create demo data
python manage.py seed_data

# 5. Start the server
python manage.py runserver
```

### Access the Application

Open your browser to: **http://127.0.0.1:8000/**

---

## 👥 Demo Users

After running `seed_data`, you can log in as:

### Beneficiaries (المستفيدون)
| Name | Status | Description |
|------|--------|-------------|
| أحمد محمد العتيبي | 🟢 Green | Stable case, 3 months in |
| خالد سعد الغامدي | 🟡 Yellow | Needs job support |
| عبدالله فيصل الدوسري | 🔴 Red | Urgent intervention needed |
| محمد علي الشهري | 🟢 Green | New case (just released) |
| سلطان ناصر المطيري | 🟢 Green | Almost completed (month 11) |

### Case Workers (الأخصائيون)
| Name | Role |
|------|------|
| فهد الزهراني | Case Worker |
| سارة القحطاني | Case Worker |

---

## 📁 Project Structure

```
safe_return_project/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3                 # SQLite database
├── safe_return/               # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                      # Main application
│   ├── models.py              # Data models
│   ├── views.py               # Views (template + API)
│   ├── urls.py                # URL routing
│   ├── serializers.py         # DRF serializers
│   ├── risk_engine.py         # Risk calculation logic
│   ├── admin.py               # Django admin config
│   ├── templates/core/        # HTML templates
│   └── management/commands/   # Custom commands
└── static/css/                # Static files
```

---

## 🔧 Core Features

### 1. Monthly Check-in Form
Beneficiaries submit monthly reports on:
- 🏠 Housing status (stable, temporary, with family, homeless)
- 💼 Job status (employed, self-employed, searching, unemployed, training)
- 🧠 Mental state (good, moderate, stressed, bad)
- 👨‍👩‍👧‍👦 Family status (supportive, neutral, problematic, no contact)

### 2. Risk Assessment Engine
Automatic risk level calculation:
- **🔴 RED**: `mental_state == 'bad'` OR `housing_status == 'homeless'`
- **🟡 YELLOW**: `job_status == 'unemployed'` OR `family_status == 'problematic'`
- **🟢 GREEN**: All other cases

### 3. Support Ticket System
Auto-generated tickets for:
- Psychological support (bad mental state)
- Housing support (homeless)
- Job support (unemployed)
- Social support (family problems)

### 4. Case Worker Dashboard
- View all profiles with risk indicators
- Filter by risk level and city
- Create and manage support tickets
- Mark follow-up plans as completed

---

## 🌐 API Endpoints

REST API available at `/api/`:

| Endpoint | Description |
|----------|-------------|
| `GET /api/users/` | List all users |
| `GET /api/profiles/` | List release profiles |
| `GET /api/profiles/{id}/risk_summary/` | Get risk analysis |
| `GET /api/checkins/` | List monthly check-ins |
| `POST /api/checkins/` | Submit a check-in |
| `GET /api/jobs/` | List job opportunities |
| `GET /api/tickets/` | List support tickets |
| `GET /api/notifications/` | List notifications |

---

## 🎨 UI Features

- **Arabic RTL support** (right-to-left layout)
- **Saudi government portal simulation** (Absher-style header)
- **Responsive design** (works on mobile)
- **Risk color coding** throughout the UI
- **Progress visualization** for 12-month plan

---

## 📞 Simulated Support Resources

The prototype includes references to real Saudi support services:
- **خط تراحم للدعم النفسي**: 920033360
- **الضمان الاجتماعي**: 800-124-1212
- **منصة دروب**: doroob.sa (training)
- **طاقات**: taqat.sa (job search)

---

## 🛠️ Development

### Run Development Server
```powershell
python manage.py runserver
```

### Access Django Admin
```powershell
# Create superuser first
python manage.py createsuperuser

# Then visit: http://127.0.0.1:8000/admin/
```

### Reset Database
```powershell
Remove-Item db.sqlite3
python manage.py migrate
python manage.py seed_data
```

---

## 📄 License

This is a hackathon prototype for demonstration purposes.

---

<div align="center">

**Built with ❤️ for social impact**

عودة آمنة - Safe Return | 2024

</div>

