# Healthcare Platform API – Role‑Based Backend

A production‑ready REST API built with **FastAPI**, **async SQLAlchemy**, **PostgreSQL (Supabase)**, **JWT**, and **bcrypt**. Implements three core endpoints with role‑based access control enforced via middleware.

## 📦 Tech Stack
- Python 3.11
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL (Supabase free tier)
- PyJWT + bcrypt
- Pydantic v2
- pytest + httpx (testing)

## 🚀 Features
- **Patient registration** (`POST /patients`) – stores user credentials + patient details.
- **Authentication** (`POST /auth/login`) – returns JWT with `user_id` and `role`.
- **List all patients** (`GET /patients`) – only **Admin** or **Clinician** roles can access; **Patient** role gets `403 Forbidden` (enforced in **middleware**, not inline).
- **Separate tables** for `users` and `patients` (1:1 relationship).
- **UUID primary keys**, automatic `created_at` timestamps.
- **Async database** operations for high concurrency.

## 🧪 Testing
Comprehensive `pytest` suite covering:
- Patient registration (success, duplicate email, missing fields).
- Login (valid/invalid).
- Role‑based access to `GET /patients` (admin ✅, clinician ✅, patient ❌, no token ❌, invalid token ❌).

## 📁 Project Structure
```
healthcare-role-based-api/
├── app/
│   ├── main.py                 # FastAPI app + RoleBasedAccessMiddleware
│   ├── config.py               # Environment variables (Pydantic settings)
│   ├── database.py             # Async engine, session dependency
│   ├── models.py               # User & Patient tables (UUID, relationships)
│   ├── schemas.py              # Pydantic validators
│   ├── utils.py                # bcrypt, JWT helpers
│   └── routers/
│       ├── auth.py             # POST /auth/login
│       └── patients.py         # POST /patients, GET /patients
├── tests/                      # Async pytest suite
├── seed.py                     # Bootstrap admin & clinician users
├── .env.example
├── requirements.txt
├── postman_collection.json
└── README.md
```

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/tarun1sisodia/healthcare-role-based-api.git
cd healthcare-role-based-api
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
# or .\venv\Scripts\activate (Windows)
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `.env.example` to `.env` and fill in:
```ini
DATABASE_URL=postgresql+asyncpg://postgres:password@db.ref.supabase.co:5432/postgres?sslmode=require
JWT_SECRET_KEY=your-strong-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
> If your password contains special characters like `#`, URL‑encode them (`%23`).

### 5. Create database tables & seed admin/clinician users
```bash
python seed.py
```
This creates:
- `admin@clinic.com` / `admin123`
- `clinician@clinic.com` / `clinician123`

### 6. Run the server
```bash
uvicorn app.main:app --reload
```
API available at `http://localhost:8000`

## 📬 API Endpoints

| Method | Endpoint        | Description                     | Access                     |
|--------|-----------------|---------------------------------|----------------------------|
| POST   | `/patients`     | Register a new patient          | Public                     |
| POST   | `/auth/login`   | Login, receive JWT              | Public                     |
| GET    | `/patients`     | List all patients               | `admin` or `clinician` only |

### Example requests

#### 1. Register a patient
```bash
curl -X POST http://localhost:8000/patients \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "secure123",
    "name": "John Doe",
    "age": 30,
    "gender": "Male",
    "contact": "+1234567890"
  }'
```

#### 2. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@clinic.com", "password": "admin123"}'
```
Response:
```json
{"access_token": "eyJ...", "token_type": "bearer"}
```

#### 3. List patients (as Admin or Clinician)
```bash
curl -X GET http://localhost:8000/patients \
  -H "Authorization: Bearer YOUR_TOKEN"
```
If a **Patient** token is used → `403 Forbidden`.

## 🧪 Running Tests
```bash
pytest -v
```
Make sure a test database is configured (see `.env.test` example). The suite will create/drop tables in a separate schema.

## 🧠 Design Decisions
- **Middleware for RBAC** – The `GET /patients` endpoint contains **no role‑checking logic**. All enforcement happens in `RoleBasedAccessMiddleware`, as required.
- **Separate `users` and `patients` tables** – Normalises authentication data from medical records, allowing future addition of clinicians/admins without patient fields.
- **Async SQLAlchemy** – Non‑blocking DB operations for better concurrency.
- **UUID primary keys** – Avoids sequential ID enumeration attacks.
- **Bcrypt hashing** – Industry standard for password storage.
- **Explicit allowlist in middleware** – Only `admin` and `clinician` roles can access; any missing/malformed role is rejected.
- **Postman collection** – Included for quick manual testing.

## 🔧 Potential Improvements (Not Required)
- Use Alembic for migrations instead of `create_all`.
- Add an index on `Patient.created_at` for faster sorting.
- Implement refresh tokens & token blacklisting.

## 📄 License
This project is for evaluation purposes only.

## 👥 Collaborators
- Add `tarun@example.com` and `reviewer@example.com` as collaborators on your private GitHub repo.
