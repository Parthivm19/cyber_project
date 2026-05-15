# 🎬 CineVault

A secure movie booking web application built with Flask, designed to demonstrate comprehensive web security countermeasures.

## 🚀 Setup Instructions for Teammates

Follow these steps to get the project running locally on your machine.

### 1. Clone the repository
```bash
git clone <your-repository-url>
cd cinevault
```

### 2. Create and Activate a Virtual Environment
It is highly recommended to use a virtual environment to avoid dependency conflicts.

**On Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
You must set up your local environment variables. **Never commit the `.env` file to Git.**

1. Copy the example file to create your own `.env` file:
   **Windows:** `copy .env.example .env`
   **macOS/Linux:** `cp .env.example .env`
2. Open the newly created `.env` file and add your `GEMINI_API_KEY`. (You can leave `ENCRYPTION_KEY` blank, the app will auto-generate one if needed).

### 5. Generate SSL Certificates (Required for HTTPS)
Because this app enforces HTTPS for security, you need a local SSL certificate.

Run the provided Python script to automatically generate self-signed certificates (`cert.pem` and `key.pem`):
```bash
python generate_cert.py
```

### 6. Run the Application
Start the Flask development server:
```bash
python app.py
```

### 7. Access the App
Open your browser and navigate to exactly:
👉 **https://127.0.0.1:5000** 

*(Note: Because we are using a self-signed certificate, your browser will show a "Your connection is not private" warning. Click **Advanced** -> **Proceed to 127.0.0.1 (unsafe)** to view the site).*

---

## 🔒 Security Features Implemented
For a detailed breakdown of the security countermeasures (RBAC, SQLi prevention, XSS prevention, CSRF tokens, etc.), please see the [README_SECURITY.md](README_SECURITY.md) file.
