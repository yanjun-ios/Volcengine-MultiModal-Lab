import streamlit as st
from api_modules.visual_image import i2i_30_portrait

def render_i2i_portrait(visual_service):
    """图生图3.0-人像写真页面"""
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