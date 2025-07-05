from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
import requests
import os
import urllib3
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Отключаем предупреждения о небезопасных SSL запросах
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Конфиг серверов
OUTLINE_SERVERS = {
    "USA": {
        "api_url": "https://80.209.242.200:10467/mrK1gt5EE2Co18a13bAAtQ",
        "token": "e5d439f5-a184-4ef6-8fc8-d4e8dea63d0c"
    },
    "Germany": {
        "api_url": "https://80.209.242.200:10467/mrK1gt5EE2Co18a13bAAtQ",
        "token": "e5d439f5-a184-4ef6-8fc8-d4e8dea63d0c"
    },
}

DB_PATH = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT,
            created_at TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            outline_key TEXT,
            country TEXT,
            issued_at TEXT,
            expires_at TEXT,
            is_free INTEGER
        )''')
        conn.commit()

def get_telegram_id():
    return session.get('telegram_id', 'test_user')

def render_page(content, title="VPN Mini App", **kwargs):
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{{ title }}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            html, body { height: 100%; min-height: 100%; }
            body { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            .container { 
                max-width: 600px; 
                margin-top: 20px; 
                padding: 0 15px;
            }
            .glass-card {
                background: rgba(255, 255, 255, 0.25);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 20px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                overflow: hidden;
            }
            .glass-card-small {
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(15px);
                -webkit-backdrop-filter: blur(15px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.2);
            }
            .ios-button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                border-radius: 12px;
                color: white;
                font-weight: 600;
                padding: 12px 24px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                width: 170px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
                text-decoration: none;
            }
            .ios-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
                color: white;
            }
            .ios-button-outline {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 12px;
                color: white;
                font-weight: 600;
                padding: 12px 24px;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                width: 170px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
                text-decoration: none;
            }
            .ios-button-outline:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-1px);
                color: white;
            }
            .outline-key { 
                word-break: break-all; 
                font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 12px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .text-white { color: white !important; }
            .text-white-80 { color: rgba(255, 255, 255, 0.8) !important; }
            .text-white-60 { color: rgba(255, 255, 255, 0.6) !important; }
            .icon-container {
                width: 48px;
                height: 48px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                backdrop-filter: blur(10px);
            }
            .card-icon {
                width: 32px;
                height: 32px;
                background: rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                backdrop-filter: blur(5px);
            }
            .page-header {
                font-size: 24px;
                font-weight: 700;
            }
            .card-title {
                font-size: 18px;
                font-weight: 600;
            }
            .card-text {
                font-size: 14px;
            }
            .back-button {
                position: absolute;
                top: -3px;
                left: 15px;
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                backdrop-filter: blur(10px);
                color: white;
                text-decoration: none;
            }
            .back-button:hover {
                background: rgba(255, 255, 255, 0.3);
                color: white;
            }
        </style>
        <script>
            if (window.Telegram && window.Telegram.WebApp) {
                Telegram.WebApp.expand();
            }
        </script>
    </head>
    <body>
    <div class="container">
        {{ content|safe }}
    </div>
    </body>
    </html>
    ''', content=render_template_string(content, **kwargs), title=title, **kwargs)

