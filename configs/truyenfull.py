# -*- coding: utf-8 -*-
# @Author: anh-tuan.vu
# @Date:   2021-02-04 20:31:18
# @Last Modified by:   anh-tuan.vu
# @Last Modified time: 2021-02-09 14:24:02

SELECTORS = {
    "title": "title::text",
    "desc": "div.desc-text",
    "author": "div.info > div > a[itemprop=author]::text",
    "source": "span.source::text",
    "chapter_urls": "ul.list-chapter > li > a::attr(href)",
    "next_chapter_urls": "a#next_chap::attr(href)",
    "chapter_title": "a.chapter-title",
    "chapter_content": "div.chapter-c",
    "page_urls": "ul.pagination > li > a::attr(href)",
}

REMOVAL_PATTERNS = [r"dịch\s*:",  r"nhóm\s+dịch",
                    r"edit", r"beta"]

REMOVAL_SYMBOLS = ["\"", "\'", "-", "“", "”"]
