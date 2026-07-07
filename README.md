# naver-api-hub-mcp

Naver Search Open API를 MCP 서버로 구현한 예제 + Claude Code Skill 기반의
가벼운 코드 컨벤션 체크 / PR 초안 자동화 워크플로우.

## 왜 만들었나

- 신규 API를 MCP로 감싸는 연습.
- Claude Code의 Skill을 활용해 "diff 안의 변경분만" 대상으로 하는 가벼운
  자동화(네이밍 컨벤션 체크, PR 초안 작성)를 레포에 녹여보는 것.

## 구성

```
mcp_server/          # MCP 서버 (search_news / search_blog / search_img / search_webkr)
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

## Claude Code Skills

`.claude/skills/`에 있는 두 skill을 소개합니다.

### naming-check

> description: 현재 Git diff에서 새로 추가된 함수/변수 이름이 저장소
> 네이밍 규칙(Python은 snake_case, JS/TS는 camelCase, 의미 없는 한 글자
> 이름과 비-ASCII 식별자 금지)을 지키는지 검사합니다. PR을 만들기 전이나,
> 네이밍·코드 컨벤션·변수명 검사를 요청받았을 때 사용합니다.

#### 네이밍 규칙 검사

검사 범위는 일부러 좁게 잡았습니다. Git diff에서 **새로 추가된 줄**만,
그중에서도 **함수·변수 선언**만 봅니다. 전체 코드에 린터를 돌리는 게
아니라, 기존 코드는 건드리지 않고 이번에 바뀐 부분만 확인하는 용도입니다.

**언제 쓰나**

- PR 초안을 쓰거나 PR을 만들기 직전
- 네이밍 규칙·변수명·코드 컨벤션 검사를 요청받았을 때

**실행 방법**

```bash
python3 .claude/skills/naming-check/scripts/check_naming.py [git-diff-args]
```

- 인자 없이 실행하면 unstaged 변경 사항을 diff합니다.
- `--cached`를 주면 staged된 변경 사항을 diff합니다.
- `<base>...HEAD`처럼 기준 브랜치를 지정하면 그 브랜치와 비교합니다.
  (PR을 만들기 전에는 이 방식을 쓰세요.)

위반 사항이 있으면 0이 아닌 종료 코드와 함께 `file:line — issue` 형식의
목록을 출력하고, 문제가 없으면 ✅ 한 줄만 출력합니다.

**규칙**

1. Python 함수/변수명은 `snake_case`. (ALL_CAPS 상수는 예외.)
2. JS/TS 함수/변수명은 `camelCase`.
3. 한글 등 비-ASCII 식별자는 금지.
4. 의미 없는 한 글자 이름은 금지. (단, `i, j, k, x, y, n, _`처럼
   흔히 쓰이는 루프/인덱스 표기는 예외.)

**결과 보고**

PR 워크플로우 안에서 실행했다면, 출력을 요약하거나 풀어 쓰지 말고
PR 설명의 "Naming check" 섹션에 그대로 붙여넣어야 합니다.

### pr-draft

> description: 현재 브랜치와 기준 브랜치의 diff로 PR 설명을 작성하고
> 네이밍 규칙 검사 결과를 포함시킨 뒤, 사용자가 확인한 경우에만
> `gh pr create`로 PR을 생성합니다. PR 생성, PR 초안 작성, "PR
> 만들어줘" 같은 요청에 사용합니다.

#### PR 초안 작성

현재 브랜치의 diff를 바탕으로 PR 설명을 작성하고, 사용자 확인을 받은
후에만 PR을 생성합니다. 사용자 동의 없이 push하거나 PR을 만들지
않습니다.

**절차**

1. 기준 브랜치를 확인합니다(기본값 `main`). 또한 `git status`로 작업
   트리에 커밋되지 않은 변경 사항이 있는지 확인해, 의도치 않게 변경
   사항을 잃는 일이 없도록 합니다.
2. PR 컨텍스트 수집 스크립트를 실행합니다.
   ```bash
   python3 .claude/skills/pr-draft/scripts/gather_pr_context.py <base_ref>
   ```
   커밋 목록, 변경된 파일 통계, naming-check 리포트를 그대로
   반환합니다(가공하거나 설명을 덧붙이지 않은 원본 데이터입니다).
3. 이 데이터와 직접 읽은 diff(`git diff <base>...HEAD`)를 바탕으로
   `templates/pr_template.md` 형식에 맞춰 PR 본문을 작성합니다.
   - **Summary**: diff 통계를 다시 나열하는 게 아니라, *왜* 이
     변경을 했는지 2~4개 불릿포인트로.
   - **Naming check**: 스크립트 출력을 그대로 붙여넣습니다.
   - **Test plan**: 리뷰어가 그대로 실행할 수 있는 구체적인 명령이나
     절차.
4. 작성한 본문을 사용자에게 보여주고, GitHub에 영향을 주는 작업을
   하기 전에 확인을 받습니다.
5. 확인을 받은 뒤에만 아래를 실행합니다.
   ```bash
   gh pr create --title "<title>" --body-file <path-to-drafted-body>
   ```

**규칙**

- 사용자가 본문을 명시적으로 승인하기 전에는 `gh pr create`나
  `git push`를 절대 실행하지 않습니다.
- naming-check에서 위반 사항이 나오면 조용히 고치거나 빼지 말고,
  초안에 그대로 드러내어 사용자가 판단하게 합니다.

## 네이밍 컨벤션 체크

```bash
python3 .claude/skills/naming-check/scripts/check_naming.py
```

## 테스트

```bash
python3 -m pytest tests/
```
