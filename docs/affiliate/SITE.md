# アフィリエイト運用メモ — マン管マスター（mankan-master）

手順の正本: [exam-site-shell `multi-site-affiliate-workflow.md`](https://github.com/takkenshiken2026-sudo/exam-site-shell/blob/main/docs/affiliate/multi-site-affiliate-workflow.md)

## サイト情報

| 項目 | 値 |
|------|-----|
| site-id | `mankan-master` |
| ドメイン | https://mankan-master.jp |
| 棚卸し日 | 2026-06-12 |
| テンプレ drift | ok=77 / drift=0 / total=77（フェーズB同期後） |
| デプロイ | GitHub Actions（`main` push → `build_all.py` → Pages） |

---

## フェーズA 棚卸し結果（2026-06-12）

### サマリー

| 指標 | 値 |
|------|-----|
| アフィリエイト行（CSV） | 10 |
| `content_status=published` | **4** |
| **ASPリンク済み（CSV判定・buildable）** | **3** |
| **比較記事 HTML 生成** | **3**（hub付き3本。`free-vs-paid` は ASPなしで skip） |
| brief YAML | 3 |
| `images/affiliate/` | 9 webp |
| `guideIndexPicks` | **未設定** |
| 通常ガイド published | 126 |
| 通常ガイド → 比較記事（`related_links`） | **0 / 126** |
| 通常ガイド → 比較記事（本文 slug） | **0 / 126** |

### 重要な発見（要修正）

1. **エンジンが旧版** — `tools/build_article_pages.py` に `affiliate-product-hub` なし。`guide_index_picks_ui.py`・`affiliate_brief_loader.py` も未同期。**フェーズB 同期が最優先**。
2. **ASP 付き3本は CSV に URL あり**だが、再ビルド後も hub・要点サムネが出ない（現行ビルダー限界）。同期後に hub 付き HTML へ差し替え必要。
3. **`affiliate-free-vs-paid-study` は published だが ASP なし・HTML なし** — 収益導線記事（内部リンクのみ）。`affiliate-dokugaku-goukaku-hokan` 相当。比較 hub 対象外。
4. **講座比較が未整備** — `affiliate-online-course-compare` は draft・brief なし・ASP 未確定。`guideIndexPicks` の「講座」スロットのブロッカー。

---

## 公開済み比較記事（CSV）

| slug | brief | ASP（CSV） | HTML | hub | 備考 |
|------|-------|------------|------|-----|------|
| `affiliate-textbooks-recommend` | あり | Amazon×3 | あり | なし | 手書き 2026-06-04。本文に「広告・アフィリエイト」表記あり（v2 で除去候補） |
| `affiliate-problem-books` | あり | Amazon×3 | あり | なし | 同上 |
| `affiliate-mock-exam-materials` | あり | Amazon×3 | あり | なし | 一問一答・速習（フェーズFの4本目候補） |
| `affiliate-free-vs-paid-study` | なし | **なし** | **なし** | — | 導線専用・収益リンクなし（`asp=internal`） |

## draft（次に公開候補）

| slug | brief | 内容 | ブロッカー |
|------|-------|------|------------|
| `affiliate-online-course-compare` | なし | 本文かなり執筆済み | brief + ASP（A8 等）+ `published` |
| `affiliate-correspondence-course` | なし | 本文かなり執筆済み | 同上（オンラインと役割分担要整理） |
| `affiliate-beginner-material-set` | なし | 本文執筆済み | Amazon URL + brief |
| `affiliate-cram-school` | なし | 本文執筆済み | ASP 確定まで触らない |
| `affiliate-retake-short-course` | なし | 短文 | ASP 確定まで触らない |
| `affiliate-qualification-support-service` | なし | 短文 | ASP 確定まで触らない |

---

## guideIndexPicks

- **現状:** `site-config.json` にキーなし
- **目標:** 公開比較記事が **講座+テキスト+問題集** そろってから `grid-3` で3枚導入
- **想定 href（案）:**

| kind | href | image（案） | 状態 |
|------|------|-------------|------|
| 講座 | `affiliate-online-course-compare/` | 要用意 | **draft・ASP 未確定** |
| テキスト | `affiliate-textbooks-recommend/` | `mankan-book-4300120218.webp` | 公開済み |
| 問題集 | `affiliate-problem-books/` | `mankan-book-4300120331.webp` | 公開済み |

代替案: 3枚目を `affiliate-mock-exam-materials/`（一問一答）にする場合は設計メモに明記すること。

---

## 通常ガイド導線

- **現状:** 0 / 126（未接続）
- **優先接続候補（slug）:** `self-study-start`, `textbook-selection`, `problem-book-selection`, `correspondence-course-guide`, `study-plan-beginner`, `past-questions-by-year`, `past-questions-by-field`
- **除外候補:** `pass-rate`, `after-pass-procedure`, `career-after-qualification`, `exam-venue-and-region`, `compare-similar-qualifications`

### 意図マッピング（フェーズE 用）

| 意図 | 比較記事 |
|------|----------|
| テキスト・教材選び | `affiliate-textbooks-recommend` |
| 過去問・演習 | `affiliate-problem-books` |
| 一問一答・直前 | `affiliate-mock-exam-materials` |
| 通信・オンライン講座 | `affiliate-online-course-compare`（公開後） |
| 独学・無料/有料判断 | `affiliate-free-vs-paid-study`（ASP なし・内部導線） |

---

## 画像

- ディレクトリ: `images/affiliate/` — **9 webp**（TAC・LEC・早稲田 W マスター系）
- 講座サムネ（jpg/webp）: **未取得**
- 要更新: 価格は brief 上 2026-06-04 確認。公開前に Amazon で再確認

---

## ASP メモ（非公開）

- Amazon Associates: `tag=ue083093-22`（brief `operator_note` / CSV `original_note` に記載済み）
- A8 / afb（オンライン・通信講座）: **未設定** — マン管向け案件の確定がフェーズC/F のブロッカー

---

## ロールアウト進捗

| フェーズ | 状態 | 完了日 | 備考 |
|----------|------|--------|------|
| A 現状把握 | **完了** | 2026-06-12 | 本ファイル |
| B エンジン同期 | **完了** | 2026-06-12 | sync 29 + build_all OK。hub付き3本再生成 |
| C 比較記事 HTML（hub付き） | 未 | | 3本 hub 確認済み・目視待ち |
| D guideIndexPicks | 未 | | 講座 slug 公開後 |
| E 通常ガイド導線 | 未 | | 0/126 |
| F 比較記事4本 | 未 | | 3本 ASP 済み + 講座1本 |
| G 本番確認 | 未 | | |

### 次のアクション（フェーズC へ）

1. **フェーズC:** 3本（textbooks / problem-books / mock-exam）を本番目視（hub・ASP・画像・404）
2. **講座ASP確定** → `affiliate-online-course-compare` brief + published（guideIndexPicks 前提）
3. **フェーズD:** `guideIndexPicks`（講座公開後に grid-3）
4. **フェーズE:** 通常ガイド導線（目標 40〜60本）
5. **品質:** 公開記事 v2 リライトはフェーズG前後

### フェーズB 結果（2026-06-12）

- `sync_from_template.py --build`: **29ファイル**同期（`guide_index_picks_ui.py`・`build_article_pages.py` 等）
- **`build_all.py` 完走** — 全 validate OK（`validate_internal_links` 含む）
- 比較記事 HTML 再生成:

| slug | HTML | 比較 hub | 要点 aside | 画像 |
|------|------|----------|------------|------|
| `affiliate-textbooks-recommend` | あり | **あり** | あり | webp×3 |
| `affiliate-problem-books` | あり | **あり** | あり | webp×3 |
| `affiliate-mock-exam-materials` | あり | **あり** | あり | webp×3 |
| `affiliate-free-vs-paid-study` | なし | — | — | —（ASPなし・skip） |

- テンプレ drift: **ok=77 / drift=0**
- **次:** フェーズC 目視 → 講座ASP → フェーズD〜E

### フェーズA ゲート

- [x] 本番パス・デプロイ方式を把握した
- [x] 公開済み `affiliate-*` の一覧を書いた
- [x] `guideIndexPicks` の有無を確認した
- [x] **やることリスト**（パイロット `affiliate-textbooks-recommend`・講座 ASP 案件）が決まった
