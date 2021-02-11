# Change Log

All notable changes to this project will be documented in this file.

## 2021-02-11

### Changed

- [TLib](TLib.py):
    - back to use manual code in methods `cleanTags`
    
- [spider truyenfull](spider/TruyenFull.py):
    - add "ads" in removal symbols list

## 2021-02-09

### Changed

- [spider truyenfull](spider/TruyenFull.py):
    - if output_dir is empty, set it to `url2epub`
    - if source is empty, set it to `truyenfull.vn`
    - replace the condition `end_chapter=-1` to crawl all chapters by condition `not end_chapter`
- [TLib](TLib.py):
    - change method name `addDropcap` to `addDropCap`
    - use BeautifulSoup instead of manual code in methods `cleanTags`, `br2p`, `addDropCap`

### Added

- [spider vnthuquan](spider/VnThuQuan.py): crawl from vnthuquan.net

## 2021-02-07

### Added

- add cover, semantic table of contents to epub file.