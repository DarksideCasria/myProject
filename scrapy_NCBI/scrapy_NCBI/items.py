# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html


import scrapy

class ScrapyNcbiItem(scrapy.Item):
    name = scrapy.Field()
    officialName = scrapy.Field()
    src = scrapy.Field()
    index = scrapy.Field()

    # # define the fields for your item here like:
    # # name = scrapy.Field()
    # name = scrapy.Field()
    # src = scrapy.Field()
    # #query=scrapy.Field()
    # #found = scrapy.Field()
