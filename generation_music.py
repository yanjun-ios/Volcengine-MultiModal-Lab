import json
import time
import requests
import Sign

STATUS_CODE_SUCCESS = 0
QUERY_STATUS_CODE_WAITING = 0
QUERY_STATUS_CODE_HANDING = 1
QUERY_STATUS_CODE_SUCCESS = 2
QUERY_STATUS_CODE_FAILED = 3

host = "open.volcengineapi.com"
version = "2024-08-12"
region = "cn-beijing"

def get_response(response):
    response_json = json.loads(response.text)
    return response_json.get('Code'), response_json.get('Message'), response_json.get('Result'), response_json.get(
        'ResponseMetadata')

def sign(body={},action="",service="imagination"):
    query = {'Action':  action,
             'Version': version}
    x_content_sha256 = Sign.hash_sha256(json.dumps(body))
    headers = {"Content-Type": 'application/json',
               'Host': host,
               'X-Date': Sign.get_x_date(),
               'X-Content-Sha256': x_content_sha256
               }
    # 生成背景音乐请求签名
    authorization = Sign.get_authorization("POST", headers=headers, query=query, service=service, region=region, ak=ak, sk=sk)
    headers["Authorization"] = authorization
    return authorization,headers

def generation_bgm(ak,sk,text,genre,mood,instrument,theme,Duration=5):
    path = "/"
    # query = {'Action': 'GenBGM',
    #          'Version': version}
    body = {
        'Text': text,
        'Theme': theme,
        'Genre': genre,
        'Mood': mood,
        'Instrument': instrument,
        'Duration': Duration,
    }
    authorization,headers = sign(body=body,action="GenBGM",service="imagination")
    # 发送生成BGM的请求
    response = requests.post(Sign.get_url(host, path, "GenBGM", version), data=json.dumps(body), headers=headers)
    # 查询歌曲生成信息
    code, message, result, ResponseMetadata = get_response(response)
    if code != STATUS_CODE_SUCCESS or not response.ok:
        raise RuntimeError(response.text)
    taskId = result['TaskID']
    predictedWaitTime =  5  # 预计等待生成音乐需要的时间，单位：s
    time.sleep(predictedWaitTime)
    body = {'TaskID': taskId}

    # 查询请求签名
    # x_content_sha256 = Sign.hash_sha256(json.dumps(body))
    # headers['X-Content-Sha256'] = x_content_sha256
    # headers['X-Date'] = Sign.get_x_date()
    # action = 'QuerySong'
    # query["Action"] = action
    # authorization = Sign.get_authorization("POST", headers=headers, query=query, service=service, region=region, ak=ak,                                       sk=sk)
    # headers["Authorization"] = authorization
    authorization,headers = sign(body=body,action="QuerySong",service="imagination")
    songDetail = None
    while True:
        response = requests.post(Sign.get_url(host, path, "QuerySong", version), data=json.dumps(body), headers=headers)
        print(response.text)
        if not response.ok:
            raise RuntimeError(response.text)

        code, message, result, ResponseMetadata = get_response(response)
        progress = result.get('Progress')
        status = result.get('Status')

        if status == QUERY_STATUS_CODE_FAILED:
            raise RuntimeError(response.text)
        elif status == QUERY_STATUS_CODE_SUCCESS:
            songDetail = result.get('SongDetail')
            print(f"===>query finished:{progress}")
            break
        elif status == QUERY_STATUS_CODE_WAITING or status == QUERY_STATUS_CODE_HANDING:
            print(f"===>Progress:{progress}")
            # 间隔一定时间再查询
            time.sleep(5)
        else:
            print(response.text)
            break

    if songDetail is not None:
        audioUrl = songDetail.get('AudioUrl')
        print(f"===>AudioUrl:{audioUrl}")

    return audioUrl

if __name__ == "__main__":
    ak = "AKLTYjRjNTE2ZjkwMTIyNGZmMTlmMjczNGJmZWYwYWIwOGY"
    sk = "TXpSalpXUm1OREl4WldJNE5HSXlNbUpqWTJRNFpETmlNRGcyTVdFellUYw=="
    text = "现代感十足的商业广告配乐"
    genre = ["corporate"]
    mood = ["peaceful",'soft']
    Instrument=['piano','strings']
    Theme = ["every day"]
    Duration = 5 # 单位：秒，范围：[1,60]
    generation_bgm(ak,sk,text,genre,mood,Instrument,Theme,Duration)
    