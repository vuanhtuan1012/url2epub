# -*- coding: utf-8 -*-
# @Author: anh-tuan.vu
# @Date:   2021-02-04 20:37:00
# @Last Modified by:   anh-tuan.vu
# @Last Modified time: 2021-02-06 20:11:11

from U2eProcess import U2eProcess
from spiders.TruyenFull import TruyenFull
import argparse


if __name__ == '__main__':
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

    epub_conf = {
        # "title": "",
        # "author": "",
        # "desc": "",
        # "source": "",
        # "publisher": "NXB Văn Học"
    }
    crawl_conf = {
        "start_chapter": 764,
        # "end_chapter": 5,
        # "clean_dir": False
    }
    output_dir = "temps"
    url = "https://truyenfull.vn/dai-chua-te"

    process = U2eProcess(debug=debug)
    process.crawl(TruyenFull, url, debug=debug,
                  disabled_log=disabled_log,
                  epub_conf=epub_conf, crawl_conf=crawl_conf,
                  # output_dir=output_dir
                  )
    process.start()
