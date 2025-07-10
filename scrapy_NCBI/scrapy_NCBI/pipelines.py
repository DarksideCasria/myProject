# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


# class ScrapyNcbiPipeline:
#     def open_spider(self,spider):
#         self.results = []
#         self.fp=open('answer_json','w',encoding='utf-8')
#     def process_item(self, item, spider):
#         self.results.append(item)
#         return item
#         # self.fp.write(str(item)+'\n')
#         # return item
#     def close_spider(self,spider):
#         # 根据 name（即原始查询）排序，并写入文件
#         print("=====================================================================")
#         self.results.sort(key=lambda x: x['name'])
#         print(self.results)
#         print("/n")
#         for item in self.results:
#             #if item['src']:
#             print('111111111111111111111111111111111111111111111111111111111111')
#             self.fp.write(str(item) + '\n')
#             #self.fp.write(f"{item['name']}:{item['src']}\n")
#             #else:
#                 #self.fp.write(f"{item['name']}: 未查找到\n")
#         self.fp.close()
#        # self.fp.close()
class ScrapyNcbiPipeline:
    def __init__(self):
        # 用来临时存储所有 item
        self.items = []

    def process_item(self, item, spider):
        # 将 item 添加到 items 列表中
        self.items.append(item)
        return item

    def close_spider(self, spider):
        # 按 `index` 排序 items
        sorted_items = sorted(self.items, key=lambda x: x['index'])

        # 将排序后的 items 保存到文件中
        with (open('output.txt', 'w', encoding='utf-8') as f):
            for item in sorted_items:
                # line = (
                #     f"Name: {item['name']:<20} "
                #     f"OfficialName: {item['officialName']:<20} "
                #     f"Src: {item['src']:<20}"
                # )
                # f.write(line)
                # #f.write('\n')
                # f.flush()  # 手动刷新缓冲区
                #f"Name: {item['name']:<20} OfficialName: {item['officialName']:<20} Src: {item['src']:<20}\n"
                line =f"Name: {item['name']}        OfficialName: {item['officialName']}     Src: {item['src']}\n"
                f.write(line)

        print("Items have been sorted and saved to output.txt")
