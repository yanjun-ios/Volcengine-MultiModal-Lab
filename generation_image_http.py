import json
import sys
import os
import base64
import datetime
import hashlib
import hmac
import requests
from time import sleep

method = 'POST'
host = 'visual.volcengineapi.com'
# host = 'visualaccapi.speedifyvolcai.com'
region = 'cn-north-1'
endpoint = 'https://visual.volcengineapi.com'
service = 'cv'

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(key.encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'request')
    return kSigning

def formatQuery(parameters):
    request_parameters_init = ''
    for key in sorted(parameters):
        request_parameters_init += key + '=' + parameters[key] + '&'
    request_parameters = request_parameters_init[:-1]
    return request_parameters

def signV4Request(access_key, secret_key, service, req_query, req_body):
    if access_key is None or secret_key is None:
        print('No access key is available.')
        sys.exit()

    t = datetime.datetime.utcnow()
    current_date = t.strftime('%Y%m%dT%H%M%SZ')
    # current_date = '20210818T095729Z'
    datestamp = t.strftime('%Y%m%d')  # Date w/o time, used in credential scope
    canonical_uri = '/'
    canonical_querystring = req_query
    signed_headers = 'content-type;host;x-content-sha256;x-date'
    payload_hash = hashlib.sha256(req_body.encode('utf-8')).hexdigest()
    content_type = 'application/json'
    canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + host + \
        '\n' + 'x-content-sha256:' + payload_hash + \
        '\n' + 'x-date:' + current_date + '\n'
    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + \
        '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
    # print(canonical_request)
    algorithm = 'HMAC-SHA256'
    credential_scope = datestamp + '/' + region + '/' + service + '/' + 'request'
    string_to_sign = algorithm + '\n' + current_date + '\n' + credential_scope + '\n' + hashlib.sha256(
        canonical_request.encode('utf-8')).hexdigest()
    # print(string_to_sign)
    signing_key = getSignatureKey(secret_key, datestamp, region, service)
    # print(signing_key)
    signature = hmac.new(signing_key, (string_to_sign).encode(
        'utf-8'), hashlib.sha256).hexdigest()
    # print(signature)

    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + \
        credential_scope + ', ' + 'SignedHeaders=' + \
        signed_headers + ', ' + 'Signature=' + signature
    # print(authorization_header)
    headers = {'X-Date': current_date,
               'Authorization': authorization_header,
               'X-Content-Sha256': payload_hash,
               'Content-Type': content_type
               }
    # print(headers)

    # ************* SEND THE REQUEST *************
    # request_url = endpoint + '?' + canonical_querystring
    request_url = 'https://visualaccapi.speedifyvolcai.com' + '?' + canonical_querystring

    print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
    print('Request URL = ' + request_url)
    try:
        r = requests.post(request_url, headers=headers, data=req_body)
    except Exception as err:
        print(f'error occurred: {err}')
        raise
    else:
        print('\nRESPONSE++++++++++++++++++++++++++++++++++++')
        print(f'Response code: {r.status_code}\n')
        # 使用 replace 方法将 \u0026 替换为 &
        resp_str = r.text.replace("\\u0026", "&")
        print(f'Response body: {resp_str}\n')
    
    return json.loads(resp_str)

def infer(access_key,secret_key):
    # 请求Query，按照接口文档中填入即可
    query_params = {
        'Action': 'CVSync2AsyncSubmitTask',
        'Version': '2022-08-31',
    }
    formatted_query = formatQuery(query_params)

    # 请求Body，按照接口文档中填入即可
    body_params = {
        "req_key": "i2i_portrait_photo",
        "image_input": "https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_b9d0ea6bb4528cce79517a7c706ad1b7.png",
        "prompt": "演唱会现场的合照，闪光灯拍摄",
        "gpen": 0.4,
        "skin": 0.3,
        "skin_unifi": 0,
        "width": 1024,
        "height": 1024,
        "gen_mode": "creative",
        "seed": -1,
        "return_url": True
    }
    formatted_body = json.dumps(body_params)
    
    return signV4Request(access_key, secret_key, service,
                  formatted_query, formatted_body)

def get_result(access_key,secret_key,task_id):
    query_params = {
        'Action': 'CVSync2AsyncGetResult',
        'Version': '2022-08-31',
    }
    formatted_query = formatQuery(query_params)
    body_params = {
        "req_key": "i2i_portrait_photo",
        "task_id": task_id
    }
    formatted_body = json.dumps(body_params)
    
    return signV4Request(access_key, secret_key, service,
                  formatted_query, formatted_body)

if __name__ == "__main__":
    # 请求凭证，从访问控制申请
    access_key = '*'
    secret_key = '*'

    result = infer(access_key,secret_key)
    
    task_id = result['data']['task_id']
    while True:
        sleep(2)
        result = get_result(access_key,secret_key,task_id)
        # print(f"Get result: {result}")
        if result['data']['image_urls'] is not None:
            break
        
        


