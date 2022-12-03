import json
import requests

from inverter import myconverter

def sendData(data,targetUrl):
  try:
    jsonData  = json.dumps(data, default=myconverter)
    res = requests.post(targetUrl,data=jsonData,headers={'Content-type': 'application/json'})
    return res.status_code
  except:
    return 500