@app.route('/', methods=['GET', 'POST'])
def index():
    telegram_id = get_telegram_id()
    user_name = 'Иван Иванов'
    user_avatar = 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png'
    wallet_connected = False
    lang = 'ru'
    content = '''
    <!-- Блок приветствия -->
    <div class="glass-card p-4 mb-4">
      <div class="d-flex align-items-center justify-content-between">
        <div class="d-flex align-items-center">
          <img src="{{ user_avatar }}" alt="avatar" width="56" height="56" class="rounded-circle me-3 border border-white border-2">
          <div>
            <div class="fw-bold text-white card-title">Здравствуйте, {{ user_name }}</div>
            <div class="text-white-60 card-text">@{{ telegram_id }}</div>
            <div class="mt-1"><span class="text-white-80 card-text">Посетите ваш личный кабинет</span></div>
          </div>
        </div>
        <a href="{{ url_for('my_keys') }}" class="btn ios-button">Перейти &gt;</a>
      </div>
    </div>

    <!-- Блок выбрать сервер -->
    <div class="glass-card p-4 mb-3">
      <div class="d-flex align-items-center justify-content-between">
        <div class="d-flex align-items-center">
          <div class="icon-container me-3">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="white" class="bi bi-shield-lock" viewBox="0 0 16 16">
              <path d="M5.5 9a1.5 1.5 0 1 1 3 0v1a.5.5 0 0 1-1 0v-1a.5.5 0 0 0-1 0v1a.5.5 0 0 1-1 0V9z"/>
              <path d="M8 0c-.69 0-1.342.13-1.972.38C3.12 1.07 1.5 2.522 1.5 4.5c0 5.25 5.5 7.5 5.5 7.5s5.5-2.25 5.5-7.5c0-1.978-1.62-3.43-4.528-4.12A5.978 5.978 0 0 0 8 0zm0 1c.638 0 1.25.12 1.82.34C12.12 2.07 13.5 3.522 13.5 5.5c0 4.5-4.5 6.5-4.5 6.5S3.5 10 3.5 5.5c0-1.978 1.38-3.43 3.68-4.16A5.978 5.978 0 0 1 8 1z"/>
            </svg>
          </div>
          <div class="fw-bold text-white card-title">Выбрать сервер</div>
        </div>
        <a href="{{ url_for('catalog') }}" class="btn ios-button">Выбрать</a>
      </div>
    </div>

    <!-- Две карточки -->
    <div class="row g-3 mb-3">
      <div class="col-6">
        <div class="glass-card p-3 h-100 d-flex align-items-center">
          <div class="card-icon me-3">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="white" class="bi bi-translate" viewBox="0 0 16 16">
              <path d="M4.5 1a.5.5 0 0 1 .5.5V2h6v-.5a.5.5 0 0 1 1 0V2h.5A1.5 1.5 0 0 1 14 3.5v9A1.5 1.5 0 0 1 12.5 14h-9A1.5 1.5 0 0 1 2 12.5v-9A1.5 1.5 0 0 1 3.5 2H4V1.5a.5.5 0 0 1 .5-.5zM3.5 3A.5.5 0 0 0 3 3.5v9a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5v-9a.5.5 0 0 0-.5-.5h-9z"/>
              <path d="M6.5 7.5a.5.5 0 0 1 .5.5v.5h2v-.5a.5.5 0 0 1 1 0v.5h.5a.5.5 0 0 1 0 1H10v.5a.5.5 0 0 1-1 0v-.5H7v.5a.5.5 0 0 1-1 0v-.5h-.5a.5.5 0 0 1 0-1H6v-.5a.5.5 0 0 1 .5-.5z"/>
            </svg>
          </div>
          <div>
            <div class="fw-bold text-white card-title">Язык</div>
            <div class="fs-5 text-white-80 card-text">{{ lang|upper }}</div>
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="glass-card p-3 h-100 d-flex align-items-center">
          <div class="card-icon me-3">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="white" class="bi bi-wallet2" viewBox="0 0 16 16">
              <path d="M12 5H2.5A1.5 1.5 0 0 0 1 6.5v5A1.5 1.5 0 0 0 2.5 13h11A1.5 1.5 0 0 0 15 11.5v-5A1.5 1.5 0 0 0 13.5 5H13V4a2 2 0 0 0-2-2H3.5A1.5 1.5 0 0 0 2 3.5V5h10V4a1 1 0 0 1 1-1h.5A.5.5 0 0 1 14 3.5V5h-2z"/>
            </svg>
          </div>
          <div>
            <div class="fw-bold text-white card-title">Кошелек</div>
            <div class="fs-6 text-white-60 card-text">{{ 'Подключен' if wallet_connected else 'Не подключен' }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- FAQ -->
    <div class="glass-card p-4 mb-3">
      <div class="d-flex align-items-center justify-content-between">
        <div class="d-flex align-items-center">
          <div class="icon-container me-3">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="white" class="bi bi-question-circle" viewBox="0 0 16 16">
              <path d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm0 1A8 8 0 1 1 8 0a8 8 0 0 1 0 16z"/>
              <path d="M5.255 5.786a.237.237 0 0 0 .241.247h.825c.138 0 .247-.113.247-.25 0-.563.448-.986 1.07-.986.622 0 1.07.423 1.07.986 0 .364-.165.614-.547.927-.276.22-.447.375-.447.813v.07c0 .138.11.25.247.25h.819a.25.25 0 0 0 .25-.25v-.057c0-.451.18-.684.571-.987.288-.23.429-.445.429-.813 0-.98-.832-1.786-2-1.786-1.168 0-2 .806-2 1.786z"/>
              <circle cx="8" cy="12" r=".5"/>
            </svg>
          </div>
          <div class="fw-bold text-white card-title">Часто задаваемые вопросы</div>
        </div>
        <a href="#faq" class="btn ios-button">Перейти</a>
      </div>
    </div>

    <!-- Поддержка -->
    <div class="glass-card p-4 mb-3">
      <div class="d-flex align-items-center justify-content-between">
        <div class="d-flex align-items-center">
          <div class="icon-container me-3">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="white" class="bi bi-shield-check" viewBox="0 0 16 16">
              <path d="M5.072 1.2a1.5 1.5 0 0 1 1.856 0l5.5 4.4A1.5 1.5 0 0 1 13 6.5v5A1.5 1.5 0 0 1 11.5 13h-7A1.5 1.5 0 0 1 3 11.5v-5A1.5 1.5 0 0 1 3.572 5.6l5.5-4.4z"/>
              <path d="M10.854 7.146a.5.5 0 0 0-.708 0L7.5 9.793 6.354 8.646a.5.5 0 1 0-.708.708l1.5 1.5a.5.5 0 0 0 .708 0l2.5-2.5a.5.5 0 0 0 0-.708z"/>
            </svg>
          </div>
          <div>
            <div class="fw-bold text-white card-title">Поддержка</div>
            <div class="text-white-60 card-text">Мы всегда готовы помочь вам</div>
          </div>
        </div>
        <a href="#support" class="ios-button">В поддержку &gt;</a>
      </div>
    </div>
    '''
    return render_page(content, title="Главная", lang=lang, wallet_connected=wallet_connected, user_name=user_name, user_avatar=user_avatar, telegram_id=telegram_id)

