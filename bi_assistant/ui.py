"""Look and feel of the web app: fonts, brand, hero, tab styling, feature intros,
and the soccer loading animation. Pure HTML/CSS strings, no Streamlit calls."""

import base64
from functools import cache
from pathlib import Path

ASSETS_DIR = Path(__file__).parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "bionexus_logo.png"
COMPANY_NAME = "BioNexus"

# Soft pastel palette: light backgrounds with muted text of the same hue.
PASTEL = {
    "blue":   {"bg": "#eaf2fd", "border": "#cfe0f7", "text": "#2f5185"},
    "violet": {"bg": "#f1ecfb", "border": "#ddd2f3", "text": "#5a4690"},
    "mint":   {"bg": "#e7f6ee", "border": "#c9e8d7", "text": "#2f6b4f"},
    "rose":   {"bg": "#fdecec", "border": "#f5d0d0", "text": "#9a3f3f"},
    "amber":  {"bg": "#fdf4e2", "border": "#f2e0b8", "text": "#86621b"},
}

# Parameter importance: code-line highlight + Streamlit badge for labels.
IMPORTANCE = {
    "high":   {"bg": PASTEL["rose"]["bg"],  "badge": ":red-badge[중요도 높음]",   "label": "중요도 높음", "tone": "rose"},
    "medium": {"bg": PASTEL["amber"]["bg"], "badge": ":orange-badge[중요도 보통]", "label": "중요도 보통", "tone": "amber"},
    "low":    {"bg": PASTEL["blue"]["bg"],  "badge": ":blue-badge[중요도 낮음]",   "label": "중요도 낮음", "tone": "blue"},
}

# Pipeline comparison status.
STATUS = {
    "both_same":      {"label": "동일",   "tone": "mint"},
    "both_different": {"label": "차이",   "tone": "amber"},
    "only_a":         {"label": "A에만", "tone": "blue"},
    "only_b":         {"label": "B에만", "tone": "violet"},
}
_STATUS_BY_LABEL = {v["label"]: v["tone"] for v in STATUS.values()}

