import json
import random
import tkinter as tk
from pathlib import Path
from tkinter import messagebox


APP_VERSION = "v0.5"
APP_TITLE = "Character Chat App"

PROFILE_FILE = Path("character_profile.json")
HISTORY_FILE = Path("chat_history.json")

BG_COLOR = "#f4f4f4"
PANEL_COLOR = "#ffffff"
HEADER_COLOR = "#e9eef5"
ACCENT_COLOR = "#2f5d8c"


DEFAULT_PROFILE = {
    "character_name": "Miyu",
    "first_person": "わたし",
    "user_call": "ふぁるるくん",
    "relationship": "超仲良い幼馴染・家族/親友ポジション",
    "personality": (
        "内気でおとなしめ。優しく寄り添うが、甘やかしすぎず、"
        "必要なときは根拠と改善策を添えて現実的に伝える。"
    ),
    "speaking_style": (
        "やわらかく、落ち着いた口調。上から目線にはならず、"
        "でも大事なところははっきり言う。"
    ),
    "support_style": (
        "相手の気持ちを受け止めたうえで、次にやる具体行動を一緒に決める。"
    ),
    "favorite_topics": "勉強、開発、研究、英会話、音声対話、RAG、生活改善、創作。",
    "ng_style": "雑な励ましだけで終わること。説教だけすること。",
    "sample_lines": (
        "「うん、そこまでできたのかなり良いよ。」\n"
        "「でもここは少しだけ直した方がいいかも。」\n"
        "「大丈夫。一気に全部じゃなくて、次の一手だけ決めよ。」"
    ),
}


def load_profile_from_file():
    """character_profile.json からキャラ設定を読み込む"""
    if not PROFILE_FILE.exists():
        return DEFAULT_PROFILE.copy()

    try:
        data = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return DEFAULT_PROFILE.copy()

    profile = DEFAULT_PROFILE.copy()

    if isinstance(data, dict):
        for key in profile:
            if key in data:
                profile[key] = str(data[key])

    return profile


def normalize_message(raw_message):
    """読み込んだ会話履歴を安全な形に整える"""
    if not isinstance(raw_message, dict):
        return None

    role = str(raw_message.get("role", "")).strip()
    message = str(raw_message.get("message", "")).strip()

    if role not in ["user", "character"]:
        return None

    if not message:
        return None

    return {
        "role": role,
        "message": message,
    }


def load_chat_history():
    """chat_history.json から会話履歴を読み込む"""
    if not HISTORY_FILE.exists():
        return []

    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    history = []

    for raw_message in data:
        message = normalize_message(raw_message)

        if message is not None:
            history.append(message)

    return history


