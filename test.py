# -*- coding: utf-8 -*-
# @Author: anh-tuan.vu
# @Date:   2021-02-04 20:37:00
# @Last Modified by:   anh-tuan.vu
# @Last Modified time: 2021-02-07 13:24:47

from U2eProcess import U2eProcess
from spiders.TruyenFull import TruyenFull
import argparse


if __name__ == '__main__':
    # get arguments of debug & log
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', required=False)
    parser.add_argument('-l', '--log', required=False)
    args = parser.parse_args()
    # debug mode
    debug = args.debug if args.debug else ""
    debug = True if debug.lower() == "true" else False
    # logging mode
    log = args.log if args.log else ""
    log = False if log.lower() == "false" else True
    disabled_log = not log

    # set metadata for book
    epub_conf = {
        # "title": "",
        # "author": "",
        # "desc": "",
        # "source": "",
        # "publisher": "NXB Thời Đại",
        "cover": "url2epub/cover_tttd.jpg"
    }
    # configuration to crawl
    crawl_conf = {
        "start_chapter": 770,
        # "end_chapter": 775,
        # "clean_dir": False
    }
    output_dir = "/mnt/c/Users/anh-t/Desktop"
    url = "https://truyenfull.vn/dai-chua-te/"

    process = U2eProcess(debug=debug)
    process.crawl(TruyenFull, url,
                  output_dir=output_dir,  # optional
                  debug=debug,  # optional
                  disabled_log=disabled_log,  # optional
                  epub_conf=epub_conf,  # optional
                  crawl_conf=crawl_conf,  # optional
                  )
    process.start()
