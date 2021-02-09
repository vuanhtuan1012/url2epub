# -*- coding: utf-8 -*-
# @Author: anh-tuan.vu
# @Date:   2021-02-08 05:34:08
# @Last Modified by:   anh-tuan.vu
# @Last Modified time: 2021-02-09 14:24:52

import scrapy
from scrapy.spiders import CrawlSpider
from configs import vnthuquan as config
from TLib import TLib
import re
from time import time
import os
from bs4 import BeautifulSoup


class VnThuQuan(CrawlSpider):
    name = "VnThuQuan"
    allowed_domains = ["vnthuquan.net"]

    def __init__(self, url: str, *args, **kwargs):
        """Summary

        Args:
            url (str): url of story
            *args: Description
            **kwargs: Description
        """
        # get epub config
        if "epub_conf" in kwargs:
            conf = kwargs.pop("epub_conf")
            epub_conf = {k: v.strip() for k, v in conf.items() if v.strip()}
        else:
            epub_conf = {"language": "vi"}
        # get crawl config
        if "crawl_conf" in kwargs:
            crawl_conf = kwargs.pop("crawl_conf")
        else:
            crawl_conf = {"clean_dir": True}
        crawl_conf["clean_dir"] = crawl_conf.get("clean_dir", True)
        # get logging
        if "disabled_log" in kwargs:
            disabled_log = kwargs.pop("disabled_log")
        else:
            disabled_log = False
        # get debug
        if "debug" in kwargs:
            debug = kwargs.pop("debug")
        else:
            debug = False
        # get output_dir
        tlib = TLib()
        output_dir = None
        if "output_dir" in kwargs:
            output_dir = kwargs.pop("output_dir")
        if not output_dir:
            output_dir = "url2epub"
            tlib.mkdir(output_dir)

        super().__init__(*args, **kwargs)
        self.tlib = tlib
        self.epub_conf = epub_conf
        self.crawl_conf = crawl_conf
        self.debug = debug
        self.url = url
        self.output_dir = output_dir
        self.start = time()

        logger = tlib.setLogger("url2epub")
        logger.disabled = disabled_log
        self.ulogger = logger
        self.form_data = None

    def start_requests(self):
        """Verify url before parsing

        Yields:
            TYPE: Description
        """
        logger = self.ulogger
        tlib = self.tlib
        logger.info("[%s] Crawl url: %s" % (logger.name, self.url))
        logger.info("[%s] -- clean dir: %s" %
                    (logger.name, self.crawl_conf["clean_dir"]))

        # clean output directory
        error, msg = tlib.cleanDir(self.output_dir,
                                   self.crawl_conf["clean_dir"])
        if error:
            msg = "[ERROR]: %s" % msg
            logger.error("[%s] %s" % (logger.name, msg))
            if logger.disabled:
                print(msg)
            return

        # verify input url
        error, msg = tlib.isValidUrl(self.url, self.allowed_domains)
        if error:
            msg = "[ERROR]: %s" % msg
            logger.error("[%s] %s" % (logger.name, msg))
            if logger.disabled:
                print(msg)
            return

        # put stylesheet file to output directory
        tlib.putStyle2Dir(self.output_dir)
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        """Parse input url

        Args:
            response (TYPE): scrapy http response
        """
        logger = self.ulogger
        tlib = self.tlib

        # set start, end chapter to crawl
        chapters_func_calls = response.css(
            config.SELECTORS["function_calls"]).getall()
        conf = self.crawl_conf
        if not conf.get("start_chapter"):
            conf["start_chapter"] = 1
        conf["total_chapters"] = len(chapters_func_calls)
        conf["end_chapter"] = len(chapters_func_calls) \
            if not conf.get("end_chapter") else conf["end_chapter"]
        conf["current_chapter"] = conf["start_chapter"]
        self.crawl_conf = conf

        # verification
        if conf["start_chapter"] > conf["end_chapter"]:
            msg = "[ERROR] start chapter is greater than end chapter"
            logger.error("[%s] %s" % (logger.name, msg))
            if logger.disabled:
                print(msg)
            return

        form_data = self.functionCall2Kwargs(
            chapters_func_calls[conf["current_chapter"]-1])
        # form_data = {"tuaid": "13009", "chuongid": "1"}
        self.form_data = form_data
        yield self.fetchRequest(form_data)

    def functionCall2Kwargs(self, func_call: str) -> dict:
        """Get keyword arguments from a function call

        Args:
            func_call (str): vnthuquan function call

        Returns:
            dict: keyword arguments
        """
        kwargs = dict()
        kwargs_text = re.search(config.PATTERNS["function_call"],
                                func_call).group(1)
        for kwarg in kwargs_text.split("&"):
            kw, arg = kwarg.split("=")
            kwargs[kw] = arg
        return kwargs

    def fetchRequest(self, form_data: dict) -> scrapy.FormRequest:
        """fetch a request to crawl chapter

        Args:
            form_data (dict): chapter data to fetch

        Returns:
            scrapy.FormRequest: Description
        """
        return scrapy.FormRequest(
            url=config.CONTENT_URL,
            dont_filter=True,
            formdata=form_data,
            callback=self.parseChapter
        )

    def parseChapter(self, response):
        """Parse a chapter

        Args:
            response (TYPE): scrapy http response

        Returns:
            TYPE: Description
        """
        tlib = self.tlib
        logger = self.ulogger
        conf = self.crawl_conf
        data = response.text.split(config.SPLITTER)
        raw_metadata, raw_content = data[1:3]

        # set epub metadata
        metadata = self.getMetadata(raw_metadata)
        chapter_info = metadata["chapter_info"]
        title = chapter_info[0] if len(chapter_info) == 1 else chapter_info[1]
        if len(chapter_info) > 2:
            title = "%s: %s" % (title, " ".join(map(
                str.title, chapter_info[2:])))
        if conf["current_chapter"] == conf["start_chapter"]:
            epub_conf = self.epub_conf
            epub_conf["title"] = epub_conf.get(
                "title", metadata["title"].title())
            epub_conf["author"] = epub_conf.get(
                "author", metadata["author"].title())
            epub_conf["language"] = epub_conf.get("language", "vi")
            epub_conf["publisher"] = epub_conf.get("publisher", "TLab")
            epub_conf["source"] = epub_conf.get("source", "vnthuquan.net")
            self.epub_conf = epub_conf
            tlib.metadata2json(self.epub_conf, self.output_dir)
            # show logs
            logger.info("[%s] Getting story: %s" %
                        (logger.name, epub_conf["title"]))
            logger.info("[%s] -- author: %s" %
                        (logger.name, epub_conf["author"]))
            logger.info("[%s] -- total chapters: %s" %
                        (logger.name, conf["total_chapters"]))
            if conf["start_chapter"] != 1:
                logger.info("[%s] -- start chapter: %s" %
                            (logger.name, conf["start_chapter"]))
            if conf["end_chapter"] != conf["total_chapters"]:
                logger.info("[%s] -- end chapter: %s" %
                            (logger.name, conf["end_chapter"]))

        # get content
        content = self.cleanContent(raw_content)
        content = tlib.addDropCap(content, removal_symbols=config.REMOVAL_SYMBOLS)

        # create a html file
        html_conf = {
            "total_chapters": conf["total_chapters"],
            "current_chapter": conf["current_chapter"],
            "output_dir": self.output_dir,
            "language": self.epub_conf["language"]
        }
        tlib.genHtmlFile(title, content, html_conf)
        logger.info("[%s] crawled chapter %s/%s: %s" %
                    (logger.name, conf["current_chapter"],
                     conf["end_chapter"], title))
        if logger.disabled and not self.debug:
            tlib.printProgressBar(conf["current_chapter"],
                                  conf["end_chapter"],
                                  prefix="Crawling progress:")

        # crawl next chapter
        if conf["current_chapter"] < conf["end_chapter"]:
            conf["current_chapter"] += 1
            self.form_data["chuongid"] = str(conf["current_chapter"])
            self.crawl_conf = conf
            yield self.fetchRequest(self.form_data)
        else:
            # generate epub file
            error, epub_file = tlib.genEpubFile(self.output_dir)
            if error:
                msg = "[ERROR] %s" % epub_file
                logger.error("[%s] %s" % (logger.name, msg))
                if logger.disabled:
                    print(msg)
                return

            tlib.cleanDir(self.output_dir, conf["clean_dir"])
            end = time()
            logger.info("[%s] Crawling duration: %s" %
                        (logger.name, tlib.readSeconds(end - self.start)))
            msg = "The story %s is saved at %s" % \
                  (self.epub_conf["title"], epub_file)
            logger.info("[%s] %s" % (logger.name, msg))
            if logger.disabled:
                print(msg)

    def getMetadata(self, raw_metadata: str) -> dict:
        """get clean metadata of chapter

        Args:
            raw_metadata (str): raw metadata

        Returns:
            dict: Description
        """
        tlib = self.tlib
        clean_data = tlib.removeTags(raw_metadata)
        metadata = [x.strip() for x in clean_data.split('\r\n') if x.strip()]
        return {"title": metadata[0],
                "author": metadata[1],
                "chapter_info": metadata[2:]}

    def cleanContent(self, raw_content: str) -> str:
        """clean chapter content

        Args:
            raw_content (str): raw content

        Returns:
            str: clean content
        """
        tlib = self.tlib
        content = tlib.cleanTags(raw_content)
        soup = BeautifulSoup(content, features="lxml")
        soup.html.unwrap()
        soup.body.unwrap()
        # remove empty tags
        for tag in soup.find_all():
            if len(tag.get_text(strip=True)) == 0:
                tag.extract()
        content = soup.prettify().strip()
        content = tlib.br2p(content)
        return content
