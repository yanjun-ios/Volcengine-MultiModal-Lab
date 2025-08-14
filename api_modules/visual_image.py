# coding:utf-8
"""
火山引擎 Visual 图像生成相关API
"""
from __future__ import print_function
import time
import base64
import os
import json
from volcengine.visual.VisualService import VisualService

# 通用 3.0 - 文生图
def t2i_30(visual_service, prompt, seed=-1, scale=2.5, width=1328, height=1328, return_url=True):
    form = {
        "req_key": "high_aes_general_v30l_zt2i",
        "prompt": prompt,
        "seed": seed,
        "scale": scale,
        "width": width,
        "height": height,
        "return_url": return_url,
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

# 图生图 3.0 - 人像写真
def i2i_30_portrait(visual_service, image_url, prompt, seed=-1, width=1024, height=1024, gen_mode="creative"):
    form = {
        "req_key": "i2i_portrait_photo",
        "image_input": image_url,
        "prompt": prompt,
        "gpen": 0.4,
        "skin": 0.3,
        "skin_unifi": 0,
        "width": width,
        "height": height,
        "gen_mode": gen_mode,
        "seed": seed
    }
    resp = visual_service.cv_sync2async_submit_task(form)
    task_id = resp['data']['task_id']
    output_path = 'i2i_portrait_photo_output.png'
    while True:
        result = visual_service.cv_sync2async_get_result({
            "req_key": "i2i_portrait_photo",
            "task_id": task_id,
            "req_json": "{\"logo_info\":{\"add_logo\":true,\"position\":0,\"language\":0,\"opacity\":0.3,\"logo_text_content\":\"这里是明水印内容\"},\"return_url\":true}"
        })
        if result['code'] != 10000:
            print(result.get('message', 'Unknown error'))
            return None
        if result.get('data', {}).get('image_urls'):
            return result.get('data', {}).get('image_urls')[0]
        time.sleep(5)

# 图生图 3.0 - 指令编辑
def i2i_seed_edit_30(visual_service, prompt, seed=-1, scale=0.5, image_url=None, image_base64=None):
    if not image_url and not image_base64:
        raise ValueError("Either image_url or image_base64 must be provided")

    form = {
        "req_key": "seededit_v3.0",
        "prompt": prompt,
        "seed": seed,
        "scale": scale
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
    output_path = 'seededit_v3.0_output.png'
    while True:
        result = visual_service.cv_sync2async_get_result({
            "req_key": "seededit_v3.0",
            "task_id": task_id,
            "req_json": "{\"logo_info\":{\"add_logo\":true,\"position\":0,\"language\":0,\"opacity\":0.3,\"logo_text_content\":\"这里是明水印内容\"},\"return_url\":true}"
        })
        if result['code'] != 10000:
            print(result.get('message', 'Unknown error'))
            return None
        if result.get('data', {}).get('image_urls'):
            return result.get('data', {}).get('image_urls')[0]
        time.sleep(5)

# 图生图 3.0 - 角色特征保持 DreamO
def i2i_30_single_ip(visual_service, prompt, seed=-1, width=1024, height=1024, image_url=None, image_base64=None,use_rephraser=True):
    if not image_url and not image_base64:
        raise ValueError("Either image_url or image_base64 must be provided")

    form = {
        "req_key": "seed3l_single_ip",
        "prompt": prompt,
        "seed": seed,
        "width": width,
        "height":height,
        "use_rephraser":use_rephraser
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
            "req_key": "seed3l_single_ip",
            "task_id": task_id,
            "req_json": "{\"logo_info\":{\"add_logo\":true,\"position\":0,\"language\":0,\"opacity\":0.3,\"logo_text_content\":\"这里是明水印内容\"},\"return_url\":true}"
        })
        if result['code'] != 10000:
            print(result.get('message', 'Unknown error'))
            return None
        if result.get('data', {}).get('image_urls'):
            return result.get('data', {}).get('image_urls')[0]
        time.sleep(5)

# 智能绘图 - 图像特效
def i21_multi_style(visual_service, image_url=None, image_base64=None, template_id="felt_3d_polaroid", width=1024, height=1024):
    if not image_url and not image_base64:
        raise ValueError("Either image_url or image_base64 must be provided")

    form = {
        "req_key": "i2i_multi_style_zx2x",
        "template_id": template_id,
        "width": width,
        "height": height
    }

    if image_url:
        form["image_input1"] = image_url
    elif image_base64:
        form["binary_data_base64"] = [image_base64]

    resp = visual_service.cv_sync2async_submit_task(form)
    if resp['code'] != 10000:
        print(resp.get('message', 'Unknown error'))
        return None

    task_id = resp['data']['task_id']
    while True:
        result = visual_service.cv_sync2async_get_result({
            "req_key": "i2i_multi_style_zx2x",
            "task_id": task_id,
            "req_json": "{\"logo_info\":{\"add_logo\":true,\"position\":0,\"language\":0,\"opacity\":0.3,\"logo_text_content\":\"这里是明水印内容\"},\"return_url\":true}"
        })
        if result['code'] != 10000:
            print(result.get('message', 'Unknown error'))
            return None
        if result.get('data', {}).get('image_urls'):
            return result.get('data', {}).get('image_urls')[0]
        time.sleep(5)

# 数字人前置检查
def omni_human_pre_test(visual_service,image_url):
    form = {
        "req_key": "realman_avatar_picture_create_role_omni",
        "image_url": image_url,
    }
    resp = visual_service.cv_submit_task(form)
    if resp['code'] != 10000:
        print(resp.get('message', 'Unknown error'))
        return None

    task_id = resp['data']['task_id']
    while True:
        result = visual_service.cv_get_result({
            "req_key": "realman_avatar_picture_create_role_omni",
            "task_id": task_id
        })
        print(f"{result} \n")
        if result['code'] != 10000:
            print(result.get('message', 'Unknown error'))
            return None
        if result.get('data', {}).get('status') == "done":
            resp_data = json.loads(result.get('data').get('resp_data'))
            return resp_data.get("status")
        time.sleep(3)

# OmniHuman 数字人生成
def omni_human(visual_service,image_url,audio_url):
    if not image_url and not audio_url:
        raise ValueError("Either image_url and audio_url must be provided")

    form = {
        "req_key": "realman_avatar_picture_omni_v2",
        "image_url": image_url,
        "audio_url": audio_url
    }

    resp = visual_service.cv_submit_task(form)
    if resp['code'] != 10000:
        print(resp.get('message', 'Unknown error'))
        return None

    task_id = resp['data']['task_id']
    while True:
        result = visual_service.cv_get_result({
            "req_key": "realman_avatar_picture_omni_v2",
            "task_id": task_id
        })
        print(f"{result} \n")
        if result['code'] != 10000:
            print(result.get('message', 'Unknown error'))
            return None
        if result.get('data', {}).get('status') == "done":
            resp_data = json.loads(result.get('data').get('resp_data'))
            return resp_data.get('video_url')
        time.sleep(5)