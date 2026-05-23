# Character Chat App

PythonのTkinterで作った、キャラクター設定・ユーザーメモリ・返答ルール・OpenAI API・音声読み上げを使って会話できるデスクトップアプリです。

## 概要

Character Chat App は、`character_profile.json` に保存されたキャラクター設定を読み込み、ユーザーと会話できるアプリです。

最初はルールベースの簡単な返答アプリとして作り始め、現在は以下のような機能を持つ相棒アプリへ拡張しています。

- キャラクター設定の読み込み
- 会話履歴の保存
- 返答ルールの編集
- ユーザーメモリの保存
- メモリ自動更新
- 疑似LLMモード
- LLM用プロンプト生成
- LLM設定ファイルの読み込み
- OpenAI APIによる返答生成
- 短めで音声化しやすい返答生成
- Windows標準音声による読み上げ
- 読み上げ停止
- 読み上げの重なり防止
- VOICEVOX Engine連携準備

v3.4では、VOICEVOX連携準備を追加しました。  
音声エンジンを `windows` / `voicevox` から選べるようにし、VOICEVOX Engineが起動している場合は、`audio_query` と `synthesis` を使って生成したWAV音声を再生できるようにしています。

APIキーはコードや設定ファイルには書かず、環境変数 `OPENAI_API_KEY` から読み込みます。

## 主な機能

- `character_profile.json` の読み込み
- `reply_rules.json` の読み込み
- `memory.json` の読み込み
- `llm_settings.json` の読み込み
- `voice_settings.json` の読み込み
- `llm_settings.example.json` / `voice_settings.example.json` による設定例の提供
- キャラ名・一人称・ユーザーの呼び方の反映
- ユーザー入力
- 返答エンジン切り替え
- ルールベース返答
- 疑似LLM返答
- OpenAI API連携
- `openai` 返答モード
- 環境変数 `OPENAI_API_KEY` からのAPIキー読み込み
- LLM用プロンプト生成
- OpenAI返答の長さ制御
- Windows標準音声による読み上げ
- VOICEVOX Engineによる読み上げ
- 音声エンジン切り替え
- VOICEVOX接続確認
- 最新キャラ返答の手動読み上げ
- キャラ返答の自動読み上げON/OFF
- 読み上げ停止
- 読み上げの重なり防止
- 読み上げ用テキストの簡易整形
- 読み上げ処理の非同期実行
- チャット画面
- キャラ・メモリ画面
- 返答ルール編集画面
- 水色・青・白を基調にしたUIテーマ
- Gitによるバージョン管理

## 使い方

以下のコマンドで実行します。

```powershell
py -3.14 app.py
```

このプロジェクトでは、Pythonの実行は以下に統一しています。

```powershell
py -3.14 app.py
```

パッケージを追加する場合も、以下のように `py -3.14 -m pip` を使います。

```powershell
py -3.14 -m pip install パッケージ名
```

## 初回セットアップ

OpenAI API連携を使う場合は、OpenAI SDKをインストールします。

```powershell
py -3.14 -m pip install openai
```

## APIキーの設定

OpenAI APIキーは、コードやJSONファイルには書きません。  
Windowsの環境変数 `OPENAI_API_KEY` に設定します。

```powershell
setx OPENAI_API_KEY "sk-ここに自分のAPIキー"
```

設定後は、PowerShellを一度閉じて開き直します。

確認は以下で行えます。

```powershell
py -3.14 -c "import os; print('OK' if os.getenv('OPENAI_API_KEY') else 'NG')"
```

## 返答モード

チャット画面で返答モードを切り替えられます。

```text
rule
- 従来のルールベース返答

mock_llm
- 疑似LLMモード

openai
- OpenAI APIを使った返答モード
```

## 音声読み上げ

音声エンジンを切り替えられます。

```text
windows
- Windows標準音声で読み上げる
- 追加インストールなしで使いやすい

voicevox
- VOICEVOX Engineで音声合成する
- VOICEVOXを起動している場合に利用できる
```

v3.4では、VOICEVOX Engineに対して以下の流れで音声を生成します。

```text
テキスト
↓
/audio_query
↓
音声合成用クエリ
↓
/synthesis
↓
WAV音声
↓
PowerShell経由で再生
```

## voice_settings.json

ローカル用の音声設定です。GitHubには上げません。

例：

```json
{
  "engine": "windows",
  "voicevox_base_url": "http://127.0.0.1:50021",
  "voicevox_speaker": 3,
  "notes": "Local voice settings. engine can be windows or voicevox."
}
```

各項目の意味は以下の通りです。

```text
engine
- windows / voicevox のどちらを標準音声エンジンにするか

voicevox_base_url
- VOICEVOX EngineのURL

voicevox_speaker
- VOICEVOXの話者ID

notes
- 設定に関するメモ
```

## LLM設定ファイル

`llm_settings.json` により、使用するLLMプロバイダ、モデル名、直近会話履歴の使用数、メモリ使用の有無などを設定できます。

例：

```json
{
  "provider": "openai",
  "model": "gpt-5.4-nano",
  "reply_engine": "openai",
  "max_recent_messages": 4,
  "use_memory": true,
  "use_chat_history": true,
  "temperature": 0.7,
  "max_output_tokens": 350,
  "verbosity": "low",
  "response_style": "short_voice_friendly",
  "notes": "Local LLM settings. This file is ignored by Git."
}
```

## 返答エンジン設計

返答生成の入口を `generate_reply()` に集約しています。

```text
ユーザー入力
↓
generate_reply()
↓
返答モードを確認
↓
rule / mock_llm / openai
↓
キャラ返答を生成
```

音声読み上げは `speak_text_async()` に分離しています。  
v3.4では、その中で `windows` / `voicevox` の音声エンジンを切り替えます。

## v3.4の改善点

```text
- 音声エンジン切り替えUIを追加
- VOICEVOX Engine連携処理を追加
- VOICEVOX接続確認ボタンを追加
- voice_settings.json / voice_settings.example.json を追加
- Windows標準音声とVOICEVOXを切り替え可能にした
```

## 使用技術

- Python
- Tkinter
- ttk
- JSON
- pathlib
- random
- datetime
- threading
- subprocess
- tempfile
- urllib
- Windows System.Speech
- VOICEVOX Engine API
- OpenAI API
- openai Python SDK

## ファイル構成

```text
character-chat-app/
├─ app.py
├─ README.md
├─ .gitignore
├─ start_app.bat
├─ reply_rules.json
├─ llm_settings.example.json
├─ voice_settings.example.json
├─ character_profile.json
├─ chat_history.json
├─ memory.json
├─ llm_settings.json
├─ voice_settings.json
└─ openai_test.py
```

`character_profile.json`、`chat_history.json`、`memory.json`、`llm_settings.json`、`voice_settings.json`、`openai_test.py` は個人用・ローカル用データのため、Git管理からは除外しています。

## バージョン

v3.4

## 今後追加したい機能

- VOICEVOX話者選択UI
- 読み上げ音声の声質改善
- 立ち絵・キャラクターUI
- 会話履歴の要約
- RAG連携
- 実行ファイル化
- READMEへのスクリーンショット追加