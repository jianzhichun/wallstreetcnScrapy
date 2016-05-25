'''
@author: Administrator
'''
import scrapy.cmdline
from scrapy.crawler import CrawlerProcess
from wallstreetcnScrapy.spiders import CommentarySpider, jqkaCommentarySpider,\
    sinaCommentarySpider
#,'-s','JOBDIR=crawls/CommentarySpider-1'
def main():
#     process = CrawlerProcess()
#     process.crawl(CommentarySpider.CommentarySpider,args=['-s','JOBDIR=crawls/CommentarySpider-1'])
#     process.crawl(jqkaCommentarySpider.jqkaCommentarySpider,args=['-s','JOBDIR=crawls/CommentarySpider-2'])
#     process.crawl(sinaCommentarySpider.sinaCommentarySpider,args=['-s','JOBDIR=crawls/CommentarySpider-3'])
#     process.start()
#     scrapy.cmdline.execute(argv=['scrapy', 'crawl', 'CommentarySpider','-s','JOBDIR=crawls/CommentarySpider-1'])
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', 'jqkaCommentarySpider','-s','JOBDIR=crawls/CommentarySpider-2'])
#     scrapy.cmdline.execute(argv=['scrapy', 'crawl', 'sinaCommentarySpider','-s','JOBDIR=crawls/CommentarySpider-3'])
if  __name__ =='__main__':
    main()