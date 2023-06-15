from flask import Flask, request
import requests

app = Flask(__name__)

# Discord API endpoint for getting guild members
url = "https://discord.com/api/v10/guilds/{guild_id}/members"
guild_id = "1079844266727190668"  # Замените на ID вашего сервера Discord

# Discord bot token for authentication
token = "MTExODgzMjUxODQ0NDA5NzU2Ng.G5uNC_.Key_J3qs-KC9JnhG_s48S2KseTfUpMv6ftkImA"  # Замените на токен вашего бота Discord
headers = {
    "Authorization": f"Bot {token}"
}

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
    member_id = get_member_id_by_name(player_name)

    if member_id:
        # Формируем сообщение
        message = f"Игрок {player_name} найден. ID: {member_id}"

        # Отправляем сообщение на вебхук Discord
        discord_webhook_url = "https://discord.com/api/webhooks/1118673768710144033/RwC_fIX-By29CheDDag2J0tkaZErmO3Bb6rUnUsV-F4K5UJTCWlNTZ0ixgpKr70AA41q"  # Замените на URL вашего вебхука Discord
        payload = {
            "content": message
        }
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(discord_webhook_url, json=payload, headers=headers)

        if response.status_code == 204:
            return "Упоминание успешно отправлено в Discord."
        else:
            return "Произошла ошибка при отправке упоминания в Discord."
    else:
        return "Игрок не найден."

if __name__ == "__main__":
    app.run()
