# Character Chat App

Python / Tkinter / OpenAI API / VOICEVOX を使って作成した、キャラクター会話デスクトップアプリです。

## 概要

Character Chat App は、キャラクター設定・ユーザーメモリ・会話履歴・音声読み上げ・キャラクター画像表示を組み合わせた、個人用の相棒アプリです。

最初はルールベースの簡単なチャットアプリとして作り始め、現在は OpenAI API と VOICEVOX を利用して、テキスト会話・音声読み上げ・キャラクター表示まで行えるアプリへ拡張しています。

v4.0では、GitHubや成果物として見せやすいように、README・アプリ内概要タブ・依存関係ファイルを整理しています。

## スクリーンショット

スクリーンショットは `docs/screenshots/` に配置する想定です。

```text
docs/screenshots/chat.png
docs/screenshots/voice_settings.png
docs/screenshots/overview.png
```

## 主な機能

- キャラクター設定の読み込み
- ユーザーメモリの保存・読み込み
- 会話履歴の保存・検索
- 返答ルールの編集
- ルールベース返答
- 疑似LLM返答
- OpenAI APIによるキャラクター返答
- LLM用プロンプト確認
- LLM設定確認
- Windows標準音声による読み上げ
- VOICEVOX Engineによる読み上げ
- VOICEVOX話者・スタイル選択
- VOICEVOX音声設定
- キャラクター画像表示
- 状態別キャラクター画像切り替え
- チャットUI改善
- アプリ内概要タブ

## 使用技術

- Python
- Tkinter / ttk
- JSON
- OpenAI API
- VOICEVOX Engine API
- Pillow
- PowerShell
- Git / GitHub

## 実行方法

```powershell
py -3.14 app.py
```

## セットアップ

必要なPythonパッケージをインストールします。

```powershell
py -3.14 -m pip install -r requirements.txt
```

OpenAI APIを使う場合は、環境変数 `OPENAI_API_KEY` を設定します。

```powershell
setx OPENAI_API_KEY "sk-ここに自分のAPIキー"
```

設定後、PowerShellを開き直して確認します。

```powershell
py -3.14 -c "import os; print('OK' if os.getenv('OPENAI_API_KEY') else 'NG')"
```

## 返答モード

```text
rule
- reply_rules.json のキーワードに応じて返答するルールベースモード

mock_llm
- LLM APIを使わず、メモリや履歴を組み合わせて疑似的にLLM風の返答を作るモード

openai
- OpenAI APIを使い、キャラクター設定・メモリ・直近履歴を反映して返答するモード
```

## VOICEVOX連携

VOICEVOXを使う場合は、VOICEVOX本体またはVOICEVOX Engineを起動します。

既定では以下のURLへ接続します。

```text
http://127.0.0.1:50021
```

アプリ内の「音声設定」タブから以下を行えます。

```text
- VOICEVOX接続確認
- 話者取得
- 話者・スタイル選択
- 話速調整
- 音量調整
- 抑揚調整
- 高さ調整
```

## キャラクター画像

プロジェクト直下に以下の画像を置くと、チャット画面右側に表示できます。

```text
character_image.png
```

状態別に切り替えたい場合は、以下の画像を置きます。

```text
character_normal.png
character_thinking.png
character_talking.png
```

画像は個人利用・権利確認済みのものを使ってください。公開できない画像はGit管理しない方針です。

## ローカル設定ファイル

以下のファイルはローカル用です。GitHubには上げない想定です。

```text
character_profile.json
chat_history.json
memory.json
llm_settings.json
voice_settings.json
openai_test.py
character_image.png
character_image.gif
character_normal.png
character_talking.png
character_thinking.png
images/
```

## ファイル構成

```text
character-chat-app/
├─ app.py
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ start_app.bat
├─ reply_rules.json
├─ llm_settings.example.json
├─ voice_settings.example.json
├─ docs/
│  └─ screenshots/
└─ ...
```

## 開発のポイント

このアプリでは、以下の点を意識して開発しています。

```text
- まず小さく動くものを作る
- 機能を段階的に追加する
- 設定をJSONへ分離する
- APIキーなどの秘密情報をコードに書かない
- Gitでバージョン管理する
- 将来の拡張を考えて処理を関数に分ける
```

## 今後の拡張予定

- 表情差分の追加
- 音声再生中の簡易アニメーション
- 会話履歴の要約
- RAG連携
- 実行ファイル化
- READMEへのスクリーンショット追加
- UI全体のさらなる改善

## バージョン

v4.0
