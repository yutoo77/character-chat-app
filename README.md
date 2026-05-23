# Character Chat App

PythonのTkinterで作った、キャラクター設定・メモリ・OpenAI API・VOICEVOX・キャラクター画像表示を使って会話できるデスクトップアプリです。

## 概要

v3.8では、キャラクター画像の状態別切り替えに対応しました。  
画像が1枚だけでも動きますが、状態別の画像を置くと、返答生成中・会話中にキャラクター表示が切り替わります。

## 主な機能

- OpenAI APIによるキャラクター返答
- VOICEVOX読み上げ
- VOICEVOX話者選択
- VOICEVOX音声設定
- キャラクター画像表示
- 状態別キャラクター画像切り替え
- 画像がない場合のプレースホルダー表示

## 使い方

```powershell
py -3.14 app.py
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
- 通常時の画像

character_thinking.png
- 返答生成中の画像

character_talking.png
- 会話中・返答直後の画像
```

画像はプロジェクト直下に置きます。

```text
character-chat-app/
├─ app.py
├─ character_image.png
├─ character_talking.png
├─ character_thinking.png
└─ ...
```

`images/` フォルダに置く場合も一部対応しています。

```text
images/character.png
images/character.gif
images/character_talking.png
images/character_thinking.png
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

v3.8
