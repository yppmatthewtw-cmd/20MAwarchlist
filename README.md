# 20MA Uptrend Watchlist

美股 20MA 上升趨勢觀察名單 —— 全美上市普通股掃描，篩選「MA 仍在向上 + 一底高於一底」的股票，
並以 **VCP 收縮指數**（volatility contraction，越收縮排名越高）排序。

## 報告（`reports/`）

| 版本 | 內容 |
|------|------|
| R1.00 | S&P 500 掃描 · 單頁（1 個月 20MA），按 20MA 月斜率排序 |
| R2.01 | 全美掃描 · 5 頁：總覽（爆發潛力分數）＋ 1星期(10MA)/2星期/1個月/2個月(20MA) 四個時間框，各頁按 VCP 指數取 top 50；Ticker 連結開 TradingView chart layout |

報告為獨立 HTML，直接用瀏覽器開啟；頁面切換、light/dark 主題內建。

## 篩選規則（R2）

1. **Universe**：全美上市普通股（Nasdaq/NYSE/AMEX），存續至數據終點、歷史 ≥90 交易日、
   價格 ≥$2、20 日中位成交額 ≥$1M。
2. **MA 上升**：各頁以自己的時間框比較 —— PAGE 2：10 天 MA 較 5 個交易日前高；
   PAGE 3/4/5：20 天 MA 分別較 10 / 21 / 42 個交易日前高；且 MA 最後 3 日逐日上升、期內 ≥70% 日子上升。
3. **「底」**：某日收盤係 ±3 日內最低，且 3 日前收盤高過佢（跌咗約三天）、3 日後收盤高過佢（回升約三天）；
   相鄰 ≤3 日重複底去重。
4. **一底高於一底**：最後 45 個交易日內 ≥2 個底且逐個遞升；最近一個底喺 25 個交易日內。
5. **VCP 指數（0–100）**：10日波幅/前30日波幅（35%）＋近10日高低區間佔價（25%）＋
   近10日成交量/前30日成交量（20%）＋近15日區間/前30–45日區間（20%），四項以全體合資格股票百分位合成。
6. **爆發潛力分數（總覽頁）** = 0.7 × VCP 指數 + 0.3 × 覆蓋度（達標時間框數 ÷ 4 × 100）。

## 數據來源與重建

環境內可達的數據源為 GitHub 每日鏡像，逐 git commit 重建每日收盤/成交量序列：

- 價格/成交量：[zyhe16/top-us-stock-tickers](https://github.com/zyhe16/top-us-stock-tickers)
  每日 Nasdaq 快照（`tickers/all.csv` + `tickers/sp500.csv`），依 commit 時間映射至美股交易日；
  無快照的交易日以前值填補；尾日收盤以官方 net-change 校正。
- GICS 類別（S&P 500）：[klaywang24/market-chronicle](https://github.com/klaywang24/market-chronicle)
- 交易所歸屬：[irachex/open-stock-data](https://github.com/irachex/open-stock-data)

抽樣驗證：R2 重建序列與 R1 報告的底部價格 10/10 完全一致，20MA 平均偏差 0.18%；
另經 6 組獨立代理人對抗性驗證（lineage / 頁面條件 / VCP 數學 / 規格合規）。

限制:快照只有收盤價與成交量（無日內高低價），VCP 以收盤/成交量計算;價格未除息調整;
外國註冊而非 S&P 500 的美國上市股票（部分 ADR）缺完整歷史，未納入掃描。

已核實的邊界情況（均不影響任何上榜結果）：08-27 官方校正設 ±5% 合理性護欄，37 隻保留快照價
（全部不合資格）；個別股票連續缺 >3 個快照日會整隻剔除而非斷點續接，受影響的 25 隻中僅 NTWO
勉強接近門檻（中位成交額 $73K，遠低於 $1M）；commit 時間映射已按美國夏令時間精確處理。

## 重新產生報告

```bash
# 先 clone 三個數據 repo（路徑可用環境變數覆蓋：TICKERS_REPO / CHRONICLE_REPO / OPENSTOCK_REPO）
export WORK_DIR=./data
python3 scripts/extract_series.py   # 由 git 歷史重建序列 -> data/series2.pkl
python3 scripts/screener.py         # 篩選 + VCP -> data/screen_results.json
python3 scripts/build_report.py     # 產生 HTML 報告
```

`data/screen_results.json` 為本次（數據至 2026-08-28 收盤）的完整篩選輸出。

> 本項目只係篩選工具，唔係投資建議。
