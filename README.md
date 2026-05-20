# Character Chat App

PythonのTkinterで作った、キャラクター設定を読み込んで会話できるデスクトップアプリです。

## 概要

Character Chat App は、`character_profile.json` に保存されたキャラクター設定を読み込み、ユーザーと簡単な会話を行うアプリです。

v2.0では、返答エンジンを分離しました。  
従来のルールベース返答に加えて、将来のLLM連携を想定した疑似LLMモードを追加しています。

疑似LLMモードでは、実際のAPIは使わず、ルールベース返答・メモリ情報・直近の会話履歴を組み合わせて、LLM連携後の流れを疑似的に再現します。

会話履歴は `chat_history.json` に保存され、次回起動時に自動で読み込まれます。

## 主な機能

- `character_profile.json` の読み込み
- `reply_rules.json` の読み込み
- `memory.json` の読み込み
- キャラ名・一人称・ユーザーの呼び方の反映
- ユーザー入力
- 返答エンジン切り替え
- ルールベース返答
- 疑似LLM返答
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
- 「今の目標は〜」による現在目標の更新
- 「最近〜できた」による最近の進捗の更新
- 「好きな話題は〜」による好きな話題の更新
- 「覚えて：〜」によるメモ追記
- 会話履歴の表示
- 会話履歴への日時追加
- `chat_history.json` への会話履歴保存
- 起動時の会話履歴読み込み
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

`character_profile.json` を同じフォルダに置くと、そのキャラ設定を読み込んで起動します。  
ファイルがない場合は、アプリ内の初期設定で起動します。

入力欄にメッセージを入力して「送信」を押すと、キャラが返答します。  
Enterキーでも送信できます。

## 返答モード

v2.0では、チャット画面で返答モードを切り替えられます。

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

## 返答エンジン設計

v2.0では、返答生成の入口を `generate_reply()` に集約しています。

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

## ファイル構成

```text
character-chat-app/
├─ app.py
├─ README.md
├─ .gitignore
├─ start_app.bat
├─ reply_rules.json
├─ character_profile.json
├─ chat_history.json
└─ memory.json
```

`character_profile.json`、`chat_history.json`、`memory.json` は個人用データのため、Git管理からは除外しています。  
`reply_rules.json` はアプリの返答ルールとしてGit管理します。

## バージョン

v2.0

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
- メモリ更新結果のUI反映
- 返答テンプレートへの変数埋め込み
- 会話履歴の保存
- 会話履歴検索
- 日時付きログ管理
- ルールベース応答
- 返答エンジンの分離
- 返答モード切り替え
- 疑似LLMモードの設計
- LLM連携に向けた拡張構造
- Gitによるコミット管理

## 今後追加したい機能

- OpenAI API連携
- ローカルLLM連携
- LLM用プロンプト生成
- 音声読み上げ
- RAG連携
- 会話履歴の要約
- メモリ自動更新ルールの強化
- 実行ファイル化
- 立ち絵・キャラクターUI