# Character Chat App

PythonのTkinterで作った、キャラクター設定・ユーザーメモリ・返答ルール・OpenAI API・音声読み上げを使って会話できるデスクトップアプリです。

## 概要

Character Chat App は、`character_profile.json` に保存されたキャラクター設定を読み込み、ユーザーと会話できる相棒アプリです。

最初はルールベースの簡単な返答アプリとして作り始め、現在は以下のような機能を持つアプリへ拡張しています。

- キャラクター設定の読み込み
- 会話履歴の保存
- 返答ルールの編集
- ユーザーメモリの保存
- メモリ自動更新
- 疑似LLMモード
- LLM用プロンプト生成
- OpenAI APIによる返答生成
- 短めで音声化しやすい返答生成
- Windows標準音声による読み上げ
- VOICEVOX Engineによる読み上げ
- VOICEVOX話者・スタイル選択
- VOICEVOX音声設定UI
- チャット画面下部のショートカットボタン整理

v3.6.1では、VOICEVOX音声設定UIを「音声設定」タブへ分離しました。  
これによりチャット画面が狭くなる問題を改善し、話速・音量・抑揚・高さを見やすく調整できるようにしています。

v3.6.2では、チャット画面下部のショートカットボタン配置を改善しました。  
これまで縦に並んでいた「キャラから話しかける」「LLMプロンプト確認」「LLM設定確認」を横並びにし、チャット画面の下部が窮屈になりにくいように調整しています。

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
- LLM設定確認
- LLMプロンプト確認
- OpenAI返答の長さ制御
- Windows標準音声による読み上げ
- VOICEVOX Engineによる読み上げ
- 音声エンジン切り替え
- VOICEVOX接続確認
- VOICEVOX話者一覧取得
- VOICEVOX話者・スタイル選択
- 選択したVOICEVOX speaker IDの保存
- VOICEVOX話速調整
- VOICEVOX音量調整
- VOICEVOX抑揚調整
- VOICEVOX高さ調整
- 音声設定の保存
- 最新キャラ返答の手動読み上げ
- キャラ返答の自動読み上げON/OFF
- 読み上げ停止
- 読み上げの重なり防止
- 読み上げ用テキストの簡易整形
- 読み上げ処理の非同期実行
- チャット画面
- キャラ・メモリ画面
- 返答ルール編集画面
- 音声設定画面
- チャット画面下部ショートカットボタンの横並び配置
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

確認する場合は以下を実行します。

```powershell
py -3.14 -m pip show openai
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

`OK` と表示されれば設定できています。

## 返答モード

チャット画面で返答モードを切り替えられます。

```text
rule
- 従来のルールベース返答
- reply_rules.json のキーワードに応じて返答する

mock_llm
- 疑似LLMモード
- 実際のLLM APIは使わない
- ルールベース返答に加えて、メモリ情報や直近会話履歴を組み合わせる
- 将来のLLM連携を想定した仮の返答エンジン

openai
- OpenAI APIを使った返答モード
- build_llm_prompt() で生成したプロンプトをAPIに渡す
- APIキーは環境変数 OPENAI_API_KEY から読み込む
- llm_settings.json の model に指定したモデルを使用する
- 短めで音声化しやすい返答になるように調整
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
音声設定タブで話速・音量・抑揚・高さを調整
↓
音声設定保存
↓
最新返答を読み上げ
```

## VOICEVOX Engine連携

VOICEVOX Engineに対して以下のAPIを使います。

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
音声設定を反映
↓
/synthesis
↓
WAV音声
↓
PowerShell経由で再生
```

## VOICEVOX音声設定

音声設定タブで以下を調整できます。

```text
話速
- voicevox_speed_scale
- 標準は 1.0
- 大きいほど速くなる

音量
- voicevox_volume_scale
- 標準は 1.0
- 大きいほど大きくなる

抑揚
- voicevox_intonation_scale
- 標準は 1.0
- 大きいほど表情が強くなる

高さ
- voicevox_pitch_scale
- 標準は 0.0
- 変更幅は小さめがおすすめ
```

