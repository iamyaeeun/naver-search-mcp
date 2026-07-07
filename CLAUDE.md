# naver-api-hub-mcp

Naver Search Open API(뉴스/블로그/쇼핑)를 MCP 서버로 감싼 예제 겸, Claude Code
Skill을 활용한 가벼운 컨벤션 체크 + PR 초안 자동화 워크플로우 레포입니다.

## 구조

- `mcp_server/` — MCP 서버 본체
  - `naver_client.py`: Naver Search Open API 호출 (키가 없으면 mock 데이터 반환)
  - `server.py`: FastMCP로 `search_news` / `search_blog` / `search_img` / `search_webkr` 툴 노출
- `.claude/skills/naming-check/` — diff에 새로 추가된 함수/변수명만 검사하는 skill
- `.claude/skills/pr-draft/` — diff + naming-check 결과로 PR 본문 초안을 만드는 skill
- `tests/` — mock 모드 기준 동작 테스트

## 코드 컨벤션 (naming-check가 강제하는 범위)

- Python: 함수/변수명은 `snake_case`. 상수(ALL_CAPS)는 예외.
- JS/TS: 함수/변수명은 `camelCase`.
- 한글 등 비-ASCII 식별자 금지.
- 의미 없는 한 글자 이름 금지 (`i, j, k, x, y, n, _` 제외).

이 규칙은 **새로 추가된 줄에만** 적용됩니다. 기존 코드 전체를 검사하는 linter가
아닙니다 — 범위를 좁게 유지하는 것이 의도된 설계입니다.

## PR 워크플로우

1. 작업 완료 후 `pr-draft` skill로 PR 본문 초안 생성 (naming-check 리포트 포함).
2. 초안을 사용자에게 보여주고 확인받는다.
3. 확인 후에만 `gh pr create` 실행. **사용자 확인 없이 push/PR 생성 금지.**

## 환경 변수

`.env.example` 참고. `NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET`이 없으면
`naver_client.py`는 자동으로 mock 데이터를 반환합니다 (에러 아님).
