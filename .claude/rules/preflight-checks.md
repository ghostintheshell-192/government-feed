# Pre-flight Checks

## Session Startup (ALWAYS, first message)

At the start of every conversation, before doing anything else:

1. **Read project context** — `.development/ARCHITECTURE.md` and `.development/CURRENT-STATUS.md`
2. **Read hand-off notes** — latest file in `.memory-bank/` (session continuity)
3. **Wait for user request** — do NOT start working proactively. If the user doesn't make a request immediately, wait for the next message.

## Before Code Modifications

When the user makes a request that involves code changes:

1. **Check git state** — `git status`, `git branch`. Report branch and any uncommitted changes.
2. **Validate branch** — never work on `main` or `develop` directly. If on the wrong branch, ask the user how to proceed (stash? commit? new branch?) before touching any code.
3. **Create feature branch if needed** — only after aligning with the user.

## Agent Exploration

When launching an Explore agent, always instruct it to read `.development/ARCHITECTURE.md` first to orient its search.
