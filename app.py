# main api starter
from flask import Flask, request, jsonify, render_template, session, redirect
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import json
from datetime import date
from database import (init_db, get_message_count, increment_message_count,
                      save_message, get_history, save_integration, get_integration)

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv(
    'SECRET_KEY', 
    'secret123')
CORS(app)

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"
FREE_LIMIT = 100

init_db()

# ── Pages ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_email' in session:
        return redirect('/chat')
    return render_template('index.html')

@app.route('/chat')
def chat_page():
    if 'user_email' not in session:
        return redirect('/')
    return render_template('chat.html', user=session.get('user_name'))

@app.route('/settings')
def settings_page():
    if 'user_email' not in session:
        return redirect('/')
    return render_template('settings.html', user=session.get('user_name'))

# ── Auth ───────────────────────────────────────────────────────────────────

@app.route('/api/google-login', methods=['POST'])
def google_login():
    data = request.json
    session['user_email'] = data.get('email')
    session['user_name'] = data.get('name')
    return jsonify({"success": True})

@app.route('/api/logout')
def logout():
    session.clear()
    return redirect('/')

# ── Chat ───────────────────────────────────────────────────────────────────

@app.route('/api/chat', methods=['POST'])
def chat():
    if 'user_email' not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_email = session['user_email']
    today = str(date.today())
    count = get_message_count(user_email, today)

    if count >= FREE_LIMIT:
        return jsonify({
            "error": "limit_reached",
            "message": "You've used all 100 free messages today. Upgrade to Premium for unlimited access!",
            "premium_info": {
                "price": "$9.99/month",
                "features": ["Unlimited messages", "Priority support", "Advanced models"]
            }
        }), 403

    user_message = request.json.get('message', '')
    history = get_history(user_email)
    history.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ] + history,
        "max_tokens": 1024
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload)
    result = response.json()

    ai_reply = result['choices'][0]['message']['content']

    save_message(user_email, "user", user_message)
    save_message(user_email, "assistant", ai_reply)
    increment_message_count(user_email, today)

    remaining = FREE_LIMIT - (count + 1)
    return jsonify({
        "reply": ai_reply,
        "messages_used": count + 1,
        "messages_remaining": remaining
    })

@app.route('/api/message-count')
def message_count():
    if 'user_email' not in session:
        return jsonify({"count": 0})
    today = str(date.today())
    count = get_message_count(session['user_email'], today)
    return jsonify({"count": count, "limit": FREE_LIMIT, "remaining": FREE_LIMIT - count})

# ── Settings ───────────────────────────────────────────────────────────────

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    if 'user_email' not in session:
        return jsonify({"error": "Not logged in"}), 401
    if request.method == 'POST':
        save_integration(session['user_email'], request.json)
        return jsonify({"success": True})
    return jsonify(get_integration(session['user_email']))

if __name__ == '__main__':
    app.run(host='localhost', debug=True)