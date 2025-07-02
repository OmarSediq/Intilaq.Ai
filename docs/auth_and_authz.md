# Authentication & Authorization (Full Logic Overview)

The Intilaq AI platform implements a robust authentication and authorization system, using **JWT**, **Redis**, and **PostgreSQL**. The architecture separates the logic for **Regular Users** and **HR Users**, while sharing core services and infrastructure for token management and session control. The system is fully aligned with **Clean Architecture** principles and uses **Dependency Injection** to isolate concerns and enable testability.

---

## Regular User Authentication

### Registration & Verification

The `AccountService` coordinates the entire registration and verification logic:

- **Password Matching**: Validates that `password` equals `confirm_password`.
- **Duplicate Check**: Verifies if a username or email already exists.
- **User Creation**: Registers a new user with `is_verified = 0` in the `users` table.
- **Code Generation**: A 6-digit code is generated and stored using `UserRepository.save_reset_code()`. This is saved in the `reset_codes` table and/or Redis with a TTL of 5 minutes.
- **Verification**:
  - Verifies the code using both DB and Redis.
  - If `new_password` exists, the password is updated using a hash.
  - If not, `is_verified` is set to `1`.

### Login / Logout / Token Refresh

The `AuthService` handles session state with JWT:

- **Login**:
  - Validates credentials (`email`, `password`) against hashed values.
  - If the account is verified, generates both `access_token` and `refresh_token` via `TokenService`.
  - Stores `refresh_token` in Redis and sends both tokens as `HttpOnly` cookies.

- **Logout**:
  - Extracts `refresh_token` from cookie.
  - Verifies token against Redis.
  - Deletes stored token and clears cookies.

- **Refresh**:
  - Extracts `refresh_token`, verifies it via `TokenService`, and issues a new `access_token`.
  - Stores it as a secure cookie again.

---

## HR User Authentication

The HR auth flow is handled separately via dedicated services:

### Registration & Verification

- **`HRRegisterService`**:
  - Registers new HR users into `hr_users`.
  - Generates and stores a reset code into `reset_codes`.

- **`HRVerificationService`**:
  - Validates the reset code and sets `is_verified = 1` on the HR user.

- **Code Resending**:
  - Only allowed if user is not verified.
  - Sends a new 6-digit code via `send_email()` utility.

### Login

- **`HRAuthService`**:
  - Verifies business email and password.
  - On success, generates `access_token` and `refresh_token`.
  - Tokens are stored in Redis and set as cookies (`HttpOnly`, `Secure`).

---

## TokenService (Shared)

This service abstracts all JWT logic and is reused by both user types.

- **Token Generation**:
  - `create_access_token(user_id, role)` – valid for 15 minutes.
  - `create_refresh_token(user_id)` – valid for 7 days.

- **Token Storage**:
  - `store_refresh_token(user_id, token)` → Redis (`user:{id}:refresh_token`)
  - `get_stored_refresh_token(user_id)` → used for validation
  - `delete_refresh_token(user_id)` → clears Redis entry

- **Token Decoding & Validation**:
  - Verifies JWT signature, expiry, and structure.

---

## Redis-Based Session & Code Handling

### `CodeRedisRepository`

Used for:
- Storing temporary verification codes (keyed by email).
- Valid for 5 minutes using `setex`.
- Deleted after use or expiry.

### `SessionRedisRepository`

Used to manage:
- Current question index per interview session.
- Completed questions set.
- Session status tracking (e.g., `in_progress`, `completed`).
- All stored with user/session-specific keys.

---

## Database Design (PostgreSQL)

- `users`: Holds all regular user data and verification status.
- `hr_users`: Contains HR-specific data, including business details.
- `reset_codes`: Common table used for both user types for email-based verification.

---

## Authentication Middleware

File: `backend/core/middlewares/auth_logging.py`

### Responsibilities:

- Reads `access_token` from request cookies.
- Decodes and verifies the token using `TokenService`.
- On valid token:
  - Extracts `user_id` and `role`.
  - Sets `request.state.user = {user_id, role}` for use in any route.
  - Logs every authenticated request.
- On expired or invalid token:
  - Logs a warning and proceeds anonymously (non-blocking).

---

## Security Layers Overview

| Layer             | Used For                          | Technologies                       |
|------------------|-----------------------------------|------------------------------------|
| Token             | Session authentication            | JWT (access & refresh)             |
| Token Storage     | Refresh token persistence         | Redis                              |
| Code Validation   | Account verification & reset      | Redis & PostgreSQL `reset_codes`   |
| Cookie Handling   | Stateless session propagation     | FastAPI secure cookies             |
| Middleware        | Silent session validation         | Custom `BaseHTTPMiddleware`        |

---

## Sample Authentication Flow

1. User registers  
2. User receives 6-digit verification code via email  
3. User verifies → system sets `is_verified = 1`  
4. User logs in → JWT access/refresh tokens are issued and stored in cookies  
5. Cookies (`access_token`, `refresh_token`) are sent automatically with each request  
6. `AuthenticationMiddleware` extracts the token, validates it, and attaches user data to `request.state.user`
