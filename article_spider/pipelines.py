# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# 导入打开文件的包，比open好，可以避免很多编码问题
import codecs
import json

from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter


class ArticleSpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonEncodingPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        self.file = codecs.open("article.json", "w", encoding='utf-8')

    def process_item(self, item, spider):
        # 调用pipeline生成的函数,ensure_ascii=False防止中文等编码错误
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        '''
        调用spider_closed(信号)关闭文件 
        '''
        self.file.close()


class ArticleImagePipeline(ImagesPipeline):
    '''
    定制图片的pipepline
    '''

    def item_completed(self, results, item, info):
        #只处理有front_image_path的
        if "front_image_url" in item:
            for ok, value in results:
                image_path = value['path']
            item['front_image_path'] = image_path
        return item


class JsonExporterPipeline(object):
    # 调用scrapy提供的exporter导出json文件
    def __init__(self):
        self.file = open("articlexporter.json", "wb")
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlPipeline(object):
    # 数据导入数据库,自定制，有可能会阻塞
    def __init__(self):
        self.conn = MySQLdb.connect("localhost", "root", "112358", "bole_articles", charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        inser_sql = """
        insert into articles(title,url,url_object_id,font_img_url,font_img_path,create_time,fa_num,sc_num,pinglun_num,tag,content)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        self.cursor.execute(inser_sql, (item["title"], item["url"], item["url_object_id"],
                                        item["front_image_url"], item["front_image_path"], item["create_date"],
                                        item["praise_nums"], item["fav_nums"], item["comment_nums"], item["tags"],
                                        item["content"]))
        self.conn.commit()


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    # 导入setting中的配置（固定函数）
    @classmethod
    def from_settings(cls, setting):
        # 将dbtool传入
        dbparms = dict(
            host=setting["MYSQL_HOST"],
            db=setting["MYSQL_DBNAME"],
            user=setting["MYSQL_USER"],
            password=setting["MYSQL_PASSWORD"],
            charset="utf8",
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        # twisted异步容器，使用MySQldb模块连接
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用Twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error,item,spider)

    def handle_error(self, failure, item, spider):
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        inser_sql = """
               insert into articles(title,url,url_object_id,font_img_url,font_img_path,create_time,fa_num,sc_num,pinglun_num,tag,content)
               VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
               """
        cursor.execute(inser_sql, (item["title"], item["url"], item["url_object_id"],
                                   item["front_image_url"], item["front_image_path"], item["create_date"],
                                   item["praise_nums"], item["fav_nums"], item["comment_nums"], item["tags"],
                                   item["content"]))
