import json
import random
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox


APP_VERSION = "v1.1"
APP_TITLE = "Character Chat App"

PROFILE_FILE = Path("character_profile.json")
HISTORY_FILE = Path("chat_history.json")
RULES_FILE = Path("reply_rules.json")

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


DEFAULT_REPLY_RULES = {
    "rules": [
        {
            "name": "tired",
            "keywords": ["疲れ", "つかれ", "しんど", "だるい"],
            "replies": [
                "{user_call}、おつかれさま。まず水を飲んで、5分だけ休も。"
            ],
        }
    ],
    "default_replies": [
        "うん、聞いてるよ。もう少しだけ言葉にしてくれたら一緒に整理できると思う。"
    ],
}


def now_text():
    """現在時刻を YYYY-MM-DD HH:MM 形式で返す"""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def load_json_file(path, default_value):
    """JSONファイルを読み込む。失敗したらdefault_valueを返す"""
    if not path.exists():
        return default_value

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        messagebox.showwarning(
            "読み込みエラー",
            f"{path.name} の形式が壊れていたため、初期設定で起動します。",
        )
        return default_value


def load_profile_from_file():
    """character_profile.json からキャラ設定を読み込む"""
    data = load_json_file(PROFILE_FILE, DEFAULT_PROFILE.copy())

    profile = DEFAULT_PROFILE.copy()

    if isinstance(data, dict):
        for key in profile:
            if key in data:
                profile[key] = str(data[key])

    return profile


def normalize_reply_rule(raw_rule):
    """読み込んだ返答ルールを安全な形に整える"""
    if not isinstance(raw_rule, dict):
        return None

    name = str(raw_rule.get("name", "unnamed")).strip()
    keywords = raw_rule.get("keywords", [])
    replies = raw_rule.get("replies", [])

    if not isinstance(keywords, list) or not isinstance(replies, list):
        return None

    normalized_keywords = [
        str(keyword).strip()
        for keyword in keywords
        if str(keyword).strip()
    ]

    normalized_replies = [
        str(reply).strip()
        for reply in replies
        if str(reply).strip()
    ]

    if not normalized_keywords or not normalized_replies:
        return None

    return {
        "name": name,
        "keywords": normalized_keywords,
        "replies": normalized_replies,
    }


def load_reply_rules_from_file():
    """reply_rules.json から返答ルールを読み込む"""
    data = load_json_file(RULES_FILE, DEFAULT_REPLY_RULES.copy())

    if not isinstance(data, dict):
        return DEFAULT_REPLY_RULES.copy()

    raw_rules = data.get("rules", [])
    raw_default_replies = data.get("default_replies", [])

    rules = []

    if isinstance(raw_rules, list):
        for raw_rule in raw_rules:
            rule = normalize_reply_rule(raw_rule)

            if rule is not None:
                rules.append(rule)

    default_replies = []

    if isinstance(raw_default_replies, list):
        default_replies = [
            str(reply).strip()
            for reply in raw_default_replies
            if str(reply).strip()
        ]

    if not rules:
        rules = DEFAULT_REPLY_RULES["rules"]

    if not default_replies:
        default_replies = DEFAULT_REPLY_RULES["default_replies"]

    return {
        "rules": rules,
        "default_replies": default_replies,
    }


def normalize_message(raw_message):
    """読み込んだ会話履歴を安全な形に整える"""
    if not isinstance(raw_message, dict):
        return None

    role = str(raw_message.get("role", "")).strip()
    message = str(raw_message.get("message", "")).strip()
    timestamp = str(raw_message.get("timestamp", "")).strip()

    if role not in ["user", "character"]:
        return None

    if not message:
        return None

    return {
        "role": role,
        "message": message,
        "timestamp": timestamp,
    }


def load_chat_history():
    """chat_history.json から会話履歴を読み込む"""
    data = load_json_file(HISTORY_FILE, [])

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


def get_speaker_name(role):
    """roleに応じた表示名を返す"""
    if role == "user":
        return profile["user_call"]

    return profile["character_name"]


