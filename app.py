from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from googletrans import Translator
from models import db, User, ChatHistory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here_change_in_production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///swasth_ai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

translator = Translator()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Load Health Data
def load_health_data():
    try:
        with open('data/health_data.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return {"intents": []}

health_data = load_health_data()

# --- Routes ---
@app.route('/')
@login_required
def home():
    recent_chats = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.desc()).limit(15).all()
    return render_template('index.html', user=current_user, history=recent_chats)

@app.route('/profile')
@login_required
def profile():
    user_chats = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.desc()).limit(50).all()
    total_chats = ChatHistory.query.filter_by(user_id=current_user.id).count()
    return render_template('profile.html', user=current_user, chats=user_chats, total_chats=total_chats)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.')
            
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = User.query.filter_by(email=email).first()
    if user:
        flash('Email already exists.')
        return redirect(url_for('login'))
        
    new_user = User(
        username=username, 
        email=email, 
        password=generate_password_hash(password, method='scrypt')
    )
    db.session.add(new_user)
    db.session.commit()
    
    login_user(new_user)
    return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.json
    user_message = data.get('message')
    target_lang = data.get('language', 'en')
    
    if not user_message:
        return jsonify({'response': 'Please enter a message.'}), 400

    # 1. Translate User Message to English (if not En)
    # Note: For simple keyword matching, we rely on English keywords in our JSON.
    # In a real app, we'd detect language or use a multilingual model.
    try:
        if target_lang != 'en':
            translation = translator.translate(user_message, dest='en')
            processed_message = translation.text.lower()
        else:
            processed_message = user_message.lower()
    except Exception as e:
        print(f"Translation error: {e}")
        processed_message = user_message.lower()

    # 2. Find Intent
    response_text = "I'm not sure about that. Try asking about flu, headache, or covid."
    matched = False
    
    for intent in health_data['intents']:
        for pattern in intent['patterns']:
            if pattern in processed_message:
                response_text = intent['responses'][0]
                matched = True
                break
        if matched:
            break
            
    # 3. Translate Response back to Target Language
    try:
        if target_lang != 'en':
            final_response = translator.translate(response_text, dest=target_lang).text
        else:
            final_response = response_text
    except Exception as e:
        print(f"Response translation error: {e}")
        final_response = response_text

    # 4. Save History
    new_chat = ChatHistory(
        user_id=current_user.id,
        message=user_message,
        response=final_response,
        language=target_lang
    )
    db.session.add(new_chat)
    db.session.commit()

    return jsonify({'response': final_response})

@app.route('/delete_chat/<int:chat_id>', methods=['DELETE'])
@login_required
def delete_chat(chat_id):
    try:
        print(f"Attempting to delete chat {chat_id} for user {current_user.id}")
        chat = ChatHistory.query.get_or_404(chat_id)
        if chat.user_id != current_user.id:
            print(f"Unauthorized delete attempt by user {current_user.id} for chat {chat_id}")
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(chat)
        db.session.commit()
        print(f"Chat {chat_id} deleted successfully")
        return jsonify({'success': 'Chat deleted'})
    except Exception as e:
        print(f"Error deleting chat {chat_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username')
    email = request.form.get('email')
    
    # Simple Validation
    if not username or not email:
        flash('Username and Email are required.')
        return redirect(url_for('profile'))

    user = User.query.filter_by(email=email).first()
    if user and user.id != current_user.id:
        flash('Email already exists.')
        return redirect(url_for('profile'))
        
    current_user.username = username
    current_user.email = email
    db.session.commit()
    flash('Profile updated successfully.')
    return redirect(url_for('profile'))

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not check_password_hash(current_user.password, current_password):
        flash('Incorrect current password.')
        return redirect(url_for('profile'))
        
    if new_password != confirm_password:
        flash('New passwords do not match.')
        return redirect(url_for('profile'))
        
    current_user.password = generate_password_hash(new_password, method='scrypt')
    db.session.commit()
    flash('Password changed successfully.')
    return redirect(url_for('profile'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
