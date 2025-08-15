import streamlit as st
from api_modules.jimeng_image import t2i_jimeng_v31

def render_jimeng_t2i_v31(visual_service):
    """既梦AI-文生图3.1页面"""
    st.header("既梦AI 图像生成 3.1")
    st.markdown("""
   文生图3.1是与即梦同源的文生图能力，该版本重点实现画面效果呈现升级，在画面美感塑造、风格精准多样及画面细节丰富度方面提升显著，同时兼具文字响应效果。
    """)
    st.markdown("接口文档: https://www.volcengine.com/docs/85621/1770977")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        style_presets = {
            "水下摄影":"水下摄影,美女在海里潜水，抬头往上看,斑驳的阳光洒在脸上",
            "棚拍摄影": "棚拍摄影,美女写真，清凉暑夏"
        }
        
        # 添加自定义选项到开头
        style_presets = {"自定义": "电影质感，小女孩在商店", **style_presets}
        
        # 初始化session state用于存储提示词
        if 'prompt_t2i_jimeng_v31' not in st.session_state:
            st.session_state.prompt_t2i_jimeng_v31 = style_presets["自定义"]

        # 风格选择回调函数
        def update_jimeng_v31_prompt():
            selected_style = st.session_state.jimeng_v31_style_selector
            if selected_style in style_presets:
                st.session_state.prompt_t2i_jimeng_v31 = style_presets[selected_style]

        # 风格选择下拉框
        selected_jimeng_v31_style = st.selectbox(
            "选择风格类型",
            options=list(style_presets.keys()),
            key="jimeng_v31_style_selector",
            on_change=update_jimeng_v31_prompt
        )
        
        # 提示词输入框，使用session state中的值
        prompt_t2i_jimeng_v31 = st.text_area("输入文生图提示词:", key="prompt_t2i_jimeng_v31", height=100)
        seed_t2i_jimeng_v31 = st.number_input("Seed", value=-1, key="seed_t2i_jimeng_v31")
        width_t2i_jimeng_v31 = st.number_input("Width", value=512, key="width_t2i_jimeng_v31")
        height_t2i_jimeng_v31 = st.number_input("Height", value=512, key="height_t2i_jimeng_v31")
        use_pre_llm_jimeng_v31 = st.checkbox("Use Pre-LLM (开启文本扩写，会针对输入prompt进行扩写优化)", value=True, key="use_pre_llm_jimeng_v31")
        generate_button_t2i_jimeng_v31 = st.button("生成图片", key="button_t2i_jimeng_v31")

    with col2:
        st.subheader("生成结果")
        if generate_button_t2i_jimeng_v31:
            with st.spinner("Generating..."):
                image_url = t2i_jimeng_v31(visual_service, prompt_t2i_jimeng_v31, seed_t2i_jimeng_v31, width_t2i_jimeng_v31, height_t2i_jimeng_v31, use_pre_llm_jimeng_v31)
                if image_url:
                    st.image(image_url, caption="Generated Image")
                else:
                    st.error("图像生成失败，请检查参数或稍后重试")