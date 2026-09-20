# CIVIQ — National Public Grievance Portal

Poora runnable Django project — `manage.py` ke saath. Extract karo aur seedha
migrations + runserver chala sakte ho.

## Setup (Termux) — ek baar ka setup, phir baar-baar export nahi karna

```bash
cd civiq_portal

# 1. Dependencies install karo
pip install -r requirements.txt --break-system-packages

# 2. .env file banao (sirf ek baar) — isme Gmail credentials daal do
cp .env.example .env
# ab .env file ko Acode mein kholo aur CIVIQ_GMAIL_USER /
# CIVIQ_GMAIL_APP_PASSWORD ki real values bhar do

# 3. Migrations
python manage.py makemigrations civiq
python manage.py migrate

# 4. Superadmin banao
python manage.py createsuperuser

# 5. Server chalao — ab koi export command nahi chahiye
python manage.py runserver 0.0.0.0:8000
```

`.env` file `.gitignore` mein hai — GitHub pe kabhi push nahi hogi, safe hai.
Ab jab bhi terminal band-khol karoge, `settings.py` khud `.env` se values utha
lega — bas ek baar bharna hai.

## Live Deploy (Render — tumhara wahi purana RiBhay portfolio wala setup)

Render pe `.env` file nahi chalti — wahan environment variables seedhe
**dashboard mein** set karte ho, aur wo hamesha ke liye set rehte hain (kabhi
export nahi karna padta):

1. GitHub pe is project ko push karo (jaisa tum RiBhay portfolio ke liye
   karte ho — Termux se `git add`, `git commit`, `git push`).

2. Render pe naya **Web Service** banao, apna GitHub repo connect karo.

3. **Build Command:**
   ```
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py seed_departments
   ```
   (`seed_departments` zaroori hai kyunki free tier ka disk ephemeral hai —
   har restart/redeploy pe database khaali ho jaata hai, isliye ye har
   build pe dobara chalna chahiye taaki departments/emails hamesha maujood rahein.)

4. **Start Command:**
   ```
   gunicorn civiq_portal.wsgi:application
   ```

5. Render dashboard mein **Environment → Add Environment Variable** karke
   ye sab ek-ek baar daal do (hamesha ke liye save rahenge):

   | Key | Value |
   |---|---|
   | `CIVIQ_GMAIL_USER` | tumhara Gmail address |
   | `CIVIQ_GMAIL_APP_PASSWORD` | wahi 16-digit App Password |
   | `DJANGO_SECRET_KEY` | koi bhi lamba random string |
   | `DJANGO_DEBUG` | `False` |
   | `DJANGO_ALLOWED_HOSTS` | `yourapp.onrender.com` |

6. Deploy karo — bas. Ab har complaint pe email automatically jaati rahegi,
   bina kisi terminal command ke.

**Zaroori warning:** Render ke **free tier** ka disk *ephemeral* hota hai —
matlab `db.sqlite3` (saari complaints) aur uploaded photos har redeploy/restart
pe **delete ho jaate hain**. Isi wajah se departments/emails baar-baar
"gayab" ho jaate the. Iska permanent fix neeche diya hai.

## PERMANENT FIX: Free PostgreSQL attach karo (data kabhi delete nahi hoga)

1. Render dashboard → **New +** → **PostgreSQL** → free plan select karo → create karo.

2. Us Postgres instance ke page pe **"Internal Database URL"** copy karo.

3. Apni Web Service ke **Environment** tab mein jaake naya variable add karo:
   | Key | Value |
   |---|---|
   | `DATABASE_URL` | wahi Internal Database URL jo copy kiya |

4. Build Command wapas simple kar do (ab `seed_departments` sirf **ek baar**
   chalana hai, hamesha ke liye nahi — kyunki ab Postgres mein data delete
   nahi hoga):
   ```
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```

5. Deploy karo. Pehli baar deploy hone ke baad, Render ke **Shell** tab
   (agar available ho) ya ek baar Build Command mein temporarily
   `&& python manage.py seed_departments` add karke ek deploy chala do
   — data permanently save ho jaayega, phir Build Command wapas simple kar
   sakte ho.

