from requests.api import options
import websocket
import json
import threading
import time
import requests
from services import *
import os
from pprint import pprint
from datetime import datetime

token = os.environ["auth"]
appId = os.environ["appid"]

threadList = []
counter3 = 0

question_db = read_json("Questions.json")

channelIDs = [ 8979787696969687687998 ]

class responseThread (threading.Thread):
   def __init__(self):
       super(responseThread, self).__init__()
       self._stop_event = threading.Event() 
   def stop(self):
       self._stop_event.set()
   def setValues(self, authKey, appId, messageId, channelId, guildId,session_id, delay,typeD="airdrop",message=None):
       self.authKey = authKey
       self.appId = appId
       self.session_id = session_id
       self.messageId = messageId
       self.channelId = channelId
       self.guildid = guildId
       self.delay = delay
       self.typeD = typeD
       self.message = message
   def run(self):
       global counter3
       counter3+=1
       sendResponseCurr(self.authKey,self.appId, self.messageId, self.channelId, self.guildid,self.session_id , self.delay,self.typeD,self.message)

def send_json_request(ws, request):
    ws.send(json.dumps(request))

def receive_json_response(ws):
    response = ws.recv()
    if(response):
        return json.loads(response)

def heartbeat(interval, ws):
    print("heartbeat begin")
    flag = 1
    while(True):
        time.sleep(interval * flag)
        heartbeatJSON = {
            "op": 1,
            "d": "null"
        }
        try:
            send_json_request(ws, heartbeatJSON)
            flag = 1
        except Exception:
            flag = 0
            continue
        print("heartbeat sent")

def WsConnect():
    ws = websocket.WebSocket()
    ws.connect("wss://gateway.discord.gg/?v=6&encoding=json")
    event = receive_json_response(ws)
    heartbeat_interval = event["d"]["heartbeat_interval"]/1000

    threading._start_new_thread(heartbeat, (heartbeat_interval, ws))
    return ws

wsG = websocket.WebSocket()

def setWsG(ws):
    global wsG
    wsG = ws

def getWsG():
    global wsG
    return wsG

setWsG(WsConnect())

payload = {
    "op": 2,
    "d":{
        "token": token,
        "properties": {
            "$os": "linux",
            "$browser": "chrome",
            "$device": "pc"
        }
    }
}
def getPayload():
    global payload
    return payload

send_json_request(getWsG(),payload)

def got_emoji(msg):
    return msg.index("with")

session_id = None


while(True):
    try:
        event = receive_json_response(getWsG())
        if(event["t"] == "READY"):
            session_id = event["d"]["session_id"]
    except:
        wsL = WsConnect()
        setWsG(wsL)
        pld = getPayload()
        send_json_request(wsL, pld)
        continue
    try:
        content = event["d"]["content"]
        if("/check" in content):
            sendMessage(token,channelIDs[0],"$chks top")
    except:
        pass
    try:
        content = event["d"]["embeds"][0]
        if('%' in content["description"]):
            pentoken = getPentos(content["description"])
        else:
            pentoken = getPentos_novalue(content["description"])
        if(pentoken < float(os.environ["threshold"]) and event["t"] == "MESSAGE_CREATE"):
            print("%"+str(pentoken)+" ignored... ")
        else:
            delay  = getDelay(event["d"]["timestamp"],content["timestamp"])
            if("A pentogram appears" in content["title"] and event["t"] == "MESSAGE_CREATE"):
                resThread = responseThread()
                resThread.setValues(authKey= token, appId = appId, messageId = event["d"]["id"], channelId = event["d"]["channel_id"], guildId = event["d"]["guild_id"],session_id=session_id, delay = delay)
                threadList.append(resThread)
                threadList[-1].start()
            elif("Phrase pentogram" in content["title"] and event["t"] == "MESSAGE_CREATE" and pentoken < 5.0):
                message = getPhaseMsg(content["description"])
                typeD = "phrase"
                resThread = responseThread()
                resThread.setValues(authKey= token, appId = appId, messageId = event["d"]["id"], channelId = event["d"]["channel_id"], guildId = event["d"]["guild_id"],session_id=session_id, delay = delay,typeD=typeD,message=message)
                threadList.append(resThread)
                threadList[-1].start()
            elif("Trivia pentogram time" in content["title"] and event["t"] == "MESSAGE_CREATE" and pentoken < 5.0):
                option = event["d"]["components"][0]["components"]
                question = findQuestion(content["description"])
                message = findAnswer(question,question_db,option)
                typeD = "trivia"
                resThread = responseThread()
                resThread.setValues(authKey= token, appId = appId, messageId = event["d"]["id"], channelId = event["d"]["channel_id"], guildId = event["d"]["guild_id"],session_id=session_id, delay = delay,typeD=typeD,message=message)
                threadList.append(resThread)
                threadList[-1].start()
            else:
                pass
    except:
        pass
