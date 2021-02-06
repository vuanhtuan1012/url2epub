# url2epub

## Resources

- [Epub Validator](https://www.ebookit.com/tools/bp/Bo/eBookIt/epub-validator)
- [XHTML Validator](https://validator.w3.org/nu/#file)
- [Create a Table of Contents with a Navigation Document](https://kdp.amazon.com/en_US/help/topic/G201605710)

## After generating

Open epub file with Sigil, then
- Add cover: Tools > Add Cover...
- Add semantic table of contents:
	- Right click on file `nav.xhtml` > Add semantics... > Table of Contents.
    - In file `nav.xhtml` change `<nav epub:type="toc" id="id" role="doc-toc">` to `<nav epub:type="toc" id="toc" role="doc-toc">`.
- Add TOC & start page: add this snippet code to file `content.opf`, before close tag `</package>`
```html
  <guide>
    <reference type="toc" title="Table of Contents" href="nav.xhtml#toc"/>
    <reference type="text" title="start" href="chapter_01.xhtml"/>
  </guide>
```

These actions will create the file `cover.xhtml` & changement in `nav.xhtml`, `content.opf`.

## Miscellaneity

Kindles want three objects to be tagged:

1) The cover IMAGE (not the page)
2) The text TOC
3) The Starting position.

Actually you can create an AZW/mobi from an ePub without these and it will work, but better to make it happy.

You can do this in Sigil by right-clicking on the file list and choosing "Add semantics".

1) For the cover PAGE you can tag it "Cover" but you must also be sure that the cover IMAGE is tagged "Cover Image" -- may be already done if you used the "Add cover" tool.

2) The TOC choose "Table of Contents" (again, will be set if you used the "Create HTML TOC" tool)

3) The Start page -- for this choose "Text" (presumably meaning the first page of text).
I usually use the title page as the Start page. Amazon tells you to use Chapter 1, so do that if you're submitting to them. You cannot use the Cover, however, as Kindles do not have a HTML cover page, only the image.

These "semantics" all create entries in the opf file, the TOC and Start in the "Guide" at the end; the cover image in the "meta' and "manifest".

[Kindle Reviewer 3 says there's no TOC](https://www.mobileread.com/forums/showpost.php?p=3557815&postcount=4)

