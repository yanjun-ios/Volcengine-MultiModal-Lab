import streamlit as st
import os

def render_settings():
    st.header("⚙️ 系统设置")
    st.markdown("在这里配置系统设置")
    
    # 创建两列布局
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("API 配置")
        
        # Byteplus Model Ark 开关
        st.markdown("**Byteplus Model Ark 配置**")
        
        # 获取当前开关状态
        current_byteplus_enabled = st.session_state.get("byteplus_ark_enabled", False)
        
        byteplus_enabled = st.toggle(
            "启用 Byteplus Model Ark",
            value=current_byteplus_enabled,
            help="开启后将使用 Byteplus Model Ark 替代默认的 Volcengine Ark"
        )
        
        # 保存开关状态到 session_state
        st.session_state.byteplus_ark_enabled = byteplus_enabled
        
        # 如果开启了 Byteplus，显示 API Key 输入框和模型配置
        if byteplus_enabled:
            current_model_ark_key = os.environ.get("MODEL_ARK_API_KEY", "")
            
            with st.form("byteplus_settings_form"):
                st.markdown("**API Key 配置**")
                model_ark_key = st.text_input(
                    "MODEL_ARK_API_KEY",
                    value=current_model_ark_key,
                    type="password",
                    help="Byteplus Model Ark API Key"
                )
                
                st.markdown("**模型配置**")
                
                # SeedDream 3.0 文生图模型
                current_t2i_model = st.session_state.get("byteplus_t2i_model", "seedream-3-0-t2i-250415")
                t2i_model = st.text_input(
                    "SeedDream 3.0 文生图模型",
                    value=current_t2i_model,
                    help="用于文本生成图像的模型名称"
                )
                
                # SeedDream 3.0 图生图模型
                current_i2i_model = st.session_state.get("byteplus_i2i_model", "seededit-3-0-i2i-250628")
                i2i_model = st.text_input(
                    "SeedDream 3.0 图生图模型",
                    value=current_i2i_model,
                    help="用于图像编辑的模型名称"
                )
                
                # SeedDream 4.0 模型
                current_seedream40_model = st.session_state.get("byteplus_seedream40_model", "seedream-4-0-250828")
                seedream40_model = st.text_input(
                    "SeedDream 4.0 模型",
                    value=current_seedream40_model,
                    help="用于 SeedDream 4.0 图像生成的模型名称"
                )
                
                st.markdown("**视频生成模型配置**")
                
                # 文生视频模型
                current_t2v_model = st.session_state.get("byteplus_t2v_model", "seedance-1-0-pro-250528,seedance-1-0-lite-t2v-250428")
                t2v_model = st.text_input(
                    "文生视频模型",
                    value=current_t2v_model,
                    help="用于文本生成视频的模型名称，多个模型用逗号分隔"
                )
                
                # 图生视频模型
                current_i2v_model = st.session_state.get("byteplus_i2v_model", "seedance-1-0-pro-250528,seedance-1-0-lite-i2v-250428")
                i2v_model = st.text_input(
                    "图生视频模型",
                    value=current_i2v_model,
                    help="用于图像生成视频的模型名称，多个模型用逗号分隔"
                )
                
                submitted = st.form_submit_button("保存 Byteplus 设置", type="primary")
                
                if submitted:
                    if model_ark_key:
                        # 保存 API Key
                        os.environ["MODEL_ARK_API_KEY"] = model_ark_key
                        
                        # 保存模型配置到 session_state
                        st.session_state.byteplus_t2i_model = t2i_model
                        st.session_state.byteplus_i2i_model = i2i_model
                        st.session_state.byteplus_seedream40_model = seedream40_model
                        st.session_state.byteplus_t2v_model = t2v_model
                        st.session_state.byteplus_i2v_model = i2v_model
                        
                        # 标记需要重新初始化，避免立即清除缓存导致重复 key 错误
                        st.session_state.need_reinit_ark = True
                        
                        st.success("✅ Byteplus Model Ark 设置已保存！")
                        st.info("💡 设置将在下次使用时生效，或者刷新页面立即生效。")
                    else:
                        st.warning("⚠️ 请输入 MODEL_ARK_API_KEY")
    
    with col2:
        st.subheader("设置说明")
        
        st.markdown("""
        **Byteplus Model Ark:**
        
        🚀 **功能说明**
        - Byteplus Model Ark 是字节跳动海外版本的模型服务
        - 提供与 Volcengine Ark 类似的 AI 模型能力
        - 适用于海外用户和特定场景
        
        🔑 **API Key 获取**
        1. 访问 Byteplus 控制台
        2. 进入 Model Ark 服务
        3. 创建或查看 API Key
        
        ⚙️ **使用说明**
        - 默认关闭，使用 Volcengine Ark
        - 开启后自动切换到 Byteplus Model Ark
        - 需要配置对应的 API Key
        """)
        
        # 显示当前配置状态
        st.subheader("当前配置状态")
        
        byteplus_status = "✅ 已启用" if byteplus_enabled else "❌ 未启用"
        model_ark_key_status = "✅ 已配置" if os.environ.get("MODEL_ARK_API_KEY") else "❌ 未配置"
        
        st.markdown(f"""
        **Byteplus Model Ark:** {byteplus_status}
        
        **MODEL_ARK_API_KEY:** {model_ark_key_status}
        """)
        
        if byteplus_enabled:
            # 显示当前模型配置
            t2i_model = st.session_state.get("byteplus_t2i_model", "seedream-3-0-t2i-250415")
            i2i_model = st.session_state.get("byteplus_i2i_model", "seededit-3-0-i2i-250628")
            seedream40_model = st.session_state.get("byteplus_seedream40_model", "seedream-4-0-250828")
            t2v_model = st.session_state.get("byteplus_t2v_model", "seedance-1-0-pro-250528,seedance-1-0-lite-t2v-250428")
            i2v_model = st.session_state.get("byteplus_i2v_model", "seedance-1-0-pro-250528,seedance-1-0-lite-i2v-250428")
            
            st.markdown("**当前模型配置:**")
            st.markdown(f"""
            **图像生成模型:**
            - **文生图模型:** {t2i_model}
            - **图生图模型:** {i2i_model}
            - **SeedDream 4.0:** {seedream40_model}
            
            **视频生成模型:**
            - **文生视频模型:** {t2v_model}
            - **图生视频模型:** {i2v_model}
            """)
            
            if not os.environ.get("MODEL_ARK_API_KEY"):
                st.warning("⚠️ 已启用 Byteplus Model Ark 但未配置 API Key")

