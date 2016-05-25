# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import solr
from scrapy.utils.project import get_project_settings
from twisted.enterprise import adbapi
from hashlib import md5
from scrapy import log
import os
import requests
import re
from scrapy.exceptions import DropItem

settings = get_project_settings()

class RequiredFieldsPipeline(object):

    required_fields = ('title', 'uri', 'author')

    def process_item(self, item, spider):
        for field in self.required_fields:
            
            if not item[field]:
#                 log.msg("Field '%s' missing" % (field))
                print "Field '%s' missing" % (field)
                raise DropItem("Field '%s' missing: %r" % (field, item))
        return item

class IdGeneratePipeline(object):
    
    def process_item(self, item, spider):
        item['id'] = self._get_linkmd5id(item)
        return item
    
    def _get_linkmd5id(self, item):
        return md5((item['uri'] + item['title'] + item['author']).encode("utf8")).hexdigest()


class ImageDownloadPipeline(object):
    def process_item(self, item, spider):
        if 'image_urls' in item:
            images = []
            abpath = '%s/%s/%s/%s' % (spider.name, item['id'][0],item['id'][1],item['id'])
            dir_path = '%s/%s' % (settings['IMAGES_STORE'], abpath)
            if not os.path.exists(dir_path) and len(item['image_urls'])>0:
                os.makedirs(dir_path)
            for image_url in item['image_urls']:
                name = image_url.split('/')[-1]
                _i = name.rfind('!')
                if _i > 4:
                    name = name[:_i]
                name = re.sub('\\\|/|:|\*|\?|"|<|>','_',name)
                image_file_name = name[-100:]
                file_path = '%s/%s' % (dir_path, image_file_name)
                images.append((image_url, file_path))
                if os.path.exists(file_path):
                    continue
                with open(file_path, 'wb') as handle:
                    try:
                        response = requests.get(image_url, stream=True)
                        for block in response.iter_content(1024):
                            if not block:
                                break
                            handle.write(block)
    #                     log.msg("download img to %s" % file_path)
                    except:
                        continue
            item['images'] = images
            if not images:
                pass
            else:
                _ = images[0][1]
                item['firstimage'] = '%s/%s' % (abpath, _[_.rfind('/')+1:])
                print item['firstimage']
        return item

class SolrPipeline(object):
    
    def __init__(self):
        self.mapping = settings['SOLR_MAPPING'].items()
        self.solr = solr.Solr(settings['SOLR_URL'])
        
    def process_item(self, item, spider):
        solr_item = {}
        for dst, src in self.mapping:
            if type(src) is str:
                solr_item[dst] = item[src] if src in item else None
            elif type(src) is list:
                #########
                solr_item[dst] = [item[i] if i in item else None for i in src]
            else:
                assert False
        self.solr.add(solr_item)
        return item

class MysqlPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool
    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            port=settings['MYSQL_PORT'],
            charset='utf8',
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        d = self.dbpool.runInteraction(self._do_upinsert, item, spider)    
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return d


    def _parseItem(self, item):
        id1 = str(item['id'].encode('utf8'))
        uri = str(item['uri'].encode('utf8'))
        title = str(item['title'].encode('utf8'))
        author = str(item['author'].encode('utf8'))
        time = str(item['time'].encode('utf8').replace('T', ' ')[:-1])
        description = str(item['description'].encode('utf8'))
        content = str(item['content'].encode('utf8'))
        images = str(item['images'])
        view = str(item['view'].encode('utf8'))
        return uri, title, author, time, description, content, images, view, id1

    def _do_upinsert(self, conn, item, spider):
        conn.execute("""SELECT EXISTS(
            SELECT 1 FROM wstable WHERE id = %s
        )""", (item['id'],))
        ret = conn.fetchone()[0]
        uri, title, author, time, description, content, images, view, id1 = self._parseItem(item)
        if ret:
            conn.execute("""
                update wstable set uri = %s, title = %s, author = %s, time1 = %s, description = %s, content = %s, images = %s, view1 = %s where id = %s    
            """, (uri,title,author,time,description,content,images,view,id1))
#             log.msg("""
#                 update wstable set uri = %s, title = %s, author = %s, time1 = %s, description = %s, content = %s, images = %s, view1 = %s where id = %s    
#                 """ % (uri,title,author,time,description,content,images,view,id1))
        else:
#             log.msg("""
#             insert into wstable(id, uri, title, author, time1, description, content, images, view1) 
#             values(%s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """ % (id1,uri,title,author,time,description,content,images,view))
            conn.execute("""
            insert into wstable(id, uri, title, author, time1, description, content, images, view1) 
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (id1,uri,title,author,time,description,content,images,view))
#             log.msg('finished item %s' % item['id'])
            print 'finished item %s' % item['id']
            
    def _handle_error(self, failue, item, spider):
        log.err(failue)
        