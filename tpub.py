# -*- coding: utf-8 -*-
# @Author: anh-tuan.vu
# @Date:   2021-02-07 02:54:48
# @Last Modified by:   anh-tuan.vu
# @Last Modified time: 2021-02-07 12:24:21

from ebooklib import epub
import six
import io
from lxml import etree
from PIL import Image
from collections import OrderedDict
from ebooklib.utils import parse_string, get_pages_for_items
import zipfile
import os
import ebooklib

"""
Overriding ebooklib methods to:
    - add cover & set it to full page
    - add semantic table of contents
    - set start page to the first chapter
"""


# COVER
COVER_TEMPLATE = ("<?xml version=\"1.0\" encoding=\"UTF-8\" "
                  "standalone=\"no\" ?>\n<!DOCTYPE html>\n"
                  "<html xmlns=\"http://www.w3.org/1999/xhtml\" "
                  "xmlns:epub=\"http://www.idpf.org/2007/ops\">\n"
                  "<head>\n<title>Cover</title>\n</head>\n"
                  "<body>\n<div style=\"text-align: center; padding: 0pt; "
                  "margin: 0pt;\">\n\t\t"
                  "<svg xmlns=\"http://www.w3.org/2000/svg\" height=\"100%\" "
                  "version=\"1.1\" width=\"100%\" "
                  "xmlns:xlink=\"http://www.w3.org/1999/xlink\">\n\t\t\t"
                  "<image/>\n\t\t</svg>\n    </div></body>\n</html>")


def initEpubCoverHtml(self, uid="cover", file_name="cover.xhtml",
                      image_name="", title="Cover", image_data=six.b("")):

    super(epub.EpubCoverHtml, self).__init__(uid=uid,
                                             file_name=file_name, title=title)
    self.image_name = image_name
    self.image_data = image_data
    self.is_linear = False


def getContentEpubCoverHtml(self):
    # get image size
    im = Image.open(io.BytesIO(self.image_data))
    width, height = im.size

    # set values to cover
    NAMESPACES = {"SVG": "http://www.w3.org/2000/svg"}
    # self.content = self.book.get_template("cover")
    self.content = six.b(COVER_TEMPLATE)
    tree = parse_string(super(epub.EpubCoverHtml, self).get_content())
    tree_root = tree.getroot()

    img = tree_root.xpath("//svg:image",
                          namespaces={"svg": NAMESPACES["SVG"]})
    img[0].attrib["width"] = "%s" % width
    img[0].attrib["height"] = "%s" % height
    img[0].attrib["{http://www.w3.org/1999/xlink}href"] = self.image_name

    svg = tree_root.xpath("//svg:svg", namespaces={"svg": NAMESPACES["SVG"]})
    svg[0].attrib["viewBox"] = "0 0 %s %s" % (width, height)
    svg[0].attrib["preserveAspectRatio"] = "xMidYMid meet"

    return etree.tostring(tree, pretty_print=True,
                          encoding="utf-8", xml_declaration=True)


def setCoverEpubBook(self, file_name, content, create_page=True):
    c0 = epub.EpubCover(file_name=file_name)
    c0.content = content
    self.add_item(c0)

    if create_page:
        c1 = epub.EpubCoverHtml(image_name=file_name, image_data=content)
        c1.properties = ["svg"]
        self.add_item(c1)
        g = {"href": c1.file_name, "title": c1.title, "type": "cover"}
        self.guide.append(g)

    self.add_metadata(None, "meta", "", OrderedDict([("name", "cover"),
                      ("content", "cover-img")]))


epub.EpubCoverHtml.__init__ = initEpubCoverHtml
epub.EpubCoverHtml.get_content = getContentEpubCoverHtml
epub.EpubBook.set_cover = setCoverEpubBook