def message_matches_search(item, keyword):
    """会話履歴が検索キーワードに一致するか判定する"""
    if not keyword:
        return True

    keyword = keyword.lower()
    speaker = get_speaker_name(item["role"]).lower()
    message = item["message"].lower()
    timestamp = item.get("timestamp", "").lower()

    return keyword in speaker or keyword in message or keyword in timestamp


def refresh_chat_display():
    """会話履歴を画面に表示し直す"""
    chat_text.config(state="normal")
    chat_text.delete("1.0", tk.END)

    keyword = search_var.get().strip()
    visible_count = 0

    for item in chat_history:
        if not message_matches_search(item, keyword):
            continue

        speaker = get_speaker_name(item["role"])
        timestamp = item.get("timestamp", "")

        if timestamp:
            chat_text.insert(tk.END, f"{speaker} ({timestamp})\n")
        else:
            chat_text.insert(tk.END, f"{speaker}\n")

        chat_text.insert(tk.END, f"{item['message']}\n\n")
        visible_count += 1

    chat_text.see(tk.END)
    chat_text.config(state="disabled")

    update_count_label(visible_count)


def add_message(role, message):
    """会話履歴に発言を追加し、画面とファイルに反映する"""
    chat_history.append(
        {
            "role": role,
            "message": message,
            "timestamp": now_text(),
        }
    )

    save_chat_history()
    refresh_chat_display()


def contains_any(text, keywords):
    """文字列にキーワードのどれかが含まれているか確認する"""
    return any(keyword in text for keyword in keywords)


def format_reply_template(template):
    """返答テンプレートにキャラ設定を差し込む"""
    values = {
        "character_name": profile["character_name"],
        "first_person": profile["first_person"],
        "user_call": profile["user_call"],
        "relationship": profile["relationship"],
    }

    try:
        return template.format(**values)
    except KeyError:
        return template


def generate_character_reply(user_message):
    """ユーザー入力に対して、reply_rules.jsonのルールで返答を作る"""
    message = user_message.lower()

    for rule in reply_rules["rules"]:
        keywords = rule["keywords"]

        if contains_any(message, keywords):
            reply_template = random.choice(rule["replies"])
            return format_reply_template(reply_template)

    default_template = random.choice(reply_rules["default_replies"])
    return format_reply_template(default_template)


def send_message(event=None):
    """ユーザー入力を送信し、キャラの返答を表示する"""
    user_message = input_var.get().strip()

    if not user_message:
        messagebox.showinfo("入力エラー", "メッセージを入力してね。")
        return

    input_var.set("")
    search_var.set("")

    add_message("user", user_message)

    reply = generate_character_reply(user_message)
    add_message("character", reply)

    set_status("メッセージを送信しました。")


def add_starter_message():
    """キャラ側から会話のきっかけを出す"""
    starters = [
        "{user_call}、今日は何から進めよっか。小さい一歩で大丈夫だよ。",
        "今の気分を一言で言うならどんな感じ？そこから一緒に整理しよ。",
        "作りたいものの話、少ししよ。ワクワクする方向から決めてもいいと思う。",
        "今日は頑張る日？整える日？どっちでも、ちゃんと意味はあるよ。",
    ]

    search_var.set("")
    message = format_reply_template(random.choice(starters))
    add_message("character", message)
    set_status("キャラから話しかけました。")


def clear_input():
    """入力欄をクリアする"""
    input_var.set("")
    set_status("入力欄をクリアしました。")


def search_history():
    """会話履歴を検索する"""
    refresh_chat_display()

    keyword = search_var.get().strip()
    if keyword:
        set_status(f"会話履歴を検索しました: {keyword}")
    else:
        set_status("検索欄が空なので、全件表示しています。")


def clear_search():
    """検索をクリアする"""
    search_var.set("")
    refresh_chat_display()
    set_status("検索をクリアしました。")


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

    set_status("会話履歴を削除しました。")


def reload_profile():
    """キャラ設定を再読み込みする"""
    global profile

    profile = load_profile_from_file()
    update_profile_display()
    refresh_chat_display()

    set_status("キャラ設定を再読み込みしました。")


