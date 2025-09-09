import streamlit as st
from page_modules.t2i_general import render_t2i_general
from page_modules.i2i_portrait import render_i2i_portrait
from page_modules.i2i_edit import render_i2i_edit
from page_modules.i2i_character import render_i2i_character
from page_modules.image_effects import render_image_effects
from page_modules.ark_t2i import render_ark_t2i
from page_modules.ark_i2i import render_ark_i2i
from page_modules.ark_seedream_40 import render_ark_seedream_40
from page_modules.jimeng_t2i import render_jimeng_t2i_21
from page_modules.jimeng_t2i_v30 import render_jimeng_t2i_v30
from page_modules.jimeng_t2i_v31 import render_jimeng_t2i_v31
from page_modules.jimeng_i2i import render_jimeng_i2i_30
from page_modules.t2v_seedance import render_t2v_seedance
from page_modules.music_generation import render_music_generation
from page_modules.i2v_seedance import render_i2v_seedance
from page_modules.jimeng_t2v import render_jimeng_t2v
from page_modules.jimeng_i2v import render_jimeng_i2v
from page_modules.video_effects import render_video_effects
from page_modules.omni_human import render_omni_human
from page_modules.tts import render_tts
from page_modules.settings import render_settings
from utils.tos_utils import upload_to_tos

def route_page(selected_function, visual_service, ark_client):
    """根据选中的功能路由到对应的页面"""
    
    if selected_function == "通用3.0-文生图":
        render_t2i_general(visual_service)
        
    elif selected_function == "图生图3.0-人像写真":
        render_i2i_portrait(visual_service)
        
    elif selected_function == "图生图3.0-指令编辑":
        render_i2i_edit(visual_service)
        
    elif selected_function == "设置":
        render_settings()
        
    elif selected_function == "图生图3.0-角色特征保持":
        render_i2i_character(visual_service)
        
    elif selected_function == "智能绘图 - 图像特效":
        render_image_effects(visual_service, upload_to_tos)
        
    elif selected_function == "方舟-文生图3.0":
        render_ark_t2i(ark_client)
        
    elif selected_function == "方舟-图像编辑3.0":
        render_ark_i2i(ark_client)
        
    elif selected_function == "方舟-SeedDream4.0":
        render_ark_seedream_40(ark_client)
        
    elif selected_function == "既梦AI-文生图2.1":
        render_jimeng_t2i_21(visual_service)
        
    elif selected_function == "既梦AI-文生图3.0":
        render_jimeng_t2i_v30(visual_service)  # 使用同一个函数
        
    elif selected_function == "既梦AI-文生图3.1":
        render_jimeng_t2i_v31(visual_service)  # 使用同一个函数
        
    elif selected_function == "既梦AI-图生图3.0":
        render_jimeng_i2i_30(visual_service)
        
    elif selected_function == "文生视频":
        render_t2v_seedance(ark_client)
        
    elif selected_function == "图生视频":
        render_i2v_seedance(ark_client)
        
    elif selected_function == "既梦AI-文生视频":
        render_jimeng_t2v(visual_service)
        
    elif selected_function == "既梦AI-图生视频":
        render_jimeng_i2v(visual_service)
        
    elif selected_function == "视频生成-视频特效":
        render_video_effects(visual_service, upload_to_tos)
        
    elif selected_function == "音乐生成":
        render_music_generation()
        
    elif selected_function == "TTS":
        render_tts()
        
    elif selected_function == "数字人(Omni_Human)":
        render_omni_human(visual_service, upload_to_tos)
        
    else:
        # 对于未实现的功能，显示开发中提示
        st.header(f"{selected_function}")
        st.info("💡 该功能正在开发中，敬请期待！")
        st.markdown("---")