Isse database `db.sqlite3` ki jagah Postgres use karega — koi code tumhe
badalna nahi hai, `settings.py` khud detect kar lega ki `DATABASE_URL`
set hai to Postgres use karo, warna local Termux pe SQLite hi chalega.

## Django Admin mein ab sirf ye baaki bacha hai (Sectors/Departments auto-seeded hain)

1. **OfficerProfile** — kisi existing User (pehle Django Admin mein User banao)
   ko officer bana ke department assign karo.

2. **TeamMember** — apna aur Riya ka entry `is_ribhay_credit=True` ke saath
   daalo taaki "Engineering Credits" section pe RiBhay Studio dikhe.

3. **StaticPage** — Citizen Charter, FAQs, Privacy Policy, About Us
   (`/page/<slug>/` pe accessible, footer mein bhi auto-list ho jaayenge).

## Emails kahaan store hoti hain (code mein nahi, database mein)

Officials ke Gmail/email addresses **Python code mein kahin nahi likhe** —
wo database ke **Department table** ke `contact_email` column mein rehte
hain. Jab koi complaint submit hoti hai, `views.py` sirf itna karta hai:
`complaint.department.contact_email` — yaani database se uss field ko
**read** karta hai aur usi pe mail bhejta hai. Agar database mein wo field
khaali hai, to mail kahin nahi jaayegi (kyunki bhejne ke liye address hi
nahi mila).

**Agar tumne Admin check kiya aur Department/Sector table khaali mile ya
`contact_email` khaali dikha, ye command chalao — turant fix ho jaayega:**

```bash
python manage.py seed_departments
```

Ye 5 departments aur 13 categories ko unke real email/helpline ke saath
daal dega (already exist karte hon to sirf refresh kar dega — safe hai,
duplicate nahi banayega). Chalane ke baad terminal mein har department ka
naam aur uski email print hogi — confirm ho jaayega ki data aa gaya.

**Data kyun khaali reh gaya hoga (common reasons):**
- Purana zip use kiya jisme ye seeding feature nahi thi
- `python manage.py migrate` sirf ek baar chalaya tha, us waqt naya
  `0002_seed_data.py` file abhi zip mein nahi thi
- `db.sqlite3` file purani hai jo kabhi delete-recreate nahi hui

Verify karne ke liye:
```bash
python manage.py shell -c "from civiq.models import Department; [print(d.name, '->', d.contact_email) for d in Department.objects.all()]"
```



Tumhe manually kuch nahi daalna — `migrate` chalate hi ye sab automatically
database mein aa jaayega:

**13 Categories (Sectors):** Potholes & Road Damage, Garbage Collection,
Street Lighting, Stray Animals, Illegal Encroachment, Water Supply,
Sewage & Drainage, Power Outage & Faults, Electricity Billing, Traffic
Signal Fault, Illegal Parking, Mosquito & Disease Control, Hospital
Sanitation.

**5 Departments**, har ek real publicly-listed Lucknow government contact
ke saath:

| Department | Email | Helpline |
|---|---|---|
| Nagar Nigam Lucknow | nnlko@nic.in | 1533 |
| Jal Sansthan / Jalkal Vibhag | nnlko@nic.in (Nagar Nigam ka hi wing) | 8177054003 |
| MVVNL (Power/Discom) | cccmvvnl1912@gmail.com | 1912 |
| Traffic Directorate, UP Police | dirtraffic-up@nic.in | 1073 |
| CMO Lucknow (Public Health) | cmolko@gmail.com | 0522-2622080 |

**Zaroori disclaimer:** Ye contacts publicly-listed official sources se
liye gaye hain (Nagar Nigam/UP Police/MVVNL ki apni websites), lekin
government contacts time ke saath badalte rehte hain. Real complaints
bhejne se pehle Django Admin mein jaake har Department ka `contact_email`
ek baar khud verify/confirm kar lena — especially Jal Sansthan ka, jiska
koi alag public email nahi mila (isliye Nagar Nigam ka hi email daala hai).
Agar tumhe koi department ka zyada accurate/current email pata ho, Admin
mein jaake update kar dena — baaki sab kaam automatic rahega.



