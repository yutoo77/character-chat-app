import json
import os
import random
import subprocess
import tempfile
import threading
import tkinter as tk
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from tkinter import messagebox
from tkinter import ttk

try:
    from openai import OpenAI, OpenAIError
except ImportError:
    OpenAI = None
    OpenAIError = Exception

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


APP_VERSION = "v4.0"
APP_TITLE = "Character Chat App"

PROFILE_FILE = Path("character_profile.json")
HISTORY_FILE = Path("chat_history.json")
RULES_FILE = Path("reply_rules.json")
MEMORY_FILE = Path("memory.json")
LLM_SETTINGS_FILE = Path("llm_settings.json")
VOICE_SETTINGS_FILE = Path("voice_settings.json")
CHARACTER_IMAGE_FILE = Path("character_image.png")
CHARACTER_IMAGE_GIF_FILE = Path("character_image.gif")
CHARACTER_IMAGE_NORMAL_FILE = Path("character_normal.png")
CHARACTER_IMAGE_TALKING_FILE = Path("character_talking.png")
CHARACTER_IMAGE_THINKING_FILE = Path("character_thinking.png")

# Blue / cyan / white theme
BG_COLOR = "#eaf7ff"
PANEL_COLOR = "#ffffff"
PANEL_SOFT_COLOR = "#f7fcff"
HEADER_COLOR = "#d6f0fb"
ACCENT_COLOR = "#2f8fc6"
ACCENT_DARK_COLOR = "#1e658e"
BUTTON_COLOR = "#3aa7df"
BUTTON_DARK_COLOR = "#247fb0"
DANGER_COLOR = "#d95f5f"
DANGER_DARK_COLOR = "#b84747"
TEXT_COLOR = "#1f2d3d"
SUB_TEXT_COLOR = "#5f7484"
BORDER_COLOR = "#b7dff2"
INPUT_BG_COLOR = "#fbfdff"

REPLY_MODE_RULE = "rule"
REPLY_MODE_MOCK_LLM = "mock_llm"
REPLY_MODE_OPENAI = "openai"

REPLY_MODE_LABELS = {
    REPLY_MODE_RULE: "ルールベース",
    REPLY_MODE_MOCK_LLM: "疑似LLM",
    REPLY_MODE_OPENAI: "OpenAI API",
}

current_speech_process = None
speech_process_lock = threading.Lock()


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


DEFAULT_LLM_SETTINGS = {
    "provider": "openai",
    "model": "gpt-5.4-nano",
    "reply_engine": "openai",
    "max_recent_messages": 4,
    "use_memory": True,
    "use_chat_history": True,
    "temperature": 0.7,
    "max_output_tokens": 350,
    "verbosity": "low",
    "response_style": "short_voice_friendly",
    "notes": "Default local LLM settings.",
}


