# Character Chat App

PythonのTkinterで作った、キャラクター設定・ユーザーメモリ・返答ルール・OpenAI APIを使って会話できるデスクトップアプリです。

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

v3.1では、OpenAI API返答の品質改善を行いました。  
将来的な音声読み上げを見据えて、返答が長くなりすぎないようにし、2〜4文程度の自然な会話文を返すようにプロンプトと設定を調整しています。

APIキーはコードや設定ファイルには書かず、環境変数 `OPENAI_API_KEY` から読み込みます。

## 主な機能

- `character_profile.json` の読み込み
- `reply_rules.json` の読み込み
- `memory.json` の読み込み
- `llm_settings.json` の読み込み
- `llm_settings.example.json` による設定例の提供
- キャラ名・一人称・ユーザーの呼び方の反映
- ユーザー入力
- 返答エンジン切り替え
- ルールベース返答
- 疑似LLM返答
- OpenAI API連携
- `openai` 返答モード
- 環境変数 `OPENAI_API_KEY` からのAPIキー読み込み
- OpenAI APIエラー時のメッセージ表示
- LLM用プロンプト生成
- LLM設定を含むプロンプト生成
- OpenAI返答の長さ制御
- 音声読み上げを見据えた短め返答
- `max_output_tokens` による出力上限設定
- `verbosity` による返答の詳しさ設定
- `response_style` による返答スタイル設定
- LLM用プロンプト確認ウィンドウ
- LLM用プロンプトのコピー
- LLM設定確認ウィンドウ
- LLM設定のコピー
- LLM設定の再読み込み
- キャラクター設定・メモリ・直近履歴・ユーザー入力を含むプロンプト作成
- 返答テンプレートへのキャラ設定・メモリ情報の差し込み
- 直近会話履歴を使った疑似文脈生成
- チャット画面
- キャラ・メモリ画面
- 返答ルール編集画面
- タブによる画面整理
- 水色・青・白を基調にしたUIテーマ
- カード風パネル
- 青系ボタン
- 返答ルール一覧表示
- 返答ルールの追加
- 返答ルールの編集
- 返答ルールの削除
- `reply_rules.json` への返答ルール保存
- メモリ編集
- `memory.json` へのメモリ保存
- ユーザー発言からのメモリ自動更新
- 会話履歴の表示
- 会話履歴検索
- 会話履歴削除
- キャラ設定の再読み込み
- メモリの再読み込み
- キャラから話しかける会話スターター
- Enterキーによる送信
- Windows用の起動バッチファイル

## 使い方

以下のコマンドで実行します。

```powershell
py -3.14 app.py
```

または、Windowsでは `start_app.bat` をダブルクリックして起動できます。

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
- v3.1では短めで音声化しやすい返答になるように調整
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

各項目の意味は以下の通りです。

```text
provider
- mock / openai / local など、将来の接続先を表す

model
- 使用するモデル名

reply_engine
- 使用する返答エンジン

max_recent_messages
- プロンプトに入れる直近会話履歴の件数

use_memory
- memory.json の内容をプロンプトに含めるか

use_chat_history
- 直近会話履歴をプロンプトに含めるか

temperature
- 将来LLM APIに渡す生成のランダム性設定

max_output_tokens
- OpenAI APIから返ってくる出力の最大トークン数

verbosity
- 返答の詳しさ。low / medium / high を想定

response_style
- 返答スタイル。v3.1では short_voice_friendly を標準にしている

notes
- 設定に関するメモ
```

`llm_settings.json` は個人用設定としてGitHubには上げません。  
代わりに `llm_settings.example.json` をGit管理し、設定例として公開します。

## LLM用プロンプト生成

将来LLM APIに渡すためのプロンプトを生成できます。

プロンプトには以下の情報を含めます。

```text
- LLM設定
- キャラクター名
- 一人称
- ユーザーの呼び方
- 関係性
- 性格
- 話し方
- 支援スタイル
- 避けるべき話し方
- ユーザーメモリ
- 現在の目標
- 最近の進捗
- 好きな話題
- メモ
- 直近の会話履歴
- 今回のユーザー入力
- 応答方針
```

チャット画面の「LLMプロンプト確認」ボタンを押すと、現在の入力欄の内容をもとにプロンプト確認ウィンドウが開きます。  
生成されたプロンプトはコピーできます。

v3.1では、将来的な音声読み上げを見据えて、短く自然な会話文を返すようにプロンプトを調整しています。

## 返答エンジン設計

返答生成の入口を `generate_reply()` に集約しています。

```text
ユーザー入力
↓
generate_reply()
↓
返答モードを確認
↓
rule の場合：generate_rule_based_reply()
mock_llm の場合：generate_mock_llm_reply()
openai の場合：generate_openai_reply()
↓
キャラ返答を生成
```

OpenAI API連携は `generate_openai_reply()` に分離しており、将来的にローカルLLMやRAG連携を追加する場合も、同じ構成で拡張できます。

## v3.1の改善点

