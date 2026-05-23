# Character Chat App

Python / Tkinter / OpenAI API / VOICEVOX を使って作成した、キャラクター会話デスクトップアプリです。

## 概要

Character Chat App は、キャラクター設定・ユーザーメモリ・会話履歴・音声読み上げ・キャラクター画像表示を組み合わせた、個人用の相棒アプリです。

v4.1では、キャラクター設定編集UIを追加しました。  
これまで `character_profile.json` を直接編集していたキャラ名・一人称・ユーザーの呼び方・性格・話し方などを、アプリ上の編集画面から変更して保存できます。

## 主な機能

- キャラクター設定の読み込み
- キャラクター設定編集UI
- キャラ名・一人称・ユーザーの呼び方の編集
- 性格・話し方・支援スタイルの編集
- ユーザーメモリの保存・読み込み
- 会話履歴の保存・検索
- 返答ルールの編集
- ルールベース返答
- 疑似LLM返答
- OpenAI APIによるキャラクター返答
- Windows標準音声による読み上げ
- VOICEVOX Engineによる読み上げ
- VOICEVOX話者・スタイル選択
- VOICEVOX音声設定
- キャラクター画像表示
- 状態別キャラクター画像切り替え
- チャットUI改善
- アプリ内概要タブ

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

## キャラクター設定編集

「キャラ・メモリ」タブの「キャラ設定編集」ボタンから編集できます。

編集できる項目は以下です。

```text
- キャラ名
- 一人称
- ユーザーの呼び方
- 関係性
- 性格
- 話し方
- 支援スタイル
- 好きな話題・得意な話題
- 避けるべき話し方
- サンプル台詞
```

保存すると `character_profile.json` に反映されます。  
次のOpenAI返答から、編集したキャラクター設定がプロンプトに反映されます。

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

## 使用技術

- Python
- Tkinter / ttk
- JSON
- OpenAI API
- VOICEVOX Engine API
- Pillow
- PowerShell
- Git / GitHub

## 今後のロードマップ

```text
v4.2：ユーザー設定・メモリ編集改善
v4.3：会話ログのエクスポート
v4.4：メモリ自動要約
v4.5：見た目テーマ切り替え
v5.0：音声入力
```

## バージョン

v4.1
