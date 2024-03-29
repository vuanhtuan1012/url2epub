# -*- coding: utf-8 -*-
# @Author: anh-tuan.vu
# @Date:   2021-02-04 20:18:19
# @Last Modified by:   anh-tuan.vu
# @Last Modified time: 2021-04-08 19:20:20

import scrapy
from scrapy.spiders import CrawlSpider
from configs import truyenfull as config
from TLib import TLib
import re
from time import time
import os


class TruyenFull(CrawlSpider):
    name = "TruyenFull"
    allowed_domains = ["truyenfull.vn"]

    def __init__(self, url: str, *args, **kwargs):
        """Initialize object

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

    def start_requests(self):
        """Verify url before parsing

        Yields:
            def: parse
        """
        logger = self.ulogger
        tlib = self.tlib
        logger.info("[%s] %s Crawl url: %s" %
                    (logger.name, tlib.getLogLevelName(logger.level),
                     self.url))
        logger.info("[%s] %s -- clean dir: %s" %
                    (logger.name, tlib.getLogLevelName(logger.level),
                     self.crawl_conf["clean_dir"]))

        # clean output directory
        error, msg = tlib.cleanDir(self.output_dir,
                                   self.crawl_conf["clean_dir"])
        if error:
            logger.setLevel("ERROR")
            logger.error("[%s] %s %s" %
                         (logger.name,
                          tlib.getLogLevelName(logger.level), msg))
            if logger.disabled:
                print("[ERROR] %s" % msg)
            return

        # verify input url
        error, msg = tlib.isValidUrl(self.url, self.allowed_domains)
        if error:
            logger.setLevel("ERROR")
            logger.error("[%s] %s %s" %
                         (logger.name,
                          tlib.getLogLevelName(logger.level), msg))
            if logger.disabled:
                print("[ERROR] %s" % msg)
            return

        # put stylesheet file to output directory
        tlib.putStyle2Dir(self.output_dir)
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        """Parse input url

        Args:
            response (scrapy.http.response): html reponse

        Yields:
            def: getTotalChapters
        """
        logger = self.ulogger
        tlib = self.tlib

        # set metadata
        conf = self.epub_conf
        metadata = self.getMetadata(response)
        epub_conf = {
            "title": conf.get("title", metadata["title"]),
            "author": conf.get("author", metadata["author"]),
            "desc": conf.get("desc", metadata["desc"]),
            "source": conf.get("source", metadata["source"]),
            "language": conf.get("language", "vi"),
            "publisher": conf.get("publisher", "TLab")
        }
        if not epub_conf["source"]:
            epub_conf["source"] = "truyenfull.vn"
        if conf.get("cover"):
            epub_conf["cover"] = conf["cover"]
        self.epub_conf = epub_conf
        logger.info("[%s] %s Getting story: %s" %
                    (logger.name, tlib.getLogLevelName(logger.level),
                     epub_conf["title"]))
        logger.info("[%s] %s -- author: %s" %
                    (logger.name, tlib.getLogLevelName(logger.level),
                     epub_conf["author"]))

        # set start, limit chapter to crawl
        conf = self.crawl_conf
        conf["limit"] = conf.get("limit", 0)
        if not conf.get("start_chapter"):
            conf["start_chapter"] = 1
        chapter_urls = response.css(config.SELECTORS["chapter_urls"]).getall()
        conf["first_chapter_url"] = chapter_urls[0]
        conf["total_chapters"] = len(chapter_urls)
        self.crawl_conf = conf
        last_page_url = response.url
        page_urls = response.css(config.SELECTORS["page_urls"]).getall()
        if page_urls:
            i = -1
            last_page_url = page_urls[i]
            while "javascript" in last_page_url:
                i -= 1
                last_page_url = page_urls[i]
        yield scrapy.Request(last_page_url, dont_filter=True,
                             callback=self.getTotalChapters)

    def getMetadata(self, response) -> dict:
        """Get metadata of a story

        Args:
            response (scrapy.http.response): html reponse

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
        """Get total chapters

        Args:
            response (scrapy.http.response): html reponse

        Yields:
            def: parseChapter
        """
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
        self.crawl_conf = conf

        # show logs
        logger.info("[%s] %s -- total chapters: %s" %
                    (logger.name, tlib.getLogLevelName(logger.level),
                     conf["total_chapters"]))
        if conf["start_chapter"] != 1:
            logger.info("[%s] %s -- start chapter: %s" %
                        (logger.name, tlib.getLogLevelName(logger.level),
                         conf["start_chapter"]))
        if conf["limit"]:
            logger.info("[%s] %s -- limit: %s" %
                        (logger.name, tlib.getLogLevelName(logger.level),
                         conf["limit"]))

        # create epub metadata file
        self.epub_conf["start_chapter"] = conf["start_chapter"]
        self.epub_conf["limit"] = conf["limit"]
        tlib.metadata2json(self.epub_conf, self.output_dir)
        # parse chapters
        chapter_url = self.getChapterUrl(conf["start_chapter"]) \
            if conf["start_chapter"] != 1 else conf["first_chapter_url"]
        yield scrapy.Request(chapter_url, callback=self.parseChapter)

    def getChapterUrl(self, idx: int) -> str:
        """Get chapter url given chapter index

        Args:
            idx (int): chapter index

        Returns:
            str: chapter url
        """
        conf = self.crawl_conf
        idx = 1 if idx < 1 else idx
        chapter_url = os.path.join(self.url, "chuong-%s" % idx)
        self.crawl_conf["current_chapter"] = idx - 1
        return chapter_url

    def parseChapter(self, response):
        """Crawl a chapter to html file

        Args:
            response (scrapy.http.response): html reponse

        Yields:
            def: parseChapter
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
            content = tlib.br2p(content)  # convert <br/> to <p>

            # add drop cap to first paragraph
            kwargs = {
                "title": title,
                "removal_patterns": config.REMOVAL_PATTERNS,
                "removal_symbols": config.REMOVAL_SYMBOLS
            }
            content = tlib.addDropCap(content, **kwargs)
            if hasattr(config, "CORRECTIONS") and config.CORRECTIONS:
                content = tlib.correctWords(content, config.CORRECTIONS)

            # create a html file
            html_conf = {
                "total_chapters": conf["total_chapters"],
                "current_chapter": conf["current_chapter"],
                "output_dir": self.output_dir,
                "language": self.epub_conf["language"]
            }
            tlib.genHtmlFile(title, content, html_conf)

            # show log
            end_chapter = conf["total_chapters"] if not conf["limit"] \
                else conf["start_chapter"] + conf["limit"] - 1
            if end_chapter > conf["total_chapters"]:
                end_chapter = conf["total_chapters"]
            logger.info("[%s] %s crawled chapter %s/%s: %s" %
                        (logger.name, tlib.getLogLevelName(logger.level),
                         conf["current_chapter"],
                         end_chapter, title))
            if logger.disabled and not self.debug:
                tlib.printProgressBar(conf["current_chapter"]+1,
                                      end_chapter,
                                      prefix="Crawling progress:")
        # crawl next chapter
        continuable = True if not conf["limit"] \
            else (conf["current_chapter"] <
                  conf["start_chapter"] + conf["limit"] - 1)
        next_chapter_url = response.css(
            config.SELECTORS["next_chapter_urls"]).getall()[0]
        continuable = continuable and not ("javascript" in next_chapter_url)
        if continuable:
            yield scrapy.Request(next_chapter_url,
                                 callback=self.parseChapter)
        else:
            # generate epub file
            error, epub_file = tlib.genEpubFile(self.output_dir)
            if error:
                msg = epub_file
                logger.setLevel("ERROR")
                logger.error("[%s] %s %s" %
                             (logger.name,
                              tlib.getLogLevelName(logger.level), msg))
                if logger.disabled:
                    print("[ERROR] %s" % msg)
                return

            tlib.cleanDir(self.output_dir, conf["clean_dir"])
            end = time()
            logger.info("[%s] %s Crawling duration: %s" %
                        (logger.name, tlib.getLogLevelName(logger.level),
                         tlib.readSeconds(end - self.start)))
            msg = "The story %s is saved at %s" % \
                (self.epub_conf["title"], epub_file)
            logger.info("[%s] %s %s" %
                        (logger.name,
                         tlib.getLogLevelName(logger.level), msg))
            if logger.disabled:
                print(msg)
