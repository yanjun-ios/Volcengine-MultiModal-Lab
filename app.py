import base64
import os
import tos
import json
from tos import GranteeType, CannedType, PermissionType
from tos.models2 import Grantee, Grant, Owner
import time
import streamlit as st
# 从新的API模块导入函数
from api_modules.visual_image import t2i_30, i2i_30_portrait, i2i_seed_edit_30, i2i_30_single_ip, i21_multi_style, omni_human_pre_test, omni_human
from api_modules.visual_video import template_2_video
from api_modules.jimeng_image import t2i_jimeng, i2i_jimeng_v30
from api_modules.jimeng_video import t2v_jimeng_s20_pro, i2v_jimeng_s20_pro
from api_modules.ark_image import ark_t2i, ark_i2i
from api_modules.ark_video import t2v_seedance, i2v_seedance
from api_modules.generation_music import generation_bgm
from volcengine.visual.VisualService import VisualService
from volcenginesdkarkruntime import Ark
from byteplussdkarkruntime import Ark as Byteplus_Ark
from utils.llm_prompt_optmize import optimize_stream
from dotenv import load_dotenv
import requests
import tempfile

# 导入页面组件
from components.sidebar import render_sidebar
from utils.page_router import route_page

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Volcengine MultiModal Lab", page_icon="🎨", layout="wide")

# upload_to_tos 函数已移动到 utils/tos_utils.py 中

@st.cache_resource
def set_auth():
    ak = os.environ.get("VOLC_ACCESSKEY", "")
    sk = os.environ.get("VOLC_SECRETKEY", "")
    api_key = os.environ.get("VOLCENGINE_API_KEY", "")
    st.session_state.ak = ak
    st.session_state.sk = sk
    st.session_state.api_key = api_key

@st.cache_resource
def get_visual_service():
    # It's recommended to use environment variables for AK and SK
    ak = os.environ.get("VOLC_ACCESSKEY", "")
    sk = os.environ.get("VOLC_SECRETKEY", "")
    visual_service = VisualService()
    visual_service.set_ak(ak)
    visual_service.set_sk(sk)
    return visual_service

@st.cache_resource
def get_ark_client():
    # 检查是否启用了 Byteplus Model Ark
    byteplus_enabled = st.session_state.get("byteplus_ark_enabled", False)
    
    if byteplus_enabled:
        # 使用 Byteplus Model Ark
        model_ark_api_key = os.environ.get("MODEL_ARK_API_KEY", "")
        if model_ark_api_key:
            return Byteplus_Ark(api_key=model_ark_api_key)
        else:
            st.error("❌ Byteplus Model Ark 已启用但未配置 MODEL_ARK_API_KEY")
            return None
    else:
        # 使用默认的 Volcengine Ark
        api_key = os.environ.get("VOLCENGINE_API_KEY", "")
        return Ark(api_key=api_key)

# 初始化设置
set_auth()

# 初始化服务实例到 session_state
if 'visual_service' not in st.session_state:
    st.session_state.visual_service = get_visual_service()
if 'ark_client' not in st.session_state:
    st.session_state.ark_client = get_ark_client()

# 检查是否需要重新初始化 Ark 客户端
if st.session_state.get("need_reinit_ark", False):
    # 清除缓存并重新初始化
    st.cache_resource.clear()
    st.session_state.ark_client = get_ark_client()
    # 清除标志
    st.session_state.need_reinit_ark = False

# 从 session_state 获取服务实例
visual_service = st.session_state.visual_service
ark_client = st.session_state.ark_client

st.title("火山引擎 - AI多模态体验中心")

# 渲染侧边栏并获取选中的功能
selected_function = render_sidebar()

# 使用页面路由器渲染对应页面
route_page(selected_function, visual_service, ark_client)