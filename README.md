
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

## 3.设置AK SK
```
export VOLC_ACCESS_KEY=
export VOLC_SECRET_KEY=
export API_KEY=
```

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
