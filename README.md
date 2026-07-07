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

`.claude/skills/` 아래 SKILL.md는 영어로 작성되어 있습니다. 전체 내용을
한글로 옮기면 다음과 같습니다.

### naming-check

> description: 현재 Git diff에서 새로 추가된 함수 및 변수 이름이 저장소의
> 네이밍 규칙을 따르는지 검사합니다. (Python은 snake_case, JS/TS는
> camelCase, 의미 없는 한 글자 이름 및 비-ASCII 식별자 금지) PR을 생성하기
> 전이나, 사용자가 네이밍/코드 컨벤션/변수명 검사를 요청할 때 사용합니다.

#### 네이밍 규칙 검사

검사 범위는 의도적으로 제한되어 있습니다.

현재 Git diff에서 **추가된 줄(added lines)** 만 확인하며,
그중에서도 **함수 및 변수 선언**만 검사합니다.

전체 린터(linter)를 실행하지 않으며,
기존(변경되지 않은) 코드는 검사하지 않습니다.

**사용 시점**

- PR 초안을 작성하거나 PR을 생성하기 직전
- 사용자가 현재 변경 사항에 대해
  - 네이밍 규칙
  - 변수명
  - 코드 컨벤션
  검사를 요청한 경우

**실행 방법**

```bash
python3 .claude/skills/naming-check/scripts/check_naming.py [git-diff-args]
```

- 인자 없음: unstaged 상태의 작업 트리 변경 사항을 diff합니다.
- `--cached`: staged된 변경 사항을 diff합니다.
- `<base>...HEAD`: 기준(base) 브랜치/참조와 비교하여 diff합니다.
  (PR을 생성하기 전에 이 방식을 사용하세요.)

스크립트는 위반 사항을 발견하면 0이 아닌 종료 코드를 반환하고
`file:line — issue` 형식의 목록을 출력하며, 문제가 없으면 ✅ 한 줄만
출력합니다.

**적용되는 규칙**

1. Python 함수/변수 이름은 `snake_case`여야 합니다. (모두 대문자인
   상수는 예외입니다.)
2. JS/TS 함수/변수 이름은 `camelCase`여야 합니다.
3. 비-ASCII(예: 한글) 식별자는 허용되지 않습니다.
4. 흔히 쓰이는 루프/인덱스 표기(`i, j, k, x, y, n, _`)를 제외하고,
   한 글자짜리 이름은 허용되지 않습니다.

**결과 보고**

PR 워크플로우의 일부로 실행된 경우, 스크립트의 출력을 다른 말로 풀어
쓰지 말고 PR 설명의 "Naming check" 섹션에 그대로(verbatim) 포함해야
합니다.

### pr-draft

> description: 현재 브랜치와 기준(base) 브랜치의 diff를 기반으로 PR
> 설명(PR Description)을 작성하고, 네이밍 규칙 검사 결과를 포함하며,
> 사용자가 확인한 경우에만 `gh pr create`로 PR을 생성합니다. 사용자가
> PR 생성, PR 초안 작성, "PR 만들어줘", "PR 초안" 등을 요청할 때
> 사용합니다.

#### PR 초안 작성

현재 브랜치의 변경 사항(diff)을 기반으로 PR 설명을 작성하고,
사용자가 확인한 후에만 PR을 생성합니다.
사용자 동의 없이 PR을 푸시하거나 생성해서는 안 됩니다.

**절차**

1. 기준(base) 브랜치를 확인합니다(기본값: `main`). 또한 `git status`를
   실행하여 작업 트리에 커밋되지 않은 변경 사항이 있는지 확인합니다.
   (의도치 않게 변경 사항을 잃지 않도록 하기 위함입니다.)
2. PR 컨텍스트 수집 스크립트를 실행합니다.
   ```bash
   python3 .claude/skills/pr-draft/scripts/gather_pr_context.py <base_ref>
   ```
   이 스크립트는 커밋 목록, 변경된 파일 통계, 그리고 naming-check
   리포트(naming-check 참고)를 반환합니다. 전부 가공되지 않은 원본
   데이터이며, 별도의 설명 문구는 포함되지 않습니다.
3. 이 데이터와, 직접 읽은 diff(`git diff <base>...HEAD`)를 바탕으로
   `templates/pr_template.md` 형식에 맞춰 PR 본문을 작성합니다.
   - **Summary**: diff 통계를 그대로 다시 서술하는 것이 아니라, *왜*
     이 변경을 했는지에 대한 2~4개의 불릿포인트.
   - **Naming check**: 스크립트의 출력을 그대로(verbatim) 붙여넣습니다.
   - **Test plan**: 리뷰어가 실행할 수 있는 구체적인 명령 또는 절차.
4. 작성된 본문을 사용자에게 보여주고, GitHub에 영향을 주는 작업을
   하기 전에 확인을 요청합니다.
5. 명시적으로 확인받은 후에만 다음을 실행합니다.
   ```bash
   gh pr create --title "<title>" --body-file <path-to-drafted-body>
   ```

**규칙**

- 사용자가 작성된 본문을 명시적으로 승인하기 전에는 절대 `gh pr create`
  (또는 `git push`)를 실행해서는 안 됩니다.
- naming-check에서 위반 사항이 보고되면, 조용히 고치거나 누락시키지
  말고 초안에 그대로 드러내어 사용자가 판단할 수 있도록 해야 합니다.

## 네이밍 컨벤션 체크

```bash
python3 .claude/skills/naming-check/scripts/check_naming.py
```

## 테스트

```bash
python3 -m pytest tests/
```
