# -*- coding: utf-8 -*-
# @Author: anh-tuan.vu
# @Date:   2021-02-04 21:00:44
# @Last Modified by:   anh-tuan.vu
# @Last Modified time: 2021-02-07 10:33:17

import logging
from datetime import datetime
import os
import re
import shutil
import json
import sys
from time import sleep
from ebooklib import epub
import tpub


class TLib(object):
    """docstring for TLib"""
    __HEADER = ("<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 "
                "Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/"
                "xhtml1-strict.dtd\">\n"
                "<html xmlns=\"http://www.w3.org/1999/xhtml\" "
                "xml:lang=\"{lang}\" lang=\"{lang}\">\n"
                "<head>\n\t<title>{title}</title>\n\t"
                "<link href=\"stylesheet.css\" type=\"text/css\""
                " rel=\"stylesheet\" media=\"all\"/>\n</head>\n")
    __BODY = ("<body>\n"
              "<h2 class=\"title\">{title}</h2>\n{content}\n"
              "</body>\n</html>")
    KEPT_TAGS = ['b', 'strong', 'em', 'p', 'i', 'sup']
    __FILE_EXT = ".e2u"
    __ERROR_CODES = {
        10: "Could not find metadata file",
        11: "Could not find stylesheet file",
        12: "Book title is empty",
        13: "Book author is empty",
        20: "Invalid url. %s",
        21: "Not allowed domain. Allowed domain(s): %s",
        30: "Directory doesn't exists. %s"
    }

    def __init__(self):
        super().__init__()

    def setLogger(self, log_name: str, **kwargs) -> logging.Logger:
        """Create a logger

        Args:
            log_name (str): name of logger
            **kwargs: keyword arguments

        Returns:
            logging.Logger: Description
        """
        # set default values
        level = kwargs.get("level", logging.INFO)
        storing = kwargs.get("storing", False)
        streaming = kwargs.get("streaming", True)
        log_dir = kwargs.get("log_dir", "")
        log_filename = "{}_{}.log".format(log_name,
                                          datetime.now()
                                          .strftime("%Y%m%d_%H%M%S_%f"))

        logger = logging.getLogger(log_name)
        logger.setLevel(level)
        formatter = logging.Formatter("%(message)s")

        if streaming:
            streamHandler = logging.StreamHandler()
            streamHandler.setFormatter(formatter)
            logger.addHandler(streamHandler)

        if storing:
            if log_dir and not os.path.isdir(log_dir):
                os.mkdir(log_dir)
            log_filepath = os.path.join(log_dir, log_filename)
            fileHandler = logging.FileHandler(log_filepath, mode="w",
                                              encoding="utf-8")
            fileHandler.setFormatter(formatter)
            logger.addHandler(fileHandler)
        return logger

    def getLogger(self, log_name: str) -> logging.Logger:
        """Summary

        Args:
            log_name (str): name of logger to get

        Returns:
            logging.Logger: Description
        """
        logger = logging.getLogger(log_name)
        return logger

    def cleanTags(self, content: str) -> str:
        """Clean tags in a text, except kept tags

        Args:
            content (str): text to clean tags

        Returns:
            str: clean text
        """
        # remove tags except kept tags
        close_tags = ["/" + tag for tag in self.KEPT_TAGS]
        kept_tags_pattern = r"<(?!(?:{})).*?>".format(
                            "|".join(self.KEPT_TAGS + close_tags))
        clean_text = re.sub(kept_tags_pattern, r"", content)
        # correct br tags
        clean_text = re.sub(r"<br.*?>", "<br/>", clean_text)
        # remove /br tags if it exists
        clean_text = re.sub(r"</br>", r"", clean_text)
        # remove &nbsp;
        clean_text = re.sub(r"&nbsp;", r" ", clean_text)
        # remove more than 2 spaces
        clean_text = re.sub(r"\s+", " ", clean_text)

        return clean_text.strip()

    def br2p(self, content: str) -> str:
        """Convert br tags in a text to p tags

        Args:
            content (str): text to convert

        Returns:
            str: converted text
        """
        # remove multiple <br/>
        converted_text = re.sub(r"(<br/>)+", r"<br/>", content)
        # converted_text <br/> to <p>
        converted_text = re.sub(r"<br/>", r"</p>\n<p>", converted_text)
        # add <p> if needed
        converted_text = "<p>" + converted_text
        converted_text += "</p>"
        # clean space
        converted_text = re.sub(r"<p>\s+", r"<p>", converted_text)
        converted_text = re.sub(r"\s+</p>", r"</p>", converted_text)
        # clear empty paragraphs
        converted_text = re.sub(r"<p></p>", r"", converted_text)

        return converted_text.strip()

    def isUrl(self, url: str) -> bool:
        """Check whether a string is an url or not

        Args:
            url (str): string to check

        Returns:
            bool: Description
        """
        pattern = re.compile(
            r"^(?:http|ftp)s?://"  # http:// or https://
            # domain...
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+"
            r"(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$", re.IGNORECASE
        )
        return False if pattern.match(url) is None else True

    def isValidUrl(self, url: str, allowed_domains: list) -> tuple:
        """Check whether an url is in allowed domains

        Args:
            url (str): url to check
            allowed_domains (list): list of allowed domains

        Returns:
            bool: error code, matches or message
        """
        if not self.isUrl(url):
            return 20, TLib.__ERROR_CODES[20] % url
        domains = [d.replace(".", r"\.") for d in allowed_domains]
        pattern = r"%s" % "|".join(domains)
        matches = re.search(pattern, url)
        if not matches:
            return 21, TLib.__ERROR_CODES[21] % ", ".join(allowed_domains)
        return 0, matches

    def cleanDir(self, output_dir: str, clean: bool) -> tuple:
        """Clean url2epub files in the output directory

        Args:
            output_dir (str): directory to clean
            clean (bool): True to clean, False to not clean

        Returns:
            tuple: error code, message or None
        """
        if not os.path.isdir(output_dir):
            return 30, TLib.__ERROR_CODES[30] % output_dir
        if not clean:
            return 0, None
        # remove url2epub files
        files = [file for file in os.listdir(output_dir)
                 if file.endswith(TLib.__FILE_EXT)]
        for file in files:
            os.remove(os.path.join(output_dir, file))
        # remove metadata & stylesheet files
        files = ["metadata.json", "stylesheet.css"]
        for file in files:
            filepath = os.path.join(output_dir, file)
            if os.path.isfile(filepath):
                os.remove(filepath)
        return 0, None

    def putStyle2Dir(self, output_dir: str):
        """Coppy stylesheet file to ouput directory

        Args:
            output_dir (str): path to output directory
        """
        stylesheet_file = os.path.join("configs", "stylesheet.css")
        destination = os.path.join(output_dir, "stylesheet.css")
        shutil.copyfile(stylesheet_file, destination)

    def metadata2json(self, data: dict, output_dir: str):
        """Save epub metadata to json file

        Args:
            data (dict): metadata
            output_dir (str): path to directory containing json file
        """
        filepath = os.path.join(output_dir, "metadata.json")
        with open(filepath, "w+", encoding="utf-8") as fp:
            json.dump(data, fp, indent=4, ensure_ascii=False)

    def removeTags(self, content: str) -> str:
        """Remove all tags in a text

        Args:
            content (str): text to remove tags

        Returns:
            str: clean text
        """
        # remove all tags
        clean_text = re.sub(r"<.*?>", "", content)
        # correct spaces
        clean_text = re.sub(r"\s+", " ", clean_text)
        return clean_text.strip()

    def addDropcap(self, content: str, **kwargs) -> str:
        """Add style has-dropcap to a text

        Args:
            content (str): text to add style
            **kwargs (optional): keyword arguments
                - title (str): title to remove redundant
                - removal_patterns (list[str]): patterns to
                                                remove unrelated text
                - removal_symbols (str): patterns to remove quotation marks

        Returns:
            str: Description
        """
        # get default values
        title = kwargs.get("title")
        removal_patterns = kwargs.get("removal_patterns")
        removal_symbols = kwargs.get("removal_symbols")

        # remove redundant paragraphs
        first_paragraph = re.search(r"<p>.*?</p>", content).group()
        if removal_patterns is not None:
            pattern = r"%s" % "|".join(removal_patterns)
            while re.search(pattern, first_paragraph):
                content = content[len(first_paragraph):].strip()
                first_paragraph = re.search(r"<p>.*?</p>", content).group()

        # remove redundant title
        if title is not None:
            pattern = r"[^a-zA-Z0-9]"
            cleaned_paragraph = self.removeTags(first_paragraph)
            asciied_paragraph = re.sub(pattern, "", cleaned_paragraph)
            asciied_title = re.sub(pattern, "", title)
            if asciied_paragraph in asciied_title:
                content = content[len(first_paragraph):].strip()
                first_paragraph = re.search(r"<p>.*?</p>", content).group()

        # remove all quotation mark in first_paragraph
        loc = len(first_paragraph)
        if removal_symbols is not None:
            first_paragraph = re.sub(removal_symbols, "", first_paragraph)
            first_paragraph = re.sub(r"\s+", " ", first_paragraph)

        # add stylesheet for drop cap
        first_paragraph = "<p class=\"has-dropcap\">" + first_paragraph[3:]
        content = first_paragraph + content[loc:]
        return content.strip()

    def genHtmlFile(self, title: str, content: str, conf: dict):
        """Write chapter to html file

        Args:
            title (str): chapter title
            content (str): chapter content
            conf (dict): configuration
                - total_chapters (int): total chapters
                - current_chapter (int): current chapters
                - output_dir (str): path to output directory
        """
        total_chapters = str(conf["total_chapters"])
        current_chapter = str(conf["current_chapter"])
        idx = "0" * (len(total_chapters) - len(current_chapter)) \
              + current_chapter
        filename = "chapter_%s%s" % (idx, TLib.__FILE_EXT)
        file_location = os.path.join(conf["output_dir"], filename)
        # set header & body
        header = TLib.__HEADER
        header = header.format(title=title, lang=conf["language"])
        body = TLib.__BODY
        body = body.format(title=title, content=content)
        # write to file
        with open(file_location, "w+", encoding="utf-8") as fp:
            fp.write(header)
            fp.write(body)

    def printProgressBar(self, i: int, n: int, **kwargs):
        """Print a progress bar on console

        Args:
            i (int): iteration
            n (int): upper limit of iteration
            delay (int, optional): delay time in seconds
            **kwargs: keyword arguments

        Raises:
            UnicodeError: if console cannot display unicode character
        """
        # verify the environment
        if sys.stdout.encoding.upper() != "UTF-8":
            msg = [
                "your environment encoding is not UTF-8! Try command:",
                "PYTHONIOENCODING=UTF-8:surrogateescape python3 %s" %
                sys.argv[0]
            ]
            raise UnicodeError("\n".join(msg))

        # set default values
        delay = kwargs.get("delay", 0)
        prefix = kwargs.get("prefix", "Progress:")
        suffix = kwargs.get("suffix", "Completed")
        decimals = kwargs.get("decimals", 2)
        length = kwargs.get("length", 30)
        fill = kwargs.get("fill", "█")

        # calculate for bar display
        i += 1
        percent = round(100 * i / n, decimals)
        filled_length = int(length * i // n)
        bar = fill * filled_length + "-" * (length-filled_length)
        if i < n:
            print("\r%s |%s| %s%% (%d/%d)" %
                  (prefix, bar, percent, i, n), end="\r")
        if delay:
            sleep(delay)
        if i == n:
            print("\r%s |%s| %s%% (%d/%d) %s" %
                  (prefix, bar, percent, i, n, suffix))

    def genEpubFile(self, output_dir: str) -> tuple:
        """Create epub from html files

        Args:
            output_dir (str): directory containing html files

        Returns:
            tuple: error code, epub_filepath or message
        """
        # verification
        metadata_file = os.path.join(output_dir, "metadata.json")
        stylesheet_file = os.path.join(output_dir, "stylesheet.css")
        if not os.path.isfile(metadata_file):
            return 10, TLib.__ERROR_CODES[10]
        if not os.path.isfile(stylesheet_file):
            return 11, TLib.__ERROR_CODES[11]

        with open(metadata_file, "r", encoding="utf-8") as fp:
            metadata = json.load(fp)
        title = metadata.get("title")
        author = metadata.get("author")
        if not title:
            return 12, TLib.__ERROR_CODES[12]
        if not author:
            return 13, TLib.__ERROR_CODES[13]

        # set default values
        metadata["language"] = metadata.get("language", "vi")
        metadata["publisher"] = metadata.get("publisher", "TLab")
        if not metadata.get("source"):
            metadata["source"] = "truyenfull.vn"

        # create book
        book = epub.EpubBook()
        book.set_identifier("tlab_%s" % datetime.now()
                            .strftime("%Y%m%d%H%I%S"))
        book.set_language(metadata["language"])
        if metadata["title"]:
            book.set_title(metadata["title"])
        if metadata["author"]:
            book.add_author(metadata["author"])
        if metadata["desc"]:
            book.add_metadata("DC", "description", metadata["desc"])
        book.add_metadata("DC", "source", metadata["source"])
        book.add_metadata("DC", "publisher", metadata["publisher"])
        book.add_metadata("DC", "date", datetime.now().strftime("%Y-%m-%d"))

        # add book cover
        spine = list()
        if metadata.get("cover"):
            filename = "cover%s" % os.path.splitext(metadata["cover"])[1]
            book.set_cover(filename, open(metadata["cover"], "rb").read())
            spine.append("cover")

        # add book style
        with open(stylesheet_file, "r") as fp:
            style = fp.read()
        chapter_style = epub.EpubItem(uid="chapter_style",
                                      file_name="stylesheet.css",
                                      media_type="text/css",
                                      content=style)
        book.add_item(chapter_style)

        # add book chapters
        toc = list()
        spine.append("nav")
        files = [file for file in os.listdir(output_dir)
                 if file.endswith(TLib.__FILE_EXT)]
        files.sort()
        for file in files:
            filepath = os.path.join(output_dir, file)
            with open(filepath, "r", encoding="utf-8") as fp:
                content = fp.read()
            pattern = re.compile("<h2.*?>(.*)</h2>")
            title = pattern.search(content).group(1)
            # create chapter & add to book
            filename = "%s.xhtml" % os.path.splitext(file)[0]
            chapter = epub.EpubHtml(file_name=filename, title=title,
                                    lang=metadata["language"])
            chapter.content = content
            chapter.add_item(chapter_style)
            book.add_item(chapter)
            spine.append(chapter)
            toc.append(epub.Link(filename, title, os.path.splitext(file)[0]))

        # create table of contents
        book.toc = tuple(toc)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = spine

        # gen epub file
        filename = "%s - %s.epub" % (metadata["author"], metadata["title"])
        epub_file = os.path.join(output_dir, filename)
        epub.write_epub(epub_file, book, {})
        return 0, epub_file

    def mkdir(self, dirpath: str):
        if not os.path.isdir(dirpath):
            os.mkdir(dirpath)

    def readSeconds(self, seconds: float, **kwargs) -> str:
        """Read seconds into text

        Args:
            seconds (float): seconds to read
            **kwargs: keyword arguments

        Returns:
            str: text of seconds
        """
        _UNITS = ["day", "hour", "minute", "second"]
        _CONVERSION = {
            "day": 60*60*24,
            "hour": 60*60,
            "minute": 60,
            "second": 1
        }

        # set default value
        decimals = kwargs.get("decimals", 2)
        seconds = round(seconds, decimals)

        v = 0
        i = -1
        while not v:
            i += 1
            if i == len(_UNITS):
                return "%s seconds" % seconds
            unit = _UNITS[i]
            v = seconds // _CONVERSION[unit]
        res = ""
        for unit in _UNITS[i:]:
            v = seconds // _CONVERSION[unit]
            seconds = seconds % _CONVERSION[unit]
            v = int(v)
            if unit == "second":
                v = v + seconds
                v = round(v, decimals)
            if not v:
                continue
            if v != 1:
                res += "%s %ss " % (v, unit)
            else:
                res += "%s %s " % (v, unit)
        return res.strip()
