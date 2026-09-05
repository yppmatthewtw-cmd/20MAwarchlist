# 20MA Uptrend Watchlist

美股 20MA 上升趨勢觀察名單 —— 全美上市普通股掃描，篩選「MA 仍在向上 + 一底高於一底」的股票，
並以 **VCP 收縮指數**（volatility contraction，越收縮排名越高）排序。

## 報告（`reports/`）

| 版本 | 內容 |
|------|------|
| R1.00 | S&P 500 掃描 · 單頁（1 個月 20MA），按 20MA 月斜率排序 |
| R2.01 | 全美掃描 · 5 頁：總覽（爆發潛力分數）＋ 1星期(10MA)/2星期/1個月/2個月(20MA) 四個時間框，各頁按 VCP 指數取 top 50；Ticker 連結開 TradingView chart layout |
| R3.00 | R2 基礎上新增 **底部確定性 7 項量化**（突破中間高位/回補幅度/守底時間/下試量縮/回撤遞減/相對強度/均線位置）；排名改為 **綜合分數 = 0.5×VCP + 0.5×確定性**；每隻上榜股加 **下跌→回升原因** 欄（[Bigdata.com](https://bigdata.com) 新聞索引＋公開網頁逐隻研究，附信心度）及 2026年6–8月市場背景卡 |
| R4.00 | R3 分欄互動版：VCP／確定性分拆兩欄＋TOP BAR「按VCP／按確定性」排序；7 項確定性證據分拆 7 個可排序欄；下跌/回升原因分拆兩欄（濃縮，🔥 高亮市場熱炒 news-driven 催化）；欄闊可拖拉調整 |
| R5.00 | R4 分層版（含分層缺陷修正）：每個時間框拆成 **大型股(≥$10B)／中型股($2B–$10B)／小型股(<$2B)** 三個獨立 top 50 榜，共 12 個分層頁＋總表（217 隻不重複）；新增市值欄（可排序）、**🔥 熱炒 news-driven 催化劑獨立欄**＋每頁頂部可點擊橫幅 |
| R6.01 | **數據更新至 2026-08-31 收盤**。改用真實日線 OHLCV 鏡像（[natezone/market-tracker](https://github.com/natezone/market-tracker)，收市後推送）取代 Nasdaq 快照重建；宇宙改為 **S&P 1500 綜合指數**（1,504 隻），分層改用 **指數成分**（S&P 500／400／600 = 大／中／小型股）；R6.01 起改為 **固定深色模式**（不再跟隨瀏覽器主題）|
| R7.00 | **數據更新至 2026-09-01 收盤**。快照鏡像恢復運作，**回復全美掃描**（7,396 條序列／6,874 隻有 9/1 收盤／3,005 隻合資格，上榜 208 隻）；分層回復市值門檻；8/31 鏡像停擺日以日線鏡像補回 1,500 隻；抽取管道新增「收市後 commit」防護，自動剔除未完成的盤中 bar |

| AI Sector R5.00 | **數據推進至 2026-09-04 收盤 + Yahoo Finance 第二數據源**（與 SubSector R4.00 同一引擎與合併規則）。111 隻美股／ADR 全部有真實 OHLCV（合併 75、Yahoo 獨有 36），SBGSY／TCEHY 亦補齊、未計入清零；13 隻 ADR 由「只計方向」變為完整量能基準。**修正 R4.00 APH 2 拆 1 未調整**（D5 連接器 09-02 籃子報酬曾顯示 −26.9%）；QCOM 股息調整差異改用 Yahoo。交叉核對：快照 vs Yahoo 逐日中位 0.0000%；日線鏡像 vs Yahoo 299 個收盤中位 0.0000%。獨立重算 0 problems |
| AI Sector R4.00 | **數據推進至 2026-09-03 收盤**（視窗 08-28 → 09-03；9/4 收盤所有可達鏡像尚未發佈，唔以盤中價冒充）。沿用 SubSector R3.00 嘅 critical review 修正：① 缺 20 日量能基準嘅成分股唔再剔除 —— ARM／ASML／ASX／BABA／BIDU／CAMT／CCJ／IREN／NBIS／POET／SIMO／TSEM／TSM 共 13 隻歸位（方向計分、量能中性、個股虛線底），計分美股 96 → **109**，8 個籃子改變（AA1 Neo Cloud 2→4、D2 矽光 1→3、B3 先進封裝 5→7…），**AA3 中國雲**由「數據不足」變為可計算（33 組）；② 40% 單一股票硬上限（迭代 water-filling）；③ 08-31 內插成交量視為未知；④ 頁面文字修正 —— R3.00 嘅 H1 仍寫 R1.00、第 4 頁標題仍寫「8/26–9/1」、頁尾「數據終點」係 R2 舊文並話 TSM／ASML／BABA「數據不足」。成分股欄提示改為逐股顯示量能未知日數；未計入淨得 SBGSY、TCEHY（OTC ADR）。無紅字標示（依指示）；獨立重算 0 problems |
| AI Sector R3.00 | 在「AI 小群組」與「大分類」之間新增 **成分股 · 按資金流向排序**欄：每組的美股／ADR 成分股逐隻計算 5 日資金流向分（與群組同一條公式、同一組近日較重權重），**由流入最多排到流出最多**，**綠底＝資金流入、紅底＝資金流出**（深淺代表強度，灰＝中性），代號右側顯示該股流向分，滑鼠停留可見淨額估算與 5 日報酬。原「成分股（美股／ADR）」欄改為「未計入成分股」，只保留因數據不足或非美股而未計入的部分。資料與計分邏輯不變（08-27 → 09-02，32 組可計算／9 組不可） |
| AI Sector R2.00 | **數據推進至 2026-09-02 收盤**（視窗 08-27 → 09-02）。09-02 全宇宙收盤由 09-03 盤中快照的 `price − price_change` 取得，與日線鏡像 1,498 隻交叉核對中位偏差 0.0000%；該快照成交量屬 09-03 partial，故非日線鏡像覆蓋的股票 09-02 **量能項設為中性**並標示「量?」，不以估算量冒充。新增 **穩健分**（z×√(n/(n+2))，樣本細者向中性收斂）、**資金強度**（淨額/成交額，去規模）、**可信度**（美股樣本數）與**廣度**（籃子內超額報酬為正比例）；28 個小群組名次有變 |
| AI Sector R1.00 | **AI 產業鏈資金流向**：以附件 `Dashboard_R15.6_0828_hk16.15.html` 嘅 **41 個 AI 小群組**（8 大分類：運算核心／Neo Cloud／製造／記憶體儲存／互連／系統整合／基礎設施／雲端應用）為對象，沿用 SubSector R1.01 完全相同嘅計分引擎與版面。**只納入美股上市股票及 US ADR**（全球成分 224 隻中美股 111 隻，實際計分 96 隻）；成分股全屬中國A股／台股／日韓／歐洲掛牌嘅 9 個小群組列出但唔參與排名。四頁：總覽／每日矩陣／8 大分類匯總／**象限背離**（儀表板 8/27 RS 象限 vs 8/26–9/1 實測資金流）|
| SubSector R4.00 | **數據推進至 2026-09-04 收盤**（視窗 08-31 → 09-04）+ **加入 Yahoo Finance 第二數據源**：兩個鏡像至建置時仍未發佈 09-04 收盤，改由 GitHub Actions runner（`.github/workflows/fetch_yahoo_eod.yml`，容器本身連唔到 Yahoo）以 yfinance 拉取 546 隻代表股未調整日線並提交 `data/yahoo/`，再連同 10MA-watchlist 倉庫同法拉取嘅 2,758 隻，合共 2,811 隻。每隻股票日線鏡像為主、Yahoo 補其未有嘅交易日，最近 15 個共同收盤中位偏差 ≤0.5% 先合併，否則整段改用 Yahoo（APH、BF.B 及 15 隻有股息調整差異嘅日線鏡像股）。**交叉核對**：快照序列 vs Yahoo 逐日中位偏差 0.0000%（09-02／09-03 反推收盤 100% 喺 0.5% 內）；日線鏡像 vs Yahoo 1,623 個收盤中位 0.0000%。**修正 R3.00 APH 2 拆 1（09-02）未調整**（快照序列 $163.18→$80.04 被當成跌 51%）。491 隻全部有真實 OHLCV（合併 375、Yahoo 獨有 116），「量?」「無量基準」「僅收盤」標記全部消失；全巿中位基準改為合併宇宙（~2,850 隻／日）。獨立重算（含 Yahoo 合併規則）0 problems |
| SubSector R3.00 | **數據推進至 2026-09-03 收盤**（視窗 08-28 → 09-03）。9/4 收盤未納入：建置時（09-05 11:54 HKT）所有可達鏡像都未發佈 09-04 收盤價（日線鏡像只推送成交量；Nasdaq 快照最新一筆為 09-04 10:24 ET 盤中價）。**對 R2.00 嘅 critical review 修正 7 項**：① 40% 單一股票上限被重新歸一化抵銷（最大實際權重可達 66.7%）→ 迭代 water-filling，實際權重 ≤40%；② 缺 20 日量能基準嘅代表股唔再剔除（TSM／ASML／ARM／TEAM／SHOP／NVO／DEO／INFY／TECK／CCJ／AEM／KGC／UUUU／WCN 等 33 隻歸位，08-27 前收由 08-28 收市後快照補回），樣本 457 → **491**，25 個籃子改變（鈾與核燃料 1→5、晶圓代工 2→4、黃金 3→6…）；③ 08-31 內插成交量改視為未知（B=0、標「量?」），只有 13 隻真正內插收盤標「內插」；④ BF.B 對上日線檔 BF-B；⑤ 工作簿說明文字唔再當 ticker；⑥ 混合來源籃子新增 OHLC 覆蓋率；⑦ R2.00 title／H1 仍寫 R1.01、頁尾「數據終點」段係 R1.01 舊文 → 重寫。同一視窗下引擎修正令名次中位變動 1 位（最大 42）；新交易日本身令名次中位變動 15 位。無紅字標示（依指示）；獨立重算 0 problems |
| SubSector R2.00 | **數據推進至 2026-09-02 收盤**（視窗 08-27 → 09-02，順帶移走 08-26 估算日）。9/3 未納入：日線鏡像當日只出到 1,003/1,503 隻、亦無全宇宙快照。09-02 全宇宙收盤由 09-03 盤中快照的 `price − price_change` 取得（與日線鏡像 1,498 隻交叉核對，中位偏差 0.0000%）；該快照成交量屬 09-03 partial，故非日線鏡像覆蓋的股票 09-02 **量能項設為中性**並標示「量?」（34 個子板塊受影響）。新增 **穩健分**、**資金強度**、**可信度**、**廣度**（與 AI Sector R2.00 同一套指標）；109 個子板塊名次有變 |
| SubSector R1.01 | 加入**版面切換按鈕**（自動／☀淺色／🌙深色）：調色盤改為 token 制 —— `:root` 定義完整淺色，`@media (prefers-color-scheme:dark)`（以 `:root:not([data-theme="light"])` 保護）及 `:root[data-theme="dark"]` 覆寫深色，資金流向色階、熱度色、陰影、邊框全部跟住換色；選擇存 localStorage，並用 MutationObserver 令頁內選擇唔會被檢視器主題覆寫 |
| SubSector R1.00 | **子板塊資金流向**（新產品線）：以附件工作簿 `US_Market_Sector_SubSector_HeatMap_R2_20260903.xlsx` 嘅 **111 個子板塊**為對象，用代表股籃子對 **2026-08-26 → 09-01 五個交易日**逐日打資金流向分 （方向 tanh(超額報酬/2%) ＋ Chaikin 收盤位置 ＋ 成交額量能放大，成交額加權、每日橫向百分位 0–100）；四頁：總覽／每日矩陣／GICS 板塊匯總／熱度背離。註：非真實基金流數據，屬價量代理指標 |

| R8.00 | **R7 經 7 組獨立審視（併購套利／數據完整性／新聞質量／篩選邊界／版面／市場背景／方法論）後修正**，所有相對 R7 嘅變更喺報告內以紅色標示。數據修補：快照鏡像漏咗 03-18、08-11、08-12、08-26、08-31 共 5 個交易日，R7 以前值填補（假平台、VCP 高估）；R8 逐隻以真實日線／9/1 快照隱含官方收盤／線性內插修補，並校正 8/27 未完成成交量、回溯調整 0 隻未調整拆股。新規則：⑪ 併購套利／價格釘死股剔出排名（11 隻，獨立方框列出）· ⑬ 封閉式基金／royalty trust 剔出（9 隻）· ⑭ 同一發行人多類別只保留一個（1 隻）· ⑤ 收緊：現價必須仍高於最後一個底（剔除 187 隻）。新聞：糾正 THC／MAN／RCEL／PESI／ITGR／ICE 等條目，🔥 唔再標示併購套利股，回落 ≥10% 加註近況，重查 24 隻低信心／過時條目。上榜 190 隻（大65／中62／小63）|

報告為獨立 HTML，直接用瀏覽器開啟；頁面切換內建。R6.01 起版面固定深色（深色調色板直接定義在 `:root`，不設主題切換）。

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
6. **確定性分數（R3，0–100）**：1.1 突破中間高位（最近兩底之間高位已被升穿？25%）· 1.2 回補幅度（收復最後跌幅 %，10%）·
   1.3 時間（最後底部已守日數，15 日滿分；曾跌穿×0.25，15%）· 2.1 下試量縮（近15日跌日/升日成交量比，15%）·
   2.2 回撤遞減（末段/首段跌幅比，10%）· 2.3 相對強度（21日回報−全體中位，10%）· 2.4 均線位置（價>20MA＋20MA>50MA＋50MA向上，15%）；
   百分位項以全體合資格股票為基準。
7. **排名（R3 各時間框頁）= 綜合分數 = 0.5×VCP + 0.5×確定性**（確定性做評分欄，唔係過濾）；
   **爆發潛力分數（總覽頁）** = 0.4×VCP + 0.4×確定性 + 0.2×覆蓋度（R2 為 0.7×VCP + 0.3×覆蓋度）。
8. **市值分層（R5）**：大型股 ≥$10B、中型股 $2B–$10B、小型股 <$2B（含通過流動性門檻的微型股）。
   每個時間框各自分三層、每層獨立取 top 50，避免細價股被大價股擠走。
   **快照無市值數據的非普通股證券**（優先股／存託股如 ORCL^D、MTB^J、KKR^D，以及 SPAC、封閉式基金）
   不會當成小型股，已剔出分層頁——本次 8 隻；三層合資格數 ＋ 剔除數 ＝ 該時間框原總數（已驗證守恆）。
9. 已知設計註記：下試量縮以近15日跌/升日成交量做代理（未必正好覆蓋對前底嘅實際下試）；回撤遞減只比較末段對首段。

10. **R8 新增／收緊**：
    - ⑤ 收緊：數據終點收盤必須仍高於最後一個底（現價已跌穿最後底者，一底高於一底已失效，剔除；盤中曾跌穿但收復者保留並標 ⚠）。
    - ⑪ 併購套利／價格釘死：已公布現金收購（或現金為主）而股價釘住作價嘅股票，VCP 收縮屬假象、冇突破空間，剔出排名及 top 50，改列各頁「🚫 併購套利」方框（連原可排名次）。判定＝新聞確認清單（`data/deal_pinned8.json`）＋數據規則 A1（15 日收盤區間 <2% 且中位日變動 <0.25%）／A2（60 日內單日跳升 ≥15% 後 ≥5 日區間 <3%）。
    - ⑫ 缺快照交易日修補：見「數據來源」R8 段。
    - ⑬ 封閉式基金／市政或定期信託／royalty trust 剔出分層頁（淨值錨定，波幅收縮屬結構性）；REIT／銀行／MLP／BDC 保留。
    - ⑭ 同一發行人多類別股份只保留流動性較高嘅一個。
    - 總表走勢／MA 改取 1個月（20MA）分頁數值；新增 ⚡ 事件驅動（30 日內單日 ≥20% 或 20 日 ≥40%）、「單日跳升推動」（1星期頁）、「MA將轉向」、守底「剛確認」標示。

## 數據來源與重建

環境內可達的數據源只有 GitHub 公開 repo（其餘行情站與 API 一律被網絡政策封鎖）。

**R8（現行）** — R7 雙來源合成之上嘅修補（`scripts/extract_series8_patch.py`）：

- 審視發現快照鏡像除 8/31 外仲漏咗 03-18、08-11、08-12、08-26、08-31（無 commit），R7 對全宇宙以前值填補（複製收盤及成交量）。R8 逐隻修補：有 natezone 真實日線者用真實 bar（按最近真實快照日嘅 series/natezone 收盤比例校正除息調整）；8/31 其餘股票用 9/1 快照隱含嘅官方收盤（price − price_change，5,337 隻，修補前中位偏差 1.06%）；其他缺日線性內插、成交量取前後平均。
- 8/27 快照於 16:05 ET 拍攝，成交量未完成（中位只有真實嘅 0.62×）：有真實 bar 者用真實成交量，其餘按中位比例放大。
- 未調整拆股：單日收盤比例落喺標準拆股比例 ±1.5% 內，且經 natezone 已調整日線或快照隱含股數確認者，回溯調整價格及成交量（0 隻：）。
- 每個估算 bar 記錄於 `meta8`，報告以「估n」標示；底部若落喺估算 bar 會另外警示（本版 0 隻）。
- 審視原始發現見 `data/review8_findings.json`。

**R7** — 雙來源合成，以全美快照為主線：

- 主線價格/成交量：zyhe16/top-us-stock-tickers 每日 Nasdaq 快照（v2 契約 `data/v2/tickers.csv`，7,153 行），
  逐 commit 依收市時間映射至交易日；該鏡像 2026-08-31 因排程故障無快照，改由下述日線鏡像補回 1,500 隻，其餘以前值填補。
- 補充/校驗：natezone/market-tracker 的真實日線 OHLCV。
- **盤中防護**：`extract_series7.py` 要求來源 commit 晚於該日 16:00 ET 收市，否則自動剔除未完成的當日 bar
  （2026-09-01 該鏡像只出到盤中快照，防護已實測生效）。

**R6** — 只用日線鏡像（S&P 1500 宇宙）：

- [natezone/market-tracker](https://github.com/natezone/market-tracker)：每交易日 14:00 及 22:00 UTC 由 yfinance 更新，
  `data/UNIFIED/history/<TICKER>.csv`（`Date,Open,High,Low,Close,Volume`），涵蓋 S&P 1500 綜合指數約 1,560 隻、約 3 年歷史。
  遇上游跑漏某一日（如 2026-08-28），由上一個 commit 還原。
- 指數成分／GICS 分類／公司名：同 repo 的 `data/SP500|SP400|SP600/latest_metrics.csv`。
- 市值：由 Nasdaq 快照推算股數（市值 ÷ 收盤），再以最新收盤重估。

**R2–R5（歷史版本）** — 逐 git commit 重建每日收盤/成交量序列：

- 價格/成交量：[zyhe16/top-us-stock-tickers](https://github.com/zyhe16/top-us-stock-tickers)
  每日 Nasdaq 快照（`tickers/all.csv` + `tickers/sp500.csv`），依 commit 時間映射至美股交易日；
  無快照的交易日以前值填補；尾日收盤以官方 net-change 校正。
- GICS 類別（S&P 500）：[klaywang24/market-chronicle](https://github.com/klaywang24/market-chronicle)
- 交易所歸屬：[irachex/open-stock-data](https://github.com/irachex/open-stock-data)

抽樣驗證：R2 重建序列與 R1 報告的底部價格 10/10 完全一致，20MA 平均偏差 0.18%；R6 的 yfinance 日線與 R5 的 Nasdaq 快照兩條獨立血緣交叉核對，2,932 個重疊收盤價中 2,926 個（99.8%）偏差 <0.5%、中位偏差 0.000%；R7 的 2026-09-01 收盤與獨立 Yahoo 日線抽樣 30 隻全部吻合、偏差 0.000%；
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

`data/screen_results8.json` 為現行版本（數據至 2026-09-01 收盤）的完整篩選輸出；`data/screen_results.json` 為 R2 原始輸出。

## 子板塊資金流向（SubSector R1）

```bash
python3 scripts/extend_series9.py          # 由 series8.pkl 延伸至 2026-09-02 -> series9.pkl
# Yahoo 第二數據源：GitHub Actions → data/yahoo/eod_<start>_<end>.csv.gz（workflow_dispatch fetch_yahoo_eod.yml）
python3 scripts/subsector_flow4.py         # R4 引擎：日線鏡像 ∪ Yahoo 合併、交叉核對、視窗至 09-04 -> data/subsector_flow4.json
python3 scripts/build_subsector_report4.py # 產生 R4 HTML
python3 scripts/verify_subsector_flow4.py  # R4 獨立重算（含 Yahoo 合併規則，0 problems）
python3 scripts/extend_series10.py         # series10.pkl：補 2026-09-03 收盤 + 08-28 新增股票嘅 08-27 前收
python3 scripts/subsector_flow3.py         # R3 引擎（硬 40% 上限、無基準股票 B=0、逐日量能未知）-> data/subsector_flow3.json
python3 scripts/build_subsector_report3.py # 產生 R3 HTML 報告（由 make_build_subsector_report3.py 從 R2 builder 衍生）
python3 scripts/verify_subsector_flow3.py  # R3 獨立重算驗證（0 problems）
python3 scripts/subsector_flow2.py         # 111 子板塊 x 5 日資金流向（R2）-> data/subsector_flow2.json
python3 scripts/subsector_flow.py          # R1 版本（視窗至 09-01）
python3 scripts/build_subsector_report2.py # 產生 R2 HTML 報告
python3 scripts/build_subsector_report.py  # R1 版本
python3 scripts/verify_subsector_flow2.py  # R2 獨立重算驗證（0 problems）
python3 scripts/verify_subsector_flow.py   # R1 獨立重算驗證
```

- 子板塊定義、代表 Tickers、熱度分與 LEADING INDICATOR 取自附件工作簿（`data/subsectors.json`，111 列）。
- 價量來源：natezone/market-tracker 真實日線 OHLCV 為主（有日內高低價，可算 Chaikin 收盤位置），
  其餘以 Nasdaq 快照重建序列（`series8.pkl`）補足，只有收盤與成交量。
- 工作簿列出但鏡像無數據嘅股票（外國 ADR 如 TSM/ASML/NVO，或已除牌如 K/X/CEIX）以人手核對嘅同業補充樣本頂替；
  工作簿無列 ticker 嘅 2 個子板塊用代理樣本。樣本數與品質標示喺報告「樣本」欄。
- **限制**：環境內無法取得 ETF 申購贖回／13F／委託簿數據，「資金流向」全部由價格、成交量與收盤位置推算。

## AI 產業鏈資金流向（AI Sector R1）

```bash
python3 scripts/extend_series9.py    # 由 series8.pkl 延伸至 2026-09-02 -> data 用 series9.pkl
python3 scripts/ai_flow5.py          # R5：Yahoo 第二數據源、視窗至 09-04 -> data/ai_flow5.json
python3 scripts/build_ai_report5.py  # 產生 R5 HTML
python3 scripts/verify_ai_flow5.py   # R5 獨立重算（0 problems）
python3 scripts/ai_flow4.py          # R4：SubSector R3 引擎修正（硬上限、無基準股票 B=0、逐日量能未知）-> data/ai_flow4.json
python3 scripts/build_ai_report4.py  # 產生 R4 HTML 報告（由 make_build_ai_report4.py 從 R3 builder 衍生）
python3 scripts/verify_ai_flow4.py   # R4 獨立重算驗證（0 problems；另檢查成分股欄排序與無基準標記）
python3 scripts/ai_flow3.py          # R3：另計每隻成分股的 5 日流向 -> data/ai_flow3.json
python3 scripts/ai_flow2.py          # R2 版本 -> data/ai_flow2.json
python3 scripts/ai_flow.py           # R1 版本（視窗至 09-01）-> data/ai_flow.json
python3 scripts/build_ai_report3.py  # 產生 R3 HTML 報告（含成分股資金流向欄）
python3 scripts/build_ai_report2.py  # R2 版本
python3 scripts/build_ai_report.py   # R1 版本（CSS/JS 取自 SubSector 報告，兩份保持同一套系統）
python3 scripts/verify_ai_flow3.py   # R3 獨立重算驗證（另檢查 96 個成分股標籤的排序、色階與連結）
python3 scripts/verify_ai_flow2.py   # R2 獨立重算驗證（0 problems，另檢查穩健分/強度/廣度一致性）
python3 scripts/verify_ai_flow.py    # R1 獨立重算驗證
```

- 分類、成分股、RS 象限、RSI 與 1週／1月／3月報酬全部取自附件儀表板（`data/ai_groups.json`，41 組）；
  RS 象限為儀表板 **2026-08-27** 數值，資金流向計分視窗為 **2026-08-26 → 09-01**，兩者時點不同，正好用於背離分析。
- **只計美股／US ADR**：儀表板本身已用 ADR 代號表示有 ADR 的外國公司（台積電＝TSM、ASML＝Nasdaq ADR）；
  帶交易所後綴（.SS/.SH/.SZ/.TW/.T/.KS/.DE/.AS/.VI）的股票一律排除，不以其他股票代替。
- 計分公式與 SubSector R1.01 完全一致（`ai_flow.py` 由 `subsector_flow.py` 轉換而成，只換籃子來源）。
- **限制**：AI 供應鏈重心在亞洲，美股樣本偏薄（籃子中位數 2 隻，16 組僅 ≤2 隻），各行已標示美股數／全球數／覆蓋率。

> 本項目只係篩選工具，唔係投資建議。
