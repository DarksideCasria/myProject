
import json
import requests
from bs4 import BeautifulSoup
from sentence_transformers import CrossEncoder
import numpy as np  # 添加缺失的numpy导入

def search(query):
    # 保持原有搜索函数不变
    reconnect = 0
    while reconnect < 3:
        reconnect += 1
        try:
            url = "https://google.serper.dev/search"
            payload = json.dumps({
                "q": query,
                "num": 5
            })
            headers = {
                'X-API-KEY': "Google-Serper-API-Key",
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f'Error (attempt {reconnect}/3): {e}')
    return None

def page_loader(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('h1').text if soup.find('h1') else ''
        paragraphs = [p.text.strip() for p in soup.find_all('p') if p.text.strip() and len(p.text.strip()) > 10]

        return {
            'title': title,
            'paragraphs': paragraphs,
            'url': url
        }
    except Exception as e:
        print(f'Error loading {url}: {e}')
        return {'title': '', 'paragraphs': [], 'url': url}

def rank_results(model, web_results, query):
    # 收集所有唯一URL
    urls = set()
    for result in web_results.get('organic', []):
        urls.add(result['link'])
        if 'sitelinks' in result:
            for link in result['sitelinks']:
                urls.add(link['link'])

    # # 加载页面内容
    # # pages是处理的所有文章加所有段落
    # pages = [page_loader(url) for url in urls]
    # 加载页面内容，并对 URL 去重（去除锚点 #xxx）
    seen_urls = set()
    pages = []

    for url in urls:
        normalized_url = url.split('#')[0]
        if normalized_url in seen_urls:
            continue
        seen_urls.add(normalized_url)
        pages.append(page_loader(url))

    existing=set()
    scored_pages = []
    for page in pages:
        if not page['paragraphs']:
            continue  # 跳过没有内容的页面

        try:
            # 生成分数数组（形状为 [n_paragraphs]）
            # para是每一段
            score_pairs = [(query, para) for para in page['paragraphs']]

            # CrossEncoder返回的是二维数组 [[score1], [score2], ...]
            scores = model.predict(score_pairs)

            # 正确提取最大值（处理二维数组）
            if scores.size > 0:
                max_score = float(np.max(scores))
                best_idx = int(np.argmax(scores))  # 直接使用展平后的索引
            else:
                max_score = 0.0
                best_idx = 0

            temp=''
            if page['paragraphs'] and best_idx < len(page['paragraphs']):
                candidate = page['paragraphs'][best_idx][:500].strip().lower()
                if candidate not in existing:
                    temp=candidate
                    existing.add(temp)

            scored_pages.append({
                'title': page['title'],
                'url': page['url'],
                'score': max_score,
                'best_paragraph': temp
            })
        except Exception as e:
            print(f"Error processing {page['url']}: {e}")
            continue

    # 按分数降序排序并返回前5
    return sorted(scored_pages, key=lambda x: x['score'], reverse=True)[:5]

def main(query):
    # 初始化CrossEncoder模型
    #ranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2', max_length=512, device='cpu')
    ranker = CrossEncoder(
        'cross-encoder/ms-marco-MiniLM-L-6-v2',
        max_length=512,
        device='cpu'  # 自动选择设备
    )
    # query = "What is deep learning?"
    search_results = search(query)

    temp_list = []
    if search_results:
        ranked = rank_results(ranker, search_results, query)
        for i, result in enumerate(ranked):
            if result['score'] > 5:
                temp_list.append(result['best_paragraph'][:200])
            print(f"{i + 1}. Score: {result['score']:.4f}")
            print(f"Title: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Relevant Paragraph: {result['best_paragraph'][:200]}...\n")
    else:
        print("Failed to get search results")
    if not temp_list:
        print("搜索出的所有结果都不好")
    return temp_list
if __name__ == '__main__':
    query='What is love?'
    t=main(query)

