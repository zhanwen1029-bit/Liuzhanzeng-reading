import streamlit as st
import streamlit.components.v1 as components
import re
import html
import os
import csv
import json
import time
import pandas as pd
from datetime import datetime
from urllib.parse import quote

st.set_page_config(page_title="《82岁名模——刘占增》", layout="wide")

# =========================
# 基础配置
# =========================
TITLE = "《82岁名模——刘占增》"

TEXT = """他毕业于北京大学医学院，会英、德、日三种外语，在联合国做过翻译。退休后，他当了一名人体模特。这个人就是刘占增。

今年82岁的刘占增，是美术界里的名模。画家们有一句话：你要是没画过刘占增，你就不算是画家。

刘大爷从小就喜欢艺术。退休那年，天津美院招模特，刘占增被录取了。开始，刘大爷的家人，看他整天很忙碌，还以为老人被学校聘用教课了呢。知道真实情况后，儿子生气地对他说：“爸爸，我可以理解你，可社会上不懂的人多，他们不理解啊！我要是谈恋爱，告诉人家你是干人体模特的，人家可能就不跟我好了！”

但刘占增铁了心要按照自己的心意生活。老伴告诉他：“当模特可以，只能当肖像模特，不能当裸体的。”刘占增当时一笑，什么都没说。

当了几个月肖像模特后，一位美院的老师说：“像您这样的身体和气质，在全国都很难找，您又不是年轻小姑娘，不做人体模特可惜了。”被这位老师这么一说，刘占增决定为艺术“献身”。刚开始，面对和他孙女一般大的女学生们，刘占增觉得脱光衣服实在不好意思。可是同学们对他身体的赞美，让他找到了新的价值，并对自己的身体越来越自信。

刘占增做人体模特是偷偷的，不敢告诉老伴。但遇到以自己为模特的作品在画展中获奖，或被收进画册时，他就会忍不住地高兴。有一次，他把从学生那里得到的画，拿回家挂在墙上，气得老伴直骂他。老伴把画拿下来，他又挂上去……

一次，美院来了一对美国夫妻，翻译不在，刘占增就自己翻译。这对美国夫妻说：“中国到处是人才。”以后，他就经常帮美院老师们做一些翻译工作。

这样的生活，他感到很充实。老伴说他退休后，像是才开始工作。他说自己很幸福，因为年轻时的理想，在退休后都实现了。“我为自己活着，不管那么多！要不，多累啊！”说这话时，老人笑了。"""

GLOSSES = {
    "退休": "不再继续原来的工作，离开工作岗位。English: retire",
    "录取": "经过考核后被正式接受。English: admit",
    "忙碌": "事情很多，很忙。English: busy",
    "聘用": "正式请某人来工作。English: hire",
    "模特": "供艺术创作或服装展示的人。English: model",
    "肖像": "以人物形象为对象的绘画或照片。English: portrait",
    "献身": "把自己全部投入某种事业或目标。English: devote oneself to",
    "画册": "收集绘画作品的册子。English: art album",
    "画展": "公开展出绘画作品的展览。English: art exhibition",
    "充实": "内容丰富，内心满足。English: fulfilling",
}
TERMS = sorted(GLOSSES.keys(), key=len, reverse=True)

# =========================
# 题目配置
# =========================

# 前测：词汇配对
PRETEST_WORDS = [
    "退休", "录取", "忙碌", "聘用", "模特",
    "肖像", "献身", "画册", "画展", "充实"
]
PRETEST_OPTIONS = {
    "A": "art album",
    "B": "devote oneself to",
    "C": "busy",
    "D": "fulfilling",
    "E": "model",
    "F": "portrait",
    "G": "admit",
    "H": "retire",
    "I": "art exhibition",
    "J": "hire",
}
PRETEST_ANSWERS = {
    "退休": "H",
    "录取": "G",
    "忙碌": "C",
    "聘用": "J",
    "模特": "E",
    "肖像": "F",
    "献身": "B",
    "画册": "A",
    "画展": "I",
    "充实": "D",
}

