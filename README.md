# Character Chat App

PythonのTkinterで作った、キャラクター設定・ユーザーメモリ・返答ルール・OpenAI API・音声読み上げ・立ち絵表示を使って会話できるデスクトップアプリです。

## 概要

Character Chat App は、`character_profile.json` に保存されたキャラクター設定を読み込み、ユーザーと会話できる相棒アプリです。

v3.7では、チャット画面にキャラクター表示エリアを追加しました。  
プロジェクト直下に `character_image.png` を置くと、チャット画面右側にキャラクター画像を表示できます。画像がない場合でも、プレースホルダー表示になり、アプリはそのまま起動します。

## 主な機能

- OpenAI APIによるキャラクター返答
- キャラクター設定・メモリの読み込み
- 会話履歴保存
- Windows標準音声による読み上げ
- VOICEVOX Engineによる読み上げ
- VOICEVOX話者・スタイル選択
- VOICEVOX音声設定タブ
- チャット画面右側のキャラクター画像表示
- `character_image.png` / `character_image.gif` の読み込み
- 画像がない場合のプレースホルダー表示
- 画像再読み込みボタン
- 返答生成中・会話中などの簡易ステータス表示

## 使い方

```powershell
py -3.14 app.py
```

## キャラクター画像の設定

プロジェクト直下に画像を置くと、アプリ起動時に自動で読み込みます。

```text
character-chat-app/
├─ app.py
├─ character_image.png
└─ ...
```

対応候補は以下です。

```text
character_image.png
character_image.gif
images/character.png
images/character.gif
```

画像を置いたあと、アプリの「画像を再読み込み」ボタンを押すと再読み込みできます。

## 注意

GitHubで公開する場合、キャラクター画像の権利に注意してください。  
個人利用の画像や権利的に公開できない画像は、Git管理しない方が安全です。

`.gitignore` に以下を入れておくと、ローカル画像をGitHubに上げずに済みます。

```text
character_image.png
character_image.gif
images/
```

## 音声読み上げ

音声エンジンを切り替えられます。

```text
windows
- Windows標準音声で読み上げる

voicevox
- VOICEVOX Engineで音声合成する
```

## VOICEVOX音声設定

音声設定タブで以下を調整できます。

```text
話速
音量
抑揚
高さ
```

これらはVOICEVOX読み上げ時に反映されます。

## Git管理しないファイル

以下はローカル用としてGit管理しない想定です。

```text
character_profile.json
chat_history.json
memory.json
llm_settings.json
voice_settings.json
openai_test.py
character_image.png
character_image.gif
images/
```

## バージョン

v3.7

## 今後追加したい機能

- 表情差分
- 返答中の表情切り替え
- 音声に合わせた簡易アニメーション
- 会話履歴の要約
- RAG連携
- 実行ファイル化
- READMEへのスクリーンショット追加
