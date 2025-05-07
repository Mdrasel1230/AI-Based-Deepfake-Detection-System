
# AI-Based Deepfake Detection System

## 🔍 Overview

The AI-Based Deepfake Detection System is a Flask-powered web application designed to detect deepfake images and videos. Leveraging a modular architecture, the system integrates machine learning models to analyze uploaded media files and determine their authenticity. The application offers a user-friendly interface for uploading files, viewing detection results, and managing user sessions.

## Features

- **User Authentication**: Secure login and registration system for users and administrators.
- **Media Upload**: Supports uploading of images and videos for analysis.
- **Deepfake Detection**: Processes uploaded media to detect potential deepfakes using integrated ML models.
- **Admin Panel**: Administrative interface to manage users, view logs, and monitor system activity.
- **Responsive Design**: Frontend built with HTML, CSS, and JavaScript for seamless user experience.

## Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (via SQLAlchemy ORM)
- **Machine Learning**: OpenCV, NumPy
- **Authentication**: Flask-Login
- **Form Handling**: Flask-WTF

## Project Structure

```
AI-Based-Deepfake-Detection-System/
├── app.py
├── create_admin.py
├── deepfake_detector.py
├── forms.py
├── models.py
├── routes.py
├── utils.py
├── requirements.txt
├── instance/
│   └── deepfake_detection.db
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   └── dashboard.html
└── uploads/
```

## ⚙️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Mdrasel1230/AI-Based-Deepfake-Detection-System.git
   cd AI-Based-Deepfake-Detection-System
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**:
   ```bash
   flask db init
   flask db migrate -m "Initial migration."
   flask db upgrade
   ```

5. **Create an admin user**:
   ```bash
   python create_admin.py
   ```

6. **Run the application**:
   ```bash
   flask run
   ```

   The application will be accessible at `http://127.0.0.1:5000/`.

## 🧪 Usage

1. **Register/Login**: Create a new account or log in using existing credentials.
2. **Upload Media**: Navigate to the upload section and select an image or video file.
3. **Analyze**: Submit the file for analysis. The system will process the media and display the detection results.
4. **Admin Panel**: If logged in as an admin, access the admin panel to manage users and view system logs.

## 📌 Notes

- Ensure that the `uploads/` directory has appropriate read/write permissions.
- The current ML model in `deepfake_detector.py` is a placeholder. For production use, integrate a robust deepfake detection model.
- Update the `SECRET_KEY` in `app.py` for enhanced security.
