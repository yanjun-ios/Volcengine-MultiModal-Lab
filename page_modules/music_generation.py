import streamlit as st
import requests
from api_modules.generation_music import generation_bgm

def render_music_generation():
    """音乐生成页面"""
    st.header("🎵 音乐生成")
    st.markdown("使用火山引擎音乐生成API创建背景音乐")
    st.markdown("接口文档: https://www.volcengine.com/docs/84992/1535146")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("输入参数")
        
        # 文本描述
        text_music = st.text_area(
            "音乐描述文本:",
            "现代感十足的商业广告配乐",
            height=100,
            key="text_music",
            help="描述您想要生成的音乐风格和用途"
        )
        
        # 音乐时长
        duration_music = st.slider(
            "音乐时长 (秒)",
            min_value=1,
            max_value=60,
            value=15,
            key="duration_music",
            help="生成音乐的时长，范围1-60秒"
        )
        
        # 音乐风格 (Genre) - 多选
        st.subheader("音乐风格 (Genre)")
        genre_options = [
            "pop(流行)", "rock(摇滚)", "jazz(爵士)", "classical(古典)", "electronic(电子)", "hip-hop(嘻哈)", 
            "country(乡村)", "folk(民谣)", "blues(蓝调)", "reggae(雷鬼)", "latin(拉丁)", "world(世界音乐)",
            "ambient(环境音乐)", "cinematic(电影配乐)", "corporate(企业)", "upbeat(欢快)", "chill(轻松)", "dramatic(戏剧性)"
        ]
        
        selected_genres_display = st.multiselect(
            "选择音乐风格 (最多10个):",
            options=genre_options,
            default=["corporate(企业)"],
            key="genre_music",
            help="选择适合的音乐风格，可多选"
        )
        
        # 提取英文部分用于API调用
        selected_genres = [genre.split('(')[0] for genre in selected_genres_display]
        
        # 限制选择数量
        if len(selected_genres) > 10:
            st.warning("⚠️ 最多只能选择10个风格，请减少选择")
            selected_genres = selected_genres[:10]
        
        # 音乐情绪 (Mood) - 多选
        st.subheader("音乐情绪 (Mood)")
        mood_options = [
            "happy(快乐)", "sad(悲伤)", "energetic(充满活力)", "calm(平静)", "peaceful(宁静)", "soft(柔和)",
            "dramatic(戏剧性)", "mysterious(神秘)", "romantic(浪漫)", "nostalgic(怀旧)", "hopeful(充满希望)",
            "tense(紧张)", "relaxing(放松)", "uplifting(振奋)", "melancholic(忧郁)", "triumphant(胜利)"
        ]
        
        selected_moods_display = st.multiselect(
            "选择音乐情绪 (最多10个):",
            options=mood_options,
            default=["peaceful(宁静)", "soft(柔和)"],
            key="mood_music",
            help="选择音乐要表达的情绪，可多选"
        )
        
        # 提取英文部分用于API调用
        selected_moods = [mood.split('(')[0] for mood in selected_moods_display]
        
        # 限制选择数量
        if len(selected_moods) > 10:
            st.warning("⚠️ 最多只能选择10个情绪，请减少选择")
            selected_moods = selected_moods[:10]
        
        # 乐器 (Instrument) - 多选
        st.subheader("乐器 (Instrument)")
        instrument_options = [
            "piano(钢琴)", "guitar(吉他)", "violin(小提琴)", "drums(鼓)", "bass(贝斯)", "strings(弦乐)",
            "brass(铜管乐)", "woodwind(木管乐)", "synthesizer(合成器)", "organ(管风琴)", "harp(竖琴)",
            "flute(长笛)", "saxophone(萨克斯)", "trumpet(小号)", "cello(大提琴)", "acoustic_guitar(原声吉他)"
        ]
        
        selected_instruments_display = st.multiselect(
            "选择乐器 (最多10个):",
            options=instrument_options,
            default=["piano(钢琴)", "strings(弦乐)"],
            key="instrument_music",
            help="选择想要包含的乐器，可多选"
        )
        
        # 提取英文部分用于API调用
        selected_instruments = [instrument.split('(')[0] for instrument in selected_instruments_display]
        
        # 限制选择数量
        if len(selected_instruments) > 10:
            st.warning("⚠️ 最多只能选择10个乐器，请减少选择")
            selected_instruments = selected_instruments[:10]
        
        # 主题 (Theme) - 多选
        st.subheader("音乐主题 (Theme)")
        theme_options = [
            "every day(日常)", "celebration(庆祝)", "adventure(冒险)", "romance(浪漫)", "nature(自然)",
            "technology(科技)", "business(商务)", "travel(旅行)", "family(家庭)", "friendship(友谊)",
            "success(成功)", "inspiration(励志)", "meditation(冥想)", "workout(健身)", "party(派对)"
        ]
        
        selected_themes_display = st.multiselect(
            "选择音乐主题 (最多10个):",
            options=theme_options,
            default=["every day(日常)"],
            key="theme_music",
            help="选择音乐的主题场景，可多选"
        )
        
        # 提取英文部分用于API调用
        selected_themes = [theme.split('(')[0] for theme in selected_themes_display]
        
        # 限制选择数量
        if len(selected_themes) > 10:
            st.warning("⚠️ 最多只能选择10个主题，请减少选择")
            selected_themes = selected_themes[:10]
        
        # 生成按钮
        generate_button_music = st.button("🎵 生成音乐", key="button_music", type="primary")
    
    with col2:
        st.subheader("生成结果")
        
        # 显示当前选择的参数
        with st.expander("📋 当前参数预览", expanded=True):
            st.write(f"**描述文本:** {text_music}")
            st.write(f"**时长:** {duration_music} 秒")
            st.write(f"**风格:** {', '.join(selected_genres) if selected_genres else '未选择'}")
            st.write(f"**情绪:** {', '.join(selected_moods) if selected_moods else '未选择'}")
            st.write(f"**乐器:** {', '.join(selected_instruments) if selected_instruments else '未选择'}")
            st.write(f"**主题:** {', '.join(selected_themes) if selected_themes else '未选择'}")
        
        if generate_button_music:
            # 验证必要参数
            if not text_music.strip():
                st.error("❌ 请输入音乐描述文本")
            elif not selected_genres:
                st.error("❌ 请至少选择一个音乐风格")
            elif not selected_moods:
                st.error("❌ 请至少选择一个音乐情绪")
            elif not selected_instruments:
                st.error("❌ 请至少选择一个乐器")
            elif not selected_themes:
                st.error("❌ 请至少选择一个音乐主题")
            elif len(selected_genres) > 10 or len(selected_moods) > 10 or len(selected_instruments) > 10 or len(selected_themes) > 10:
                st.error("❌ 每个类别最多只能选择10个选项")
            else:
                # 获取API密钥 - 使用与图像生成相同的密钥
                music_ak = st.session_state.ak
                music_sk = st.session_state.sk
                
                if not music_ak or not music_sk:
                    st.error("❌ 请先在设置页面配置火山引擎API密钥 (VOLC_ACCESSKEY 和 VOLC_SECRETKEY)")
                    st.info("💡 提示：音乐生成使用与图像生成相同的火山引擎API密钥")
                else:
                    with st.spinner("🎵 正在生成音乐，请耐心等待..."):
                        try:
                            # 调用音乐生成API
                            audio_url = generation_bgm(
                                ak=music_ak,
                                sk=music_sk,
                                text=text_music,
                                genre=selected_genres,
                                mood=selected_moods,
                                instrument=selected_instruments,
                                theme=selected_themes,
                                Duration=duration_music
                            )
                            
                            if audio_url:
                                st.success("✅ 音乐生成成功！")
                                
                                # 音频播放器 - 直接下载并播放
                                st.subheader("🎵 音频播放器")
                                
                                try:
                                    with st.spinner("🔄 正在下载音频文件..."):
                                        # 下载音频文件
                                        response = requests.get(audio_url, timeout=30)
                                        response.raise_for_status()
                                        
                                        # 根据Content-Type确定文件扩展名
                                        content_type = response.headers.get('content-type', '').lower()
                                        if 'mp3' in content_type:
                                            ext = '.mp3'
                                            audio_format = 'audio/mp3'
                                        elif 'wav' in content_type:
                                            ext = '.wav'
                                            audio_format = 'audio/wav'
                                        elif 'ogg' in content_type:
                                            ext = '.ogg'
                                            audio_format = 'audio/ogg'
                                        elif 'mp4' in content_type:
                                            ext = '.mp4'
                                            audio_format = 'audio/mp4'
                                        else:
                                            # 默认为mp3，但也尝试从URL推断
                                            if audio_url.lower().endswith('.wav'):
                                                ext = '.wav'
                                                audio_format = 'audio/wav'
                                            elif audio_url.lower().endswith('.ogg'):
                                                ext = '.ogg'
                                                audio_format = 'audio/ogg'
                                            else:
                                                ext = '.mp3'
                                                audio_format = 'audio/mp3'
                                        
                                        # 直接使用音频字节数据播放
                                        audio_bytes = response.content
                                        st.audio(audio_bytes, format=audio_format)
                                        st.success("✅ 音频加载成功！")
                                        
                                        # 显示文件信息
                                        file_size_kb = len(audio_bytes) / 1024
                                        st.info(f"🎵 **音乐信息:** 时长 {duration_music} 秒 | 文件大小 {file_size_kb:.1f} KB | 格式 {ext[1:].upper()}")
                                        
                                except requests.exceptions.RequestException as e:
                                    st.error(f"❌ 下载音频文件失败: {str(e)}")
                                    st.write("可能的原因：")
                                    st.write("- 网络连接问题")
                                    st.write("- 音频URL已过期")
                                    st.write("- 服务器响应超时")
                                    
                                except Exception as e:
                                    st.error(f"❌ 音频播放失败: {str(e)}")
                                    st.write("可能的原因：")
                                    st.write("- 音频文件格式不支持")
                                    st.write("- 文件损坏或不完整")
                                
                                # 提供下载链接
                                st.markdown("---")
                                st.subheader("📥 下载选项")
                                st.markdown(f"🔗 [点击下载音乐文件]({audio_url})")
                                st.info("💡 **提示:** 右键点击上方链接，选择'另存为'可将音频文件保存到本地。")
                                
                            else:
                                st.error("❌ 音乐生成失败，请检查参数或稍后重试")
                                
                        except Exception as e:
                            st.error(f"❌ 生成音乐时出错: {str(e)}")
                            st.info("💡 请检查API密钥是否正确，或稍后重试")