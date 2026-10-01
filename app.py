"""Streamlit web UI: one app, three tabs sharing the same pipeline parser.

Run with:  streamlit run app.py
"""

import hashlib
import html
from pathlib import Path

import streamlit as st

from bi_assistant import config
from bi_assistant.features import comparator, converter, param_advisor
from bi_assistant.llm import LLMError
from bi_assistant.loader import PipelineSource, load_file, load_text
from bi_assistant.parser import parse_pipeline

EXAMPLES_DIR = Path(__file__).parent / "examples"
EXAMPLES = sorted(p.name for p in EXAMPLES_DIR.iterdir() if p.suffix in (".R", ".py"))
UPLOAD_TYPES = ["py", "R", "r", "Rmd", "qmd", "ipynb", "smk", "nf", "sh", "txt"]

st.set_page_config(page_title="BI Pipeline Assistant", page_icon="🧬", layout="wide")

# Replace Streamlit's top-right "running" icon with a player dribbling a ball.
RUNNING_ICON_CSS = """
<style>
[data-testid="stStatusWidgetRunningIcon"] svg { display: none !important; }
[data-testid="stStatusWidgetRunningIcon"] {
  position: relative; width: 4.2rem; height: 1.8rem; overflow: visible;
}
[data-testid="stStatusWidgetRunningIcon"]::before,
[data-testid="stStatusWidgetRunningIcon"]::after {
  position: absolute; bottom: 0.1rem; line-height: 1;
}
/* runner: the emoji faces left, so flip it to run toward the ball */
[data-testid="stStatusWidgetRunningIcon"]::before {
  content: "🏃"; left: 0; font-size: 1.4rem;
  animation: bi-run 0.35s ease-in-out infinite alternate;
}
/* ball: kicked forward, rolls back to the runner's foot */
[data-testid="stStatusWidgetRunningIcon"]::after {
  content: "⚽"; left: 1.45rem; font-size: 0.8rem;
  animation: bi-dribble 0.7s ease-in-out infinite;
}
@keyframes bi-run {
  from { transform: scaleX(-1) translateY(0); }
  to   { transform: scaleX(-1) translateY(-3px); }
}
@keyframes bi-dribble {
  0%   { transform: translateX(0) rotate(0deg); }
  50%  { transform: translateX(1.4rem) translateY(-2px) rotate(360deg); }
  100% { transform: translateX(0) rotate(720deg); }
}
@media (prefers-reduced-motion: reduce) {
  [data-testid="stStatusWidgetRunningIcon"]::before,
  [data-testid="stStatusWidgetRunningIcon"]::after { animation: none; }
}
</style>
"""
st.markdown(RUNNING_ICON_CSS, unsafe_allow_html=True)


# ---------- helpers ----------

def pipeline_input(key: str, label: str, default_example: str | None = None) -> PipelineSource | None:
    """Example picker / file upload / paste box. Returns the chosen pipeline."""
    st.markdown(f"**{label}**")
    mode = st.radio("입력 방식", ["예제", "파일 업로드", "직접 붙여넣기"], key=f"{key}_mode", horizontal=True)
    if mode == "예제":
        index = EXAMPLES.index(default_example) if default_example in EXAMPLES else 0
        name = st.selectbox("예제 선택", EXAMPLES, index=index, key=f"{key}_example")
        source = load_file(EXAMPLES_DIR / name)
    elif mode == "파일 업로드":
        uploaded = st.file_uploader("파이프라인 파일", type=UPLOAD_TYPES, key=f"{key}_upload")
        if uploaded is None:
            return None
        source = load_text(uploaded.name, uploaded.getvalue().decode("utf-8"))
    else:
        lang = st.selectbox("언어", ["R", "Python"], key=f"{key}_lang")
        text = st.text_area("코드", height=250, key=f"{key}_text")
        if not text.strip():
            return None
        source = load_text("pasted.R" if lang == "R" else "pasted.py", text)
    with st.expander(f"코드 보기 · {source.name} ({source.language})"):
        st.code(source.code, language="r" if source.language == "R" else "python", line_numbers=True)
    return source


