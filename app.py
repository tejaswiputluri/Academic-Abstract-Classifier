# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from catboost import CatBoostClassifier
import joblib
import numpy as np
import re
from scipy.sparse import hstack, csr_matrix
from datetime import datetime
import secrets
import os
from functools import wraps

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///arxiv_classifier.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'seetharamakartheekchallapalli@gmail.com'  # Change this
app.config['MAIL_PASSWORD'] = 'tjkq hnxn lxcj kmsk'      # Change this
app.config['MAIL_DEFAULT_SENDER'] = 'seetharamakartheekchallapalli@gmail.com'

db = SQLAlchemy(app)
mail = Mail(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    classifications = db.relationship('Classification', backref='user', lazy=True)

class Classification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.Text, nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    predicted_category = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Load ML model
print("Loading model + vectorizer + keywords...")
try:
    model = CatBoostClassifier()
    model.load_model('catboost_hybrid.cbm')
    vectorizer = joblib.load('vectorizer.pkl')
    DOMAIN_KEYWORDS = joblib.load('keywords.pkl')
    print("All files loaded successfully!")
except Exception as e:
    print(f"Load error: {e}")
    model = vectorizer = DOMAIN_KEYWORDS = None

CATEGORY_INFO = {
    'AI_ML': {
        'name': 'AI & Machine Learning',
        'icon': '🤖',
        'color': '#667eea',
        'description': 'Research in artificial intelligence, machine learning, and related computational methods.'
    },
    'Physics': {
        'name': 'Physics',
        'icon': '⚛️',
        'color': '#f093fb',
        'description': 'Studies in theoretical, experimental, and applied physics.'
    },
    'Mathematics': {
        'name': 'Mathematics',
        'icon': '📐',
        'color': '#4facfe',
        'description': 'Research in pure and applied mathematics, including analysis, algebra, and geometry.'
    },
    'Biology_Health': {
        'name': 'Biology & Health',
        'icon': '🧬',
        'color': '#fa709a',
        'description': 'Research in biological sciences, health, and medicine.'
    },
    'Chemistry_Mat': {
        'name': 'Chemistry & Materials',
        'icon': '🧪',
        'color': '#43e97b',
        'description': 'Studies in chemistry, materials science, and related fields.'
    }
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def clean_text(text):
    text = (text or "").lower()
    text = re.sub(r'\$[^\$]+\$', ' ', text)
    text = re.sub(r'\\[a-zA-Z]+', ' ', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def send_verification_email(user):
    token = secrets.token_urlsafe(32)
    user.verification_token = token
    db.session.commit()
    
    verify_url = url_for('verify_email', token=token, _external=True)
    
    msg = Message('Verify Your Email - arXiv Classifier',
                  recipients=[user.email])
    msg.body = f'''Hello {user.username},

Thank you for registering with arXiv Paper Classifier!

Please click the link below to verify your email address:
{verify_url}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
arXiv Classifier Team
'''
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('signup'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        if send_verification_email(user):
            flash('Registration successful! Please check your email to verify your account.', 'success')
        else:
            flash('Registration successful! However, verification email could not be sent.', 'warning')
        
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_verified:
                flash('Please verify your email before logging in.', 'warning')
                return redirect(url_for('login'))
            
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            # Redirect to admin panel if user is admin
            if user.is_admin:
                flash(f'Welcome back, Admin {user.username}!', 'success')
                return redirect(url_for('admin'))
            
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('classifier'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/verify/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    
    if user:
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        flash('Email verified successfully! You can now log in.', 'success')
    else:
        flash('Invalid or expired verification link.', 'danger')
    
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('home'))

@app.route('/classifier')
@login_required
def classifier():
    return render_template('classifier.html')

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    if model is None or vectorizer is None or DOMAIN_KEYWORDS is None:
        return jsonify({'error': 'Model or artifacts not loaded'}), 500

    try:
        data = request.get_json() or {}
        title = data.get('title', '')
        abstract = data.get('abstract', '')
        raw_text = (title + " " + abstract).strip()
        text = clean_text(raw_text)

        if len(text.split()) < 10:
            return jsonify({'error': 'Text too short'}), 400

        # TF-IDF
        X_tfidf = vectorizer.transform([text])

        # Keyword features
        kw_counts = []
        for label in ['AI_ML', 'Physics', 'Mathematics', 'Biology_Health', 'Chemistry_Mat']:
            count = sum(1 for word in DOMAIN_KEYWORDS.get(label, []) if word in text)
            kw_counts.append(count)
        X_keywords = csr_matrix(np.array([kw_counts]))

        # Combine features
        X_final = hstack([X_tfidf, X_keywords])
        X_final_arr = X_final.toarray()

        # Predict
        probs = model.predict_proba(X_final_arr)[0]
        pred_idx = int(np.argmax(probs))

        try:
            predicted_class = model.classes_[pred_idx]
        except Exception:
            predicted_class = model.predict(X_final_arr)[0]

        confidence = float(probs[pred_idx])

        # Save to database
        classification = Classification(
            user_id=session['user_id'],
            title=title,
            abstract=abstract,
            predicted_category=predicted_class,
            confidence=confidence
        )
        db.session.add(classification)
        db.session.commit()

        # Top-5 predictions
        top_idx = np.argsort(probs)[-5:][::-1]
        top_predictions = []
        for i in top_idx:
            c = model.classes_[i] if hasattr(model, 'classes_') else str(i)
            info = CATEGORY_INFO.get(c, {'name': c.replace('_',' & '), 'icon': '📄', 'color': '#888'})
            top_predictions.append({
                'category': c,
                'name': info['name'],
                'icon': info['icon'],
                'color': info['color'],
                'description': info.get('description', ''),
                'confidence': float(probs[i])
            })

        main = CATEGORY_INFO.get(predicted_class, {'name': predicted_class, 'icon': '🎯', 'color': '#667eea'})

        return jsonify({
            'success': True,
            'prediction': {**main, 'category': predicted_class, 'confidence': confidence},
            'top_predictions': top_predictions,
            'text_stats': {'word_count': len(text.split()), 'char_count': len(text)}
        })

    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/history')
@login_required
def get_history():
    classifications = Classification.query.filter_by(user_id=session['user_id'])\
                                          .order_by(Classification.timestamp.desc())\
                                          .all()
    
    history = []
    for c in classifications:
        info = CATEGORY_INFO.get(c.predicted_category, {})
        history.append({
            'id': c.id,
            'title': c.title,
            'abstract': c.abstract[:150] + '...' if len(c.abstract) > 150 else c.abstract,
            'category': info.get('name', c.predicted_category),
            'icon': info.get('icon', '📄'),
            'color': info.get('color', '#888'),
            'confidence': c.confidence,
            'timestamp': c.timestamp.strftime('%Y-%m-%d %H:%M')
        })
    
    return jsonify({'history': history})

@app.route('/admin')
@admin_required
def admin():
    return render_template('admin.html')

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    user_data = []
    
    for user in users:
        classifications = Classification.query.filter_by(user_id=user.id).all()
        user_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_verified': user.is_verified,
            'is_admin': user.is_admin,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M'),
            'total_classifications': len(classifications)
        })
    
    return jsonify({'users': user_data})

@app.route('/admin/user/<int:user_id>/history')
@admin_required
def admin_user_history(user_id):
    classifications = Classification.query.filter_by(user_id=user_id)\
                                          .order_by(Classification.timestamp.desc())\
                                          .all()
    
    history = []
    for c in classifications:
        info = CATEGORY_INFO.get(c.predicted_category, {})
        history.append({
            'id': c.id,
            'title': c.title,
            'abstract': c.abstract[:150] + '...' if len(c.abstract) > 150 else c.abstract,
            'category': info.get('name', c.predicted_category),
            'icon': info.get('icon', '📄'),
            'color': info.get('color', '#888'),
            'confidence': c.confidence,
            'timestamp': c.timestamp.strftime('%Y-%m-%d %H:%M')
        })
    
    return jsonify({'history': history})

# NEW DELETE USER ROUTE - ADD THIS
@app.route('/admin/user/<int:user_id>/delete', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Admin route to delete a user"""
    # Get current admin user
    current_user_id = session.get('user_id')
    current_user = User.query.get(current_user_id)
    
    # Double-check admin status (redundant with decorator but safe)
    if not current_user or not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Prevent admin from deleting themselves
    if current_user_id == user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    try:
        # Get the user to delete
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent deleting other admins
        if user.is_admin:
            return jsonify({'error': 'Cannot delete admin users'}), 403
        
        # Delete user's classification history first (due to foreign key constraint)
        Classification.query.filter_by(user_id=user_id).delete()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'User {user.username} deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete user: {str(e)}'}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Create admin user if doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                is_verified=True,
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username='admin', password='admin123'")
    
    app.run(host="127.0.0.1", port=5000, debug=True)