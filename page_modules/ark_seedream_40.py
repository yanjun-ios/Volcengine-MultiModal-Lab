import streamlit as st
import base64
import json
from api_modules.ark_image import ark_seedream_40

def render_ark_seedream_40(ark_client):
    """方舟-SeedDream4.0页面"""
    st.header("方舟-SeedDream4.0")
    st.markdown("文档: https://www.volcengine.com/docs/82379/1824718")
    st.markdown("提示词指南: https://bytedance.larkoffice.com/wiki/SWalw66Flihm1pkudaQcvWuBn3d")
    st.markdown("💡 使用方舟SeedDream4.0进行高质量图像生成，支持多参考图，多角色特征保持")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        
        # 模型选择
        model_options = [
            "doubao-seedream-4-0-250828"
        ]
        model_seedream = st.selectbox(
            "选择模型",
            options=model_options,
            index=0,
            key="model_seedream_40"
        )
        
        # 提示词输入
        prompt_seedream = st.text_area(
            "输入文生图提示词:",
            "星际穿越，黑洞，黑洞里冲出一辆快支离破碎的复古列车，抢视觉冲击力，电影大片，末日既视感，动感，对比色，oc渲染，光线追踪，动态模糊，景深，超现实主义，深蓝,生成两张图片",
            height=120,
            key="prompt_seedream_40"
        )
        
        # 图片尺寸
        size_seedream = st.selectbox(
            "图片尺寸",
            ["1K","2K","4K","1024x1024","1152x864","864x1152","1280x720","720x1280","1248x832","832x1248","1512x648","2048x2048","2304x1728","1728x2304","2560x1440","1440x2560","2496x1664","1664x2496","3024x1296","4096x4096","4736x3552","3552x4736","5472x2072","2072x5472","5024x3360","3360x5024","6272x2688"],
            key="size_seedream_40"
        )
        
        # 图像输入（可选）
        st.subheader("图像输入（可选）")
        image_input_type = st.radio(
            "图像输入方式",
            ["无", "URL上传", "本地上传"],
            key="image_input_type_seedream_40"
        )
        
        image_seedream = []
        uploaded_images = []
        
        if image_input_type == "URL上传":
            image_urls_text = st.text_input(
                "输入图片URL (多个URL用逗号分隔，最多10张):",
                key="image_urls_seedream_40",
                help="例如: url1.jpg,url2.jpg,url3.jpg"
            )
            if image_urls_text.strip():
                urls = [url.strip() for url in image_urls_text.split(',') if url.strip()]
                if len(urls) > 10:
                    st.warning("最多只能上传10张图片，已自动截取前10张")
                    urls = urls[:10]
                image_seedream = urls if urls else ""
                
                # URL图片预览
                if urls:
                    st.write("图片预览:")
                    preview_cols = st.columns(min(len(urls), 5))
                    for i, url in enumerate(urls):
                        with preview_cols[i % 5]:
                            try:
                                st.image(url, caption=f"图片 {i+1}", width=100)
                            except:
                                st.write(f"图片 {i+1}: 无法预览")
                                
        elif image_input_type == "本地上传":
            uploaded_files = st.file_uploader(
                "选择图片文件 (最多10张):",
                type=['png', 'jpg', 'jpeg'],
                accept_multiple_files=True,
                key="uploaded_files_seedream_40"
            )
            
            if uploaded_files:
                if len(uploaded_files) > 10:
                    st.warning("最多只能上传10张图片，已自动截取前10张")
                    uploaded_files = uploaded_files[:10]
                
                # 转换为base64
                base64_images = []
                for uploaded_file in uploaded_files:
                    bytes_data = uploaded_file.read()
                    base64_str = base64.b64encode(bytes_data).decode()
                    base64_images.append(f"data:image/{uploaded_file.type.split('/')[-1]};base64,{base64_str}")
                
                image_seedream = base64_images if base64_images else ""
                
                # 本地图片预览
                st.write("图片预览:")
                preview_cols = st.columns(min(len(uploaded_files), 5))
                for i, uploaded_file in enumerate(uploaded_files):
                    with preview_cols[i % 5]:
                        st.image(uploaded_file, caption=f"图片 {i+1}", width=100)
        
        # 高级参数
        st.subheader("高级参数")
        
        col_param1, col_param2 = st.columns(2)
        
        with col_param1:
            seed_seedream = st.number_input("Seed", value=-1, key="seed_seedream_40")
            guidance_scale_seedream = st.slider(
                "Guidance Scale", 
                min_value=1.0, 
                max_value=10.0, 
                value=5.5, 
                step=0.1, 
                key="guidance_scale_seedream_40"
            )
        
        with col_param2:
            sequential_image_generation = st.selectbox(
                "Sequential Image Generation",
                ["auto", "disabled"],
                index=0,
                key="sequential_seedream_40"
            )
            
            # 只有当选择auto时才显示max_images参数
            if sequential_image_generation == "auto":
                max_images_seedream = st.number_input(
                    "Max Images", 
                    min_value=1, 
                    max_value=15, 
                    value=15, 
                    key="max_images_auto_seedream_40"
                )
            else:
                max_images_seedream = 1  # disabled时默认为1
                
            watermark_seedream = st.checkbox("添加水印", value=True, key="watermark_seedream_40")
            stream_seedream = st.checkbox("Stream模式", value=True, key="stream_seedream_40")
        
        generate_button_seedream = st.button("生成图片", key="button_seedream_40")
    
    with col2:
        st.subheader("生成结果")
        
        if generate_button_seedream:
            if stream_seedream:
                # 流式模式 - 实时显示生成的图片
                st.info("🔄 流式生成模式：图片将逐个生成并显示")
                
                # 创建占位符用于实时更新
                status_placeholder = st.empty()
                results_container = st.container()
                
                try:
                    status_placeholder.info("正在批量生成图片...")
                    
                    # 调用流式API，获取响应对象
                    response = ark_seedream_40(
                        ark_client,
                        model=model_seedream,
                        prompt=prompt_seedream,
                        image=image_seedream,
                        size=size_seedream,
                        seed=seed_seedream,
                        sequential_image_generation=sequential_image_generation,
                        max_images=max_images_seedream,
                        stream=True,
                        guidance_scale=guidance_scale_seedream,
                        watermark=watermark_seedream
                    )
                    
                    if response:
                        status_placeholder.info("🔄 正在生成图片...")
                        
                        # 存储生成的图片结果
                        generated_images = []
                        
                        # 创建动态占位符用于显示结果
                        results_placeholder = st.empty()
                        
                        # 初始显示预期的图片数量占位符
                        expected_images = max_images_seedream if sequential_image_generation == "auto" else 1
                        
                        def render_images_with_placeholders():
                            """渲染图片，包括已生成的和占位符"""
                            with results_placeholder.container():
                                for i in range(0, expected_images, 2):
                                    col_img1, col_img2 = st.columns(2)
                                    
                                    # 第一张图片位置
                                    with col_img1:
                                        if i < len(generated_images):
                                            # 已生成的图片
                                            image_data = generated_images[i]
                                            st.image(image_data['url'], caption=f"图片 {i+1}", use_column_width=True)
                                            st.text_input(f"图片 {i+1} URL:", value=image_data['url'], key=f"stream_url_{i}_{len(generated_images)}")
                                        elif i < expected_images:
                                            # 占位符
                                            st.info(f"🔄 图片 {i+1} 正在生成...")
                                            st.text_input(f"图片 {i+1} URL:", value="", placeholder="生成中...", key=f"stream_placeholder_{i}_{len(generated_images)}")
                                    
                                    # 第二张图片位置
                                    if i + 1 < expected_images:
                                        with col_img2:
                                            if i + 1 < len(generated_images):
                                                # 已生成的图片
                                                image_data = generated_images[i + 1]
                                                st.image(image_data['url'], caption=f"图片 {i+2}", use_column_width=True)
                                                st.text_input(f"图片 {i+2} URL:", value=image_data['url'], key=f"stream_url_{i+1}_{len(generated_images)}")
                                            else:
                                                # 占位符
                                                st.info(f"🔄 图片 {i+2} 正在生成...")
                                                st.text_input(f"图片 {i+2} URL:", value="", placeholder="生成中...", key=f"stream_placeholder_{i+1}_{len(generated_images)}")
                        
                        # 初始显示所有占位符
                        render_images_with_placeholders()
                        
                        # 处理流式响应
                        for line in response.iter_lines():
                            if line:
                                line_str = line.decode('utf-8')
                                if line_str.startswith('data: '):
                                    try:
                                        data_str = line_str[6:]  # 移除 'data: ' 前缀
                                        event_data = json.loads(data_str)
                                        
                                        # 检查是否是图片生成成功事件
                                        if event_data.get('type') == 'image_generation.partial_succeeded':
                                            result_item = {
                                                'url': event_data.get('url'),
                                                'image_index': event_data.get('image_index'),
                                                'size': event_data.get('size'),
                                                'created': event_data.get('created')
                                            }
                                            generated_images.append(result_item)
                                            
                                            # 实时更新状态
                                            status_placeholder.info(f"🔄 已生成 {len(generated_images)}/{expected_images} 张图片...")
                                            
                                            # 重新渲染图片（包括新生成的和剩余占位符）
                                            render_images_with_placeholders()
                                            
                                    except json.JSONDecodeError:
                                        continue
                        
                        # 生成完成
                        if generated_images:
                            status_placeholder.success(f"✅ 图片生成完成！共生成 {len(generated_images)} 张图片")
                        else:
                            status_placeholder.error("未生成任何图片，请检查参数")
                    else:
                        status_placeholder.error("API连接失败，请检查参数或稍后重试")
                        
                except Exception as e:
                    status_placeholder.error(f"生成图片时出错: {str(e)}")
                    st.exception(e)
            else:
                # 非流式模式 - 传统方式
                with st.spinner("正在生成图片..."):
                    try:
                        result = ark_seedream_40(
                            ark_client,
                            model=model_seedream,
                            prompt=prompt_seedream,
                            image=image_seedream,
                            size=size_seedream,
                            seed=seed_seedream,
                            sequential_image_generation=sequential_image_generation,
                            max_images=max_images_seedream,
                            stream=False,
                            guidance_scale=guidance_scale_seedream,
                            watermark=watermark_seedream
                        )
                        
                        if result:
                            # 判断result是否为数组
                            if isinstance(result, list):
                                st.success(f"图片生成成功！共生成 {len(result)} 张图片")
                                
                                # 每行显示两张图片
                                for i in range(0, len(result), 2):
                                    col_img1, col_img2 = st.columns(2)
                                    
                                    # 第一张图片
                                    if i < len(result):
                                        image_data = result[i]
                                        with col_img1:
                                            if hasattr(image_data, 'url') and image_data.url:
                                                st.image(image_data.url, caption=f"图片 {i+1}", use_column_width=True)
                                                st.text_input(f"图片 {i+1} URL:", value=image_data.url, key=f"result_url_{i}")
                                            elif isinstance(image_data, dict) and 'url' in image_data:
                                                st.image(image_data['url'], caption=f"图片 {i+1}", use_column_width=True)
                                                st.text_input(f"图片 {i+1} URL:", value=image_data['url'], key=f"result_url_{i}")
                                    
                                    # 第二张图片
                                    if i + 1 < len(result):
                                        image_data = result[i + 1]
                                        with col_img2:
                                            if hasattr(image_data, 'url') and image_data.url:
                                                st.image(image_data.url, caption=f"图片 {i+2}", use_column_width=True)
                                                st.text_input(f"图片 {i+2} URL:", value=image_data.url, key=f"result_url_{i+1}")
                                            elif isinstance(image_data, dict) and 'url' in image_data:
                                                st.image(image_data['url'], caption=f"图片 {i+2}", use_column_width=True)
                                                st.text_input(f"图片 {i+2} URL:", value=image_data['url'], key=f"result_url_{i+1}")
                            else:
                                # 单张图片结果
                                st.image(result, caption="SeedDream4.0生成图片", use_column_width=True)
                                st.success("图片生成成功！")
                                st.text_input("生成的图片URL:", value=result, key="single_result_url")
                        else:
                            st.error("图片生成失败，请检查参数或稍后重试")
                            
                    except Exception as e:
                        st.error(f"生成图片时出错: {str(e)}")
                        st.exception(e)