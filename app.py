import base64
import os
import tos
import json
from tos import GranteeType, CannedType, PermissionType
from tos.models2 import Grantee, Grant, Owner
import time
import streamlit as st
from generation_image_sdk import t2i_30, i2i_30_portrait, i2i_seed_edit_30, t2v_seedance, i2v_seedance, i2i_30_single_ip, ark_t2i, ark_i2i, t2i_jimeng, i2i_jimeng_v30, t2v_jimeng_s20_pro, i2v_jimeng_s20_pro, omni_human_pre_test, omni_human, i21_multi_style, template_2_video
from generation_music import generation_bgm
from volcengine.visual.VisualService import VisualService
from volcenginesdkarkruntime import Ark
from llm_prompt_optmize import optimize_stream
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Volcengine MultiModal Lab", page_icon="🎨", layout="wide")

def upload_to_tos(object_key, content, bucket_name=None):
    ak = os.environ.get("VOLC_ACCESSKEY", "")
    sk = os.environ.get("VOLC_SECRETKEY", "")
    region = os.environ.get("region", "cn-beijing")
    bucket_name = os.environ.get("TOS_BUCKET_NAME", "default-bucket")
    endpoint = f"tos-{region}.volces.com"
    try:
        client = tos.TosClientV2(ak, sk, endpoint, region)
        # 上传
        result = client.put_object(bucket_name, object_key, content=content)

        client.put_object_acl(bucket_name, object_key, acl=tos.ACLType.ACL_Public_Read)
        
        url = f"https://{bucket_name}.{endpoint}/{object_key}"
        print(f"Successfully uploaded to TOS {url}")
        return url
    except Exception as e:
        print('upload file to tos fail with error: {}'.format(e))
        return None


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
    visual_service = VisualService()
    visual_service.set_ak(st.session_state.ak)
    visual_service.set_sk(st.session_state.sk)
    return visual_service

@st.cache_resource
def get_ark_client():
    return Ark(api_key=st.session_state.api_key)

# 初始化设置
set_auth()

# 初始化服务实例到 session_state
if 'visual_service' not in st.session_state:
    st.session_state.visual_service = get_visual_service()
if 'ark_client' not in st.session_state:
    st.session_state.ark_client = get_ark_client()

# 从 session_state 获取服务实例
visual_service = st.session_state.visual_service
ark_client = st.session_state.ark_client

st.title("火山引擎 - AI多模态体验中心")

# 自定义CSS样式 - 简约现代化左侧菜单
st.markdown("""
<style>
/* 侧边栏整体样式 */
.css-1d391kg {
    background-color: #f8f9fa;
    padding-top: 1rem;
}

/* 隐藏默认按钮样式 */
.stButton > button {
    background: transparent !important;
    border: none !important;
    padding: 8px 16px !important;
    color: #495057 !important;
    text-decoration: none !important;
    height: auto !important;
    width: 100% !important;
    text-align: left !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    border-radius: 6px !important;
    margin: 2px 0 !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
}

.stButton > button:hover {
    background-color: #e9ecef !important;
    color: #212529 !important;
}

.stButton > button:focus {
    background-color: #e9ecef !important;
    color: #212529 !important;
    box-shadow: none !important;
}

[data-testid="stSidebarContent"] div[data-testid="stMarkdownContainer"] {
    width: 100%;
    text-align: left;
}

/* 菜单分组样式 */
.menu-group {
    margin: 10px 0 10px 0;
    padding: 0 16px;
    font-size: 12px;
    font-weight: 600;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* 分割线样式 */
.menu-divider {
    height: 1px;
    background-color: #dee2e6;
    margin: 12px 16px;
    border: none;
}

/* 侧边栏标题 */
.sidebar-title {
    font-size: 18px;
    font-weight: 600;
    color: #212529;
    text-align: center;
    margin-bottom: 24px;
    padding: 0 16px;
}
</style>
""", unsafe_allow_html=True)

# 使用侧边栏菜单选择功能模块
st.sidebar.markdown('<div class="sidebar-title">功能菜单</div>', unsafe_allow_html=True)

# 初始化选中状态
if 'selected_function' not in st.session_state:
    st.session_state.selected_function = "通用3.0-文生图"

# 图像生成菜单
image_generation_menu = [
    "通用3.0-文生图",
    "图生图3.0-人像写真", 
    "图生图3.0-指令编辑",
    "图生图3.0-角色特征保持",
    "智能绘图 - 图像特效",
    "方舟-文生图3.0",
    "方舟-图像编辑3.0",
    "既梦AI-文生图2.1",
    "既梦AI-文生图3.0",
    "既梦AI-文生图3.1",
    "既梦AI-图生图3.0"
]

# 视频生成菜单
video_generation_menu = [
    "文生视频",
    "图生视频",
    "既梦AI-文生视频",
    "既梦AI-图生视频",
    "视频生成-视频特效",
]

# 其他
others_menu = [
    "TTS",
    "音乐生成",
    "数字人(Omni_Human)"
]

# 添加分组标题
st.sidebar.markdown('<div class="menu-group">图片生成</div>', unsafe_allow_html=True)

# 图片生成菜单
for im in image_generation_menu:
    if st.sidebar.button(im, key=f"menu_{im}"):
        st.session_state.selected_function = im
        st.rerun()

# 分割线
st.sidebar.markdown('<hr class="menu-divider">', unsafe_allow_html=True)
# 视频生成分组
st.sidebar.markdown('<div class="menu-group">视频生成</div>', unsafe_allow_html=True)

# 视频生成菜单
for vm in video_generation_menu:
    if st.sidebar.button(vm, key=f"menu_{vm}"):
        st.session_state.selected_function = vm
        st.rerun()
# 分割线
st.sidebar.markdown('<hr class="menu-divider">', unsafe_allow_html=True)
# 其他生成分组
st.sidebar.markdown('<div class="menu-group">其他</div>', unsafe_allow_html=True)
# 其他生成菜单
for om in others_menu:
    if st.sidebar.button(om, key=f"menu_{om}"):
        st.session_state.selected_function = om
        st.rerun()
# 分割线
st.sidebar.markdown('<hr class="menu-divider">', unsafe_allow_html=True)

# 设置按钮
st.sidebar.markdown('<div class="menu-group">系统设置</div>', unsafe_allow_html=True)
if st.sidebar.button("⚙️ 设置", key="settings_button"):
    st.session_state.selected_function = "设置"
    st.rerun()

selected_function = st.session_state.selected_function

if selected_function == "通用3.0-文生图":
    st.header("通用3.0-文生图")
    st.markdown("提示词秘籍:https://bytedance.larkoffice.com/docx/DUAJdq59Zo9GQAx4KZ4c2DP9noc?from=from_copylink")
    st.markdown("接口文档:https://www.volcengine.com/docs/85128/1526761")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("输入参数")
        prompt_t2i = st.text_area("输入文生图提示词:", "千军万马", height=100, key="prompt_t2i")
        seed_t2i = st.number_input("Seed", value=-1, key="seed_t2i")
        scale_t2i = st.slider("Scale", min_value=0.0, max_value=10.0, value=2.5, step=0.1, key="scale_t2i")
        width_t2i = st.number_input("Width", value=1328, key="width_t2i")
        height_t2i = st.number_input("Height", value=1328, key="height_t2i")
        return_url_t2i = st.checkbox("Return URL", value=True, key="return_url_t2i")
        generate_button_t2i = st.button("生成图片", key="button_t2i")

    with col2:
        st.subheader("生成结果")
        if generate_button_t2i:
            with st.spinner("Generating..."):
                image_url = t2i_30(visual_service, prompt_t2i, seed_t2i, scale_t2i, width_t2i, height_t2i, return_url_t2i)
                if image_url:
                    st.image(image_url, caption="Generated Image")

elif selected_function == "图生图3.0-人像写真":
    st.header("图生图3.0-人像写真")
    st.markdown("接口文档:https://www.volcengine.com/docs/85128/1602212")
    style_presets = {
        "美漫": "美式漫画风格，2D，平面插画，漫画，有力的线条，复古色彩",
        "赛博朋克": "赛博朋克风格写实照片，人物穿着机甲风格的夹克外套，背景是赛博朋克风格的霓虹城市",
        "异域风情": "异域沙漠服饰装扮，异域的头饰，背景是异域的沙漠绿洲和建筑，发丝细腻刻画，高清特写，极致细节，光影交错，气质，oc渲染，朦胧，肌理感，3D CG渲染，3d动漫厚涂，发丝细腻刻画富有光泽，光影交错，光影对比强烈，光影斑斓，3d动漫风格",
        "模糊自拍-路飞cos": "一张极其平凡无奇的iphone自拍照，没有明确的主体或构图感，画面有些拿不稳的动态模糊，正在角色扮演的路飞coser，带着草帽",
        "未来感美漫": "3D美漫角色正面半身照，80年代复古美漫，波普，厚涂，穿着运动感的数字时装廓形外套，单色随机荧光亮色配色，蒸汽波和赛博朋克的结合，超现实，高细节，超精细数字插画，电影照明，ArtStation 质量，带深度的黑色渐变背景，",
        "高级感写真": "极致光影的室内摄影，大师构图，反差感，黑色背景，极简，解构，远景，索尼胶片，电影感，人像摄影，艺术摄影，荒木经椎，弥散光学，明暗对比，优雅动态角度，高级感，高清修复，脸部特写，头部特写，肖像，正面，极致侧面特写，正脸，眼神暗示，流动光影，一缕光照在脸上，迷幻主义，细节生动，杰作，艺术氛围感，",
        "赛场上": "高精度建模渲染，脸被淡淡的渐变粉灰色光照亮，梦幻，真实的皮肤纹理，细节丰富的发丝，布满水珠的皮肤，氛围感，2K，大师级光影，层次感，立体感，极致的光线，发丝细腻，王家卫电影胶片颗粒质感 ，柔焦，高斯模糊，明暗交错，虚实结合的构图张力，双色温闪光灯布光，背景光斑虚化处理，动态范围，彩色光斑，穿着10号球衣",
    }
    styles = list(style_presets.keys())

    # Callback to update prompt in session state
    def update_prompt_from_style():
        st.session_state.prompt_i2i = style_presets[st.session_state.style_selector]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("输入参数")
        image_url_i2i = st.text_input("Enter an image URL for image-to-image generation:", "https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_bada876d0cb71c5598a6e0885f14c83c.png", key="image_url_i2i")
        
        # Set default prompt if not in state
        if 'prompt_i2i' not in st.session_state:
            st.session_state.prompt_i2i = style_presets[styles[0]]

        selected_style = st.selectbox(
            "选择风格类型",
            options=styles,
            key="style_selector",
            on_change=update_prompt_from_style
        )
        
        # The text area uses the session state.
        prompt_i2i = st.text_area("输入人像写真提示词:", key="prompt_i2i", height=100)
        
        seed_i2i = st.number_input("Seed", value=-1, key="seed_i2i")
        width_i2i = st.number_input("Width", value=1024, key="width_i2i")
        height_i2i = st.number_input("Height", value=1024, key="height_i2i")
        gen_mode_i2i = st.selectbox("Generation Mode", ["creative","reference","reference_char"], key="gen_mode_i2i")
        generate_button_i2i = st.button("生成图片", key="button_i2i")

    with col2:
        st.subheader("图片预览和生成结果")
        preview_col, result_col = st.columns(2)
        with preview_col:
            if image_url_i2i:
                st.image(image_url_i2i, caption="图片预览")
        
        with result_col:
            if generate_button_i2i:
                with st.spinner("Generating..."):
                    # The value from the text_input is in prompt_i2i
                    img_url = i2i_30_portrait(visual_service, image_url_i2i, prompt_i2i, seed_i2i, width_i2i, height_i2i, gen_mode_i2i)
                    if img_url:
                        st.image(img_url, caption="Generated Image")

