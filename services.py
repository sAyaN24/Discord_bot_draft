import requests, ctypes, random
import datetime, time, sys,os
import re 
import json

novaluetokens = {
    
}

try:
    s = os.environ["seed"]
    random.seed(s)
except:
    pass


chList={}

def getChList():
    global chList
    return chList

def setChList(openfile):
    global chList
    chList = json.load(openfile)

def read_json(file_name):
    file = open(file_name)
    data = json.load(file)
    return data

def terminate_thread(thread):
    if not thread.isAlive():
        return

    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        raise ValueError("nonexistent thread id")
    elif res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def getMessage(channelId, authKey):
    url = "https://discord.com/api/v9/channels/"+channelId+"/messages"
    headers = {'Content-Type':'application/x-www-form-urlencoded', 'authorization': authKey}
    re = requests.get(url, headers=headers)
    if(re.status_code==200):
        dict_list = json.loads(re.text)
        return dict_list[0]
    else:
        return "Null"


def sendResponse(authKey, messageId, channelId, emoj, author, delay):
    url = "https://discord.com/api/v9/channels/"+str(channelId)+"/messages/"+str(messageId)+"/reactions/"+emoj
    headers = {'Content-Type':'application/x-www-form-urlencoded', 'authorization': authKey}
    if(delay<6):
        return
    delay = randomOP(delay-2)
    time.sleep(delay)
    re = requests.put(url, headers=headers)
    if(re.status_code==204):
        return True
    else:
        return False


def sendInteraction(authKey, appId, messageId, channelId, guildId,session_id,text):
    url = "https://discord.com/api/v9/interactions"
    headers = {'Content-Type':'application/json', 'authorization': authKey}
    data = {
        "type": 3,
        "guild_id": str(guildId),
        "channel_id": str(channelId),
        "message_flags": 0,
        "message_id": str(messageId),
        "application_id": str(appId),
        "session_id":session_id,
        "data": {
            "component_type": 2,
            "custom_id": text
        }
    }
    re = requests.post(url, headers=headers,json = data)

    if(re.status_code == 204):
        return True
    else:
        return False

def getPhaseMsg(message):
    result = re.findall("\*\* \*(.*)\*",message).pop().replace("\u200b","")
    return result

def findQuestion(message):
    result = re.findall("\*\* \*(.*)\*",message).pop()
    return result


def sendResponseCurr(authKey, appId, messageId, channelId, guildId,session_id, delay,droptype="airdrop",message=None):
    if(delay<6):
        return
    delay = randomOP(delay-2)
    time.sleep(delay)
    if(droptype == "phrase"):
        sendMessage(authKey,channelId,message)
    elif(droptype == "trivia"):
        sendInteraction(authKey,appId,messageId,channelId,guildId,session_id,message)
    else:
        sendInteraction(authKey, appId, messageId, channelId, guildId,session_id,"airdrop-claim")

def randomOP(range):
    if(range<=6):
        range+=2
    return random.randint(0,range-4)*random.random() + 4
    
def getDelay(start, end):
    strt = datetime.datetime.strptime(start.split(".")[0], "%Y-%m-%dT%H:%M:%S")
    ed = datetime.datetime.strptime(end.split(".")[0], "%Y-%m-%dT%H:%M:%S")
    return int((ed - strt).total_seconds())

def stopPython(delay, dummy):
    time.sleep(delay)
    sys.exit()

def getEmoj(message):
    emoj = message[message.index("with")+5]
    emoj_not_op = str(emoj.encode())
    emoj_not_op = emoj_not_op.replace("\\x","%")
    emojOP = emoj_not_op[2:-1] + "/%40me"
    return emojOP

def getPentos(message):    
    value = re.findall("\$(.*)\)",message).pop()
    value = float(value.replace(",",""))
    return value

def getPentos_novalue(message):
    message = re.findall("\*\*(.*)\*\*",message)[0].split()
    value = message[0].replace(",","")
    token = message[1]
    total = float(value) * novaluetokens[token]
    return total

def sendMessage(token,channel,message):
    link = f"https://discord.com/api/v9/channels/{channel}/messages"
    data = {"content": message}
    header = {"authorization": token}
    requests.post(url=link,data=data,headers=header)


def findAnswer(question,search_space,option):
    correct_answer = search_space[question]
    for i in option:
        if(i["label"] == correct_answer):
            return i["custom_id"]
    return correct_answer