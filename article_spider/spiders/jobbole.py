# -*- coding: utf-8 -*-
import scrapy
import re
import datetime

from scrapy.http import Request
#提取域名的函数
#python3
from urllib import parse
#python2
#import urlparse
from scrapy.loader import ItemLoader

from article_spider.items import JobboleArticleSpider,ArticleItemLoader
from article_spider.utils.common import get_md5

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        '''
        1.获取文章列表页中的文章url并交给scrapy下载后进行解析；
        2.获取下一页url并交给scrapy下载交给parse解析字段  
        '''
        #解析列表页中所有文章url交给scrapy下载后进行解析
        #获取url及image的节点
        post_nodes=response.css("div#archive div.floated-thumb div.post-thumb a")
        for post_node in post_nodes:
            image_url=post_node.css("img::attr(src)").extract_first("")
            post_url=post_node.css("::attr(href)").extract_first("")
            #若提取的url不全，不包含域名,可以用parse拼接
            #Request(url=parse.urljoin(response.url,post_url),callback=self.parse_detail)
            #生成器,回调
            yield Request(url=parse.urljoin(response.url,post_url),meta={"front-image-url":image_url},callback=self.parse_detail)
        #提取下一页并交给scrapy下载
        next_url=response.css(".next.page-numbers::attr(href)").extract_first()
        if next_url:
            yield Request(next_url,callback=self.parse)

    def parse_detail(self,response):
        #实例化item中JobboleArtilce对象
        # article_item=JobboleArticleSpider()
        # 通过xpath提取
        # front_image_url=response.meta.get("front-image-url","")#文章封面图
        # title=response.xpath('//div[@class="entry-header"]/h1/text()').extract_first()
        # create_date= response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].replace("·","").strip()
        # praise_nums=response.xpath("//span[contains(@class,'vote-post-up')]/h10/text()").extract()[0]
        # if praise_nums:
        #     praise_nums=int(praise_nums)
        # else:
        #     praise_nums=0
        # fav_nums=response.xpath("//span[contains(@class,'bookmark-btn')]/text()").extract()[0]
        # match_fav=re.match(".*(\d+).*",fav_nums)
        # if match_fav:
        #     fav_nums=int(match_fav.group(1))
        # else:
        #     fav_nums=0
        # comments_nums = response.xpath("//a[@href='#article-comment']/span/text()").extract()[0]
        # math_comments=re.match(".*(\d).*",comments_nums)
        # if math_comments:
        #     comments_nums=int(math_comments.group(1))
        # else:
        #     comments_nums=0
        # content=response.xpath('//div[@class="entry"]').extract()[0]
        # tag_list= response.xpath('//div[@class="entry-meta"]/p/a/text()').extract()
        # tag_list=[element for element in tag_list if not element.strip().endswith("评论")]
        # tags=','.join(tag_list)
        #
        # #填充item数据
        # article_item["title"]=title
        # article_item["url"]=response.url
        # try:
        #     create_date=datetime.datetime.strptime(create_date,"%Y/%m/%d").date()
        # except Exception as e:
        #     create_date=datetime.datetime.now().date()
        # article_item["create_date"]=create_date
        # article_item["front_image_url"]=[front_image_url]
        # article_item["url_object_id"]=get_md5(front_image_url)
        # article_item["praise_nums"]=praise_nums
        # article_item["fav_nums"]=fav_nums
        # article_item["comment_nums"]=comments_nums
        # article_item["tags"]=tags
        # article_item["content"]=content
        #传递到item中
        # yield article_item
        #通过CSS提取
        # title=response.css(".entry-header > h1::text").extract()[0]
        # create_time=response.css("p.entry-meta-hide-on-mobile::text").extract()[0].replace("·","").strip()
        # praise_nums=int(response.css("span.vote-post-up h10::text").extract()[0])
        # if praise_nums:
        #     praise_nums = int(praise_nums)
        # else:
        #     praise_nums = 0
        # fav_nums=response.css(".bookmark-btn::text").extract()[0]
        # match_fav = re.match(".*(\d+).*", fav_nums)
        # if match_fav:
        #     fav_nums = int(match_fav.group(1))
        # else:
        #     fav_nums = 0
        # comments_nums=response.css("a[href='#article-comment'] span::text").extract()[0]
        # math_comments = re.match(".*(\d).*", comments_nums)
        # if math_comments:
        #     comments_nums = int(math_comments.group(1))
        # else:
        #     comments_nums = 0
        # content=response.css("div.entry").extract()[0]
        # tag_list = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ','.join(tag_list)

        #通过item_loader加载item
        front_image_url=response.meta.get("front-image-url","")#文章封面图
        item_loader=ArticleItemLoader(item=JobboleArticleSpider(),response=response)
        #三个重要方法item_loader.add_xpath();item_loader.add_css();item_loader.add_css()
        item_loader.add_css("title",".entry-header > h1::text")
        item_loader.add_value("url",response.url)
        item_loader.add_value("url_object_id",get_md5(front_image_url))
        item_loader.add_css("create_date","p.entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_image_url",[front_image_url])
        item_loader.add_css("praise_nums","span.vote-post-up h10::text")
        item_loader.add_css("fav_nums",".bookmark-btn::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("content", "div.entry")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")

        article_item=item_loader.load_item()
        yield article_item

        