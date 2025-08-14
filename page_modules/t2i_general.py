import streamlit as st
from api_modules.visual_image import t2i_30

def render_t2i_general(visual_service):
    """通用3.0-文生图页面"""
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