Jab citizen complaint lodge karta hai aur NLP engine se department detect ho
jaata hai, to us **Department.contact_email** pe automatically ek email chali
jaati hai — sector, priority, citizen details, location, aur photo evidence
(attachment ke saath).

Ye chalane ke liye Gmail App Password chahiye (2-Step Verification account
mein on hona zaroori hai): https://myaccount.google.com/apppasswords

```bash
export CIVIQ_GMAIL_USER="yourteam@gmail.com"
export CIVIQ_GMAIL_APP_PASSWORD="xxxxxxxxxxxxxxxx"   # 16-char app password, spaces hata dena
python manage.py runserver 0.0.0.0:8000
```

Ye env variables set nahi karoge to emails console mein hi print hongi (crash
nahi honge) — taaki bina Gmail set kiye bhi form test kar sako.

**Zaroori:** Django Admin mein har **Department** ka `contact_email` field
bharo — jis department ka email khaali hoga, uske liye mail skip ho jaayegi
(citizen ki submission fir bhi safal rahegi, sirf log mein warning aayega).



```
civiq_portal/
├── manage.py
├── requirements.txt
├── civiq_portal/          # project package (settings, root urls)
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── civiq/                 # the app
    ├── models.py
    ├── admin.py
    ├── views.py
    ├── urls.py
    ├── apps.py
    ├── context_processors.py
    ├── utils/nlp_engine.py
    ├── migrations/
    ├── templates/
    └── static/
```

## NEW: AI Camera Reporting (`/report/`)

Ek naya, parallel reporting flow add hua hai — purana `/lodge/` (manual text
form + department email) **bilkul waisa hi hai, kuch nahi hata**. Ye naya
flow sirf **database/Admin tak** save karta hai, koi email nahi bhejta
(future mein department routing add karne ke liye architecture ready hai).

**Naya flow:** Home/Navbar → "Report with AI" → Camera khulti hai → Photo
capture (ya desktop pe upload fallback) → "Analyze" → AI photo dekh ke
problem, category (existing Sectors mein se hi), description, priority
suggest karta hai → Citizen review/edit karta hai → Submit → Tracking ID
ke saath success page → Django Admin mein turant dikh jaata hai.

### Files changed
- `civiq/models.py` — Complaint model mein 3 naye fields add kiye
  (`problem_type`, `ai_confidence`, `ai_processed`), aur `PRIORITY_CHOICES`
  / `STATUS_CHOICES` mein naye options additively add kiye (purane options
  bilkul waise hi hain, kuch delete nahi hua).
- `civiq/admin.py` — Complaint admin mein naye fields dikhte hain
  (list_display, filters, search), + ek clickable OpenStreetMap location
  link.
- `civiq/views.py` — naye AI report views add kiye.
- `civiq/urls.py` — naye `/report/...` routes add kiye.
- `civiq/templates/base.html`, `index.html` — navbar/hero mein "Report with
  AI" CTA add kiya (purane "Lodge Grievance"/"Track Status" buttons wahin
  hain).
- `civiq_portal/settings.py` — AI provider config add kiya; ek pehle se
  maujood static-files bug bhi fix kiya (isse pehle `collectstatic`/`check`
  fail ho sakta tha).

### Files newly created
- `civiq/ai/__init__.py`, `analyzer.py`, `prompts.py`, `services.py` —
  modular AI service layer (views se alag, koi tight coupling nahi).
- `civiq/templates/ai_report_home.html`, `ai_camera.html`, `ai_success.html`
- `civiq/static/civiq/js/camera.js`, `location.js`, `ai-report.js`
- `civiq/static/civiq/css/camera.css`, `report.css`

