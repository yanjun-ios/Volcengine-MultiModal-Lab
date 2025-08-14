import streamlit as st
import base64
import time
from api_modules.visual_image import i21_multi_style

def render_image_effects(visual_service, upload_to_tos):
    """智能绘图 - 图像特效页面"""
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