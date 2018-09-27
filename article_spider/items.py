# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import datetime
import re

import scrapy
# TakeFirst取第一个，Join连接
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader


class ArticleSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(value):
    # 定义处理时间函数，返回时间
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


class ArticleItemLoader(ItemLoader):
    # 自定义itemloader,值取数组的第一个，修改item中的loader
    default_output_processor = TakeFirst()


def get_nums(value):
    # 定义处理点赞数，收藏数，评论数处理等
    match_num = re.match(".*(\d+).*", value)
    if match_num:
        value = int(match_num.group(1))
    else:
        value = 0
    return value


def return_value(value):
    # 什么也不做
    return value


def remove_comment(value):
    # 去掉tag中提取的含评论的便签
    if "评论" in value:
        return ""
    else:
        return value


class JobboleArticleSpider(scrapy.Item):
    # 字段中有Field类型，可以接受任何类型
    title = scrapy.Field()
    create_date = scrapy.Field(
        # 处理时间,还是数组
        input_processor=MapCompose(date_convert),
        # 只取数组的第一个
        # output_processor=TakeFirst()
    )
    url = scrapy.Field()
    # 对url做MD5，固定url的长度
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        #覆盖取第一个，这里必须为列表
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        # 覆盖定制的取第一个
        output_processor=Join(",")
    )
    content = scrapy.Field()