# 即时测 / 延后测（完全一致）
VOCAB_QS = [
    {
        "id": "v1",
        "target": "退休",
        "stem": "他退休后，像是才开始工作。",
        "options": {"A": "retire", "B": "graduate", "C": "resign", "D": "travel"},
        "answer": "A",
    },
    {
        "id": "v2",
        "target": "录取",
        "stem": "天津美院招模特，他被录取了。",
        "options": {"A": "reject", "B": "admit", "C": "ignore", "D": "cancel"},
        "answer": "B",
    },
    {
        "id": "v3",
        "target": "忙碌",
        "stem": "家人看他整天很忙碌。",
        "options": {"A": "bored", "B": "busy", "C": "relaxed", "D": "angry"},
        "answer": "B",
    },
    {
        "id": "v4",
        "target": "聘用",
        "stem": "家人以为他被学校聘用教课。",
        "options": {"A": "fire", "B": "hire", "C": "punish", "D": "forbid"},
        "answer": "B",
    },
    {
        "id": "v5",
        "target": "模特",
        "stem": "退休后，他当了一名人体模特。",
        "options": {"A": "model", "B": "customer", "C": "painter", "D": "doctor"},
        "answer": "A",
    },
    {
        "id": "v6",
        "target": "肖像",
        "stem": "只能当肖像模特，不能当裸体的。",
        "options": {"A": "portrait", "B": "landscape", "C": "poem", "D": "furniture"},
        "answer": "A",
    },
    {
        "id": "v7",
        "target": "献身",
        "stem": "他决定为艺术‘献身’。",
        "options": {"A": "complain", "B": "devote oneself to", "C": "give up", "D": "show off"},
        "answer": "B",
    },
    {
        "id": "v8",
        "target": "画册",
        "stem": "作品被收进画册时，他很高兴。",
        "options": {"A": "art album", "B": "dictionary", "C": "ticket", "D": "newspaper"},
        "answer": "A",
    },
    {
        "id": "v9",
        "target": "画展",
        "stem": "作品在画展中获奖。",
        "options": {"A": "art exhibition", "B": "dance show", "C": "book fair", "D": "music class"},
        "answer": "A",
    },
    {
        "id": "v10",
        "target": "充实",
        "stem": "这样的生活，他感到很充实。",
        "options": {"A": "noisy", "B": "fulfilling", "C": "dangerous", "D": "embarrassing"},
        "answer": "B",
    },
]

# 阅读理解
READING_QS = [
    {
        "id": "r1",
        "stem": "【概要重述 1】儿子反对，是因为：",
        "options": {
            "A": "担心找不到女朋友",
            "B": "担心女朋友不跟他结婚",
            "C": "担心女朋友看不起爸爸",
            "D": "担心女朋友也想当模特"
        },
        "answer": "B",
    },
    {
        "id": "r2",
        "stem": "【概要重述 2】但刘占增在老师的鼓励下，还是为艺术：",
        "options": {
            "A": "当了模特",
            "B": "当了肖像模特",
            "C": "“牺牲”",
            "D": "不干"
        },
        "answer": "C",
    },
    {
        "id": "r3",
        "stem": "【概要重述 3】刚开始，面对女学生们，刘占增觉得脱光衣服：",
        "options": {
            "A": "不舒服",
            "B": "不好意思",
            "C": "丢脸",
            "D": "害羞"
        },
        "answer": "B",
    },
    {
        "id": "r4",
        "stem": "【概要重述 4】遇到以自己为模特的作品在画展中获奖，他就会：",
        "options": {
            "A": "告诉别人",
            "B": "挂出来给人看",
            "C": "拿到外面展览",
            "D": "忍不住地高兴"
        },
        "answer": "D",
    },
    {
        "id": "r5",
        "stem": "【概要重述 5】这样的生活，让他感到很充实，老伴说他退休后：",
        "options": {
            "A": "爱好吃喝",
            "B": "对工作没兴趣了",
            "C": "像刚刚开始工作",
            "D": "改变了原来的爱好"
        },
        "answer": "C",
    },
    {
        "id": "r6",
        "stem": "【内容理解 1】第[4]段中“铁了心”的意思是：",
        "options": {
            "A": "心很硬",
            "B": "变了心",
            "C": "心意坚定",
            "D": "改变想法"
        },
        "answer": "C",
    },
    {
        "id": "r7",
        "stem": "【内容理解 2】刘占增那次在美院为什么给美国夫妻当翻译？",
        "options": {
            "A": "他会外语",
            "B": "他想当翻译",
            "C": "当时翻译不在",
            "D": "美国人让他当翻译"
        },
        "answer": "C",
    },
    {
        "id": "r8",
        "stem": "【内容理解 3】关于刘占增，下面哪种说法不对？",
        "options": {
            "A": "身体素质很好",
            "B": "艺术修养很高",
            "C": "当模特是因为爱好",
            "D": "原来的工作不好"
        },
        "answer": "D",
    },
    {
        "id": "r9",
        "stem": "【内容理解 4】这篇文章的主要意思是：",
        "options": {
            "A": "中国改革开放的变化",
            "B": "刘占增的模特经历",
            "C": "什么人可以当模特",
            "D": "刘占增的退休生活"
        },
        "answer": "B",
    },
    {
        "id": "r10",
        "stem": "【句意理解 1】“你要是没画过刘占增，你就不算是画家。”这句话的意思是：",
        "options": {
            "A": "说明刘占增很重要",
            "B": "说明画家很多",
            "C": "说明画家都认识刘占增",
            "D": "说明画什么很重要"
        },
        "answer": "A",
    },
    {
        "id": "r11",
        "stem": "【句意理解 2】“我要是谈恋爱，告诉人家你是干人体模特的，人家可能就不跟我好了！”这句话的意思是：",
        "options": {
            "A": "别人看不起刘占增",
            "B": "儿子看不起刘占增",
            "C": "儿子当不了人体模特",
            "D": "爸爸当人体模特很丢人"
        },
        "answer": "D",
    },
    {
        "id": "r12",
        "stem": "【句意理解 3】“刘占增做人体模特是偷偷的，不敢告诉老伴。”这句话的意思是：",
        "options": {
            "A": "刘占增害怕别人偷东西",
            "B": "刘占增衣服被偷了",
            "C": "刘占增当人体模特不想让别人知道",
            "D": "刘占增不知道怎样当人体模特"
        },
        "answer": "C",
    },
]

