# mankan-master（マン管マスター）

マンション管理士試験の対策サイトです。`exam-site-shell` テンプレートをベースに構築しています。

## 構成

| ファイル / フォルダ | 役割 |
|----------------------|------|
| `site-config.json` | サイト名・試験名・分野・テーマ色・公式リンク |
| `index.html` | 学習 SPA（過去問・実践演習・一問一答・用語） |
| `about.html` / `privacy.html` / `related-sites.html` | 静的ページ |
| `site-pages.css` / `site-theme.css` | デザイン |
| `data/*.csv` | 問題・用語・試験ガイドのソース |
| `articles/` / `terms/` / `q/` | ビルドで生成される SEO / 過去問ページ |
| `tools/` | ビルド・検証スクリプト |
| `docs/` | 運用ルール |
| `public_site/` | ビルド出力（Git 管理外） |

`exam-site-data-past.js`, `exam-site-data-practice.js`, `exam-site-data-ichimondou.js`, `site-config.js`, `site-theme.css`, `sitemap.xml`, `articles/**`, `terms/g-*.html` などは自動生成のため手編集しません。

## ビルド

```bash
python3 tools/build_all.py
python3 -m http.server 8765
```

- トップ（SPA）: http://127.0.0.1:8765/
- 試験ガイド: http://127.0.0.1:8765/articles/
- 用語集: http://127.0.0.1:8765/terms/
- 過去問: http://127.0.0.1:8765/q/

## 差し替えポイント

| ファイル | 内容 |
|----------|------|
| `site-config.json` | ブランド名、試験名、ドメイン、分野、ナビ、`theme.accent`、公式リンク |
| `data/past_questions.csv` | 過去問（静的 `q/past/` を生成） |
| `data/practice_questions.csv` | 実践演習（静的 `q/practice/` を生成） |
| `data/ichimon_questions.csv` | 一問一答（静的 `q/ichimon/` を生成） |
| `data/glossary_terms.csv` | 用語集（本番 300件以上想定） |
| `data/guide_articles.csv` | 試験ガイド（本番 100本以上想定） |

## テンプレートからの同期

UI 共通部の更新はテンプレ（`exam-site-shell`）側で行い、ここへ取り込みます。

```bash
# exam-site-shell 側で実行
python3 tools/check_template_drift.py --target /Users/otedaiki/mankan-master
python3 tools/sync_from_template.py --target /Users/otedaiki/mankan-master --dry-run
python3 tools/sync_from_template.py --target /Users/otedaiki/mankan-master --build
```

`site-config.json` / `data/*.csv` / `index.html` などサイト固有のファイルは上書きされません（`tools/template_site_only.paths`）。

## 公式情報

- [公益財団法人マンション管理センター](https://www.mankan.org/) — 試験日程・要項・合格発表・登録制度
- [国土交通省 マンション管理関連](https://www.mlit.go.jp/jutakukentiku/house/jutakukentiku_house_tk5_000058.html)

## 注意

同梱の CSV・`example.com` リンク・GA4 ID はサンプル/未設定です。本番公開前に公式 URL・権利・プライバシー・GA4 を必ず確認してください。
