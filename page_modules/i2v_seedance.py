import streamlit as st
import base64
from api_modules.ark_video import i2v_seedance
from utils.llm_prompt_optmize import optimize_stream

def render_i2v_seedance(ark_client):
    """Seedance 1.0 图生视频页面"""
    st.header("Seedance 1.0 图生视频")
    st.markdown("接口文档: https://www.volcengine.com/docs/82379/1520757")
    st.markdown("Seedance-pro 提示词指南: https://bytedance.larkoffice.com/docx/Svl9dMwvCokzZHxamTWcCz5en1f?from=from_copylink")
    st.markdown("Seedance-lit 提示词指南: https://bytedance.larkoffice.com/docx/UQoSd3NEvoAkghxAl0ccjdplnhR?from=from_copylink")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        
        # 模型选择
        model_i2v = st.selectbox(
            "选择模型",
            ["doubao-seedance-1-0-pro-250528", "doubao-seedance-1-0-lite-i2v-250428"],
            key="model_i2v"
        )
        
        # 首帧图片上传
        st.subheader("图片上传")
        first_frame_file = st.file_uploader(
            "上传首帧图片 (必需)",
            type=["png", "jpg", "jpeg"],
            key="first_frame_i2v"
        )
        
        # 根据模型显示尾帧上传选项
        last_frame_file = None
        if model_i2v == "doubao-seedance-1-0-lite-i2v-250428":
            last_frame_file = st.file_uploader(
                "上传尾帧图片 (可选)",
                type=["png", "jpg", "jpeg"],
                key="last_frame_i2v"
            )
            st.info("💡 Seedance 1.0 lite 模型支持首帧和尾帧，可以更精确控制视频内容")
        else:
            st.info("💡 Seedance 1.0 pro 模型只支持首帧")

        # 基础提示词 - 使用优化后的值或默认值
        if 'optimized_prompt_i2v' in st.session_state and st.session_state.optimized_prompt_i2v:
            default_prompt_i2v = st.session_state.optimized_prompt_i2v
        else:
            default_prompt_i2v = "让图片中的人物动起来，自然的动作"
            
        # 创建标题和优化链接
        st.write("输入视频描述提示词:")   
        base_prompt_i2v = st.text_area(
            "视频描述提示词",
            value=default_prompt_i2v,
            height=100,
            key="base_prompt_i2v",
            label_visibility="collapsed"
        )
        optimize_button_i2v = st.button("一键优化", key="optimize_i2v", help="使用AI优化您的提示词", type="secondary")
        
        # 处理提示词优化
        if optimize_button_i2v:
            if base_prompt_i2v.strip():
                with st.spinner("正在优化提示词..."):
                    try:
                        # 获取首帧图片的base64编码用于优化
                        first_frame_url = None
                        if first_frame_file is not None:
                            first_frame_base64 = base64.b64encode(first_frame_file.getvalue()).decode('utf-8')
                            # 根据文件类型设置正确的MIME类型
                            mime_type = f"image/{first_frame_file.type.split('/')[-1]}" if first_frame_file.type else "image/jpeg"
                            first_frame_url = f"data:{mime_type};base64,{first_frame_base64}"
                        
                        # 流式显示优化过程
                        placeholder = st.empty()
                        optimized_text = ""
                        
                        for chunk in optimize_stream(ark_client, "i2v", base_prompt_i2v, first_frame_url):
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
                            st.session_state.optimized_prompt_i2v = optimized_text.strip()
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
        
        resolution_i2v = st.selectbox(
            "分辨率",
            ["480p", "720p", "1080p"],
            index=1,
            key="resolution_i2v"
        )
        
        ratio_i2v = st.selectbox(
            "宽高比",
            ["keep_ratio","adaptive"],
            index=1,
            key="ratio_i2v"
        )
        
        duration_i2v = st.selectbox(
            "时长",
            ["5", "10"],
            key="duration_i2v"
        )
        
        fps_i2v = st.selectbox(
            "帧率",
            [16, 24],
            index=1,
            key="fps_i2v"
        )
        
        watermark_i2v = st.checkbox("添加水印", value=True, key="watermark_i2v")
        
        seed_i2v = st.number_input("Seed", value=-1, key="seed_i2v")
        
        camera_fixed_i2v = st.checkbox("固定镜头", value=False, key="camera_fixed_i2v")
        
        generate_button_i2v = st.button("生成视频", key="button_i2v")
    
    with col2:
        st.subheader("图片预览和生成结果")
        
        # 图片预览区域
        preview_col1, preview_col2 = st.columns(2)
        
        with preview_col1:
            st.write("**首帧预览**")
            if first_frame_file is not None:
                st.image(first_frame_file, caption="首帧图片")
            else:
                st.info("请上传首帧图片")
        
        with preview_col2:
            st.write("**尾帧预览**")
            if last_frame_file is not None:
                st.image(last_frame_file, caption="尾帧图片")
            elif model_i2v == "doubao-seedance-1-0-lite-i2v-250428":
                st.info("可选择上传尾帧图片")
            else:
                st.info("当前模型不支持尾帧")
        
        # 生成结果区域
        st.subheader("生成结果")
        
        if generate_button_i2v:
            if first_frame_file is None:
                st.error("请先上传首帧图片！")
            else:
                with st.spinner("正在生成视频，请耐心等待..."):
                    try:
                        # 将图片转换为base64并上传获取URL
                        # 这里简化处理，实际应该上传到云存储获取URL
                        first_frame_base64 = base64.b64encode(first_frame_file.getvalue()).decode('utf-8')
                        # 根据文件类型设置正确的MIME类型
                        first_frame_mime = f"image/{first_frame_file.type.split('/')[-1]}" if first_frame_file.type else "image/jpeg"
                        first_frame_url = f"data:{first_frame_mime};base64,{first_frame_base64}"
                        
                        last_frame_url = None
                        if last_frame_file is not None:
                            last_frame_base64 = base64.b64encode(last_frame_file.getvalue()).decode('utf-8')
                            # 根据文件类型设置正确的MIME类型
                            last_frame_mime = f"image/{last_frame_file.type.split('/')[-1]}" if last_frame_file.type else "image/jpeg"
                            last_frame_url = f"data:{last_frame_mime};base64,{last_frame_base64}"
                        
                        # 构建完整的提示词
                        full_prompt = base_prompt_i2v
                        full_prompt += f" --resolution {resolution_i2v}"
                        full_prompt += f" --ratio {ratio_i2v}"
                        full_prompt += f" --duration {duration_i2v}"
                        full_prompt += f" --fps {fps_i2v}"
                        full_prompt += f" --watermark {str(watermark_i2v).lower()}"
                        if seed_i2v != -1:
                            full_prompt += f" --seed {seed_i2v}"
                        full_prompt += f" --camerafixed {str(camera_fixed_i2v).lower()}"
                        
                        st.info(f"完整提示词: {full_prompt}")
                        
                        # 调用图生视频函数
                        video_url = i2v_seedance(
                            ark_client, 
                            model_i2v, 
                            full_prompt,
                            first_frame=first_frame_url,
                            last_frame=last_frame_url
                        )
                        
                        if video_url:
                            st.success("视频生成成功！")
                            st.video(video_url)
                            st.markdown(f"[下载视频]({video_url})")
                        else:
                            st.error("视频生成失败，请检查参数或稍后重试")
                            
                    except Exception as e:
                        st.error(f"生成视频时出错: {str(e)}")