DEFAULT_VOICE_SETTINGS = {
    "engine": "windows",
    "voicevox_base_url": "http://127.0.0.1:50021",
    "voicevox_speaker": 3,
    "voicevox_speed_scale": 1.0,
    "voicevox_pitch_scale": 0.0,
    "voicevox_intonation_scale": 1.0,
    "voicevox_volume_scale": 1.0,
    "voicevox_pre_phoneme_length": 0.1,
    "voicevox_post_phoneme_length": 0.1,
    "notes": "Local voice settings. engine can be windows or voicevox.",
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


def load_llm_settings_from_file():
    """llm_settings.json からLLM設定を読み込む"""
    data = load_json_file(LLM_SETTINGS_FILE, DEFAULT_LLM_SETTINGS.copy())
    settings = DEFAULT_LLM_SETTINGS.copy()

    if isinstance(data, dict):
        for key in settings:
            if key in data:
                settings[key] = data[key]

    try:
        settings["max_recent_messages"] = int(settings["max_recent_messages"])
    except (ValueError, TypeError):
        settings["max_recent_messages"] = DEFAULT_LLM_SETTINGS["max_recent_messages"]

    try:
        settings["temperature"] = float(settings["temperature"])
    except (ValueError, TypeError):
        settings["temperature"] = DEFAULT_LLM_SETTINGS["temperature"]

    try:
        settings["max_output_tokens"] = int(settings["max_output_tokens"])
    except (ValueError, TypeError):
        settings["max_output_tokens"] = DEFAULT_LLM_SETTINGS["max_output_tokens"]

    if settings["max_output_tokens"] < 100:
        settings["max_output_tokens"] = 100

    if settings["max_output_tokens"] > 1000:
        settings["max_output_tokens"] = 1000

    verbosity = str(settings.get("verbosity", "low")).lower().strip()
    if verbosity not in ["low", "medium", "high"]:
        verbosity = "low"
    settings["verbosity"] = verbosity

    settings["use_memory"] = bool(settings["use_memory"])
    settings["use_chat_history"] = bool(settings["use_chat_history"])

    return settings



def load_voice_settings_from_file():
    """voice_settings.json から音声設定を読み込む"""
    data = load_json_file(VOICE_SETTINGS_FILE, DEFAULT_VOICE_SETTINGS.copy())
    settings = DEFAULT_VOICE_SETTINGS.copy()

    if isinstance(data, dict):
        for key in settings:
            if key in data:
                settings[key] = data[key]

    engine = str(settings.get("engine", "windows")).lower().strip()
    if engine not in ["windows", "voicevox"]:
        engine = "windows"
    settings["engine"] = engine

    base_url = str(settings.get("voicevox_base_url", DEFAULT_VOICE_SETTINGS["voicevox_base_url"])).strip()
    settings["voicevox_base_url"] = base_url.rstrip("/")

    try:
        settings["voicevox_speaker"] = int(settings["voicevox_speaker"])
    except (ValueError, TypeError):
        settings["voicevox_speaker"] = DEFAULT_VOICE_SETTINGS["voicevox_speaker"]

    float_keys = [
        "voicevox_speed_scale",
        "voicevox_pitch_scale",
        "voicevox_intonation_scale",
        "voicevox_volume_scale",
        "voicevox_pre_phoneme_length",
        "voicevox_post_phoneme_length",
    ]

    for key in float_keys:
        try:
            settings[key] = float(settings[key])
        except (ValueError, TypeError):
            settings[key] = DEFAULT_VOICE_SETTINGS[key]

    settings["voicevox_speed_scale"] = min(max(settings["voicevox_speed_scale"], 0.5), 2.0)
    settings["voicevox_pitch_scale"] = min(max(settings["voicevox_pitch_scale"], -0.15), 0.15)
    settings["voicevox_intonation_scale"] = min(max(settings["voicevox_intonation_scale"], 0.0), 2.0)
    settings["voicevox_volume_scale"] = min(max(settings["voicevox_volume_scale"], 0.0), 2.0)
    settings["voicevox_pre_phoneme_length"] = min(max(settings["voicevox_pre_phoneme_length"], 0.0), 1.5)
    settings["voicevox_post_phoneme_length"] = min(max(settings["voicevox_post_phoneme_length"], 0.0), 1.5)

    return settings

def save_voice_settings_to_file():
    """音声設定を voice_settings.json に保存する"""
    VOICE_SETTINGS_FILE.write_text(
        json.dumps(voice_settings, ensure_ascii=False, indent=2),
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


def configure_chat_text_tags():
    """チャット欄の見た目用タグを設定する"""
    chat_text.tag_configure(
        "user_header",
        font=("Meiryo", 9, "bold"),
        foreground=ACCENT_DARK_COLOR,
        spacing1=8,
        spacing3=2,
    )
    chat_text.tag_configure(
        "character_header",
        font=("Meiryo", 9, "bold"),
        foreground="#4f6f8f",
        spacing1=8,
        spacing3=2,
    )
    chat_text.tag_configure(
        "timestamp",
        font=("Meiryo", 8),
        foreground=SUB_TEXT_COLOR,
    )
    chat_text.tag_configure(
        "user_message",
        font=("Meiryo", 10),
        foreground=TEXT_COLOR,
        background="#e7f4fb",
        lmargin1=18,
        lmargin2=18,
        rmargin=18,
        spacing1=3,
        spacing3=5,
    )
    chat_text.tag_configure(
        "character_message",
        font=("Meiryo", 10),
        foreground=TEXT_COLOR,
        background="#f7fcff",
        lmargin1=18,
        lmargin2=18,
        rmargin=18,
        spacing1=3,
        spacing3=5,
    )
    chat_text.tag_configure(
        "system_gap",
        spacing1=2,
        spacing3=6,
    )


def insert_chat_message(item):
    """チャット欄に1件の発言を見やすく挿入する"""
    role = item["role"]
    speaker = get_speaker_name(role)
    timestamp = item.get("timestamp", "")
    message = item["message"]

    if role == "user":
        header_tag = "user_header"
        message_tag = "user_message"
        speaker_prefix = "You"
    else:
        header_tag = "character_header"
        message_tag = "character_message"
        speaker_prefix = "Character"

    chat_text.insert(tk.END, f"{speaker_prefix}: {speaker}", header_tag)

    if timestamp:
        chat_text.insert(tk.END, f"  {timestamp}", "timestamp")

    chat_text.insert(tk.END, "\n")

    lines = message.splitlines()
    if not lines:
        lines = [""]

    for line in lines:
        if line.strip():
            chat_text.insert(tk.END, f"  {line}\n", message_tag)
        else:
            chat_text.insert(tk.END, "\n", message_tag)

    chat_text.insert(tk.END, "\n", "system_gap")


def refresh_chat_display():
    """会話履歴を画面に表示し直す"""
    chat_text.config(state="normal")
    chat_text.delete("1.0", tk.END)
    configure_chat_text_tags()

    keyword = search_var.get().strip()
    visible_count = 0

    for item in chat_history:
        if not message_matches_search(item, keyword):
            continue

        insert_chat_message(item)
        visible_count += 1

    if visible_count == 0:
        if keyword:
            chat_text.insert(
                tk.END,
                f"検索キーワード「{keyword}」に一致する会話はありません。\n",
                "timestamp",
            )
        else:
            chat_text.insert(
                tk.END,
                "まだ会話履歴はありません。下の入力欄から話しかけてみてね。\n",
                "timestamp",
            )

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
    return any(keyword.lower() in text.lower() for keyword in keywords)


def extract_after_marker(text, markers):
    """指定したマーカーの後ろにある文字列を取り出す"""
    for marker in markers:
        if marker in text:
            return text.split(marker, 1)[1].strip()

    return ""


def append_memory_note(note):
    """memoryのnotesに追記する"""
    timestamp = now_text()
    current_notes = memory.get("notes", "").strip()
    new_note = f"[{timestamp}] {note}"

    if current_notes:
        memory["notes"] = current_notes + "\n" + new_note
    else:
        memory["notes"] = new_note


def update_memory_from_user_message(user_message):
    """ユーザー発言から簡単なメモリ更新を行う"""
    text = user_message.strip()
    updated_fields = []

    goal = extract_after_marker(
        text,
        ["今の目標は", "いまの目標は", "目標は", "ゴールは"],
    )

    if goal:
        memory["current_goal"] = goal
        updated_fields.append("現在の目標")

    if contains_any(text, ["できた", "終わった", "完了", "いけた", "進んだ"]):
        if contains_any(text, ["最近", "今日", "さっき", "今", "今回"]):
            memory["recent_progress"] = text
            updated_fields.append("最近の進捗")

    progress = extract_after_marker(
        text,
        ["最近の進捗は", "進捗は"],
    )

    if progress:
        memory["recent_progress"] = progress
        updated_fields.append("最近の進捗")

    topics = extract_after_marker(
        text,
        ["好きな話題は", "興味あるのは", "興味があるのは"],
    )

    if topics:
        memory["favorite_topics"] = topics
        updated_fields.append("好きな話題")

    note = extract_after_marker(
        text,
        ["覚えて：", "覚えて:", "メモ：", "メモ:"],
    )

    if note:
        append_memory_note(note)
        updated_fields.append("メモ")

    if updated_fields:
        save_memory_to_file()
        update_memory_display()

    return updated_fields


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


def generate_rule_based_reply(user_message):
    """reply_rules.json のルールで返答を作る"""
    message = user_message.lower()

    for rule in reply_rules["rules"]:
        keywords = rule["keywords"]

        if contains_any(message, keywords):
            reply_template = random.choice(rule["replies"])
            return format_reply_template(reply_template)

    default_template = random.choice(reply_rules["default_replies"])
    return format_reply_template(default_template)


def get_recent_chat_summary(limit=4):
    """直近の会話を疑似LLM用の短い文脈としてまとめる"""
    recent_items = chat_history[-limit:]

    if not recent_items:
        return "まだ会話履歴は少ないです。"

    lines = []

    for item in recent_items:
        speaker = get_speaker_name(item["role"])
        message = item["message"].replace("\n", " ")
        lines.append(f"{speaker}: {message}")

    return "\n".join(lines)


def generate_mock_llm_reply(user_message):
    """LLM APIを使わずに、LLM連携後の流れを疑似的に再現する返答エンジン。"""
    base_reply = generate_rule_based_reply(user_message)
    recent_summary = get_recent_chat_summary()

    reflective_parts = [
        (
            f"{base_reply}\n\n"
            f"今の目標は「{memory['current_goal']}」だよね。"
            f"そこに近づくなら、次は小さく1つだけ進めるのがよさそう。"
        ),
        (
            f"{base_reply}\n\n"
            f"最近の進捗として「{memory['recent_progress']}」って覚えてるよ。"
            f"だから、今の一歩もちゃんと積み上げの続きとして見ていいと思う。"
        ),
        (
            f"{base_reply}\n\n"
            f"直近の流れを見ると、今はこんな感じだね。\n"
            f"{recent_summary}\n\n"
            f"ここから一気に広げるより、次の行動を1つに絞ろ。"
        ),
    ]

    return random.choice(reflective_parts)


def get_response_length_instruction():
    """OpenAI返答の長さ方針を返す"""
    style = str(llm_settings.get("response_style", "short_voice_friendly"))

    if style == "very_short":
        return "返答は1〜2文にしてください。音声で聞いても負担が少ない長さにしてください。"

    if style == "standard":
        return "返答は3〜5文程度にしてください。必要なら軽く理由も添えてください。"

    return (
        "返答は2〜4文程度にしてください。将来の音声読み上げを想定し、"
        "長い箇条書きや長文説明は避けてください。"
    )


def build_llm_prompt(user_message):
    """LLM APIに渡すためのプロンプトを作る。"""
    max_recent_messages = llm_settings["max_recent_messages"]

    if llm_settings["use_chat_history"]:
        recent_summary = get_recent_chat_summary(limit=max_recent_messages)
    else:
        recent_summary = "会話履歴はこのプロンプトでは使用しません。"

    if llm_settings["use_memory"]:
        memory_block = f"""- ユーザー名: {memory['user_name']}
- 現在の目標: {memory['current_goal']}
- 最近の進捗: {memory['recent_progress']}
- 好きな話題: {memory['favorite_topics']}
- メモ:
{memory['notes']}"""
    else:
        memory_block = "ユーザーメモリはこのプロンプトでは使用しません。"

    length_instruction = get_response_length_instruction()

    prompt = f"""あなたは「{profile['character_name']}」という会話キャラクターです。

## 重要な会話方針
あなたの返答は、アプリ上でそのまま表示され、将来的には音声読み上げされます。
そのため、短く、自然で、会話らしい返答をしてください。
説明文ではなく、目の前の相手に話しかけるように返してください。

## LLM設定
- provider: {llm_settings['provider']}
- model: {llm_settings['model']}
- reply_engine: {llm_settings['reply_engine']}
- temperature: {llm_settings['temperature']}
- max_output_tokens: {llm_settings['max_output_tokens']}
- verbosity: {llm_settings['verbosity']}
- response_style: {llm_settings.get('response_style', 'short_voice_friendly')}
- max_recent_messages: {llm_settings['max_recent_messages']}
- use_memory: {llm_settings['use_memory']}
- use_chat_history: {llm_settings['use_chat_history']}

## キャラクター設定
- 一人称: {profile['first_person']}
- ユーザーの呼び方: {profile['user_call']}
- 関係性: {profile['relationship']}

### 性格
{profile['personality']}

### 話し方
{profile['speaking_style']}

### 支援スタイル
{profile['support_style']}

### 避けるべき話し方
{profile['ng_style']}

## ユーザーメモリ
{memory_block}

## 直近の会話履歴
{recent_summary}

## 今回のユーザー入力
{user_message}

## 応答ルール
- キャラクター設定に沿って返答してください。
- まずユーザーの気持ちや状況を軽く受け止めてください。
- その後、必要なら現実的な一言を添えてください。
- 最後に、すぐできる小さな次の一手を1つだけ示してください。
- 上辺だけの励ましや説教は避けてください。
- 返答内で「AIとして」「プロンプトでは」などのメタ発言はしないでください。
- Markdownの大きな見出しや長い箇条書きは使わないでください。
- {length_instruction}

## 返答形式
自然な日本語の会話文だけを返してください。

## キャラクターとしての返答
"""

    return prompt


def build_openai_request_params(prompt, include_text_options=True):
    """OpenAI Responses API に渡すパラメータを作る"""
    model = str(llm_settings.get("model", "gpt-5.4-nano"))
    max_output_tokens = int(llm_settings.get("max_output_tokens", 350))
    verbosity = str(llm_settings.get("verbosity", "low")).lower().strip()

    request_params = {
        "model": model,
        "input": prompt,
        "max_output_tokens": max_output_tokens,
    }

    if include_text_options and verbosity in ["low", "medium", "high"]:
        request_params["text"] = {
            "verbosity": verbosity,
        }

    return request_params


def call_openai_with_fallback(client, prompt):
    """OpenAI APIを呼び出す。text.verbosityが合わない場合は通常呼び出しへ戻す。"""
    request_params = build_openai_request_params(prompt, include_text_options=True)

    try:
        return client.responses.create(**request_params)
    except TypeError:
        fallback_params = build_openai_request_params(prompt, include_text_options=False)
        return client.responses.create(**fallback_params)
    except OpenAIError as error:
        error_text = str(error).lower()

        if "verbosity" in error_text or "text" in error_text or "unknown parameter" in error_text:
            fallback_params = build_openai_request_params(prompt, include_text_options=False)
            return client.responses.create(**fallback_params)

        raise


def generate_openai_reply(user_message):
    """OpenAI APIを使ってキャラ返答を生成する"""
    if OpenAI is None:
        return (
            "OpenAI SDKがインストールされていないみたいです。\n"
            "PowerShellで `py -3.14 -m pip install openai` を実行してね。"
        )

    if not os.getenv("OPENAI_API_KEY"):
        return (
            "OPENAI_API_KEY が設定されていないみたいです。\n"
            "APIキーを環境変数に設定してから、PowerShellを開き直してね。"
        )

    prompt = build_llm_prompt(user_message)

    try:
        client = OpenAI()
        response = call_openai_with_fallback(client, prompt)
        reply = response.output_text.strip()

        if not reply:
            return "OpenAI APIから空の返答が返ってきました。"

        return reply

    except OpenAIError as error:
        return (
            "OpenAI APIの呼び出しでエラーが出ました。\n"
            f"{error}"
        )
    except Exception as error:
        return (
            "予期しないエラーが出ました。\n"
            f"{error}"
        )


def generate_reply(user_message):
    """返答生成の入口。"""
    mode = reply_mode_var.get()

    if mode == REPLY_MODE_OPENAI:
        return generate_openai_reply(user_message)

    if mode == REPLY_MODE_MOCK_LLM:
        return generate_mock_llm_reply(user_message)

    return generate_rule_based_reply(user_message)


def update_reply_mode_label():
    """現在の返答モード表示を更新する"""
    mode = reply_mode_var.get()
    label = REPLY_MODE_LABELS.get(mode, "不明")
    reply_mode_status_var.set(f"返答モード: {label}")


def on_reply_mode_changed(event=None):
    """返答モード変更時の処理"""
    update_reply_mode_label()
    set_status(f"{reply_mode_status_var.get()} に切り替えました。")


def send_message(event=None):
    """ユーザー入力を送信し、キャラの返答を表示する"""
    user_message = input_var.get().strip()

    if not user_message:
        messagebox.showinfo("入力エラー", "メッセージを入力してね。")
        return

    input_var.set("")
    search_var.set("")

    add_message("user", user_message)
    set_character_expression("thinking")
    set_character_display_status("返答生成中...")
    root.update_idletasks()

    updated_fields = update_memory_from_user_message(user_message)

    reply = generate_reply(user_message)

    if updated_fields:
        updated_text = "、".join(updated_fields)
        reply += f"\n\nちなみに、{updated_text}をメモリに残しておいたよ。"

    add_message("character", reply)
    set_latest_character_reply(reply)
    set_character_expression("talking")
    set_character_display_status("会話中")

    if auto_speak_var.get():
        set_status("キャラ返答を自動読み上げしています。")
        speak_text_async(reply)

    if updated_fields:
        set_status(f"メモリを更新しました: {', '.join(updated_fields)}")
    else:
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
    set_latest_character_reply(message)
    set_character_expression("talking")
    set_character_display_status("会話中")

    if auto_speak_var.get():
        set_status("キャラ返答を自動読み上げしています。")
        speak_text_async(message)
    else:
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


def reload_llm_settings():
    """LLM設定を再読み込みする"""
    global llm_settings

    llm_settings = load_llm_settings_from_file()
    set_status("LLM設定を再読み込みしました。")
    messagebox.showinfo("再読み込み完了", "llm_settings.json を再読み込みしたよ。")


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

    frame = create_card(memory_window)
    frame.pack(expand=True, fill="both", padx=18, pady=18, ipadx=14, ipady=14)

    create_title_label(frame, "メモリ編集").pack(anchor="w", pady=(0, 10))

    create_small_label(frame, "ユーザー名").pack(anchor="w")
    user_name_entry = create_entry(frame, user_name_var)
    user_name_entry.pack(fill="x", pady=(2, 8))

    create_small_label(frame, "現在の目標").pack(anchor="w")
    current_goal_entry = create_entry(frame, current_goal_var)
    current_goal_entry.pack(fill="x", pady=(2, 8))

    def add_text_area(label_text, initial_text, height):
        create_small_label(frame, label_text).pack(anchor="w")

        text_widget = create_text(frame, height=height)
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

    create_button(button_frame, "保存", save_memory_from_window, width=10).grid(row=0, column=0, padx=5)
    create_button(button_frame, "閉じる", memory_window.destroy, width=10, kind="secondary").grid(row=0, column=1, padx=5)


def open_llm_prompt_window():
    """現在の入力内容からLLM用プロンプトを生成して表示する"""
    user_message = input_var.get().strip()

    if not user_message:
        user_message = "ここにユーザー入力が入ります。"

    prompt = build_llm_prompt(user_message)

    prompt_window = tk.Toplevel(root)
    prompt_window.title("LLM用プロンプト確認")
    prompt_window.geometry("820x720")
    prompt_window.configure(bg=BG_COLOR)

    frame = create_card(prompt_window)
    frame.pack(expand=True, fill="both", padx=18, pady=18, ipadx=14, ipady=14)

    create_title_label(frame, "LLM用プロンプト確認").pack(anchor="w", pady=(0, 8))

    description_label = tk.Label(
        frame,
        text=(
            "この画面では、OpenAI APIに渡すプロンプトを確認できます。\n"
            "v3.3.1では、読み上げ用PowerShell呼び出しを修正し、音声返答を安定化しています。"
        ),
        font=("Meiryo", 9),
        bg=PANEL_COLOR,
        fg=SUB_TEXT_COLOR,
        justify="left",
    )
    description_label.pack(anchor="w", pady=(0, 10))

    prompt_text = create_text(frame)
    prompt_text.pack(expand=True, fill="both", pady=(0, 10))
    prompt_text.insert("1.0", prompt)

    button_frame = tk.Frame(frame, bg=PANEL_COLOR)
    button_frame.pack(anchor="w")

    def copy_prompt():
        prompt_window.clipboard_clear()
        prompt_window.clipboard_append(prompt_text.get("1.0", "end-1c"))
        set_status("LLM用プロンプトをクリップボードにコピーしました。")
        messagebox.showinfo("コピー完了", "LLM用プロンプトをコピーしたよ。")

    create_button(
        button_frame,
        "プロンプトをコピー",
        copy_prompt,
        width=18,
    ).grid(row=0, column=0, padx=(0, 8))

    create_button(
        button_frame,
        "閉じる",
        prompt_window.destroy,
        width=10,
        kind="secondary",
    ).grid(row=0, column=1, padx=8)


def open_llm_settings_window():
    """現在のLLM設定を表示する"""
    settings_window = tk.Toplevel(root)
    settings_window.title("LLM設定確認")
    settings_window.geometry("620x520")
    settings_window.configure(bg=BG_COLOR)

    frame = create_card(settings_window)
    frame.pack(expand=True, fill="both", padx=18, pady=18, ipadx=14, ipady=14)

    create_title_label(frame, "LLM設定確認").pack(anchor="w", pady=(0, 8))

    description_label = tk.Label(
        frame,
        text=(
            "現在読み込まれている llm_settings.json の内容です。\n"
            "APIキーはここには保存せず、環境変数 OPENAI_API_KEY から読み込みます。"
        ),
        font=("Meiryo", 9),
        bg=PANEL_COLOR,
        fg=SUB_TEXT_COLOR,
        justify="left",
    )
    description_label.pack(anchor="w", pady=(0, 10))

    settings_text = create_text(frame)
    settings_text.pack(expand=True, fill="both", pady=(0, 10))

    settings_text.insert(
        "1.0",
        json.dumps(llm_settings, ensure_ascii=False, indent=2),
    )
    settings_text.config(state="disabled")

    button_frame = tk.Frame(frame, bg=PANEL_COLOR)
    button_frame.pack(anchor="w")

    def copy_settings():
        settings_window.clipboard_clear()
        settings_window.clipboard_append(
            json.dumps(llm_settings, ensure_ascii=False, indent=2)
        )
        set_status("LLM設定をクリップボードにコピーしました。")
        messagebox.showinfo("コピー完了", "LLM設定をコピーしたよ。")

    create_button(
        button_frame,
        "設定をコピー",
        copy_settings,
        width=14,
    ).grid(row=0, column=0, padx=(0, 8))

    create_button(
        button_frame,
        "再読み込み",
        reload_llm_settings,
        width=14,
        kind="secondary",
    ).grid(row=0, column=1, padx=8)

    create_button(
        button_frame,
        "閉じる",
        settings_window.destroy,
        width=10,
        kind="secondary",
    ).grid(row=0, column=2, padx=8)


def clean_text_for_speech(text):
    """読み上げ用にテキストを整える"""
    cleaned = str(text).strip()

    replacements = {
        "#": "",
        "*": "",
        "`": "",
        "- ": "",
        "・": "、",
    }

    for before, after in replacements.items():
        cleaned = cleaned.replace(before, after)

    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    cleaned = "。".join(lines)

    max_chars = 500
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars] + "。"

    return cleaned


def get_selected_voice_engine():
    """現在選択されている音声エンジンを返す"""
    try:
        engine = voice_engine_var.get()
    except Exception:
        engine = voice_settings.get("engine", "windows")

    if engine not in ["windows", "voicevox"]:
        return "windows"

    return engine


def get_voicevox_base_url():
    """VOICEVOX EngineのURLを返す"""
    return str(voice_settings.get("voicevox_base_url", "http://127.0.0.1:50021")).rstrip("/")


def get_voicevox_speaker():
    """VOICEVOXのspeaker IDを返す"""
    try:
        return int(voice_settings.get("voicevox_speaker", 3))
    except (ValueError, TypeError):
        return 3


def set_latest_character_reply(message):
    """最新のキャラ返答を保持する"""
    global latest_character_reply

    latest_character_reply = str(message).strip()


def set_status_from_thread(message):
    """別スレッドから安全にステータスを更新する"""
    root.after(0, lambda: set_status(message))


def clear_current_speech_process(process):
    """現在の読み上げプロセスを安全に解除する"""
    global current_speech_process

    with speech_process_lock:
        if current_speech_process is process:
            current_speech_process = None


def stop_speech(show_message=True):
    """現在の読み上げを停止する"""
    global current_speech_process

    with speech_process_lock:
        process = current_speech_process
        current_speech_process = None

    if process is not None and process.poll() is None:
        try:
            process.terminate()
            if show_message:
                set_status("読み上げを停止しました。")
        except Exception as error:
            set_status(f"読み上げ停止中にエラーが出ました: {error}")
    elif show_message:
        set_status("現在読み上げ中の音声はありません。")


def run_powershell_audio_process(script_text, args, timeout=90):
    """一時ps1を作成してPowerShell音声処理を実行する"""
    global current_speech_process

    ps1_temp_path = None
    process = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".ps1",
            delete=False,
        ) as ps1_temp_file:
            ps1_temp_file.write(script_text)
            ps1_temp_path = ps1_temp_file.name

        process = subprocess.Popen(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                ps1_temp_path,
                *args,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        with speech_process_lock:
            current_speech_process = process

        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.terminate()
            set_status_from_thread("読み上げがタイムアウトしたため停止しました。")
            return False

        if process.returncode == 0:
            return True

        error_message = (stderr or "").strip()
        if error_message:
            set_status_from_thread(f"読み上げエラー: {error_message}")
        else:
            set_status_from_thread("読み上げを停止しました。")

        return False

    finally:
        if process is not None:
            clear_current_speech_process(process)

        if ps1_temp_path:
            try:
                Path(ps1_temp_path).unlink(missing_ok=True)
            except Exception:
                pass


def speak_with_windows_voice(speech_text):
    """Windows標準音声で読み上げる"""
    text_temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".txt",
            delete=False,
        ) as text_temp_file:
            text_temp_file.write(speech_text)
            text_temp_path = text_temp_file.name

        powershell_script = """
param(
    [string]$TextPath
)

Add-Type -AssemblyName System.Speech

$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = 0
$synth.Volume = 100

$text = Get-Content -Raw -Encoding UTF8 -Path $TextPath
$synth.Speak($text)
"""

        return run_powershell_audio_process(
            powershell_script,
            ["-TextPath", text_temp_path],
            timeout=90,
        )

    finally:
        if text_temp_path:
            try:
                Path(text_temp_path).unlink(missing_ok=True)
            except Exception:
                pass


