import requests
import asyncio
import websocket
import json


TTV_BOT_USER_ID = "YOUR_BOT_USER_ID_HERE"
TTV_OAUTH_TOKEN = "YOUR_OAUTH_TOKEN_HERE"
TTV_CLIENT_ID = "YOUR_BOT_CLIENT_ID_HERE"

CHAT_CHANNEL_USER_ID = "USER_ID_OF_CHAT_CHANNEL_TO_USE"

EVENTSUB_WEBSOCKET_URL = "wss://eventsub.wss.twitch.tv/ws"

ttv_headers = {
    "Authorization":f"Bearer {TTV_OAUTH_TOKEN}",
    "Client-Id":TTV_CLIENT_ID,
    "Content-Type":"application/json"
}

response = requests.get('https://id.twitch.tv/oauth2/validate', headers={"Authorization":f"OAuth {TTV_OAUTH_TOKEN}"})
if response.status_code != 200:
    print(f"Token not valid. Status code: {response.status_code}")
else:
    print("Token validated.")

def on_open(ws):
    print(f"Websocket connection opened to {EVENTSUB_WEBSOCKET_URL}")

def on_message(ws, message):
    print("Message received")
    msg_json = json.loads(message)
    print(msg_json["metadata"]["message_type"])
    if msg_json["metadata"]["message_type"] == "session_welcome":
        print("session_welcome received. Calling registerEventSubListener.")
        registerEventSubListener(msg_json["payload"]["session"]["id"])
    

def registerEventSubListener(session_ID):
    print("registerEventSubListener called")
    print("Constructing data for POST request")
    es_data = {
        "type" : "channel.chat.message",
        "version" : "1",
        "condition" : {
            "broadcaster_user_id" : CHAT_CHANNEL_USER_ID,
            "user_id" : TTV_BOT_USER_ID
        },
        "transport" : {
            "method" : "websocket",
            "session_id" : session_ID
        }
    }
    print("Sending post request...")
    es_response = requests.post('https://api.twitch.tv/helix/eventsub/subscriptions',headers=ttv_headers, json=es_data)
    print(es_response)
    if es_response.status_code != 202 :
        print(f"Failed to subscribe. Status code {es_response.status_code}")
    else:
        print("Subscribed to channel.")



ttv_websocketClient = websocket.WebSocketApp(EVENTSUB_WEBSOCKET_URL,on_open=on_open,on_message=on_message)
print("Websocket App Created")
print("Running websocket client...")
ttv_websocketClient.run_forever()
print("Websocket client closed.")