### Database / model changes
`Complaint` model mein 3 naye column: `problem_type` (text), `ai_confidence`
(decimal 0–1), `ai_processed` (true/false). `priority` aur `status` ke
choice-lists mein naye options add hue (`low`/`medium`/`critical` aur
`new`/`in_review`) — koi purana value hata nahi.

### Migration instructions
Same pattern jo pehle se use kar rahe ho:
```bash
python manage.py makemigrations civiq
python manage.py migrate
```
Purani migrations (`0001_initial`, `0002_seed_data`) ko haath mat lagana —
bas ye naya `makemigrations` naya migration file bana dega jo sirf ye 3 naye
column + choices update add karega.

### Environment variables required (AI setup)
`.env` file (ya Render ke Environment tab) mein:
```
AI_PROVIDER=anthropic
AI_API_KEY=
AI_MODEL=claude-sonnet-4-6
```
- `AI_API_KEY` **khaali chhod sakte ho** — tab bhi poora flow kaam karega,
  bas AI "fallback/demo mode" mein chalega: category detect nahi hogi,
  citizen ko manually select karna padega. UI pe clearly "AI unavailable —
  fallback" notice dikhega.
- Real AI ke liye: Anthropic Console (console.anthropic.com) se ek API key
  banao aur `AI_API_KEY` mein daal do. Koi aur setup nahi chahiye — code
  khud image ko base64 karke Claude ke vision API ko bhejta hai aur uska
  JSON response parse karta hai.

### Exact commands to run
```bash
pip install -r requirements.txt --break-system-packages
python manage.py makemigrations civiq
python manage.py migrate
python manage.py seed_departments   # agar categories/departments pehle se nahi hain
python manage.py runserver 0.0.0.0:8000
```
Phir browser mein `/report/` kholo.

### Limitations / fallback behavior
- Agar `AI_API_KEY` set nahi hai, ya AI call fail ho jaaye (network issue,
  invalid response, etc.) — application crash nahi hoga. Ek clearly-marked
  fallback result dikhega aur citizen manually category/description bhar
  sakta hai. Ye kabhi bhi fake AI result ke roop mein present nahi hota.
- Is version mein AI-reported complaints **kisi department ko email nahi
  jaati** — sirf database/Admin mein save hoti hain (jaisa spec mein
  explicitly manga gaya tha). Purana `/lodge/` flow abhi bhi email bhejta
  hai, jaisa pehle se tha.
- AI se detect hui category hamesha existing `Sector` records se hi match
  hoti hai (koi naya random category kabhi nahi banta) — agar match na
  mile, dropdown khaali reh jaata hai aur citizen khud select karta hai.
- Camera browser permission pe depend karta hai — agar denied ho ya device
  mein camera na ho (jaise laptop bina webcam), automatically file-upload
  wala fallback UI dikh jaata hai.
- Custom admin dashboard summary (total reports/high-priority counts widget
  Django Admin ke andar) is version mein nahi banaya — `/analytics/` page
  pehle se similar public metrics deta hai. Chaho to alag se bana sakta
  hoon.

## Notes

- SQLite database (`db.sqlite3`) use ho raha hai — zero extra setup, Termux-friendly.
  Migrate karte hi wo file auto-create ho jaayegi.
- Photo uploads (evidence, resolution proof, officer/team photos) ke liye Pillow
  zaroori hai — `requirements.txt` mein already hai.
- Termux FUSE `flock()` fix `settings.py` ke end mein already merged hai — agar
  `/sdcard` par project rakhoge to upload crash nahi hoga.
- NLP engine dependency-free hai — koi extra pip install nahi chahiye.
- Officer dashboard sirf un complaints ko dikhata hai jo `assigned_officer`
  field mein explicitly assign hain. Abhi auto-assignment sirf department set
  karta hai, officer nahi — agar chaho to lodge_complaint view mein department
  ke first active officer ko bhi auto-assign karwa sakta hoon, bata dena.
- Production deploy (Render, etc.) ke liye `settings.py` mein `SECRET_KEY`,
  `DEBUG=False`, `ALLOWED_HOSTS`, aur WhiteNoise add karna hoga — abhi ye
  local-dev-ready config hai.
