
# 火山引擎多模态体验中心 🎨

一个基于火山引擎AI服务的多模态内容生成平台，集成了火山引擎图像生成、视频生成、音乐生成、数字人生成等多种AI能力，提供直观易用的Web界面，所有功能均直接调用火山引擎官方API接口，可以方便的通过界面调试各类AI接口效果。

## 项目介绍

火山引擎多模态体验中心是一个综合性的AI内容生成平台，整合了火山引擎智能视觉、既梦AI、方舟等多个AI服务的能力。用户可以通过简洁的Web界面体验各种AI生成功能，包括：

### 🖼️ 图像生成能力
- **文生图**: 通过文本描述生成高质量图像
- **图生图**: 基于参考图像进行风格转换和编辑
- **人像写真**: 专业级人像照片生成
- **角色特征保持**: 保持角色一致性的图像生成
- **图像特效**: 智能图像风格化处理

### 🎬 视频生成能力
- **文生视频**: 从文本描述生成动态视频
- **图生视频**: 将静态图像转换为动态视频
- **视频特效**: 视频风格化和特效处理

### 🎵 其他AI能力
- **音乐生成**: AI背景音乐创作
- **数字人**: 虚拟数字人生成
- **语音合成**: 文本转语音(TTS)

## 项目结构

```
Volcengine-MultiModal-Lab/
├── app.py                      # 主应用入口
├── main.py                     # 启动脚本
├── .env                        # 环境变量配置
├── pyproject.toml              # 项目依赖配置
├── 
├── api_modules/                # API模块目录
│   ├── __init__.py
│   ├── visual_image.py         # 火山引擎图像API
│   ├── visual_video.py         # 火山引擎视频API
│   ├── jimeng_image.py         # 既梦AI图像API
│   ├── jimeng_video.py         # 既梦AI视频API
│   ├── ark_image.py            # 方舟图像API
│   ├── ark_video.py            # 方舟视频API
│   └── generation_music.py     # 音乐生成API
│
├── page_modules/               # 页面模块目录
│   ├── t2i_general.py          # 通用文生图页面
│   ├── i2i_portrait.py         # 人像写真页面
│   ├── i2i_edit.py             # 图像编辑页面
│   ├── video_effects.py        # 视频特效页面
│   ├── music_generation.py     # 音乐生成页面
│   └── ...                     # 其他功能页面
│
├── components/                 # UI组件目录
│   └── sidebar.py              # 侧边栏组件
│
├── utils/                      # 工具函数目录
│   ├── page_router.py          # 页面路由器
│   ├── tos_utils.py            # TOS存储工具
│   └── llm_prompt_optmize.py   # 提示词优化
│
└── README.md                   # 项目说明文档
```

## 使用方法

### 环境准备

首先确保已安装 uv。在终端执行：

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -UseBasicParsing | Invoke-Expression
```

### 1. 创建虚拟环境

```bash
cd ./Volcengine-MultiModal-Lab
uv venv
source .venv/bin/activate  # macOS/Linux
# 或 .venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
# 安装所有依赖（包括开发依赖）
uv sync

# 仅安装生产环境依赖
uv sync --no-dev
```

### 3. 设置环境变量

创建 `.env` 文件并设置 API 密钥：

```bash
# 创建 .env 文件
touch .env
```

在 `.env` 文件中添加以下配置：

```env
# 火山引擎 API 密钥
VOLCENGINE_API_KEY=your_volcengine_api_key_here

# 火山引擎访问密钥
VOLC_ACCESSKEY=your_access_key_here
VOLC_SECRETKEY=your_secret_key_here

# TOS 存储桶名称
TOS_BUCKET_NAME=your_bucket_name_here
```

> ⚠️ **注意**: 请将上述占位符替换为你的实际密钥值，并确保 `.env` 文件已添加到 `.gitignore` 中以避免泄露敏感信息。

### 4. 启动应用

```bash
# 方式1: 使用 Streamlit 直接启动
streamlit run app.py

# 方式2: 使用项目启动脚本
python main.py
```

应用启动后，在浏览器中访问 `http://localhost:8501` 即可使用。

### API 接口加速配置

