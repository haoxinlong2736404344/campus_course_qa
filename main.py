import streamlit as st
import tempfile
import os
from rag_service import CampusCourseRAG

st.set_page_config(page_title="校园课程知识库问答系统", layout="wide")

if "rag_engine" not in st.session_state:
    st.session_state["rag_engine"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

st.title("📚 校园课程知识库智能问答系统")

with st.sidebar:
    st.header("⚙ API配置")
    api_key = st.text_input("API_KEY", type="password")
    base_url = st.text_input("Base URL", value="https://api.deepseek.com/v1")
    model_name = st.text_input("模型名称", value="deepseek-chat")

    st.divider()
    st.header("📂上传课程文档")
    uploaded_files = st.file_uploader("上传PDF / TXT课件", accept_multiple_files=True, type=["pdf", "txt"])

    btn_init = st.button("🔧初始化知识库系统")
    btn_upload = st.button("📥将上传文档载入向量库")
    btn_clear_chat = st.button("🗑清空对话历史")

    if btn_init:
        if not api_key:
            st.error("请填写API_KEY！")
        else:
            try:
                st.session_state["rag_engine"] = CampusCourseRAG(api_key, base_url, model_name)
                st.success("✅系统初始化完成，可以上传文档！")
            except Exception as e:
                st.error(f"初始化失败：{str(e)}")

    if btn_upload:
        rag = st.session_state.get("rag_engine")
        if rag is None:
            st.warning("请先【初始化知识库系统】！")
        elif not uploaded_files:
            st.warning("请先选择要上传的文件！")
        else:
            for up_file in uploaded_files:
                with tempfile.NamedTemporaryFile(delete=False, suffix=up_file.name) as tmp_f:
                    tmp_f.write(up_file.read())
                    tmp_path = tmp_f.name
                try:
                    chunk_count = rag.load_file_to_vector(tmp_path)
                    st.success(f"✅{up_file.name} 导入成功，切片数量：{chunk_count}")
                except Exception as err:
                    st.error(f"导入失败 {up_file.name} : {err}")
                finally:
                    os.unlink(tmp_path)

    if btn_clear_chat:
        st.session_state["chat_history"] = []
        st.rerun()

for chat_item in st.session_state["chat_history"]:
    with st.chat_message("user"):
        st.markdown(chat_item["question"])
    with st.chat_message("assistant"):
        st.markdown(chat_item["answer"])
        if chat_item["sources"]:
            with st.expander("📎参考知识库片段"):
                for idx, doc in enumerate(chat_item["sources"]):
                    st.markdown(f"**片段{idx+1}**")
                    st.text(doc.page_content[:600])

user_input = st.chat_input("请输入课程相关问题...")
if user_input:
    rag = st.session_state.get("rag_engine")
    if rag is None:
        st.warning("⚠请先在侧边栏完成API配置并初始化系统！")
    else:
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("AI正在检索课程知识库并生成回答..."):
                try:
                    ans, source_list = rag.query(user_input)
                    st.markdown(ans)
                    with st.expander("📎参考知识库片段"):
                        for idx, doc in enumerate(source_list):
                            st.markdown(f"**片段{idx+1}**")
                            st.text(doc.page_content[:600])
                    st.session_state["chat_history"].append({
                        "question": user_input,
                        "answer": ans,
                        "sources": source_list
                    })
                except Exception as e:
                    st.error(f"请求异常：{str(e)}")
