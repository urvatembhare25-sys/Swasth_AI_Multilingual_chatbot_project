# Swasth_AI_Multilingual_chatbot_project
A multilingual medical chatbot for public health awareness built as a college minor project.

# 💬 Medical Health Chatbot
A medical health chatbot that provides basic health-related information, symptom checks, and guidance.  
Includes a **user login & registration system**, interactive chatbot UI, and dataset integration.

---

## 🚀 Features
- 🔐 User Login & Registration  
- 🧠 AI-based Health Chatbot  
- 🌐 Interactive and Responsive UI  
- 📊 Uses dataset (Kaggle/WHO) for training & responses  
- 🩺 Provides symptom-based suggestions  
- 💬 Multilingual support (English/Hindi/etc.)  
- 📁 Clean folder structure for easy development  

---

## 🛠️ Tech Stack
- **Frontend:** HTML5, CSS3, JavaScript  
- **Backend:** Python (Flask framework)
- **Database:** SQLite (via SQLAlchemy ORM) 
- **AI Model:** Googletrans (Multilingual Translation API)
- **Dataset:** WHO or Kaggle Health Dataset  

---

## 📂 Project Structure

├── app.py              # Main Flask application
├── models.py           # Database models (User, ChatHistory)
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html      # Main chat interface
│   ├── login.html      # Authentication page
│   └── profile.html    # User profile page
├── static/
│   ├── css/style.css   # Styling
│   └── js/script.js    # Frontend logic
├── data/
│   └── health_data.json # Health knowledge base
└── instance/
    └── swasth_ai.db    # SQLite database
