import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

CHROMA_DB_PATH = "./chroma_db"

class CampusCourseRAG:
    def __init__(self, api_key: str, base_url: str, model_name: str = "deepseek-chat"):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name

        self.embedding = OpenAIEmbeddings(
            api_key=self.api_key,
            base_url=self.base_url,
            model="text-embedding-v2"
        )

        self.vector_store = Chroma(
            persist_directory=CHROMA_DB_PATH,
            embedding_function=self.embedding
        )

        self.llm = ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model_name,
            temperature=0.2
        )

        self.retrieval_chain = None
        self._build_chain()

    def _build_chain(self):
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

        system_prompt = (
            "你是校园课程问答助手，请严格依据下面的课程知识库内容回答学生的问题。"
            "如果知识库没有相关信息，直接回答：【知识库未找到该课程相关内容，无法作答】，不要编造内容。"
            "回答尽量简洁清晰，分点输出。\n"
            "知识库上下文：{context}"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])

        combine_docs_chain = create_stuff_documents_chain(self.llm, prompt)
        self.retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

    def load_file_to_vector(self, file_path: str):
        if file_path.lower().endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file_path.lower().endswith(".txt"):
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            raise Exception("仅支持 pdf / txt 文件")

        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100
        )
        split_docs = text_splitter.split_documents(docs)
        self.vector_store.add_documents(split_docs)
        return len(split_docs)

    def query(self, question: str):
        if self.retrieval_chain is None:
            raise Exception("RAG链未初始化")
        result = self.retrieval_chain.invoke({"input": question})
        answer = result["answer"]
        source_docs = result["context"]
        return answer, source_docs
