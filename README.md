# url2epub

This is a tool for creating a ebook in epub format from an url.

Supported sites:
- [vnthuquan.net](https://vnthuquan.net/)
- [truyenfull.vn](https://truyenfull.vn/)

## Usage

```
python crawl.py [-h] [-d] [-l] [-o OUTPUT_DIR] [-c COVER] [-p PUBLISHER] [-s START] [-i LIMIT] url
```

- `-h`: display help
- `-d`: enable debug mode. Default: disabled
- `-l`: disable logging mode. Default: enabled
- `-o`: path to output directory. Default: `url2epub` inside current directory
- `-c`: path to the cover of story. Default: empty string
- `-p`: the name of the publisher of story. Default: empty string
- `-s`: chapter index to start crawl. Default: crawl from the first chapter
- `-i`: limit total chapters to crawl. Default: 0 - no limit
- `url`: the url of story

## Cover

- The longest side of cover image is **at least 500px**.
- The **ideal aspect ratio** is 1.6
- The aspect ratio of **kindle Oasis 2** is 1.33
- Use [calibre](https://calibre-ebook.com/) to keep cover image:
	- connecte your kindle to computer
	- open Calibre then import the created ebook (epub file) to it.
	- select your ebook, then click on **Send to device** in menu.
	- select format **azw3** to send the ebook to your kindle.
	- eject device, turn on wifi of your kindle, waiting for cover disappear
	- reconnect your kindle to PC, and use Calibre to eject it.

> If the cover image does not appear:
> - Check the size of cover image.
> - Try to use another format of this image.

## Resources

- [Epub Validator](https://www.ebookit.com/tools/bp/Bo/eBookIt/epub-validator)
- [EPUB Validator (beta)](http://validator.idpf.org/)
- [XHTML Validator](https://validator.w3.org/nu/#file)

## Shell scrapy

```
scrapy shell [url]
```

1. Display help

```
shelp()
```

2. Do a POST request

```
req = scrapy.FormRequest(url=[new_url], formdata=[your_data])
fetch(req)
```

3. Fetch a new url

```
fetch(new_url)
```

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