v3.1では、OpenAI APIで生成される返答の品質を改善しました。

```text
- 返答を短めに調整
- 音声読み上げを見据えた長さに調整
- 2〜4文程度の自然な会話文を目指す
- 長い箇条書きや説明文を避ける
- 気持ちを受け止める → 現実的に一言 → 次の一手、の流れを強化
- max_output_tokens による出力上限設定を追加
- verbosity による返答の詳しさ設定を追加
- response_style による返答スタイル設定を追加
```

これにより、今後の音声返答機能に進むための土台を整えています。

## 画面構成

以下の3つのタブに画面を分けています。

```text
チャット
- 会話
- 返答モード切り替え
- LLMプロンプト確認
- LLM設定確認
- 履歴検索
- メッセージ送信
- キャラから話しかける

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
```

## UIデザイン

v1.6以降では、以下のようにUIを改善しています。

```text
- 水色・青・白を基調にした配色
- カード風パネル
- 青系の主要ボタン
- 淡い水色の背景
- 読みやすい入力欄
- タブUIの見た目調整
- 危険操作用の赤系ボタン
```

機能だけでなく、ユーザーが継続して使いやすい見た目を意識しています。

## メモリ機能

`memory.json` には、ユーザーに関する簡単な情報を保存します。

例：

```json
{
  "user_name": "ふぁるるくん",
  "current_goal": "Character Chat Appを本格的な相棒アプリに育てる",
  "recent_progress": "Python/Tkinterで複数の小さなデスクトップアプリを作成した",
  "favorite_topics": "開発、研究、英会話、音声対話、RAG",
  "notes": "一気に完璧を目指さず、小さい機能追加を積み上げる。"
}
```

返答テンプレートでは、以下のメモリ情報を使えます。

```text
{user_name}
{current_goal}
{recent_progress}
{memory_topics}
{memory_notes}
```

## メモリ自動更新

ユーザーの発言から簡単なメモリ更新を行えます。

以下のような発言に反応します。

```text
今の目標はCharacter Chat Appを本格的な相棒アプリに育てる
最近v1.3のメモリ機能までできた
好きな話題は音声合成、RAG、キャラクター会話アプリ
覚えて：将来的にVOICEVOXで読み上げできるようにしたい
```

更新された内容は `memory.json` に保存されます。

## 返答ルールの編集

「返答ルール編集」タブから、返答ルールを追加・編集・削除できます。

返答候補を複数入れる場合は、`---` の行で区切ります。

```text
{user_call}、おつかれさま。まず少し休も。
---
うん、疲れてるときは無理しすぎない方がいいかも。
```

返答テンプレートでは、以下の値を使えます。

```text
{character_name}
{first_person}
{user_call}
{relationship}
{user_name}
{current_goal}
{recent_progress}
{memory_topics}
{memory_notes}
```

## 使用技術

- Python
- Tkinter
- ttk
- JSON
- pathlib
- random
- datetime
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
├─ character_profile.json
├─ chat_history.json
├─ memory.json
├─ llm_settings.json
└─ openai_test.py
```

`character_profile.json`、`chat_history.json`、`memory.json`、`llm_settings.json`、`openai_test.py` は個人用・ローカル用データのため、Git管理からは除外しています。

`reply_rules.json` と `llm_settings.example.json` はGit管理します。

## Git管理しないファイル

以下は `.gitignore` に入れています。

```text
character_profile.json
chat_history.json
memory.json
llm_settings.json
openai_test.py
```

特に `OPENAI_API_KEY` は、コード・README・JSONファイルには絶対に書かず、環境変数から読み込みます。

## バージョン

v3.1

## 開発で学んだこと

- TkinterによるチャットUI作成
- ttk.NotebookによるタブUI
- TkinterでのUIテーマ調整
- JSONファイルの読み込み
- キャラ設定データの利用
- 返答ルールの外部JSON化
- 返答ルール編集UI
- メモリ情報の保存と読み込み
- ユーザー発言からの簡易情報抽出
- メモリ情報の自動更新
- 返答テンプレートへの変数埋め込み
- 会話履歴の保存
- 会話履歴検索
- ルールベース応答
- 返答エンジンの分離
- 返答モード切り替え
- 疑似LLMモードの設計
- LLM用プロンプト生成
- LLM設定ファイルの分離
- サンプル設定ファイルの作成
- API連携に向けた安全な設定管理
- OpenAI APIの接続
- 環境変数によるAPIキー管理
- OpenAI SDKによるResponses API呼び出し
- LLM返答モードの追加
- OpenAI返答の品質改善
- 音声読み上げを見据えた返答設計
- max_output_tokens による出力制御
- verbosity / response_style による返答調整
- Gitによるコミット管理

## 今後追加したい機能

- 音声読み上げ
- 自動音声返答
- 読み上げON/OFF
- ローカルLLM連携
- 会話履歴の要約
- メモリ自動更新ルールの強化
- RAG連携
- 実行ファイル化
- 立ち絵・キャラクターUI
- READMEへのスクリーンショット追加