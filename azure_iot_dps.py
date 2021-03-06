# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import sys
import httplib2 as http
import urllib
if sys.version_info[0] >= 3:
  import urllib.parse
import json
import hashlib
import hmac
import base64
import calendar
import time

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

EXPIRES = 7200 # 2 hours

def computeDrivedSymmetricKey(secret, regId):
  secret = base64.b64decode(secret)
  derivedSymmetricKey = hmac.new(secret, regId.encode('utf8'), digestmod=hashlib.sha256).digest()
  return base64.b64encode(derivedSymmetricKey)


def loopAssign(operationId, headers, deviceId, scopeId, deviceKey, callback):
  uri = "https://global.azure-devices-provisioning.net/%s/registrations/%s/operations/%s?api-version=2019-03-31" % (scopeId, deviceId, operationId)

  target = urlparse(uri)
  method = 'GET'

  h = http.Http()
  response, content = h.request(
          target.geturl(),
          method,
          "",
          headers)
  data = json.loads(content)

  if 'status' in data:
    if data['status'] == 'assigning':
      time.sleep(1)
      loopAssign(operationId, headers, deviceId, scopeId, deviceKey, callback)
      return
    elif data['status'] == "assigned":
      state = data['registrationState']
      hub = state['assignedHub']
      callback(None, hub)
      return

  callback(data, None)

def getConnectionString(deviceId, mkey, scopeId, isMasterKey, callback, modelId=None):
  global EXPIRES

  body = ""
  if modelId:
    body = "{\"registrationId\":\"%s\", \"payload\":{\"iotcModelId\":\"%s\"}}" % (deviceId, modelId)
  else:
    body = "{\"registrationId\":\"%s\"}" % deviceId

  expires = calendar.timegm(time.gmtime()) + EXPIRES

  deviceKey = mkey
  if isMasterKey:
    deviceKey = computeDrivedSymmetricKey(mkey, deviceId)

  sr = scopeId + "%2fregistrations%2f" + deviceId
  sigNoEncode = computeDrivedSymmetricKey(deviceKey, sr + "\n" + str(expires))
  if sys.version_info[0] < 3:
    sigEncoded = urllib.quote(sigNoEncode, safe='~()*!.\'')
  else:
    sigEncoded = urllib.parse.quote(sigNoEncode, safe='~()*!.\'')

  authString = "SharedAccessSignature sr=" + sr + "&sig=" + sigEncoded + "&se=" + str(expires) + "&skn=registration"
  headers = {
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
    "Connection": "keep-alive",
    "UserAgent": "prov_device_client/1.0",
    "Authorization" : authString
  }

  uri = "https://global.azure-devices-provisioning.net/%s/registrations/%s/register?api-version=2019-03-31" % (scopeId, deviceId)
  target = urlparse(uri)
  method = 'PUT'

  h = http.Http()
  response, content = h.request(
          target.geturl(),
          method,
          body,
          headers)
  data = json.loads(content)

  if 'errorCode' in data:
    callback(data, None)
  else:
    if isMasterKey:
      loopAssign(data['operationId'], headers, deviceId, scopeId, deviceKey, callback)
    else:
      loopAssign(data['operationId'], headers, deviceId, scopeId, "KEY", callback)
