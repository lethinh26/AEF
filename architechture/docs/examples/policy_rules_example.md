# Policy examples — illustration only, NOT executable production policy

```text
PERMIT read_code when
    user/agent identity is authenticated
    AND mission warrant is active
    AND requested repo is in goal scope
    AND tenant matches resource tenant.

PERMIT branch_patch when
    mission profile == branch_only
    AND target branch starts_with "aeo/"
    AND patch paths do not intersect protected paths
    AND sandbox identity is valid
    AND resource budget reservation succeeds.

REQUIRE_APPROVAL merge_protected when
    patch digest equals approved digest
    AND human approver has repo-owner scope
    AND approval is single-use and unexpired.

DENY production_database_delete by default.
DENY secrets_export by default.
DENY host_shell_exec by default.
DENY external_network_access unless explicit egress allowlist.
```

Đây là *policy intent*. Khi triển khai cần schema/OPA Rego (hoặc typed rules), unit tests và enforcement tại Tool Gateway, không cài các mệnh đề này như prompt hướng dẫn cho LLM.
