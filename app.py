import json
import random
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox


APP_VERSION = "v1.3"
APP_TITLE = "Character Chat App"

PROFILE_FILE = Path("character_profile.json")
HISTORY_FILE = Path("chat_history.json")
RULES_FILE = Path("reply_rules.json")
MEMORY_FILE = Path("memory.json")

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


DEFAULT_MEMORY = {
    "user_name": "ふぁるるくん",
    "current_goal": "Character Chat Appを本格的な相棒アプリに育てる",
    "recent_progress": "Python/Tkinterで複数の小さなデスクトップアプリを作成し、GitHub公開まで経験した",
    "favorite_topics": "開発、研究、英会話、音声対話、RAG、キャラクター会話アプリ",
    "notes": "一気に完璧を目指さず、小さい機能追加を積み上げる。疲れているときは休憩も前進として扱う。",
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
    profile_data = DEFAULT_PROFILE.copy()

    if isinstance(data, dict):
        for key in profile_data:
            if key in data:
                profile_data[key] = str(data[key])

    return profile_data


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

    if not name:
        name = "unnamed"

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


def save_reply_rules_to_file():
    """返答ルールを reply_rules.json に保存する"""
    RULES_FILE.write_text(
        json.dumps(reply_rules, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def make_reply_rules_snapshot():
    """現在の返答ルールを比較用文字列にする"""
    return json.dumps(reply_rules, ensure_ascii=False, sort_keys=True)


def has_unsaved_rule_changes():
    """返答ルールに未保存変更があるか確認する"""
    return make_reply_rules_snapshot() != last_saved_rules_snapshot_var.get()


def update_rules_status_label():
    """返答ルールの保存状態表示を更新する"""
    if has_unsaved_rule_changes():
        rules_status_var.set("ルール未保存")
    else:
        rules_status_var.set("ルール保存済み")


def load_memory_from_file():
    """memory.json からユーザーメモリを読み込む"""
    data = load_json_file(MEMORY_FILE, DEFAULT_MEMORY.copy())
    memory_data = DEFAULT_MEMORY.copy()

    if isinstance(data, dict):
        for key in memory_data:
            if key in data:
                memory_data[key] = str(data[key])

    return memory_data


def save_memory_to_file():
    """ユーザーメモリを memory.json に保存する"""
    MEMORY_FILE.write_text(
        json.dumps(memory, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


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
    return any(keyword.lower() in text for keyword in keywords)


def format_reply_template(template):
    """返答テンプレートにキャラ設定・メモリ情報を差し込む"""
    values = {
        "character_name": profile["character_name"],
        "first_person": profile["first_person"],
        "user_call": profile["user_call"],
        "relationship": profile["relationship"],
        "user_name": memory["user_name"],
        "current_goal": memory["current_goal"],
        "recent_progress": memory["recent_progress"],
        "memory_topics": memory["favorite_topics"],
        "memory_notes": memory["notes"],
    }

    try:
        return template.format(**values)
    except Exception:
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
        "{user_call}、今日は何から進めよっか。今の目標は「{current_goal}」だよね。小さい一歩で大丈夫だよ。",
        "今の気分を一言で言うならどんな感じ？そこから一緒に整理しよ。",
        "作りたいものの話、少ししよ。ワクワクする方向から決めてもいいと思う。",
        "最近の進捗は「{recent_progress}」って覚えてるよ。ここから次の一手を決めよ。",
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


def reload_memory():
    """メモリを再読み込みする"""
    global memory

    memory = load_memory_from_file()
    update_memory_display()
    set_status("メモリを再読み込みしました。")


def reload_reply_rules():
    """返答ルールを再読み込みする"""
    global reply_rules

    if has_unsaved_rule_changes():
        answer = messagebox.askyesno(
            "未保存の返答ルール",
            "保存していない返答ルールの変更があります。\n"
            "再読み込みすると、現在の編集内容は失われます。\n\n"
            "再読み込みしますか？",
        )

        if not answer:
            set_status("返答ルールの再読み込みをキャンセルしました。")
            return

    reply_rules = load_reply_rules_from_file()
    last_saved_rules_snapshot_var.set(make_reply_rules_snapshot())
    refresh_rule_list()
    clear_rule_editor()
    update_rule_count_label()
    update_rules_status_label()
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


def update_memory_display():
    """メモリ概要表示を更新する"""
    memory_summary_text.config(state="normal")
    memory_summary_text.delete("1.0", tk.END)
    memory_summary_text.insert(
        "1.0",
        f"ユーザー名:\n{memory['user_name']}\n\n"
        f"現在の目標:\n{memory['current_goal']}\n\n"
        f"最近の進捗:\n{memory['recent_progress']}\n\n"
        f"好きな話題:\n{memory['favorite_topics']}\n\n"
        f"メモ:\n{memory['notes']}"
    )
    memory_summary_text.config(state="disabled")


def update_count_label(visible_count=None):
    """会話件数を更新する"""
    if visible_count is None:
        visible_count = len(chat_history)

    count_var.set(f"表示: {visible_count}件 / 履歴: {len(chat_history)}件")


def update_rule_count_label():
    """返答ルール数を表示する"""
    rule_count_var.set(f"返答ルール: {len(reply_rules['rules'])}種類")


def format_rule_for_list(rule):
    """返答ルール一覧用の文字列を作る"""
    keyword_count = len(rule["keywords"])
    reply_count = len(rule["replies"])
    return f"{rule['name']} / キーワード{keyword_count}個 / 返答{reply_count}個"


def refresh_rule_list():
    """返答ルール一覧を更新する"""
    rule_listbox.delete(0, tk.END)

    for rule in reply_rules["rules"]:
        rule_listbox.insert(tk.END, format_rule_for_list(rule))

    update_rule_count_label()
    update_rules_status_label()


def get_selected_rule_index():
    """選択中の返答ルール番号を取得する"""
    selection = rule_listbox.curselection()

    if not selection:
        return None

    return selection[0]


def set_rule_reply_text(replies):
    """返答候補をText欄に表示する"""
    rule_replies_text.delete("1.0", tk.END)
    rule_replies_text.insert("1.0", "\n---\n".join(replies))


def get_rule_replies_from_text():
    """Text欄から返答候補を取得する"""
    raw_text = rule_replies_text.get("1.0", "end-1c").strip()

    if not raw_text:
        return []

    return [
        part.strip()
        for part in raw_text.split("\n---\n")
        if part.strip()
    ]


def parse_keywords(keyword_text):
    """カンマ区切りのキーワードをリストにする"""
    normalized = keyword_text.replace("、", ",")
    return [
        keyword.strip()
        for keyword in normalized.split(",")
        if keyword.strip()
    ]


def on_rule_selected(event=None):
    """返答ルールが選択されたとき、編集欄に反映する"""
    selected_index = get_selected_rule_index()

    if selected_index is None:
        return

    rule = reply_rules["rules"][selected_index]

    rule_name_var.set(rule["name"])
    rule_keywords_var.set(", ".join(rule["keywords"]))
    set_rule_reply_text(rule["replies"])

    set_status(f"返答ルールを選択しました: {rule['name']}")


def clear_rule_editor():
    """返答ルール編集欄を空にする"""
    rule_listbox.selection_clear(0, tk.END)
    rule_name_var.set("")
    rule_keywords_var.set("")
    rule_replies_text.delete("1.0", tk.END)
    set_status("返答ルール編集欄をクリアしました。")


def get_rule_from_editor():
    """編集欄から返答ルールを作る"""
    name = rule_name_var.get().strip()
    keywords = parse_keywords(rule_keywords_var.get())
    replies = get_rule_replies_from_text()

    if not name:
        messagebox.showerror("入力エラー", "ルール名を入力してね。")
        return None

    if not keywords:
        messagebox.showerror("入力エラー", "キーワードを1つ以上入力してね。")
        return None

    if not replies:
        messagebox.showerror("入力エラー", "返答候補を1つ以上入力してね。")
        return None

    return {
        "name": name,
        "keywords": keywords,
        "replies": replies,
    }


def add_or_update_rule():
    """返答ルールを追加または更新する"""
    rule = get_rule_from_editor()

    if rule is None:
        return

    selected_index = get_selected_rule_index()

    if selected_index is None:
        reply_rules["rules"].append(rule)
        selected_index = len(reply_rules["rules"]) - 1
        set_status(f"返答ルールを追加しました: {rule['name']}（未保存）")
    else:
        reply_rules["rules"][selected_index] = rule
        set_status(f"返答ルールを更新しました: {rule['name']}（未保存）")

    refresh_rule_list()
    rule_listbox.selection_set(selected_index)
    rule_listbox.activate(selected_index)
    update_rules_status_label()


def delete_rule():
    """選択中の返答ルールを削除する"""
    selected_index = get_selected_rule_index()

    if selected_index is None:
        messagebox.showinfo("選択エラー", "削除する返答ルールを選択してね。")
        return

    rule = reply_rules["rules"][selected_index]

    answer = messagebox.askyesno(
        "削除の確認",
        f"この返答ルールを削除しますか？\n\n{rule['name']}",
    )

    if not answer:
        set_status("返答ルール削除をキャンセルしました。")
        return

    reply_rules["rules"].pop(selected_index)

    refresh_rule_list()
    clear_rule_editor()
    update_rules_status_label()
    set_status(f"返答ルールを削除しました: {rule['name']}（未保存）")


def save_reply_rules():
    """返答ルールを reply_rules.json に保存する"""
    save_reply_rules_to_file()
    last_saved_rules_snapshot_var.set(make_reply_rules_snapshot())
    update_rules_status_label()
    set_status("返答ルールを reply_rules.json に保存しました。")
    messagebox.showinfo("保存完了", "返答ルールを保存したよ。")


def open_memory_window():
    """メモリ編集ウィンドウを開く"""
    memory_window = tk.Toplevel(root)
    memory_window.title("メモリ編集")
    memory_window.geometry("700x620")
    memory_window.configure(bg=BG_COLOR)

    user_name_var = tk.StringVar(value=memory["user_name"])
    current_goal_var = tk.StringVar(value=memory["current_goal"])

    frame = tk.Frame(memory_window, bg=PANEL_COLOR, bd=1, relief="solid")
    frame.pack(expand=True, fill="both", padx=16, pady=16, ipadx=12, ipady=12)

    title_label = tk.Label(
        frame,
        text="メモリ編集",
        font=("Meiryo", 14, "bold"),
        bg=PANEL_COLOR,
        fg=ACCENT_COLOR,
    )
    title_label.pack(anchor="w", pady=(0, 10))

    tk.Label(frame, text="ユーザー名", font=("Meiryo", 9), bg=PANEL_COLOR).pack(anchor="w")
    user_name_entry = tk.Entry(frame, textvariable=user_name_var, font=("Meiryo", 10))
    user_name_entry.pack(fill="x", pady=(2, 8))

    tk.Label(frame, text="現在の目標", font=("Meiryo", 9), bg=PANEL_COLOR).pack(anchor="w")
    current_goal_entry = tk.Entry(frame, textvariable=current_goal_var, font=("Meiryo", 10))
    current_goal_entry.pack(fill="x", pady=(2, 8))

    def add_text_area(label_text, initial_text, height):
        tk.Label(
            frame,
            text=label_text,
            font=("Meiryo", 9),
            bg=PANEL_COLOR,
        ).pack(anchor="w")

        text_widget = tk.Text(
            frame,
            font=("Meiryo", 10),
            height=height,
            wrap="word",
            bd=1,
            relief="solid",
        )
        text_widget.pack(fill="x", pady=(2, 8))
        text_widget.insert("1.0", initial_text)
        return text_widget

    recent_progress_text = add_text_area("最近の進捗", memory["recent_progress"], 4)
    favorite_topics_text = add_text_area("好きな話題", memory["favorite_topics"], 3)
    notes_text = add_text_area("メモ", memory["notes"], 5)

    def save_memory_from_window():
        global memory

        new_memory = {
            "user_name": user_name_var.get().strip() or DEFAULT_MEMORY["user_name"],
            "current_goal": current_goal_var.get().strip() or DEFAULT_MEMORY["current_goal"],
            "recent_progress": recent_progress_text.get("1.0", "end-1c").strip(),
            "favorite_topics": favorite_topics_text.get("1.0", "end-1c").strip(),
            "notes": notes_text.get("1.0", "end-1c").strip(),
        }

        memory = new_memory
        save_memory_to_file()
        update_memory_display()

        set_status("メモリを memory.json に保存しました。")
        messagebox.showinfo("保存完了", "メモリを保存したよ。")

    button_frame = tk.Frame(frame, bg=PANEL_COLOR)
    button_frame.pack(pady=(6, 0))

    save_button = tk.Button(
        button_frame,
        text="保存",
        font=("Meiryo", 10),
        command=save_memory_from_window,
        width=10,
    )
    save_button.grid(row=0, column=0, padx=5)

    close_button = tk.Button(
        button_frame,
        text="閉じる",
        font=("Meiryo", 10),
        command=memory_window.destroy,
        width=10,
    )
    close_button.grid(row=0, column=1, padx=5)


def on_close():
    """アプリ終了時の処理"""
    if has_unsaved_rule_changes():
        answer = messagebox.askyesno(
            "未保存の返答ルール",
            "保存していない返答ルールの変更があります。\n"
            "保存せずに終了すると、変更は失われます。\n\n"
            "終了しますか？",
        )

        if not answer:
            set_status("終了をキャンセルしました。")
            return

    root.destroy()


def set_status(message):
    """ステータスメッセージを更新する"""
    status_var.set(message)


# データ読み込み
profile = load_profile_from_file()
reply_rules = load_reply_rules_from_file()
memory = load_memory_from_file()
chat_history = load_chat_history()


# アプリのメインウィンドウ
root = tk.Tk()
root.title(APP_TITLE)
root.geometry("1240x820")
root.configure(bg=BG_COLOR)

# 変数
input_var = tk.StringVar()
search_var = tk.StringVar()
status_var = tk.StringVar(value="準備完了")
profile_summary_var = tk.StringVar()
count_var = tk.StringVar()
rule_count_var = tk.StringVar()
rules_status_var = tk.StringVar(value="ルール保存済み")
last_saved_rules_snapshot_var = tk.StringVar(value="")

rule_name_var = tk.StringVar()
rule_keywords_var = tk.StringVar()

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
    text="キャラ設定・返答ルール・メモリを使って会話できるデスクトップアプリ",
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

# 中央：キャラ情報・メモリ
profile_frame = tk.Frame(main_frame, bg=PANEL_COLOR, bd=1, relief="solid")
profile_frame.pack(side="left", fill="y", padx=(0, 14), ipadx=12, ipady=12)

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
    wraplength=250,
)
profile_summary_label.pack(anchor="w", pady=(0, 10))

personality_preview_text = tk.Text(
    profile_frame,
    font=("Meiryo", 9),
    wrap="word",
    width=32,
    height=10,
    bd=1,
    relief="solid",
    state="disabled",
)
personality_preview_text.pack(pady=(0, 10))

memory_title = tk.Label(
    profile_frame,
    text="メモリ",
    font=("Meiryo", 11, "bold"),
    bg=PANEL_COLOR,
)
memory_title.pack(anchor="w", pady=(4, 6))

memory_summary_text = tk.Text(
    profile_frame,
    font=("Meiryo", 9),
    wrap="word",
    width=32,
    height=12,
    bd=1,
    relief="solid",
    state="disabled",
)
memory_summary_text.pack(pady=(0, 8))

rule_count_label = tk.Label(
    profile_frame,
    textvariable=rule_count_var,
    font=("Meiryo", 9),
    bg=PANEL_COLOR,
    fg="#666666",
)
rule_count_label.pack(anchor="w", pady=(0, 4))

rules_status_label = tk.Label(
    profile_frame,
    textvariable=rules_status_var,
    font=("Meiryo", 9),
    bg=PANEL_COLOR,
    fg="#666666",
)
rules_status_label.pack(anchor="w", pady=(0, 8))

reload_profile_button = tk.Button(
    profile_frame,
    text="キャラ設定を再読み込み",
    font=("Meiryo", 10),
    command=reload_profile,
    width=24,
)
reload_profile_button.pack(pady=(0, 6))

edit_memory_button = tk.Button(
    profile_frame,
    text="メモリ編集",
    font=("Meiryo", 10),
    command=open_memory_window,
    width=24,
)
edit_memory_button.pack(pady=(0, 6))

reload_memory_button = tk.Button(
    profile_frame,
    text="メモリ再読み込み",
    font=("Meiryo", 10),
    command=reload_memory,
    width=24,
)
reload_memory_button.pack(pady=(0, 6))

reload_rules_button = tk.Button(
    profile_frame,
    text="返答ルールを再読み込み",
    font=("Meiryo", 10),
    command=reload_reply_rules,
    width=24,
)
reload_rules_button.pack(pady=(0, 6))

clear_history_button = tk.Button(
    profile_frame,
    text="会話履歴を削除",
    font=("Meiryo", 10),
    command=clear_history,
    width=24,
)
clear_history_button.pack(pady=(0, 8))

# 右側：返答ルール編集
rules_frame = tk.Frame(main_frame, bg=PANEL_COLOR, bd=1, relief="solid")
rules_frame.pack(side="left", fill="both", ipadx=12, ipady=12)

rules_title = tk.Label(
    rules_frame,
    text="返答ルール編集",
    font=("Meiryo", 11, "bold"),
    bg=PANEL_COLOR,
)
rules_title.pack(anchor="w", pady=(0, 8))

rule_listbox = tk.Listbox(
    rules_frame,
    font=("Meiryo", 9),
    width=44,
    height=10,
    activestyle="dotbox",
)
rule_listbox.pack(fill="x", pady=(0, 8))
rule_listbox.bind("<<ListboxSelect>>", on_rule_selected)

tk.Label(
    rules_frame,
    text="ルール名",
    font=("Meiryo", 9),
    bg=PANEL_COLOR,
).pack(anchor="w")

rule_name_entry = tk.Entry(
    rules_frame,
    textvariable=rule_name_var,
    font=("Meiryo", 9),
    width=44,
)
rule_name_entry.pack(fill="x", pady=(2, 6))

tk.Label(
    rules_frame,
    text="キーワード（カンマ区切り）",
    font=("Meiryo", 9),
    bg=PANEL_COLOR,
).pack(anchor="w")

rule_keywords_entry = tk.Entry(
    rules_frame,
    textvariable=rule_keywords_var,
    font=("Meiryo", 9),
    width=44,
)
rule_keywords_entry.pack(fill="x", pady=(2, 6))

tk.Label(
    rules_frame,
    text="返答候補（複数候補は --- の行で区切る）",
    font=("Meiryo", 9),
    bg=PANEL_COLOR,
).pack(anchor="w")

rule_replies_text = tk.Text(
    rules_frame,
    font=("Meiryo", 9),
    wrap="word",
    width=44,
    height=13,
    bd=1,
    relief="solid",
)
rule_replies_text.pack(fill="both", expand=True, pady=(2, 8))

rule_button_frame = tk.Frame(rules_frame, bg=PANEL_COLOR)
rule_button_frame.pack(fill="x", pady=(0, 8))

new_rule_button = tk.Button(
    rule_button_frame,
    text="新規",
    font=("Meiryo", 9),
    command=clear_rule_editor,
    width=8,
)
new_rule_button.grid(row=0, column=0, padx=3)

add_update_rule_button = tk.Button(
    rule_button_frame,
    text="追加/更新",
    font=("Meiryo", 9),
    command=add_or_update_rule,
    width=10,
)
add_update_rule_button.grid(row=0, column=1, padx=3)

delete_rule_button = tk.Button(
    rule_button_frame,
    text="削除",
    font=("Meiryo", 9),
    command=delete_rule,
    width=8,
)
delete_rule_button.grid(row=0, column=2, padx=3)

save_rules_button = tk.Button(
    rule_button_frame,
    text="ルール保存",
    font=("Meiryo", 9),
    command=save_reply_rules,
    width=10,
)
save_rules_button.grid(row=0, column=3, padx=3)

rule_hint_label = tk.Label(
    rules_frame,
    text=(
        "例: {user_call}、おつかれさま。\n"
        "使える変数: {character_name}, {first_person}, {user_call}, {relationship}, "
        "{current_goal}, {recent_progress}, {memory_topics}"
    ),
    font=("Meiryo", 8),
    bg=PANEL_COLOR,
    fg="#666666",
    justify="left",
    wraplength=330,
)
rule_hint_label.pack(anchor="w")

# ステータスバー
status_label = tk.Label(
    root,
    textvariable=status_var,
    font=("Meiryo", 9),
    bg=BG_COLOR,
    anchor="w",
)
status_label.pack(fill="x", padx=18, pady=(0, 8))

# ショートカット・終了処理
input_entry.bind("<Return>", send_message)
search_entry.bind("<Return>", lambda event: search_history())
root.protocol("WM_DELETE_WINDOW", on_close)
input_entry.focus_set()

# 初期表示
last_saved_rules_snapshot_var.set(make_reply_rules_snapshot())
update_profile_display()
update_memory_display()
refresh_rule_list()
update_rule_count_label()
update_rules_status_label()
refresh_chat_display()
set_status(f"{profile['character_name']} の設定・返答ルール・メモリを読み込みました。")

# アプリ起動
root.mainloop()