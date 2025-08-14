# coding:utf-8
"""
方舟 图像生成相关API
"""
from __future__ import print_function
import time
import base64
import os
import json
from volcenginesdkarkruntime import Ark

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