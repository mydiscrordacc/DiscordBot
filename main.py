import logging
from flask import Flask, request
import requests
import os

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello, world!"


# Discord API endpoint for getting guild members
url = "https://discord.com/api/v10/guilds/{guild_id}/members"
guild_id = os.getenv("DISCORD_GUILD_ID")  # Получаем ID сервера Discord из переменной окружения

# Discord bot token for authentication
token = os.getenv("DISCORD_BOT_TOKEN")  # Получаем токен бота Discord из переменной окружения
headers = {
    "Authorization": f"Bot {token}"
}

# Создание объекта логгера для вашего приложения
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Настройка обработчика для записи в журнал
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

# Настройка формата записей в журнал
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Добавление обработчика к логгеру приложения
logger.addHandler(handler)


def get_member_id_by_name(member_name):
    # Construct the request URL
    request_url = url.replace("{guild_id}", guild_id)

    # Parameters for getting the member by name
    params = {
        "limit": 1000  # Максимальное количество участников для получения
    }

    # Send the request to Discord API to get all guild members
    response = requests.get(request_url, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        members = response.json()

        # Iterate over the members to find the member by name
        for member in members:
            if member["user"]["username"] == member_name:
                return member["user"]["id"]

    return None


@app.route("/search", methods=["POST"])
def search_player():
    player_name = request.form.get("playerName")

    # Убираем пробелы в начале и конце имени игрока
    player_name = player_name.strip()

    # Выводим данные из формы в журнал приложения
    logger.debug(f"Received playerName from form: {player_name.strip()}")

    member_id = get_member_id_by_name(player_name)

    if member_id:
        # Формируем сообщение
        message = f"Игрок {player_name} найден. <@{member_id}>"

        # Отправляем сообщение на вебхук Discord
        discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        payload = {"content": message}
        headers = {"Content-Type": "application/json"}

        response = requests.post(discord_webhook_url, json=payload, headers=headers)

        if response.status_code == 204:
            return "Упоминание успешно отправлено в Discord."
        else:
            return "Произошла ошибка при отправке упоминания в Discord."
    else:
        return "Игрок не найден."


if __name__ == "__main__":
    app.run()
