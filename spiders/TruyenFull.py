# -*- coding: utf-8 -*-
# @Author: anh-tuan.vu
# @Date:   2021-02-04 20:18:19
# @Last Modified by:   anh-tuan.vu
# @Last Modified time: 2021-02-04 23:38:09

import scrapy
from scrapy.spiders import CrawlSpider
from configs import truyenfull as config
from tlib import TLib


class TruyenFull(CrawlSpider):
    name = "TruyenFull"

    def __init__(self, url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url

        tlib = TLib()
        logger = tlib.setLogger("url2epub")
        logger.propagate = True
        self.ulogger = logger
        self.tlib = tlib

    def start_requests(self):
        logger = self.ulogger
        logger.info("[%s] crawl url: %s" % (logger.name, self.url))
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        logger = self.ulogger
        metadata = self.getMetadata(response)
        logger.info("[%s] metadata: %s" % (logger.name, metadata))

    def getMetadata(self, response) -> dict:
        """Get metadata of a story

        Args:
            response (TYPE): scrapy http response

        Returns:
            dict: metadata obtained
        """
        # get raw metadata
        raw_title = ''.join(response.css(config.selectors['title']).getall())
        raw_author = ' & '.join(response.css(config.selectors['author'])
                                .getall())
        raw_desc = ''.join(response.css(config.selectors['desc']).getall())
        raw_source = ''.join(response.css(config.selectors['source'])
                             .getall())
        # clean description
        tlib = self.tlib
        desc = tlib.cleanTags(raw_desc)
        desc = tlib.br2p(desc)

        return {
            'title': raw_title.strip(),
            'author': raw_author.strip(),
            'desc': desc,
            'source': raw_source.strip()
        }
