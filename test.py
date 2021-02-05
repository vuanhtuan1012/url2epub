# -*- coding: utf-8 -*-
# @Author: anh-tuan.vu
# @Date:   2021-02-04 20:37:00
# @Last Modified by:   anh-tuan.vu
# @Last Modified time: 2021-02-05 17:06:49

from U2eProcess import U2eProcess
from spiders.TruyenFull import TruyenFull
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', required=False)
    parser.add_argument('-l', '--disabled_logging', required=False)
    args = parser.parse_args()
    debug = args.debug if args.debug else ""
    disabled_logging = args.disabled_logging if args.disabled_logging else ""
    debug = True if debug.lower() == "true" else False
    disabled_logging = True if disabled_logging.lower() == "true" else False

    # epub_conf = {
    #     "title": "",
    #     "author": "",
    #     "desc": "",
    #     "source": ""
    # }
    # crawl_conf = {
    #     "start_chapter": 0,
    #     "end_chapter": 5,
    #     # "clean_dir": False
    # }
    # url = "https://truyenfull.vn/dai-chua-te"
    # output_dir = "temps"

    process = U2eProcess(debug=debug)
    process.crawl(TruyenFull, url, disabled_logging=disabled_logging)
    process.start()
