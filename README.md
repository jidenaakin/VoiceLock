
# VoiceLock 🔐

VoiceLock is a Python-based voice authentication system that uses speaker recognition to verify a user's identity.

Users create an account with a username and password, register their voice, and authenticate using both credentials.

## Features

- User registration and login
- Voice enrollment using a microphone
- Speaker verification using a pretrained WeSpeaker ResNet34 model
- Password hashing
- Voice-based password recovery
- Password reset
- Protected user dashboard
- SQLite database

## Technologies Used

- Python
- Flask
- SQLite
- HTML and CSS
- JavaScript
- SpeakerONNX
- ONNX Runtime
- WeSpeaker ResNet34

## How It Works

1. A user creates an account.
2. The user records a voice sample.
3. VoiceLock stores the voice recording linked to the account.
4. During login, the user enters their username and password.
5. The user records their voice again.
6. The system compares the new recording with the registered voice.
7. Access is granted if the similarity score meets the configured threshold.

## Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Simplevoiceauth
```

### 2. Create a virtual environment

```bash
py -3.14 -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python app.py
```

### 6. Open in your browser

```text
http://127.0.0.1:5000
```

## Important Notes

- A working microphone is required.
- VoiceLock is an educational prototype developed for learning and demonstration.
- Speaker similarity thresholds require further testing and calibration.
- Voice recognition alone does not guarantee protection against recorded-voice replay or other spoofing attacks.
- Do not use this prototype to protect real sensitive accounts or information.

## Author

Developed as a Cybersecurity academic project.
