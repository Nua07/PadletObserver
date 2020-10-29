import ssl
import websocket
import requests
import json
from bs4 import BeautifulSoup as bs

mainurl = "https://padlet.com/"
sockurl = "wss://rt.padlet.com/_/cable"

def getWallId(req):
    html = req.text

    b = bs(html, "html.parser")
    infourl = mainurl + b.select("link#starting-state-preload")[0].get("href")

    return json.loads(requests.get(infourl).text)["wall"]["id"]

def getDeviceUUID(req):
    return req.cookies["ww_d"]

#url = "https://padlet.com/abcd/abcd"
url = input("url: ")
req = requests.get(url)

wallId = getWallId(req)
deviceUUID = getDeviceUUID(req)
cookies = "; ".join(str(a)+"="+str(b) for a, b in req.cookies.get_dict().items())

print("wallId : {}\nUUID : {}".format(wallId, deviceUUID))
print("cookies : ", cookies)
print("\n")

def on_message(ws, msg):
    try:
        obj = json.loads(msg)

        if "type" in obj and obj["type"] == "welcome":
            ws.send(json.dumps({"command":"subscribe", "identifier":json.dumps({"channel":"WallChannel", "wall_id":wallId})}))
            ws.send(json.dumps({"command":"subscribe", "identifier":json.dumps({"channel":"DeviceChannel", "device_id":deviceUUID})}))
        
        if "identifier" in obj and "message" in obj:
            identifier = json.loads(obj["identifier"])
            message = obj["message"]
        
            if identifier["channel"] == "WallChannel":
                print("WallId : {}\nevent : {}\nuid : {}\nmessage : {}\n".format(identifier["wall_id"], message["event"], message["uid"], message["message"]))
                print("")
    except Exception as e:
        print("Err ", str(e))

ws = websocket.WebSocketApp(sockurl, on_message = on_message, cookie=cookies)
ws.run_forever()
