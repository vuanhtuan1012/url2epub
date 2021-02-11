# -*- coding: utf-8 -*-
# @Author: anh-tuan.vu
# @Date:   2021-02-04 20:37:00
# @Last Modified by:   anh-tuan.vu
# @Last Modified time: 2021-02-11 13:37:04

from U2eProcess import U2eProcess
from spiders.TruyenFull import TruyenFull
from spiders.VnThuQuan import VnThuQuan
import argparse
from urllib.parse import urlparse
from TLib import TLib


def getSpider(url: str):
    """Get spider from url

    Args:
        url (str): url to crawl

    Returns:
        TYPE: None if invalid url
    """
    allowed_domains = VnThuQuan.allowed_domains + TruyenFull.allowed_domains
    error, msg = TLib().isValidUrl(url, allowed_domains)
    if error:
        print("[ERROR] %s" % msg)
        return

    spiders = {k: VnThuQuan for k in VnThuQuan.allowed_domains}
    spiders.update({k: TruyenFull for k in TruyenFull.allowed_domains})
    domain = urlparse(url).netloc
    return spiders[domain]


def initialize():
    parser = argparse.ArgumentParser("crawl.py")
    parser.add_argument("url", type=str,
                        help="url to crawl")
    parser.add_argument("-d", "--debug", default=False,
                        action="store_const", const=True,
                        help="enable debug mode",
                        required=False)
    parser.add_argument("-l", "--log", default=True,
                        action="store_const", const=False,
                        help="disable log mode",
                        required=False)
    parser.add_argument("-o", "--output_dir", default="",
                        help="output directory",
                        required=False)
    parser.add_argument("-c", "--cover", default="",
                        help="path to cover image",
                        required=False)
    parser.add_argument("-p", "--publisher", default="",
                        help="name of publisher",
                        required=False)
    parser.add_argument("-e", "--end_chapter", default=0, type=int,
                        help="chapter index to finish crawl",
                        required=False)
    parser.add_argument("-s", "--start_chapter", default=1, type=int,
                        help="chapter index to start crawl",
                        required=False)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    # get arguments
    args = initialize()
    url = args.url
    output_dir = args.output_dir
    cover = args.cover
    publisher = args.publisher
    end_chapter = args.end_chapter
    start_chapter = args.start_chapter
    debug = args.debug
    disabled_log = not args.log

    # set metadata for book
    epub_conf = {
        # "title": "",
        # "author": "",
        # "desc": "",
        # "source": "",
        "publisher": publisher,
        "cover": cover
    }
    # configuration to crawl
    crawl_conf = {
        "start_chapter": start_chapter,
        "end_chapter": end_chapter,
        # "clean_dir": False
    }

    spider = getSpider(url)
    if not spider:
        exit(1)
    process = U2eProcess(debug=debug)
    process.crawl(spider, url,
                  output_dir=output_dir,  # optional
                  debug=debug,  # optional
                  disabled_log=disabled_log,  # optional
                  epub_conf=epub_conf,  # optional
                  crawl_conf=crawl_conf,  # optional
                  )
    process.start()
