
安装 uv
首先确保已安装 uv。在终端执行：
```
bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -UseBasicParsing | Invoke-Expression
```

## 1.创建虚拟环境
```
cd ./Volcengine-MultiModal-Lab
uv venv
source .venv/bin/activate
```

## 2.安装依赖
```
# 安装所有依赖（包括开发依赖）
uv sync

# 仅安装生产环境依赖
uv sync --no-dev

# uv add volcengine streamlit
```

## 3.设置环境变量
创建 `.env` 文件并设置 AK SK：
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

> 注意：请将上述占位符替换为你的实际密钥值，并确保 `.env` 文件已添加到 `.gitignore` 中以避免泄露敏感信息。

## 4.启动应用
```
streamlit run app.py
```

**api 接口加速** (加速域名找产解配置 visualaccapi.speedifyvolcai.com)

http的签名中，需要将 request_url 的endpoint替换成加速域名

**SDK 调用需要改两个地方**：
1. 在.venv/lib/python3.12/site-packages/volcengine/base/Request.py 文件最后一行改成 
 ```
 return self.schema + '://' + "visualaccapi.speedifyvolcai.com" + self.path + '?' + urlencode(self.query, doseq)
 ```
2. 在.venv/lib/python3.12/site-packages/volcengine/base/Service.py 文件的235行注释掉

```
 # mheaders['Host'] = self.service_info.host
```
