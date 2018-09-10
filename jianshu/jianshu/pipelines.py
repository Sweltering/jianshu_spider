# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from twisted.enterprise import adbapi
from pymysql import cursors

# 同步的方式保存数据
class JianshuPipeline(object):
    def __init__(self):
        dbparams = {
            'host': '192.168.161.129',
            'port': 3306,
            'user': 'wangjie',
            'password': 'wangjie',
            'database': 'jianshu',
            'charset': 'utf8'
        }
        self.conn = pymysql.connect(**dbparams)  # 连接数据库
        self.cursor = self.conn.cursor()  # 创建游标
        self._sql = None

    def process_item(self, item, spider):
        self.cursor.execute(self.sql, (item['title'], item['content'], item['author'], item['avatar'], item['pub_time'],
                                       item['origin_url'], item['article_id']))  # 执行SQL语句
        self.conn.commit()  # 提交
        return item

    # SQL语句
    @property
    def sql(self):
        if not self._sql:
            self._sql = """
            insert into article(id, title, content, author, avatar, pub_time, origin_url, article_id) 
            values(null, %s, %s, %s, %s, %s, %s, %s)
            """
            return self._sql
        return self._sql


# 异步的方式保存数据
class JianshuTwistedPipeline(object):
    def __init__(self):
        dbparams = {
            'host': '192.168.161.129',
            'port': 3306,
            'user': 'wangjie',
            'password': 'wangjie',
            'database': 'jianshu',
            'charset': 'utf8',
            'cursorclass': cursors.DictCursor
        }
        self.dbpool = adbapi.ConnectionPool('pymysql', **dbparams)  # 创建一个连接池
        self._sql = None

    @property
    def sql(self):
        if not self._sql:
            self._sql = """
                insert into article(id, title, content, author, avatar, pub_time, origin_url, article_id) 
                values(null, %s, %s, %s, %s, %s, %s, %s)
                """
            return self._sql
        return self._sql

    def process_item(self, item, spider):
        defer = self.dbpool.runInteraction(self.insert_item, item)
        defer.addErrback(self.handle_error, item, spider)

    # 将数据插入到数据库中
    def insert_item(self, cursor, item):
        cursor.execute(self.sql, (item['title'], item['content'], item['author'], item['avatar'], item['pub_time'],
                                       item['origin_url'], item['article_id']))

    # 错误处理函数
    def handle_error(self, error, item, spider):
        print("="*50+"error"+"="*50)
        print(error)
        print("="*50+"error"+"="*50)