elif selected_function == "图生图3.0-指令编辑":
    st.header("图生图3.0-指令编辑")
    st.markdown("接口文档:https://www.volcengine.com/docs/85128/1602254")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("输入参数")
        input_method = st.radio("选择图片来源", ("URL", "上传图片"), key="input_method_edit")
        image_url_edit = None
        uploaded_file = None

        if input_method == "URL":
            image_url_edit = st.text_input("输入图片 URL:", "https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_b9d0ea6bb4528cce79517a7c706ad1b7.png", key="image_url_edit")
        else:
            uploaded_file = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"], key="file_uploader_edit")

        prompt_edit = st.text_area("输入编辑指令:", "将小女孩的衣服换成白色的公主裙", height=100, key="prompt_edit")
        seed_edit = st.number_input("Seed", value=-1, key="seed_edit")
        scale_edit = st.slider("Scale", min_value=0.0, max_value=1.0, value=0.5, step=0.1, key="scale_edit")
        generate_button_edit = st.button("开始编辑", key="button_edit")

    with col2:
        st.subheader("图片预览和编辑结果")
        preview_col, result_col = st.columns(2)

        with preview_col:
            preview_image = None
            if input_method == "URL" and image_url_edit:
                preview_image = image_url_edit
            elif input_method == "上传图片" and uploaded_file is not None:
                preview_image = uploaded_file
            
            if preview_image is not None:
                st.image(preview_image, caption="图片预览")

        with result_col:
            if generate_button_edit:
                with st.spinner("正在编辑中..."):
                    img_url = None
                    if input_method == "URL":
                        if image_url_edit:
                            img_url = i2i_seed_edit_30(visual_service, prompt=prompt_edit, seed=seed_edit, scale=scale_edit, image_url=image_url_edit)
                    elif input_method == "上传图片":
                        if uploaded_file is not None:
                            image_base64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                            img_url = i2i_seed_edit_30(visual_service, prompt=prompt_edit, seed=seed_edit, scale=scale_edit, image_base64=image_base64)
                    
                    if img_url:
                        st.image(img_url, caption="编辑后图片")

elif selected_function == "图生图3.0-角色特征保持":
    st.header("图生图3.0-角色特征保持 DreamO")
    st.markdown("接口文档:https://www.volcengine.com/docs/85128/1722713")
    st.markdown("💡 DreamO模型可以保持角色特征，生成不同场景下的同一角色图片")
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("输入参数")
        input_method_dreamo = st.radio("选择图片来源", ("URL", "上传图片"), key="input_method_dreamo")
        image_url_dreamo = None
        uploaded_file_dreamo = None

        if input_method_dreamo == "URL":
            image_url_dreamo = st.text_input(
                "输入角色图片 URL:", 
                "https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_bada876d0cb71c5598a6e0885f14c83c.png", 
                key="image_url_dreamo"
            )
        else:
            uploaded_file_dreamo = st.file_uploader(
                "上传角色图片", 
                type=["png", "jpg", "jpeg"], 
                key="file_uploader_dreamo"
            )

        prompt_dreamo = st.text_area(
            "输入生成提示词:", 
            "衣服换成西装，带上暗灰色的墨镜，头发变成板栗色",
            height=100,
            key="prompt_dreamo"
        )
        
        seed_dreamo = st.number_input("Seed", value=-1, key="seed_dreamo")
        width_dreamo = st.number_input("Width", value=1024, key="width_dreamo")
        height_dreamo = st.number_input("Height", value=1024, key="height_dreamo")
        use_rephraser_dreamo = st.checkbox("使用提示词优化", value=True, key="use_rephraser_dreamo")
        
        generate_button_dreamo = st.button("生成角色图片", key="button_dreamo")

    with col2:
        st.subheader("图片预览和生成结果")
        preview_col, result_col = st.columns(2)

        with preview_col:
            st.write("**角色图片预览**")
            preview_image_dreamo = None
            if input_method_dreamo == "URL" and image_url_dreamo:
                preview_image_dreamo = image_url_dreamo
            elif input_method_dreamo == "上传图片" and uploaded_file_dreamo is not None:
                preview_image_dreamo = uploaded_file_dreamo
            
            if preview_image_dreamo is not None:
                st.image(preview_image_dreamo, caption="角色参考图片")
            else:
                st.info("请上传或输入角色图片")

        with result_col:
            st.write("**生成结果**")
            if generate_button_dreamo:
                if (input_method_dreamo == "URL" and not image_url_dreamo) or \
                   (input_method_dreamo == "上传图片" and uploaded_file_dreamo is None):
                    st.error("请先上传角色图片或输入图片URL！")
                else:
                    with st.spinner("正在生成角色特征保持图片..."):
                        try:
                            img_url = None
                            if input_method_dreamo == "URL":
                                img_url = i2i_30_single_ip(
                                    visual_service, 
                                    prompt=prompt_dreamo, 
                                    seed=seed_dreamo, 
                                    width=width_dreamo,
                                    height=height_dreamo,
                                    image_url=image_url_dreamo,
                                    use_rephraser=use_rephraser_dreamo
                                )
                            elif input_method_dreamo == "上传图片":
                                image_base64_dreamo = base64.b64encode(uploaded_file_dreamo.getvalue()).decode('utf-8')
                                img_url = i2i_30_single_ip(
                                    visual_service, 
                                    prompt=prompt_dreamo, 
                                    seed=seed_dreamo, 
                                    width=width_dreamo,
                                    height=height_dreamo,
                                    image_base64=image_base64_dreamo,
                                    use_rephraser=use_rephraser_dreamo
                                )
                            
                            if img_url:
                                st.image(img_url, caption="角色特征保持生成图片")
                                st.success("角色特征保持图片生成成功！")
                            else:
                                st.error("图片生成失败，请检查参数或稍后重试")
                                
                        except Exception as e:
                            st.error(f"生成图片时出错: {str(e)}")

