# coding:utf-8
"""
火山引擎 Visual 视频生成相关API
"""
from __future__ import print_function
import time
import base64
import os
import json
from volcengine.visual.VisualService import VisualService

# 视频生成 - 视频特效
def template_2_video(visual_service, image_input, template_id):
    print(f"image_input:{image_input}, template_id:{template_id}")
    form = {
        "req_key": "i2v_bytedance_effects_v1",
        "image_input": image_input,
        "template_id": template_id
    }

    resp = visual_service.cv_sync2async_submit_task(form)
    if resp['code'] != 10000:
        print(resp.get('message', 'Unknown error'))
        return None

    task_id = resp['data']['task_id']
    while True:
        result = visual_service.cv_sync2async_get_result({
            "req_key": "i2v_bytedance_effects_v1",
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