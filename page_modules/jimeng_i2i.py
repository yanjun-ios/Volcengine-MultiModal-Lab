import streamlit as st
import base64
from api_modules.jimeng_image import i2i_jimeng_v30

def render_jimeng_i2i_30(visual_service):
    """既梦AI-图生图3.0页面"""
    st.header("既梦AI-图生图 3.0")
    st.markdown("""
产品优势
**细节保留精准**：可在保持主体元素和图像风格等不变的基础上对图像进行指令编辑，支持增减元素、调整光影、更换背景或修改文字等; 
**指令遵循能力强**： 智能解析复杂编辑指令，对用户意图理解准确。无论是局部细节调整还是全局性修改，均能实现精准响应和高效执行; 
**专业级海报设计**：营销海报场景下的生产力利器，支持生成覆盖广泛行业需求的海报素材，在排版美感与文字设计感方面表现突出; 
    """)
    st.markdown("接口文档: https://www.volcengine.com/docs/85128/1602254")
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("输入参数")
        input_method_jimeng_i2i = st.radio("选择图片来源", ("URL", "上传图片", "示例模板"), key="input_method_jimeng_i2i")
        image_url_jimeng_i2i = None
        uploaded_file_jimeng_i2i = None
        
        style_presets = {
            "元素消除": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_6dc837655edb35b90071547bc0b96e9e.png","prompt":"消除图片中的路人"},
            "元素更改": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_d586db140ae55431890252e42b567e83.jpeg","prompt":"将图片里的主体变成苹果,保留质感,光影,材质不变"},
            "光影变化": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_d2eb521d2805b644ee16ce032a85025d.png","prompt":"保持画面不变，在图片左上角打一束自然的光"},
            "风格转换": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_513b1d605d03f8c080bad2ad61eda88d.png","prompt":"保持背景结构，保持人物特征，风格改成中国水墨画，泼墨细节，工笔，简单的背景"},
            "文字修改": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_a154cafca83c25ca0e8e4dced3c2097b.jpeg","prompt":"字改成图中初夏文字改为夏至，CHU XIA改为Summer Solstice"},
            "设计补全": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_203c395adef4e44b6e5812f6f54b7e9e.png","prompt":'这是一张盛夏潮玩市集宣传海报，主标题使用大字中文"盛夏潮玩市集"与英文"SUMMER MARKET"组合呈现'},
            "商品图背景替换": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_30e36934801512b6416b61590271a24e.png","prompt":"根据图中物品的属性替换背景为其适合的背景场景"},
            "电商促销海报制作": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_1d400b9e85962e4891b8015f5be5ca9b.png","prompt":'电商促销海报设计，一张清新可爱的毛绒玩具海报。正中央放超呆萌的 "蒜鸟" 黄毛绒玩偶：身子圆滚滚的，眼睛像小黑豆，嘴巴和小脚是嫩黄色，头顶顶着一撮绿油油的蒜苗造型帽子！背景采用浅蓝色渐变底色，点缀着不规则散落的白色与绿色小方块增加灵动感；画面上方用黑色粗体字呈现 "蒜鸟，都不涌易" 的趣味 slogan，中部以黄色字体标注 "好东西代表：蒜鸟玩偶" 及 "# 适用人群：脆皮省电人" 等标签化信息，整体营造出符合年轻人审美的可爱清新视觉效果。背景是天空蓝色渐变，清爽，整体很有夏日风格 。'},
            "商品图包装": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_0f37291d4e326a104fe1ff35c074f80b.png","prompt":'海报上方用橙色粗体字写着"居家幸福感拉满！"，文字带有白色描边，下方添加同色系衬底，十分醒目。产品图中的粉色拖鞋周围点缀着星星和小兔子的装饰元素，与拖鞋上的兔子图案相呼应，同时为拖鞋添加白色粗描边，使其更突出。三条文案分别为"踩屎感谁懂！""懒人必备神器""少女心爆棚啦"，均用白色字体，搭配黑色描边，分布在产品图的合适位置。背景是模糊虚化的木质地板场景，色调与商品的粉色、旁边的米色杯子相协调，营造出温馨舒适的居家氛围。整体风格突出产品的柔软舒适与可爱特性，吸引消费者目光。'},
            "拍立得风格": {"url":"https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_78bf49fc071461941cd401d4f6eddca9.png","prompt":"将照片变为这个风格：类似拍立得相纸白色边框，暗朦，隐约的淡彩褪色，非对称，个性视角表达，对焦主体，随意瞬间抓拍模糊场景，y2k，光朦，过曝，复古，低饱和，质感，模糊晕染，强透视，高噪点，胶片颗粒质感，现场感，情绪写意，大片美学，前卫艺术美学，细节丰富，高级感，杰作"},
        }

        # 初始化session state用于存储模板选择的值
        first_template_key = list(style_presets.keys())[0]
        if 'jimeng_i2i_template_url' not in st.session_state:
            st.session_state.jimeng_i2i_template_url = style_presets[first_template_key]["url"]
        if 'jimeng_i2i_template_prompt' not in st.session_state:
            st.session_state.jimeng_i2i_template_prompt = style_presets[first_template_key]["prompt"]

        # 根据选择的输入方式显示不同的输入控件
        if input_method_jimeng_i2i == "URL":
            image_url_jimeng_i2i = st.text_input("输入图片 URL:", "https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_b9d0ea6bb4528cce79517a7c706ad1b7.png", key="image_url_jimeng_i2i")
        elif input_method_jimeng_i2i == "上传图片":
            uploaded_file_jimeng_i2i = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"], key="file_uploader_jimeng_i2i")
        elif input_method_jimeng_i2i == "示例模板":
            # 模板选择回调函数
            def update_template_values():
                selected_style = st.session_state.style_template_selector
                if selected_style in style_presets:
                    st.session_state.jimeng_i2i_template_url = style_presets[selected_style]["url"]
                    st.session_state.jimeng_i2i_template_prompt = style_presets[selected_style]["prompt"]
            
            # 风格模板选择器
            selected_template = st.selectbox(
                "选择示例模板",
                options=list(style_presets.keys()),
                key="style_template_selector",
                on_change=update_template_values
            )
            
            # 显示选中模板的URL（只读）
            st.text_input(
                "模板图片 URL:", 
                value=st.session_state.jimeng_i2i_template_url or style_presets[selected_template]["url"],
                disabled=True,
                key="template_url_display"
            )
            
            # 设置image_url_jimeng_i2i为模板URL
            image_url_jimeng_i2i = st.session_state.jimeng_i2i_template_url or style_presets[selected_template]["url"]

        # 提示词输入框，根据是否选择模板显示不同的默认值
        if input_method_jimeng_i2i == "示例模板":
            prompt_default = st.session_state.jimeng_i2i_template_prompt or style_presets[list(style_presets.keys())[0]]["prompt"]
        else:
            prompt_default = "将小女孩的衣服换成白色的公主裙"
            
        prompt_jimeng_i2i = st.text_area("输入编辑指令:", prompt_default, height=100, key="prompt_jimeng_i2i")
        seed_jimeng_i2i = st.number_input("Seed", value=-1, key="seed_jimeng_i2i")
        width_jimeng_i2i = st.number_input("Width", value=1328, key="width_jimeng_i2i")
        height_jimeng_i2i = st.number_input("Height", value=1328, key="height_jimeng_i2i")
        scale_jimeng_i2i = st.slider("Scale", min_value=0.0, max_value=1.0, value=0.5, step=0.1, key="scale_jimeng_i2i")
        generate_button_jimeng_i2i = st.button("开始编辑", key="button_jimeng_i2i")

    with col2:
        st.subheader("图片预览和编辑结果")
        preview_col, result_col = st.columns(2)

        with preview_col:
            preview_image = None
            if input_method_jimeng_i2i == "URL" and image_url_jimeng_i2i:
                preview_image = image_url_jimeng_i2i
            elif input_method_jimeng_i2i == "上传图片" and uploaded_file_jimeng_i2i is not None:
                preview_image = uploaded_file_jimeng_i2i
            elif input_method_jimeng_i2i == '示例模板':
                preview_image = st.session_state.jimeng_i2i_template_url

            if preview_image is not None:
                st.image(preview_image, caption="图片预览")

        with result_col:
            if generate_button_jimeng_i2i:
                with st.spinner("正在编辑中..."):
                    img_url = None
                    image_base64 = None
                    if input_method_jimeng_i2i == "上传图片" and uploaded_file_jimeng_i2i is not None:
                        image_base64 = base64.b64encode(uploaded_file_jimeng_i2i.getvalue()).decode('utf-8')
                    
                    img_url = i2i_jimeng_v30(
                        visual_service, 
                        prompt=prompt_jimeng_i2i, 
                        seed=seed_jimeng_i2i, 
                        width=width_jimeng_i2i,
                        height=height_jimeng_i2i,
                        scale=scale_jimeng_i2i, 
                        image_url=image_url_jimeng_i2i, 
                        image_base64=image_base64
                    )
                    
                    if img_url:
                        st.image(img_url, caption="编辑后图片")