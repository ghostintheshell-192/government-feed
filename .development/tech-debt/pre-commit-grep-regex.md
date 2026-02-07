---
type: bug
priority: low
status: open
discovered: 2026-02-07
related: []
related_decision: null
report: null
---

# Pre-commit hook: grep doesn't support \s+ regex

## Problem

The pre-commit hook's security check for private keys uses `\s+` in the grep pattern, but basic `grep` doesn't support Perl-style regex. This causes 27 "unrecognized option" errors per commit (one per staged file). The commit still succeeds because the hook doesn't fail on grep errors.

## Analysis

The pattern `-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----` uses `\s+` which requires either `grep -P` (Perl regex) or `grep -E` with `[[:space:]]+` (POSIX extended regex). The current invocation likely uses basic grep which doesn't understand `\s`.

## Possible Solutions

- **Option A**: Use `grep -P` flag — enables Perl regex, `\s+` works as-is. Not available on all systems (macOS lacks it by default).
- **Option B**: Use `grep -E` with POSIX classes — change `\s+` to `[[:space:]]+`. Portable across all systems.
- **Option C**: Use a simpler fixed-string pattern — `grep -F '-----BEGIN'` is enough to catch private keys. Less precise but simpler.

## Recommended Approach

**Option B** — most portable while keeping the pattern precise:
```
-----BEGIN[[:space:]]+(RSA[[:space:]]+)?PRIVATE[[:space:]]+KEY-----
```

## Notes

- Non-blocking: commits succeed despite the grep errors
- The noise is cosmetic but annoying (27 error lines per commit in this session)
- Located in `.githooks/pre-commit`

## Related Documentation

- **Code Locations**: `.githooks/pre-commit` (security check section)
