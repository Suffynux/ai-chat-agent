
# ai-chat-agent

Full-stack chat app powered by a GPT-class LLM API, Google login, daily usage limits, and integration settings for WhatsApp and e-commerce platforms.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=flat-square&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-Auth-FFCA28?style=flat-square&logo=firebase&logoColor=black)

---

## What it does

- Google OAuth login via Firebase — no passwords stored
- Chat interface connected to `llama-3.3-70b-versatile` (GroqCloud)
- Sends conversation history for multi-turn context
- 100 free messages/day per user, enforced server-side
- Saves all messages to SQLite with timestamps
- Settings page to configure WhatsApp and e-commerce API keys

---

## Stack

| Layer | Tool |
|---|---|
| Backend | Python + Flask |
| Frontend | HTML, CSS, Vanilla JS |
| Database | SQLite |
| Auth | Firebase (Google OAuth) |
| LLM API | GroqCloud |

---

## Project structure

```
ai-chat-agent/
├── app.py              # routes, API logic, session handling
├── database.py         # all SQLite queries
├── .env.example        # env variable template
└── templates/
    ├── index.html      # login page
    ├── chat.html       # chat interface
    └── settings.html   # integration settings
```

---

## Setup

```bash
git clone https://github.com/your-username/ai-chat-agent.git
cd ai-chat-agent
pip install flask flask-cors requests python-dotenv
cp .env.example .env   # add your Groq API key and secret key
python app.py
```

Then open `http://localhost:5000` and add your Firebase config to `templates/index.html`.

---

## API endpoints

| Method | Route | Description |
|---|---|---|
| `POST` | `/api/google-login` | creates Flask session after Firebase auth |
| `POST` | `/api/chat` | calls LLM, saves messages, returns reply |
| `GET` | `/api/message-count` | returns `{used, remaining}` |
| `GET/POST` | `/api/settings` | fetch or save integration config |
| `GET` | `/api/logout` | clears session |

---

## Notes

- Rate limit is enforced in Python before the API call — not just in the UI
- Conversation history (last 20 messages) is passed to the model on every request
- All integration settings (WhatsApp number, store URL, API keys) are stored per user in SQLite

---

## Author

**[Your Name]** — [GitHub](https://github.com/your-username) · [LinkedIn](https://linkedin.com/in/your-profile)