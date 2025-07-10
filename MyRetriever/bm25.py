from langchain_community.retrievers import BM25Retriever
from langchain.schema import Document
from pdf_parse import DataProcess
import jieba


# BM25召回
class Bm25Retriever(object):
    def __init__(self, data_path=None, pdf_path=None):
        docs = []
        full_docs = []
        if data_path is not None:
            with open(data_path, "r", encoding="utf-8") as file:
                docs, full_docs = self.data_process(file)
        if pdf_path is not None:
            dp = DataProcess(pdf_path)
            dp.ParseBlock(max_seq=1024)
            dp.ParseBlock(max_seq=512)
            dp.ParseAllPage(max_seq=256)
            dp.ParseAllPage(max_seq=512)
            dp.ParseOnePageWithRule(max_seq=256)
            dp.ParseOnePageWithRule(max_seq=512)
            print("bm25 pdf_parse is ok")
            docs, full_docs = self.data_process(dp.data)
        self.documents = docs
        self.full_documents = full_docs
        self.retriever = self._init_bm25()

    # 对解析后的文本数据进行处理
    def data_process(self, data):
        docs = []
        full_docs = []
        for idx, line in enumerate(data):
            line = line.strip("\n").strip()
            if len(line) < 5:
                continue
            tokens = " ".join(jieba.cut_for_search(line))
            docs.append(Document(page_content=tokens, metadata={"id": idx}))
            words = line.split("\t")
            full_docs.append(Document(page_content=words[0], metadata={"id": idx}))
        return docs, full_docs

    # 初始化BM25的知识库
    def _init_bm25(self):
        return BM25Retriever.from_documents(self.documents)

    def GetBM25TopK(self, query, top_k):
        self.retriever.k = top_k
        query = " ".join(jieba.cut_for_search(query))
        ans_docs = self.retriever.invoke(query)
        ans = []
        seen_contents = set()
        for line in ans_docs:
            doc = self.full_documents[line.metadata["id"]]
            if doc.page_content not in seen_contents:
                ans.append(doc)
                seen_contents.add(doc.page_content)
            if len(ans) >= top_k:
                break
        return ans


if __name__ == "__main__":
    data_path = "../all_text.txt"
    pdf_path = "../Oxford.pdf"

    # bm25 = Bm25Retriever(pdf_path)
    bm25 = Bm25Retriever(data_path)
    res = bm25.GetBM25TopK("天文", 2)

    print(type(res))
    # 打印检索结果
    for idx, doc in enumerate(res):
        print(f"\n=== Top {idx + 1} 文档内容 ===")
        print(doc.page_content[:500])  # 只显示前500字，防止太长






