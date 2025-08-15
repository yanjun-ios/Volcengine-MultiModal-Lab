import streamlit as st
import os

def render_settings():
     st.header("⚙️ 系统设置")
     st.markdown("在这里配置系统设置")

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