import streamlit as st
from api_modules.jimeng_image import t2i_jimeng

def render_jimeng_t2i_21(visual_service):
    """既梦AI-文生图2.1页面"""
    st.header("既梦AI 图像生成")
    st.markdown("""
    产品优势
**文字生成能力**：支持生成准确的中文汉字和英文字母; 
**构图**：整体在景别、视角方面变化多样性提升明显，画面层次感增强;
**光影：去除了刻意的光线表达，画面表现更加真实自然; 
**色彩**：画面色调统一性增强，去除了大部分高对比混乱杂色; 
**质感**：人物皮肤磨皮感及油腻感减弱，人像、动物及材质类类纹理质感表现更加真实细腻; 
**细节丰富度**：简化了过于繁琐的画面元素，画面整体表现现更加具有层次感、秩序感; 
    """)
    st.markdown("接口文档: https://www.volcengine.com/docs/85128/125990")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        style_presets = {
            "文字海报":"制作一张vlog视频封面。马卡龙配色，美女旅游照片+色块的拼贴画风格，主文案是“威海旅游vlog”，副文案是“特种兵一日游 被低估的旅游城市”，海报主体是一个穿着短裙、梳双马尾的少女，人物白色描边",
            "浪漫水彩":"工笔画风格，三维古风，东方禅意，航拍高角度视角，捕捉了海底极小人物的奔跑追逐；构图大面积留白和丰富的光影，背景以水墨晕染展现水中阳光的多彩折射，现实与虚拟相结合的思考，水墨风格，蓝绿色调，逆光和辉光效果增强冷暖对比，高角度拍摄景深感，整体画面高清，画质通透，发光呈现幽静空灵感",
            "胶片梦核": "过曝，强对比，夜晚，雪地里，巨大的黄色浴缸，小狗泡澡带墨镜，在喝红酒，胶片摄影，毛刺质感，复古滤镜，夜晚，过度曝光，古早，70年代摄影，复古老照片，闪光灯拍摄，闪光灯效果，过曝，过度曝光，闪光灯过曝，极简，高饱和复古色，70s vintage photography, vintage, retro style"
        }
        
        # 添加自定义选项到开头
        style_presets = {"自定义": "一只可爱的猫", **style_presets}
        
        # 初始化session state用于存储提示词
        if 'prompt_t2i_jimeng' not in st.session_state:
            st.session_state.prompt_t2i_jimeng = style_presets["自定义"]

        # 风格选择回调函数
        def update_jimeng_prompt():
            selected_style = st.session_state.jimeng_style_selector
            if selected_style in style_presets:
                st.session_state.prompt_t2i_jimeng = style_presets[selected_style]

        # 风格选择下拉框
        selected_jimeng_style = st.selectbox(
            "选择风格类型",
            options=list(style_presets.keys()),
            key="jimeng_style_selector",
            on_change=update_jimeng_prompt
        )
        
        # 提示词输入框，使用session state中的值
        prompt_t2i_jimeng = st.text_area("输入文生图提示词:", key="prompt_t2i_jimeng", height=100)
        seed_t2i_jimeng = st.number_input("Seed", value=-1, key="seed_t2i_jimeng")
        width_t2i_jimeng = st.number_input("Width", value=512, key="width_t2i_jimeng")
        height_t2i_jimeng = st.number_input("Height", value=512, key="height_t2i_jimeng")
        use_pre_llm_jimeng = st.checkbox("Use Pre-LLM (开启文本扩写，会针对输入prompt进行扩写优化)", value=True, key="use_pre_llm_jimeng")
        use_sr_jimeng = st.checkbox("Use SR (文生图+AIGC超分)", value=True, key="use_sr_jimeng")
        return_url_t2i_jimeng = st.checkbox("Return URL", value=True, key="return_url_t2i_jimeng")
        generate_button_t2i_jimeng = st.button("生成图片", key="button_t2i_jimeng")

    with col2:
        st.subheader("生成结果")
        if generate_button_t2i_jimeng:
            with st.spinner("Generating..."):
                image_url = t2i_jimeng(visual_service, prompt_t2i_jimeng, seed_t2i_jimeng, width_t2i_jimeng, height_t2i_jimeng, return_url_t2i_jimeng, use_pre_llm_jimeng, use_sr_jimeng)
                if image_url:
                    st.image(image_url, caption="Generated Image")