# Supersonic Control Core — Operator Guide v3

[![Live Preview](https://img.shields.io/badge/Pages-Live_Preview-brightgreen)](./)  
*(Workflow will rewrite this badge link to your repo's Pages URL on release.)*

## What’s new in v3
- 🧠 **Smart semantic versioning**: `fix:`→patch, `feat:`→minor, `breaking:`→major
- 🔔 **Discord + Slack** webhooks (optional) for release/build notifications
- 🌐 **Pages Preview badge** injected into README + release notes
- 🔧 **Auto-tag & push** enabled by default (can be disabled via env)

## Install
```bash
pip install requests semver watchdog colorama rich pyttsx3 playsound
```

## Make targets (after including make/ControlCore.mk)
```bash
make ai-build        # Build with AI summary
make ai-watch        # Watch + AI
make ai-bump         # Compute next version + tag + push
make ai-release      # bump -> build -> (optional) push -> notify
```

## Env (optional)
```bash
export SUP_ENGINE_MODE=hybrid
export SUP_DISCORD_WEBHOOK=https://discord.com/api/webhooks/XXXX
export SUP_SLACK_WEBHOOK=https://hooks.slack.com/services/XXXX
export SUP_AUTOPUSH=1      # default ON in v3
```
