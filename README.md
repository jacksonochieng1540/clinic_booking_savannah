# Clinic Booking System - Savannah

## Overview
Backend Technical Challenge - Clinic Booking System

A production-ready clinic appointment booking API built with Django REST Framework. Patients can book, cancel, and reschedule appointments with doctors in 30-minute slots.

**Live Demo:** [https://clinic-booking-1b3m.onrender.com](https://clinic-booking-1b3m.onrender.com)

**GitHub Repository:** [https://github.com/jacksonochieng1540](https://github.com/jacksonochieng1540/clinic_booking_savannah)

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

## API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/accounts/api/register/` | Register new user |
| POST | `/accounts/api/login/` | Login user |
| POST | `/accounts/api/logout/` | Logout user |
| GET | `/accounts/api/profile/` | Get user profile |
| POST | `/accounts/api/change-password/` | Change password |
| POST | `/accounts/api/password-reset/` | Request password reset |
| POST | `/accounts/api/token/refresh/` | Refresh JWT token |

### Clinic Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/doctors/api/` | List all doctors |
| GET | `/doctors/api/{id}/` | Get doctor details |
| GET | `/schedules/api/doctors/{id}/availability/?date=YYYY-MM-DD` | Get available slots |
| POST | `/appointments/api/create/` | Book appointment |
| GET | `/appointments/api/` | List appointments |
| GET | `/appointments/api/{id}/` | Get appointment details |
| PATCH | `/appointments/api/{id}/cancel/` | Cancel appointment |
| PATCH | `/appointments/api/{id}/reschedule/` | Reschedule appointment |
| GET | `/appointments/api/patients/{id}/appointments/` | Patient's upcoming appointments (Bonus) |

---

## Authentication

Users can register and login using email and password with JWT authentication.

### Register Endpoint

```http
POST /accounts/api/register/
Content-Type: application/json

{
    "email": "user@example.com",
    "username": "username",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "role": "patient"
}
