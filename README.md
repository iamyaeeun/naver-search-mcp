# naver-api-hub-mcp

Naver Search Open API를 MCP 서버로 구현한 예제 + Claude Code Skill 기반의
가벼운 코드 컨벤션 체크 / PR 초안 자동화 워크플로우.

## 왜 만들었나

- 신규 API를 MCP로 감싸는 연습.
- Claude Code의 Skill을 활용해 "diff 안의 변경분만" 대상으로 하는 가벼운
  자동화(네이밍 컨벤션 체크, PR 초안 작성)를 레포에 녹여보는 것.

## 구성

```
mcp_server/          # MCP 서버 (search_news / search_blog / search_shop)
.claude/skills/
  naming-check/       # diff에 추가된 함수/변수명 네이밍 검사
  pr-draft/           # diff + naming-check 결과로 PR 본문 초안 작성
tests/
CLAUDE.md             # 컨벤션 및 워크플로우 규칙
```

## 실행

```bash
pip install -r requirements.txt
cp .env.example .env   # NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 채우기 (없어도 mock으로 동작)
python3 -m mcp_server.server
```

Claude Code에서 MCP 서버로 등록하려면 `claude mcp add` 또는 프로젝트
`.mcp.json`에 다음과 같이 추가하세요:

```json
{
  "mcpServers": {
    "naver-search": {
      "command": "python3",
      "args": ["-m", "mcp_server.server"],
      "cwd": "."
    }
  }
}
```

## 네이밍 컨벤션 체크

```bash
python3 .claude/skills/naming-check/scripts/check_naming.py
```

## 테스트

```bash
python3 -m pytest tests/
```
