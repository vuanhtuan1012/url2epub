# -*- coding: utf-8 -*-
# @Author: anh-tuan.vu
# @Date:   2021-02-04 20:18:19
# @Last Modified by:   anh-tuan.vu
# @Last Modified time: 2021-02-05 17:05:43

import scrapy
from scrapy.spiders import CrawlSpider
from configs import truyenfull as config
from TLib import TLib
import re


class TruyenFull(CrawlSpider):
    name = "TruyenFull"
    allowed_domains = ["truyenfull.vn"]

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
            epub_conf = {k: v for k, v in conf.items() if v}
        else:
            epub_conf = {"language": "vi"}
        # get crawl config
        if "crawl_conf" in kwargs:
            crawl_conf = kwargs.pop("crawl_conf")
        else:
            crawl_conf = {"clean_dir": True}
        crawl_conf["clean_dir"] = crawl_conf.get("clean_dir", True)
        # get logging
        if "disabled_logging" in kwargs:
            disabled_logging = kwargs.pop("disabled_logging")
        else:
            disabled_logging = False
        # get output_dir
        tlib = TLib()
        if "output_dir" in kwargs:
            output_dir = kwargs.pop("output_dir")
        else:
            output_dir = "url2epub"
            tlib.mkdir(output_dir)

        super().__init__(*args, **kwargs)
        self.epub_conf = epub_conf
        self.crawl_conf = crawl_conf
        self.url = url
        self.output_dir = output_dir

        logger = tlib.setLogger("url2epub")
        logger.disabled = disabled_logging
        self.ulogger = logger
        self.tlib = tlib

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
        cleaned = tlib.cleanDir(self.output_dir,
                                self.crawl_conf["clean_dir"], logger)
        if not cleaned:
            return
        # put stylesheet file to output directory
        tlib.putStyle2Dir(self.output_dir)
        # verify input url
        if tlib.isValidUrl(self.url, self.allowed_domains):
            yield scrapy.Request(url=self.url, callback=self.parse)
        else:
            logger.info("[%s] INVALID URL. ALLOWED DOMAINS: %s" %
                        (logger.name, ",".join(self.allowed_domains)))

    def parse(self, response):
        """Parse input url

        Args:
            response (TYPE): scrapy http response
        """
        logger = self.ulogger

        # set metadata
        conf = self.epub_conf
        metadata = self.getMetadata(response)
        epub_conf = {
            "title": conf.get("title", metadata["title"]),
            "author": conf.get("author", metadata["author"]),
            "desc": conf.get("desc", metadata["desc"]),
            "source": conf.get("source", metadata["source"]),
            "language": conf.get("language", "vi"),
            "publisher": "TLab"
        }
        self.epub_conf = epub_conf
        logger.info("[%s] Getting story: %s" %
                    (logger.name, epub_conf["title"]))
        logger.info("[%s] -- author: %s" %
                    (logger.name, epub_conf["author"]))

        # set start, end chapter to crawl
        conf = self.crawl_conf
        if not conf.get("start_chapter", None):
            conf["start_chapter"] = 1
        if not conf.get("end_chapter", None):
            conf["end_chapter"] = -1
        # get total chapters
        chapter_urls = response.css(config.SELECTORS["chapter_urls"]).getall()
        conf["first_chapter_url"] = chapter_urls[0]
        conf["total_chapters"] = len(chapter_urls)
        self.crawl_conf = conf
        page_urls = response.css(config.SELECTORS["page_urls"]).getall()
        if page_urls:
            i = -1
            last_page_url = page_urls[i]
            while "javascript" in last_page_url:
                i -= 1
                last_page_url = page_urls[i]
        else:
            last_page_url = response.url
        yield scrapy.Request(last_page_url, callback=self.getTotalChapters)

    def getMetadata(self, response) -> dict:
        """Get metadata of a story

        Args:
            response (TYPE): scrapy http response

        Returns:
            dict: metadata obtained
        """
        # get raw metadata
        raw_title = "".join(response.css(config.SELECTORS["title"]).getall())
        raw_author = " & ".join(response.css(config.SELECTORS["author"])
                                .getall())
        raw_desc = "".join(response.css(config.SELECTORS["desc"]).getall())
        raw_source = "".join(response.css(config.SELECTORS["source"])
                             .getall())
        # clean description
        tlib = self.tlib
        desc = tlib.cleanTags(raw_desc)
        desc = tlib.br2p(desc)

        return {
            "title": raw_title.strip(),
            "author": raw_author.strip(),
            "desc": desc,
            "source": raw_source.strip()
        }

    def getPageNumber(self, url: str) -> int:
        """Get page number from url of list chapters

        Args:
            url (str): Description

        Returns:
            int: Description
        """
        if not re.search(r"\d+", url):
            return None
        return int(re.findall(r"\d+", url)[-1])

    def getTotalChapters(self, response):
        tlib = self.tlib
        conf = self.crawl_conf
        logger = self.ulogger
        total_chapters = conf["total_chapters"]
        total_pages = self.getPageNumber(response.url)
        if total_pages:
            chapters_per_url = total_chapters
            chapter_urls = response.css(config.SELECTORS["chapter_urls"])\
                .getall()
            total_chapters = chapters_per_url*(total_pages - 1) \
                + len(chapter_urls)
            conf["total_chapters"] = total_chapters
        conf["current_chapter"] = 0
        conf["end_chapter"] = total_chapters if conf["end_chapter"] == -1 \
            else conf["end_chapter"]
        self.crawl_conf = conf
        # show logs
        logger.info("[%s] -- total chapters: %s" %
                    (logger.name, conf["total_chapters"]))
        logger.info("[%s] -- start chapter: %s" %
                    (logger.name, conf["start_chapter"]))
        logger.info("[%s] -- end chapter: %s" %
                    (logger.name, conf["end_chapter"]))
        # create epub metadata file
        self.epub_conf["start_chapter"] = conf["start_chapter"]
        self.epub_conf["end_chapter"] = conf["end_chapter"]
        tlib.metadata2json(self.epub_conf, self.output_dir)
        # parse chapters
        yield scrapy.Request(conf["first_chapter_url"],
                             callback=self.parseChapter)

    def parseChapter(self, response):
        """Crawl a chapter to html file

        Args:
            response (TYPE): scrapy http response

        Yields:
            TYPE: Description
        """
        tlib = self.tlib
        logger = self.ulogger
        conf = self.crawl_conf
        # get title
        title = "".join(response.css(config.SELECTORS["chapter_title"])
                        .getall())
        title = tlib.removeTags(title)

        conf["current_chapter"] += 1
        if conf["current_chapter"] >= conf["start_chapter"]:
            # get content
            content = "".join(response.css(
                              config.SELECTORS["chapter_content"]).getall())
            # remove html tags except kept tags
            content = tlib.cleanTags(content)
            content = tlib.br2p(content)  # convert <br> to <p>
            # add drop cap to first paragraph
            kwargs = {
                "title": title,
                "removal_patterns": config.REMOVAL_PATTERNS,
                "removal_symbols": config.REMOVAL_SYMBOLS
            }
            content = tlib.addDropcap(content, **kwargs)

            # create a html file
            html_conf = {
                "total_chapters": conf["total_chapters"],
                "current_chapter": conf["current_chapter"],
                "output_dir": self.output_dir,
            }
            tlib.genHtmlFile(title, content, html_conf)
            logger.info("[%s] crawled chapter %s/%s: %s" %
                        (logger.name, conf["current_chapter"],
                         conf["end_chapter"], title))
            if logger.disabled:
                tlib.printProgressBar(conf["current_chapter"],
                                      conf["end_chapter"],
                                      prefix="Crawling progress:")
        # get url of next chapter
        next_chapter_url = response.css(
                           config.SELECTORS["next_chapter_urls"]).getall()[0]
        epub_conf = {
            "output_dir": self.output_dir,
            "clean_dir": conf["clean_dir"]
        }
        if "javascript" in next_chapter_url:
            tlib.genEpubFile(epub_conf, logger)
            return
        if conf["current_chapter"] < conf["end_chapter"]:
            yield scrapy.Request(next_chapter_url,
                                 callback=self.parseChapter)
        else:
            tlib.genEpubFile(epub_conf, logger)
