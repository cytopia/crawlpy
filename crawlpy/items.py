# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

"""
Need Field and Item
"""
#import scrapy
from scrapy.item import Item, Field

class CrawlpyItem(Item): # pylint: disable=too-many-ancestors
    """
    Data Model Class
    """
    # define the fields for your item here like:
    url = Field()
    text = Field()
    depth = Field()
    referer = Field()
