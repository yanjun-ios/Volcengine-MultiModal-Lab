import streamlit as st
from api_modules.jimeng_video import t2v_jimeng_s20_pro

def render_jimeng_t2v(visual_service):
    """既梦AI 文生视频页面"""
    st.header("既梦AI 文生视频")
    st.markdown("""
产品优势
**高语义遵循**：具有极高的"提示词遵循能力"，支持输入很复杂的提示词（例如镜头切换、人物连续动作、情绪演绎、运镜控制）
**动效流畅**：动作效果流畅自然，整体视频效果结构稳定
**画面一致性**：支持保持风格及主体一致性
    """)
    st.markdown("接口文档: https://www.volcengine.com/docs/85621/1538636")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        prompt_t2v_jimeng = st.text_area(
            "输入文生视频提示词:", 
            "衣服爆发出一团白色泡沫状的物体，仿佛瞬间膨胀或炸裂开来；衣服被气球完全包裹，气球的颜色以橙色、白色和银色为主，层层叠叠地围绕身体。越来越多不断生长；衣服逐渐化作一团不断扩展的巨大银色丝球，闪烁着光泽，呈现出无尽生长的动态；衣服像气球般迅速膨胀，逐渐充满周围的空间，随后开始缓缓泄气；衣服变成很多个银色的气球，飞起来，然后散落在地面", 
            height=100, 
            key="prompt_t2v_jimeng"
        )
        seed_t2v_jimeng = st.number_input("Seed", value=-1, key="seed_t2v_jimeng")
        aspect_ratio_t2v_jimeng = st.selectbox("Aspect Ratio", ["16:9", "9:16", "1:1"], key="aspect_ratio_t2v_jimeng")
        generate_button_t2v_jimeng = st.button("生成视频", key="button_t2v_jimeng")

    with col2:
        st.subheader("生成结果")
        if generate_button_t2v_jimeng:
            with st.spinner("Generating..."):
                video_url = t2v_jimeng_s20_pro(visual_service, prompt_t2v_jimeng, seed_t2v_jimeng, aspect_ratio_t2v_jimeng)
                if video_url:
                    st.video(video_url)