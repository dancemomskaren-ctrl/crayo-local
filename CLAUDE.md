# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Chipotlai Max** is a meme fork of [OpenCode](https://github.com/anomalyco/opencode) (MIT, 120k+ stars) that ships Chipotle's "Pepper AI" support bot as the default model via the [chipotle-llm-provider](https://github.com/Gonzih/chipotle-llm-provider) proxy.

## Build & Run

```bash
bun install                    # install deps
./start-chipotlai.sh           # starts proxy + CLI together

# Or manually:
cd chipotle-llm-provider && npm install && npm run dev  # Terminal 1: proxy
bun run dev                                              # Terminal 2: CLI
```

Build: `bun run --cwd packages/opencode script/build.ts`

## Architecture

- **Provider system**: `packages/opencode/src/provider/` — branded `ProviderID`/`ModelID` types via Effect Schema. Chipotle Pepper registered in `schema.ts` (well-known ID), `provider.ts` (BUNDLED_PROVIDERS + CUSTOM_LOADERS + model injection).
- **Theme**: `packages/ui/src/styles/theme.css` — CSS custom properties for light/dark modes. Chipotle palette applied (primary `#AC2318`, dark backgrounds `#1A0A04`/`#2A1508`).
- **Logo**: `packages/ui/src/components/logo.tsx` — burrito emoji components (Mark, Splash, Logo).
- **Proxy**: `chipotle-llm-provider/` git submodule — OpenAI-compatible at `localhost:3000/v1`, model `pepper-1`.
- **Monorepo**: Bun workspaces + Turborepo. Package renamed from `opencode` to `chipotlai` — workspace refs in `packages/web/package.json` and imports in `packages/web/src/components/` updated accordingly.
