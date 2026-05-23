# Character Chat App

PythonのTkinterで作った、キャラクター設定・ユーザーメモリ・返答ルール・OpenAI API・音声読み上げを使って会話できるデスクトップアプリです。

## 概要

Character Chat App は、`character_profile.json` に保存されたキャラクター設定を読み込み、ユーザーと会話できるアプリです。

v3.5では、VOICEVOX話者選択UIを追加しました。  
VOICEVOX Engineを起動した状態で「話者取得」を押すと、`/speakers` から話者・スタイル一覧を取得し、画面上で選択できます。選択したspeaker IDは `voice_settings.json` に保存されます。

APIキーはコードや設定ファイルには書かず、環境変数 `OPENAI_API_KEY` から読み込みます。

## 主な機能

- キャラクター設定の読み込み
- 会話履歴の保存
- 返答ルールの編集
- ユーザーメモリの保存
- メモリ自動更新
- 疑似LLMモード
- LLM用プロンプト生成
- OpenAI APIによる返答生成
- Windows標準音声による読み上げ
- VOICEVOX Engineによる読み上げ
- VOICEVOX話者一覧取得
- VOICEVOX話者・スタイル選択
- 選択したVOICEVOX speaker IDの保存
- 自動読み上げON/OFF
- 読み上げ停止
- 水色・青・白を基調にしたUIテーマ

## 使い方

```powershell
py -3.14 app.py
```

## APIキーの設定

OpenAI APIキーは、コードやJSONファイルには書きません。  
Windowsの環境変数 `OPENAI_API_KEY` に設定します。

```powershell
setx OPENAI_API_KEY "sk-ここに自分のAPIキー"
```

設定後はPowerShellを開き直します。

確認は以下で行えます。

```powershell
py -3.14 -c "import os; print('OK' if os.getenv('OPENAI_API_KEY') else 'NG')"
```

## 返答モード

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

voicevox
- VOICEVOX Engineで音声合成する
```

VOICEVOXを使う流れは以下です。

```text
VOICEVOXを起動
↓
アプリで「VOICEVOX接続確認」
↓
アプリで「話者取得」
↓
話者・スタイルを選択
↓
音声エンジンを voicevox にする
↓
最新返答を読み上げ
```

## VOICEVOX Engine連携

v3.5では、VOICEVOX Engineに対して以下のAPIを使います。

```text
/speakers
- 利用可能な話者・スタイル一覧を取得

/audio_query
- 音声合成用クエリを作成

/synthesis
- WAV音声を生成
```

音声合成は以下の流れです。

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

```json
{
  "engine": "windows",
  "voicevox_base_url": "http://127.0.0.1:50021",
  "voicevox_speaker": 3,
  "notes": "Local voice settings. engine can be windows or voicevox."
}
```

## Git管理しないファイル

以下は `.gitignore` に入れます。

```text
character_profile.json
chat_history.json
memory.json
llm_settings.json
voice_settings.json
openai_test.py
```

## バージョン

v3.5

## 今後追加したい機能

- 読み上げ速度・音量・抑揚調整
- 立ち絵・キャラクターUI
- 会話履歴の要約
- RAG連携
- 実行ファイル化
- READMEへのスクリーンショット追加
