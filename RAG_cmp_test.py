from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama  # 修改导入
from langchain_core.runnables import RunnablePassthrough
from ExternalRAG import main
from InternalRAG import inMain
from MyRetriever.bm25 import Bm25Retriever
from MyRetriever.m3e import M3eRetriever
import os


def initial():
    # 修改为使用Ollama调用本地Llama3模型
    llm = Ollama(
        base_url="http://localhost:11434",  # 本地Ollama服务地址
        model="llama3:8b",  # 指定模型名称
        temperature=0.7,
        num_predict=1024  # 注意参数名称变化
    )

    act_template = """
    我是你的天文问题专家！
    {description} 是我的独特特征
    现在准备好接收你的问题

    【任务说明】
    1. 先仔细看看用户提供的资料：
    {search_information}

    2. 然后分析用户的问题：
    "{question}"

    3. 回答时要：
     要有逻辑
     请灵活有选择性地地结合使用用户给的资料和你自己的知识回答问题（但要用自然的口语表达，并要有逻辑）
     用英文回答
     最后更新我们的亲密度评分(0到10分以内)

    现在开始思考如何用最专业的方式回答吧！
    """

    prompt = PromptTemplate(
        template=act_template,
        input_variables=["description", "search_information", "question", "relationship_score"]
    )

    chain = (
            RunnablePassthrough.assign(
                description=lambda _: "专业严谨且知识渊博",
                search_information=lambda x: x["search_information"],
                question=lambda x: x["question"],
                relationship_score=lambda x: x.get("relationship_score", 5)
            )
            | prompt
            | llm
    )
    return chain


def initial_contrast():
    # 对比模型也改为Llama3
    llm = Ollama(
        base_url="http://localhost:11434",
        model="llama3:8b",
        temperature=0.7,
        num_predict=1024
    )

    act_template = '''我会给你一个问题，你给我一个输出结果，请用英文回答，问题是：{question}'''

    prompt = PromptTemplate(
        template=act_template,
        input_variables=["question"]
    )

    chain = (
            RunnablePassthrough.assign(
                question=lambda x: x["question"]
            )
            | prompt
            | llm
    )
    return chain
def mi_main(chain, chain_contrast):
    current_score = 5  # 初始化亲密度
    while True:
        s = input("请输入问题（输入 exit 或 退出 结束程序）：")
        if s.strip().lower() in ["exit", "退出"]:
            break

        # 获取RAG结果
        try:
            t = main(s)
            print("外部知识库加载完成")
            tr = inMain(s)
            print("内部知识库加载完成")
        except Exception as e:
            print(f"喵~获取知识时遇到问题啦（＞人＜；）: {str(e)}")
            t, tr = [], []

        print("现在开始加载模型嵌入数据库")
        data_path = "./all_text.txt"
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"喵呜~找不到 {data_path} 哦，快去检查一下文件位置和名字！")
        pdf_path = "./Oxford.pdf"

        # 加载Bm25的检索器
        bm25 = Bm25Retriever(data_path)
        ttt = bm25.GetBM25TopK(s, 2)
        # 取出文档内容并裁剪到500个字符以内
        ttt_contents = [doc.page_content[:500] for doc in ttt]
        print("嵌入检索器Bm25加载完成")

        # 加载M3eRetriever时，确保模型路径和参数正确
        retriever = M3eRetriever()
        #     # model_path="./MyRetriever/m3e_model",   # 本地模型路径
        #     vector_path="./vector_db/faiss_m3e_index"  # 本地向量库路径
        # )
        print("嵌入检索器M3e加载完成")
        # 执行查询
        results = retriever.GetTopK(s, 2)
        # 获取内容
        m3e_contents = [doc.page_content[:500] for doc, score in results]

        # 组合成向量
        temp_t = ('\n'.join(map(str, t[:2])))
        if len(temp_t) > 800:
            temp_t = temp_t[: 800]
        temp_tr = ('\n'.join(map(str, tr[:2])))
        if len(temp_tr) > 800:
            temp_tr = temp_tr[: 800]
        temp_ttt = ('\n'.join(map(str, ttt_contents[:2])))
        if len(temp_ttt) > 500:
            temp_ttt = temp_ttt[: 500]
        temp_m3e = ('\n'.join(map(str, m3e_contents[:2])))
        if len(temp_m3e) > 500:
            temp_m3e = temp_m3e[: 500]

        # 将他们拼接成一个完整输入提示
        temp_str = temp_t + temp_tr + temp_ttt + temp_m3e

        # 生成第一个回答
        result_contrast = chain_contrast.invoke({
            "question": s + "请用中文回答"
        })

        # 生成第二个回答
        result = chain.invoke({
            "search_information": temp_str,
            "question": s,
            "relationship_score": current_score
        })

        print(f'第一个回答是{result_contrast}')

        # # 更新亲密度（示例逻辑）
        # if "悄悄告诉你" in result:
        current_score = min(10, current_score + 1)

        print(f"第二个回答是：（亲密度：{current_score}/10）\n{result}")


if __name__ == "__main__":
    # 先检查Ollama服务是否运行
    try:
        import requests

        response = requests.get("http://localhost:11434")
        if response.status_code != 200:
            raise ConnectionError("Ollama服务未启动！")
    except Exception as e:
        print(f"错误：{str(e)}\n请先启动Ollama服务（命令行运行ollama serve）")
        exit()

    chain = initial()
    chain_contrast = initial_contrast()
    mi_main(chain, chain_contrast)