def render_settings_bak():
    """设置页面"""
    st.header("⚙️ 系统设置")
    st.markdown("在这里配置您的API密钥和其他系统设置")
    
    # 创建两列布局
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("API 密钥配置")
        
        # 获取当前环境变量值
        current_volc_ak = os.environ.get("VOLC_ACCESSKEY", "")
        current_volc_sk = os.environ.get("VOLC_SECRETKEY", "")
        current_api_key = os.environ.get("API_KEY", "")
        
        # 创建表单
        with st.form("api_settings_form"):
            st.markdown("**火山引擎 Visual API 配置**")
            volc_ak = st.text_input(
                "VOLC_ACCESSKEY",
                value=current_volc_ak,
                type="password",
                help="火山引擎 Access Key"
            )
            
            volc_sk = st.text_input(
                "VOLC_SECRETKEY", 
                value=current_volc_sk,
                type="password",
                help="火山引擎 Secret Key"
            )
            
            st.markdown("**方舟 API 配置**")
            api_key = st.text_input(
                "API_KEY",
                value=current_api_key,
                type="password", 
                help="方舟 API Key"
            )
                      
            # 提交按钮
            submitted = st.form_submit_button("保存设置", type="primary")
            
            if submitted:
                # 更新环境变量
                if volc_ak:
                    os.environ["VOLC_ACCESSKEY"] = volc_ak
                if volc_sk:
                    os.environ["VOLC_SECRETKEY"] = volc_sk
                if api_key:
                    os.environ["API_KEY"] = api_key
                
                # 清除缓存的服务实例，强制重新创建
                st.cache_resource.clear()
                
                # 重新初始化服务实例，使其立即使用新的API密钥
                try:
                    # 重新执行全局变量赋值，使用新的API密钥
                    from app import get_visual_service, get_ark_client
                    st.session_state.visual_service = get_visual_service()
                    st.session_state.ark_client = get_ark_client()
                    
                    st.success("✅ 设置已保存并立即生效！")
                    st.info("💡 提示：为了安全起见，建议在系统环境变量中设置这些密钥。")
                except Exception as e:
                    st.error(f"❌ 重新初始化服务时出错: {str(e)}")
                    st.warning("⚠️ 设置已保存，但可能需要刷新页面才能生效。")
    
    with col2:
        st.subheader("设置说明")
        
        st.markdown("""
        **如何获取API密钥：**
        
        🔥 **火山引擎 Visual API**
        1. 访问 [火山引擎控制台](https://console.volcengine.com/)
        2. 进入"访问控制" → "访问密钥"
        3. 创建或查看 AccessKey 和 SecretKey
        
        🚀 **方舟 API**
        1. 访问 [方舟控制台](https://console.volcengine.com/ark/)
        2. 进入"API管理"
        3. 创建或查看 API Key
        
        💡 **注意：** 音乐生成功能使用与图像生成相同的火山引擎API密钥
        
        **安全建议：**
        - 不要在代码中硬编码密钥
        - 定期轮换API密钥
        - 使用环境变量存储敏感信息
        """)
        
        # 显示当前配置状态
        st.subheader("当前配置状态")
        
        # 检查配置状态
        volc_status = "✅ 已配置" if current_volc_ak and current_volc_sk else "❌ 未配置"
        ark_status = "✅ 已配置" if current_api_key else "❌ 未配置"
        
        st.markdown(f"""
        **火山引擎 Visual API:** {volc_status}
        (图像生成和音乐生成共用此API密钥)
        
        **方舟 API:** {ark_status}
        """)
        
        # 测试连接按钮
        if st.button("🔍 测试连接", help="测试API密钥是否有效"):
            with st.spinner("正在测试连接..."):
                try:
                    # 这里可以添加实际的API测试逻辑
                    # 暂时显示配置状态
                    if current_volc_ak and current_volc_sk and current_api_key:
                        st.success("✅ 所有API密钥已配置")
                    else:
                        missing = []
                        if not current_volc_ak or not current_volc_sk:
                            missing.append("火山引擎 Visual API")
                        if not current_api_key:
                            missing.append("方舟 API")
                        st.warning(f"⚠️ 缺少配置: {', '.join(missing)}")
                except Exception as e:
                    st.error(f"❌ 连接测试失败: {str(e)}")