# 感知问卷
SURVEY_ITEMS = [
    ("q1", "我能比较容易地找到目标词的注释。"),
    ("q2", "查看注释不会让我感到操作麻烦。"),
    ("q3", "这种注释方式会影响我阅读正文的连贯性。"),
    ("q4", "我在阅读过程中能够较自然地在正文和注释之间切换。"),
    ("q5", "总体来说，我能够接受这种注释方式。"),
    ("q6", "如果以后继续使用数字化阅读材料，我愿意使用这种注释方式。"),
]

# =========================
# 数据文件
# =========================
DATA_DIR = "data"
PROGRESS_DIR = os.path.join(DATA_DIR, "progress")
LOG_DIR = os.path.join(DATA_DIR, "logs")
os.makedirs(PROGRESS_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

EVENT_FILE = os.path.join(LOG_DIR, "events.csv")
SURVEY_FILE = os.path.join(LOG_DIR, "survey.csv")
SCORE_FILE = os.path.join(LOG_DIR, "scores.csv")

def ensure_csv(path, headers):
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

ensure_csv(EVENT_FILE, [
    "timestamp", "participant_id", "mode", "stage", "event_type", "item_id",
    "value", "elapsed_since_last_sec"
])
ensure_csv(SURVEY_FILE, [
    "timestamp", "participant_id", "mode", "q1", "q2", "q3", "q4", "q5", "q6", "comment"
])
ensure_csv(SCORE_FILE, [
    "timestamp", "participant_id", "mode", "stage", "score", "max_score"
])

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def now_ts():
    return time.time()

def progress_path(pid):
    return os.path.join(PROGRESS_DIR, f"{pid}.json")

def load_progress(pid):
    path = progress_path(pid)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "participant_id": pid,
        "mode": "",
        "current_stage": "pretest",
        "pretest_answers": {},
        "reading_done": False,
        "immediate_vocab_answers": {},
        "reading_answers": {},
        "survey_answers": {},
        "survey_comment": "",
        "survey_done": False,
        "delayed_vocab_answers": {},
        "last_event_ts": now_ts()
    }

