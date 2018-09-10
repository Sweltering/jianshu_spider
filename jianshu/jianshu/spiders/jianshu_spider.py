# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from jianshu.items import ArticleItem


class JianshuSpiderSpider(CrawlSpider):
    name = 'jianshu_spider'
    allowed_domains = ['jianshu.com']
    start_urls = ['https://www.jianshu.com/']

    rules = (
        Rule(LinkExtractor(allow=r'.*/p/[0-9a-z]{12}.*'), callback='parse_detail', follow=True),
    )

    def parse_detail(self, response):
        title = response.xpath("//h1[@class='title']/text()").get()  # 标题
        avatar = response.xpath("//a[@class='avatar']/img/@src").get()  # 头像url
        author = response.xpath("//span[@class='name']/a/text()").get()  # 作者
        pub_time = response.xpath("//span[@class='publish-time']/text()").get()  # 发布时间
        origin_url = response.url  # 获取文章的url，然后解析这个url来获取文章的id
        url1 = origin_url.split("?")[0]  # 根据问号分割
        article_id = url1.split("/")[-1]  # 这就是文章的id
        content = response.xpath("//div[@class='show-content']").get()  # 文章（保留标签格式）

        # 一下是ajax数据
        word_count = response.xpath("//span[@class='wordage']/text()").get()  # 字数
        comment_count = response.xpath("//span[@class='comments-count']/text()").get()  # 评论数
        like_count = response.xpath("//span[@class='views-count']/text()").get()  # 喜欢数
        read_count = response.xpath("//span[@class='likes-count']/text()").get()  # 阅读数
        subjects = response.xpath("//div[@class='include-collection']/a/div/text()").getall()  # 专题信息，返回的是列表
        subjects = ",".join(subjects)

        item = ArticleItem(
            title=title,
            avatar=avatar,
            author=author,
            pub_time=pub_time,
            origin_url=origin_url,
            article_id=article_id,
            content=content,
            subjects=subjects,
            word_count=word_count,
            comment_count=comment_count,
            read_count=read_count,
            like_count=like_count
        )
        yield item