def reload_reply_rules():
    """返答ルールを再読み込みする"""
    global reply_rules

    reply_rules = load_reply_rules_from_file()
    update_rule_count_label()
    set_status("返答ルールを再読み込みしました。")


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


def update_count_label(visible_count=None):
    """会話件数を更新する"""
    if visible_count is None:
        visible_count = len(chat_history)

    count_var.set(f"表示: {visible_count}件 / 履歴: {len(chat_history)}件")


def update_rule_count_label():
    """返答ルール数を表示する"""
    rule_count_var.set(f"返答ルール: {len(reply_rules['rules'])}種類")


def set_status(message):
    """ステータスメッセージを更新する"""
    status_var.set(message)


# データ読み込み
profile = load_profile_from_file()
reply_rules = load_reply_rules_from_file()
chat_history = load_chat_history()


# アプリのメインウィンドウ
root = tk.Tk()
root.title(APP_TITLE)
root.geometry("1020x740")
root.configure(bg=BG_COLOR)

# 変数
input_var = tk.StringVar()
search_var = tk.StringVar()
status_var = tk.StringVar(value="準備完了")
profile_summary_var = tk.StringVar()
count_var = tk.StringVar()
rule_count_var = tk.StringVar()

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
    text="キャラ設定と返答ルールを読み込んで会話できるデスクトップアプリ",
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

search_frame = tk.Frame(chat_frame, bg=PANEL_COLOR)
search_frame.pack(fill="x", pady=(0, 8))

search_entry = tk.Entry(
    search_frame,
    textvariable=search_var,
    font=("Meiryo", 10),
)
search_entry.pack(side="left", expand=True, fill="x", padx=(0, 8))

search_button = tk.Button(
    search_frame,
    text="履歴検索",
    font=("Meiryo", 9),
    command=search_history,
    width=10,
)
search_button.pack(side="left", padx=4)

clear_search_button = tk.Button(
    search_frame,
    text="検索クリア",
    font=("Meiryo", 9),
    command=clear_search,
    width=10,
)
clear_search_button.pack(side="left", padx=4)

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

starter_button = tk.Button(
    chat_frame,
    text="キャラから話しかける",
    font=("Meiryo", 10),
    command=add_starter_message,
    width=20,
)
starter_button.pack(anchor="w", pady=(10, 0))

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
    wraplength=270,
)
profile_summary_label.pack(anchor="w", pady=(0, 10))

personality_preview_text = tk.Text(
    profile_frame,
    font=("Meiryo", 9),
    wrap="word",
    width=35,
    height=18,
    bd=1,
    relief="solid",
    state="disabled",
)
personality_preview_text.pack(pady=(0, 10))

rule_count_label = tk.Label(
    profile_frame,
    textvariable=rule_count_var,
    font=("Meiryo", 9),
    bg=PANEL_COLOR,
    fg="#666666",
)
rule_count_label.pack(anchor="w", pady=(0, 8))

reload_profile_button = tk.Button(
    profile_frame,
    text="キャラ設定を再読み込み",
    font=("Meiryo", 10),
    command=reload_profile,
    width=24,
)
reload_profile_button.pack(pady=(0, 8))

reload_rules_button = tk.Button(
    profile_frame,
    text="返答ルールを再読み込み",
    font=("Meiryo", 10),
    command=reload_reply_rules,
    width=24,
)
reload_rules_button.pack(pady=(0, 8))

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
        "v1.1では返答ルールを reply_rules.json に分離しました。\n"
        "コードを変えなくても、キーワードや返答を増やせます。\n"
        "次以降でLLM連携や音声読み上げに拡張できます。"
    ),
    font=("Meiryo", 8),
    bg=PANEL_COLOR,
    fg="#666666",
    justify="left",
    wraplength=270,
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
search_entry.bind("<Return>", lambda event: search_history())
input_entry.focus_set()

# 初期表示
update_profile_display()
update_rule_count_label()
refresh_chat_display()
set_status(f"{profile['character_name']} の設定と返答ルールを読み込みました。")

# アプリ起動
root.mainloop()