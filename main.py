import logging
from flask import Flask, request
import requests
import os

app = Flask(__name__)

url = "https://discord.com/api/v10/guilds/{guild_id}/members"
guild_id = os.getenv("DISCORD_GUILD_ID")
token = os.getenv("DISCORD_TOKEN")
headers = {
    "Authorization": f"Bot {token}"
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_member_id_by_name(member_name):
    request_url = url.replace("{guild_id}", guild_id)
    params = {
        "limit": 1000
    }

    response = requests.get(request_url, headers=headers, params=params)

    if response.status_code == 200:
        members = response.json()

        for member in members:
            if member["user"]["display_name"] == member_name:
                return member["user"]["id"]

    return None


@app.route("/search", methods=["POST"])
def search_player():
    player_name = request.form.get("playerName")

    player_name = player_name.strip()

    logger.debug(f"Received playerName from form: {player_name}")

    if not player_name:
        logger.debug("No player name provided")
        return "Пожалуйста, введите никнейм игрока."

    member_id = get_member_id_by_name(player_name)

    if member_id:
        message = f"1.<@{member_id}>\n" "2.Прослушал вводную лекцию"

        discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        if not discord_webhook_url:
            logger.debug("No Discord webhook URL configured")
            return "Webhook URL для Discord не настроен."

        payload = {"content": message}
        headers = {"Content-Type": "application/json"}

        response = requests.post(discord_webhook_url, json=payload, headers=headers)
        logger.debug(f"Response from Discord webhook: {response.text}")

        if response.status_code == 204:
            return "Упоминание успешно отправлено в Discord."
        else:
            return "Произошла ошибка при отправке упоминания в Discord."
    else:
        logger.debug(f"Player not found: {player_name}")
        return "Игрок не найден."


if __name__ == "__main__":
    app.run()
