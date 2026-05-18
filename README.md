# Character Chat App

PythonのTkinterで作った、キャラクター設定を読み込んで会話できるデスクトップアプリです。

## 概要

Character Chat App は、`character_profile.json` に保存されたキャラクター設定を読み込み、ユーザーと簡単な会話を行うアプリです。

v0.5ではAPIやLLMは使わず、キーワードに応じたルールベースの返答を行います。  
会話履歴は `chat_history.json` に保存されます。

## 主な機能

- `character_profile.json` の読み込み
- キャラ名・一人称・ユーザーの呼び方の反映
- ユーザー入力
- ルールベースのキャラ返答
- 会話履歴の表示
- `chat_history.json` への会話履歴保存
- 起動時の会話履歴読み込み
- 会話履歴の削除
- キャラ設定の再読み込み
- Enterキーによる送信

## 使い方

以下のコマンドで実行します。

```powershell
python app.py
```

または、Windowsでは `start_app.bat` をダブルクリックして起動できます。

`character_profile.json` を同じフォルダに置くと、そのキャラ設定を読み込んで起動します。  
ファイルがない場合は、アプリ内の初期設定で起動します。

## 使用技術

- Python
- Tkinter
- JSON
- pathlib
- random

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

## 現在のバージョン

v0.5

## 開発で学んだこと

- TkinterによるチャットUI作成
- JSONファイルの読み込み
- キャラ設定データの利用
- 会話履歴の保存
- ルールベース応答
- 入力内容に応じた条件分岐
- Gitによるコミット管理

## 今後追加したい機能

- 未保存確認
- 返答ルールの追加
- LLM API連携
- ローカルLLM連携
- 音声読み上げ
- 記憶機能