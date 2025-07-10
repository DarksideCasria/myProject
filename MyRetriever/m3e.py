import os
import torch
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from pdf_parse import DataProcess

script_dir = os.path.dirname(__file__)  # 当前脚本的目录


class M3eRetriever:
    def __init__(self, data_path=None, vector_path=None, pdf_path=None):
        # 关键修改1：增加初始化参数打印
        print(f"\n[DEBUG] 初始化参数: vector_path={vector_path}, data_path={data_path}, pdf_path={pdf_path}")

        # 初始化Embedding模型
        self.embeddings = HuggingFaceEmbeddings(
            model_name="D:/pycharmProject/MyRAG/MyRetriever/m3e_model",
            model_kwargs={"device": "cpu", "trust_remote_code": True},
            encode_kwargs={"batch_size": 64}
        )

        # 关键修改2：封装路径处理方法
        def resolve_path(relative_path):
            if not relative_path:
                return None
            full_path = os.path.normpath(os.path.join(script_dir, relative_path))
            print(f"[DEBUG] 路径转换: {relative_path} => {full_path}")
            return full_path

        # 处理所有路径
        # vector_path = resolve_path(vector_path)
        vector_path = r"D:\pycharmProject\MyRAG\vector_db\faiss_m3e_index"  # 直接硬编码绝对路径
        data_path = resolve_path(data_path)
        pdf_path = resolve_path(pdf_path)
        # 关键修改3：增强索引存在性检查
        index_exists = False
        if vector_path:
            index_file = os.path.join(vector_path, "index.faiss")
            index_exists = os.path.exists(index_file)
            print(f"[DEBUG] 索引检查: {index_file} 存在? {index_exists}")

        if not index_exists:  # 强制重建条件
            print(f"[INFO] 开始构建向量库（原因: {'未指定存储路径' if not vector_path else '索引文件不存在'}）")
            docs = []

            try:
                # 优先处理文本数据
                if data_path and os.path.exists(data_path):
                    with open(data_path, "r", encoding="utf-8") as file:
                        raw_lines = file.readlines()
                        print(f"[DEBUG] 读取到 {len(raw_lines)} 行原始数据")
                        docs = self.data_process(raw_lines)
                    print(f"[INFO] 文本文件加载成功: {os.path.basename(data_path)}")

                # 其次处理PDF文件
                elif pdf_path and os.path.exists(pdf_path):
                    dp = DataProcess(pdf_path)
                    # 多种解析策略
                    dp.ParseBlock(max_seq=1024)
                    dp.ParseBlock(max_seq=512)
                    dp.ParseAllPage(max_seq=256)
                    dp.ParseAllPage(max_seq=512)
                    dp.ParseOnePageWithRule(max_seq=256)
                    dp.ParseOnePageWithRule(max_seq=512)
                    print(f"[INFO] PDF解析完成，生成 {len(dp.data)} 个文本块")
                    docs = self.data_process(dp.data)

                else:
                    raise FileNotFoundError("未找到有效的输入文件")

                # 向量库构建与计时
                import time
                # start_time = time.time()
                # self.vector_store = FAISS.from_documents(docs, self.embeddings)

                # 改为：
                from tqdm import tqdm  # 需先 pip install tqdm

                start_time = time.time()
                print("[PROGRESS] 开始向量化处理...")

                # 分批次处理（显示进度条）
                batch_size = 64
                with tqdm(total=len(docs), desc="生成嵌入向量") as pbar:
                    for i in range(0, len(docs), batch_size):
                        batch = docs[i:i + batch_size]
                        if i == 0:
                            self.vector_store = FAISS.from_documents(batch, self.embeddings)
                        else:
                            self.vector_store.add_documents(batch)
                        pbar.update(len(batch))

                build_time = time.time() - start_time
                print(f"[SUCCESS] 向量库构建完成，耗时 {build_time:.2f} 秒，共处理 {len(docs)} 个文档")

                # 自动保存逻辑
                save_path = vector_path or resolve_path("../vector_db/faiss_m3e_index")
                os.makedirs(save_path, exist_ok=True)
                self.vector_store.save_local(save_path)
                print(f"[INFO] 索引已保存至: {save_path}")

            except Exception as e:
                print(f"[ERROR] 构建失败: {str(e)}")
                raise

        else:  # 直接加载已有索引
            print(f"[INFO] 正在加载已有索引...")
            try:
                self.vector_store = FAISS.load_local(
                    vector_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print(f"[SUCCESS] 索引加载成功，当前文档数: {self.vector_store.index.ntotal}")
            except Exception as e:
                print(f"[ERROR] 索引加载失败: {str(e)}")
                raise

        # 资源清理
        del self.embeddings
        torch.cuda.empty_cache()

    def data_process(self, data):
        """数据清洗和格式化"""
        # data=data[:100]
        docs = []
        for idx, line in enumerate(data):
            line = line.strip("\n").strip()
            if not line:
                continue
            # 处理制表符分隔的数据
            parts = line.split("\t")
            clean_text = parts[0].strip() if len(parts) > 0 else line
            docs.append(Document(
                page_content=clean_text,
                metadata={"id": idx, "source": "text" if "\t" not in line else "structured"}
            ))
        print(f"[DEBUG] 有效文档数: {len(docs)}")
        return docs

    def GetTopK(self, query, k=3):
        """带相似度得分的检索"""
        return self.vector_store.similarity_search_with_score(query, k=k)

    def GetvectorStore(self):
        return self.vector_store


if __name__ == "__main__":
    # 测试用例（根据需要切换注释）

    # 用例1：强制重建（不指定vector_path）
    # retriever = M3eRetriever(
    #     data_path="../all_text.txt",
    #     # pdf_path="../Oxford.pdf",  # 切换数据源
    # )

    # 用例2：加载现有索引
    retriever = M3eRetriever()
    #     vector_path="../vector_db/faiss_m3e_index"
    # )

    # 执行查询
    results = retriever.GetTopK("天文学", 2)
    print(f'results的类型是{type(results)}')
    for doc, score in results:
        print(f"\n[相似度 {score:.4f}] {doc.page_content[:80]}...")

