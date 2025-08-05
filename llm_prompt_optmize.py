# coding:utf-8
import os
import time
from volcenginesdkarkruntime import Ark

# 优化提示词 - 支持流式返回
def optimize_stream(client,type="i2v", user_prompt="", user_image=""):
    """
    优化提示词，返回生成器用于流式输出
    """
    system_prompt = ""
    prompt_file=""
    if type == 'i2v':
        prompt_file = "i2v_prompt_guaidance.md"
    elif type == 't2v':
        prompt_file = "t2v_prompt_guaidance.md"
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        # 将{{user_prompt}}变量替换成 user_prompt
        system_prompt = system_prompt.replace('{{user_prompt}}', user_prompt)
    except FileNotFoundError:
        yield "错误：找不到 t2v_prompt_guaidance.md 文件"
        return
    except Exception as e:
        yield f"读取文件时出错：{e}"
        return

    try:
        # 构建消息内容
        message_content = [{"text": system_prompt, "type": "text"}]
        if user_image:
            message_content.insert(0, {"image_url": {"url": user_image}, "type": "image_url"})

        stream = client.chat.completions.create(
            model="doubao-seed-1-6-250615",
            messages=[
                {"content": message_content, "role": "user"}
            ],
            extra_headers={'x-is-encrypted': 'true'},
            temperature=0,
            top_p=0.7,
            max_tokens=4096,
            frequency_penalty=0,
            stream=True,
            thinking={"type": "disabled"}
        )
        
        for chunk in stream:
            if not chunk.choices:
                continue
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        yield f"优化提示词时出错：{e}"

# 优化提示词 - 返回完整结果
def optimize(type="t2v", user_prompt="", user_image=""):
    """
    优化提示词，返回完整的优化结果
    """
    result = ""
    for chunk in optimize_stream(type, user_prompt, user_image):
        result += chunk
    return result