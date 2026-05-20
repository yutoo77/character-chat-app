# Character Chat App

PythonのTkinterで作った、キャラクター設定を読み込んで会話できるデスクトップアプリです。

## 概要

Character Chat App は、`character_profile.json` に保存されたキャラクター設定を読み込み、ユーザーと簡単な会話を行うアプリです。

v2.2では、LLM設定ファイルを追加しました。  
`llm_settings.json` により、使用するLLMプロバイダ、モデル名、直近会話履歴の使用数、メモリ使用の有無などを設定できます。

実際のLLM APIはまだ呼び出さず、将来のOpenAI API連携やローカルLLM連携に向けて、設定をコードから分離しています。

会話履歴は `chat_history.json` に保存され、次回起動時に自動で読み込まれます。

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
- LLM用プロンプト生成
- LLM設定を含むプロンプト生成
- LLM用プロンプト確認ウィンドウ
- LLM用プロンプトのコピー
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
- LLM設定確認ウィンドウ
- LLM設定のコピー
- LLM設定の再読み込み

## 使い方

以下のコマンドで実行します。

```powershell
py -3.14 app.py
```

または、Windowsでは `start_app.bat` をダブルクリックして起動できます。

初回利用時は、必要に応じて `llm_settings.example.json` をコピーして `llm_settings.json` を作成します。

```powershell
copy llm_settings.example.json llm_settings.json
```

このプロジェクトでは `llm_settings.json` は個人用設定としてGit管理から除外しています。

## 返答モード

v2.0以降では、チャット画面で返答モードを切り替えられます。

```text
rule
- 従来のルールベース返答
- reply_rules.json のキーワードに応じて返答する

mock_llm
- 疑似LLMモード
- 実際のLLM APIは使わない
- ルールベース返答に加えて、メモリ情報や直近会話履歴を組み合わせる
- 将来のLLM連携を想定した仮の返答エンジン
```

## LLM設定ファイル

v2.2では、`llm_settings.json` を追加しました。

例：

```json
{
  "provider": "mock",
  "model": "not_set_yet",
  "reply_engine": "mock_llm",
  "max_recent_messages": 6,
  "use_memory": true,
  "use_chat_history": true,
  "temperature": 0.7,
  "notes": "Local LLM settings. This file is ignored by Git."
}
```

各項目の意味は以下の通りです。

```text
provider
- mock / openai / local など、将来の接続先を表す

model
- 使用予定のモデル名

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

notes
- 設定に関するメモ
```

`llm_settings.json` は個人用設定としてGitHubには上げません。  
代わりに `llm_settings.example.json` をGit管理し、設定例として公開します。

## LLM用プロンプト生成

v2.1以降では、将来LLM APIに渡すためのプロンプトを生成できます。

v2.2では、`llm_settings.json` の設定もプロンプトに反映します。

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

v2.2ではAPI呼び出しは行わず、プロンプト生成と設定分離のみを行います。

## 返答エンジン設計

v2.0以降では、返答生成の入口を `generate_reply()` に集約しています。

```text
ユーザー入力
↓
generate_reply()
↓
返答モードを確認
↓
rule の場合：generate_rule_based_reply()
mock_llm の場合：generate_mock_llm_reply()
↓
キャラ返答を生成
```

将来的にOpenAI APIやローカルLLMを接続する場合も、`generate_reply()` から新しい返答エンジンを呼び出す形に拡張できます。

## 画面構成

以下の3つのタブに画面を分けています。

```text
チャット
- 会話
- 返答モード切り替え
- LLMプロンプト確認
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

## 使用技術

- Python
- Tkinter
- ttk
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
├─ reply_rules.json
├─ llm_settings.example.json
├─ character_profile.json
├─ chat_history.json
├─ memory.json
└─ llm_settings.json
```

`character_profile.json`、`chat_history.json`、`memory.json`、`llm_settings.json` は個人用データのため、Git管理からは除外しています。  
`reply_rules.json` と `llm_settings.example.json` はGit管理します。

## バージョン

v2.3

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
- Gitによるコミット管理
- LLM設定の画面表示
- 設定ファイルの再読み込み処理

## 今後追加したい機能

- OpenAI API連携
- ローカルLLM連携
- LLM返答モード
- 音声読み上げ
- RAG連携
- 会話履歴の要約
- メモリ自動更新ルールの強化
- 実行ファイル化
- 立ち絵・キャラクターUI