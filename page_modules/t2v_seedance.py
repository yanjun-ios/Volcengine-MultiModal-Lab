import streamlit as st
from api_modules.ark_video import t2v_seedance
from utils.llm_prompt_optmize import optimize_stream

def render_t2v_seedance(ark_client):
    """Seedance 1.0 文生视频页面"""
    st.header("Seedance 1.0 文生视频")
    st.markdown("接口文档: https://www.volcengine.com/docs/82379/1520757")
    st.markdown("Seedance-pro 提示词指南: https://bytedance.larkoffice.com/docx/Svl9dMwvCokzZHxamTWcCz5en1f?from=from_copylink")
    st.markdown("Seedance-lit 提示词指南: https://bytedance.larkoffice.com/docx/UQoSd3NEvoAkghxAl0ccjdplnhR?from=from_copylink")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        
        # 模型选择
        model_t2v = st.selectbox(
            "选择模型",
            ["doubao-seedance-1-0-pro-250528", "doubao-seedance-1-0-lite-t2v-250428"],
            key="model_t2v"
        )
        
        # 基础提示词 - 使用优化后的值或默认值
        if 'optimized_prompt_t2v' in st.session_state and st.session_state.optimized_prompt_t2v:
            default_prompt_t2v = st.session_state.optimized_prompt_t2v
        else:
            default_prompt_t2v = "一只可爱的小猫在花园里玩耍"
            
        # 创建标题和优化链接
        st.write("输入视频描述提示词:")
            
        base_prompt_t2v = st.text_area(
            "视频描述提示词",
            value=default_prompt_t2v,
            height=100,
            key="base_prompt_t2v",
            label_visibility="collapsed"
        )
        optimize_button_t2v = st.button("一键优化", key="optimize_t2v", help="使用AI优化您的提示词", type="secondary")
        
        # 处理提示词优化
        if optimize_button_t2v:
            if base_prompt_t2v.strip():
                with st.spinner("正在优化提示词..."):
                    try:
                        # 流式显示优化过程
                        placeholder = st.empty()
                        optimized_text = ""
                        
                        for chunk in optimize_stream(ark_client, "t2v", base_prompt_t2v):
                            optimized_text += chunk
                            # 实时显示优化进度
                            placeholder.text_area(
                                "优化中...",
                                value=optimized_text,
                                height=100,
                                disabled=True
                            )
                        
                        # 优化完成后保存结果并重新运行
                        if optimized_text.strip():
                            st.session_state.optimized_prompt_t2v = optimized_text.strip()
                            placeholder.empty()  # 清除临时显示
                            st.success("提示词优化完成！")
                            st.rerun()
                        else:
                            placeholder.empty()
                            st.error("优化失败，请稍后重试")
                            
                    except Exception as e:
                        st.error(f"优化提示词时出错: {str(e)}")
            else:
                st.warning("请先输入提示词再进行优化")
        
        # 视频参数
        st.subheader("视频参数")
        
        resolution_t2v = st.selectbox(
            "分辨率",
            ["480p", "720p", "1080p"],
            index=1,
            key="resolution_t2v"
        )
        
        ratio_t2v = st.selectbox(
            "宽高比",
            ["21:9", "16:9", "4:3", "1:1", "3:4", "9:16", "9:21", "keep_ratio", "adaptive"],
            index=1,
            key="ratio_t2v"
        )
        
        duration_t2v = st.selectbox(
            "时长",
            ["5", "10"],
            key="duration_t2v"
        )
        
        fps_t2v = st.selectbox(
            "帧率",
            [16, 24],
            index=1,
            key="fps_t2v"
        )
        
        watermark_t2v = st.checkbox("添加水印", value=True, key="watermark_t2v")
        
        seed_t2v = st.number_input("Seed", value=-1, key="seed_t2v")
        
        camera_fixed_t2v = st.checkbox("固定镜头", value=False, key="camera_fixed_t2v")
        
        generate_button_t2v = st.button("生成视频", key="button_t2v")
    
    with col2:
        st.subheader("生成结果")
        
        if generate_button_t2v:
            with st.spinner("正在生成视频，请耐心等待..."):
                # 构建完整的提示词，将参数拼接到提示词末尾
                full_prompt = base_prompt_t2v
                full_prompt += f" --resolution {resolution_t2v}"
                full_prompt += f" --ratio {ratio_t2v}"
                full_prompt += f" --duration {duration_t2v}"
                full_prompt += f" --fps {fps_t2v}"
                full_prompt += f" --watermark {str(watermark_t2v).lower()}"
                if seed_t2v != -1:
                    full_prompt += f" --seed {seed_t2v}"
                full_prompt += f" --camerafixed {str(camera_fixed_t2v).lower()}"
                
                st.info(f"完整提示词: {full_prompt}")
                
                try:
                    video_url = t2v_seedance(ark_client, model_t2v, full_prompt)
                    if video_url:
                        st.success("视频生成成功！")
                        st.video(video_url)
                        st.markdown(f"[下载视频]({video_url})")
                    else:
                        st.error("视频生成失败，请检查参数或稍后重试")
                except Exception as e:
                    st.error(f"生成视频时出错: {str(e)}")