import scrapy
import os
from scrapy_NCBI.items import ScrapyNcbiItem

class PaNcbiSpider(scrapy.Spider):
    name = "Pa_NCBI"
    allowed_domains = ["www.ncbi.nlm.nih.gov"]

    file_path = os.path.join(os.path.dirname(__file__), "t.tsv")
    start_urls = []
    names = []

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            num = line.strip().split()
            if len(num) > 1:
                query = "".join(num[1:])
                start_urls.append(f"https://www.ncbi.nlm.nih.gov/gene/?term={query}")
                names.append(query)

    def start_requests(self):
        for index, (url, name) in enumerate(zip(self.start_urls, self.names)):
            yield scrapy.Request(url=url, callback=self.parse, meta={'name': name, 'index': index})

    def parse(self, response):
        name = response.meta['name']
        index = response.meta['index']
        officialName = response.xpath('//*[@id="summaryDl"]/dd[2]/text()').extract_first()
        a = response.xpath('(//td[@class="gene-name-id"]//a/@href)[1]').extract_first()
        t = response.xpath('//dt[text()="Summary"]/following-sibling::dd[1]/text()').extract_first()
        if t:
            return ScrapyNcbiItem(name=name,src=t,index=index,officialName=officialName)
        elif a:
            url = 'https://www.ncbi.nlm.nih.gov/' + a
            return scrapy.Request(url=url, callback=self.parse_second, meta={'name': name, 'index': index})
        else:
            return ScrapyNcbiItem(name=name, src=None, index=index, officialName=None)

    def parse_second(self, response):
        name = response.meta['name']
        index = response.meta['index']
        officialName = response.xpath('//*[@id="summaryDl"]/dd[2]/text()').extract_first()
        src = response.xpath('//dt[text()="Summary"]/following-sibling::dd[1]/text()').extract_first()
        return ScrapyNcbiItem(name=name, src=src, index=index,officialName=officialName)





#//*[@id="summaryDl"]/dd[2]/text()
# import scrapy
# import os
# from scrapy_NCBI.items import ScrapyNcbiItem
# class PaNcbiSpider(scrapy.Spider):
#     name = "Pa_NCBI"
#     allowed_domains = ["www.ncbi.nlm.nih.gov"]
#
#     # 通过读取文件构造 start_urls
#     file_path = os.path.join(os.path.dirname(__file__), "t.tsv")
#     start_urls = []
#     names=[]
#     # 打开文件并填充 start_urls
#     with open(file_path, "r", encoding="utf-8") as file:
#         for line in file:
#             num = line.strip().split()
#             if len(num) > 1:
#                 query = "".join(num[1:])
#                 start_urls.append(f"https://www.ncbi.nlm.nih.gov/gene/?term={query}")
#                 names.append(query)
#
#
#     def parse(self, response):
#         name=response.meta['name']
#         a=response.xpath('(//td[@class="gene-name-id"]//a/@href)[1]').extract_first()
#         #if a:
#         url = 'https://www.ncbi.nlm.nih.gov/' + a
#         if name==None:
#             print('cccccccccccccccccccccccccccccccccccccccccccccccccccccc')
#         yield scrapy.Request(url=url, callback=self.parse_second, meta={'name': name})
#         #else:
#             ## 处理没有找到结果的情况
#             #yield ScrapyNcbiItem(name=query, src=None)
#         #url='https://www.ncbi.nlm.nih.gov/'+a
#         #yield scrapy.Request(url=url,callback=self.parse_second)
#
#     def parse_second(self,response):
#         #warning = response.xpath('//li[@class="warn icon"]').get() is not None
#         name = response.meta['name']
#         #name = response.xpath('//dd[@class="noline"]/text()').extract_first()
#         src = response.xpath('//dt[text()="Summary"]/following-sibling::dd[1]').extract_first()
#         yield ScrapyNcbiItem(name=name,src=src)
        #yield search_answer



#//dd[@class="noline"]/text()
#//h1[@class="title"]
#//h1[@class="title"]



#https://www.ncbi.nlm.nih.gov/gene/?term=HMGCR+membrane+domain搜索第一个基因出现的网页
#(//td[@class='gene-name-id']//a/@href)[1]搜索网页出现的第一个基因
#//dt[text()='Summary']/following-sibling::dd[1]获取summary


#https://www.ncbi.nlm.nih.gov/gene/?term=nicotinamide+adenine+dinucleotide+phosphatase%3A+quinone-acceptor+1
#第二个，这里是没搜到的基因
#(//td[@class='gene-name-id']//a/@href)[1]搜索结果是NULL

#https://www.ncbi.nlm.nih.gov/gene/?term=coli+xanthine-guanine+phosphoribosyltransferase
#(//td[@class='gene-name-id']//a/@href)[1]搜索网页出现的第一个基因
#//dt[text()='Summary']/following-sibling::dd[1]搜索结果是summary

#https://www.ncbi.nlm.nih.gov/gene/?term=bis-diol+epoxides
#(//td[@class='gene-name-id']//a/@href)[1]搜索网页出现的第一个化合物
#//dt[text()='Summary']/following-sibling::dd[1]搜索结果是summary