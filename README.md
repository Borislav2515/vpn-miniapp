# VPN Telegram Mini App

Современный Telegram Mini App для выдачи Outline VPN ключей с красивым iOS-стилем дизайном.

## Установка

```bash
pip install -r requirements.txt
```

## Локальный запуск

1. Создайте файл `.env` с вашими настройками:
```
BOT_TOKEN=ваш_токен_бота
WEBAPP_URL=http://localhost:5000/
```

2. Запустите мини-апп:
```bash
python app.py
```

3. Запустите бота:
```bash
python bot.py
```

## Деплой на Render

1. Загрузите код на GitHub
2. Создайте Web Service на Render
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`
5. Добавьте Environment Variables:
   - `BOT_TOKEN` = ваш токен бота
   - `WEBAPP_URL` = https://ваш-app.onrender.com/

## Функции

- ✅ Современный iOS-стиль дизайн
- ✅ Glassmorphism эффекты
- ✅ Выдача Outline ключей
- ✅ Личный кабинет пользователя
- ✅ Каталог серверов по странам
- ✅ Telegram WebApp интеграция 