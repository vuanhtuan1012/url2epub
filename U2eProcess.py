# -*- coding: utf-8 -*-
# @Author: anh-tuan.vu
# @Date:   2021-02-04 22:09:14
# @Last Modified by:   anh-tuan.vu
# @Last Modified time: 2021-02-04 23:27:51

from scrapy.crawler import CrawlerProcess


class U2eProcess(CrawlerProcess):
    """docstring for U2eProcess"""
    def __init__(self, **kwargs):
        user_agent = kwargs.get("user_agent", None)
        if user_agent is None:
            # latest Chrome browser on Windows
            user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/88.0.4324.146 Safari/537.36")
        settings = {
            "USER_AGENT": user_agent,
            "LOG_ENABLED": False,
        }
        super().__init__(settings)
