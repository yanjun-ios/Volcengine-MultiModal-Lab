# coding:utf-8
"""
既梦AI 图像生成相关API
"""
from __future__ import print_function
import time
import base64
import os
import json
from volcengine.visual.VisualService import VisualService

# 既梦 AI 文生图2.1
def t2i_jimeng(visual_service, prompt, seed=-1, width=512, height=512,return_url=True,use_pre_llm=True,use_sr=True):
    form = {
        "req_key": "jimeng_high_aes_general_v21_L",
        "prompt": prompt,
        "seed": seed,
        "width": width,
        "height": height,
        "return_url": return_url,
        "use_pre_llm": use_pre_llm,
        "use_sr": use_pre_llm,
        "logo_info": {
            "add_logo": False,
            "position": 0,
            "language": 0,
            "opacity": 0.3,
            "logo_text_content": "这里是明水印内容"
        }
    }
    resp = visual_service.cv_process(form)
    if resp.get('data') and resp['data'].get('image_urls'):
        return resp['data']['image_urls'][0]
    return None

# 既梦 AI 图生图 3.0
def i2i_jimeng_v30(visual_service, prompt, seed=-1,width=1328, height=1328, scale=0.5, image_url=None, image_base64=None):
    if not image_url and not image_base64:
        raise ValueError("Either image_url or image_base64 must be provided")

    form = {
        "req_key": "jimeng_i2i_v30",
        "prompt": prompt,
        "seed": seed,
        "scale": scale,
        "width": width,
        "height":height
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
            "req_key": "jimeng_i2i_v30",
            "task_id": task_id,
            "req_json": "{\"logo_info\":{\"add_logo\":true,\"position\":0,\"language\":0,\"opacity\":0.3,\"logo_text_content\":\"这里是明水印内容\"},\"return_url\":true}"
        })
        if result['code'] != 10000:
            print(result.get('message', 'Unknown error'))
            return None
        if result.get('data', {}).get('image_urls'):
            return result.get('data', {}).get('image_urls')[0]
        time.sleep(5)