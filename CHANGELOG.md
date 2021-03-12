# Change Log

All notable changes to this project will be documented in this file.

## 2021-03-12

### Changed

- crawl.py, TruyenFull, VnThuQuan: replaced parameter `end_chapter` by `limit`.
- TLib: add method `correctWords` for words correction.

## 2021-02-11

### Changed

- TLib: capitalize the first paragraph of content in methods `addDropCap`

## 2021-02-11

### Changed

- TLib: back to use manual code in methods `cleanTags`
- TruyenFull: add "ads" in removal symbols list

## 2021-02-09

### Changed

- TruyenFull:
    - if output_dir is empty, set it to `url2epub`
    - if source is empty, set it to `truyenfull.vn`
    - replace the condition `end_chapter=-1` to crawl all chapters by condition `not end_chapter`
- TLib:
    - change method name `addDropcap` to `addDropCap`
    - use BeautifulSoup instead of manual code in methods `cleanTags`, `br2p`, `addDropCap`

### Added

- VnThuQuan: crawl from vnthuquan.net

## 2021-02-07

### Added

- add cover, semantic table of contents to epub file.