# NAV
def writeItemsEpubWriter(self):
    for item in self.book.get_items():
        if isinstance(item, epub.EpubNcx):
            self.out.writestr("%s/%s" %
                              (self.book.FOLDER_NAME, item.file_name),
                              self._get_ncx())
        elif isinstance(item, epub.EpubNav):
            g = {"href": item.file_name, "title": self.book.title,
                 "type": "toc"}
            self.book.guide.append(g)
            self.out.writestr("%s/%s" %
                              (self.book.FOLDER_NAME, item.file_name),
                              self._get_nav(item))
        elif item.manifest:
            self.out.writestr("%s/%s" %
                              (self.book.FOLDER_NAME, item.file_name),
                              item.get_content())
        else:
            self.out.writestr("%s" % item.file_name, item.get_content())


def writeEpubWriter(self):
    # check for the option allowZip64
    self.out = zipfile.ZipFile(self.file_name, "w", zipfile.ZIP_DEFLATED)
    self.out.writestr("mimetype", "application/epub+zip",
                      compress_type=zipfile.ZIP_STORED)

    self._write_container()
    self._write_items()
    self._write_opf()
    self.out.close()


def writeOpfManifestEpubWriter(self, root):
    manifest = etree.SubElement(root, "manifest")
    _ncx_id = None

    for item in self.book.get_items():
        if not item.manifest:
            continue
        if isinstance(item, epub.EpubNav):
            etree.SubElement(manifest, "item", {"href": item.get_name(),
                                                "id": item.id,
                                                "media-type": item.media_type,
                                                "properties": "nav"})
        elif isinstance(item, epub.EpubNcx):
            _ncx_id = item.id
            etree.SubElement(manifest, "item", {"href": item.file_name,
                                                "id": item.id,
                                                "media-type": item.media_type})
        elif isinstance(item, epub.EpubCover):
            etree.SubElement(manifest, "item", {"href": item.file_name,
                                                "id": item.id,
                                                "media-type": item.media_type,
                                                "properties": "cover-image"})
        else:
            opts = {"href": item.file_name,
                    "id": item.id,
                    "media-type": item.media_type}

            if hasattr(item, "properties") and len(item.properties) > 0:
                opts["properties"] = " ".join(item.properties)

            if hasattr(item, "media_overlay") and \
               item.media_overlay is not None:
                opts["media-overlay"] = item.media_overlay

            if hasattr(item, "media_duration") and \
               item.media_duration is not None:
                opts["duration"] = item.media_duration

            etree.SubElement(manifest, "item", opts)

        if item.id == "chapter_0":
            g = {"href": item.file_name, "title": item.title, "type": "text"}
            self.book.guide.append(g)
    return _ncx_id


