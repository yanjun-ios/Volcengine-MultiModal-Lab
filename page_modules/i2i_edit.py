import streamlit as st
import base64
from api_modules.visual_image import i2i_seed_edit_30

def render_i2i_edit(visual_service):
    """图生图3.0-指令编辑页面"""
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