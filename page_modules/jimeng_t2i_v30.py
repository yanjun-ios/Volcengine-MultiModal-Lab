import streamlit as st
from api_modules.jimeng_image import t2i_jimeng_v30

def render_jimeng_t2i_v30(visual_service):
    """既梦AI-文生图3.0页面"""
    st.header("既梦AI 图像生成 3.0")
    st.markdown("""
   文生图3.0是即梦同源的文生图能力，在文字响应准确度、图文排版、层次美感和语义理解能力上相较之前版本均有显著提升，人像质感更逼真，且支持输出高清大图。此外，在文字响应更精准的基础下，还支持响应大小字、各类艺术字体和不同字重。
    """)
    st.markdown("接口文档: https://www.volcengine.com/docs/85621/1770795")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        style_presets = {
            "精准文字":"3D卡通渲染风格，春日露营主题场景，竖版海报构图，画面中心是一片绿意盎然的草地、小岛平台中央搭建了奶油色天幕帐篷，帐篷周围布置有野餐垫、藤编桌椅、花束、饮品、果盘等春游元素。中央大标题“春日出逃计划”副标题“开启元气好心情”。底部左侧是手写风格文案：“把春天装进行囊，把快乐播进生活”有下角是活动信息：“4.10-4.30快来打卡春日限定乐园”。底部信息文字放置在绿色渐变曲线底座上，整体色调为蓝绿系主色，搭配明亮橙黄点缀，活泼、治愈、轻松自然。",
            "高清质感": "一个长发美女，白色长裙，海边，微风，电影质感，时尚摄影"
        }
        
        # 添加自定义选项到开头
        style_presets = {"自定义": "一只可爱的猫,冷色调,浅景深/背景虚化", **style_presets}
        
        # 初始化session state用于存储提示词
        if 'prompt_t2i_jimeng_v30' not in st.session_state:
            st.session_state.prompt_t2i_jimeng_v30 = style_presets["自定义"]

        # 风格选择回调函数
        def update_jimeng_v30_prompt():
            selected_style = st.session_state.jimeng_v30_style_selector
            if selected_style in style_presets:
                st.session_state.prompt_t2i_jimeng_v30 = style_presets[selected_style]

        # 风格选择下拉框
        selected_jimeng_v30_style = st.selectbox(
            "选择风格类型",
            options=list(style_presets.keys()),
            key="jimeng_v30_style_selector",
            on_change=update_jimeng_v30_prompt
        )
        
        # 提示词输入框，使用session state中的值
        prompt_t2i_jimeng_v30 = st.text_area("输入文生图提示词:", key="prompt_t2i_jimeng_v30", height=100)
        seed_t2i_jimeng_v30 = st.number_input("Seed", value=-1, key="seed_t2i_jimeng_v30")
        width_t2i_jimeng_v30 = st.number_input("Width", value=512, key="width_t2i_jimeng_v30")
        height_t2i_jimeng_v30 = st.number_input("Height", value=512, key="height_t2i_jimeng_v30")
        use_pre_llm_jimeng_v30 = st.checkbox("Use Pre-LLM (开启文本扩写，会针对输入prompt进行扩写优化)", value=True, key="use_pre_llm_jimeng_v30")
        generate_button_t2i_jimeng_v30 = st.button("生成图片", key="button_t2i_jimeng_v30")

    with col2:
        st.subheader("生成结果")
        if generate_button_t2i_jimeng_v30:
            with st.spinner("Generating..."):
                image_url = t2i_jimeng_v30(visual_service, prompt_t2i_jimeng_v30, seed_t2i_jimeng_v30, width_t2i_jimeng_v30, height_t2i_jimeng_v30, use_pre_llm_jimeng_v30)
                if image_url:
                    st.image(image_url, caption="Generated Image")
                else:
                    st.error("图像生成失败，请检查参数或稍后重试")