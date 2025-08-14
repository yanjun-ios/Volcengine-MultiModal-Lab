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