import streamlit as st

def render_sidebar():
    """渲染侧边栏菜单"""
    
    # 自定义CSS样式 - 简约现代化左侧菜单
    st.markdown("""
    <style>
    /* 侧边栏整体样式 */
    .css-1d391kg {
        background-color: #f8f9fa;
        padding-top: 1rem;
    }

    /* 隐藏默认按钮样式 */
    .stButton > button {
        background: transparent !important;
        border: none !important;
        padding: 8px 16px !important;
        color: #495057 !important;
        text-decoration: none !important;
        height: auto !important;
        width: 100% !important;
        text-align: left !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        border-radius: 6px !important;
        margin: 2px 0 !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
    }

    .stButton > button:hover {
        background-color: #e9ecef !important;
        color: #212529 !important;
    }

    .stButton > button:focus {
        background-color: #e9ecef !important;
        color: #212529 !important;
        box-shadow: none !important;
    }

    [data-testid="stSidebarContent"] div[data-testid="stMarkdownContainer"] {
        width: 100%;
        text-align: left;
    }

    /* 菜单分组样式 */
    .menu-group {
        margin: 10px 0 10px 0;
        padding: 0 16px;
        font-size: 12px;
        font-weight: 600;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* 分割线样式 */
    .menu-divider {
        height: 1px;
        background-color: #dee2e6;
        margin: 12px 16px;
        border: none;
    }

    /* 侧边栏标题 */
    .sidebar-title {
        font-size: 18px;
        font-weight: 600;
        color: #212529;
        text-align: center;
        margin-bottom: 24px;
        padding: 0 16px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 使用侧边栏菜单选择功能模块
    st.sidebar.markdown('<div class="sidebar-title">功能菜单</div>', unsafe_allow_html=True)

    # 初始化选中状态
    if 'selected_function' not in st.session_state:
        st.session_state.selected_function = "通用3.0-文生图"

    # 图像生成菜单
    image_generation_menu = [
        "通用3.0-文生图",
        "图生图3.0-人像写真", 
        "图生图3.0-指令编辑",
        "图生图3.0-角色特征保持",
        "智能绘图 - 图像特效",
        "方舟-文生图3.0",
        "方舟-图像编辑3.0",
        "既梦AI-文生图2.1",
        "既梦AI-文生图3.0",
        "既梦AI-文生图3.1",
        "既梦AI-图生图3.0"
    ]

    # 视频生成菜单
    video_generation_menu = [
        "文生视频",
        "图生视频",
        "既梦AI-文生视频",
        "既梦AI-图生视频",
        "视频生成-视频特效",
    ]

    # 其他
    others_menu = [
        "TTS",
        "音乐生成",
        "数字人(Omni_Human)"
    ]

    # 添加分组标题
    st.sidebar.markdown('<div class="menu-group">图片生成</div>', unsafe_allow_html=True)

    # 图片生成菜单
    for im in image_generation_menu:
        if st.sidebar.button(im, key=f"menu_{im}"):
            st.session_state.selected_function = im
            st.rerun()

    # 分割线
    st.sidebar.markdown('<hr class="menu-divider">', unsafe_allow_html=True)
    # 视频生成分组
    st.sidebar.markdown('<div class="menu-group">视频生成</div>', unsafe_allow_html=True)

    # 视频生成菜单
    for vm in video_generation_menu:
        if st.sidebar.button(vm, key=f"menu_{vm}"):
            st.session_state.selected_function = vm
            st.rerun()
    # 分割线
    st.sidebar.markdown('<hr class="menu-divider">', unsafe_allow_html=True)
    # 其他生成分组
    st.sidebar.markdown('<div class="menu-group">其他</div>', unsafe_allow_html=True)
    # 其他生成菜单
    for om in others_menu:
        if st.sidebar.button(om, key=f"menu_{om}"):
            st.session_state.selected_function = om
            st.rerun()
    # 分割线
    st.sidebar.markdown('<hr class="menu-divider">', unsafe_allow_html=True)

    # 设置按钮
    st.sidebar.markdown('<div class="menu-group">系统设置</div>', unsafe_allow_html=True)
    if st.sidebar.button("⚙️ 设置", key="settings_button"):
        st.session_state.selected_function = "设置"
        st.rerun()

    return st.session_state.selected_function