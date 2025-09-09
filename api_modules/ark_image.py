# coding:utf-8
"""
方舟 图像生成相关API
"""
from __future__ import print_function
import time
import base64
import os
import json
import requests
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

def ark_seedream_40(ark_client, model="doubao-seedream-4-0-250828", prompt="", image=[], size="2K", seed=-1, sequential_image_generation="auto", max_images=4, stream=False, guidance_scale=5.5, watermark=True):
    """
    方舟 SeedDream 4.0 图像生成
    """
    # 从环境变量读取API密钥
    from dotenv import load_dotenv
    load_dotenv()
    
    ark_api_key = os.getenv('VOLCENGINE_API_KEY')
    if not ark_api_key:
        raise ValueError("VOLCENGINE_API_KEY not found in environment variables")
    
    # 构建请求数据
    data = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "sequential_image_generation": sequential_image_generation,
        "stream": stream,
        "watermark": watermark
    }
    
    # 添加可选参数
    if seed != -1:
        data["seed"] = seed
    if guidance_scale != 5.5:
        data["guidance_scale"] = guidance_scale
    
    # 处理sequential_image_generation相关参数
    if sequential_image_generation == "auto":
        data["sequential_image_generation_options"] = {"max_images": max_images}
    
    # 处理image参数 - 可能是字符串或字符串数组
    if image:
        if isinstance(image, list) and len(image) == 1:
            data["image"] = image[0]  # 单张图片传字符串
        elif image:
            data["image"] = image  # 多张图片或非空字符串
    
    # 设置请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ark_api_key}"
    }
    
    try:
        # 发送POST请求
        response = requests.post(
            "https://ark.cn-beijing.volces.com/api/v3/images/generations",
            headers=headers,
            json=data,
            timeout=600,
            stream=stream  # 启用流式响应
        )
        
        # 检查响应状态
        response.raise_for_status()
        
        if stream:
            # 返回响应对象供前端处理流式数据
            return response
        else:
            # 处理非流式响应
            result = response.json()
            print(result)
            
            # 返回生成的图像URL
            if result.get('data') and len(result['data']) > 0:
                return result['data']
            else:
                return None
                
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse response JSON: {e}")
        return None