@app.route('/catalog')
def catalog():
    countries = [
        {
            'code': 'USA',
            'name': 'США',
            'flag': 'https://flagcdn.com/us.svg'
        },
        {
            'code': 'Germany',
            'name': 'Германия',
            'flag': 'https://flagcdn.com/de.svg'
        }
    ]
    content = '''
    <div style="position: relative;">
        <div class="d-flex flex-row justify-content-center align-items-center w-100 mb-3">
            <a href="{{ url_for('index') }}" class="btn back-button">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-arrow-left" viewBox="0 0 16 16">
                  <path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"/>
              </svg>
            </a>
          <h3 class="page-header text-white text-center">Выберите сервер</h3>
        </div>
        
        <div class="row g-4">
        {% for c in countries %}
          <div class="col-6">
            <div class="glass-card padding-2 text-center h-100" style="border-radius:18px;">
              <div class="card-body d-flex flex-column align-items-center justify-content-between">
                <img src="{{c.flag}}" alt="flag" style="width:100%;height:140px;object-fit:cover;" class="mb-2">
                <div class="fw-bold fs-5 mb-2 text-white card-title">{{c.name}}</div>
                <a href="{{ url_for('get_key', country=c.code) }}" class="ios-button btn mb-3">Получить ключ</a>
              </div>
            </div>
          </div>
        {% endfor %}
        </div>
    </div>
    '''
    return render_page(content, title="Выбор сервера", countries=countries)

