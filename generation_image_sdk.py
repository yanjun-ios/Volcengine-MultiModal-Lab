# coding:utf-8
from __future__ import print_function
import time
import base64
import os
import json
from volcengine.visual.VisualService import VisualService
from volcenginesdkarkruntime import Ark

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

# 方舟 文生图 3.0
def ark_t2i(ark_client,model="doubao-seedream-3-0-t2i-250415",prompt="",size="1024x1024",seed=-1,guidance_scale=2.5,watermark=True):
    imagesResponse = ark_client.images.generate(
        model=model,
        prompt=prompt,
        response_format="url",
        size=size,
        seed=seed,
        guidance_scale=guidance_scale,
        watermark=watermark
    )

    if imagesResponse.data[0].url:
        return imagesResponse.data[0].url

# 方舟 图像编辑 3.0
def ark_i2i(ark_client,model="doubao-seededit-3-0-i2i-250628",prompt="",image="",seed=-1,guidance_scale=5.5,watermark=True):
    imagesResponse = ark_client.images.generate(
        model=model,
        prompt=prompt,
        image=image,
        response_format="url",
        size="adaptive",
        seed=seed,
        guidance_scale=guidance_scale,
        watermark=watermark
    )
    if imagesResponse.data[0].url:
        return imagesResponse.data[0].url

# 既梦 AI 图像生成
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

# 文生视频 [doubao-seedance-1-0-pro-250528,doubao-seedance-1-0-lite-t2v-250428]
def t2v_seedance(ark_client, model, prompt):
    resp = ark_client.content_generation.tasks.create(
        model=model,
        content=[{"text": prompt, "type": "text"}]
    )
    print(resp)
    if resp.id:
        while True:
            result = ark_client.content_generation.tasks.get(
                task_id=resp.id,
            )
            print(f"Task status: {result.status}")
            if result.status == 'failed':
                print(f"Task failed: {getattr(result, 'message', 'Unknown error')}")
                return None
            if result.status == 'succeeded' and hasattr(result, 'content') and hasattr(result.content, 'video_url'):
                return result.content.video_url
            time.sleep(5)


# 图生视频 [doubao-seedance-1-0-pro-250528,doubao-seedance-1-0-lite-i2v-250428]
def i2v_seedance(ark_client, model, prompt, first_frame=None, last_frame=None):
    content = [{"type": "text", "text": prompt}]
    if first_frame:
        content.append({"type": "image_url", "role": "first_frame", "image_url": {"url": first_frame}})
    if last_frame:
        content.append({"type": "image_url", "role": "last_frame", "image_url": {"url": last_frame}})
    
    resp = ark_client.content_generation.tasks.create(
        model=model,
        content=content
    )

    if resp.id:
        while True:
            result = ark_client.content_generation.tasks.get(
                task_id=resp.id,
            )
            print(f"Task status: {result.status}")
            if result.status == 'failed':
                print(f"Task failed: {getattr(result, 'message', 'Unknown error')}")
                return None
            if result.status == 'succeeded' and hasattr(result, 'content') and hasattr(result.content, 'video_url'):
                return result.content.video_url
            time.sleep(5)