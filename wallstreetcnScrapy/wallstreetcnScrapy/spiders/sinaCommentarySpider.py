# -*- coding: UTF-8 -*-   
'''
@author: Administrator
'''
from scrapy.spiders.crawl import CrawlSpider, Rule
from scrapy.utils.response import get_base_url
from wallstreetcnScrapy.items import CommentaryItem
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from bs4 import BeautifulSoup
# from scrapy import log


class sinaCommentarySpider(CrawlSpider):
    name = 'sinaCommentarySpider'
    allowed_domains = ['finance.sina.com.cn']
    start_urls = [
        'http://finance.sina.com.cn/',
    ]
    rules = [
        Rule(LxmlLinkExtractor(allow=("doc-\w+.shtml")),follow=True,callback='parse_commentary'),
    ]
    def parse_commentary(self, response):
        sel = response.selector
        item = CommentaryItem()
        #get uri
        item['uri'] = get_base_url(response)
        print 'Download from uri: %s' % item['uri']
#         log.msg('Download from uri: %s' % item['uri'])
        #get title
        _ = sel.xpath('//meta[@property="og:title"]/@content')
        item['title'] = '' if not _ else _[0].extract()
        #get time
        _ = sel.xpath('//meta[@property="article:published_time"]/@content')
        _time = '' if not _ else _[0].extract()
        if not _time:
            item['time'] = None
        else:
            _time = _time[:-6]+'Z'
            item['time'] = _time
        #get author
        _ = sel.xpath('//meta[@property="article:author"]/@content')
        item['author'] = '' if not _ else _[0].extract()
        #get description
        _ = sel.xpath('//meta[@name="description"]/@content')
        item['description'] = '' if not _ else _[0].extract()
        #get content & imgs & view
        _ = sel.xpath('//div[@class="article article_16"]')
        _ = _[0].extract()
        _content = BeautifulSoup(_)
        item['content'] = item['view'] = _content.text;
        _image_urls = []
        for img in _content.find_all('img'):
            if img.has_key('src') and img['src'].startswith('http'):
                _image_urls.append(img['src'])
            elif img.has_key('alt') and img['alt'].startswith('http'):
                _image_urls.append(img['alt'])
            else:
                continue
        item['image_urls'] = _image_urls
        #item['image_urls'] = [img.src if img.src is not None and img.src.startswith('http') else img.alt if img.alt is not None else None for img in _content.find_all('img')]
        return item
                
            
                
        
        
        