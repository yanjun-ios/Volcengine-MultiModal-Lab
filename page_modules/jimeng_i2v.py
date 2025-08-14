import streamlit as st
import base64
from api_modules.jimeng_video import i2v_jimeng_s20_pro

def render_jimeng_i2v(visual_service):
    """既梦AI 图生视频页面"""
    st.header("既梦AI 图生视频")
    st.markdown("""
产品优势
**高语义遵循**：具有极高的"提示词遵循能力"，支持输入很复杂的提示词（例如镜头切换、人物连续动作、情绪演绎、运镜控制）
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