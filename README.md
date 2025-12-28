# arXiv Paper Classifier
**AI-Powered Research Paper Categorization Platform**

---

## Overview
**arXiv Paper Classifier** is a full-stack web application that automatically classifies research papers into academic domains using machine learning. Users submit a paper’s **title and abstract**, and the system predicts the most relevant research category with confidence scores.

The project integrates **modern frontend design**, **secure authentication**, **admin management**, and a **CatBoost-based machine learning model** into a single end-to-end system.

---

## Key Features

### Authentication & Security
- User signup and login
- Email verification for account activation
- Secure password hashing
- Role-based access (User / Admin)

### Machine Learning Classification
- CatBoost-based text classifier
- TF-IDF and domain-specific keyword features
- Confidence scores and top-5 predictions

### User Dashboard
- Submit paper title and abstract
- View predicted category with explanation
- Track past classification history

### Admin Panel
- View all registered users
- Monitor user activity and classifications
- Delete users securely (admin-only access)

---

## Supported Research Domains
- AI and Machine Learning
- Physics
- Mathematics
- Biology and Health
- Chemistry and Materials

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


---

## How to Run

### 1. Clone the repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```
 2. Install dependencies
---bash
pip install -r requirements.txt
```
3. Run the application
---bash
python app.py
```

4. Open in browser
---bash

## Default Admin Access

