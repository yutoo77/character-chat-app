# Character Chat App

PythonのTkinterで作った、キャラクター設定・メモリ・OpenAI API・VOICEVOX・キャラクター画像表示を使って会話できるデスクトップアプリです。

## 概要

v3.9では、チャット画面の見た目を改善しました。  
これまで単純なテキストログとして表示していた会話履歴を、ユーザー発言・キャラクター発言・時刻が見分けやすいように整えています。

## 主な機能

- OpenAI APIによるキャラクター返答
- VOICEVOX読み上げ
- VOICEVOX話者選択
- VOICEVOX音声設定
- キャラクター画像表示
- 状態別キャラクター画像切り替え
- チャットUI改善
- ユーザー発言とキャラクター発言の見分けやすい表示
- 入力欄の案内表示

## 使い方

```powershell
py -3.14 app.py
```

## v3.9の改善点

```text
- チャット欄の表示を会話アプリ風に調整
- ユーザー発言とキャラクター発言の見た目を分離
- 時刻表示をサブ情報として表示
- 会話がない時の案内メッセージを追加
- 入力欄の案内テキストを追加
```

## キャラクター画像

最低限、以下のどちらかを置けば画像表示できます。

```text
character_image.png
character_image.gif
```

状態別に切り替えたい場合は、以下を置きます。

```text
character_normal.png
character_thinking.png
character_talking.png
```

## Git管理しない画像

公開できない画像はGitHubに上げないようにします。

```text
character_image.png
character_image.gif
character_normal.png
character_talking.png
character_thinking.png
images/
```

## バージョン

v3.9

## 今後追加したい機能

- チャット吹き出し表示のさらなる改善
- 表情差分の自動切り替え強化
- 音声に合わせた簡易アニメーション
- 会話履歴の要約
- RAG連携
- 実行ファイル化
- READMEへのスクリーンショット追加