def getNavEpubWriter(self, item):
    NAMESPACES = {"XML": "http://www.w3.org/XML/1998/namespace",
                  "EPUB": "http://www.idpf.org/2007/ops"}
    # just a basic navigation for now
    nav_xml = parse_string(self.book.get_template("nav"))
    root = nav_xml.getroot()

    root.set("lang", self.book.language)
    root.attrib["{%s}lang" % NAMESPACES["XML"]] = self.book.language

    nav_dir_name = os.path.dirname(item.file_name)

    head = etree.SubElement(root, "head")
    title = etree.SubElement(head, "title")
    title.text = self.book.title

    # for now this just handles css files and ignores others
    for _link in item.links:
        _lnk = etree.SubElement(head, "link", {
            "href": _link.get("href", ""), "rel": "stylesheet",
            "type": "text/css"
        })

    body = etree.SubElement(root, "body")
    nav = etree.SubElement(body, "nav", {
        "{%s}type" % NAMESPACES["EPUB"]: "toc",
        "id": "toc",
        "role": "doc-toc",
    })

    content_title = etree.SubElement(nav, "h2")
    content_title.text = self.book.title

    def _create_section(itm, items):
        ol = etree.SubElement(itm, "ol")
        for item in items:
            if isinstance(item, tuple) or isinstance(item, list):
                li = etree.SubElement(ol, "li")
                if isinstance(item[0], EpubHtml):
                    href = os.path.relpath(item[0].file_name, nav_dir_name)
                    a = etree.SubElement(li, "a", {"href": href})
                elif isinstance(item[0], Section) and item[0].href != "":
                    href = os.path.relpath(item[0].href, nav_dir_name)
                    a = etree.SubElement(li, "a", {"href": href})
                elif isinstance(item[0], Link):
                    href = os.path.relpath(item[0].href, nav_dir_name)
                    a = etree.SubElement(li, "a", {"href": href})
                else:
                    a = etree.SubElement(li, "span")
                a.text = item[0].title

                _create_section(li, item[1])

            elif isinstance(item, epub.Link):
                li = etree.SubElement(ol, "li")
                href = os.path.relpath(item.href, nav_dir_name)
                a = etree.SubElement(li, "a", {"href": href})
                a.text = item.title
            elif isinstance(item, epub.EpubHtml):
                li = etree.SubElement(ol, "li")
                href = os.path.relpath(item.file_name, nav_dir_name)
                a = etree.SubElement(li, "a", {"href": href})
                a.text = item.title

    _create_section(nav, self.book.toc)

    # LANDMARKS / GUIDE
    if len(self.book.guide) > 0 and self.options.get("epub3_landmark"):

        # Epub2 guide types do not map completely to epub3 landmark types.
        guide_to_landscape_map = {
            "notes": "rearnotes",
            "text": "bodymatter"
        }
        key = "{%s}type" % NAMESPACES["EPUB"]
        guide_nav = etree.SubElement(body, "nav",
                                     {key: "landmarks", "hidden": "hidden"})

        guide_content_title = etree.SubElement(guide_nav, "h2")
        guide_content_title.text = self.options.get("landmark_title", "Guide")

        guild_ol = etree.SubElement(guide_nav, "ol")

        for elem in self.book.guide:
            li_item = etree.SubElement(guild_ol, "li")

            if "item" in elem:
                chap = elem.get("item", None)
                if chap:
                    _href = chap.file_name
                    _title = chap.title
            else:
                _href = elem.get("href", "")
                _title = elem.get("title", "")

            guide_type = elem.get("type", "")
            key = "{%s}type" % NAMESPACES["EPUB"]
            a_item = etree.SubElement(li_item, "a", {
                key: guide_to_landscape_map.get(guide_type, guide_type),
                "href": os.path.relpath(_href, nav_dir_name)
            })
            a_item.text = _title

    # PAGE-LIST
    if self.options.get("epub3_pages"):
        type_items = self.book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        inserted_pages = get_pages_for_items([item for item in type_items
                                              if not
                                              isinstance(item, epub.EpubNav)])

        if len(inserted_pages) > 0:
            pagelist_nav = etree.SubElement(
                body,
                "nav",
                {
                    "{%s}type" % NAMESPACES["EPUB"]: "page-list",
                    "id": "pages",
                    "hidden": "hidden",
                }
            )
            pagelist_content_title = etree.SubElement(pagelist_nav, "h2")
            pagelist_content_title.text = self.options.get(
                "pages_title", "Pages"
            )

            pages_ol = etree.SubElement(pagelist_nav, "ol")

            for filename, pageref, label in inserted_pages:
                li_item = etree.SubElement(pages_ol, "li")

                _href = u"{}#{}".format(filename, pageref)
                _title = label

                a_item = etree.SubElement(li_item, "a", {
                    "href": os.path.relpath(_href, nav_dir_name),
                })
                a_item.text = _title

    return etree.tostring(nav_xml, pretty_print=True,
                          encoding="utf-8", xml_declaration=True)


epub.EpubWriter._write_items = writeItemsEpubWriter
epub.EpubWriter.write = writeEpubWriter
epub.EpubWriter._write_opf_manifest = writeOpfManifestEpubWriter
epub.EpubWriter._get_nav = getNavEpubWriter
