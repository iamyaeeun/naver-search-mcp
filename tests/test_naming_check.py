import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "naming-check" / "scripts"))

from check_naming import scan  # noqa: E402


def make_diff(filename: str, added_lines: list[str]) -> str:
    body = "\n".join(f"+{line}" for line in added_lines)
    return f"diff --git a/{filename} b/{filename}\n--- a/{filename}\n+++ b/{filename}\n@@ -0,0 +1,{len(added_lines)} @@\n{body}\n"


def test_flags_camelcase_python_function():
    diff = make_diff("mod.py", ["def getUserName():", "    pass"])
    violations = scan(diff)
    assert any(v[2] == "getUserName" and v[3] == "not snake_case" for v in violations)


def test_flags_non_ascii_variable():
    diff = make_diff("mod.py", ["사용자 = 1"])
    violations = scan(diff)
    assert any(v[3] == "non-ASCII identifier" for v in violations)


def test_allows_snake_case_python():
    diff = make_diff("mod.py", ["def get_user_name():", "    pass"])
    assert scan(diff) == []


def test_flags_snake_case_js_function():
    diff = make_diff("mod.js", ["function get_user_name() {}"])
    violations = scan(diff)
    assert any(v[3] == "not camelCase" for v in violations)


def test_allows_all_caps_python_constant():
    diff = make_diff("mod.py", ["MAX_RETRIES = 3"])
    assert scan(diff) == []