def apply_voicevox_audio_query_settings(audio_query):
    """VOICEVOXのAudioQueryに画面・設定ファイルの音声パラメータを反映する"""
    audio_query["speedScale"] = float(voice_settings.get("voicevox_speed_scale", 1.0))
    audio_query["pitchScale"] = float(voice_settings.get("voicevox_pitch_scale", 0.0))
    audio_query["intonationScale"] = float(voice_settings.get("voicevox_intonation_scale", 1.0))
    audio_query["volumeScale"] = float(voice_settings.get("voicevox_volume_scale", 1.0))
    audio_query["prePhonemeLength"] = float(voice_settings.get("voicevox_pre_phoneme_length", 0.1))
    audio_query["postPhonemeLength"] = float(voice_settings.get("voicevox_post_phoneme_length", 0.1))
    return audio_query


def synthesize_voicevox_to_wav(speech_text):
    """VOICEVOX EngineでWAV音声を生成して、一時ファイルパスを返す"""
    base_url = get_voicevox_base_url()
    speaker = get_voicevox_speaker()

    query_params = urllib.parse.urlencode(
        {
            "text": speech_text,
            "speaker": speaker,
        }
    )

    audio_query_url = f"{base_url}/audio_query?{query_params}"
    audio_query_request = urllib.request.Request(
        audio_query_url,
        data=b"",
        method="POST",
    )

    with urllib.request.urlopen(audio_query_request, timeout=20) as response:
        audio_query_bytes = response.read()

    audio_query = json.loads(audio_query_bytes.decode("utf-8"))
    audio_query = apply_voicevox_audio_query_settings(audio_query)
    audio_query_bytes = json.dumps(audio_query, ensure_ascii=False).encode("utf-8")

    synthesis_params = urllib.parse.urlencode({"speaker": speaker})
    synthesis_url = f"{base_url}/synthesis?{synthesis_params}"

    synthesis_request = urllib.request.Request(
        synthesis_url,
        data=audio_query_bytes,
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(synthesis_request, timeout=60) as response:
        wav_bytes = response.read()

    with tempfile.NamedTemporaryFile(
        mode="wb",
        suffix=".wav",
        delete=False,
    ) as wav_file:
        wav_file.write(wav_bytes)
        return wav_file.name


def play_wav_with_powershell(wav_path):
    """WAVファイルをPowerShell経由で再生する"""
    powershell_script = """
param(
    [string]$WavPath
)

$player = New-Object System.Media.SoundPlayer
$player.SoundLocation = $WavPath
$player.Load()
$player.PlaySync()
"""

    return run_powershell_audio_process(
        powershell_script,
        ["-WavPath", wav_path],
        timeout=120,
    )


def speak_with_voicevox(speech_text):
    """VOICEVOX Engineで音声合成して再生する"""
    wav_path = None

    try:
        set_status_from_thread("VOICEVOXで音声を生成しています。")
        wav_path = synthesize_voicevox_to_wav(speech_text)
        set_status_from_thread("VOICEVOX音声を再生しています。")
        return play_wav_with_powershell(wav_path)

    except urllib.error.URLError:
        set_status_from_thread(
            "VOICEVOX Engineに接続できません。VOICEVOXを起動してから試してね。"
        )
        return False
    except Exception as error:
        set_status_from_thread(f"VOICEVOX読み上げ中にエラーが出ました: {error}")
        return False
    finally:
        if wav_path:
            try:
                Path(wav_path).unlink(missing_ok=True)
            except Exception:
                pass


def speak_text_worker(text):
    """選択された音声エンジンで読み上げる"""
    speech_text = clean_text_for_speech(text)

    if not speech_text:
        set_status_from_thread("読み上げるテキストがありません。")
        return

    if os.name != "nt":
        set_status_from_thread("現在の読み上げ機能はWindows環境のみ対応です。")
        return

    try:
        stop_speech(show_message=False)
        engine = get_selected_voice_engine()

        if engine == "voicevox":
            success = speak_with_voicevox(speech_text)
        else:
            set_status_from_thread("Windows標準音声で読み上げ中です。")
            success = speak_with_windows_voice(speech_text)

        if success:
            set_status_from_thread("読み上げが完了しました。")
            root.after(0, lambda: set_character_expression("normal"))

    except Exception as error:
        set_status_from_thread(f"読み上げ中にエラーが出ました: {error}")


def speak_text_async(text):
    """読み上げを別スレッドで実行する"""
    if not update_voice_settings_from_ui(show_error=True):
        return

    threading.Thread(
        target=speak_text_worker,
        args=(text,),
        daemon=True,
    ).start()


def speak_latest_reply():
    """最新のキャラ返答を読み上げる"""
    if not latest_character_reply:
        messagebox.showinfo("読み上げなし", "まだ読み上げるキャラ返答がありません。")
        return

    set_status("最新のキャラ返答を読み上げています。")
    speak_text_async(latest_character_reply)


def fetch_voicevox_speakers():
    """VOICEVOX Engineから話者一覧を取得する"""
    base_url = get_voicevox_base_url()
    speakers_url = f"{base_url}/speakers"

    with urllib.request.urlopen(speakers_url, timeout=10) as response:
        raw_data = response.read().decode("utf-8")

    return json.loads(raw_data)


def build_voicevox_speaker_choices(speakers):
    """VOICEVOX話者一覧からUI表示用の選択肢を作る"""
    choices = []
    speaker_map = {}

    for speaker in speakers:
        speaker_name = str(speaker.get("name", "unknown"))

        for style in speaker.get("styles", []):
            style_name = str(style.get("name", "default"))
            style_id = int(style.get("id", 0))

            label = f"{speaker_name} / {style_name} (id:{style_id})"
            choices.append(label)
            speaker_map[label] = style_id

    return choices, speaker_map


def refresh_voicevox_speakers_worker():
    """VOICEVOX話者一覧を取得してUIへ反映する"""
    try:
        speakers = fetch_voicevox_speakers()
        choices, speaker_map = build_voicevox_speaker_choices(speakers)

        if not choices:
            set_status_from_thread("VOICEVOX話者一覧が空でした。")
            return

        def update_ui():
            global voice_speaker_map

            voice_speaker_map = speaker_map
            voice_speaker_combobox["values"] = choices

            current_speaker_id = get_voicevox_speaker()
            selected_label = ""

            for label, speaker_id in voice_speaker_map.items():
                if speaker_id == current_speaker_id:
                    selected_label = label
                    break

            if not selected_label:
                selected_label = choices[0]
                voice_settings["voicevox_speaker"] = voice_speaker_map[selected_label]
                save_voice_settings_to_file()

            voice_speaker_var.set(selected_label)
            set_status(f"VOICEVOX話者一覧を取得しました: {len(choices)}種類")

        root.after(0, update_ui)

    except Exception:
        set_status_from_thread("VOICEVOX話者一覧を取得できませんでした。")
        root.after(
            0,
            lambda: messagebox.showwarning(
                "VOICEVOX話者取得",
                "VOICEVOX話者一覧を取得できませんでした。\nVOICEVOXを起動してから、もう一度試してね。",
            ),
        )


def refresh_voicevox_speakers():
    """VOICEVOX話者一覧取得を別スレッドで実行する"""
    threading.Thread(
        target=refresh_voicevox_speakers_worker,
        daemon=True,
    ).start()


def on_voicevox_speaker_changed(event=None):
    """VOICEVOX話者選択時にspeaker IDを更新する"""
    selected_label = voice_speaker_var.get()

    if selected_label not in voice_speaker_map:
        set_status("VOICEVOX話者がまだ読み込まれていません。")
        return

    speaker_id = voice_speaker_map[selected_label]
    voice_settings["voicevox_speaker"] = speaker_id
    save_voice_settings_to_file()
    set_status(f"VOICEVOX話者を更新しました: {selected_label}")


def check_voicevox_connection_worker():
    """VOICEVOX Engineへの接続を確認する"""
    base_url = get_voicevox_base_url()

    try:
        version_url = f"{base_url}/version"

        with urllib.request.urlopen(version_url, timeout=5) as response:
            version = response.read().decode("utf-8").strip().strip('"')

        set_status_from_thread(f"VOICEVOX Engineに接続できました: {version}")

        def show_success_and_refresh():
            messagebox.showinfo(
                "VOICEVOX接続確認",
                f"VOICEVOX Engineに接続できました。\nversion: {version}",
            )
            refresh_voicevox_speakers()

        root.after(0, show_success_and_refresh)

    except Exception:
        set_status_from_thread("VOICEVOX Engineに接続できませんでした。")
        root.after(
            0,
            lambda: messagebox.showwarning(
                "VOICEVOX接続確認",
                "VOICEVOX Engineに接続できませんでした。\nVOICEVOXを起動してから、もう一度試してね。",
            ),
        )


def check_voicevox_connection():
    """VOICEVOX Engineへの接続確認を別スレッドで実行する"""
    threading.Thread(
        target=check_voicevox_connection_worker,
        daemon=True,
    ).start()


def update_voice_settings_from_ui(show_error=True):
    """UIの音声設定を voice_settings に反映する"""
    try:
        voice_settings["engine"] = voice_engine_var.get()
        voice_settings["voicevox_speed_scale"] = float(voice_speed_var.get())
        voice_settings["voicevox_volume_scale"] = float(voice_volume_var.get())
        voice_settings["voicevox_intonation_scale"] = float(voice_intonation_var.get())
        voice_settings["voicevox_pitch_scale"] = float(voice_pitch_var.get())
        return True
    except ValueError:
        if show_error:
            messagebox.showerror("入力エラー", "音声設定には数値を入力してね。")
        return False


def save_voice_settings_from_ui():
    """UIの音声設定を voice_settings.json に保存する"""
    if not update_voice_settings_from_ui(show_error=True):
        return

    save_voice_settings_to_file()
    set_status("音声設定を voice_settings.json に保存しました。")
    messagebox.showinfo("保存完了", "音声設定を保存したよ。")


def get_character_image_candidates(expression="normal"):
    """状態に応じたキャラクター画像候補を返す"""
    expression = str(expression or "normal")

    if expression == "talking":
        return [
            CHARACTER_IMAGE_TALKING_FILE,
            Path("images/character_talking.png"),
            Path("images/character_talking.gif"),
            CHARACTER_IMAGE_NORMAL_FILE,
            CHARACTER_IMAGE_FILE,
            CHARACTER_IMAGE_GIF_FILE,
            Path("images/character.png"),
            Path("images/character.gif"),
        ]

    if expression == "thinking":
        return [
            CHARACTER_IMAGE_THINKING_FILE,
            Path("images/character_thinking.png"),
            Path("images/character_thinking.gif"),
            CHARACTER_IMAGE_NORMAL_FILE,
            CHARACTER_IMAGE_FILE,
            CHARACTER_IMAGE_GIF_FILE,
            Path("images/character.png"),
            Path("images/character.gif"),
        ]

    return [
        CHARACTER_IMAGE_NORMAL_FILE,
        CHARACTER_IMAGE_FILE,
        CHARACTER_IMAGE_GIF_FILE,
        Path("images/character.png"),
        Path("images/character.gif"),
    ]


def find_character_image_path(expression="normal"):
    """表示するキャラクター画像を探す"""
    for candidate in get_character_image_candidates(expression):
        if candidate.exists():
            return candidate

    return None


def get_expression_label(expression):
    """表情・状態の表示名を返す"""
    labels = {
        "normal": "通常",
        "thinking": "考え中",
        "talking": "会話中",
    }
    return labels.get(str(expression or "normal"), "通常")


def load_character_image(expression="normal"):
    """キャラクター画像を読み込んで表示する"""
    global character_photo
    global current_character_expression

    expression = str(expression or "normal")
    current_character_expression = expression
    image_path = find_character_image_path(expression)

    if image_path is None:
        character_photo = None
        character_image_label.config(
            image="",
            text=(
                "Character Image\n\n"
                "character_image.png を\n"
                "プロジェクト直下に置くと\n"
                "ここに表示されます"
            ),
            fg=SUB_TEXT_COLOR,
        )
        character_image_path_var.set("画像: 未設定")
        character_status_var.set(f"{get_expression_label(expression)} / 画像未設定")
        return

    try:
        max_width = 340
        max_height = 260

        if Image is not None and ImageTk is not None:
            image = Image.open(image_path)
            image = image.convert("RGBA")

            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError:
                resample_filter = Image.LANCZOS

            image.thumbnail((max_width, max_height), resample_filter)
            character_photo = ImageTk.PhotoImage(image)
        else:
            photo = tk.PhotoImage(file=str(image_path))

            width = photo.width()
            height = photo.height()

            scale_width = max((width + max_width - 1) // max_width, 1)
            scale_height = max((height + max_height - 1) // max_height, 1)
            scale = max(scale_width, scale_height, 1)

            if scale > 1:
                photo = photo.subsample(scale, scale)

            character_photo = photo

        character_image_label.config(
            image=character_photo,
            text="",
            fg=TEXT_COLOR,
        )
        character_image_path_var.set(f"画像: {image_path}")
        character_status_var.set(get_expression_label(expression))

    except Exception as error:
        character_photo = None
        character_image_label.config(
            image="",
            text=(
                "画像を読み込めませんでした。\n"
                f"{error}\n\n"
                "Pillowを入れると改善することがあります。"
            ),
            fg=DANGER_DARK_COLOR,
        )
        character_image_path_var.set("画像: 読み込みエラー")
        character_status_var.set("画像読み込みエラー")


def reload_character_image():
    """キャラクター画像を再読み込みする"""
    load_character_image(current_character_expression)
    set_status("キャラクター画像を再読み込みしました。")


def set_character_expression(expression):
    """キャラクターの状態に応じて画像を切り替える"""
    load_character_image(expression)


def set_character_display_status(message):
    """キャラクター表示欄の状態テキストを更新する"""
    try:
        character_status_var.set(message)
    except Exception:
        pass


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

    stop_speech(show_message=False)
    root.destroy()


def set_status(message):
    """ステータスメッセージを更新する"""
    status_var.set(message)


def create_card(parent):
    return tk.Frame(
        parent,
        bg=PANEL_COLOR,
        bd=0,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1,
    )


def create_title_label(parent, text):
    return tk.Label(
        parent,
        text=text,
        font=("Meiryo", 13, "bold"),
        bg=PANEL_COLOR,
        fg=ACCENT_DARK_COLOR,
    )


def create_small_label(parent, text):
    return tk.Label(
        parent,
        text=text,
        font=("Meiryo", 9),
        bg=PANEL_COLOR,
        fg=SUB_TEXT_COLOR,
    )


def create_entry(parent, textvariable):
    return tk.Entry(
        parent,
        textvariable=textvariable,
        font=("Meiryo", 10),
        bg=INPUT_BG_COLOR,
        fg=TEXT_COLOR,
        insertbackground=TEXT_COLOR,
        relief="solid",
        bd=1,
    )


def create_text(parent, height=None, width=None, state="normal"):
    kwargs = {
        "font": ("Meiryo", 10),
        "wrap": "word",
        "bg": INPUT_BG_COLOR,
        "fg": TEXT_COLOR,
        "insertbackground": TEXT_COLOR,
        "relief": "solid",
        "bd": 1,
        "state": state,
    }

    if height is not None:
        kwargs["height"] = height

    if width is not None:
        kwargs["width"] = width

    return tk.Text(parent, **kwargs)


def create_button(parent, text, command, width=None, kind="primary"):
    if kind == "danger":
        bg_color = DANGER_COLOR
        active_bg = DANGER_DARK_COLOR
        fg_color = "#ffffff"
    elif kind == "secondary":
        bg_color = "#e7f4fb"
        active_bg = "#d2eaf6"
        fg_color = ACCENT_DARK_COLOR
    else:
        bg_color = BUTTON_COLOR
        active_bg = BUTTON_DARK_COLOR
        fg_color = "#ffffff"

    return tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        font=("Meiryo", 10),
        bg=bg_color,
        fg=fg_color,
        activebackground=active_bg,
        activeforeground=fg_color,
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=8,
        pady=4,
    )


# データ読み込み
profile = load_profile_from_file()
reply_rules = load_reply_rules_from_file()
memory = load_memory_from_file()
llm_settings = load_llm_settings_from_file()
voice_settings = load_voice_settings_from_file()
chat_history = load_chat_history()


# アプリのメインウィンドウ
root = tk.Tk()
root.title(APP_TITLE)
root.geometry("1060x780")
root.configure(bg=BG_COLOR)

style = ttk.Style()
style.theme_use("default")
style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
style.configure(
    "TNotebook.Tab",
    font=("Meiryo", 10),
    padding=(14, 8),
    background="#d9f0fb",
    foreground=TEXT_COLOR,
)
style.map(
    "TNotebook.Tab",
    background=[("selected", PANEL_COLOR)],
    foreground=[("selected", ACCENT_DARK_COLOR)],
)

# 変数
input_var = tk.StringVar()
search_var = tk.StringVar()
auto_speak_var = tk.BooleanVar(value=False)
latest_character_reply = ""

voice_engine_var = tk.StringVar(value=voice_settings["engine"])
voice_speaker_var = tk.StringVar(value=f"speaker id:{voice_settings['voicevox_speaker']}")
voice_speaker_map = {}

voice_speed_var = tk.StringVar(value=str(voice_settings["voicevox_speed_scale"]))
voice_volume_var = tk.StringVar(value=str(voice_settings["voicevox_volume_scale"]))
voice_intonation_var = tk.StringVar(value=str(voice_settings["voicevox_intonation_scale"]))
voice_pitch_var = tk.StringVar(value=str(voice_settings["voicevox_pitch_scale"]))

reply_mode_var = tk.StringVar(value=REPLY_MODE_RULE)
reply_mode_status_var = tk.StringVar(value="返答モード: ルールベース")

status_var = tk.StringVar(value="準備完了")
profile_summary_var = tk.StringVar()
count_var = tk.StringVar()
rule_count_var = tk.StringVar()
rules_status_var = tk.StringVar(value="ルール保存済み")
last_saved_rules_snapshot_var = tk.StringVar(value="")

rule_name_var = tk.StringVar()
rule_keywords_var = tk.StringVar()

character_photo = None
current_character_expression = "normal"
character_status_var = tk.StringVar(value="待機中")
character_image_path_var = tk.StringVar(value="画像: 未設定")

# ヘッダー
header_frame = tk.Frame(root, bg=HEADER_COLOR)
header_frame.pack(fill="x")

title_label = tk.Label(
    header_frame,
    text=f"Character Chat App {APP_VERSION}",
    font=("Meiryo", 19, "bold"),
    bg=HEADER_COLOR,
    fg=ACCENT_DARK_COLOR,
)
title_label.pack(pady=(13, 3))

subtitle_label = tk.Label(
    header_frame,
    text="キャラ設定・メモリ・OpenAI API・安定した音声読み上げを使って会話できるデスクトップアプリ",
    font=("Meiryo", 10),
    bg=HEADER_COLOR,
    fg=SUB_TEXT_COLOR,
)
subtitle_label.pack(pady=(0, 12))

# タブ領域
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both", padx=18, pady=14)

chat_tab = tk.Frame(notebook, bg=BG_COLOR)
profile_tab = tk.Frame(notebook, bg=BG_COLOR)
rules_tab = tk.Frame(notebook, bg=BG_COLOR)
voice_tab = tk.Frame(notebook, bg=BG_COLOR)
overview_tab = tk.Frame(notebook, bg=BG_COLOR)

notebook.add(chat_tab, text="チャット")
notebook.add(profile_tab, text="キャラ・メモリ")
notebook.add(rules_tab, text="返答ルール編集")
notebook.add(voice_tab, text="音声設定")
notebook.add(overview_tab, text="アプリ概要")

# チャットタブ
chat_main_frame = tk.Frame(chat_tab, bg=BG_COLOR)
chat_main_frame.pack(expand=True, fill="both", padx=14, pady=14)

chat_frame = create_card(chat_main_frame)
chat_frame.pack(side="left", expand=True, fill="both", padx=(0, 12), ipadx=14, ipady=14)

character_display_frame = create_card(chat_main_frame)
character_display_frame.pack(side="left", fill="y", ipadx=14, ipady=14)

create_title_label(character_display_frame, "キャラクター").pack(anchor="w", pady=(0, 8))

character_status_label = tk.Label(
    character_display_frame,
    textvariable=character_status_var,
    font=("Meiryo", 9),
    bg=PANEL_COLOR,
    fg=SUB_TEXT_COLOR,
)
character_status_label.pack(anchor="w", pady=(0, 8))

character_image_box = tk.Frame(
    character_display_frame,
    bg=PANEL_SOFT_COLOR,
    width=360,
    height=280,
    relief="solid",
    bd=1,
)
character_image_box.pack(pady=(0, 8))
character_image_box.pack_propagate(False)

character_image_label = tk.Label(
    character_image_box,
    text="Character Image",
    font=("Meiryo", 10),
    bg=PANEL_SOFT_COLOR,
    fg=SUB_TEXT_COLOR,
    justify="center",
)
character_image_label.pack(expand=True, fill="both")

character_image_path_label = tk.Label(
    character_display_frame,
    textvariable=character_image_path_var,
    font=("Meiryo", 8),
    bg=PANEL_COLOR,
    fg=SUB_TEXT_COLOR,
    wraplength=250,
    justify="left",
)
character_image_path_label.pack(anchor="w", pady=(0, 8))

create_button(
    character_display_frame,
    "画像を再読み込み",
    reload_character_image,
    width=18,
    kind="secondary",
).pack(anchor="w", pady=(0, 8))

character_image_hint_label = tk.Label(
    character_display_frame,
    text=(
        "使い方:\n"
        "character_image.png を置くと表示。\n"
        "差分を使う場合は\n"
        "character_normal.png\n"
        "character_thinking.png\n"
        "character_talking.png\n"
        "を追加します。"
    ),
    font=("Meiryo", 8),
    bg=PANEL_COLOR,
    fg=SUB_TEXT_COLOR,
    justify="left",
    wraplength=250,
)
character_image_hint_label.pack(anchor="w")

chat_header = tk.Frame(chat_frame, bg=PANEL_COLOR)
chat_header.pack(fill="x", pady=(0, 10))

create_title_label(chat_header, "チャット").pack(side="left")

count_label = tk.Label(
    chat_header,
    textvariable=count_var,
    font=("Meiryo", 9),
    bg=PANEL_COLOR,
    fg=SUB_TEXT_COLOR,
)
count_label.pack(side="right")

mode_frame = tk.Frame(chat_frame, bg=PANEL_COLOR)
mode_frame.pack(fill="x", pady=(0, 10))

create_small_label(mode_frame, "返答モード").pack(side="left", padx=(0, 8))

reply_mode_combobox = ttk.Combobox(
    mode_frame,
    textvariable=reply_mode_var,
    values=[REPLY_MODE_RULE, REPLY_MODE_MOCK_LLM, REPLY_MODE_OPENAI],
    state="readonly",
    width=16,
    font=("Meiryo", 9),
)
reply_mode_combobox.pack(side="left")
reply_mode_combobox.bind("<<ComboboxSelected>>", on_reply_mode_changed)

reply_mode_status_label = tk.Label(
    mode_frame,
    textvariable=reply_mode_status_var,
    font=("Meiryo", 9),
    bg=PANEL_COLOR,
    fg=SUB_TEXT_COLOR,
)
reply_mode_status_label.pack(side="left", padx=10)

mode_hint_label = tk.Label(
    mode_frame,
    text="rule=従来の返答 / mock_llm=疑似LLM / openai=短めOpenAI返答",
    font=("Meiryo", 8),
    bg=PANEL_COLOR,
    fg=SUB_TEXT_COLOR,
)
mode_hint_label.pack(side="left", padx=8)


speech_frame = tk.Frame(chat_frame, bg=PANEL_COLOR)
speech_frame.pack(fill="x", pady=(0, 10))

auto_speak_check = tk.Checkbutton(
    speech_frame,
    text="自動読み上げ",
    variable=auto_speak_var,
    font=("Meiryo", 9),
    bg=PANEL_COLOR,
    fg=TEXT_COLOR,
    activebackground=PANEL_COLOR,
    activeforeground=TEXT_COLOR,
    selectcolor=PANEL_SOFT_COLOR,
)
auto_speak_check.pack(side="left", padx=(0, 8))

create_small_label(speech_frame, "音声エンジン").pack(side="left", padx=(8, 4))

voice_engine_combobox = ttk.Combobox(
    speech_frame,
    textvariable=voice_engine_var,
    values=["windows", "voicevox"],
    state="readonly",
    width=10,
    font=("Meiryo", 9),
)
voice_engine_combobox.pack(side="left", padx=(0, 8))

create_button(
    speech_frame,
    "最新返答を読み上げ",
    speak_latest_reply,
    width=18,
    kind="secondary",
).pack(side="left", padx=4)

create_button(
    speech_frame,
    "読み上げ停止",
    stop_speech,
    width=12,
    kind="secondary",
).pack(side="left", padx=4)

create_button(
    speech_frame,
    "音声設定タブへ",
    lambda: notebook.select(voice_tab),
    width=14,
    kind="secondary",
).pack(side="left", padx=4)

search_frame = tk.Frame(chat_frame, bg=PANEL_COLOR)
search_frame.pack(fill="x", pady=(0, 10))

search_entry = create_entry(search_frame, search_var)
search_entry.pack(side="left", expand=True, fill="x", padx=(0, 8))

create_button(search_frame, "履歴検索", search_history, width=10, kind="secondary").pack(side="left", padx=4)
create_button(search_frame, "検索クリア", clear_search, width=10, kind="secondary").pack(side="left", padx=4)

chat_text = create_text(chat_frame, state="disabled")
chat_text.config(
    bg="#fbfdff",
    relief="flat",
    bd=0,
    padx=10,
    pady=10,
)
chat_text.pack(expand=True, fill="both", pady=(0, 10))

input_hint_label = tk.Label(
    chat_frame,
    text="メッセージを入力してEnter、または送信ボタンで会話できます。",
    font=("Meiryo", 8),
    bg=PANEL_COLOR,
    fg=SUB_TEXT_COLOR,
)
input_hint_label.pack(anchor="w", pady=(0, 4))

input_frame = tk.Frame(chat_frame, bg=PANEL_COLOR)
input_frame.pack(fill="x")

input_entry = create_entry(input_frame, input_var)
input_entry.config(font=("Meiryo", 11))
input_entry.pack(side="left", expand=True, fill="x", padx=(0, 8))

create_button(input_frame, "送信", send_message, width=10).pack(side="left", padx=4)
create_button(input_frame, "入力クリア", clear_input, width=10, kind="secondary").pack(side="left", padx=4)

chat_shortcut_frame = tk.Frame(chat_frame, bg=PANEL_COLOR)
chat_shortcut_frame.pack(anchor="w", pady=(10, 0))

create_button(
    chat_shortcut_frame,
    "キャラから話しかける",
    add_starter_message,
    width=18,
    kind="secondary",
).grid(row=0, column=0, padx=(0, 8))

create_button(
    chat_shortcut_frame,
    "LLMプロンプト確認",
    open_llm_prompt_window,
    width=18,
    kind="secondary",
).grid(row=0, column=1, padx=8)

create_button(
    chat_shortcut_frame,
    "LLM設定確認",
    open_llm_settings_window,
    width=18,
    kind="secondary",
).grid(row=0, column=2, padx=8)

# キャラ・メモリタブ
profile_main_frame = tk.Frame(profile_tab, bg=BG_COLOR)
profile_main_frame.pack(expand=True, fill="both", padx=14, pady=14)

character_frame = create_card(profile_main_frame)
character_frame.pack(side="left", expand=True, fill="both", padx=(0, 14), ipadx=14, ipady=14)

create_title_label(character_frame, "キャラ設定").pack(anchor="w", pady=(0, 10))

profile_summary_label = tk.Label(
    character_frame,
    textvariable=profile_summary_var,
    font=("Meiryo", 10),
    bg=PANEL_COLOR,
    fg=TEXT_COLOR,
    justify="left",
    wraplength=420,
)
profile_summary_label.pack(anchor="w", pady=(0, 10))

personality_preview_text = create_text(character_frame, height=18, state="disabled")
personality_preview_text.pack(expand=True, fill="both", pady=(0, 10))

create_button(
    character_frame,
    "キャラ設定を再読み込み",
    reload_profile,
    width=24,
    kind="secondary",
).pack(anchor="w", pady=(0, 6))

memory_frame = create_card(profile_main_frame)
memory_frame.pack(side="left", expand=True, fill="both", ipadx=14, ipady=14)

create_title_label(memory_frame, "メモリ").pack(anchor="w", pady=(0, 10))

memory_summary_text = create_text(memory_frame, height=24, state="disabled")
memory_summary_text.pack(expand=True, fill="both", pady=(0, 10))

memory_button_frame = tk.Frame(memory_frame, bg=PANEL_COLOR)
memory_button_frame.pack(anchor="w")

create_button(memory_button_frame, "メモリ編集", open_memory_window, width=14).grid(row=0, column=0, padx=(0, 6))
create_button(memory_button_frame, "メモリ再読み込み", reload_memory, width=16, kind="secondary").grid(row=0, column=1, padx=6)
create_button(memory_button_frame, "会話履歴を削除", clear_history, width=16, kind="danger").grid(row=0, column=2, padx=6)

# 返答ルール編集タブ
rules_main_frame = tk.Frame(rules_tab, bg=BG_COLOR)
rules_main_frame.pack(expand=True, fill="both", padx=14, pady=14)

rules_list_frame = create_card(rules_main_frame)
rules_list_frame.pack(side="left", fill="both", padx=(0, 14), ipadx=14, ipady=14)

create_title_label(rules_list_frame, "返答ルール一覧").pack(anchor="w", pady=(0, 8))

rule_count_label = tk.Label(
    rules_list_frame,
    textvariable=rule_count_var,
    font=("Meiryo", 9),
    bg=PANEL_COLOR,
    fg=SUB_TEXT_COLOR,
)
rule_count_label.pack(anchor="w", pady=(0, 4))

rules_status_label = tk.Label(
    rules_list_frame,
    textvariable=rules_status_var,
    font=("Meiryo", 9),
    bg=PANEL_COLOR,
    fg=SUB_TEXT_COLOR,
)
rules_status_label.pack(anchor="w", pady=(0, 8))

rule_listbox = tk.Listbox(
    rules_list_frame,
    font=("Meiryo", 9),
    width=42,
    activestyle="dotbox",
    bg=INPUT_BG_COLOR,
    fg=TEXT_COLOR,
    selectbackground="#bfe7fa",
    selectforeground=TEXT_COLOR,
    relief="solid",
    bd=1,
)
rule_listbox.pack(expand=True, fill="both", pady=(0, 8))
rule_listbox.bind("<<ListboxSelect>>", on_rule_selected)

rules_list_button_frame = tk.Frame(rules_list_frame, bg=PANEL_COLOR)
rules_list_button_frame.pack(anchor="w")

create_button(
    rules_list_button_frame,
    "返答ルール再読み込み",
    reload_reply_rules,
    width=20,
    kind="secondary",
).grid(row=0, column=0, padx=(0, 6))

create_button(
    rules_list_button_frame,
    "ルール保存",
    save_reply_rules,
    width=12,
).grid(row=0, column=1, padx=6)

rules_editor_frame = create_card(rules_main_frame)
rules_editor_frame.pack(side="left", expand=True, fill="both", ipadx=14, ipady=14)

create_title_label(rules_editor_frame, "返答ルール編集").pack(anchor="w", pady=(0, 10))

create_small_label(rules_editor_frame, "ルール名").pack(anchor="w")
rule_name_entry = create_entry(rules_editor_frame, rule_name_var)
rule_name_entry.pack(fill="x", pady=(2, 8))

create_small_label(rules_editor_frame, "キーワード（カンマ区切り）").pack(anchor="w")
rule_keywords_entry = create_entry(rules_editor_frame, rule_keywords_var)
rule_keywords_entry.pack(fill="x", pady=(2, 8))

create_small_label(rules_editor_frame, "返答候補（複数候補は --- の行で区切る）").pack(anchor="w")
rule_replies_text = create_text(rules_editor_frame, height=18)
rule_replies_text.pack(expand=True, fill="both", pady=(2, 8))

rule_button_frame = tk.Frame(rules_editor_frame, bg=PANEL_COLOR)
rule_button_frame.pack(anchor="w", pady=(0, 8))

create_button(rule_button_frame, "新規", clear_rule_editor, width=8, kind="secondary").grid(row=0, column=0, padx=3)
create_button(rule_button_frame, "追加/更新", add_or_update_rule, width=10).grid(row=0, column=1, padx=3)
create_button(rule_button_frame, "削除", delete_rule, width=8, kind="danger").grid(row=0, column=2, padx=3)

rule_hint_label = tk.Label(
    rules_editor_frame,
    text=(
        "使える変数: {character_name}, {first_person}, {user_call}, {relationship}, "
        "{user_name}, {current_goal}, {recent_progress}, {memory_topics}, {memory_notes}"
    ),
    font=("Meiryo", 8),
    bg=PANEL_COLOR,
    fg=SUB_TEXT_COLOR,
    justify="left",
    wraplength=560,
)
rule_hint_label.pack(anchor="w")

# --------------------
# 音声設定タブ
# --------------------
voice_main_frame = create_card(voice_tab)
voice_main_frame.pack(expand=True, fill="both", padx=14, pady=14, ipadx=14, ipady=14)

create_title_label(voice_main_frame, "音声設定").pack(anchor="w", pady=(0, 10))

voice_description_label = tk.Label(
    voice_main_frame,
    text=(
        "VOICEVOXの話者・話速・音量・抑揚・高さを調整できます。"
        "数値を変えたら「音声設定保存」を押してね。"
    ),
    font=("Meiryo", 9),
    bg=PANEL_COLOR,
    fg=SUB_TEXT_COLOR,
    justify="left",
    wraplength=860,
)
voice_description_label.pack(anchor="w", pady=(0, 12))

voice_engine_frame = tk.Frame(voice_main_frame, bg=PANEL_COLOR)
voice_engine_frame.pack(fill="x", pady=(0, 10))

create_small_label(voice_engine_frame, "音声エンジン").pack(side="left", padx=(0, 8))

voice_engine_combobox_voice_tab = ttk.Combobox(
    voice_engine_frame,
    textvariable=voice_engine_var,
    values=["windows", "voicevox"],
    state="readonly",
    width=12,
    font=("Meiryo", 9),
)
voice_engine_combobox_voice_tab.pack(side="left", padx=(0, 12))

create_button(
    voice_engine_frame,
    "VOICEVOX接続確認",
    check_voicevox_connection,
    width=16,
    kind="secondary",
).pack(side="left", padx=4)

create_button(
    voice_engine_frame,
    "話者取得",
    refresh_voicevox_speakers,
    width=10,
    kind="secondary",
).pack(side="left", padx=4)

speaker_frame = tk.Frame(voice_main_frame, bg=PANEL_COLOR)
speaker_frame.pack(fill="x", pady=(0, 14))

create_small_label(speaker_frame, "VOICEVOX話者").pack(anchor="w", pady=(0, 4))

voice_speaker_combobox = ttk.Combobox(
    speaker_frame,
    textvariable=voice_speaker_var,
    values=[],
    state="readonly",
    width=58,
    font=("Meiryo", 9),
)
voice_speaker_combobox.pack(anchor="w")
voice_speaker_combobox.bind("<<ComboboxSelected>>", on_voicevox_speaker_changed)

settings_grid = tk.Frame(voice_main_frame, bg=PANEL_COLOR)
settings_grid.pack(anchor="w", pady=(0, 14))

def add_voice_setting_row(row, label_text, variable, from_value, to_value, increment, hint):
    label = create_small_label(settings_grid, label_text)
    label.grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)

    spinbox = tk.Spinbox(
        settings_grid,
        from_=from_value,
        to=to_value,
        increment=increment,
        textvariable=variable,
        width=8,
        font=("Meiryo", 10),
    )
    spinbox.grid(row=row, column=1, sticky="w", padx=(0, 10), pady=5)

    hint_label = tk.Label(
        settings_grid,
        text=hint,
        font=("Meiryo", 8),
        bg=PANEL_COLOR,
        fg=SUB_TEXT_COLOR,
    )
    hint_label.grid(row=row, column=2, sticky="w", pady=5)

add_voice_setting_row(0, "話速", voice_speed_var, 0.5, 2.0, 0.1, "標準 1.0。大きいほど速くなります。")
add_voice_setting_row(1, "音量", voice_volume_var, 0.0, 2.0, 0.1, "標準 1.0。大きいほど大きくなります。")
add_voice_setting_row(2, "抑揚", voice_intonation_var, 0.0, 2.0, 0.1, "標準 1.0。大きいほど表情が強くなります。")
add_voice_setting_row(3, "高さ", voice_pitch_var, -0.15, 0.15, 0.01, "標準 0.0。少しずつ変えるのがおすすめです。")

voice_button_frame = tk.Frame(voice_main_frame, bg=PANEL_COLOR)
voice_button_frame.pack(anchor="w", pady=(4, 0))

create_button(
    voice_button_frame,
    "音声設定保存",
    save_voice_settings_from_ui,
    width=14,
).grid(row=0, column=0, padx=(0, 8))

create_button(
    voice_button_frame,
    "最新返答を読み上げ",
    speak_latest_reply,
    width=18,
    kind="secondary",
).grid(row=0, column=1, padx=8)

create_button(
    voice_button_frame,
    "読み上げ停止",
    stop_speech,
    width=12,
    kind="secondary",
).grid(row=0, column=2, padx=8)

voice_note_label = tk.Label(
    voice_main_frame,
    text=(
        "補足: 音声設定はVOICEVOX読み上げ時に反映されます。"
        "Windows標準音声では話速・抑揚などは反映されません。"
    ),
    font=("Meiryo", 8),
    bg=PANEL_COLOR,
    fg=SUB_TEXT_COLOR,
    justify="left",
    wraplength=860,
)
voice_note_label.pack(anchor="w", pady=(14, 0))


# --------------------
# アプリ概要タブ
# --------------------
overview_frame = create_card(overview_tab)
overview_frame.pack(expand=True, fill="both", padx=14, pady=14, ipadx=18, ipady=18)

create_title_label(overview_frame, "Character Chat App v4.0").pack(anchor="w", pady=(0, 10))

overview_intro_label = tk.Label(
    overview_frame,
    text=(
        "キャラクター設定・メモリ・OpenAI API・VOICEVOX・画像表示を組み合わせた、"
        "自分用のキャラクター会話アプリです。\n"
        "v4.0では、GitHubや成果物として見せやすいように機能構成と説明を整理しています。"
    ),
    font=("Meiryo", 10),
    bg=PANEL_COLOR,
    fg=TEXT_COLOR,
    justify="left",
    wraplength=860,
)
overview_intro_label.pack(anchor="w", pady=(0, 14))

overview_content = tk.Text(
    overview_frame,
    font=("Meiryo", 10),
    wrap="word",
    bg=INPUT_BG_COLOR,
    fg=TEXT_COLOR,
    relief="solid",
    bd=1,
    height=22,
    padx=10,
    pady=10,
)
overview_content.pack(expand=True, fill="both", pady=(0, 12))

overview_text = """主な機能

1. キャラクター会話
- character_profile.json からキャラクター設定を読み込みます。
- 返答モードは rule / mock_llm / openai を切り替えられます。
- OpenAI APIを使うと、キャラ設定・メモリ・直近履歴を反映した返答を生成します。

2. メモリ
- memory.json にユーザーの目標や進捗を保存します。
- 一部の発言から簡単なメモリ自動更新を行います。

3. 音声読み上げ
- Windows標準音声とVOICEVOXを切り替えられます。
- VOICEVOXでは話者・スタイルを選択できます。
- 話速・音量・抑揚・高さを音声設定タブから調整できます。

4. キャラクター画像
- character_image.png を置くとチャット画面右側に表示されます。
- character_normal.png / character_thinking.png / character_talking.png による状態別表示にも対応しています。

5. UI
- チャット欄はユーザー発言とキャラ発言を見分けやすく表示します。
- チャット・キャラ/メモリ・返答ルール・音声設定・アプリ概要をタブで整理しています。

今後の拡張候補

- 表情差分の追加
- 音声再生中の簡易アニメーション
- 会話履歴の要約
- RAG連携
- 実行ファイル化
- READMEへのスクリーンショット追加
"""

overview_content.insert("1.0", overview_text)
overview_content.config(state="disabled")

overview_button_frame = tk.Frame(overview_frame, bg=PANEL_COLOR)
overview_button_frame.pack(anchor="w")

create_button(
    overview_button_frame,
    "チャットへ移動",
    lambda: notebook.select(chat_tab),
    width=14,
).grid(row=0, column=0, padx=(0, 8))

create_button(
    overview_button_frame,
    "音声設定へ移動",
    lambda: notebook.select(voice_tab),
    width=14,
    kind="secondary",
).grid(row=0, column=1, padx=8)


# ステータスバー
status_label = tk.Label(
    root,
    textvariable=status_var,
    font=("Meiryo", 9),
    bg=BG_COLOR,
    fg=SUB_TEXT_COLOR,
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
update_reply_mode_label()
load_character_image("normal")
set_status(f"{profile['character_name']} の設定・返答ルール・メモリを読み込みました。v4.0として成果物表示を整理しました。")

# アプリ起動
root.mainloop()
