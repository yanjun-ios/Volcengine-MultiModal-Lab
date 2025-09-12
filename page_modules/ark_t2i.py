import streamlit as st
from api_modules.ark_image import ark_t2i

def render_ark_t2i(ark_client):
    """方舟-文生图3.0页面"""
    st.header("方舟-文生图3.0")
    st.markdown("接口文档: https://www.volcengine.com/docs/82379/1541523")
    st.markdown("💡 使用方舟API进行文生图，支持多种尺寸和参数调节")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        
        # 模型选择 - 根据 Byteplus 开关状态获取模型
        byteplus_enabled = st.session_state.get("byteplus_ark_enabled", False)
        
        if byteplus_enabled:
            # 从设置中获取 Byteplus 文生图模型
            default_model = st.session_state.get("byteplus_t2i_model", "seedream-3-0-t2i-250415")
        else:
            # 使用默认的 Volcengine 模型
            default_model = "doubao-seedream-3-0-t2i-250415"
        
        model_ark_t2i = st.text_input(
            "输入模型名称",
            value=default_model,
            key="model_ark_t2i",
            help="当前使用的模型名称"
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