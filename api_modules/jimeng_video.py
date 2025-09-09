# coding:utf-8
"""
既梦AI 视频生成相关API
"""
from __future__ import print_function
import time
import base64
import os
import json
from volcengine.visual.VisualService import VisualService

# 既梦AI - 文生视频S2.0 Pro
def t2v_jimeng_s20_pro(visual_service, prompt, seed=-1,aspect_ratio="16:9"):
    form = {
        "req_key": "jimeng_vgfm_t2v_l20",
        "prompt": prompt,
        "seed": seed,
        "aspect_ratio": aspect_ratio,
    }

    resp = visual_service.cv_sync2async_submit_task(form)
    if resp['code'] != 10000:
        print(resp.get('message', 'Unknown error'))
        return None

    task_id = resp['data']['task_id']
    while True:
        result = visual_service.cv_sync2async_get_result({
            "req_key": "jimeng_vgfm_t2v_l20",
            "task_id": task_id
        })
        print(result)
        if result['code'] != 10000:
            print(result.get('message', 'Unknown error'))
            return None
        if result.get('data', {}).get('resp_data'):
            resp_data = json.loads(result.get('data', {}).get('resp_data'))
            return resp_data.get('urls')[0]
        time.sleep(5)

# 既梦AI - 图生视频S2.0 Pro
def i2v_jimeng_s20_pro(visual_service, prompt, seed=-1,aspect_ratio="16:9", image_url=None, image_base64=None):
    if not image_url and not image_base64:
        raise ValueError("Either image_url or image_base64 must be provided")

    form = {
        "req_key": "jimeng_vgfm_i2v_l20",
        "prompt": prompt,
        "seed": seed,
        "aspect_ratio": aspect_ratio
    }

    if image_url:
        form["image_urls"] = [image_url]
    elif image_base64:
        form["binary_data_base64"] = [image_base64]

    resp = visual_service.cv_sync2async_submit_task(form)
    if resp['code'] != 10000:
        print(resp.get('message', 'Unknown error'))
        return None

    task_id = resp['data']['task_id']
    while True:
        result = visual_service.cv_sync2async_get_result({
            "req_key": "jimeng_vgfm_i2v_l20",
            "task_id": task_id
        })
        print(result)
        if result['code'] != 10000:
            print(result.get('message', 'Unknown error'))
            return None
        if result.get('data', {}).get('resp_data'):
            resp_data = json.loads(result.get('data', {}).get('resp_data'))
            return resp_data.get('urls')[0]
        time.sleep(5)

# 既梦AI - 图生视频 3.0 
def i2v_jimeng_30(visual_service, prompt, seed=-1, image_urls=None, image_base64=None):
    if not image_urls and not image_base64:
        raise ValueError("Either image_urls or image_base64 must be provided")

    form = {
        "req_key": "jimeng_i2v_first_tail_v30_1080",
        "prompt": prompt,
        "seed": seed,
        "frames": 121
    }

    if image_urls:
        form["image_urls"] = ["https://n.sinaimg.cn/sinacn11/350/w1200h750/20180327/32de-fysqfnh2765647.jpg","https://th.bing.com/th/id/R.a4c4e6be86487dabde3dee9b71bbceec?rik=DMQbkJEggdbicg&riu=http%3a%2f%2fimg1.mydrivers.com%2fimg%2f20190220%2fbbc61bcc95234abaa772262676ab6f7d.jpg&ehk=m8gTVa3en1r3m9qD%2f7fgmIEWAVgnMi7dYdCt83AW07Y%3d&risl=&pid=ImgRaw&r=0"]
    elif image_base64:
        form["binary_data_base64"] = [image_base64]

    resp = visual_service.cv_sync2async_submit_task(form)
    if resp['code'] != 10000:
        print(resp.get('message', 'Unknown error'))
        return None

    task_id = resp['data']['task_id']
    while True:
        result = visual_service.cv_sync2async_get_result({
            "req_key": "jimeng_i2v_first_tail_v30_1080",
            "task_id": task_id
        })
        print(result)
        if result['code'] != 10000:
            print(result.get('message', 'Unknown error'))
            return None
        if result.get('data', {}).get('video_url'):
            resp_data = json.loads(result.get('data', {}))
            return resp_data.get('video_url')
        time.sleep(5)