THEME_CSS = """
<style>
:root {
  --bi-text: #111827; --bi-muted: #6b7280; --bi-border: #e5e7eb; --bi-surface: #f9fafb;
  --bi-font: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', sans-serif;
}

/* ---------- brand (sidebar, top-left) ---------- */
.bi-brand { display: flex; align-items: center; gap: 10px; margin: -8px 0 20px; }
.bi-brand img { height: 44px; width: auto; }
.bi-brand span {
  font-family: var(--bi-font); font-weight: 700; font-size: 1.4rem;
  letter-spacing: -.01em; color: var(--bi-text);
}

/* ---------- hero title ---------- */
.bi-hero { margin: 0 0 14px; font-family: var(--bi-font); }
.bi-hero-title {
  font-weight: 800; font-size: 2.6rem; line-height: 1.15; letter-spacing: -.035em; color: var(--bi-text);
}
.bi-hero-sub { font-size: 1.05rem; color: var(--bi-muted); margin-top: 8px; letter-spacing: -.01em; }

/* ---------- tabs: three separate, neutral cards ---------- */
[data-testid="stTabs"] [role="tablist"] {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;
  border-bottom: none; margin-bottom: 6px;
}
[data-testid="stTabs"] .react-aria-SelectionIndicator,
[data-testid="stTabs"] [role="tablist"]::after { display: none; }
[data-testid="stTab"] {
  --bi-tab-bg: #eaf2fd; --bi-tab-border: #cfe0f7; --bi-tab-text: #2f5185;
  display: flex; flex-direction: column; align-items: flex-start; justify-content: center;
  height: auto; padding: 16px 20px; border-radius: 12px;
  border: 1px solid var(--bi-border); background: var(--bi-surface);
  transition: border-color .15s, background .15s, box-shadow .15s;
}
[data-testid="stTab"]:nth-child(2) { --bi-tab-bg: #f1ecfb; --bi-tab-border: #ddd2f3; --bi-tab-text: #5a4690; }
[data-testid="stTab"]:nth-child(3) { --bi-tab-bg: #e7f6ee; --bi-tab-border: #c9e8d7; --bi-tab-text: #2f6b4f; }
[data-testid="stTab"]:hover { border-color: var(--bi-tab-border); }
[data-testid="stTab"] p {
  font-family: var(--bi-font); font-size: 1.2rem; font-weight: 700; letter-spacing: -.02em;
  color: var(--bi-muted);
}
[data-testid="stTab"]::after {
  font-family: var(--bi-font); font-size: .85rem; font-weight: 400; color: #9ca3af; margin-top: 4px;
}
[data-testid="stTab"]:nth-child(1)::after { content: "R 코드 ⇄ Python 코드 자동 변환"; }
[data-testid="stTab"]:nth-child(2)::after { content: "내 파이프라인 vs 참고 파이프라인"; }
[data-testid="stTab"]:nth-child(3)::after { content: "바꿔볼 parameter와 추천값 안내"; }
[data-testid="stTab"][aria-selected="true"] {
  background: var(--bi-tab-bg); border: 1.5px solid var(--bi-tab-border);
  box-shadow: 0 4px 14px rgba(17, 24, 39, .05);
}
[data-testid="stTab"][aria-selected="true"] p { color: var(--bi-tab-text); }
[data-testid="stTab"][aria-selected="true"]::after { color: var(--bi-muted); }

/* ---------- feature intro card (top of each tab) ---------- */
.bi-intro {
  font-family: var(--bi-font); color: var(--bi-text);
  border: 1px solid var(--bi-intro-border); border-radius: 12px; padding: 20px 24px; margin: 8px 0 20px;
  background: linear-gradient(180deg, var(--bi-intro-bg) 0%, #fff 85%);
}
.bi-intro h3 {
  margin: 0 0 4px; padding: 0; font-size: 1.2rem; font-weight: 700; letter-spacing: -.02em;
  color: var(--bi-intro-text);
}
.bi-intro .bi-lead { font-size: 1rem; margin: 0 0 16px; color: var(--bi-muted); }
.bi-intro-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.bi-intro-grid h4 {
  margin: 0 0 6px; padding: 0; font-size: .8rem; font-weight: 600; color: var(--bi-muted);
  letter-spacing: .02em;
}
.bi-intro-grid ul { margin: 0; padding-left: 1.05em; font-size: .92rem; line-height: 1.6; }
.bi-intro .bi-tip {
  margin: 16px 0 0; padding-top: 12px; border-top: 1px solid var(--bi-intro-border);
  font-size: .88rem; color: var(--bi-muted);
}
.bi-intro .bi-tip b { color: var(--bi-text); font-weight: 600; }
/* inline code: neutral instead of Streamlit's green */
[data-testid="stMarkdownContainer"] code { color: var(--bi-text); background: #f3f4f6; }

/* ---------- status/info boxes: soft pastel (errors keep Streamlit's red) ---------- */
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) {
  background: #eaf2fd !important; border: 1px solid #cfe0f7;
}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) {
  background: #e7f6ee !important; border: 1px solid #c9e8d7;
}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) {
  background: #fdf4e2 !important; border: 1px solid #f2e0b8;
}
[data-testid="stAlertContentInfo"] { color: #2f5185 !important; }
[data-testid="stAlertContentSuccess"] { color: #2f6b4f !important; }
[data-testid="stAlertContentWarning"] { color: #86621b !important; }

/* ---------- result helpers ---------- */
.bi-chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 4px 0 10px; font-family: var(--bi-font); }
.bi-chip {
  display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 999px;
  font-size: .85rem; font-weight: 600; border: 1px solid;
}
.bi-chip b { font-weight: 800; }

@media (max-width: 900px) {
  [data-testid="stTabs"] [role="tablist"], .bi-intro-grid { grid-template-columns: 1fr; }
}
</style>
"""

