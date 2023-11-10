import socket
import requests
import re
import json
import os

datatowrite = {
    "WEBHOOK_URL": "url",
    "Port": 600,
    "Join_color": "0x00ff00",
    "Leave_color": "0xff0000",
    "Message_color": "0x42f5ad",
    "Api_key": "key"
}

folder_name = "data"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
filename = os.path.join(folder_name, "config.json")
if not os.path.isfile(filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(datatowrite, f, indent=4)
        
with open(filename, 'r', encoding='utf-8') as f:
    config = json.load(f)
    global WEBHOOK_URL_g, Port_g, Join_color, Leave_color, Message_color, Api_key
    WEBHOOK_URL_g = config['WEBHOOK_URL']
    Port_g = int(config['Port'])
    Join_color = int(config['Join_color'], 16)
    Leave_color = int(config['Leave_color'], 16)
    Message_color = int(config['Message_color'], 16)
    Api_key = config['Api_key']

def send_discord_webhook(embed_data):
    payload = {'embeds': [embed_data]}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(WEBHOOK_URL_g, data=json.dumps(payload), headers=headers)
    print(f"Ответ от вебхука: {response.status_code}")
    
def get_steam_avatar_url(steam_id):
    api_url = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={Api_key}&steamids={steam_id}'
    try:
        response = requests.get(api_url)
        data = response.json()
        avatar_url = data['response']['players'][0]['avatarfull']
        return avatar_url
    except Exception as e:
        print(f"Error fetching Steam avatar URL: {e}")
        return None
    
def parse_message(data):
    match_message = re.search(r'GET /Message/sender_n = (\S+): user_peer_id = (\S+): message = (.+): steam_id = (\S+): HTTP/1.1', data)
    if match_message:
        sender_name = match_message.group(1)
        user_peer_id = match_message.group(2)
        message = match_message.group(3)

        embed_data = {
            'title': 'Message',
            'description': f"**Sender Name:** {sender_name}\n**User Peer ID:** {user_peer_id}\n**Message:** {message}",
            'color': Message_color  
        }

        send_discord_webhook(embed_data)

def parse_leave(data):
    match_leave = re.search(r'GET /Leave/steam_id = (\S+): name = (.+) HTTP/1.1', data)
    if match_leave:
        steam_id = match_leave.group(1)
        name = match_leave.group(2)
        avatar_url = get_steam_avatar_url(steam_id)

        embed_data = {
            'title': f'{name} Leave',
            'url': f"https://steamcommunity.com/profiles/{steam_id}",
            'description': f"**Steam ID:** {steam_id}\n**Player:** {name} leave.",
            'color': Leave_color,
            "thumbnail": {"url": avatar_url}
        }

        send_discord_webhook(embed_data)

def parse_join(data):
    match_join = re.search(r'GET /Join/steam_id = (\S+): name = (.+) HTTP/1.1', data)
    if match_join:
        steam_id = match_join.group(1)
        name = match_join.group(2)
        avatar_url = get_steam_avatar_url(steam_id)
        
        embed_data = {
            'title': f'{name} Joined',
            'url': f"https://steamcommunity.com/profiles/{steam_id}",
            'description': f"**Steam ID:** {steam_id}\n**Player:** {name} joined.",
            'color': Join_color,
            "thumbnail": {"url": avatar_url}
        }

        send_discord_webhook(embed_data)

def main():
    if WEBHOOK_URL_g == "url":
        print("Please insert the webhook URL")
        return
    if Port_g == "":
        print("Please insert the Port")
        return
    if Api_key == "key":
        print("Please insert the API key")
        return
                    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = Port_g
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"The server is listening on port: {port}")

    while True:
        client_socket, client_address = server_socket.accept()
        data = client_socket.recv(1024)
        if not data:
            break

        decoded_data = data.decode('utf-8').split('\r\n')
        print(f"Received from client: {decoded_data[0]}")

        parse_message(decoded_data[0])
        parse_leave(decoded_data[0])
        parse_join(decoded_data[0])

        client_socket.close()

    server_socket.close()

if __name__ == "__main__":
    main()