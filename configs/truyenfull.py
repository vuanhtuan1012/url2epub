# -*- coding: utf-8 -*-
# @Author: anh-tuan.vu
# @Date:   2021-02-04 20:31:18
# @Last Modified by:   anh-tuan.vu
# @Last Modified time: 2021-03-12 11:10:51

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

REMOVAL_PATTERNS = [r"dịch.*?:",  r"nhóm\s+dịch",
                    r"edit", r"beta", r"biên\s+lại", r"biên\s+soạn"]

REMOVAL_SYMBOLS = ["\"", "\'", "-", "“", "”", "…", ".", "ads"]

# triple of (pattern, repl, flag)
# flag = 2 for case insensitive
# flag = 0 for case sensitive
# CORRECTIONS = [('lâm lạc', 'Lâm Lạc', 2)]
CORRECTIONS = []