def save_progress(data):
    with open(progress_path(data["participant_id"]), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def log_event(pid, mode, stage, event_type, item_id="", value=""):
    prog_local = load_progress(pid)
    current_ts = now_ts()
    elapsed = round(current_ts - prog_local.get("last_event_ts", current_ts), 2)
    prog_local["last_event_ts"] = current_ts
    save_progress(prog_local)
    with open(EVENT_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([now_str(), pid, mode, stage, event_type, item_id, value, elapsed])

def log_score(pid, mode, stage, score, max_score):
    with open(SCORE_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([now_str(), pid, mode, stage, score, max_score])

# =========================
# Query 参数
# =========================
query = st.query_params

teacher = str(query.get("teacher", "0")) == "1"

mode = query.get("mode", "popup")
if isinstance(mode, list):
    mode = mode[0]
if mode not in ["popup", "sidebar", "endnote"]:
    mode = "popup"

pid = query.get("pid", "")
if isinstance(pid, list):
    pid = pid[0]

term = query.get("term", "")
if isinstance(term, list):
    term = term[0]

evt = query.get("evt", "")
if isinstance(evt, list):
    evt = evt[0]

# =========================
# 教师端
# =========================
if teacher:
    st.title("教师端记录查看")

    df_events = pd.read_csv(EVENT_FILE) if os.path.exists(EVENT_FILE) else pd.DataFrame()
    df_survey = pd.read_csv(SURVEY_FILE) if os.path.exists(SURVEY_FILE) else pd.DataFrame()
    df_scores = pd.read_csv(SCORE_FILE) if os.path.exists(SCORE_FILE) else pd.DataFrame()

    progress_rows = []
    for fn in os.listdir(PROGRESS_DIR):
        if fn.endswith(".json"):
            with open(os.path.join(PROGRESS_DIR, fn), "r", encoding="utf-8") as f:
                p = json.load(f)
            progress_rows.append({
                "participant_id": p["participant_id"],
                "mode": p.get("mode", ""),
                "current_stage": p.get("current_stage", ""),
                "reading_done": p.get("reading_done", False),
                "survey_done": p.get("survey_done", False),
                "pretest_done_items": len(p.get("pretest_answers", {})),
                "immediate_vocab_done_items": len(p.get("immediate_vocab_answers", {})),
                "reading_done_items": len(p.get("reading_answers", {})),
                "delayed_vocab_done_items": len(p.get("delayed_vocab_answers", {})),
            })
    df_progress = pd.DataFrame(progress_rows)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("参与者人数", len(df_progress) if not df_progress.empty else 0)
    with c2:
        click_count = len(df_events[df_events["event_type"] == "gloss_click"]) if not df_events.empty else 0
        st.metric("注释点击总次数", click_count)
    with c3:
        survey_count = len(df_survey) if not df_survey.empty else 0
        st.metric("已提交问卷数", survey_count)
    with c4:
        finished_count = len(df_progress[df_progress["current_stage"] == "finished"]) if not df_progress.empty else 0
        st.metric("已完成全部阶段", finished_count)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["进度", "分数统计", "行为日志", "问卷结果", "下载数据"])

    with tab1:
        st.subheader("参与者进度")
        if not df_progress.empty:
            st.dataframe(df_progress, use_container_width=True)
        else:
            st.info("暂无进度数据。")

    with tab2:
        st.subheader("分数统计")
        if not df_scores.empty:
            st.dataframe(df_scores, use_container_width=True)

            st.markdown("#### 各阶段平均分（按模式）")
            score_summary = (
                df_scores.groupby(["mode", "stage"])["score"]
                .mean()
                .reset_index()
                .rename(columns={"score": "avg_score"})
            )
            st.dataframe(score_summary, use_container_width=True)

            st.markdown("#### 各阶段平均分（按模式和样本量）")
            score_summary2 = (
                df_scores.groupby(["mode", "stage"])
                .agg(avg_score=("score", "mean"), avg_max_score=("max_score", "mean"), n=("score", "count"))
                .reset_index()
            )
            st.dataframe(score_summary2, use_container_width=True)
        else:
            st.info("暂无分数数据。")

    with tab3:
        st.subheader("行为日志")
        if not df_events.empty:
            st.dataframe(df_events, use_container_width=True)

            click_df = df_events[df_events["event_type"] == "gloss_click"]
            if not click_df.empty:
                st.markdown("#### 注释点击次数统计")
                click_summary = (
                    click_df.groupby(["participant_id", "mode"])
                    .size()
                    .reset_index(name="click_count")
                )
                st.dataframe(click_summary, use_container_width=True)
            else:
                st.info("当前版本中，侧边式可记录注释点击；弹窗式为页内弹窗，不做稳定点击回传。")
        else:
            st.info("暂无行为日志。")

    with tab4:
        st.subheader("问卷结果")
        if not df_survey.empty:
            st.dataframe(df_survey, use_container_width=True)

            likert_cols = ["q1", "q2", "q3", "q4", "q5", "q6"]
            if all(col in df_survey.columns for col in likert_cols):
                st.markdown("#### 问卷均值（按模式）")
                survey_summary = (
                    df_survey.groupby("mode")[likert_cols]
                    .mean()
                    .reset_index()
                )
                st.dataframe(survey_summary, use_container_width=True)
        else:
            st.info("暂无问卷数据。")

    with tab5:
        st.subheader("下载数据")
        if not df_progress.empty:
            st.download_button(
                "下载进度数据 CSV",
                df_progress.to_csv(index=False).encode("utf-8-sig"),
                file_name="progress.csv",
                mime="text/csv"
            )
        if not df_scores.empty:
            st.download_button(
                "下载分数数据 CSV",
                df_scores.to_csv(index=False).encode("utf-8-sig"),
                file_name="scores.csv",
                mime="text/csv"
            )
        if not df_events.empty:
            st.download_button(
                "下载行为日志 CSV",
                df_events.to_csv(index=False).encode("utf-8-sig"),
                file_name="events.csv",
                mime="text/csv"
            )
        if not df_survey.empty:
            st.download_button(
                "下载问卷结果 CSV",
                df_survey.to_csv(index=False).encode("utf-8-sig"),
                file_name="survey.csv",
                mime="text/csv"
            )

    st.stop()

# =========================
# 学生端：输入编号
# =========================
if not pid:
    st.title("请输入被试编号")
    with st.form("pid_form"):
        input_pid = st.text_input("被试编号（请使用固定编号，便于中断后恢复进度）")
        submitted = st.form_submit_button("进入")
    if submitted and input_pid.strip():
        st.query_params["pid"] = input_pid.strip()
        st.query_params["mode"] = mode
        st.rerun()
    st.stop()

prog = load_progress(pid)
if not prog.get("mode"):
    prog["mode"] = mode
    save_progress(prog)

# 仅侧边式保留点击日志
if mode == "sidebar" and term and evt:
    log_event(pid, mode, prog["current_stage"], "gloss_click", item_id=term, value=term)

# =========================
# 页面样式
# =========================
st.markdown("""
<style>
.main-title {
    text-align:center;
    font-size: 2.2rem;
    font-weight: 700;
    color: #1f6fb2;
    margin-top: 0.3rem;
    margin-bottom: 1.2rem;
}
.reading-p {
    text-indent: 2em;
    line-height: 2.3;
    font-size: 24px;
    color: #222;
    margin-bottom: 0.9em;
}
.term-sidebar {
    background-color: #dff1ff;
    padding: 2px 5px;
    border-radius: 5px;
    text-decoration: none;
    color: #222;
    font-weight: 600;
}
.term-endnote {
    background-color: #f3e8ff;
    padding: 2px 5px;
    border-radius: 5px;
    color: #222;
    font-weight: 600;
}
.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin-top: 0.2rem;
    margin-bottom: 1rem;
    color: #1f6fb2;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 工具函数
# =========================
def get_stage_order():
    return [
        "pretest",
        "reading",
        "immediate_vocab",
        "reading_comp",
        "survey",
        "delayed_vocab",
        "finished"
    ]

def get_stage_label(stage):
    mapping = {
        "pretest": "前测",
        "reading": "阅读",
        "immediate_vocab": "即时词汇测试",
        "reading_comp": "阅读理解测试",
        "survey": "问卷",
        "delayed_vocab": "延后测",
        "finished": "已完成"
    }
    return mapping.get(stage, stage)

def render_progress_header(current_stage):
    order = get_stage_order()
    idx = order.index(current_stage) if current_stage in order else 0
    progress = idx / (len(order) - 1) if len(order) > 1 else 0
    st.markdown(f"### 当前阶段：{get_stage_label(current_stage)}")
    st.progress(progress)

def build_url(mode_value, pid_value, term_value=None):
    base = f"?mode={quote(mode_value)}&pid={quote(pid_value)}"
    if term_value:
        token = str(int(time.time() * 1000))
        base += f"&term={quote(term_value)}&evt={quote(token)}"
    return base

def score_mcq(questions, answers_dict):
    score = 0
    for q in questions:
        if answers_dict.get(q["id"]) == q["answer"]:
            score += 1
    return score

def format_target_in_stem(stem, target):
    safe_stem = html.escape(stem)
    safe_target = html.escape(target)
    return safe_stem.replace(safe_target, f"<u><b>{safe_target}</b></u>")

def render_mcq_question(q, saved_answers, answer_key_prefix, pid, mode, stage, prog):
    current = saved_answers.get(q["id"], "")
    options = list(q["options"].keys())
    labels = [f"{k}. {q['options'][k]}" for k in options]
    label_to_key = {f"{k}. {q['options'][k]}": k for k in options}

    if "target" in q:
        formatted_stem = format_target_in_stem(q["stem"], q["target"])
        st.markdown(formatted_stem, unsafe_allow_html=True)
        radio_label = "请选择答案："
    else:
        radio_label = q["stem"]

    default_index = None
    if current in q["options"]:
        current_label = f"{current}. {q['options'][current]}"
        if current_label in labels:
            default_index = labels.index(current_label)

    selected_label = st.radio(
        radio_label,
        labels,
        index=default_index,
        key=f"{answer_key_prefix}_{q['id']}"
    )

    if selected_label is not None:
        new_value = label_to_key[selected_label]
        if new_value != current:
            saved_answers[q["id"]] = new_value
            save_progress(prog)
            log_event(pid, mode, stage, "answer_change", item_id=q["id"], value=new_value)

def render_plain_text():
    paragraphs = TEXT.split("\n\n")
    for p in paragraphs:
        st.markdown(f"<div class='reading-p'>{html.escape(p)}</div>", unsafe_allow_html=True)

def split_text_for_popup(text):
    pattern = "(" + "|".join(map(re.escape, TERMS)) + ")"
    parts = re.split(pattern, text)
    result = []
    for part in parts:
        if not part:
            continue
        if part in TERMS:
            result.append(("term", part))
        else:
            result.append(("normal", part))
    return result

def render_popup_reading():
    paragraphs = TEXT.split("\n\n")
    html_blocks = []

    for p in paragraphs:
        parts = split_text_for_popup(p)
        segs = []
        for kind, val in parts:
            if kind == "normal":
                segs.append(html.escape(val))
            else:
                safe_term = html.escape(val)
                safe_gloss = html.escape(GLOSSES[val]).replace("'", "\\'")
                segs.append(
                    f"<span class='term-popup-inline' onclick=\"openGloss('{safe_term}', '{safe_gloss}')\">{safe_term}</span>"
                )
        html_blocks.append(f"<div class='reading-p'>{''.join(segs)}</div>")

    popup_html = f"""
    <html>
    <head>
    <style>
    body {{
        font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
        background: white;
        margin: 0;
        padding: 8px 10px 10px 10px;
    }}
    .reading-p {{
        text-indent: 2em;
        line-height: 2.3;
        font-size: 24px;
        color: #222;
        margin-bottom: 0.9em;
    }}
    .term-popup-inline {{
        background-color: #fff2b3;
        padding: 2px 5px;
        border-radius: 5px;
        cursor: pointer;
        font-weight: 600;
    }}
    .term-popup-inline:hover {{
        background-color: #ffe082;
    }}
    #gloss-overlay {{
        display: none;
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.18);
        z-index: 9998;
    }}
    #gloss-modal {{
        display: none;
        position: fixed;
        top: 22%;
        left: 50%;
        transform: translateX(-50%);
        width: min(520px, 80vw);
        background: white;
        border: 2px solid #1f6fb2;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        padding: 18px 20px;
        z-index: 9999;
    }}
    #gloss-modal-title {{
        font-size: 24px;
        font-weight: 700;
        color: #1f6fb2;
        margin-bottom: 10px;
    }}
    #gloss-modal-content {{
        font-size: 20px;
        line-height: 1.8;
        color: #333;
    }}
    .gloss-close-btn {{
        margin-top: 14px;
        padding: 8px 16px;
        border: none;
        border-radius: 8px;
        background: #1f6fb2;
        color: white;
        font-size: 16px;
        cursor: pointer;
    }}
    </style>
    </head>
    <body>
        {''.join(html_blocks)}

        <div id="gloss-overlay" onclick="closeGloss()"></div>
        <div id="gloss-modal">
            <div id="gloss-modal-title"></div>
            <div id="gloss-modal-content"></div>
            <button class="gloss-close-btn" onclick="closeGloss()">关闭</button>
        </div>

        <script>
        function openGloss(term, gloss) {{
            document.getElementById("gloss-modal-title").innerText = term;
            document.getElementById("gloss-modal-content").innerText = gloss;
            document.getElementById("gloss-overlay").style.display = "block";
            document.getElementById("gloss-modal").style.display = "block";
        }}
        function closeGloss() {{
            document.getElementById("gloss-overlay").style.display = "none";
            document.getElementById("gloss-modal").style.display = "none";
        }}
        </script>
    </body>
    </html>
    """
    components.html(popup_html, height=1450, scrolling=True)

def render_reading(mode_value, selected_term=""):
    st.markdown(f"<div class='main-title'>{TITLE}</div>", unsafe_allow_html=True)
    paragraphs = TEXT.split("\n\n")

    if mode_value == "popup":
        render_popup_reading()

    elif mode_value == "sidebar":
        col_main, col_side = st.columns([3, 1])

        with col_main:
            def repl(match):
                w = match.group(0)
                return f'<a class="term-sidebar" href="{build_url("sidebar", pid, w)}">{html.escape(w)}</a>'

            pattern = "(" + "|".join(map(re.escape, TERMS)) + ")"
            for p in paragraphs:
                rendered = re.sub(pattern, repl, html.escape(p))
                st.markdown(f"<div class='reading-p'>{rendered}</div>", unsafe_allow_html=True)

        with col_side:
            st.markdown("### 注释")
            if selected_term in GLOSSES:
                st.markdown(f"**{selected_term}**")
                st.write(GLOSSES[selected_term])
            else:
                st.info("点击正文中的目标词后，这里会显示对应释义。")

    else:
        term_to_num = {term: i + 1 for i, term in enumerate(TERMS)}

        def repl(match):
            w = match.group(0)
            num = term_to_num[w]
            return f'<span class="term-endnote">{html.escape(w)}<sup>{num}</sup></span>'

        pattern = "(" + "|".join(map(re.escape, TERMS)) + ")"
        for p in paragraphs:
            rendered = re.sub(pattern, repl, html.escape(p))
            st.markdown(f"<div class='reading-p'>{rendered}</div>", unsafe_allow_html=True)

        st.markdown("### 词语注释")
        for t in TERMS:
            st.write(f"{term_to_num[t]}. **{t}**：{GLOSSES[t]}")

# =========================
# 阶段渲染
# =========================
stage = prog["current_stage"]

st.caption(f"被试编号：{pid}｜当前模式：{mode}")
render_progress_header(stage)

# 前测
if stage == "pretest":
    st.markdown("<div class='section-title'>前测：词汇配对</div>", unsafe_allow_html=True)
    st.write("请将左侧词语与右侧英文释义进行配对。")
    st.write("例如：1 → C")

    st.markdown("#### 英文释义选项")
    for k, v in PRETEST_OPTIONS.items():
        st.write(f"{k}. {v}")

    for idx, word in enumerate(PRETEST_WORDS, start=1):
        key = f"pre_{word}"
        default = prog["pretest_answers"].get(word, "")
        options = [""] + list(PRETEST_OPTIONS.keys())
        current_index = options.index(default) if default in options else 0
        choice = st.selectbox(f"{idx}. {word}", options, index=current_index, key=key)
        if choice != default:
            prog["pretest_answers"][word] = choice
            save_progress(prog)
            log_event(pid, mode, stage, "answer_change", item_id=word, value=choice)

    if st.button("提交前测并进入阅读"):
        score = sum(1 for w in PRETEST_WORDS if prog["pretest_answers"].get(w) == PRETEST_ANSWERS[w])
        log_event(pid, mode, stage, "submit_pretest")
        log_score(pid, mode, stage, score, len(PRETEST_WORDS))
        prog["current_stage"] = "reading"
        save_progress(prog)
        st.rerun()

# 阅读
elif stage == "reading":
    st.markdown("<div class='section-title'>阅读</div>", unsafe_allow_html=True)
    render_reading(mode, term)

    if st.button("完成阅读，进入即时词汇测试"):
        log_event(pid, mode, stage, "finish_reading")
        prog["reading_done"] = True
        prog["current_stage"] = "immediate_vocab"
        save_progress(prog)
        st.rerun()

# 即时词汇测试
elif stage == "immediate_vocab":
    st.markdown("<div class='section-title'>即时词汇测试</div>", unsafe_allow_html=True)
    st.write("请根据句子语境，选择加粗并加下划线词语最合适的英文意思。")

    with st.expander("点击展开原文（做题时可随时回看）", expanded=False):
        render_plain_text()

    for q in VOCAB_QS:
        render_mcq_question(
            q=q,
            saved_answers=prog["immediate_vocab_answers"],
            answer_key_prefix="imm",
            pid=pid,
            mode=mode,
            stage=stage,
            prog=prog
        )

    if st.button("提交即时词汇测试并进入阅读理解测试"):
        vocab_score = score_mcq(VOCAB_QS, prog["immediate_vocab_answers"])
        log_score(pid, mode, "immediate_vocab", vocab_score, len(VOCAB_QS))
        log_event(pid, mode, stage, "submit_immediate_vocab")
        prog["current_stage"] = "reading_comp"
        save_progress(prog)
        st.rerun()

# 阅读理解测试
elif stage == "reading_comp":
    st.markdown("<div class='section-title'>阅读理解测试</div>", unsafe_allow_html=True)

    with st.expander("点击展开原文（做题时可随时回看）", expanded=False):
        render_plain_text()

    for q in READING_QS:
        render_mcq_question(
            q=q,
            saved_answers=prog["reading_answers"],
            answer_key_prefix="read",
            pid=pid,
            mode=mode,
            stage=stage,
            prog=prog
        )

    if st.button("提交阅读理解测试并进入问卷"):
        reading_score = score_mcq(READING_QS, prog["reading_answers"])
        log_score(pid, mode, "reading_comp", reading_score, len(READING_QS))
        log_event(pid, mode, stage, "submit_reading_comp")
        prog["current_stage"] = "survey"
        save_progress(prog)
        st.rerun()

# 问卷
elif stage == "survey":
    st.markdown("<div class='section-title'>阅读体验问卷</div>", unsafe_allow_html=True)
    st.caption("请根据你刚才的阅读体验作答：1=非常不同意，5=非常同意。")

    for qid, qtext in SURVEY_ITEMS:
        current = prog["survey_answers"].get(qid, 3)
        val = st.radio(
            qtext,
            [1, 2, 3, 4, 5],
            index=[1, 2, 3, 4, 5].index(current) if current in [1, 2, 3, 4, 5] else 2,
            horizontal=True,
            key=f"sv_{qid}"
        )
        if val != current:
            prog["survey_answers"][qid] = val
            save_progress(prog)
            log_event(pid, mode, stage, "answer_change", item_id=qid, value=str(val))

    comment = st.text_area("你对这种注释位置还有什么意见或建议？（可选）", value=prog.get("survey_comment", ""))
    if comment != prog.get("survey_comment", ""):
        prog["survey_comment"] = comment
        save_progress(prog)

    if st.button("提交问卷"):
        with open(SURVEY_FILE, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                now_str(), pid, mode,
                prog["survey_answers"].get("q1", ""),
                prog["survey_answers"].get("q2", ""),
                prog["survey_answers"].get("q3", ""),
                prog["survey_answers"].get("q4", ""),
                prog["survey_answers"].get("q5", ""),
                prog["survey_answers"].get("q6", ""),
                prog.get("survey_comment", "")
            ])
        log_event(pid, mode, stage, "submit_survey")
        prog["survey_done"] = True
        prog["current_stage"] = "delayed_vocab"
        save_progress(prog)
        st.success("问卷已提交。你现在可以关闭页面；七天后使用同一个编号再次进入，系统会直接进入延后测。")
        st.stop()

# 延后测
elif stage == "delayed_vocab":
    st.markdown("<div class='section-title'>延后测：词汇意义识别</div>", unsafe_allow_html=True)
    st.info("请根据句子语境，选择加粗并加下划线词语最合适的英文意思。")

    with st.expander("点击展开原文（做题时可随时回看）", expanded=False):
        render_plain_text()

    for q in VOCAB_QS:
        render_mcq_question(
            q=q,
            saved_answers=prog["delayed_vocab_answers"],
            answer_key_prefix="del",
            pid=pid,
            mode=mode,
            stage=stage,
            prog=prog
        )

    if st.button("提交延后测"):
        score = score_mcq(VOCAB_QS, prog["delayed_vocab_answers"])
        log_score(pid, mode, "delayed_vocab", score, len(VOCAB_QS))
        log_event(pid, mode, stage, "submit_delayed")
        prog["current_stage"] = "finished"
        save_progress(prog)
        st.success("延后测已提交，感谢你的参与。")
        st.stop()

# 完成
else:
    st.success("你已完成所有阶段。感谢参与。")
    