def get_ir(source: PipelineSource):
    """Parse once per unique source; results are reused across tabs."""
    key = "ir_" + hashlib.sha256(source.code.encode()).hexdigest()
    if key not in st.session_state:
        with st.spinner(f"{source.name} 구조 분석 중..."):
            st.session_state[key] = parse_pipeline(source)
    return st.session_state[key]


def show_ir(ir) -> None:
    with st.expander(f"파이프라인 구조 ({ir.analysis_type}, {len(ir.steps)}단계)"):
        st.write(ir.summary)
        st.dataframe(
            [
                {"단계": s.name, "카테고리": s.category, "줄": f"{s.start_line}-{s.end_line}",
                 "도구": ", ".join(s.tools), "parameter 수": len(s.parameters)}
                for s in ir.steps
            ],
            use_container_width=True,
            hide_index=True,
        )


def highlighted_code(code: str, lines: dict[int, str]) -> str:
    """HTML <pre> with given line numbers highlighted by importance colour."""
    colours = {"high": "rgba(239,68,68,.25)", "medium": "rgba(245,158,11,.25)", "low": "rgba(59,130,246,.18)"}
    rows = []
    for i, line in enumerate(code.splitlines(), 1):
        bg = colours.get(lines.get(i, ""), "transparent")
        rows.append(
            f'<div style="background:{bg};white-space:pre"><span style="opacity:.45;display:inline-block;'
            f'width:3em">{i}</span>{html.escape(line) or "&nbsp;"}</div>'
        )
    return (
        '<pre style="font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;line-height:1.45;padding:12px;border-radius:8px;'
        'overflow-x:auto;background:rgba(127,127,127,.08)">' + "".join(rows) + "</pre>"
    )


def run_safely(fn):
    try:
        return fn()
    except LLMError as e:
        st.error(str(e))
        return None


# ---------- layout ----------

st.title("🧬 BI Pipeline Assistant")
st.caption("R ↔ Python 변환 · 파이프라인 비교/보완 · Parameter 가이드")

with st.sidebar:
    st.subheader("설정")
    providers = config.available_providers()
    if len(providers) > 1:
        config.PROVIDER = st.radio(
            "AI 모델",
            providers,
            index=providers.index(config.PROVIDER),
            format_func=lambda p: config.PROVIDERS[p]["label"],
            horizontal=True,
        )
    online = config.has_api_key()
    if online:
        label = config.PROVIDERS[config.PROVIDER]["label"]
        st.success(f"{label} API 연결됨\n\n모델: `{config.model_for(config.PROVIDER)}`")
    else:
        st.warning(
            "API 키 없음 → 오프라인 모드\n\n"
            "`.env`에 `ANTHROPIC_API_KEY` 또는 `OPENAI_API_KEY`를 넣으면 모든 기능이 켜집니다."
        )
    st.caption("⚠️ 회사 코드/데이터를 외부 API로 보내도 되는지 사내 정책을 확인하세요.")

tab_convert, tab_compare, tab_params = st.tabs(["① R ↔ Python 변환", "② 파이프라인 비교", "③ Parameter 가이드"])

# ① Conversion
with tab_convert:
    source = pipeline_input("conv", "변환할 파이프라인", "scrna_seurat.R")
    if source:
        target = converter.target_for(source.language)
        verify = st.checkbox(
            f"변환 후 실행해서 검증 ({target} 인터프리터와 데이터 필요, 최대 3회 자동 수정)",
            key="conv_verify",
        )
        if st.button(f"{source.language} → {target} 변환", type="primary", disabled=not online):
            def _convert():
                ir = get_ir(source)
                show_ir(ir)
                with st.spinner("변환 중..."):
                    result = converter.convert(source, ir, target)
                if verify:
                    with st.spinner("실행 검증 중..."):
                        log = converter.verify_and_fix(source, result)
                    for i, run in enumerate(log.rounds, 1):
                        icon = "✅" if run.ok else "❌"
                        with st.expander(f"{icon} 실행 {i}회차"):
                            st.code(run.stderr or run.stdout or "(출력 없음)")
                    result = log.final
                return result

            result = run_safely(_convert)
            if result:
                lang = "r" if result.target_language == "R" else "python"
                st.subheader("변환 결과")
                st.code(result.code, language=lang, line_numbers=True)
                ext = ".R" if lang == "r" else ".py"
                st.download_button("다운로드", result.code, file_name=Path(source.name).stem + "_converted" + ext)
                st.caption(f"설치: `{result.install_hint}`")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**패키지 매핑**")
                    st.dataframe([m.model_dump() for m in result.package_mapping], hide_index=True)
                with c2:
                    st.markdown("**주의사항**")
                    for c in result.caveats:
                        st.markdown(f"- {c}")

