import streamlit as st
import base64
from api_modules.ark_image import ark_i2i

def render_ark_i2i(ark_client):
    """方舟-图像编辑3.0页面"""
    st.header("方舟-图像编辑3.0")
    st.markdown("接口文档: https://www.volcengine.com/docs/82379/1666946")
    st.markdown("💡 使用方舟API进行图像编辑，支持多种编辑指令")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        
        # 模型选择 - 根据 Byteplus 开关状态获取模型
        byteplus_enabled = st.session_state.get("byteplus_ark_enabled", False)
        
        if byteplus_enabled:
            # 从设置中获取 Byteplus 图生图模型
            default_model = st.session_state.get("byteplus_i2i_model", "seededit-3-0-i2i-250628")
        else:
            # 使用默认的 Volcengine 模型
            default_model = "doubao-seededit-3-0-i2i-250628"
        
        model_ark_i2i = st.text_input(
            "输入模型名称",
            value=default_model,
            key="model_ark_i2i",
            help="当前使用的模型名称"
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