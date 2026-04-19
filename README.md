# SignalHub

AI / Agents 분야의 기술 동향을 자동 수집·요약하고 팀에 공유하는 Intelligence Hub.

- **수집**: arXiv 논문 + GeekNews RSS
- **분석**: 로컬 LLM (vLLM / Ollama 호환, 기본 `gemma4:e2b`)
- **저장**: SQLite
- **스케줄**: 매일 09:00 (Asia/Seoul) 자동 실행
- **알림**: 완료 시 SMTP 메일 발송 (보안 없이 발송 가능, no-auth 지원)
- **대시보드**: 타임라인 / 워드클라우드 / 토픽 온톨로지 네트워크 / 인피니티 스크롤 결과 뷰
- **오프라인 실행**: 모든 프론트 라이브러리 `app/static/vendor/`에 포함, Docker 이미지 단일 파일 배포

## 로컬 실행

```bash
python -m venv .venv
source .venv/Scripts/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8765
```

브라우저: http://localhost:8765

## 설정

기본값은 `app/config.py` 에 있고, 모든 항목은 **설정 탭에서 편집 가능**합니다 (DB에 override 저장).

주요 항목:

| 키 | 기본값 | 설명 |
| -- | ------ | ---- |
| `vllm_base_url` | `http://localhost:11434/v1` | LLM 엔드포인트 |
| `vllm_model`    | `gemma4:e2b`                | 모델명 |
| `auto_run_hour` / `auto_run_minute` | 9 / 0 | 자동 실행 시각 |
| `smtp_host` / `smtp_port` / `smtp_sender` | `""` / 25 / `signalhub@localhost` | 메일 발송 기본 |
| `smtp_use_tls` | `false` | STARTTLS 여부 (no-auth plain SMTP 기본) |
| `retention_days` | `0` | 0 = 무제한, N = N일 이전 분석 삭제 (매일 03:30) |

## Docker 실행 (오프라인망 포함)

### 빌드 & 압축 릴리즈

```bash
bash scripts/build_release.sh            # dist/signalhub-latest-YYYYMMDD.tar.gz 생성
```

### 오프라인 호스트로 이관

```bash
# 이관
scp dist/signalhub-*.tar.gz user@offline-host:/tmp/

# 오프라인 호스트에서
docker load < /tmp/signalhub-latest-YYYYMMDD.tar.gz

# 실행 (compose)
docker compose up -d
```

호스트에서 Ollama/vLLM이 돌고 있다면 설정 탭에서 `vllm_base_url`을
`http://host.docker.internal:11434/v1` 로 변경하세요. `docker-compose.yml` 에
`host.docker.internal:host-gateway` 가 이미 매핑되어 있습니다.

### 데이터

SQLite DB는 `./data/analysis.db` — compose 볼륨으로 호스트에 마운트됩니다.

## API 개요

| Method | Path | 설명 |
| ------ | ---- | ---- |
| GET  | `/stats` | 대시보드 통계 |
| GET  | `/keywords` | 키워드 목록 |
| POST | `/keywords` | 키워드 추가 |
| PATCH | `/keywords/{id}` | enabled 토글 |
| DELETE | `/keywords/{id}` | 삭제 |
| POST | `/run` | 특정 키워드 수동 실행 |
| POST | `/run-all` | 활성 키워드 전체 실행 |
| GET  | `/results?limit=&before_id=&keyword=&run_type=` | 커서 기반 페이지 (인피니티 스크롤) |
| GET  | `/results/{id}` | 상세 |
| GET  | `/insights` | 타임라인/태그/네트워크 집계 |
| GET  | `/settings` | 현재 설정 (시크릿 마스킹) |
| PUT  | `/settings` | 설정 변경 |
| POST | `/settings/reset` | 전체 초기화 |
| GET/POST/PATCH/DELETE | `/recipients[/{id}]` | 수신자 CRUD |
| POST | `/recipients/test` | SMTP 테스트 발송 |
