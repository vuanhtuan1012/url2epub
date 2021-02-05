# -*- coding: utf-8 -*-
# @Author: anh-tuan.vu
# @Date:   2021-02-04 21:00:44
# @Last Modified by:   anh-tuan.vu
# @Last Modified time: 2021-02-05 17:04:35

import logging
from datetime import datetime
import os
import constants
import re
import shutil
import json
import sys
from time import sleep
from ebooklib import epub


class TLib(object):
    """docstring for TLib"""
    CLEAN_DIR_EXCEPTION = [".jpg", ".png", ".epub"]
    HTML_HEADER = ("<html xmlns=\"http://www.w3.org/1999/xhtml\">\n"
                   "<head>\n\t<title>{title}</title>\n\t"
                   "<meta charset=\"utf-8\">\n\t"
                   "<link href=\"stylesheet.css\" type=\"text/css\""
                   " rel=\"stylesheet\">\n"
                   "</head>\n")
    HTML_BODY = ("<body>\n"
                 "<h2 class=\"title\">{title}</h2>\n{content}\n"
                 "</body>\n</html>")

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
        close_tags = ["/" + tag for tag in constants.HTML_KEPT_TAGS]
        kept_tags_pattern = r"<(?!(?:{})).*?>".format(
                            "|".join(constants.HTML_KEPT_TAGS + close_tags))
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

    def isValidUrl(self, url: str, allowed_domains: list) -> bool:
        """Check whether an url is in allowed domains

        Args:
            url (str): url to check
            allowed_domains (list): list of allowed domains

        Returns:
            bool: Description
        """
        if not self.isUrl(url):
            return False
        domains = [d.replace(".", r"\.") for d in allowed_domains]
        pattern = r"%s" % "|".join(domains)
        return True if re.search(pattern, url) else False

    def cleanDir(self, output_dir: str, clean: bool, logger: logging) -> bool:
        """Clean output directory

        Args:
            output_dir (str): directory to clean
            clean (bool): True to clean, False to not clean
            logger (logging): Description

        Returns:
            bool: False if the directory does not exist, otherwise True
        """
        if not os.path.isdir(output_dir):
            logger.info("[%s] ERROR: Output directory %s does not exist" %
                        (logger.name, output_dir))
            return False
        if not clean:
            return True
        files = [file for file in os.listdir(output_dir)]
        for file in files:
            if os.path.splitext(file)[1] not in self.CLEAN_DIR_EXCEPTION:
                os.remove(os.path.join(output_dir, file))
        return True

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
        title = kwargs.get("title", None)
        removal_patterns = kwargs.get("removal_patterns", None)
        removal_symbols = kwargs.get("removal_symbols", None)

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
        filename = "chapter_%s.html" % idx
        file_location = os.path.join(conf["output_dir"], filename)
        # set header & body
        header = self.HTML_HEADER
        header = header.format(title=title)
        body = self.HTML_BODY
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
        length = kwargs.get("length", 50)
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

    def genEpubFile(self, conf: dict, logger: logging):
        """Create epub from html files

        Args:
            conf (dict): configuration
                - output_dir (str): directory containing html files
                - clean_dir (bool): True to clean directory after generating
            logger (logging): Description
        """
        book = epub.EpubBook()
        # get metadata
        filepath = os.path.join(conf["output_dir"], "metadata.json")
        with open(filepath, "r", encoding="utf-8") as fp:
            metadata = json.load(fp)
        if not metadata.get("language", None):
            metadata["language"] = "vi"
        if not metadata.get("publisher", None):
            metadata["publisher"] = "TLab"
        if not metadata.get("source", None):
            metadata["source"] = "truyenfull.vn"
        # set book metadata
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
        # add book style
        filepath = os.path.join(conf["output_dir"], "stylesheet.css")
        with open(filepath, "r") as fp:
            style = fp.read()
        chapter_style = epub.EpubItem(uid="chapter_style",
                                      file_name="stylesheet.css",
                                      media_type="text/css",
                                      content=style)
        book.add_item(chapter_style)
        # add chapters
        toc = list()
        spine = list()
        files = [file for file in os.listdir(conf["output_dir"])
                 if file.endswith("html")]
        for file in files:
            filepath = os.path.join(conf["output_dir"], file)
            with open(filepath, "r", encoding="utf-8") as fp:
                content = fp.read()
            pattern = re.compile("<h2.*?>(.*)</h2>")
            title = pattern.search(content).group(1)
            # create chapter & add to book
            chapter = epub.EpubHtml(file_name=file, title=title,
                                    lang=metadata["language"])
            chapter.content = content
            chapter.add_item(chapter_style)
            book.add_item(chapter)
            spine.append(chapter)
            toc.append(epub.Link(file, title, os.path.splitext(file)[0]))
        # create table of contents
        book.toc = tuple(toc)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        spine.append("nav")
        book.spine = spine
        # gen epub file
        filename = "%s - %s.epub" % (metadata["author"], metadata["title"])
        filepath = os.path.join(conf["output_dir"], filename)
        epub.write_epub(filepath, book, {})
        logger.info("[%s] The story %s is saved at %s" %
                    (logger.name, metadata["title"], filepath))
        self.cleanDir(conf["output_dir"], conf["clean_dir"], logger)

    def mkdir(self, dirpath: str):
        os.mkdir(dirpath)
