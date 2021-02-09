# -*- coding: utf-8 -*-
# @Author: anh-tuan.vu
# @Date:   2021-02-08 05:35:07
# @Last Modified by:   anh-tuan.vu
# @Last Modified time: 2021-02-09 14:24:20

SELECTORS = {
    "function_calls": "div::attr(onclick)",
}

PATTERNS = {
    "function_call": r"\'(.*)\'",
}

CONTENT_URL = "https://vnthuquan.net/truyen/chuonghoi_moi.aspx"
SPLITTER = "--!!tach_noi_dung!!--"
REMOVAL_SYMBOLS = ["\"", "\'", "-", "“", "”"]