@app.route('/get_key')
def get_key():
    telegram_id = get_telegram_id()
    country = request.args.get('country')
    if not country or country not in OUTLINE_SERVERS:
        return render_page('<div class="alert alert-danger">Страна не найдена</div>', title="Ошибка")
    
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE telegram_id=?', (telegram_id,))
        row = c.fetchone()
        if row:
            user_id = row[0]
        else:
            c.execute('INSERT INTO users (telegram_id, created_at) VALUES (?, ?)', (telegram_id, datetime.utcnow().isoformat()))
            user_id = c.lastrowid
            conn.commit()
        
        server = OUTLINE_SERVERS[country]
        try:
            r = requests.post(f"{server['api_url']}/access-keys", 
                            headers={"Authorization": f"Bearer {server['token']}"}, 
                            timeout=10, 
                            verify=False)  # Отключаем проверку SSL
            r.raise_for_status()
            key_data = r.json()
            outline_key = key_data.get('accessUrl')
            if not outline_key:
                return render_page('<div class="alert alert-danger">Не удалось получить ключ от сервера</div>', title="Ошибка")
        except requests.exceptions.RequestException as e:
            return render_page(f'<div class="alert alert-danger">Ошибка подключения к серверу: {e}</div>', title="Ошибка")
        except Exception as e:
            return render_page(f'<div class="alert alert-danger">Ошибка при получении ключа: {e}</div>', title="Ошибка")
        
        issued_at = datetime.utcnow()
        expires_at = issued_at + timedelta(days=3)
        c.execute('INSERT INTO keys (user_id, outline_key, country, issued_at, expires_at, is_free) VALUES (?, ?, ?, ?, ?, ?)',
                  (user_id, outline_key, country, issued_at.isoformat(), expires_at.isoformat(), 1))
        conn.commit()
    
    content = f'''
        <div class="glass-card p-4 mb-4">
            <h3 class="mb-3 text-white text-center">✅ Ключ успешно создан!</h3>
            <div class="text-center mb-3">
                <div class="badge bg-success fs-6 mb-2">Страна: {country}</div>
                <div class="badge bg-info fs-6 mb-2">Бесплатно до: {expires_at.strftime('%d.%m.%Y %H:%M')}</div>
            </div>
            <div class="outline-key text-white mb-4 text-center">
                <small class="text-white-60 d-block mb-2">Ваш Outline ключ:</small>
                <code class="fs-6">{outline_key}</code>
            </div>
            <div class="d-flex flex-column gap-2">
                <a class="ios-button" href="{{ url_for('my_keys') }}">Мои ключи</a>
                <a class="ios-button-outline" href="{{ url_for('index') }}">На главную</a>
            </div>
        </div>
    '''
    return render_page(content, title="Ваш ключ")

@app.route('/my_keys')
def my_keys():
    telegram_id = get_telegram_id()
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE telegram_id=?', (telegram_id,))
        row = c.fetchone()
        if not row:
            return render_page('<div class="alert alert-info text-white">У вас пока нет ключей.</div>', title="Мои ключи")
        user_id = row[0]
        c.execute('SELECT outline_key, country, issued_at, expires_at, is_free FROM keys WHERE user_id=?', (user_id,))
        keys = c.fetchall()
    
    content = '''
        <h3 class="mb-4 text-white">Мои ключи</h3>
        <div class="table-responsive">
        <table class="table table-bordered align-middle text-white">
            <thead class="glass-card-small">
            <tr><th class="text-white">Страна</th><th class="text-white">Ключ</th><th class="text-white">Выдан</th><th class="text-white">Действует до</th><th class="text-white">Бесплатно?</th></tr>
            </thead>
            <tbody>
            {% for k in keys %}
            <tr class="glass-card-small">
                <td class="text-white">{{k[1]}}</td>
                <td class="outline-key" style="max-width:200px;">{{k[0]}}</td>
                <td class="text-white">{{k[2][:16]}}</td>
                <td class="text-white">{{k[3][:16]}}</td>
                <td>{% if k[4] %}<span class="badge bg-success">Да</span>{% else %}<span class="badge bg-secondary">Нет</span>{% endif %}</td>
            </tr>
            {% endfor %}
            </tbody>
        </table>
        </div>
        <a class="ios-button-outline w-100 text-decoration-none" href="{{ url_for('index') }}">Назад</a>
    '''
    return render_page(content, title="Мои ключи", keys=keys)

if __name__ == '__main__':
    import sys
    init_db()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 