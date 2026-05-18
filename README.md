# Character Chat App

PythonのTkinterで作った、キャラクター設定を読み込んで会話できるデスクトップアプリです。

## 概要

Character Chat App は、`character_profile.json` に保存されたキャラクター設定を読み込み、ユーザーと簡単な会話を行うアプリです。

v1.0ではAPIやLLMは使わず、キーワードに応じたルールベースの返答を行います。  
会話履歴は `chat_history.json` に保存され、次回起動時に自動で読み込まれます。

このアプリは、将来的にLLM連携、音声読み上げ、記憶機能、RAG連携へ拡張するための土台として作成しました。

## 主な機能

- `character_profile.json` の読み込み
- キャラ名・一人称・ユーザーの呼び方の反映
- ユーザー入力
- ルールベースのキャラ返答
- 会話履歴の表示
- 会話履歴への日時追加
- `chat_history.json` への会話履歴保存
- 起動時の会話履歴読み込み
- 会話履歴検索
- 会話履歴削除
- キャラ設定の再読み込み
- キャラから話しかける会話スターター
- Enterキーによる送信
- Windows用の起動バッチファイル

## 使い方

以下のコマンドで実行します。

```powershell
python app.py
```

または、Windowsでは `start_app.bat` をダブルクリックして起動できます。

`character_profile.json` を同じフォルダに置くと、そのキャラ設定を読み込んで起動します。  
ファイルがない場合は、アプリ内の初期設定で起動します。

入力欄にメッセージを入力して「送信」を押すと、キャラがルールベースで返答します。  
Enterキーでも送信できます。

会話履歴は自動で `chat_history.json` に保存されます。

## 使用技術

- Python
- Tkinter
- JSON
- pathlib
- random
- datetime

## ファイル構成

```text
character-chat-app/
├─ app.py
├─ README.md
├─ .gitignore
├─ start_app.bat
├─ character_profile.json
└─ chat_history.json
```

`character_profile.json` と `chat_history.json` は個人用データのため、Git管理からは除外しています。

## バージョン

v1.0

## 開発で学んだこと

- TkinterによるチャットUI作成
- JSONファイルの読み込み
- キャラ設定データの利用
- 会話履歴の保存
- 会話履歴検索
- 日時付きログ管理
- ルールベース応答
- 入力内容に応じた条件分岐
- Gitによるコミット管理
- GitHubへのpush
- Gitタグによるバージョン管理

## 今後追加したい機能

- 返答ルールの外部JSON化
- LLM API連携
- ローカルLLM連携
- 音声読み上げ
- 記憶機能
- RAG連携
- 実行ファイル化
- 立ち絵・キャラクターUI