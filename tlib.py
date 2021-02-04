# -*- coding: utf-8 -*-
# @Author: anh-tuan.vu
# @Date:   2021-02-04 21:00:44
# @Last Modified by:   anh-tuan.vu
# @Last Modified time: 2021-02-04 22:42:28

import logging
from datetime import datetime
import os
import constants
import re


class TLib(object):
    """docstring for TLib"""
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
        level = kwargs.get('level', logging.INFO)
        storing = kwargs.get('storing', False)
        streaming = kwargs.get('streaming', True)
        log_dir = kwargs.get('log_dir', '')
        log_filename = '{}_{}.log'.format(log_name,
                                          datetime.now()
                                          .strftime('%Y%m%d_%H%M%S_%f'))

        logger = logging.getLogger(log_name)
        logger.setLevel(level)
        formatter = logging.Formatter('%(message)s')

        if streaming:
            streamHandler = logging.StreamHandler()
            streamHandler.setFormatter(formatter)
            logger.addHandler(streamHandler)

        if storing:
            if log_dir and not os.path.isdir(log_dir):
                os.mkdir(log_dir)
            log_filepath = os.path.join(log_dir, log_filename)
            fileHandler = logging.FileHandler(log_filepath, mode='w',
                                              encoding='utf-8')
            fileHandler.setFormatter(formatter)
            logger.addHandler(fileHandler)
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
