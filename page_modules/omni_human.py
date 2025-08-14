import streamlit as st
import base64
import time
import requests
import tempfile
import os
import threading
from api_modules.visual_image import omni_human_pre_test, omni_human

def render_omni_human(visual_service, upload_to_tos):
    """数字人(Omni_Human)页面"""
    st.header("👤 数字人(Omni_Human)")
    st.markdown("接口文档: https://www.volcengine.com/docs/85128/1580768")
    st.markdown("💡 数字人功能可以根据输入的图片和音频生成数字人视频")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        
        # 图片输入
        st.subheader("📷 人物图片")
        input_method_omni = st.radio("选择图片来源", ("URL", "上传图片"), key="input_method_omni")
        image_url_omni = None
        uploaded_file_omni = None

        if input_method_omni == "URL":
            image_url_omni = st.text_input(
                "输入人物图片 URL:", 
                "https://qwer123.tos-cn-beijing.volces.com/omnihuman-image.jpg", 
                key="image_url_omni",
                help="请输入清晰的人物正面照片URL"
            )
        else:
            uploaded_file_omni = st.file_uploader(
                "上传人物图片", 
                type=["png", "jpg", "jpeg"], 
                key="file_uploader_omni",
                help="请上传清晰的人物正面照片"
            )
        
        # 音频输入
        st.subheader("🎵 音频文件")
        audio_input_method = st.radio("选择音频来源", ("URL", "上传音频"), key="audio_input_method")
        audio_url_omni = None
        uploaded_audio_omni = None
        
        if audio_input_method == "URL":
            audio_url_omni = st.text_input(
                "输入音频 URL:", 
                "https://qwer123.tos-cn-beijing.volces.com/audio-002.m4a", 
                key="audio_url_omni",
                help="支持 mp3, wav, m4a 等格式"
            )
        else:
            uploaded_audio_omni = st.file_uploader(
                "上传音频文件", 
                type=["mp3", "wav", "m4a", "aac"], 
                key="file_uploader_audio_omni",
                help="支持 mp3, wav, m4a, aac 等格式"
            )
        
        # 生成按钮
        col_check, col_generate = st.columns(2)
        
        with col_check:
            check_button_omni = st.button("🔍 前置检查", key="check_button_omni", help="检查图片是否适合生成数字人")
        
        with col_generate:
            generate_button_omni = st.button("🎬 生成数字人视频", key="generate_button_omni", type="primary")
    
    with col2:
        st.subheader("预览和生成结果")
        
        # 预览区域
        preview_col1, preview_col2 = st.columns(2)
        
        with preview_col1:
            st.write("**图片预览**")
            preview_image_omni = None
            final_image_url = None
            
            if input_method_omni == "URL" and image_url_omni:
                preview_image_omni = image_url_omni
                final_image_url = image_url_omni
            elif input_method_omni == "上传图片" and uploaded_file_omni is not None:
                # 上传图片到TOS获取URL
                object_key = f"uploads/omni_human_{int(time.time())}_{uploaded_file_omni.name}"
                upload_result = upload_to_tos(object_key, uploaded_file_omni.getvalue())
                if upload_result:
                    st.success(f"✅ 文件已成功上传到TOS: {object_key}")
                    final_image_url = upload_result
                    preview_image_omni = uploaded_file_omni
                else:
                    st.warning("⚠️ 文件上传到TOS失败，但仍可继续使用")
                    preview_image_omni = uploaded_file_omni
            
            if preview_image_omni is not None:
                st.image(preview_image_omni, caption="人物图片", use_container_width=True)
            else:
                st.info("请上传或输入人物图片")
        
        with preview_col2:
            st.write("**音频预览**")
            final_audio_url = None
            
            if audio_input_method == "URL" and audio_url_omni:
                try:
                    st.audio(audio_url_omni)
                    st.success("✅ 音频URL有效")
                    final_audio_url = audio_url_omni
                except Exception as e:
                    st.warning(f"⚠️ 无法预览音频: {str(e)}")
                    final_audio_url = audio_url_omni
            elif audio_input_method == "上传音频" and uploaded_audio_omni is not None:
                object_key = f"uploads/omni_human_{int(time.time())}_{uploaded_audio_omni.name}"
                upload_result = upload_to_tos(object_key, uploaded_audio_omni.getvalue())
                if upload_result:
                    st.success(f"✅ 文件已成功上传到TOS: {object_key}")
                    final_audio_url = upload_result
                    st.audio(uploaded_audio_omni)
                else:
                    st.warning("⚠️ 文件上传到TOS失败，但仍可继续使用")
                    st.audio(uploaded_audio_omni)
            else:
                st.info("请上传或输入音频文件")
        
        # 前置检查结果
        if check_button_omni:
            if not final_image_url:
                st.error("❌ 请先输入有效的图片URL或上传图片进行前置检查")
            else:
                with st.spinner("🔍 正在进行前置检查..."):
                    try:
                        check_result = omni_human_pre_test(visual_service, final_image_url)
                        
                        if check_result == 1:
                            st.success("✅ 前置检查通过！图片适合生成数字人视频")
                            st.session_state.omni_check_passed = True
                            st.session_state.omni_checked_image_url = final_image_url
                        else:
                            st.error(f"❌ 前置检查未通过，检查结果: {check_result}")
                            st.warning("请尝试使用以下类型的图片：")
                            st.write("- 清晰的人物正面照")
                            st.write("- 人脸清晰可见")
                            st.write("- 光线充足")
                            st.write("- 背景简洁")
                            st.session_state.omni_check_passed = False
                            
                    except Exception as e:
                        st.error(f"❌ 前置检查失败: {str(e)}")
                        st.session_state.omni_check_passed = False
        
        # 生成数字人视频
        if generate_button_omni:
            # 检查是否已通过前置检查
            if not st.session_state.get('omni_check_passed', False):
                st.error("❌ 请先进行前置检查并确保检查通过")
            else:
                # 准备最终的图片和音频URL
                final_image_url = st.session_state.get('omni_checked_image_url')
                
                if not final_image_url or not final_audio_url:
                    st.error("❌ 请确保图片和音频URL都已正确输入")
                else:
                    with st.spinner("🎬 正在生成数字人视频，请耐心等待..."):
                        try:
                            video_url = omni_human(visual_service, final_image_url, final_audio_url)
                            
                            if video_url:
                                st.success("✅ 数字人视频生成成功！")
                                
                                # 显示生成的视频
                                st.subheader("🎬 生成的数字人视频")
                                
                                try:
                                    # 下载视频到本地临时文件
                                    with st.spinner("📥 正在下载视频文件..."):
                                        # 创建临时文件
                                        temp_dir = tempfile.gettempdir()
                                        temp_video_path = os.path.join(temp_dir, f"digital_human_video_{int(time.time())}.mp4")
                                        
                                        # 下载视频
                                        response = requests.get(video_url, stream=True, timeout=60)
                                        response.raise_for_status()
                                        
                                        with open(temp_video_path, 'wb') as f:
                                            for chunk in response.iter_content(chunk_size=8192):
                                                if chunk:
                                                    f.write(chunk)
                                    
                                    # 使用本地文件显示视频
                                    st.video(temp_video_path)
                                    st.success("✅ 视频加载成功！")
                                    
                                    # 提供下载功能
                                    st.markdown("---")
                                    st.subheader("📥 下载选项")
                                    
                                    # 读取视频文件用于下载
                                    with open(temp_video_path, 'rb') as video_file:
                                        video_bytes = video_file.read()
                                        st.download_button(
                                            label="📥 下载数字人视频",
                                            data=video_bytes,
                                            file_name=f"digital_human_video_{int(time.time())}.mp4",
                                            mime="video/mp4"
                                        )
                                    
                                    st.info("💡 **提示:** 点击上方按钮可将视频文件下载到本地。")
                                    
                                    # 显示视频信息
                                    with st.expander("🔍 视频信息", expanded=False):
                                        st.code(f"原始视频URL: {video_url}")
                                        st.code(f"本地临时文件: {temp_video_path}")
                                        try:
                                            file_size = os.path.getsize(temp_video_path)
                                            st.write(f"**文件大小:** {file_size/(1024*1024):.1f} MB")
                                            st.write(f"**文件格式:** MP4")
                                        except Exception as e:
                                            st.write(f"**无法获取视频详细信息:** {str(e)}")
                                    
                                    # 清理临时文件（可选，系统会自动清理）
                                    try:
                                        # 延迟删除，让用户有时间查看
                                        def cleanup_temp_file():
                                            import time
                                            time.sleep(300)  # 5分钟后删除
                                            try:
                                                if os.path.exists(temp_video_path):
                                                    os.remove(temp_video_path)
                                            except:
                                                pass
                                        
                                        cleanup_thread = threading.Thread(target=cleanup_temp_file)
                                        cleanup_thread.daemon = True
                                        cleanup_thread.start()
                                    except:
                                        pass
                                    
                                except Exception as e:
                                    st.warning(f"⚠️ 视频下载或预览失败: {str(e)}")
                                    st.write("**可能的原因:**")
                                    st.write("- 签名URL已过期")
                                    st.write("- 网络连接问题")
                                    st.write("- 视频文件较大，下载超时")
                                    st.write("- 磁盘空间不足")
                                    
                                    # 仍然提供原始下载链接作为备选
                                    st.markdown("---")
                                    st.subheader("📥 备选下载方式")
                                    st.markdown(f"🔗 [点击下载数字人视频]({video_url})")
                                    st.info("💡 **提示:** 如果上述方法失败，请尝试右键点击链接另存为。")
                                
                            else:
                                st.error("❌ 数字人视频生成失败，请检查参数或稍后重试")
                                
                        except Exception as e:
                            st.error(f"❌ 生成数字人视频时出错: {str(e)}")
                            st.info("💡 请检查网络连接和API配置，或稍后重试")
        
        # 使用说明
        with st.expander("📖 使用说明", expanded=False):
            st.markdown("""
            **数字人生成步骤：**
            
            1. **准备素材**
               - 人物图片：清晰的正面照，人脸清晰可见
               - 音频文件：支持 mp3, wav, m4a 等格式
            
            2. **前置检查**
               - 点击"前置检查"按钮验证图片是否适合
               - 只有检查通过的图片才能用于生成数字人
            
            3. **生成视频**
               - 确保前置检查通过后，点击"生成数字人视频"
               - 生成过程可能需要几分钟，请耐心等待
            
            **注意事项：**
            - 图片要求：人物正面照，光线充足，背景简洁
            - 音频要求：清晰的语音，建议时长不超过60秒
            - 支持URL输入和文件上传两种方式
            
            **技术支持：**
            - 如遇到问题，请检查API密钥配置
            - 确保网络连接稳定
            - 建议使用Chrome或Firefox浏览器
            """)