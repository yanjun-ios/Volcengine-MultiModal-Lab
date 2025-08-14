# coding:utf-8
"""
方舟 视频生成相关API
"""
from __future__ import print_function
import time
import base64
import os
import json
from volcenginesdkarkruntime import Ark

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