# 台灣上市上櫃股票分析

這是一個台灣上市上櫃股票分析的專案，預計會將股票的基本面、技術面、籌碼面、消息面以及各種財經新聞納入分析之考量，以過去經驗推測一檔股票未來的漲跌勢。此專案之工作量龐大，估計在工作之餘使用兩年時間完成。

## 當前專案進度

1. 抓取台灣上市上櫃的股票清單並存入自建的 MySQL 資料庫 (20210426)
2. 根據抓到的台灣上市上櫃股票清單去爬每支股票的歷史紀錄 (20210428)

## 使用步驟

使用 `git clone` 指令下載本專案。

```shell
$ git clone https://github.com/Chris-WenYuan/investment-strategy.git
```

使用 `cd` 進入專案資料夾中。

```shell
$ cd investment-strategy
(investment-strategy)$ 
```

利用 `requirements.txt` 安裝相關套件。

```shell
(investment-strategy)$ pip install -r requirements.txt
```

`index.py` 為本專案的主程式，直接執行即可。

```shell
(investment-strategy)$ python index.py
```

![](https://i.imgur.com/bvNKrcD.png)
