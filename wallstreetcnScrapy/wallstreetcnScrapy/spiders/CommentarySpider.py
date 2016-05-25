'''
@author: Administrator
'''
#coding=utf-8
from scrapy.spiders.crawl import CrawlSpider, Rule
from scrapy.utils.response import get_base_url
from wallstreetcnScrapy.items import CommentaryItem
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from bs4 import BeautifulSoup
import re
# from scrapy import log


class CommentarySpider(CrawlSpider):
    name = 'CommentarySpider'
    allowed_domains = ['wallstreetcn.com']
    start_urls = [
        'http://wallstreetcn.com/news?status=published&type=news&order=-created_at&limit=30&page=1',
    ]
    rules = [
        Rule(LxmlLinkExtractor(allow=("page=\d+",))),
        Rule(LxmlLinkExtractor(allow=("node/\d+")),follow=True,callback='parse_commentary'),
    ]
    def parse_commentary(self, response):
        sel = response.selector
        item = CommentaryItem()
        #get uri
        item['uri'] = get_base_url(response)
        print 'Download from uri: %s' % item['uri']
#         log.msg('Download from uri: %s' % item['uri'])
        #get title
        _ = sel.xpath('//h1[@class="article-title"]/text()')
        item['title'] = '' if not _ else _[0].extract()
        #get time
        _ = sel.xpath('//span[@class="item time"]/text()')
        _time = '' if not _ else _[0].extract()
        if not _time:
            item['time'] = None
        else:
            _time = re.sub('[^\u4E00-\u9FA5\s]', '-',_time)
            _time = _time[:10]+'T'+_time[12:]+'Z'
            item['time'] = _time
        #get author
        _ = sel.xpath('//span[@class="item author"]/a/text()')
        item['author'] = '' if not _ else _[0].extract()
        #get description
        _ = sel.xpath('//meta[@name="description"]/@content')
        item['description'] = '' if not _ else _[0].extract()[:-84]
        #get content & imgs & view
        _ = sel.xpath('//div[@class="article-content"]')
        _ = _.extract()[0]
        _view = _[:-123]+'</div>' if len(_) > 200 else _
        _content = BeautifulSoup(_view)
        item['content'] = _content.text
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
        item['view'] = _view
        return item
                
            
                
        
        
        