注意として、話速・音量・抑揚・高さは、VOICEVOX読み上げ時に反映されます。  
Windows標準音声では反映されません。

## voice_settings.json

ローカル用の音声設定です。GitHubには上げません。

例：

```json
{
  "engine": "windows",
  "voicevox_base_url": "http://127.0.0.1:50021",
  "voicevox_speaker": 3,
  "voicevox_speed_scale": 1.0,
  "voicevox_pitch_scale": 0.0,
  "voicevox_intonation_scale": 1.0,
  "voicevox_volume_scale": 1.0,
  "voicevox_pre_phoneme_length": 0.1,
  "voicevox_post_phoneme_length": 0.1,
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
- アプリ上で話者を選ぶと自動更新される

voicevox_speed_scale
- VOICEVOXの話速

voicevox_pitch_scale
- VOICEVOXの声の高さ

voicevox_intonation_scale
- VOICEVOXの抑揚

voicevox_volume_scale
- VOICEVOXの音量

voicevox_pre_phoneme_length
- 発話前の無音時間

voicevox_post_phoneme_length
- 発話後の無音時間

notes
- 設定に関するメモ
```

## llm_settings.json

ローカル用のLLM設定です。GitHubには上げません。

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
音声エンジンは `windows` / `voicevox` を切り替えられるようにしています。

VOICEVOXの場合は、選択されたspeaker IDと音声設定を使って読み上げます。

## 画面構成

以下の4つのタブに画面を分けています。

```text
チャット
- 会話
- 返答モード切り替え
- 自動読み上げON/OFF
- 音声エンジン切り替え
- 最新返答を読み上げ
- 読み上げ停止
- キャラから話しかける
- LLMプロンプト確認
- LLM設定確認
- 履歴検索
- メッセージ送信

キャラ・メモリ
- キャラ設定の確認
- メモリの確認
- メモリ編集
- 会話履歴削除

返答ルール編集
- 返答ルール一覧
- 返答ルール追加
- 返答ルール編集
- 返答ルール削除
- reply_rules.json への保存

音声設定
- 音声エンジン切り替え
- VOICEVOX接続確認
- VOICEVOX話者取得
- VOICEVOX話者・スタイル選択
- VOICEVOX話速調整
- VOICEVOX音量調整
- VOICEVOX抑揚調整
- VOICEVOX高さ調整
- 音声設定保存
```

## v3.6.1の改善点

v3.6.1では、VOICEVOX音声設定UIを専用タブへ分離しました。

```text
- 音声設定タブを追加
- チャット画面の圧迫を軽減
- VOICEVOX話者選択を音声設定タブに配置
- 話速・音量・抑揚・高さの設定を音声設定タブに配置
- 読み上げ直前にUI上の音声設定を反映
```

## v3.6.2の改善点

v3.6.2では、チャット画面の表示バランスを改善しました。

```text
- チャット画面下部の3ボタンを横並びに変更
- 「キャラから話しかける」「LLMプロンプト確認」「LLM設定確認」を1行に整理
- 音声設定タブ分離後のチャット画面をさらに見やすく調整
```

## UIデザイン

水色・青・白を基調にした、やわらかく見やすいUIを目指しています。

```text
- 水色・青・白を基調にした配色
- カード風パネル
- 青系の主要ボタン
- 淡い水色の背景
- 読みやすい入力欄
- タブUIの見た目調整
- 危険操作用の赤系ボタン
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

`reply_rules.json`、`llm_settings.example.json`、`voice_settings.example.json` はGit管理します。

## Git管理しないファイル

以下は `.gitignore` に入れています。

```text
character_profile.json
chat_history.json
memory.json
llm_settings.json
voice_settings.json
openai_test.py
```

特に `OPENAI_API_KEY` は、コード・README・JSONファイルには絶対に書かず、環境変数から読み込みます。

## バージョン

v3.6.2

## 今後追加したい機能

- 音声設定のプリセット
- 会話履歴の要約
- メモリ自動更新ルールの強化
- 立ち絵・キャラクターUI
- 表情差分
- RAG連携
- 実行ファイル化
- READMEへのスクリーンショット追加