# ② Comparison
with tab_compare:
    col_a, col_b = st.columns(2)
    with col_a:
        src_a = pipeline_input("cmp_a", "A: 내 파이프라인", "scrna_seurat.R")
    with col_b:
        src_b = pipeline_input("cmp_b", "B: 참고 파이프라인", "scrna_scanpy.py")
    if src_a and src_b and st.button("비교하기", type="primary", disabled=not online):
        def _compare():
            ir_a, ir_b = get_ir(src_a), get_ir(src_b)
            with st.spinner("단계별 비교 중..."):
                return comparator.compare(src_a, ir_a, src_b, ir_b)

        result = run_safely(_compare)
        if result:
            st.info(result.summary)
            badge = {"both_same": "✅ 동일", "both_different": "⚠️ 차이", "only_a": "🅰️ A에만", "only_b": "🅱️ B에만"}
            st.dataframe(
                [
                    {"카테고리": m.category, "상태": badge[m.status], "A": m.a_step or "—",
                     "B": m.b_step or "—", "차이점": " / ".join(m.differences)}
                    for m in result.matches
                ],
                use_container_width=True,
                hide_index=True,
            )
            st.subheader("보완 제안")
            for target in ("A", "B"):
                items = [s for s in result.suggestions if s.target == target]
                if not items:
                    continue
                st.markdown(f"#### {target}에 추가하면 좋은 것")
                src = src_a if target == "A" else src_b
                for s in items:
                    where = f" · `{s.insert_after_step}` 다음" if s.insert_after_step else ""
                    with st.expander(f"{s.title}{where}"):
                        st.write(s.rationale)
                        st.code(s.code_snippet, language="r" if src.language == "R" else "python")

# ③ Parameter guide
with tab_params:
    source = pipeline_input("par", "분석할 파이프라인", "scrna_seurat.R")
    if source and st.button("수정 가능한 parameter 찾기", type="primary"):
        if online:
            guide = run_safely(lambda: param_advisor.advise(source, get_ir(source)))
        else:
            guide = param_advisor.offline_guide(source)
        if guide:
            st.info(guide.summary)
            levels = {"high": "🔴 높음", "medium": "🟠 중간", "low": "🔵 낮음"}
            code_col, list_col = st.columns([3, 2])
            with code_col:
                marks = {}
                for p in guide.params:
                    # keep the most important mark per line
                    if p.line not in marks or list(levels).index(p.importance) < list(levels).index(marks[p.line]):
                        marks[p.line] = p.importance
                st.html(highlighted_code(source.code, marks))
            with list_col:
                for p in guide.params:
                    with st.expander(f"{levels[p.importance]} · `{p.name}` = `{p.current_value}` (줄 {p.line})"):
                        st.markdown(f"**함수**: `{p.function}`" + (f" · **단계**: {p.step}" if p.step else ""))
                        st.write(p.what_it_does)
                        if p.effect_of_increase:
                            st.markdown(f"⬆️ 올리면: {p.effect_of_increase}")
                        if p.effect_of_decrease:
                            st.markdown(f"⬇️ 내리면: {p.effect_of_decrease}")
                        st.markdown("**추천 후보**")
                        for c in p.candidates:
                            st.markdown(f"- `{c.value}`" + (f" — {c.when_to_use}" if c.when_to_use else ""))
