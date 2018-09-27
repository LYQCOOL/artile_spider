# _*_ encoding:utf-8 _*_
__author__ = 'LYQ'
__date__ = '2018/9/25 11:47'
from scrapy.cmdline import execute
import sys
import os
#将父目录添加到搜索目录中
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy","crawl","jobbole"])