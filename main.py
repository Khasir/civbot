import argparse
import json

import requests
from flask import Flask, request


CIV_CHANNEL_ID = "967454302455095306"
ENDPOINT = "https://discord.com/api"


class CivJSONObject:
    def __init__(self, incoming):
        self.game_name = incoming['value1']
        self.player_name = incoming['value2']
        self.turn_number = incoming['value3']


class DiscordClient:
    def __init__(self, token: str):
        self.token = token

    def send_message(self, incoming):
        print("received", incoming)
        with open("temp.txt", 'w') as file:
            file.write(str(incoming))
        incoming = CivJSONObject(incoming)

        data = {
            "content": f"{incoming.game_name}: Turn {incoming.turn_number} for {convert_username_to_mention(incoming.player_name)}!"
        }
        headers = {
            "Authorization": f"Bot {self.token}",
            "User-Agent": "CivBot (khasir.hean@gmail.com, v0.1)"
        }
        result = requests.post(f"{ENDPOINT}/channels/{CIV_CHANNEL_ID}/messages", data=data, headers=headers)
        print(result.status_code)
        print(result.json())


def convert_username_to_mention(username: str):
    user_id = USER_MAPPING.get(username, '')
    if user_id:
        return f"<@{user_id}>"
    return username


def is_valid(payload: str):
    try:
        payload = json.loads(payload)
    except JSONDecodeError:
        return False

    acceptable = "value1", "value2", "value3"
    for value in acceptable:
        if value not in payload:
            return False
    for value in payload:
        if value not in acceptable:
            return False
    return True


parser = argparse.ArgumentParser()
parser.add_argument('discord_token_file')
parser.add_argument('user_mapping_file')
args = parser.parse_args()

with open(args.discord_token_file) as file:
    token = file.read().strip()
print("Token read.")
with open(args.user_mapping_file) as file:
    USER_MAPPING = json.load(file)
print("User mapping read.")

app = Flask(__name__)
client = DiscordClient(token)


@app.route('/',methods=['POST'])
def process():
    if not is_valid(request.data):
        abort(401)
    incoming = json.loads(request.data)
    client.send_message(incoming)
    return "OK"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
    