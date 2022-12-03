import json
import requests

from inverter import myconverter

def sendData(data,targetUrl):
  try:
    jsonData  = json.dumps(data, default=myconverter)
    res = requests.post(targetUrl,json=jsonData)
    return res.status_code
  except:
    return 500