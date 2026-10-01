# 🧬 BI Pipeline Assistant

bioinformatics 분석 파이프라인(R / Python)을 위한 웹 도우미입니다. 한 화면에 세 가지 기능이 있습니다.

| 탭 | 기능 | 방식 |
|---|---|---|
| ① R ↔ Python 변환 | R 파이프라인은 Python으로, Python 파이프라인은 R로 변환 | 에이전트: 변환 → 실행 → 에러를 다시 보내 수정 (최대 3회) |
| ② 파이프라인 비교 | 내 파이프라인(A)과 참고 파이프라인(B)을 단계별로 맞춰 비교하고, 서로 빠진 부분을 코드로 제안 | 워크플로 |
| ③ Parameter 가이드 | 비전공자도 바꿔볼 수 있도록 수정할 parameter의 위치(줄 번호), 중요도, 추천 후보값을 안내 | 워크플로 (API 키 없이도 오프라인 모드로 동작) |

## 구조

세 기능 모두 **공통 파서**가 만든 같은 중간 표현(`PipelineIR`: 단계, 도구, 입출력, parameter)을 사용합니다.

```
입력 (.R .Rmd .qmd .py .ipynb .smk .nf)
   │  loader.py      파일 형식별로 코드만 추출
   │  static_scan.py LLM 없이 keyword argument 위치를 찾음
   ▼
 parser.py ──► PipelineIR (schemas.py)
   │
   ├─► features/converter.py      ① 변환 + 실행 검증 루프
   ├─► features/comparator.py     ② 단계 정렬, 차이점, 보완 코드
   └─► features/param_advisor.py  ③ parameter 위치, 후보값, 설명
```

```
bi-pipeline-assistant/
├── app.py                      # Streamlit 웹 UI (탭 3개)
├── bi_assistant/
│   ├── config.py               # 환경 변수 설정
│   ├── llm.py                  # Claude API 호출부 (모델 교체 시 이 파일만 수정)
│   ├── schemas.py              # Pydantic 모델 (구조화된 출력)
│   ├── loader.py               # .ipynb / .Rmd 등에서 코드 추출
│   ├── static_scan.py          # 오프라인 parameter 스캐너
│   ├── parser.py               # 공통 코어: 코드 → PipelineIR
│   ├── features/               # ① ② ③
│   └── knowledge/              # 도메인 지식 (여기를 채울수록 품질이 좋아짐)
│       ├── package_map.yaml    #   R ↔ Python 패키지/함수 대응표
│       ├── canonical_steps.yaml#   비교 기준이 되는 표준 분석 단계
│       └── param_hints.yaml    #   parameter별 설명과 추천값
├── examples/                   # Seurat(R) / scanpy(Python) 예제 파이프라인
└── tests/
```

## 실행

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env           # ANTHROPIC_API_KEY 입력
streamlit run app.py           # http://localhost:8501
```

API 키가 없으면 ③ Parameter 가이드만 오프라인 모드(정적 분석 + `param_hints.yaml`)로 동작합니다.

### 설정 (`.env`)

| 변수 | 기본값 | 설명 |
|---|---|---|
| `ANTHROPIC_API_KEY` | - | Claude API 키 |
| `BI_ASSISTANT_MODEL` | `claude-opus-5-5` | 사용할 모델 |
| `BI_ASSISTANT_EFFORT` | `high` | `low` / `medium` / `high` / `xhigh` / `max` (낮을수록 빠르고 저렴함) |
| `BI_ASSISTANT_MAX_TOKENS` | `16000` | 응답 최대 길이 (긴 파이프라인을 변환할 때 늘리기) |
| `BI_ASSISTANT_OUTPUT_LANGUAGE` | `Korean` | 설명 언어 |

## 테스트

```bash
pytest -q
```

LLM 호출은 mock 처리되어 있어서 API 키 없이 돌아갑니다. GitHub Actions(`.github/workflows/ci.yml`)와 GitLab CI(`.gitlab-ci.yml`)에서 같은 테스트를 실행합니다.

## GitHub와 회사 GitLab에 함께 올리기

```bash
git remote add gitlab https://<회사-gitlab>/<group>/bi-pipeline-assistant.git
git push origin main && git push gitlab main
```

또는 GitLab 프로젝트 설정의 **Repository → Mirroring repositories**에서 GitHub 저장소를 pull mirror로 등록하면 자동으로 동기화됩니다.

## 주의사항

- **보안**: 코드가 Claude API(외부)로 전송됩니다. 회사 파이프라인이나 데이터 경로를 보내도 되는지 사내 정책을 먼저 확인하세요. 사내 모델로 바꾸려면 `bi_assistant/llm.py`의 `structured_call`만 교체하면 됩니다.
- **실행 검증**(① 탭 체크박스)은 생성된 코드를 이 컴퓨터에서 그대로 실행합니다. 대상 언어의 인터프리터(`python3` / `Rscript`), 패키지, 입력 데이터가 있어야 하며, 신뢰할 수 있는 환경에서만 사용하세요.
- 변환 결과는 패키지 간 기본값과 알고리즘 차이(예: Louvain vs Leiden) 때문에 숫자가 완전히 같지 않을 수 있습니다. ①의 "주의사항"을 꼭 확인하세요.

## 로드맵

- [ ] 변환 검증: 원본과 변환본의 실행 결과(클러스터 수, DE 유전자 목록 등) 자동 비교
- [ ] ③ 결과에서 후보값을 고르면 수정된 코드를 바로 다운로드
- [ ] bulk RNA-seq (DESeq2 ↔ PyDESeq2) 예제 추가
- [ ] Snakemake / Nextflow 파이프라인 지원 강화
- [ ] 사내 배포 (Docker + 사내 LLM 옵션)