如需使用加速域名 `visualaccapi.speedifyvolcai.com`，需要修改以下文件：

**SDK 调用需要改两个地方**：

1. 在 `.venv/lib/python3.12/site-packages/volcengine/base/Request.py` 文件最后一行改成：
   ```python
   return self.schema + '://' + "visualaccapi.speedifyvolcai.com" + self.path + '?' + urlencode(self.query, doseq)
   ```

2. 在 `.venv/lib/python3.12/site-packages/volcengine/base/Service.py` 文件的235行注释掉：
   ```python
   # mheaders['Host'] = self.service_info.host
   ```

## 添加新功能方式

### 1. 添加新的API功能

1. **创建API模块**: 在 `api_modules/` 目录下创建新的API模块文件
2. **实现API函数**: 按照现有模块的结构实现API调用函数
3. **更新导入**: 在需要使用的页面模块中导入新的API函数

示例：
```python
# api_modules/new_service.py
def new_api_function(service, params):
    """新的API功能实现"""
    # API调用逻辑
    pass
```

### 2. 添加新的页面功能

1. **创建页面模块**: 在 `page_modules/` 目录下创建新的页面文件
2. **实现渲染函数**: 创建 `render_xxx()` 函数实现页面UI
3. **更新侧边栏**: 在 `components/sidebar.py` 中添加新的菜单项
4. **更新路由**: 在 `utils/page_router.py` 中添加新的路由规则

示例：
```python
# page_modules/new_feature.py
import streamlit as st

def render_new_feature(service):
    """渲染新功能页面"""
    st.header("新功能")
    # 页面UI实现
```

### 3. 添加新的工具函数

在 `utils/` 目录下创建新的工具模块，实现通用的辅助函数。

## 技术栈

### 核心框架
- **Streamlit**: Web应用框架，提供交互式UI
- **Python 3.12+**: 主要开发语言

### AI服务SDK
- **volcengine**: 火山引擎官方SDK
- **volcenginesdkarkruntime**: 方舟服务SDK

### 存储服务
- **TOS**: 火山引擎对象存储服务

### 开发工具
- **uv**: 现代Python包管理器
- **python-dotenv**: 环境变量管理

### 项目依赖
```toml
[project]
dependencies = [
    "dotenv>=0.9.9",
    "sign>=0.0.2", 
    "streamlit>=1.47.1",
    "tos>=2.8.4",
    "volcengine>=1.0.194",
    "volcengine-python-sdk[ark]>=4.0.7",
]
```

## 贡献指南

### 开发环境设置

1. **Fork 项目**: 在GitHub上fork本项目到你的账户
2. **克隆代码**: `git clone https://github.com/your-username/Volcengine-MultiModal-Lab.git`
3. **创建分支**: `git checkout -b feature/your-feature-name`
4. **安装依赖**: 按照上述"使用方法"章节设置开发环境

### 代码规范

1. **代码风格**: 遵循PEP 8 Python代码规范
2. **函数命名**: 使用描述性的函数名，API函数以服务名开头
3. **注释文档**: 为所有公共函数添加docstring说明
4. **错误处理**: 添加适当的异常处理和用户友好的错误提示

### 提交规范

1. **提交信息**: 使用清晰的提交信息描述变更内容
2. **功能测试**: 确保新功能在本地环境正常工作
3. **文档更新**: 如有必要，更新相关文档

### Pull Request流程

1. **创建PR**: 向主分支提交Pull Request
2. **描述变更**: 详细描述新功能或修复的问题
3. **代码审查**: 等待维护者审查代码
4. **合并代码**: 审查通过后合并到主分支

### 问题反馈

- **Bug报告**: 使用GitHub Issues报告问题
- **功能建议**: 提交功能请求和改进建议
- **技术讨论**: 参与项目相关的技术讨论

### 开发注意事项

1. **API密钥安全**: 不要在代码中硬编码API密钥
2. **依赖管理**: 新增依赖时更新 `pyproject.toml`
3. **模块化设计**: 保持代码模块化，便于维护和扩展
4. **用户体验**: 关注界面友好性和操作便捷性

---

感谢你对火山引擎多模态实验室项目的贡献！如有任何问题，欢迎通过Issues或讨论区与我们交流。
