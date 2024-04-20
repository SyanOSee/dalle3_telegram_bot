# Dalle3 Telegram Bot

Телеграм бот для генерации различных изображений с помощью Dalle2 и Dalle3

## Установка

1. Создать файл `.env` со следующим содержанием:
   ```plaintext
   # Bot token
   BOT_TOKEN="YOUR BOT TOKEN"

   # Openai token
   OPENAI_API_KEY="YOUR API TOKEN"

   # Database info
   #DATABASE_HOST="dalle3_postgres" # For docker running
   #DATABASE_HOST="localhost" # For local running
   DATABASE_PORT=5432
   DATABASE_USER="postgres"
   DATABASE_PASSWORD="password"

   # Admin panel
   #PANEL_HOST="localhost" # for local using or insert IP of server
   PANEL_PORT=8081
   SECRET_KEY="YOUR secret key"
   ```

2. Перейти в папку проекта. Запустить команду в терминале `docker compose up --build`.

3. Открыть админ панель по ссылке `localhost:8081/admin` или `<server_id>:8081/admin`.

4. Перейти в чат бота
