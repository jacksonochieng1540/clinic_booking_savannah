

---

```markdown
# Clinic Booking System - Savannah

## Overview

Backend Technical Challenge - Clinic Booking System

A production-ready clinic appointment booking API built with Django REST Framework. Patients can book, cancel, and reschedule appointments with doctors in 30-minute slots.

**Live Demo:** [https://clinic-booking-1b3m.onrender.com](https://clinic-booking-1b3m.onrender.com)

**GitHub Repository:** [https://github.com/jacksonochieng1540/clinic_booking_savannah](https://github.com/jacksonochieng1540/clinic_booking_savannah)
---

## Available Functionalities

### Patient Features
- ✅ Register and login with email/password
- ✅ View available 30-minute slots for doctors
- ✅ Book appointments (validated against working hours)
- ✅ Cancel appointments with a reason
- ✅ Reschedule appointments to new slots
- ✅ View upcoming appointments sorted by date
- ✅ Prevention of bookings within 1 hour of now (Bonus)

### Doctor Features
- ✅ View today's appointments
- ✅ View upcoming appointments
- ✅ Manage working hours (Admin only)

### Admin Features
- ✅ Manage doctors and patients
- ✅ View system statistics
- ✅ Manage users (activate/deactivate)

---

## Tech Stack

| Category | Technology |
|----------|------------|
| **Backend** | Django 4.2, Django REST Framework |
| **Database** | PostgreSQL (Production), SQLite (Development) |
| **Authentication** | JWT (djangorestframework-simplejwt) |
| **Deployment** | Render |
| **CI/CD** | GitHub Actions |
| **Containerization** | Docker, docker-compose |
| **Testing** | Django Test Framework, Coverage |
| **Email** | Django Email (Console in dev, SMTP in prod) |
| **Code Quality** | Black, isort, flake8 |

---

## Database Schema

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│      User       │     │     Doctor      │     │    Patient      │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │◄────│ user (FK)       │     │ user (FK)       │
│ email           │     │ specialty       │◄────│ blood_type      │
│ first_name      │     │ license_number  │     │ allergies       │
│ last_name       │     │ years_exp       │     │ medical_history │
│ phone_number    │     │ consultation_fee│     └─────────────────┘
│ role            │     │ is_available    │            │
│ password        │     └─────────────────┘            │
└─────────────────┘            │                       │
         │                     │                       │
         ▼                     ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  UserProfile    │     │  WorkingHours   │     │   Appointment   │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ user (FK)       │     │ doctor (FK)     │     │ patient (FK)    │
│ bio             │     │ day_of_week     │     │ doctor (FK)     │
│ emergency_contact│    │ start_time      │     │ start_time      │
└─────────────────┘     │ end_time        │     │ end_time        │
                        │ is_available    │     │ status          │
                        └─────────────────┘     │ cancellation_reason│
                                                │ notes           │
                                                └─────────────────┘
```

---

## Tests

### Backend Test Coverage - 57 tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test appointments

# Run with coverage
coverage run manage.py test
coverage report
```

**Test Coverage Summary:**
- ✅ Accounts app tests
- ✅ Appointments app tests
- ✅ Doctors app tests
- ✅ Patients app tests
- ✅ Schedules app tests
- ✅ Core app tests

---

## Getting Started

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/jacksonochieng1540/clinic_booking_savannah.git
cd clinic_booking_savannah
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**

For Windows users:
```bash
venv\Scripts\activate
```

For Unix based systems:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

6. **Run migrations and seed data**
```bash
python manage.py migrate
python manage.py createsuperuser      # Create admin user
```

7. **Run the server**
```bash
python manage.py runserver
```

8. **Access the application**
- Home: http://localhost:8000
- Admin: http://localhost:8000/admin/
- API: http://localhost:8000/accounts/api/

### Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up --build
```

---

## Project Structure

```
clinic_booking_savannah/
├── .github/
│   └── workflows/
│       ├── ci.yml          # Continuous Integration
│       └── deploy.yml      # Continuous Deployment
├── accounts/               # Authentication app
│   ├── models.py           # User, UserProfile, UserActivityLog
│   ├── views.py            # Login, Register, Profile views
│   ├── views_dashboard.py  # Dashboard views
│   ├── serializers.py      # Authentication serializers
│   └── urls.py             # Authentication URLs
├── appointments/           # Appointments app
│   ├── models.py           # Appointment model
│   ├── views.py            # Create, Cancel, Reschedule
│   ├── serializers.py      # Appointment serializers
│   └── urls.py             # Appointment URLs
├── core/                   # Shared utilities
│   ├── exceptions.py       # Custom exception handler
│   ├── permissions.py      # Custom permissions
│   ├── email.py            # Email utilities
│   └── utils.py            # Helper functions
├── doctors/                # Doctors app
│   ├── models.py           # Doctor model
│   ├── views.py            # Doctor views
│   └── serializers.py      # Doctor serializers
├── patients/               # Patients app
│   ├── models.py           # Patient model
│   ├── views.py            # Patient views
│   └── serializers.py      # Patient serializers
├── schedules/              # Schedules app
│   ├── models.py           # WorkingHours model
│   ├── views.py            # Availability views
│   └── serializers.py      # Schedule serializers
├── templates/              # Django templates
├── clinic_booking/         # Project configuration
│   ├── settings.py         # Main settings
│   └── urls.py             # Main URLs
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

---

## API Endpoints Summary

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/accounts/api/register/` | POST | Register new user | None |
| `/accounts/api/login/` | POST | Login user | None |
| `/accounts/api/logout/` | POST | Logout user | JWT |
| `/accounts/api/profile/` | GET | Get user profile | JWT |
| `/accounts/api/change-password/` | POST | Change password | JWT |
| `/accounts/api/password-reset/` | POST | Request password reset | None |
| `/doctors/api/` | GET | List all doctors | None |
| `/doctors/api/{id}/` | GET | Get doctor details | None |
| `/schedules/api/doctors/{id}/availability/` | GET | Get available slots | None |
| `/appointments/api/` | GET | List appointments | JWT |
| `/appointments/api/create/` | POST | Book appointment | JWT |
| `/appointments/api/{id}/` | GET | Get appointment details | JWT |
| `/appointments/api/{id}/cancel/` | PATCH | Cancel appointment | JWT |
| `/appointments/api/{id}/reschedule/` | PATCH | Reschedule appointment | JWT |
| `/appointments/api/patients/{id}/appointments/` | GET | Patient's appointments (Bonus) | JWT |

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## License

This project is available as open source under the terms of the [MIT License](LICENSE).

---


