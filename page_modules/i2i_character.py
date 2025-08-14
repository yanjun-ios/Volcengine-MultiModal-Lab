import streamlit as st
import base64
from api_modules.visual_image import i2i_30_single_ip

def render_i2i_character(visual_service):
    """图生图3.0-角色特征保持页面"""
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