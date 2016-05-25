# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field
import scrapy


class CommentaryItem(scrapy.Item):
    id = Field()
    uri = Field()
    firstimage = Field()
    title = Field()
    author = Field()
    time = Field()
    description = Field()
    content = Field()
    view = Field()
    image_urls = Field()
    images = Field()

