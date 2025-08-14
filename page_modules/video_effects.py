import streamlit as st
import base64
import time
import requests
import tempfile
import os
from api_modules.visual_video import template_2_video

def render_video_effects(visual_service, upload_to_tos):
    """视频生成-视频特效页面"""
    st.header("🎬 视频生成-视频特效")
    st.markdown("接口文档: https://www.volcengine.com/docs/85128/1783766")
    st.markdown("💡 基于字节自研的图像及视频处理技术和先进算法模型，支持基于用户上传的图片，稳定生成高质量、的创意特效视频。此能力亮点在于整合了多种自研图像和视频技术能力与先进模型，生成视频附带适配的背景音乐和音效，兼具创意性和视觉表现力，可广泛应用于互动娱乐和写真特效等场景。")
    
    # 定义模板选项，包含中文显示名称、英文模板ID和默认URL
    template_options = {
        "变身玩偶_480p版": {
            "id": "becoming_doll",
            "url": "https://qwer123.tos-cn-beijing.volces.com/857ff5c6-2f16-495b-bd8e-65ccbe38a29b.png"
        },
        "变身玩偶_720p版": {
            "id": "becoming_doll_720p", 
            "url": "https://qwer123.tos-cn-beijing.volces.com/857ff5c6-2f16-495b-bd8e-65ccbe38a29b.png"
        },
        "召唤坐骑-猪_480p版": {
            "id": "all_things_ridability_pig",
            "url": "https://qwer123.tos-cn-beijing.volces.com/b50a89c7-8c46-486d-b3ef-95f682e12192.png"
        },
        "召唤坐骑-猪_720p版": {
            "id": "all_things_ridability_pig_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/b50a89c7-8c46-486d-b3ef-95f682e12192.png"
        },
        "召唤坐骑-老虎_480p版": {
            "id": "all_things_ridability_tiger",
            "url": "https://qwer123.tos-cn-beijing.volces.com/faeb2464-b830-44c9-86dd-e0a65ca4e911.png"
        },
        "召唤坐骑-老虎_720p版": {
            "id": "all_things_ridability_tiger_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/faeb2464-b830-44c9-86dd-e0a65ca4e911.png"
        },
        "召唤坐骑-龙_480p版": {
            "id": "all_things_ridability_loong",
            "url": "https://qwer123.tos-cn-beijing.volces.com/fc4d15dd-7ab6-42df-be21-d40b6cde3703.png"
        },
        "召唤坐骑-龙_720p版": {
            "id": "all_things_ridability_loong_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/fc4d15dd-7ab6-42df-be21-d40b6cde3703.png"
        },
        "万物生花_480p版": {
            "id": "all_things_bloom_with_flowers",
            "url": "https://qwer123.tos-cn-beijing.volces.com/0e7aed08-267e-4272-82af-50c5e8e14a23.png"
        },
        "万物生花_720p版": {
            "id": "all_things_bloom_with_flowers_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/0e7aed08-267e-4272-82af-50c5e8e14a23.png"
        },
        "爱的拥抱（单图）_480p版": {
            "id": "double_embrace_single_person",
            "url": "https://qwer123.tos-cn-beijing.volces.com/9459a381-3bbe-4e57-a154-c9c71bd395c2.png"
        },
        "爱的拥抱（单图）_720p版": {
            "id": "double_embrace_single_person_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/9459a381-3bbe-4e57-a154-c9c71bd395c2.png"
        },
        "爱的拥抱（双图）_480p版": {
            "id": "double_embrace",
            "url": "https://qwer123.tos-cn-beijing.volces.com/9781c1f7-cd79-4daf-a027-6bd2b3775c8c.png|https://qwer123.tos-cn-beijing.volces.com/9459a381-3bbe-4e57-a154-c9c71bd395c2.png"
        },
        "爱的拥抱（双图）_720p版": {
            "id": "double_embrace_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/9781c1f7-cd79-4daf-a027-6bd2b3775c8c.png|https://qwer123.tos-cn-beijing.volces.com/9459a381-3bbe-4e57-a154-c9c71bd395c2.png"
        },
        "AI美女环绕_480p版": {
            "id": "beauty_surround",
            "url": "https://qwer123.tos-cn-beijing.volces.com/b50a89c7-8c46-486d-b3ef-95f682e12192.png"
        },
        "AI美女环绕_720p版": {
            "id": "beauty_surround_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/b50a89c7-8c46-486d-b3ef-95f682e12192.png"
        },
        "AI帅哥环绕_480p版": {
            "id": "handsome_man_surround",
            "url": "https://qwer123.tos-cn-beijing.volces.com/68c1b962-49ce-45d2-a367-6676a66f6c18.jpeg"
        },
        "AI帅哥环绕_720p版": {
            "id": "handsome_man_surround_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/68c1b962-49ce-45d2-a367-6676a66f6c18.jpeg"
        },
        "天赐宝宝_480p版": {
            "id": "ai_baby",
            "url": "https://qwer123.tos-cn-beijing.volces.com/b50a89c7-8c46-486d-b3ef-95f682e12192.png"
        },
        "天赐宝宝_720p版": {
            "id": "ai_baby_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/b50a89c7-8c46-486d-b3ef-95f682e12192.png"
        },
        "清凉泳装变身_480p版": {
            "id": "put_on_bikini",
            "url": "https://qwer123.tos-cn-beijing.volces.com/857ff5c6-2f16-495b-bd8e-65ccbe38a29b.png"
        },
        "清凉泳装变身_720p版": {
            "id": "put_on_bikini_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/857ff5c6-2f16-495b-bd8e-65ccbe38a29b.png"
        },
        "变身兔女郎_480p版": {
            "id": "put_on_bunny_girl_outfit",
            "url": "https://qwer123.tos-cn-beijing.volces.com/26fdf9e9-5a65-4e3e-b923-2a13f1bc9644.png"
        },
        "变身兔女郎_720p版": {
            "id": "put_on_bunny_girl_outfit_720p",
            "url": "https://qwer123.tos-cn-beijing.volces.com/26fdf9e9-5a65-4e3e-b923-2a13f1bc9644.png"
        }
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        
        # 模板选择下拉框
        selected_template_display = st.selectbox(
            "选择视频特效模板",
            options=list(template_options.keys()),
            key="template_selector_video",
            help="选择要应用的视频特效模板"
        )
        
        # 获取对应的模板ID和默认URL
        selected_template_info = template_options[selected_template_display]
        selected_template_id = selected_template_info["id"]
        default_url = selected_template_info["url"]

        # 特殊处理：爱的拥抱（双图）模板
        is_double_embrace = "double_embrace" in selected_template_id and "single" not in selected_template_id
        
        # 图片输入方式
        input_method_video = st.radio("选择图片来源", ("使用模板默认图片", "自定义URL", "上传图片"), key="input_method_video")
        image_input_video = None
        uploaded_file_video = None
        uploaded_file_video2 = None

        if input_method_video == "使用模板默认图片":
            image_input_video = default_url
            st.text_input(
                "模板默认图片URL:", 
                value=default_url,
                disabled=True,
                key="default_url_display_video"
            )
        elif input_method_video == "自定义URL":
            image_input_video = st.text_input(
                "输入图片 URL:", 
                value=default_url,
                key="image_url_video"
            )
            if is_double_embrace:
                st.info("💡 此模板需要两张图片，请使用'|'分隔两个图片URL")
        else:
            uploaded_file_video = st.file_uploader(
                "上传图片", 
                type=["png", "jpg", "jpeg"], 
                key="file_uploader_video"
            )
            if is_double_embrace:
                uploaded_file_video2 = st.file_uploader(
                "上传图片2", 
                type=["png", "jpg", "jpeg"], 
                key="file_uploader_video2"
            )
        
        # 生成按钮
        generate_button_video = st.button("🎬 生成视频特效", key="button_video", type="primary")
    
    with col2:
        st.subheader("图片预览和生成结果")
        
        # 预览区域
        preview_col, result_col = st.columns(2)
        
        with preview_col:
            st.write("**原图预览**")
            preview_image_video = None
            
            if input_method_video == "使用模板默认图片" or input_method_video == "自定义URL":
                if image_input_video:
                    # 处理双图情况
                    if is_double_embrace and "|" in image_input_video:
                        image_urls = image_input_video.split("|")
                        st.write("**图片1:**")
                        st.image(image_urls[0], caption="第一张图片", use_container_width=True)
                        if len(image_urls) > 1:
                            st.write("**图片2:**")
                            st.image(image_urls[1], caption="第二张图片", use_container_width=True)
                    else:
                        st.image(image_input_video, caption="原图", use_container_width=True)
            elif input_method_video == "上传图片" and uploaded_file_video is not None:
                st.image(uploaded_file_video, caption="上传的图片", use_container_width=True)
                if uploaded_file_video2 is not None:
                    st.image(uploaded_file_video2, caption="第二张图片", use_container_width=True)
            else:
                st.info("请选择或上传图片")
        
        with result_col:
            st.write("**视频特效结果**")
            if generate_button_video:
                # 验证输入
                final_image_input = None
                
                if input_method_video == "使用模板默认图片" or input_method_video == "自定义URL":
                    final_image_input = image_input_video
                elif input_method_video == "上传图片" and uploaded_file_video is not None:
                    # 对于上传的图片，需要先上传到云存储获取URL
                    object_key = f"uploads/video_effects_{int(time.time())}_{uploaded_file_video.name}"
                    upload_url = upload_to_tos(object_key, uploaded_file_video.getvalue())
                    if uploaded_file_video2 is not None:
                        object_key2 = f"uploads/video_effects_{int(time.time())}_{uploaded_file_video2.name}"
                        upload_url2 = upload_to_tos(object_key2, uploaded_file_video2.getvalue())
                        upload_url = upload_url + "|" + upload_url2
                    if upload_url:
                        final_image_input = upload_url
                        st.success(f"✅ 图片已上传: {object_key}")
                    else:
                        st.error("❌ 图片上传失败，请稍后重试")
                        final_image_input = None
                
                if not final_image_input:
                    st.error("❌ 请先选择或上传图片！")
                else:
                    # 验证双图模板的输入格式
                    if is_double_embrace and "|" not in final_image_input:
                        st.error("❌ 爱的拥抱（双图）模板需要两张图片，请使用'|'分隔两个图片URL")
                    else:
                        with st.spinner("🎬 正在生成视频特效，请耐心等待..."):
                            try:
                                video_url = template_2_video(
                                    visual_service,
                                    image_input=final_image_input,
                                    template_id=selected_template_id
                                )
                                
                                if video_url:
                                    st.success("✅ 视频特效生成成功！")
                                    
                                    # 显示生成的视频
                                    try:
                                        with st.spinner("📥 正在下载视频文件..."):
                                            # 创建临时文件
                                            temp_dir = tempfile.gettempdir()
                                            temp_video_path = os.path.join(temp_dir, f"template_video_{int(time.time())}.mp4")
                                            
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
                                        
                                        # 提供下载链接
                                        st.markdown("---")
                                        st.subheader("📥 下载选项")
                                        st.markdown(f"🔗 [点击下载视频]({video_url})")
                                        st.info("💡 **提示:** 右键点击上方链接，选择'另存为'可将视频文件保存到本地。")
                                        
                                        # 显示特效信息
                                        st.info(f"🎬 **应用特效:** {selected_template_display}")
                                        
                                    except Exception as e:
                                        st.warning(f"⚠️ 视频预览失败: {str(e)}")
                                        st.markdown(f"🔗 [点击下载视频]({video_url})")
                                        
                                else:
                                    st.error("❌ 视频特效生成失败，请检查参数或稍后重试")
                                    
                            except Exception as e:
                                st.error(f"❌ 生成视频特效时出错: {str(e)}")
                                st.info("💡 请检查网络连接和API配置，或稍后重试")
        
        # 特效说明
        with st.expander("🎬 视频特效模板说明", expanded=False):
            st.markdown("""
            **可用视频特效模板：**
            
            🎭 **变身类特效**
            - **变身玩偶**: 将人物转换为可爱的玩偶形象
            - **清凉泳装变身**: 换装为泳装造型
            - **变身兔女郎**: 换装为兔女郎造型
            
            🐾 **召唤坐骑系列**  
            - **召唤坐骑-猪**: 召唤可爱的猪坐骑
            - **召唤坐骑-老虎**: 召唤威武的老虎坐骑
            - **召唤坐骑-龙**: 召唤神秘的龙坐骑
            
            🌸 **特殊效果**
            - **万物生花**: 周围绽放美丽花朵的特效
            - **爱的拥抱**: 温馨的拥抱场景（支持单图和双图）
            
            👥 **环绕特效**
            - **AI美女环绕**: 被美女环绕的特效
            - **AI帅哥环绕**: 被帅哥环绕的特效
            
            👶 **其他特效**
            - **天赐宝宝**: 生成可爱宝宝的特效
            
            **分辨率选择：**
            - **480p版本**: 标准清晰度，生成速度较快
            - **720p版本**: 高清版本，画质更佳但生成时间较长
            
            **使用提示：**
            - 建议使用清晰、主体明确的人物图片
            - 爱的拥抱（双图）模板需要两张图片，用'|'分隔URL
            - 不同模板适合不同类型的图片内容
            - 生成时间可能需要几分钟，请耐心等待
            """)