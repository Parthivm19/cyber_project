# 🎬 CineVault Security Documentation

CineVault is a secure movie booking platform built with Flask and Python, designed to satisfy rigorous web security standards and demonstrate practical countermeasures against common vulnerabilities.

This document outlines the security measures implemented in the application, mapping them to the project requirements and corresponding lab exercises.

## 🔐 1. Authentication & Authorization

*   **Password Hashing (`auth.py`)**: 
    *   **Mechanism:** Uses `flask-bcrypt` to hash passwords before storing them in the database.
    *   **Lab Connection:** Demonstrates the defense against attacks practiced in the **John the Ripper** lab. Even if the database is leaked, attackers cannot recover plaintext passwords without significant computational effort.
*   **Role-Based Access Control (RBAC) (`admin.py`)**:
    *   **Mechanism:** Implements a custom `@admin_required` decorator to protect administrative routes. The user's role (`user` or `admin`) is verified from the server-side session.
    *   **Defense:** Prevents unauthorized privilege escalation and forced browsing to sensitive endpoints.
*   **Session Management (`app.py`)**:
    *   **Mechanism:** Uses `flask-login` for session handling. Configured `SESSION_COOKIE_HTTPONLY = True` (prevents client-side script access to the session cookie) and `SESSION_COOKIE_SECURE = True` (ensures cookies are only sent over HTTPS). Added a permanent session lifetime of 30 minutes.
*   **Brute Force Protection (`auth.py` & `security.py`)**:
    *   **Mechanism:** Uses `flask-limiter` to restrict login attempts (e.g., 5 per minute). Additionally, tracks failed attempts in the database; after 5 failures, the account is locked for 15 minutes.

## 🛡️ 2. Input Validation & Attack Prevention

*   **SQL Injection (SQLi) Prevention (`movies.py`, `auth.py`)**:
    *   **Mechanism:** Exclusively uses SQLAlchemy ORM for all database interactions. The ORM automatically parameterizes queries, neutralizing SQL injection attempts.
    *   **Demo:** A specific endpoint `/demo/sqli-safe` demonstrates how the ORM safely handles input that would typically trigger an injection.
    *   **Lab Connection:** Directly addresses vulnerabilities explored in the **DVWA SQLi Textbox** lab.
*   **Cross-Site Scripting (XSS) Prevention (`templates/`, `movies.py`)**:
    *   **Mechanism:** Jinja2 templates automatically escape all `{{ variable }}` outputs. Explicit server-side escaping is also used via `markupsafe.escape` when handling user input before passing it to the database or AI prompt. A strict Content Security Policy (CSP) is also enforced.
    *   **Lab Connection:** Mitigates vulnerabilities seen in the **DVWA XSS** lab.
*   **Cross-Site Request Forgery (CSRF) Prevention (`security.py`, `templates/`)**:
    *   **Mechanism:** `flask-wtf` with global CSRF protection is enabled. All forms include a hidden CSRF token (`{{ form.hidden_tag() }}`), which is validated on submission.
    *   **Lab Connection:** Prevents attacks practiced in the **DVWA CSRF** and **Burp Suite** labs.

## 🔒 3. Data Protection

*   **HTTPS / TLS (`app.py`, `generate_cert.py`)**:
    *   **Mechanism:** The application is configured to run with an SSL context. 
    *   **Lab Connection:** Relates to the **OpenSSL Assignments** lab. You can generate a self-signed certificate using:
        `openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes`
*   **Sensitive Data Encryption (`auth.py`)**:
    *   **Mechanism:** Uses the `cryptography` library (Fernet symmetric encryption) to encrypt Personally Identifiable Information (PII), such as phone numbers, before storing them in the database.
*   **Data Integrity / Signing (`bookings.py`)**:
    *   **Mechanism:** Booking confirmation tokens are generated as HMAC-signed values using the app's secret key. This ensures the token hasn't been tampered with.
*   **Security Headers (`security.py`)**:
    *   **Mechanism:** An `@app.after_request` hook injects critical security headers:
        *   `X-Content-Type-Options: nosniff`
        *   `X-Frame-Options: DENY`
        *   `Strict-Transport-Security: max-age=31536000; includeSubDomains`
        *   `Referrer-Policy: strict-origin-when-cross-origin`
        *   `Content-Security-Policy`
*   **Environment Variables (`.env`, `app.py`)**:
    *   **Mechanism:** Uses `python-dotenv` to load secrets (database URL, API keys, Flask secret key) from a `.env` file, ensuring they are never hardcoded in the source code.

## 🤖 Gemini Pro Integration

*   **Chatbot (`gemini.py`, `movies.py`, `chatbot.html`)**:
    *   Integrates the Google Gemini API to provide an intelligent movie recommendation chatbot.
    *   **Security:** User input is strictly sanitized (`escape()`) before being incorporated into the prompt to prevent prompt injection. The output is safely rendered in the frontend to prevent XSS.

---

## 🎥 5-Minute Presentation Outline

1.  **0:00–0:30 | Intro:** "Welcome to CineVault, a secure movie booking platform built with Flask. Today, I'll demonstrate how we've hardened this application against common web vulnerabilities."
2.  **0:30–1:30 | Authentication:** "We use bcrypt for password hashing, mitigating the risks we saw in the John the Ripper lab. We also have Role-Based Access Control (RBAC)—I'll demonstrate how regular users cannot access the `/admin` dashboard."
3.  **1:30–2:30 | Input Validation:** "Unlike the vulnerable DVWA, we use an ORM to prevent SQL Injection. Our templates automatically escape output to prevent XSS, and every state-changing request requires a CSRF token."
4.  **2:30–3:30 | Data Protection:** "Data in transit is protected by HTTPS using OpenSSL certificates. Sensitive data at rest, like phone numbers, is symmetrically encrypted using Fernet."
5.  **3:30–4:30 | Live Demo:** *Show intercepting a request in Burp Suite to highlight the CSRF token. Trigger the rate limiter by failing login multiple times.*
6.  **4:30–5:00 | Gemini Demo & Wrap-up:** *Show the secure implementation of the AI chatbot providing recommendations.*