# While the app is running, show a soccer field under the header: a player dribbles
# the ball from the left edge into the goal on the right, looping until the run ends.
# Every element is a pseudo-element of Streamlit's status widget, which only holds
# the running icon while a script is running, so the field disappears when work ends.
RUNNING_ICON_CSS = """
<style>
[data-testid="stStatusWidgetRunningIcon"] svg { display: none !important; }
[data-testid="stStatusWidgetRunningIcon"] { width: 0; }

/* the field (grass stripes + side lines) */
[data-testid="stStatusWidget"]:has([data-testid="stStatusWidgetRunningIcon"])::before {
  content: ""; position: fixed; left: 0; right: 0; top: 60px; height: 44px; z-index: 999991;
  background:
    linear-gradient(#fff, #fff) left 50% top 0 / 2px 100% no-repeat,
    repeating-linear-gradient(90deg, #3f9b3f 0 60px, #4caf50 60px 120px);
  border-top: 2px solid #fff; border-bottom: 2px solid #fff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, .15);
}
/* the goal on the right */
[data-testid="stStatusWidget"]:has([data-testid="stStatusWidgetRunningIcon"])::after {
  content: "🥅"; position: fixed; right: 10px; top: 64px; z-index: 999992;
  font-size: 32px; line-height: 1;
}
/* the player: the emoji faces left, so flip it to run right */
[data-testid="stStatusWidgetRunningIcon"]::before {
  content: "🏃"; position: fixed; top: 68px; z-index: 999993; font-size: 26px; line-height: 1;
  animation: bi-run-across 5s linear infinite, bi-run-bob .3s ease-in-out infinite alternate;
}
/* the ball: kicked ahead of the player, then shot into the goal */
[data-testid="stStatusWidgetRunningIcon"]::after {
  content: "⚽"; position: fixed; top: 82px; z-index: 999993; font-size: 14px; line-height: 1;
  animation: bi-ball-across 5s linear infinite, bi-dribble .6s ease-in-out infinite;
}
@keyframes bi-run-across {
  0%   { left: 8px; }
  80%  { left: calc(100vw - 150px); }
  100% { left: calc(100vw - 130px); }
}
@keyframes bi-run-bob {
  from { transform: scaleX(-1) translateY(0); }
  to   { transform: scaleX(-1) translateY(-4px); }
}
@keyframes bi-ball-across {
  0%   { left: 32px; }
  80%  { left: calc(100vw - 126px); }
  92%  { left: calc(100vw - 30px); }
  100% { left: calc(100vw - 30px); }
}
@keyframes bi-dribble {
  0%   { transform: translateX(0) rotate(0deg); }
  50%  { transform: translateX(14px) translateY(-3px) rotate(360deg); }
  100% { transform: translateX(0) rotate(720deg); }
}
@media (prefers-reduced-motion: reduce) {
  [data-testid="stStatusWidgetRunningIcon"]::before,
  [data-testid="stStatusWidgetRunningIcon"]::after { animation-duration: 0s; }
}
</style>
"""

HERO_HTML = """
<div class="bi-hero">
  <div class="bi-hero-title">BI Pipeline Assistant</div>
  <div class="bi-hero-sub">Bioinformatics 파이프라인을 변환하고, 비교하고, 쉽게 조정하세요.</div>
</div>
"""

