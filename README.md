```
# Campus Course QA 课程问答 RAG 系统
基于 LangChain + Chroma 向量库的课程知识库问答系统，支持上传课程文档，基于文档内容回答问题，减少大模型幻觉。

## ✨ 功能特性
- 文档入库：支持 PDF / TXT 课程资料上传，自动文本切分、向量化
- 向量检索：Chroma 本地持久化向量数据库，检索相关片段
- RAG 问答：基于检索到的文档内容回答课程相关问题
- 可配置大模型：支持 DeepSeek、通义千问等 OpenAI 兼容接口
- 本地部署：向量库保存在本地，不需要额外数据库服务
- 溯源查看：回答附带引用的原文片段

## 🛠️ 技术栈
- Python 3.9+
- LangChain
- langchain-chroma + Chromadb
- OpenAI 兼容大模型接口
- Streamlit（前端交互）

## 📁 项目结构
```

campus_course_qa/ ├── main.py                # 入口 + streamlit 页面 ├── rag_service.py         # RAG 核心服务（文档加载、切分、向量库、问答链） ├── chroma_db/             # 向量数据库持久化目录（自动生成） ├── requirements.txt       # 依赖清单 └── README.md              # 项目说明

```
## 📦 环境安装
> ⚠️ 注意：Windows 虚拟环境容易出现【假激活】问题，优先两种方案：
> 方案A：直接使用全局Python3.9（本次成功运行方案）
> 方案B：使用虚拟环境，安装时使用 `python -m pip` 避免pip路径错乱

### 1. 安装依赖
```bash
# 全局环境（你当前可用）
pip install langchain langchain-chroma chromadb streamlit openai -i https://pypi.tuna.tsinghua.edu.cn/simple
```

如果使用虚拟环境：

```
# 创建虚拟环境
python -m venv .venv
# 激活（PowerShell）
.venv\Scripts\Activate.ps1
# 安装（强制使用venv内python）
.venv\Scripts\python.exe -m pip install langchain langchain-chroma chromadb streamlit openai -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 🚀 启动项目

```
streamlit run main.py
```

启动后自动打开浏览器页面，默认地址：`http://localhost:8501`

## 📝 使用流程

1. 在页面填入大模型配置：API Key、BaseURL、模型名称
2. 上传课程文档（PDF/TXT），点击【加载文档并构建知识库】
3. 等待文档切片、向量化入库
4. 在问答框输入课程相关问题，获取基于文档的回答
5. 可查看检索到的原文片段

## ❗ 常见问题（踩坑记录）

### Q1 ModuleNotFoundError: No module named 'langchain_chroma'

原因：包没有安装到当前运行的 Python 环境 解决：

```
pip install langchain-chroma chromadb -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> 重点：保证运行代码的 python 和 pip 是同一个环境。

### Q2 终端显示 (.venv) 但是 pip 还是全局路径（假激活）

PowerShell 激活策略问题，不要直接用 pip，改用：

```
.venv\Scripts\python.exe -m pip install xxx
```

### Q3 检索不到内容、回答和文档无关

- 检查文档是否成功上传入库
- 调整文本切片大小（chunk_size /chunk_overlap）
- 调整检索数量 k
- 更换 embedding 模型

### Q4 想清空知识库

直接删除文件夹 `chroma_db/`，重新上传文档即可。

## 📌 配置说明

- 向量库持久化目录：`chroma_db/`
- 可在 rag_service.py 修改：切片大小、检索 top-k、embedding 模型
- 支持所有兼容 OpenAI 接口格式的大模型