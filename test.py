# -*- coding: utf-8 -*-
# @Author: anh-tuan.vu
# @Date:   2021-02-04 20:37:00
# @Last Modified by:   anh-tuan.vu
# @Last Modified time: 2021-02-04 23:28:26

from U2eProcess import U2eProcess
from spiders.TruyenFull import TruyenFull


if __name__ == '__main__':
    url = "https://truyenfull.vn/dai-chua-te"
    process = U2eProcess()
    process.crawl(TruyenFull, url)
    process.start()