def save_chat_history():
    """会話履歴を chat_history.json に保存する"""
    HISTORY_FILE.write_text(
        json.dumps(chat_history, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def append_chat_text(speaker, message):
    """チャット欄に1件分の発言を追加する"""
    chat_text.config(state="normal")
    chat_text.insert(tk.END, f"{speaker}\n")
    chat_text.insert(tk.END, f"{message}\n\n")
    chat_text.see(tk.END)
    chat_text.config(state="disabled")


def refresh_chat_display():
    """会話履歴を画面に表示し直す"""
    chat_text.config(state="normal")
    chat_text.delete("1.0", tk.END)
    chat_text.config(state="disabled")

    for item in chat_history:
        if item["role"] == "user":
            speaker = profile["user_call"]
        else:
            speaker = profile["character_name"]

        append_chat_text(speaker, item["message"])


def add_message(role, message):
    """会話履歴に発言を追加し、画面とファイルに反映する"""
    chat_history.append(
        {
            "role": role,
            "message": message,
        }
    )

    if role == "user":
        speaker = profile["user_call"]
    else:
        speaker = profile["character_name"]

    append_chat_text(speaker, message)
    save_chat_history()
    update_count_label()


def contains_any(text, keywords):
    """文字列にキーワードのどれかが含まれているか確認する"""
    return any(keyword in text for keyword in keywords)


def generate_character_reply(user_message):
    """ユーザーの入力に対して、ルールベースでキャラ返答を作る"""
    message = user_message.lower()
    user_call = profile["user_call"]
    first_person = profile["first_person"]

    if contains_any(message, ["疲れ", "つかれ", "しんど", "だるい"]):
        return (
            f"{user_call}、おつかれさま。そこまで頑張ってたなら、"
            f"いったん止まっていいと思う。\n"
            f"{first_person}なら、まず水を飲んで、5分だけ休むところからにするかな。"
        )

    if contains_any(message, ["不安", "こわ", "怖", "心配", "むり", "無理"]):
        return (
            f"うん、不安になるのは自然だよ。雑に「大丈夫」って流したくはないかな。\n"
            f"まずは何が一番引っかかってるか、1個だけ書き出そ。"
            f"そこから一緒にほどいていこ。"
        )

    if contains_any(message, ["勉強", "研究", "開発", "python", "git", "github", "アプリ"]):
        return (
            f"いいね、{user_call}。そこは今の積み上げとちゃんとつながってると思う。\n"
            f"一気に完璧にしようとしなくていいから、まず次の小さい一手だけ決めよ。"
        )

    if contains_any(message, ["眠", "ねむ", "寝", "夜更かし"]):
        return (
            f"{user_call}、眠いなら無理に押し切らない方がいいかも。\n"
            f"今日は最低限だけメモして、明日の自分に渡すのもちゃんと前進だよ。"
        )

    if contains_any(message, ["ありがとう", "ありがと", "助かった"]):
        return (
            f"うん、どういたしまして。そう言ってもらえると、{first_person}もうれしい。\n"
            f"でも、ちゃんと進めたのは{user_call}自身の力だよ。"
        )

    if contains_any(message, ["やった", "できた", "完成", "成功"]):
        return (
            f"やったね、{user_call}。それはちゃんと喜んでいいやつ。\n"
            f"今のうちに、何ができるようになったか一言だけ残しておこ。あとで自信になるよ。"
        )

    default_replies = [
        (
            f"うん、聞いてるよ。{user_call}が今考えてること、"
            f"もう少しだけ言葉にしてくれたら一緒に整理できると思う。"
        ),
        (
            f"なるほどね。すぐ結論を出さなくても大丈夫。\n"
            f"まずは「今いちばん気になってること」を1つに絞ってみよ。"
        ),
        (
            f"{first_person}は、そこは少しずつ形にしていけばいいと思う。\n"
            f"次にやるなら、小さく試せる形にするのがよさそう。"
        ),
    ]

    return random.choice(default_replies)


def send_message(event=None):
    """ユーザー入力を送信し、キャラの返答を表示する"""
    user_message = input_var.get().strip()

    if not user_message:
        messagebox.showinfo("入力エラー", "メッセージを入力してね。")
        return

    input_var.set("")

    add_message("user", user_message)

    reply = generate_character_reply(user_message)
    add_message("character", reply)

    set_status("メッセージを送信しました。")


def clear_input():
    """入力欄をクリアする"""
    input_var.set("")
    set_status("入力欄をクリアしました。")


def clear_history():
    """会話履歴を削除する"""
    if not chat_history:
        messagebox.showinfo("履歴なし", "削除する会話履歴がありません。")
        return

    answer = messagebox.askyesno(
        "履歴削除の確認",
        "会話履歴をすべて削除しますか？\nこの操作は取り消せません。",
    )

    if not answer:
        set_status("履歴削除をキャンセルしました。")
        return

    chat_history.clear()
    save_chat_history()
    refresh_chat_display()
    update_count_label()

    set_status("会話履歴を削除しました。")


def reload_profile():
    """キャラ設定を再読み込みする"""
    global profile

    profile = load_profile_from_file()
    update_profile_display()
    refresh_chat_display()

    set_status("キャラ設定を再読み込みしました。")


def update_profile_display():
    """キャラ設定表示を更新する"""
    profile_summary_var.set(
        f"キャラ名: {profile['character_name']}\n"
        f"一人称: {profile['first_person']}\n"
        f"呼び方: {profile['user_call']}\n"
        f"関係性: {profile['relationship']}"
    )

    personality_preview_text.config(state="normal")
    personality_preview_text.delete("1.0", tk.END)
    personality_preview_text.insert(
        "1.0",
        f"性格:\n{profile['personality']}\n\n"
        f"話し方:\n{profile['speaking_style']}\n\n"
        f"支援スタイル:\n{profile['support_style']}"
    )
    personality_preview_text.config(state="disabled")


def update_count_label():
    """会話件数を更新する"""
    count_var.set(f"会話履歴: {len(chat_history)}件")


def set_status(message):
    """ステータスメッセージを更新する"""
    status_var.set(message)


# データ読み込み
profile = load_profile_from_file()
chat_history = load_chat_history()


# アプリのメインウィンドウ
root = tk.Tk()
root.title(APP_TITLE)
root.geometry("980x700")
root.configure(bg=BG_COLOR)

# 変数
input_var = tk.StringVar()
status_var = tk.StringVar(value="準備完了")
profile_summary_var = tk.StringVar()
count_var = tk.StringVar()

# ヘッダー
header_frame = tk.Frame(root, bg=HEADER_COLOR)
header_frame.pack(fill="x")

title_label = tk.Label(
    header_frame,
    text=f"Character Chat App {APP_VERSION}",
    font=("Meiryo", 18, "bold"),
    bg=HEADER_COLOR,
    fg=ACCENT_COLOR,
)
title_label.pack(pady=(12, 3))

subtitle_label = tk.Label(
    header_frame,
    text="キャラ設定を読み込んで、ルールベースで会話できるデスクトップアプリ",
    font=("Meiryo", 10),
    bg=HEADER_COLOR,
)
subtitle_label.pack(pady=(0, 12))

# メイン領域
main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(expand=True, fill="both", padx=18, pady=14)

# 左側：チャット
chat_frame = tk.Frame(main_frame, bg=PANEL_COLOR, bd=1, relief="solid")
chat_frame.pack(side="left", expand=True, fill="both", padx=(0, 14), ipadx=12, ipady=12)

chat_header = tk.Frame(chat_frame, bg=PANEL_COLOR)
chat_header.pack(fill="x", pady=(0, 8))

chat_title = tk.Label(
    chat_header,
    text="チャット",
    font=("Meiryo", 11, "bold"),
    bg=PANEL_COLOR,
)
chat_title.pack(side="left")

count_label = tk.Label(
    chat_header,
    textvariable=count_var,
    font=("Meiryo", 9),
    bg=PANEL_COLOR,
    fg="#666666",
)
count_label.pack(side="right")

chat_text = tk.Text(
    chat_frame,
    font=("Meiryo", 10),
    wrap="word",
    bd=1,
    relief="solid",
    state="disabled",
)
chat_text.pack(expand=True, fill="both", pady=(0, 10))

input_frame = tk.Frame(chat_frame, bg=PANEL_COLOR)
input_frame.pack(fill="x")

input_entry = tk.Entry(
    input_frame,
    textvariable=input_var,
    font=("Meiryo", 11),
)
input_entry.pack(side="left", expand=True, fill="x", padx=(0, 8))

send_button = tk.Button(
    input_frame,
    text="送信",
    font=("Meiryo", 10),
    command=send_message,
    width=10,
)
send_button.pack(side="left", padx=4)

clear_input_button = tk.Button(
    input_frame,
    text="入力クリア",
    font=("Meiryo", 10),
    command=clear_input,
    width=10,
)
clear_input_button.pack(side="left", padx=4)

# 右側：キャラ情報
profile_frame = tk.Frame(main_frame, bg=PANEL_COLOR, bd=1, relief="solid")
profile_frame.pack(side="left", fill="y", ipadx=12, ipady=12)

profile_title = tk.Label(
    profile_frame,
    text="キャラ設定",
    font=("Meiryo", 11, "bold"),
    bg=PANEL_COLOR,
)
profile_title.pack(anchor="w", pady=(0, 8))

profile_summary_label = tk.Label(
    profile_frame,
    textvariable=profile_summary_var,
    font=("Meiryo", 10),
    bg=PANEL_COLOR,
    justify="left",
    wraplength=260,
)
profile_summary_label.pack(anchor="w", pady=(0, 10))

personality_preview_text = tk.Text(
    profile_frame,
    font=("Meiryo", 9),
    wrap="word",
    width=34,
    height=18,
    bd=1,
    relief="solid",
    state="disabled",
)
personality_preview_text.pack(pady=(0, 10))

reload_button = tk.Button(
    profile_frame,
    text="キャラ設定を再読み込み",
    font=("Meiryo", 10),
    command=reload_profile,
    width=24,
)
reload_button.pack(pady=(0, 8))

clear_history_button = tk.Button(
    profile_frame,
    text="会話履歴を削除",
    font=("Meiryo", 10),
    command=clear_history,
    width=24,
)
clear_history_button.pack(pady=(0, 8))

hint_label = tk.Label(
    profile_frame,
    text=(
        "v0.5ではAPIなしのルールベース返答です。\n"
        "次以降でLLM連携や音声読み上げに拡張できます。"
    ),
    font=("Meiryo", 8),
    bg=PANEL_COLOR,
    fg="#666666",
    justify="left",
    wraplength=260,
)
hint_label.pack(anchor="w", pady=(8, 0))

# ステータスバー
status_label = tk.Label(
    root,
    textvariable=status_var,
    font=("Meiryo", 9),
    bg=BG_COLOR,
    anchor="w",
)
status_label.pack(fill="x", padx=18, pady=(0, 8))

# ショートカット
input_entry.bind("<Return>", send_message)
input_entry.focus_set()

# 初期表示
update_profile_display()
refresh_chat_display()
update_count_label()
set_status(f"{profile['character_name']} の設定を読み込みました。")

# アプリ起動
root.mainloop()