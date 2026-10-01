"""Look and feel of the web app: fonts, brand, hero, tab styling, feature intros,
and the soccer loading animation. Pure HTML/CSS strings, no Streamlit calls."""

import base64
from functools import cache
from pathlib import Path

ASSETS_DIR = Path(__file__).parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "bionexus_logo.png"
COMPANY_NAME = "BioNexus"

# One accent colour per feature, used by the tab buttons and the intro cards.
TAB_COLORS = ["#2563eb", "#7c3aed", "#059669"]

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@600;700;800&family=Noto+Sans+KR:wght@400;500;700;800&display=swap');

/* ---------- brand (sidebar, top-left) ---------- */
.bi-brand { display: flex; align-items: center; gap: 12px; margin: -8px 0 18px; }
.bi-brand img { height: 52px; width: auto; }
.bi-brand span {
  font-family: 'Outfit', 'Noto Sans KR', sans-serif; font-weight: 700; font-size: 1.65rem;
  letter-spacing: .01em; color: #1f2d44;
}

/* ---------- hero title ---------- */
.bi-hero { margin: 0 0 10px; }
.bi-hero-title { display: flex; align-items: center; gap: 14px; }
.bi-hero-emoji { font-size: 2.6rem; line-height: 1; }
.bi-hero-text {
  font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 2.9rem; line-height: 1.1;
  letter-spacing: -.02em;
  background: linear-gradient(90deg, #1e3a8a 0%, #3b6fb6 55%, #0f9d9a 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.bi-hero-sub {
  font-family: 'Noto Sans KR', sans-serif; font-size: 1.05rem; color: #5b6475; margin-top: 8px;
}
.bi-hero-sub b { color: #1f2d44; font-weight: 700; }

/* ---------- tabs: three separate cards ---------- */
[data-testid="stTabs"] [role="tablist"] {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px;
  border-bottom: none; margin-bottom: 8px;
}
[data-testid="stTabs"] .react-aria-SelectionIndicator { display: none; }
[data-testid="stTab"] {
  --bi-accent: #2563eb;
  display: flex; flex-direction: column; align-items: flex-start; justify-content: center;
  height: auto; padding: 14px 18px; border-radius: 14px;
  border: 2px solid color-mix(in srgb, var(--bi-accent) 30%, transparent);
  background: color-mix(in srgb, var(--bi-accent) 6%, transparent);
  transition: background .15s, border-color .15s, transform .15s;
}
[data-testid="stTab"]:nth-child(2) { --bi-accent: #7c3aed; }
[data-testid="stTab"]:nth-child(3) { --bi-accent: #059669; }
[data-testid="stTab"]:hover { border-color: var(--bi-accent); transform: translateY(-1px); }
[data-testid="stTab"] p {
  font-family: 'Noto Sans KR', sans-serif; font-size: 1.25rem; font-weight: 700;
  color: var(--bi-accent);
}
[data-testid="stTab"]::after {
  font-family: 'Noto Sans KR', sans-serif; font-size: .85rem; font-weight: 400;
  color: #5b6475; margin-top: 4px;
}
[data-testid="stTab"]:nth-child(1)::after { content: "R 코드 ⇄ Python 코드 자동 변환"; }
[data-testid="stTab"]:nth-child(2)::after { content: "내 파이프라인 vs 참고 파이프라인"; }
[data-testid="stTab"]:nth-child(3)::after { content: "바꿔볼 parameter와 추천값 안내"; }
[data-testid="stTab"][aria-selected="true"] {
  background: var(--bi-accent); border-color: var(--bi-accent);
  box-shadow: 0 6px 16px color-mix(in srgb, var(--bi-accent) 30%, transparent);
}
[data-testid="stTab"][aria-selected="true"] p,
[data-testid="stTab"][aria-selected="true"]::after { color: #fff; }

/* ---------- feature intro card (top of each tab) ---------- */
.bi-intro {
  font-family: 'Noto Sans KR', sans-serif;
  border-left: 6px solid var(--bi-accent); border-radius: 12px; padding: 18px 22px; margin: 6px 0 18px;
  background: color-mix(in srgb, var(--bi-accent) 7%, transparent);
}
.bi-intro h3 { margin: 0 0 6px; padding: 0; font-size: 1.3rem; font-weight: 800; color: var(--bi-accent); }
.bi-intro .bi-lead { font-size: 1.02rem; margin: 0 0 14px; color: inherit; }
.bi-intro-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.bi-intro-grid > div {
  background: rgba(255, 255, 255, .65); border-radius: 10px; padding: 10px 14px;
  border: 1px solid color-mix(in srgb, var(--bi-accent) 18%, transparent);
}
.bi-intro-grid h4 { margin: 0 0 6px; padding: 0; font-size: .9rem; font-weight: 700; color: var(--bi-accent); }
.bi-intro-grid ul { margin: 0; padding-left: 1.1em; font-size: .9rem; line-height: 1.55; }
.bi-intro .bi-tip { margin: 12px 0 0; font-size: .88rem; color: #5b6475; }
@media (max-width: 900px) {
  [data-testid="stTabs"] [role="tablist"], .bi-intro-grid { grid-template-columns: 1fr; }
}
@media (prefers-color-scheme: dark) {
  .bi-brand span, .bi-hero-sub b { color: #e5e9f0; }
  .bi-intro-grid > div { background: rgba(0, 0, 0, .2); }
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
  <div class="bi-hero-title"><span class="bi-hero-emoji">🧬</span><span class="bi-hero-text">BI Pipeline Assistant</span></div>
  <div class="bi-hero-sub">Bioinformatics 파이프라인을 <b>변환</b>하고, <b>비교</b>하고, <b>쉽게 조정</b>하세요</div>
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
        "tip": "💡 '변환 후 실행해서 검증'을 켜면 변환된 코드를 직접 실행해 보고, 에러가 나면 최대 3번까지 스스로 고칩니다.",
    },
    {
        "title": "② 파이프라인 비교",
        "lead": "내 파이프라인과 참고 파이프라인을 단계별로 나란히 놓고, 빠진 단계와 다른 설정을 찾아 보완 코드를 제안합니다.",
        "input": ["A: 내가 만든 파이프라인", "B: 논문 · 튜토리얼 · 동료의 파이프라인", "A와 B의 언어가 달라도 됩니다"],
        "output": ["단계별 비교표 (✅ 동일 · ⚠️ 차이 · 🅰️ A에만 · 🅱️ B에만)", "빠진 단계를 채울 코드"],
        "when": ["놓친 QC · doublet 제거 단계가 없는지 점검할 때", "참고 파이프라인과 설정값이 왜 다른지 궁금할 때"],
        "tip": "💡 결과 품질에 영향이 큰 단계(QC, 정규화, batch 보정 등)부터 우선 제안합니다.",
    },
    {
        "title": "③ Parameter 가이드",
        "lead": "비전공자도 분석을 조정할 수 있도록, 바꿔볼 만한 parameter의 위치와 추천값을 쉬운 말로 알려줍니다.",
        "input": ["파이프라인 1개 (직접 만든 것 · 가져온 것 모두 가능)"],
        "output": ["코드에서 해당 줄 색 표시 (🔴 중요 · 🟠 보통 · 🔵 낮음)", "parameter별 쉬운 설명", "추천 후보값과 언제 쓰는지"],
        "when": ["클러스터가 너무 많거나 적게 나올 때", "QC 기준을 내 데이터에 맞게 바꾸고 싶을 때"],
        "tip": "💡 API 키가 없어도 기본 기능은 오프라인 모드로 무료 동작합니다.",
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

    return (
        f'<div class="bi-intro" style="--bi-accent:{TAB_COLORS[index]}">'
        f'<h3>{f["title"]}</h3><p class="bi-lead">{f["lead"]}</p>'
        '<div class="bi-intro-grid">'
        f'<div><h4>📥 넣는 것</h4><ul>{items(f["input"])}</ul></div>'
        f'<div><h4>📤 얻는 것</h4><ul>{items(f["output"])}</ul></div>'
        f'<div><h4>🙋 이럴 때 쓰세요</h4><ul>{items(f["when"])}</ul></div>'
        f'</div><p class="bi-tip">{f["tip"]}</p></div>'
    )