# Detailed description shown at the top of each tab.
FEATURE_INTROS = [
    {
        "title": "① R ↔ Python 변환",
        "lead": "R로 만든 파이프라인은 Python으로, Python으로 만든 파이프라인은 R로 바꿔줍니다.",
        "input": ["R 또는 Python 파이프라인 1개", ".R · .Rmd · .py · .ipynb 지원"],
        "output": ["변환된 코드 (다운로드 가능)", "패키지 대응표 (예: Seurat → scanpy)", "결과가 달라질 수 있는 주의사항"],
        "when": ["논문 코드는 R인데 우리 팀은 Python을 쓸 때", "동료에게 다른 언어로 공유해야 할 때"],
        "tip": "'변환 후 실행해서 검증'을 켜면 변환된 코드를 직접 실행해 보고, 에러가 나면 최대 3번까지 스스로 고칩니다.",
    },
    {
        "title": "② 파이프라인 비교",
        "lead": "내 파이프라인과 참고 파이프라인을 단계별로 나란히 놓고, 빠진 단계와 다른 설정을 찾아 보완 코드를 제안합니다.",
        "input": ["A: 내가 만든 파이프라인", "B: 논문 · 튜토리얼 · 동료의 파이프라인", "A와 B의 언어가 달라도 됩니다"],
        "output": ["단계별 비교표 (동일 · 차이 · A에만 · B에만)", "빠진 단계를 채울 코드"],
        "when": ["놓친 QC · doublet 제거 단계가 없는지 점검할 때", "참고 파이프라인과 설정값이 왜 다른지 궁금할 때"],
        "tip": "결과 품질에 영향이 큰 단계(QC, 정규화, batch 보정 등)부터 우선 제안합니다.",
    },
    {
        "title": "③ Parameter 가이드",
        "lead": "비전공자도 분석을 조정할 수 있도록, 바꿔볼 만한 parameter의 위치와 추천값을 쉬운 말로 알려줍니다.",
        "input": ["파이프라인 1개 (직접 만든 것 · 가져온 것 모두 가능)"],
        "output": ["코드에서 해당 줄 표시 (중요도 높음 · 보통 · 낮음)", "parameter별 쉬운 설명", "추천 후보값과 언제 쓰는지"],
        "when": ["클러스터가 너무 많거나 적게 나올 때", "QC 기준을 내 데이터에 맞게 바꾸고 싶을 때"],
        "tip": "API 키가 없어도 기본 기능은 오프라인 모드로 무료 동작합니다.",
    },
]


@cache
def brand_html() -> str:
    """Company logo + name for the top-left of the sidebar."""
    logo = base64.b64encode(LOGO_PATH.read_bytes()).decode() if LOGO_PATH.exists() else ""
    img = f'<img src="data:image/png;base64,{logo}" alt="{COMPANY_NAME} logo">' if logo else ""
    return f'<div class="bi-brand">{img}<span>{COMPANY_NAME}</span></div>'


def feature_intro_html(index: int) -> str:
    f = FEATURE_INTROS[index]

    def items(xs):
        return "".join(f"<li>{x}</li>" for x in xs)

    tone = PASTEL[["blue", "violet", "mint"][index]]
    return (
        f'<div class="bi-intro" style="--bi-intro-bg:{tone["bg"]};--bi-intro-border:{tone["border"]};'
        f'--bi-intro-text:{tone["text"]}">'
        f'<h3>{f["title"]}</h3><p class="bi-lead">{f["lead"]}</p>'
        '<div class="bi-intro-grid">'
        f'<div><h4>넣는 것</h4><ul>{items(f["input"])}</ul></div>'
        f'<div><h4>얻는 것</h4><ul>{items(f["output"])}</ul></div>'
        f'<div><h4>이럴 때 쓰세요</h4><ul>{items(f["when"])}</ul></div>'
        f'</div><p class="bi-tip"><b>Tip</b>&nbsp;&nbsp;{f["tip"]}</p></div>'
    )


def _chip(tone: str, text: str) -> str:
    t = PASTEL[tone]
    return f'<span class="bi-chip" style="background:{t["bg"]};border-color:{t["border"]};color:{t["text"]}">{text}</span>'


def importance_legend_html() -> str:
    return '<div class="bi-chips">' + "".join(_chip(v["tone"], v["label"]) for v in IMPORTANCE.values()) + "</div>"


def status_summary_html(statuses: list[str]) -> str:
    """Count chips above the comparison table, e.g. '차이 3'."""
    chips = [
        _chip(v["tone"], f'{v["label"]} <b>{statuses.count(key)}</b>')
        for key, v in STATUS.items()
    ]
    return '<div class="bi-chips">' + "".join(chips) + "</div>"


def status_cell_style(label: str) -> str:
    """pandas Styler cell style for the comparison table's status column."""
    tone = _STATUS_BY_LABEL.get(label)
    if tone is None:
        return ""
    t = PASTEL[tone]
    return f"background-color: {t['bg']}; color: {t['text']}; font-weight: 600"