elif selected_function == "智能绘图 - 图像特效":
    st.header("智能绘图 - 图像特效")
    st.markdown("接口文档: https://www.volcengine.com/docs/85128/1588782")
    st.markdown("💡 基于字节自研图像生成模型，将输入的单人写真图片，进行有创意的特效化处理。与其他风格化模型的差异在于，此能力在保证输出图特征高度相似的同时，生成图像不受原有画面构图限制，可实现跨次元、超现实的视觉表达，更有视觉冲击力。")
    
    # 定义模板选项，包含中文显示名称和英文模板ID
    template_options = {
        "felt_3d_polaroid：毛毡3d拍立得风格": "felt_3d_polaroid",
        "my_world：像素世界": "my_world", 
        "plastic_bubble_figure：盲盒玩偶风": "plastic_bubble_figure",
        "furry_dream_doll：毛绒玩偶风": "furry_dream_doll",
        "micro_landscape_mini_world：迷你世界玩偶风": "micro_landscape_mini_world",
        "acrylic_ornaments：亚克力挂饰": "acrylic_ornaments",
        "felt_keychain：毛毡钥匙扣": "felt_keychain",
        "lofi_pixel_character_mini_card：Lofi 像素人物小卡": "lofi_pixel_character_mini_card",
        "angel_figurine：天使形象手办": "angel_figurine",
        "lying_in_fluffy_belly：躺在毛茸茸肚皮里": "lying_in_fluffy_belly",
        "glass_ball：玻璃球": "glass_ball",
        "my_world_universal：像素世界-万物通用版": "my_world_universal",
        "plastic_bubble_figure_cartoon_text：塑料泡罩人偶-文字卡头版": "plastic_bubble_figure_cartoon_text",
        "micro_landscape_mini_world_professional：微型景观小世界-职业版": "micro_landscape_mini_world_professional"
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        
        # 图片输入方式
        input_method_style = st.radio("选择图片来源", ("URL", "上传图片"), key="input_method_style")
        image_url_style = None
        uploaded_file_style = None

        if input_method_style == "URL":
            image_url_style = st.text_input(
                "输入图片 URL:", 
                "https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_bada876d0cb71c5598a6e0885f14c83c.png", 
                key="image_url_style"
            )
        else:
            uploaded_file_style = st.file_uploader(
                "上传图片", 
                type=["png", "jpg", "jpeg"], 
                key="file_uploader_style"
            )
        
        # 模板选择下拉框
        selected_template_display = st.selectbox(
            "选择特效模板",
            options=list(template_options.keys()),
            key="template_selector_style",
            help="选择要应用的图像特效风格"
        )
        
        # 获取对应的英文模板ID
        selected_template_id = template_options[selected_template_display]
        
        # 图片尺寸设置
        col_width, col_height = st.columns(2)
        with col_width:
            width_style = st.number_input("Width", value=1024, key="width_style")
        with col_height:
            height_style = st.number_input("Height", value=1024, key="height_style")
        
        # 生成按钮
        generate_button_style = st.button("🎨 应用特效", key="button_style", type="primary")
    
    with col2:
        st.subheader("图片预览和特效结果")
        
        # 预览区域
        preview_col, result_col = st.columns(2)
        
        with preview_col:
            st.write("**原图预览**")
            preview_image_style = None
            if input_method_style == "URL" and image_url_style:
                preview_image_style = image_url_style
            elif input_method_style == "上传图片" and uploaded_file_style is not None:
                preview_image_style = uploaded_file_style
            
            if preview_image_style is not None:
                st.image(preview_image_style, caption="原图", use_container_width=True)
            else:
                st.info("请上传图片或输入图片URL")
        
        with result_col:
            st.write("**特效结果**")
            if generate_button_style:
                if (input_method_style == "URL" and not image_url_style) or \
                   (input_method_style == "上传图片" and uploaded_file_style is None):
                    st.error("❌ 请先上传图片或输入图片URL！")
                else:
                    with st.spinner("🎨 正在应用特效，请耐心等待..."):
                        try:
                            img_url = None
                            image_base64_style = None
                            
                            if input_method_style == "URL":
                                img_url = i21_multi_style(
                                    visual_service,
                                    image_url=image_url_style,
                                    template_id=selected_template_id,
                                    width=width_style,
                                    height=height_style
                                )
                            elif input_method_style == "上传图片":
                                image_base64_style = base64.b64encode(uploaded_file_style.getvalue()).decode('utf-8')
                                img_url = i21_multi_style(
                                    visual_service,
                                    image_base64=image_base64_style,
                                    template_id=selected_template_id,
                                    width=width_style,
                                    height=height_style
                                )
                            
                            if img_url:
                                st.image(img_url, caption=f"特效结果 - {selected_template_display.split('：')[1]}", use_container_width=True)
                                st.success("✅ 图像特效应用成功！")
                                
                                # 显示应用的特效信息
                                st.info(f"🎨 **应用特效:** {selected_template_display}")
                                
                            else:
                                st.error("❌ 图像特效应用失败，请检查参数或稍后重试")
                                
                        except Exception as e:
                            st.error(f"❌ 应用图像特效时出错: {str(e)}")
                            st.info("💡 请检查网络连接和API配置，或稍后重试")
        
        # 特效说明
        with st.expander("🎨 特效模板说明", expanded=False):
            st.markdown("""
            **可用特效模板：**
            
            🎭 **风格类特效**
            - **毛毡3d拍立得风格**: 温馨的毛毡质感配合拍立得边框
            - **毛绒玩偶风**: 可爱的毛绒玩具效果
            - **盲盒玩偶风**: 流行的盲盒手办风格
            
            🎮 **像素类特效**  
            - **像素世界**: 经典8位像素游戏风格
            - **像素世界-万物通用版**: 适用于各种物体的像素化
            - **Lofi 像素人物小卡**: 复古像素人物卡片风格
            
            🏠 **迷你世界类**
            - **迷你世界玩偶风**: 精致的微缩景观效果
            - **微型景观小世界-职业版**: 专业版微缩场景
            
            ✨ **装饰类特效**
            - **亚克力挂饰**: 透明亚克力装饰品效果
            - **毛毡钥匙扣**: 手工毛毡钥匙扣风格
            - **天使形象手办**: 精美的天使手办效果
            - **玻璃球**: 梦幻的玻璃球封装效果
            
            🎪 **特殊效果**
            - **躺在毛茸茸肚皮里**: 温暖治愈的毛茸茸效果
            - **塑料泡罩人偶-文字卡头版**: 带文字卡片的泡罩包装风格
            
            **使用提示：**
            - 建议使用清晰、主体明确的图片
            - 不同模板适合不同类型的图片内容
            - 生成时间可能需要几分钟，请耐心等待
            """)

elif selected_function == "方舟-文生图3.0":
    st.header("方舟-文生图3.0")
    st.markdown("接口文档: https://www.volcengine.com/docs/82379/1541523")
    st.markdown("💡 使用方舟API进行文生图，支持多种尺寸和参数调节")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        
        # 模型选择
        model_ark_t2i = st.text_input(
            "输入模型名称",
            value="doubao-seedream-3-0-t2i-250415",
            key="model_ark_t2i"
        )
        
        # 提示词输入
        prompt_ark_t2i = st.text_area(
            "输入文生图提示词:",
            "一只可爱的小猫在花园里玩耍，阳光明媚，高清摄影",
            height=100,
            key="prompt_ark_t2i"
        )
        
        # 图片尺寸
        size_ark_t2i = st.selectbox(
            "图片尺寸",
            ["1024x1024", "1024x1536", "1536x1024", "1024x768", "768x1024", "1536x1536"],
            key="size_ark_t2i"
        )
        
        # 其他参数
        seed_ark_t2i = st.number_input("Seed", value=-1, key="seed_ark_t2i")
        guidance_scale_ark_t2i = st.slider("Guidance Scale", min_value=1.0, max_value=10.0, value=2.5, step=0.1, key="guidance_scale_ark_t2i")
        watermark_ark_t2i = st.checkbox("添加水印", value=True, key="watermark_ark_t2i")
        
        generate_button_ark_t2i = st.button("生成图片", key="button_ark_t2i")
    
    with col2:
        st.subheader("生成结果")
        
        if generate_button_ark_t2i:
            with st.spinner("正在生成图片..."):
                try:
                    image_url = ark_t2i(
                        ark_client,
                        model=model_ark_t2i,
                        prompt=prompt_ark_t2i,
                        size=size_ark_t2i,
                        seed=seed_ark_t2i,
                        guidance_scale=guidance_scale_ark_t2i,
                        watermark=watermark_ark_t2i
                    )
                    
                    if image_url:
                        st.image(image_url, caption="方舟生成图片")
                        st.success("图片生成成功！")
                    else:
                        st.error("图片生成失败，请检查参数或稍后重试")
                        
                except Exception as e:
                    st.error(f"生成图片时出错: {str(e)}")

elif selected_function == "既梦AI-文生图2.1":
    st.header("既梦AI 图像生成")
    st.markdown("""
    产品优势
**文字生成能力**：支持生成准确的中文汉字和英文字母; 
**构图**：整体在景别、视角方面变化多样性提升明显，画面层次感增强;
**光影：去除了刻意的光线表达，画面表现更加真实自然; 
**色彩**：画面色调统一性增强，去除了大部分高对比混乱杂色; 
**质感**：人物皮肤磨皮感及油腻感减弱，人像、动物及材质类类纹理质感表现更加真实细腻; 
**细节丰富度**：简化了过于繁琐的画面元素，画面整体表现现更加具有层次感、秩序感; 
    """)
    st.markdown("接口文档: https://www.volcengine.com/docs/85128/125990")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("输入参数")
        style_presets = {
            "文字海报":"制作一张vlog视频封面。马卡龙配色，美女旅游照片+色块的拼贴画风格，主文案是“威海旅游vlog”，副文案是“特种兵一日游 被低估的旅游城市”，海报主体是一个穿着短裙、梳双马尾的少女，人物白色描边",
            "浪漫水彩":"工笔画风格，三维古风，东方禅意，航拍高角度视角，捕捉了海底极小人物的奔跑追逐；构图大面积留白和丰富的光影，背景以水墨晕染展现水中阳光的多彩折射，现实与虚拟相结合的思考，水墨风格，蓝绿色调，逆光和辉光效果增强冷暖对比，高角度拍摄景深感，整体画面高清，画质通透，发光呈现幽静空灵感",
            "胶片梦核": "过曝，强对比，夜晚，雪地里，巨大的黄色浴缸，小狗泡澡带墨镜，在喝红酒，胶片摄影，毛刺质感，复古滤镜，夜晚，过度曝光，古早，70年代摄影，复古老照片，闪光灯拍摄，闪光灯效果，过曝，过度曝光，闪光灯过曝，极简，高饱和复古色，70s vintage photography, vintage, retro style"
        }
        
        # 添加自定义选项到开头
        style_presets = {"自定义": "一只可爱的猫", **style_presets}
        
        # 初始化session state用于存储提示词
        if 'prompt_t2i_jimeng' not in st.session_state:
            st.session_state.prompt_t2i_jimeng = style_presets["自定义"]

        # 风格选择回调函数
        def update_jimeng_prompt():
            selected_style = st.session_state.jimeng_style_selector
            if selected_style in style_presets:
                st.session_state.prompt_t2i_jimeng = style_presets[selected_style]

        # 风格选择下拉框
        selected_jimeng_style = st.selectbox(
            "选择风格类型",
            options=list(style_presets.keys()),
            key="jimeng_style_selector",
            on_change=update_jimeng_prompt
        )
        
        # 提示词输入框，使用session state中的值
        prompt_t2i_jimeng = st.text_area("输入文生图提示词:", key="prompt_t2i_jimeng", height=100)
        seed_t2i_jimeng = st.number_input("Seed", value=-1, key="seed_t2i_jimeng")
        width_t2i_jimeng = st.number_input("Width", value=512, key="width_t2i_jimeng")
        height_t2i_jimeng = st.number_input("Height", value=512, key="height_t2i_jimeng")
        use_pre_llm_jimeng = st.checkbox("Use Pre-LLM (开启文本扩写，会针对输入prompt进行扩写优化)", value=True, key="use_pre_llm_jimeng")
        use_sr_jimeng = st.checkbox("Use SR (文生图+AIGC超分)", value=True, key="use_sr_jimeng")
        return_url_t2i_jimeng = st.checkbox("Return URL", value=True, key="return_url_t2i_jimeng")
        generate_button_t2i_jimeng = st.button("生成图片", key="button_t2i_jimeng")

    with col2:
        st.subheader("生成结果")
        if generate_button_t2i_jimeng:
            with st.spinner("Generating..."):
                image_url = t2i_jimeng(visual_service, prompt_t2i_jimeng, seed_t2i_jimeng, width_t2i_jimeng, height_t2i_jimeng, return_url_t2i_jimeng, use_pre_llm_jimeng, use_sr_jimeng)
                if image_url:
                    st.image(image_url, caption="Generated Image")

elif selected_function == "既梦AI-图生图3.0":
    st.header("既梦AI-图生图 3.0")
    st.markdown("""
产品优势
**细节保留精准**：可在保持主体元素和图像风格等不变的基础上对图像进行指令编辑，支持增减元素、调整光影、更换背景或修改文字等; 
**指令遵循能力强**： 智能解析复杂编辑指令，对用户意图理解准确。无论是局部细节调整还是全局性修改，均能实现精准响应和高效执行; 
**专业级海报设计**：营销海报场景下的生产力利器，支持生成覆盖广泛行业需求的海报素材，在排版美感与文字设计感方面表现突出; 
    """)
    st.markdown("接口文档: https://www.volcengine.com/docs/85128/1602254")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("输入参数")
        input_method_jimeng_i2i = st.radio("选择图片来源", ("URL", "上传图片", "示例模板"), key="input_method_jimeng_i2i")
        image_url_jimeng_i2i = None
        uploaded_file_jimeng_i2i = None
        style_presets = {
            "元素消除": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_6dc837655edb35b90071547bc0b96e9e.png","prompt":"消除图片中的路人"},
            "元素更改": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_d586db140ae55431890252e42b567e83.jpeg","prompt":"将图片里的主体变成苹果,保留质感,光影,材质不变"},
            "光影变化": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_d2eb521d2805b644ee16ce032a85025d.png","prompt":"保持画面不变，在图片左上角打一束自然的光"},
            "风格转换": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_513b1d605d03f8c080bad2ad61eda88d.png","prompt":"保持背景结构，保持人物特征，风格改成中国水墨画，泼墨细节，工笔，简单的背景"},
            "文字修改": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_a154cafca83c25ca0e8e4dced3c2097b.jpeg","prompt":"字改成图中“初夏”文字改为“夏至”，“CHU XIA”改为“Summer Solstice”"},
            "设计补全": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_203c395adef4e44b6e5812f6f54b7e9e.png","prompt":'这是一张盛夏潮玩市集宣传海报，主标题使用大字中文"盛夏潮玩市集"与英文"SUMMER MARKET"组合呈现'},
            "商品图背景替换": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_30e36934801512b6416b61590271a24e.png","prompt":"根据图中物品的属性替换背景为其适合的背景场景"},
            "电商促销海报制作": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_1d400b9e85962e4891b8015f5be5ca9b.png","prompt":'电商促销海报设计，一张清新可爱的毛绒玩具海报。正中央放超呆萌的 “蒜鸟” 黄毛绒玩偶：身子圆滚滚的，眼睛像小黑豆，嘴巴和小脚是嫩黄色，头顶顶着一撮绿油油的蒜苗造型帽子！背景采用浅蓝色渐变底色，点缀着不规则散落的白色与绿色小方块增加灵动感；画面上方用黑色粗体字呈现 "蒜鸟，都不涌易" 的趣味 slogan，中部以黄色字体标注 "好东西代表：蒜鸟玩偶" 及 "# 适用人群：脆皮省电人" 等标签化信息，整体营造出符合年轻人审美的可爱清新视觉效果。背景是天空蓝色渐变，清爽，整体很有夏日风格 。'},
            "商品图包装": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_0f37291d4e326a104fe1ff35c074f80b.png","prompt":'海报上方用橙色粗体字写着"居家幸福感拉满！"，文字带有白色描边，下方添加同色系衬底，十分醒目。产品图中的粉色拖鞋周围点缀着星星和小兔子的装饰元素，与拖鞋上的兔子图案相呼应，同时为拖鞋添加白色粗描边，使其更突出。三条文案分别为"踩屎感谁懂！""懒人必备神器""少女心爆棚啦"，均用白色字体，搭配黑色描边，分布在产品图的合适位置。背景是模糊虚化的木质地板场景，色调与商品的粉色、旁边的米色杯子相协调，营造出温馨舒适的居家氛围。整体风格突出产品的柔软舒适与可爱特性，吸引消费者目光。'},
            "拍立得风格": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_78bf49fc071461941cd401d4f6eddca9.png","prompt":"将照片变为这个风格：类似拍立得相纸白色边框，暗朦，隐约的淡彩褪色，非对称，个性视角表达，对焦主体，随意瞬间抓拍模糊场景，y2k，光朦，过曝，复古，低饱和，质感，模糊晕染，强透视，高噪点，胶片颗粒质感，现场感，情绪写意，大片美学，前卫艺术美学，细节丰富，高级感，杰作"},
        }

        # 初始化session state用于存储模板选择的值
        first_template_key = list(style_presets.keys())[0]
        if 'jimeng_i2i_template_url' not in st.session_state:
            st.session_state.jimeng_i2i_template_url = style_presets[first_template_key]["url"]
        if 'jimeng_i2i_template_prompt' not in st.session_state:
            st.session_state.jimeng_i2i_template_prompt = style_presets[first_template_key]["prompt"]

        # 根据选择的输入方式显示不同的输入控件
        if input_method_jimeng_i2i == "URL":
            image_url_jimeng_i2i = st.text_input("输入图片 URL:", "https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_b9d0ea6bb4528cce79517a7c706ad1b7.png", key="image_url_jimeng_i2i")
        elif input_method_jimeng_i2i == "上传图片":
            uploaded_file_jimeng_i2i = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"], key="file_uploader_jimeng_i2i")
        elif input_method_jimeng_i2i == "示例模板":
            # 模板选择回调函数
            def update_template_values():
                selected_style = st.session_state.style_template_selector
                if selected_style in style_presets:
                    st.session_state.jimeng_i2i_template_url = style_presets[selected_style]["url"]
                    st.session_state.jimeng_i2i_template_prompt = style_presets[selected_style]["prompt"]
            
            # 风格模板选择器
            selected_template = st.selectbox(
                "选择示例模板",
                options=list(style_presets.keys()),
                key="style_template_selector",
                on_change=update_template_values
            )
            
            # 显示选中模板的URL（只读）
            st.text_input(
                "模板图片 URL:", 
                value=st.session_state.jimeng_i2i_template_url or style_presets[selected_template]["url"],
                disabled=True,
                key="template_url_display"
            )
            
            # 设置image_url_jimeng_i2i为模板URL
            image_url_jimeng_i2i = st.session_state.jimeng_i2i_template_url or style_presets[selected_template]["url"]

        # 提示词输入框，根据是否选择模板显示不同的默认值
        if input_method_jimeng_i2i == "示例模板":
            prompt_default = st.session_state.jimeng_i2i_template_prompt or style_presets[list(style_presets.keys())[0]]["prompt"]
        else:
            prompt_default = "将小女孩的衣服换成白色的公主裙"
            
        prompt_jimeng_i2i = st.text_area("输入编辑指令:", prompt_default, height=100, key="prompt_jimeng_i2i")
        seed_jimeng_i2i = st.number_input("Seed", value=-1, key="seed_jimeng_i2i")
        width_jimeng_i2i = st.number_input("Width", value=1328, key="width_jimeng_i2i")
        height_jimeng_i2i = st.number_input("Height", value=1328, key="height_jimeng_i2i")
        scale_jimeng_i2i = st.slider("Scale", min_value=0.0, max_value=1.0, value=0.5, step=0.1, key="scale_jimeng_i2i")
        generate_button_jimeng_i2i = st.button("开始编辑", key="button_jimeng_i2i")

    with col2:
        st.subheader("图片预览和编辑结果")
        preview_col, result_col = st.columns(2)

        with preview_col:
            preview_image = None
            if input_method_jimeng_i2i == "URL" and image_url_jimeng_i2i:
                preview_image = image_url_jimeng_i2i
            elif input_method_jimeng_i2i == "上传图片" and uploaded_file_jimeng_i2i is not None:
                preview_image = uploaded_file_jimeng_i2i
            elif input_method_jimeng_i2i == '示例模板':
                preview_image = st.session_state.jimeng_i2i_template_url

            
            if preview_image is not None:
                st.image(preview_image, caption="图片预览")

        with result_col:
            if generate_button_jimeng_i2i:
                with st.spinner("正在编辑中..."):
                    img_url = None
                    image_base64 = None
                    if input_method_jimeng_i2i == "上传图片" and uploaded_file_jimeng_i2i is not None:
                        image_base64 = base64.b64encode(uploaded_file_jimeng_i2i.getvalue()).decode('utf-8')
                    
                    img_url = i2i_jimeng_v30(
                        visual_service, 
                        prompt=prompt_jimeng_i2i, 
                        seed=seed_jimeng_i2i, 
                        width=width_jimeng_i2i,
                        height=height_jimeng_i2i,
                        scale=scale_jimeng_i2i, 
                        image_url=image_url_jimeng_i2i, 
                        image_base64=image_base64
                    )
                    
                    if img_url:
                        st.image(img_url, caption="编辑后图片")

elif selected_function == "既梦AI-文生视频":
    st.header("既梦AI 文生视频")
    st.markdown("""
产品优势
**高语义遵循**：具有极高的“提示词遵循能力”，支持输入很复杂的提示词（例如镜头切换、人物连续动作、情绪演绎、运镜控制）
**动效流畅**：动作效果流畅自然，整体视频效果结构稳定
**画面一致性**：支持保持风格及主体一致性
    """)
    st.markdown("接口文档: https://www.volcengine.com/docs/85621/1538636")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("输入参数")
        prompt_t2v_jimeng = st.text_area("输入文生视频提示词:", "衣服爆发出一团白色泡沫状的物体，仿佛瞬间膨胀或炸裂开来；衣服被气球完全包裹，气球的颜色以橙色、白色和银色为主，层层叠叠地围绕身体。越来越多不断生长；衣服逐渐化作一团不断扩展的巨大银色丝球，闪烁着光泽，呈现出无尽生长的动态；衣服像气球般迅速膨胀，逐渐充满周围的空间，随后开始缓缓泄气；衣服变成很多个银色的气球，飞起来，然后散落在地面", height=100, key="prompt_t2v_jimeng")
        seed_t2v_jimeng = st.number_input("Seed", value=-1, key="seed_t2v_jimeng")
        aspect_ratio_t2v_jimeng = st.selectbox("Aspect Ratio", ["16:9", "9:16", "1:1"], key="aspect_ratio_t2v_jimeng")
        generate_button_t2v_jimeng = st.button("生成视频", key="button_t2v_jimeng")

    with col2:
        st.subheader("生成结果")
        if generate_button_t2v_jimeng:
            with st.spinner("Generating..."):
                video_url = t2v_jimeng_s20_pro(visual_service, prompt_t2v_jimeng, seed_t2v_jimeng, aspect_ratio_t2v_jimeng)
                if video_url:
                    st.video(video_url)

elif selected_function == "既梦AI-图生视频":
    st.header("既梦AI 图生视频")
    st.markdown("""
产品优势
**高语义遵循**：具有极高的“提示词遵循能力”，支持输入很复杂的提示词（例如镜头切换、人物连续动作、情绪演绎、运镜控制）
**动效流畅**：动作效果流畅自然，整体视频效果结构稳定
**画面一致性**：支持保持风格及主体一致性
    """)
    st.markdown("接口文档: https://www.volcengine.com/docs/85621/1544774")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("输入参数")
        input_method_jimeng_i2v = st.radio("选择图片来源", ("URL", "上传图片"), key="input_method_jimeng_i2v")
        image_url_jimeng_i2v = None
        uploaded_file_jimeng_i2v = None

        if input_method_jimeng_i2v == "URL":
            image_url_jimeng_i2v = st.text_input("输入图片 URL:", "https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_b9d0ea6bb4528cce79517a7c706ad1b7.png", key="image_url_jimeng_i2v")
        else:
            uploaded_file_jimeng_i2v = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"], key="file_uploader_jimeng_i2v")

        prompt_jimeng_i2v = st.text_area("输入编辑指令:", "第一个镜头-全：女孩慢慢的往前走。第二个镜头-近景：女孩慢慢的弯腰蹲下身；第三个镜头-特写：女孩伸手去抚摸地上的小草", height=100, key="prompt_jimeng_i2v")
        seed_jimeng_i2v = st.number_input("Seed", value=-1, key="seed_jimeng_i2v")
        aspect_ratio_jimeng_i2v = st.selectbox("Aspect Ratio", ["16:9", "9:16", "1:1"], key="aspect_ratio_jimeng_i2v")
        generate_button_jimeng_i2v = st.button("开始生成", key="button_jimeng_i2v")

    with col2:
        st.subheader("图片预览和生成结果")
        preview_col, result_col = st.columns(2)

        with preview_col:
            preview_image = None
            if input_method_jimeng_i2v == "URL" and image_url_jimeng_i2v:
                preview_image = image_url_jimeng_i2v
            elif input_method_jimeng_i2v == "上传图片" and uploaded_file_jimeng_i2v is not None:
                preview_image = uploaded_file_jimeng_i2v
            
            if preview_image is not None:
                st.image(preview_image, caption="图片预览")

        with result_col:
            if generate_button_jimeng_i2v:
                with st.spinner("正在生成中..."):
                    video_url = None
                    image_base64 = None
                    if input_method_jimeng_i2v == "上传图片" and uploaded_file_jimeng_i2v is not None:
                        image_base64 = base64.b64encode(uploaded_file_jimeng_i2v.getvalue()).decode('utf-8')
                    
                    video_url = i2v_jimeng_s20_pro(
                        visual_service, 
                        prompt=prompt_jimeng_i2v, 
                        seed=seed_jimeng_i2v, 
                        aspect_ratio=aspect_ratio_jimeng_i2v,
                        image_url=image_url_jimeng_i2v, 
                        image_base64=image_base64
                    )
                    
                    if video_url:
                        st.video(video_url)

elif selected_function == "方舟-图像编辑3.0":
    st.header("方舟-图像编辑3.0")
    st.markdown("接口文档: https://www.volcengine.com/docs/82379/1666946")
    st.markdown("💡 使用方舟API进行图像编辑，支持多种编辑指令")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        
        # 模型选择
        model_ark_i2i = st.text_input(
            "输入模型名称",
            value="doubao-seededit-3-0-i2i-250628",
            key="model_ark_i2i"
        )
        
        # 图片输入方式
        input_method_ark = st.radio("选择图片来源", ("URL", "上传图片"), key="input_method_ark")
        image_url_ark = None
        uploaded_file_ark = None

        if input_method_ark == "URL":
            image_url_ark = st.text_input(
                "输入图片 URL:", 
                "https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_b9d0ea6bb4528cce79517a7c706ad1b7.png", 
                key="image_url_ark"
            )
        else:
            uploaded_file_ark = st.file_uploader(
                "上传图片", 
                type=["png", "jpg", "jpeg"], 
                key="file_uploader_ark"
            )
        
        # 编辑提示词
        prompt_ark_i2i = st.text_area(
            "输入编辑指令:",
            "将衣服颜色改为红色",
            height=100,
            key="prompt_ark_i2i"
        )
        
        # 其他参数
        seed_ark_i2i = st.number_input("Seed", value=-1, key="seed_ark_i2i")
        guidance_scale_ark_i2i = st.slider("Guidance Scale", min_value=1.0, max_value=10.0, value=5.5, step=0.1, key="guidance_scale_ark_i2i")
        watermark_ark_i2i = st.checkbox("添加水印", value=True, key="watermark_ark_i2i")
        
        generate_button_ark_i2i = st.button("开始编辑", key="button_ark_i2i")
    
    with col2:
        st.subheader("图片预览和编辑结果")
        preview_col, result_col = st.columns(2)
        
        with preview_col:
            st.write("**原图预览**")
            preview_image_ark = None
            if input_method_ark == "URL" and image_url_ark:
                preview_image_ark = image_url_ark
            elif input_method_ark == "上传图片" and uploaded_file_ark is not None:
                preview_image_ark = uploaded_file_ark
            
            if preview_image_ark is not None:
                st.image(preview_image_ark, caption="原图")
            else:
                st.info("请上传图片或输入图片URL")
        
        with result_col:
            st.write("**编辑结果**")
            if generate_button_ark_i2i:
                if (input_method_ark == "URL" and not image_url_ark) or \
                   (input_method_ark == "上传图片" and uploaded_file_ark is None):
                    st.error("请先上传图片或输入图片URL！")
                else:
                    with st.spinner("正在编辑图片..."):
                        try:
                            # 准备图片数据
                            image_data = None
                            if input_method_ark == "URL":
                                image_data = image_url_ark
                            elif input_method_ark == "上传图片":
                                image_base64_ark = base64.b64encode(uploaded_file_ark.getvalue()).decode('utf-8')
                                # 根据文件类型设置正确的MIME类型
                                mime_type = f"image/{uploaded_file_ark.type.split('/')[-1]}" if uploaded_file_ark.type else "image/jpeg"
                                image_data = f"data:{mime_type};base64,{image_base64_ark}"
                            
                            image_url = ark_i2i(
                                ark_client,
                                model=model_ark_i2i,
                                prompt=prompt_ark_i2i,
                                image=image_data,
                                seed=seed_ark_i2i,
                                guidance_scale=guidance_scale_ark_i2i,
                                watermark=watermark_ark_i2i
                            )
                            
                            if image_url:
                                st.image(image_url, caption="编辑后图片")
                                st.success("图片编辑成功！")
                            else:
                                st.error("图片编辑失败，请检查参数或稍后重试")
                                
                        except Exception as e:
                            st.error(f"编辑图片时出错: {str(e)}")

elif selected_function == "文生视频":
    st.header("Seedance 1.0 文生视频")
    st.markdown("接口文档: https://www.volcengine.com/docs/82379/1520757")
    st.markdown("Seedance-pro 提示词指南: https://bytedance.larkoffice.com/docx/Svl9dMwvCokzZHxamTWcCz5en1f?from=from_copylink")
    st.markdown("Seedance-lit 提示词指南: https://bytedance.larkoffice.com/docx/UQoSd3NEvoAkghxAl0ccjdplnhR?from=from_copylink")

    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        
        # 模型选择
        model_t2v = st.selectbox(
            "选择模型",
            ["doubao-seedance-1-0-pro-250528", "doubao-seedance-1-0-lite-t2v-250428"],
            key="model_t2v"
        )
        
        # 基础提示词 - 使用优化后的值或默认值
        if 'optimized_prompt_t2v' in st.session_state and st.session_state.optimized_prompt_t2v:
            default_prompt_t2v = st.session_state.optimized_prompt_t2v
        else:
            default_prompt_t2v = "一只可爱的小猫在花园里玩耍"
            
        # 创建标题和优化链接
        prompt_col1, prompt_col2 = st.columns([3, 1])
        st.write("输入视频描述提示词:")
            
        base_prompt_t2v = st.text_area(
            "视频描述提示词",
            value=default_prompt_t2v,
            height=100,
            key="base_prompt_t2v",
            label_visibility="collapsed"
        )
        optimize_button_t2v = st.button("一键优化", key="optimize_t2v", help="使用AI优化您的提示词", type="secondary")
        
        # 处理提示词优化
        if optimize_button_t2v:
            if base_prompt_t2v.strip():
                with st.spinner("正在优化提示词..."):
                    try:
                        # 流式显示优化过程
                        placeholder = st.empty()
                        optimized_text = ""
                        
                        for chunk in optimize_stream(ark_client, "t2v", base_prompt_t2v):
                            optimized_text += chunk
                            # 实时显示优化进度
                            placeholder.text_area(
                                "优化中...",
                                value=optimized_text,
                                height=100,
                                disabled=True
                            )
                        
                        # 优化完成后保存结果并重新运行
                        if optimized_text.strip():
                            st.session_state.optimized_prompt_t2v = optimized_text.strip()
                            placeholder.empty()  # 清除临时显示
                            st.success("提示词优化完成！")
                            st.rerun()
                        else:
                            placeholder.empty()
                            st.error("优化失败，请稍后重试")
                            
                    except Exception as e:
                        st.error(f"优化提示词时出错: {str(e)}")
            else:
                st.warning("请先输入提示词再进行优化")
        
        # 视频参数
        st.subheader("视频参数")
        
        resolution_t2v = st.selectbox(
            "分辨率",
            ["480p", "720p", "1080p"],
            index=1,
            key="resolution_t2v"
        )
        
        ratio_t2v = st.selectbox(
            "宽高比",
            ["21:9", "16:9", "4:3", "1:1", "3:4", "9:16", "9:21", "keep_ratio", "adaptive"],
            index=1,
            key="ratio_t2v"
        )
        
        duration_t2v = st.selectbox(
            "时长",
            ["5", "10"],
            key="duration_t2v"
        )
        
        fps_t2v = st.selectbox(
            "帧率",
            [16, 24],
            index=1,
            key="fps_t2v"
        )
        
        watermark_t2v = st.checkbox("添加水印", value=True, key="watermark_t2v")
        
        seed_t2v = st.number_input("Seed", value=-1, key="seed_t2v")
        
        camera_fixed_t2v = st.checkbox("固定镜头", value=False, key="camera_fixed_t2v")
        
        generate_button_t2v = st.button("生成视频", key="button_t2v")
    
    with col2:
        st.subheader("生成结果")
        
        if generate_button_t2v:
            with st.spinner("正在生成视频，请耐心等待..."):
                # 构建完整的提示词，将参数拼接到提示词末尾
                full_prompt = base_prompt_t2v
                full_prompt += f" --resolution {resolution_t2v}"
                full_prompt += f" --ratio {ratio_t2v}"
                full_prompt += f" --duration {duration_t2v}"
                full_prompt += f" --fps {fps_t2v}"
                full_prompt += f" --watermark {str(watermark_t2v).lower()}"
                if seed_t2v != -1:
                    full_prompt += f" --seed {seed_t2v}"
                full_prompt += f" --camerafixed {str(camera_fixed_t2v).lower()}"
                
                st.info(f"完整提示词: {full_prompt}")
                
                try:
                    video_url = t2v_seedance(ark_client, model_t2v, full_prompt)
                    if video_url:
                        st.success("视频生成成功！")
                        st.video(video_url)
                        st.markdown(f"[下载视频]({video_url})")
                    else:
                        st.error("视频生成失败，请检查参数或稍后重试")
                except Exception as e:
                    st.error(f"生成视频时出错: {str(e)}")

elif selected_function == "图生视频":
    st.header("Seedance 1.0 图生视频")
    st.markdown("接口文档: https://www.volcengine.com/docs/82379/1520757")
    st.markdown("Seedance-pro 提示词指南: https://bytedance.larkoffice.com/docx/Svl9dMwvCokzZHxamTWcCz5en1f?from=from_copylink")
    st.markdown("Seedance-lit 提示词指南: https://bytedance.larkoffice.com/docx/UQoSd3NEvoAkghxAl0ccjdplnhR?from=from_copylink")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        
        # 模型选择
        model_i2v = st.selectbox(
            "选择模型",
            ["doubao-seedance-1-0-pro-250528", "doubao-seedance-1-0-lite-i2v-250428"],
            key="model_i2v"
        )
        # 首帧图片上传
        st.subheader("图片上传")
        first_frame_file = st.file_uploader(
            "上传首帧图片 (必需)",
            type=["png", "jpg", "jpeg"],
            key="first_frame_i2v"
        )
        
        # 根据模型显示尾帧上传选项
        last_frame_file = None
        if model_i2v == "doubao-seedance-1-0-lite-i2v-250428":
            last_frame_file = st.file_uploader(
                "上传尾帧图片 (可选)",
                type=["png", "jpg", "jpeg"],
                key="last_frame_i2v"
            )
            st.info("💡 Seedance 1.0 lite 模型支持首帧和尾帧，可以更精确控制视频内容")
        else:
            st.info("💡 Seedance 1.0 pro 模型只支持首帧")

        # 基础提示词 - 使用优化后的值或默认值
        if 'optimized_prompt_i2v' in st.session_state and st.session_state.optimized_prompt_i2v:
            default_prompt_i2v = st.session_state.optimized_prompt_i2v
        else:
            default_prompt_i2v = "让图片中的人物动起来，自然的动作"
            
        # 创建标题和优化链接
        col1_i2v, col2_i2v = st.columns([3, 1])
        st.write("输入视频描述提示词:")   
        base_prompt_i2v = st.text_area(
            "视频描述提示词",
            value=default_prompt_i2v,
            height=100,
            key="base_prompt_i2v",
            label_visibility="collapsed"
        )
        optimize_button_i2v = st.button("一键优化", key="optimize_i2v", help="使用AI优化您的提示词", type="secondary")
        
        # 处理提示词优化
        if optimize_button_i2v:
            if base_prompt_i2v.strip():
                with st.spinner("正在优化提示词..."):
                    try:
                        # 获取首帧图片的base64编码用于优化
                        first_frame_url = None
                        if first_frame_file is not None:
                            first_frame_base64 = base64.b64encode(first_frame_file.getvalue()).decode('utf-8')
                            # 根据文件类型设置正确的MIME类型
                            mime_type = f"image/{first_frame_file.type.split('/')[-1]}" if first_frame_file.type else "image/jpeg"
                            first_frame_url = f"data:{mime_type};base64,{first_frame_base64}"
                        
                        # 流式显示优化过程
                        placeholder = st.empty()
                        optimized_text = ""
                        
                        for chunk in optimize_stream(ark_client, "i2v", base_prompt_i2v, first_frame_url):
                            optimized_text += chunk
                            # 实时显示优化进度
                            placeholder.text_area(
                                "优化中...",
                                value=optimized_text,
                                height=100,
                                disabled=True
                            )
                        
                        # 优化完成后保存结果并重新运行
                        if optimized_text.strip():
                            st.session_state.optimized_prompt_i2v = optimized_text.strip()
                            placeholder.empty()  # 清除临时显示
                            st.success("提示词优化完成！")
                            st.rerun()
                        else:
                            placeholder.empty()
                            st.error("优化失败，请稍后重试")
                            
                    except Exception as e:
                        st.error(f"优化提示词时出错: {str(e)}")
            else:
                st.warning("请先输入提示词再进行优化")
        
        # 视频参数
        st.subheader("视频参数")
        
        resolution_i2v = st.selectbox(
            "分辨率",
            ["480p", "720p", "1080p"],
            index=1,
            key="resolution_i2v"
        )
        
        ratio_i2v = st.selectbox(
            "宽高比",
            ["keep_ratio","adaptive"],
            index=1,
            key="ratio_i2v"
        )
        
        duration_i2v = st.selectbox(
            "时长",
            ["5", "10"],
            key="duration_i2v"
        )
        
        fps_i2v = st.selectbox(
            "帧率",
            [16, 24],
            index=1,
            key="fps_i2v"
        )
        
        watermark_i2v = st.checkbox("添加水印", value=True, key="watermark_i2v")
        
        seed_i2v = st.number_input("Seed", value=-1, key="seed_i2v")
        
        camera_fixed_i2v = st.checkbox("固定镜头", value=False, key="camera_fixed_i2v")
        
        generate_button_i2v = st.button("生成视频", key="button_i2v")
    
    with col2:
        st.subheader("图片预览和生成结果")
        
        # 图片预览区域
        preview_col1, preview_col2 = st.columns(2)
        
        with preview_col1:
            st.write("**首帧预览**")
            if first_frame_file is not None:
                st.image(first_frame_file, caption="首帧图片")
            else:
                st.info("请上传首帧图片")
        
        with preview_col2:
            st.write("**尾帧预览**")
            if last_frame_file is not None:
                st.image(last_frame_file, caption="尾帧图片")
            elif model_i2v == "doubao-seedance-1-0-lite-i2v-250428":
                st.info("可选择上传尾帧图片")
            else:
                st.info("当前模型不支持尾帧")
        
        # 生成结果区域
        st.subheader("生成结果")
        
        if generate_button_i2v:
            if first_frame_file is None:
                st.error("请先上传首帧图片！")
            else:
                with st.spinner("正在生成视频，请耐心等待..."):
                    try:
                        # 将图片转换为base64并上传获取URL
                        # 这里简化处理，实际应该上传到云存储获取URL
                        first_frame_base64 = base64.b64encode(first_frame_file.getvalue()).decode('utf-8')
                        # 根据文件类型设置正确的MIME类型
                        first_frame_mime = f"image/{first_frame_file.type.split('/')[-1]}" if first_frame_file.type else "image/jpeg"
                        first_frame_url = f"data:{first_frame_mime};base64,{first_frame_base64}"
                        
                        last_frame_url = None
                        if last_frame_file is not None:
                            last_frame_base64 = base64.b64encode(last_frame_file.getvalue()).decode('utf-8')
                            # 根据文件类型设置正确的MIME类型
                            last_frame_mime = f"image/{last_frame_file.type.split('/')[-1]}" if last_frame_file.type else "image/jpeg"
                            last_frame_url = f"data:{last_frame_mime};base64,{last_frame_base64}"
                        
                        # 构建完整的提示词
                        full_prompt = base_prompt_i2v
                        full_prompt += f" --resolution {resolution_i2v}"
                        full_prompt += f" --ratio {ratio_i2v}"
                        full_prompt += f" --duration {duration_i2v}"
                        full_prompt += f" --fps {fps_i2v}"
                        full_prompt += f" --watermark {str(watermark_i2v).lower()}"
                        if seed_i2v != -1:
                            full_prompt += f" --seed {seed_i2v}"
                        full_prompt += f" --camerafixed {str(camera_fixed_i2v).lower()}"
                        
                        st.info(f"完整提示词: {full_prompt}")
                        
                        # 调用图生视频函数
                        video_url = i2v_seedance(
                            ark_client, 
                            model_i2v, 
                            full_prompt,
                            first_frame=first_frame_url,
                            last_frame=last_frame_url
                        )
                        
                        if video_url:
                            st.success("视频生成成功！")
                            st.video(video_url)
                            st.markdown(f"[下载视频]({video_url})")
                        else:
                            st.error("视频生成失败，请检查参数或稍后重试")
                            
                    except Exception as e:
                        st.error(f"生成视频时出错: {str(e)}")

elif selected_function == "视频生成-视频特效":
    st.header("🎬 视频生成-视频特效")
    st.markdown("接口文档: https://www.volcengine.com/docs/85128/1783766")
    st.markdown("💡 基于字节自研的图像及视频处理技术和先进算法模型，支持基于用户上传的图片，稳定生成高质量、的创意特效视频。此能力亮点在于整合了多种自研图像和视频技术能力与先进模型，生成视频附带适配的背景音乐和音效，兼具创意性和视觉表现力，可广泛应用于互动娱乐和写真特效等场景。")
    
    # 定义模板选项，包含中文显示名称、英文模板ID和默认URL
    template_options = {
        "变身玩偶_480p版": {
            "id": "becoming_doll",
            "url": "https://qwer123.tos-cn-beijing.volces.com/857ff5c6-2f16-495b-bd8e-65ccbe38a29b.png"
        },
        "变身玩偶_720p版": {
            "id": "becoming_doll_720p", 
            "url": "https://qwer123.tos-cn-beijing.volces.com/857ff5c6-2f16-495b-bd8e-65ccbe38a29b.png"
        },
        "召唤坐骑-猪_480p版": {
            "id": "all_things_ridability_pig",
            "url": "https://qwer123.tos-cn-beijing.volces.com/b50a89c7-8c46-486d-b3ef-95f682e12192.png"
        },
        "召唤坐骑-猪_720p版": {
            "id": "all_things_ridability_pig_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/b50a89c7-8c46-486d-b3ef-95f682e12192.png"
        },
        "召唤坐骑-老虎_480p版": {
            "id": "all_things_ridability_tiger",
            "url": "https://qwer123.tos-cn-beijing.volces.com/faeb2464-b830-44c9-86dd-e0a65ca4e911.png"
        },
        "召唤坐骑-老虎_720p版": {
            "id": "all_things_ridability_tiger_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/faeb2464-b830-44c9-86dd-e0a65ca4e911.png"
        },
        "召唤坐骑-龙_480p版": {
            "id": "all_things_ridability_loong",
            "url": "https://qwer123.tos-cn-beijing.volces.com/fc4d15dd-7ab6-42df-be21-d40b6cde3703.png"
        },
        "召唤坐骑-龙_720p版": {
            "id": "all_things_ridability_loong_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/fc4d15dd-7ab6-42df-be21-d40b6cde3703.png"
        },
        "万物生花_480p版": {
            "id": "all_things_bloom_with_flowers",
            "url": "https://qwer123.tos-cn-beijing.volces.com/0e7aed08-267e-4272-82af-50c5e8e14a23.png"
        },
        "万物生花_720p版": {
            "id": "all_things_bloom_with_flowers_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/0e7aed08-267e-4272-82af-50c5e8e14a23.png"
        },
        "爱的拥抱（单图）_480p版": {
            "id": "double_embrace_single_person",
            "url": "https://qwer123.tos-cn-beijing.volces.com/9459a381-3bbe-4e57-a154-c9c71bd395c2.png"
        },
        "爱的拥抱（单图）_720p版": {
            "id": "double_embrace_single_person_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/9459a381-3bbe-4e57-a154-c9c71bd395c2.png"
        },
        "爱的拥抱（双图）_480p版": {
            "id": "double_embrace",
            "url": "https://qwer123.tos-cn-beijing.volces.com/9781c1f7-cd79-4daf-a027-6bd2b3775c8c.png|https://qwer123.tos-cn-beijing.volces.com/9459a381-3bbe-4e57-a154-c9c71bd395c2.png"
        },
        "爱的拥抱（双图）_720p版": {
            "id": "double_embrace_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/9781c1f7-cd79-4daf-a027-6bd2b3775c8c.png|https://qwer123.tos-cn-beijing.volces.com/9459a381-3bbe-4e57-a154-c9c71bd395c2.png"
        },
        "AI美女环绕_480p版": {
            "id": "beauty_surround",
            "url": "https://qwer123.tos-cn-beijing.volces.com/b50a89c7-8c46-486d-b3ef-95f682e12192.png"
        },
        "AI美女环绕_720p版": {
            "id": "beauty_surround_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/b50a89c7-8c46-486d-b3ef-95f682e12192.png"
        },
        "AI帅哥环绕_480p版": {
            "id": "handsome_man_surround",
            "url": "https://qwer123.tos-cn-beijing.volces.com/68c1b962-49ce-45d2-a367-6676a66f6c18.png"
        },
        "AI帅哥环绕_720p版": {
            "id": "handsome_man_surround_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/68c1b962-49ce-45d2-a367-6676a66f6c18.png"
        },
        "天赐宝宝_480p版": {
            "id": "ai_baby",
            "url": "https://qwer123.tos-cn-beijing.volces.com/b50a89c7-8c46-486d-b3ef-95f682e12192.png"
        },
        "天赐宝宝_720p版": {
            "id": "ai_baby_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/b50a89c7-8c46-486d-b3ef-95f682e12192.png"
        },
        "清凉泳装变身_480p版": {
            "id": "put_on_bikini",
            "url": "https://qwer123.tos-cn-beijing.volces.com/857ff5c6-2f16-495b-bd8e-65ccbe38a29b.png"
        },
        "清凉泳装变身_720p版": {
            "id": "put_on_bikini_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/857ff5c6-2f16-495b-bd8e-65ccbe38a29b.png"
        },
        "变身兔女郎_480p版": {
            "id": "put_on_bunny_girl_outfit",
            "url": "https://qwer123.tos-cn-beijing.volces.com/26fdf9e9-5a65-4e3e-b923-2a13f1bc9644.png"
        },
        "变身兔女郎_720p版": {
            "id": "put_on_bunny_girl_outfit_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/26fdf9e9-5a65-4e3e-b923-2a13f1bc9644.png"
        }
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        
        # 模板选择下拉框
        selected_template_display = st.selectbox(
            "选择视频特效模板",
            options=list(template_options.keys()),
            key="template_selector_video",
            help="选择要应用的视频特效模板"
        )
        
        # 获取对应的模板ID和默认URL
        selected_template_info = template_options[selected_template_display]
        selected_template_id = selected_template_info["id"]
        default_url = selected_template_info["url"]
        
        # 图片输入方式
        input_method_video = st.radio("选择图片来源", ("使用模板默认图片", "自定义URL", "上传图片"), key="input_method_video")
        image_input_video = None
        uploaded_file_video = None

        if input_method_video == "使用模板默认图片":
            image_input_video = default_url
            st.text_input(
                "模板默认图片URL:", 
                value=default_url,
                disabled=True,
                key="default_url_display_video"
            )
        elif input_method_video == "自定义URL":
            image_input_video = st.text_input(
                "输入图片 URL:", 
                value=default_url,
                key="image_url_video"
            )
        else:
            uploaded_file_video = st.file_uploader(
                "上传图片", 
                type=["png", "jpg", "jpeg"], 
                key="file_uploader_video"
            )
        
        # 特殊处理：爱的拥抱（双图）模板
        is_double_embrace = "double_embrace" in selected_template_id and "single" not in selected_template_id
        
        if is_double_embrace:
            st.info("💡 此模板需要两张图片，请使用'|'分隔两个图片URL")
            if input_method_video == "自定义URL":
                st.markdown("**示例格式:** `https://image1.jpg|https://image2.jpg`")
        
        # 生成按钮
        generate_button_video = st.button("🎬 生成视频特效", key="button_video", type="primary")
    
    with col2:
        st.subheader("图片预览和生成结果")
        
        # 预览区域
        preview_col, result_col = st.columns(2)
        
        with preview_col:
            st.write("**原图预览**")
            preview_image_video = None
            
            if input_method_video == "使用模板默认图片" or input_method_video == "自定义URL":
                if image_input_video:
                    # 处理双图情况
                    if is_double_embrace and "|" in image_input_video:
                        image_urls = image_input_video.split("|")
                        st.write("**图片1:**")
                        st.image(image_urls[0], caption="第一张图片", use_container_width=True)
                        if len(image_urls) > 1:
                            st.write("**图片2:**")
                            st.image(image_urls[1], caption="第二张图片", use_container_width=True)
                    else:
                        st.image(image_input_video, caption="原图", use_container_width=True)
            elif input_method_video == "上传图片" and uploaded_file_video is not None:
                st.image(uploaded_file_video, caption="上传的图片", use_container_width=True)
            else:
                st.info("请选择或上传图片")
        
        with result_col:
            st.write("**视频特效结果**")
            if generate_button_video:
                # 验证输入
                final_image_input = None
                
                if input_method_video == "使用模板默认图片" or input_method_video == "自定义URL":
                    final_image_input = image_input_video
                elif input_method_video == "上传图片" and uploaded_file_video is not None:
                    # 对于上传的图片，需要先上传到云存储获取URL
                    object_key = f"uploads/video_effects_{int(time.time())}_{uploaded_file_video.name}"
                    upload_url = upload_to_tos(object_key, uploaded_file_video.getvalue())
                    if upload_url:
                        final_image_input = upload_url
                        st.success(f"✅ 图片已上传: {object_key}")
                    else:
                        st.error("❌ 图片上传失败，请稍后重试")
                        final_image_input = None
                
                if not final_image_input:
                    st.error("❌ 请先选择或上传图片！")
                else:
                    # 验证双图模板的输入格式
                    if is_double_embrace and "|" not in final_image_input:
                        st.error("❌ 爱的拥抱（双图）模板需要两张图片，请使用'|'分隔两个图片URL")
                    else:
                        with st.spinner("🎬 正在生成视频特效，请耐心等待..."):
                            try:
                                video_url = template_2_video(
                                    visual_service,
                                    image_input=final_image_input,
                                    template_id=selected_template_id
                                )
                                
                                if video_url:
                                    st.success("✅ 视频特效生成成功！")
                                    
                                    # 显示生成的视频
                                    try:
                                        st.video(video_url)
                                        st.success("✅ 视频加载成功！")
                                        
                                        # 提供下载链接
                                        st.markdown("---")
                                        st.subheader("📥 下载选项")
                                        st.markdown(f"🔗 [点击下载视频]({video_url})")
                                        st.info("💡 **提示:** 右键点击上方链接，选择'另存为'可将视频文件保存到本地。")
                                        
                                        # 显示特效信息
                                        st.info(f"🎬 **应用特效:** {selected_template_display}")
                                        
                                    except Exception as e:
                                        st.warning(f"⚠️ 视频预览失败: {str(e)}")
                                        st.markdown(f"🔗 [点击下载视频]({video_url})")
                                        
                                else:
                                    st.error("❌ 视频特效生成失败，请检查参数或稍后重试")
                                    
                            except Exception as e:
                                st.error(f"❌ 生成视频特效时出错: {str(e)}")
                                st.info("💡 请检查网络连接和API配置，或稍后重试")
        
        # 特效说明
        with st.expander("🎬 视频特效模板说明", expanded=False):
            st.markdown("""
            **可用视频特效模板：**
            
            🎭 **变身类特效**
            - **变身玩偶**: 将人物转换为可爱的玩偶形象
            - **清凉泳装变身**: 换装为泳装造型
            - **变身兔女郎**: 换装为兔女郎造型
            
            🐾 **召唤坐骑系列**  
            - **召唤坐骑-猪**: 召唤可爱的猪坐骑
            - **召唤坐骑-老虎**: 召唤威武的老虎坐骑
            - **召唤坐骑-龙**: 召唤神秘的龙坐骑
            
            🌸 **特殊效果**
            - **万物生花**: 周围绽放美丽花朵的特效
            - **爱的拥抱**: 温馨的拥抱场景（支持单图和双图）
            
            👥 **环绕特效**
            - **AI美女环绕**: 被美女环绕的特效
            - **AI帅哥环绕**: 被帅哥环绕的特效
            
            👶 **其他特效**
            - **天赐宝宝**: 生成可爱宝宝的特效
            
            **分辨率选择：**
            - **480p版本**: 标准清晰度，生成速度较快
            - **720p版本**: 高清版本，画质更佳但生成时间较长
            
            **使用提示：**
            - 建议使用清晰、主体明确的人物图片
            - 爱的拥抱（双图）模板需要两张图片，用'|'分隔URL
            - 不同模板适合不同类型的图片内容
            - 生成时间可能需要几分钟，请耐心等待
            """)

elif selected_function == "音乐生成":
    st.header("🎵 音乐生成")
    st.markdown("使用火山引擎音乐生成API创建背景音乐")
    st.markdown("接口文档: https://www.volcengine.com/docs/84992/1535146")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        
        # 文本描述
        text_music = st.text_area(
            "音乐描述文本:",
            "现代感十足的商业广告配乐",
            height=100,
            key="text_music",
            help="描述您想要生成的音乐风格和用途"
        )
        
        # 音乐时长
        duration_music = st.slider(
            "音乐时长 (秒)",
            min_value=1,
            max_value=60,
            value=15,
            key="duration_music",
            help="生成音乐的时长，范围1-60秒"
        )
        
        # 音乐风格 (Genre) - 多选
        st.subheader("音乐风格 (Genre)")
        genre_options = [
            "pop(流行)", "rock(摇滚)", "jazz(爵士)", "classical(古典)", "electronic(电子)", "hip-hop(嘻哈)", 
            "country(乡村)", "folk(民谣)", "blues(蓝调)", "reggae(雷鬼)", "latin(拉丁)", "world(世界音乐)",
            "ambient(环境音乐)", "cinematic(电影配乐)", "corporate(企业)", "upbeat(欢快)", "chill(轻松)", "dramatic(戏剧性)"
        ]
        
        selected_genres_display = st.multiselect(
            "选择音乐风格 (最多10个):",
            options=genre_options,
            default=["corporate(企业)"],
            key="genre_music",
            help="选择适合的音乐风格，可多选"
        )
        
        # 提取英文部分用于API调用
        selected_genres = [genre.split('(')[0] for genre in selected_genres_display]
        
        # 限制选择数量
        if len(selected_genres) > 10:
            st.warning("⚠️ 最多只能选择10个风格，请减少选择")
            selected_genres = selected_genres[:10]
        
        # 音乐情绪 (Mood) - 多选
        st.subheader("音乐情绪 (Mood)")
        mood_options = [
            "happy(快乐)", "sad(悲伤)", "energetic(充满活力)", "calm(平静)", "peaceful(宁静)", "soft(柔和)",
            "dramatic(戏剧性)", "mysterious(神秘)", "romantic(浪漫)", "nostalgic(怀旧)", "hopeful(充满希望)",
            "tense(紧张)", "relaxing(放松)", "uplifting(振奋)", "melancholic(忧郁)", "triumphant(胜利)"
        ]
        
        selected_moods_display = st.multiselect(
            "选择音乐情绪 (最多10个):",
            options=mood_options,
            default=["peaceful(宁静)", "soft(柔和)"],
            key="mood_music",
            help="选择音乐要表达的情绪，可多选"
        )
        
        # 提取英文部分用于API调用
        selected_moods = [mood.split('(')[0] for mood in selected_moods_display]
        
        # 限制选择数量
        if len(selected_moods) > 10:
            st.warning("⚠️ 最多只能选择10个情绪，请减少选择")
            selected_moods = selected_moods[:10]
        
        # 乐器 (Instrument) - 多选
        st.subheader("乐器 (Instrument)")
        instrument_options = [
            "piano(钢琴)", "guitar(吉他)", "violin(小提琴)", "drums(鼓)", "bass(贝斯)", "strings(弦乐)",
            "brass(铜管乐)", "woodwind(木管乐)", "synthesizer(合成器)", "organ(管风琴)", "harp(竖琴)",
            "flute(长笛)", "saxophone(萨克斯)", "trumpet(小号)", "cello(大提琴)", "acoustic_guitar(原声吉他)"
        ]
        
        selected_instruments_display = st.multiselect(
            "选择乐器 (最多10个):",
            options=instrument_options,
            default=["piano(钢琴)", "strings(弦乐)"],
            key="instrument_music",
            help="选择想要包含的乐器，可多选"
        )
        
        # 提取英文部分用于API调用
        selected_instruments = [instrument.split('(')[0] for instrument in selected_instruments_display]
        
        # 限制选择数量
        if len(selected_instruments) > 10:
            st.warning("⚠️ 最多只能选择10个乐器，请减少选择")
            selected_instruments = selected_instruments[:10]
        
        # 主题 (Theme) - 多选
        st.subheader("音乐主题 (Theme)")
        theme_options = [
            "every day(日常)", "celebration(庆祝)", "adventure(冒险)", "romance(浪漫)", "nature(自然)",
            "technology(科技)", "business(商务)", "travel(旅行)", "family(家庭)", "friendship(友谊)",
            "success(成功)", "inspiration(励志)", "meditation(冥想)", "workout(健身)", "party(派对)"
        ]
        
        selected_themes_display = st.multiselect(
            "选择音乐主题 (最多10个):",
            options=theme_options,
            default=["every day(日常)"],
            key="theme_music",
            help="选择音乐的主题场景，可多选"
        )
        
        # 提取英文部分用于API调用
        selected_themes = [theme.split('(')[0] for theme in selected_themes_display]
        
        # 限制选择数量
        if len(selected_themes) > 10:
            st.warning("⚠️ 最多只能选择10个主题，请减少选择")
            selected_themes = selected_themes[:10]
        
        # 生成按钮
        generate_button_music = st.button("🎵 生成音乐", key="button_music", type="primary")
    
    with col2:
        st.subheader("生成结果")
        
        # 显示当前选择的参数
        with st.expander("📋 当前参数预览", expanded=True):
            st.write(f"**描述文本:** {text_music}")
            st.write(f"**时长:** {duration_music} 秒")
            st.write(f"**风格:** {', '.join(selected_genres) if selected_genres else '未选择'}")
            st.write(f"**情绪:** {', '.join(selected_moods) if selected_moods else '未选择'}")
            st.write(f"**乐器:** {', '.join(selected_instruments) if selected_instruments else '未选择'}")
            st.write(f"**主题:** {', '.join(selected_themes) if selected_themes else '未选择'}")
        
        if generate_button_music:
            # 验证必要参数
            if not text_music.strip():
                st.error("❌ 请输入音乐描述文本")
            elif not selected_genres:
                st.error("❌ 请至少选择一个音乐风格")
            elif not selected_moods:
                st.error("❌ 请至少选择一个音乐情绪")
            elif not selected_instruments:
                st.error("❌ 请至少选择一个乐器")
            elif not selected_themes:
                st.error("❌ 请至少选择一个音乐主题")
            elif len(selected_genres) > 10 or len(selected_moods) > 10 or len(selected_instruments) > 10 or len(selected_themes) > 10:
                st.error("❌ 每个类别最多只能选择10个选项")
            else:
                # 获取API密钥 - 使用与图像生成相同的密钥
                music_ak = st.session_state.ak
                music_sk = st.session_state.sk
                
                if not music_ak or not music_sk:
                    st.error("❌ 请先在设置页面配置火山引擎API密钥 (VOLC_ACCESSKEY 和 VOLC_SECRETKEY)")
                    st.info("💡 提示：音乐生成使用与图像生成相同的火山引擎API密钥")
                else:
                    with st.spinner("🎵 正在生成音乐，请耐心等待..."):
                        try:
                            set_auth()
                            # 调用音乐生成API
                            audio_url = generation_bgm(
                                ak=music_ak,
                                sk=music_sk,
                                text=text_music,
                                genre=selected_genres,
                                mood=selected_moods,
                                instrument=selected_instruments,
                                theme=selected_themes,
                                Duration=duration_music
                            )
                            
                            if audio_url:
                                st.success("✅ 音乐生成成功！")
                                
                                # 音频播放器 - 直接下载并播放
                                st.subheader("🎵 音频播放器")
                                
                                try:
                                    with st.spinner("🔄 正在下载音频文件..."):
                                        import requests
                                        import tempfile
                                        import os
                                        
                                        # 下载音频文件
                                        response = requests.get(audio_url, timeout=30)
                                        response.raise_for_status()
                                        
                                        # 根据Content-Type确定文件扩展名
                                        content_type = response.headers.get('content-type', '').lower()
                                        if 'mp3' in content_type:
                                            ext = '.mp3'
                                            audio_format = 'audio/mp3'
                                        elif 'wav' in content_type:
                                            ext = '.wav'
                                            audio_format = 'audio/wav'
                                        elif 'ogg' in content_type:
                                            ext = '.ogg'
                                            audio_format = 'audio/ogg'
                                        elif 'mp4' in content_type:
                                            ext = '.mp4'
                                            audio_format = 'audio/mp4'
                                        else:
                                            # 默认为mp3，但也尝试从URL推断
                                            if audio_url.lower().endswith('.wav'):
                                                ext = '.wav'
                                                audio_format = 'audio/wav'
                                            elif audio_url.lower().endswith('.ogg'):
                                                ext = '.ogg'
                                                audio_format = 'audio/ogg'
                                            else:
                                                ext = '.mp3'
                                                audio_format = 'audio/mp3'
                                        
                                        # 直接使用音频字节数据播放
                                        audio_bytes = response.content
                                        st.audio(audio_bytes, format=audio_format)
                                        st.success("✅ 音频加载成功！")
                                        
                                        # 显示文件信息
                                        file_size_kb = len(audio_bytes) / 1024
                                        st.info(f"🎵 **音乐信息:** 时长 {duration_music} 秒 | 文件大小 {file_size_kb:.1f} KB | 格式 {ext[1:].upper()}")
                                        
                                except requests.exceptions.RequestException as e:
                                    st.error(f"❌ 下载音频文件失败: {str(e)}")
                                    st.write("可能的原因：")
                                    st.write("- 网络连接问题")
                                    st.write("- 音频URL已过期")
                                    st.write("- 服务器响应超时")
                                    
                                except Exception as e:
                                    st.error(f"❌ 音频播放失败: {str(e)}")
                                    st.write("可能的原因：")
                                    st.write("- 音频文件格式不支持")
                                    st.write("- 文件损坏或不完整")
                                
                                # 提供下载链接
                                st.markdown("---")
                                st.subheader("📥 下载选项")
                                st.markdown(f"🔗 [点击下载音乐文件]({audio_url})")
                                st.info("💡 **提示:** 右键点击上方链接，选择'另存为'可将音频文件保存到本地。")
                                
                                # 调试信息（可选展开）
                                with st.expander("🔍 调试信息", expanded=False):
                                    st.code(f"音频URL: {audio_url}")
                                    try:
                                        response_info = requests.head(audio_url, timeout=10)
                                        st.write(f"**HTTP状态码:** {response_info.status_code}")
                                        st.write(f"**Content-Type:** {response_info.headers.get('content-type', 'unknown')}")
                                        content_length = response_info.headers.get('content-length')
                                        if content_length:
                                            st.write(f"**文件大小:** {int(content_length)/1024:.1f} KB")
                                    except Exception as e:
                                        st.write(f"**无法获取文件信息:** {str(e)}")
                                
                            else:
                                st.error("❌ 音乐生成失败，请检查参数或稍后重试")
                                
                        except Exception as e:
                            st.error(f"❌ 生成音乐时出错: {str(e)}")
                            st.info("💡 请检查API密钥是否正确，或稍后重试")

elif selected_function == "TTS":
    st.header("🗣️ 文本转语音 (TTS)")
    st.markdown("TTS功能开发中...")
    st.info("💡 该功能正在开发中，敬请期待！")

elif selected_function == "数字人(Omni_Human)":
    st.header("👤 数字人(Omni_Human)")
    st.markdown("接口文档: https://www.volcengine.com/docs/85128/1580768")
    st.markdown("💡 数字人功能可以根据输入的图片和音频生成数字人视频")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        
        # 图片输入
        st.subheader("📷 人物图片")
        input_method_omni = st.radio("选择图片来源", ("URL", "上传图片"), key="input_method_omni")
        image_url_omni = None
        uploaded_file_omni = None

        if input_method_omni == "URL":
            image_url_omni = st.text_input(
                "输入人物图片 URL:", 
                "https://qwer123.tos-cn-beijing.volces.com/omnihuman-image.jpg", 
                key="image_url_omni",
                help="请输入清晰的人物正面照片URL"
            )
        else:
            uploaded_file_omni = st.file_uploader(
                "上传人物图片", 
                type=["png", "jpg", "jpeg"], 
                key="file_uploader_omni",
                help="请上传清晰的人物正面照片"
            )
        
        # 音频输入
        st.subheader("🎵 音频文件")
        audio_input_method = st.radio("选择音频来源", ("URL", "上传音频"), key="audio_input_method")
        audio_url_omni = None
        uploaded_audio_omni = None
        
        if audio_input_method == "URL":
            audio_url_omni = st.text_input(
                "输入音频 URL:", 
                "https://qwer123.tos-cn-beijing.volces.com/audio-002.m4a", 
                key="audio_url_omni",
                help="支持 mp3, wav, m4a 等格式"
            )
        else:
            uploaded_audio_omni = st.file_uploader(
                "上传音频文件", 
                type=["mp3", "wav", "m4a", "aac"], 
                key="file_uploader_audio_omni",
                help="支持 mp3, wav, m4a, aac 等格式"
            )
        
        # 生成按钮
        col_check, col_generate = st.columns(2)
        
        with col_check:
            check_button_omni = st.button("🔍 前置检查", key="check_button_omni", help="检查图片是否适合生成数字人")
        
        with col_generate:
            generate_button_omni = st.button("🎬 生成数字人视频", key="generate_button_omni", type="primary")
    
    with col2:
        st.subheader("预览和生成结果")
        
        # 预览区域
        preview_col1, preview_col2 = st.columns(2)
        
        with preview_col1:
            st.write("**图片预览**")
            preview_image_omni = None
            if input_method_omni == "URL" and image_url_omni:
                preview_image_omni = image_url_omni
            elif input_method_omni == "上传图片" and uploaded_file_omni is not None:
                # Generate unique object key for the uploaded file 
                object_key = f"uploads/omni_human_{int(time.time())}_{uploaded_file_omni.name}"
                # Upload file to TOS
                upload_url = upload_to_tos(object_key, uploaded_file_omni.getvalue())
                if upload_result:
                    st.success(f"✅ 文件已成功上传到TOS: {object_key}")
                else:
                    st.warning("⚠️ 文件上传到TOS失败，但仍可继续使用")
                
                preview_image_omni = upload_url
            
            if preview_image_omni is not None:
                st.image(preview_image_omni, caption="人物图片", use_container_width=True)
            else:
                st.info("请上传或输入人物图片")
        
        with preview_col2:
            st.write("**音频预览**")
            if audio_input_method == "URL" and audio_url_omni:
                try:
                    st.audio(audio_url_omni)
                    st.success("✅ 音频URL有效")
                except Exception as e:
                    st.warning(f"⚠️ 无法预览音频: {str(e)}")
            elif audio_input_method == "上传音频" and uploaded_audio_omni is not None:
                object_key = f"uploads/omni_human_{int(time.time())}_{uploaded_audio_omni.name}"
                # Upload file to TOS
                upload_url = upload_to_tos(object_key, uploaded_audio_omni.getvalue())
                if upload_result:
                    st.success(f"✅ 文件已成功上传到TOS: {object_key}")
                else:
                    st.warning("⚠️ 文件上传到TOS失败，但仍可继续使用")

                st.audio(upload_url)
                st.success("✅ 音频文件已上传")
            else:
                st.info("请上传或输入音频文件")
        
        # 前置检查结果
        if check_button_omni:
            # 验证输入
            final_image_url = None
            if input_method_omni == "URL" and image_url_omni:
                final_image_url = image_url_omni
            elif input_method_omni == "上传图片" and uploaded_file_omni is not None:
                # 对于上传的图片，这里简化处理，实际应该上传到云存储获取URL
                st.warning("⚠️ 上传图片功能需要先上传到云存储获取URL，当前仅支持URL输入进行前置检查")
                final_image_url = None
            
            if not final_image_url:
                st.error("❌ 请先输入有效的图片URL进行前置检查")
            else:
                with st.spinner("🔍 正在进行前置检查..."):
                    try:
                        check_result = omni_human_pre_test(visual_service, final_image_url)
                        
                        if check_result == 1:
                            st.success("✅ 前置检查通过！图片适合生成数字人视频")
                            st.session_state.omni_check_passed = True
                            st.session_state.omni_checked_image_url = final_image_url
                        else:
                            st.error(f"❌ 前置检查未通过，检查结果: {check_result}")
                            st.warning("请尝试使用以下类型的图片：")
                            st.write("- 清晰的人物正面照")
                            st.write("- 人脸清晰可见")
                            st.write("- 光线充足")
                            st.write("- 背景简洁")
                            st.session_state.omni_check_passed = False
                            
                    except Exception as e:
                        st.error(f"❌ 前置检查失败: {str(e)}")
                        st.session_state.omni_check_passed = False
        
        # 生成数字人视频
        if generate_button_omni:
            # 检查是否已通过前置检查
            if not st.session_state.get('omni_check_passed', False):
                st.error("❌ 请先进行前置检查并确保检查通过")
            else:
                # 准备最终的图片和音频URL
                final_image_url = st.session_state.get('omni_checked_image_url')
                final_audio_url = None
                
                if audio_input_method == "URL" and audio_url_omni:
                    final_audio_url = audio_url_omni
                elif audio_input_method == "上传音频" and uploaded_audio_omni is not None:
                    # 对于上传的音频，这里简化处理，实际应该上传到云存储获取URL
                    st.warning("⚠️ 上传音频功能需要先上传到云存储获取URL，当前仅支持URL输入")
                    final_audio_url = None
                
                if not final_image_url or not final_audio_url:
                    st.error("❌ 请确保图片和音频URL都已正确输入")
                else:
                    with st.spinner("🎬 正在生成数字人视频，请耐心等待..."):
                        try:
                            video_url = omni_human(visual_service, final_image_url, final_audio_url)
                            
                            if video_url:
                                st.success("✅ 数字人视频生成成功！")
                                
                                # 显示生成的视频
                                st.subheader("🎬 生成的数字人视频")
                                
                                try:
                                    # 下载视频到本地临时文件
                                    import requests
                                    import tempfile
                                    import os
                                    
                                    with st.spinner("📥 正在下载视频文件..."):
                                        # 创建临时文件
                                        temp_dir = tempfile.gettempdir()
                                        temp_video_path = os.path.join(temp_dir, f"digital_human_video_{int(time.time())}.mp4")
                                        
                                        # 下载视频
                                        response = requests.get(video_url, stream=True, timeout=60)
                                        response.raise_for_status()
                                        
                                        with open(temp_video_path, 'wb') as f:
                                            for chunk in response.iter_content(chunk_size=8192):
                                                if chunk:
                                                    f.write(chunk)
                                    
                                    # 使用本地文件显示视频
                                    st.video(temp_video_path)
                                    st.success("✅ 视频加载成功！")
                                    
                                    # 提供下载功能
                                    st.markdown("---")
                                    st.subheader("📥 下载选项")
                                    
                                    # 读取视频文件用于下载
                                    with open(temp_video_path, 'rb') as video_file:
                                        video_bytes = video_file.read()
                                        st.download_button(
                                            label="📥 下载数字人视频",
                                            data=video_bytes,
                                            file_name=f"digital_human_video_{int(time.time())}.mp4",
                                            mime="video/mp4"
                                        )
                                    
                                    st.info("💡 **提示:** 点击上方按钮可将视频文件下载到本地。")
                                    
                                    # 显示视频信息
                                    with st.expander("🔍 视频信息", expanded=False):
                                        st.code(f"原始视频URL: {video_url}")
                                        st.code(f"本地临时文件: {temp_video_path}")
                                        try:
                                            file_size = os.path.getsize(temp_video_path)
                                            st.write(f"**文件大小:** {file_size/(1024*1024):.1f} MB")
                                            st.write(f"**文件格式:** MP4")
                                        except Exception as e:
                                            st.write(f"**无法获取视频详细信息:** {str(e)}")
                                    
                                    # 清理临时文件（可选，系统会自动清理）
                                    try:
                                        # 延迟删除，让用户有时间查看
                                        import threading
                                        def cleanup_temp_file():
                                            import time
                                            time.sleep(300)  # 5分钟后删除
                                            try:
                                                if os.path.exists(temp_video_path):
                                                    os.remove(temp_video_path)
                                            except:
                                                pass
                                        
                                        cleanup_thread = threading.Thread(target=cleanup_temp_file)
                                        cleanup_thread.daemon = True
                                        cleanup_thread.start()
                                    except:
                                        pass
                                    
                                except Exception as e:
                                    st.warning(f"⚠️ 视频下载或预览失败: {str(e)}")
                                    st.write("**可能的原因:**")
                                    st.write("- 签名URL已过期")
                                    st.write("- 网络连接问题")
                                    st.write("- 视频文件较大，下载超时")
                                    st.write("- 磁盘空间不足")
                                    
                                    # 仍然提供原始下载链接作为备选
                                    st.markdown("---")
                                    st.subheader("📥 备选下载方式")
                                    st.markdown(f"🔗 [点击下载数字人视频]({video_url})")
                                    st.info("💡 **提示:** 如果上述方法失败，请尝试右键点击链接另存为。")
                                
                            else:
                                st.error("❌ 数字人视频生成失败，请检查参数或稍后重试")
                                
                        except Exception as e:
                            st.error(f"❌ 生成数字人视频时出错: {str(e)}")
                            st.info("💡 请检查网络连接和API配置，或稍后重试")
        
        # 使用说明
        with st.expander("📖 使用说明", expanded=False):
            st.markdown("""
            **数字人生成步骤：**
            
            1. **准备素材**
               - 人物图片：清晰的正面照，人脸清晰可见
               - 音频文件：支持 mp3, wav, m4a 等格式
            
            2. **前置检查**
               - 点击"前置检查"按钮验证图片是否适合
               - 只有检查通过的图片才能用于生成数字人
            
            3. **生成视频**
               - 确保前置检查通过后，点击"生成数字人视频"
               - 生成过程可能需要几分钟，请耐心等待
            
            **注意事项：**
            - 图片要求：人物正面照，光线充足，背景简洁
            - 音频要求：清晰的语音，建议时长不超过60秒
            - 当前版本仅支持URL输入，上传功能需要配置云存储
            
            **技术支持：**
            - 如遇到问题，请检查API密钥配置
            - 确保网络连接稳定
            - 建议使用Chrome或Firefox浏览器
            """)

elif selected_function == "设置":
    st.header("⚙️ 系统设置")
    st.markdown("在这里配置您的API密钥和其他系统设置")
    
    # 创建两列布局
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("API 密钥配置")
        
        # 获取当前环境变量值
        current_volc_ak = os.environ.get("VOLC_ACCESSKEY", "")
        current_volc_sk = os.environ.get("VOLC_SECRETKEY", "")
        current_api_key = os.environ.get("API_KEY", "")
        
        # 创建表单
        with st.form("api_settings_form"):
            st.markdown("**火山引擎 Visual API 配置**")
            volc_ak = st.text_input(
                "VOLC_ACCESSKEY",
                value=current_volc_ak,
                type="password",
                help="火山引擎 Access Key"
            )
            
            volc_sk = st.text_input(
                "VOLC_SECRETKEY", 
                value=current_volc_sk,
                type="password",
                help="火山引擎 Secret Key"
            )
            
            st.markdown("**方舟 API 配置**")
            api_key = st.text_input(
                "API_KEY",
                value=current_api_key,
                type="password", 
                help="方舟 API Key"
            )
                      
            # 提交按钮
            submitted = st.form_submit_button("保存设置", type="primary")
            
            if submitted:
                # 更新环境变量
                if volc_ak:
                    os.environ["VOLC_ACCESSKEY"] = volc_ak
                if volc_sk:
                    os.environ["VOLC_SECRETKEY"] = volc_sk
                if api_key:
                    os.environ["API_KEY"] = api_key
                
                # 清除缓存的服务实例，强制重新创建
                st.cache_resource.clear()
                
                # 重新初始化服务实例，使其立即使用新的API密钥
                try:
                    # 重新执行全局变量赋值，使用新的API密钥
                    st.session_state.visual_service = get_visual_service()
                    st.session_state.ark_client = get_ark_client()
                    
                    st.success("✅ 设置已保存并立即生效！")
                    st.info("💡 提示：为了安全起见，建议在系统环境变量中设置这些密钥。")
                except Exception as e:
                    st.error(f"❌ 重新初始化服务时出错: {str(e)}")
                    st.warning("⚠️ 设置已保存，但可能需要刷新页面才能生效。")
    
    with col2:
        st.subheader("设置说明")
        
        st.markdown("""
        **如何获取API密钥：**
        
        🔥 **火山引擎 Visual API**
        1. 访问 [火山引擎控制台](https://console.volcengine.com/)
        2. 进入"访问控制" → "访问密钥"
        3. 创建或查看 AccessKey 和 SecretKey
        
        🚀 **方舟 API**
        1. 访问 [方舟控制台](https://console.volcengine.com/ark/)
        2. 进入"API管理"
        3. 创建或查看 API Key
        
        💡 **注意：** 音乐生成功能使用与图像生成相同的火山引擎API密钥
        
        **安全建议：**
        - 不要在代码中硬编码密钥
        - 定期轮换API密钥
        - 使用环境变量存储敏感信息
        """)
        
        # 显示当前配置状态
        st.subheader("当前配置状态")
        
        # 检查配置状态
        volc_status = "✅ 已配置" if current_volc_ak and current_volc_sk else "❌ 未配置"
        ark_status = "✅ 已配置" if current_api_key else "❌ 未配置"
        
        st.markdown(f"""
        **火山引擎 Visual API:** {volc_status}
        (图像生成和音乐生成共用此API密钥)
        
        **方舟 API:** {ark_status}
        """)
        
        # 测试连接按钮
        if st.button("🔍 测试连接", help="测试API密钥是否有效"):
            with st.spinner("正在测试连接..."):
                try:
                    # 这里可以添加实际的API测试逻辑
                    # 暂时显示配置状态
                    if current_volc_ak and current_volc_sk and current_api_key:
                        st.success("✅ 所有API密钥已配置")
                    else:
                        missing = []
                        if not current_volc_ak or not current_volc_sk:
                            missing.append("火山引擎 Visual API")
                        if not current_api_key:
                            missing.append("方舟 API")
                        st.warning(f"⚠️ 缺少配置: {', '.join(missing)}")
                except Exception as e:
                    st.error(f"❌ 连接测试失败: {str(e)}")

# if __name__ == "__main__":
#     from streamlit.web import cli as stcli
#     import sys
#     sys.argv = ["streamlit", "run", "app.py"]
#     stcli.main()