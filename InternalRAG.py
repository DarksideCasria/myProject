

import requests
from bs4 import BeautifulSoup
from openai import OpenAI


def extract_english_keywords(query):
    client = OpenAI(
        api_key="DEEPSEEK-API-KEY",
        base_url="https://api.deepseek.com"
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": """You are an adaptive keyword extraction engine.
                Extract technical terms and key entities from English text following these rules:
                1. Primary extraction: Strict noun/proper noun terms in original form
                2. When output <3 terms:
                   a. Analyze compound terms (e.g., "machine learning" → "machine learning, machine, learning")
                   b. Include semantically related base terms
                3. Output format:
                   - Strict comma-separation
                   - No duplicates
                   - Preserve original term priority
                4. Never add non-text terms
                5. Example behavior:
                   Input: "true love relationship"  
                   Output: "true love, relationship, love, true, emotional connection"""},
            {"role": "user", "content": query}
        ],
        temperature=0.2,  # 更低的随机性保证稳定性
        max_tokens=100,
        top_p=0.9
    )

    # 处理返回结果
    raw_output = response.choices[0].message.content.strip()

    # 清理和分割关键词
    keywords = []
    for kw in raw_output.split(','):
        cleaned_kw = kw.strip().rstrip('.')  # 去除末尾标点
        if cleaned_kw and len(cleaned_kw.split()) <= 3:  # 过滤长句子
            keywords.append(cleaned_kw)

    return keywords[:5]  # 返回最多5个最相关的关键词

url = "https://en.wikipedia.org/w/api.php"




def get_html(url,key_word):
    print(f'这里的关键词是{key_word}\n\n\n')
    result_info=[]
    for i in range(len(key_word)):
        # params = {
        #     "action": "query",
        #     "format": "json",
        #     "titles": f"{key_word[i]}",
        #     "prop": "extracts",
        #     "exintro": "True"  # 修改1：布尔值应使用小写字符串形式
        # }
        params = {
            "action": "query",
            "format": "json",
            "titles": f"{key_word[i]}",
            "prop": "extracts",
            "explaintext": False,  # 或直接删除
            # 去掉 "exintro"，让它返回全文
        }

        try:
            # 修改2：添加timeout参数和错误处理
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # 检查HTTP状态码

            data = response.json()
            page = next(iter(data["query"]["pages"].values()))
            print(f"这里的相关内容是关键点{page['extract']}\n\n\n")

            # 修改3：添加内容存在性检查
            if "extract" not in page:
                print("未找到相关内容")
                exit()

            html_content = page["extract"]
            soup = BeautifulSoup(html_content, "html.parser")
            plain_text = soup.get_text()
            result_info.append(plain_text)

        except requests.exceptions.RequestException as e:
            print(f"网络请求失败，请检查网络连接: {e}")
        except KeyError:
            print("API返回数据结构异常")
        except Exception as e:
            print(f"发生未知错误: {e}")
    return result_info

def inMain(query):
    l=extract_english_keywords(query)
    info=get_html(url,l)
    if not info or all(not item.strip() for item in info):
        print("Internal知识库没有相关信息")
    else:
        print(info)
    return info
if __name__ == '__main__':
    query="What is the true love?"
    info=inMain(query)
    print('这里是最终的结果================================================================')
    print(info)
    # query="What is love?"
    # l=extract_english_keywords(query)
    # info=get_html(url,l)
    # print(info)