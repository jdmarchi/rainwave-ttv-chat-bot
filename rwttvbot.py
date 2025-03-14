import requests
import asyncio
import websocket
import json


TTV_BOT_USER_ID = "BOT_USER_ID_HERE"
TTV_OAUTH_TOKEN = "OAUTH_TOKEN_HERE"
TTV_CLIENT_ID = "CLIENT_ID_HERE"

CHAT_CHANNEL_USER_ID = "BROADCASTER_ID_HERE"

EVENTSUB_WEBSOCKET_URL = "wss://eventsub.wss.twitch.tv/ws"

ttv_headers = {
    "Authorization":f"Bearer {TTV_OAUTH_TOKEN}",
    "Client-Id":TTV_CLIENT_ID,
    "Content-Type":"application/json"
}


response = requests.get('https://id.twitch.tv/oauth2/validate', headers={"Authorization":f"OAuth {TTV_OAUTH_TOKEN}"})
if response.status_code != 200:
    print(f"User Access Token not valid. Status code: {response.status_code}")
else:
    print("User Access Token validated.")
print(response.content.decode('utf-8'))

response = requests.post('https://id.twitch.tv/oauth2/token', data={"client_id":TTV_CLIENT_ID,"client_secret":"CLIENT_SECRET_HERE","grant_type":"client_credentials"})
response_json = response.json()
print(response_json)
if "access_token" in response_json:
    print("App Access Token received.")
    APP_ACCESS_TOKEN = response_json['access_token']
    print(APP_ACCESS_TOKEN)
else:
    print("Failed to get App Access Token.")

ttv_app_headers = {
    "Authorization":f"Bearer {APP_ACCESS_TOKEN}",
    "Client-Id":TTV_CLIENT_ID,
    "Content-Type":"application/json"
}

def on_open(ws):
    print(f"Websocket connection opened to {EVENTSUB_WEBSOCKET_URL}")

def on_message(ws, message):
    msg_json = json.loads(message)
    print(msg_json["metadata"]["message_type"])
    if msg_json["metadata"]["message_type"] == "session_welcome":
        print("session_welcome received. Calling registerEventSubListener.")
        registerEventSubListener(msg_json["payload"]["session"]["id"])
    elif msg_json["metadata"]["message_type"] == "notification":
        print("Possible chat received.")
        print(msg_json["payload"]["event"]["message"]["text"])
        if msg_json["payload"]["event"]["message"]["text"] == "!song":
            print("Song request received.")
            print("Fetching song info from Rainwave")
            song_request = requests.get('https://rainwave.cc/api4/info_all?sid=2')
            print("Parsing to JSON")
            song_json = song_request.json()
            song_name = song_json["all_stations_info"]["2"]["title"]
            print(song_name)
            print("Getting artists...")
            artist_name = song_json["all_stations_info"]["2"]["artists"]
            print(artist_name)
            link_request = requests.get('https://rainwave.cc/api4/info?sid=2')
            link_json = link_request.json()
            song_link = link_json["sched_current"]["songs"][0]["url"]
            print(song_link)                                        
            sendChatMessage(f"Now playing: {song_name} - {artist_name}. Get @ OCR: {song_link}")

def sendChatMessage(message):
    print("sendChatMessage called")
    print("Constructing data for POST request")
    chat_data = {
        "broadcaster_id": CHAT_CHANNEL_USER_ID,
        "sender_id": CHAT_CHANNEL_USER_ID,
        "message": message
    }
    chat_request = requests.post('https://api.twitch.tv/helix/chat/messages', headers=ttv_headers, json=chat_data)

def registerEventSubListener(session_ID):
    print("registerEventSubListener called")
    print("Constructing data for POST request")
    es_data = {
        "type": "channel.chat.message",
        "version": "1",
        "condition": {
            "broadcaster_user_id": CHAT_CHANNEL_USER_ID,
            "user_id": CHAT_CHANNEL_USER_ID
        },
        "transport": {
            "method": "websocket",
            "session_id": session_ID
        }
    }
    print("Sending post request...")
    es_response = requests.post('https://api.twitch.tv/helix/eventsub/subscriptions', headers=ttv_headers, json=es_data)
    print(es_response)
    if es_response.status_code != 202:
        print(f"Failed to subscribe. Status code {es_response.status_code}")
        print(f"Response content: {es_response.content.decode('utf-8')}")
    else:
        print("Subscribed to channel.")



ttv_websocketClient = websocket.WebSocketApp(EVENTSUB_WEBSOCKET_URL,on_open=on_open,on_message=on_message)
print("Websocket App Created")
print("Running websocket client...")
ttv_websocketClient.run_forever()
print("Websocket client closed.")