# Academic-Abstract-Classifier  
### AI-Powered Research Paper Categorization Platform

## Overview
Academic-Abstract-Classifier is a full-stack web application that automatically classifies academic research papers into relevant domains using machine learning. Users submit a paper’s title and abstract, and the system predicts the most appropriate research category along with confidence scores.

The platform integrates a modern frontend, secure authentication, admin management, and a CatBoost-based text classification model into a complete end-to-end system.

---

## Key Features

### 🔐 Authentication & Security
- User signup and login
- Email verification for account activation
- Secure password hashing
- Role-based access control (User / Admin)

### 🤖 Machine Learning Classification
- CatBoost-based text classifier
- TF-IDF and domain-specific keyword features
- Top-5 category predictions with confidence scores

### 📊 User Dashboard
- Submit paper title and abstract
- View predicted category with explanation
- Track past classification history

### 🛠️ Admin Panel
- View all registered users
- Monitor user activity and classification logs
- Secure user deletion (admin-only access)

---

## Supported Research Domains
- Artificial Intelligence & Machine Learning  
- Physics  
- Mathematics  
- Biology & Health Sciences  
- Chemistry & Materials Science  

---

## Technology Stack

### Frontend
- HTML  
- CSS  
- JavaScript  

### Backend
- Python  
- Flask  
- Flask-SQLAlchemy  
- Flask-Mail  

### Machine Learning
- CatBoost  
- Scikit-learn  
- TF-IDF Vectorization  
- NumPy, SciPy  

### Database
- SQLite  

---

## Project Structure

├── app.py
├── requirements.txt
├── README.md
├── templates/
│ ├── home.html
│ ├── about.html
│ ├── aboutus.html
│ ├── login.html
│ ├── signup.html
│ ├── classifier.html
│ ├── admin.html
├── vectorizer.pkl
├── keywords.pkl
├── catboost_hybrid.cbm

## How to Run

```bash
git clone https://github.com/your-username/Academic-Abstract-Classifier.git
cd Academic-Abstract-Classifier
```bash
pip install -r requirements.txt
```

python app.py

Install dependencies
pip install -r requirements.txt

Run the application
python app.py

Open in browser

👉 http://127.0.0.1:5000
