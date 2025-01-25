# CursorRulesHub

Cursorの`.cursorrules`ファイルを検索・参照できるプラットフォームです。他の開発者の設定を参考にして、効率的にCursorの設定をカスタマイズすることができます。

## 機能

- GitHubの公開リポジトリから`.cursorrules`ファイルを検索
- リポジトリのスター数や主要言語でのソート・フィルタリング
- モダンでシンプルなUI（ニューモーフィズムデザイン）

## 開発環境のセットアップ

```bash
# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Linuxの場合
.\venv\Scripts\activate   # Windowsの場合

# 依存パッケージのインストール
pip install -r requirements.txt
```

## データ更新

- GitHub Actionsにより24時間ごとに自動でデータが更新されます
- 収集されたデータは`data/`ディレクトリに保存されます

## ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照してください。 