<p align="center">
  <img src="remaio.png" alt="DARK INFINITE" width="100%">
</p>

<h1 align="center">DARK INFINITE</h1>

<p align="center">
  <b>Owner-only moderation and security bot</b><br>
  moderation · anti-abuse · owner protection
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-0ea5e9?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/discord.py-2.x-5865F2?style=flat-square&logo=discord&logoColor=white" alt="discord.py">
  <img src="https://img.shields.io/badge/Components_V2-enabled-f472b6?style=flat-square" alt="Components V2">
  <img src="https://img.shields.io/badge/37_active_cogs-8b5cf6?style=flat-square" alt="37 active cogs">
  <img src="https://img.shields.io/badge/MIT-22c55e?style=flat-square" alt="MIT">
</p>

<p align="center">
  <a href="#about">About</a> ·
  <a href="#render-web-service-deployment">Render Deployment</a> ·
  <a href="#features">Features</a> ·
  <a href="#setup">Setup</a> ·
  <a href="#environment">Environment</a>
</p>

---

## About

**DARK INFINITE** is configured for one owner and loads moderation, anti-abuse, and owner-protection features. Help commands are disabled.

---

## Quick Start

```bash
pip install -r requirements.txt
copy .env.example .env
python rem.py
```

| Step | Command | Notes |
|:---:|:---|:---|
| 1 | `pip install -r requirements.txt` | Install dependencies |
| 2 | Copy `.env.example` → `.env` | Add your bot token |
| 3 | `python rem.py` | Start the bot |

**Required in `.env`:**

```env
TOKEN=your_discord_bot_token
```

Enable **Message Content** and **Server Members** intents in the Discord Developer Portal.

---

## Render Web Service Deployment

This bot is compatible with a Render Web Service. It exposes a Flask health endpoint and the app is started directly with Python.

### Render settings

#### Build command

```bash
pip install --no-cache-dir -r requirements.txt
```

#### Start command

```bash
python rem.py
```

#### Health check

Render can ping:

```text
/health
```

The bot also listens on the `PORT` environment variable. Default is `8080`.

### Render environment variable

```env
TOKEN=your_discord_bot_token
```

That is the only value you need to add manually. The owner ID and other settings have built-in defaults; Render provides `PORT` automatically.

### Recommended Render setup

- Service type: **Web Service**
- Runtime: **Python 3.11**
- Build command: `pip install --no-cache-dir -r requirements.txt`
- Start command: `python rem.py`
- Health check path: `/health`
- Auto-Deploy: optional

The free Render instance can spin down after inactivity, which interrupts a continuously connected Discord bot. Use an always-on instance if the bot must stay online continuously.

---

## Features

- Moderation: ban, unban, kick, timeout, warn, role management, message purge, and snipe
- Anti-abuse: antinuke and automod protections for spam, caps, invites, links, mass mentions, and emoji spam
- Owner protection and role recovery
- Each successfully completed owner prefix command deletes its command message; five seconds later the bot deletes the latest message in channel `1553703435000348783`
- Prefix help commands are disabled

---

## Setup

| Requirement | Purpose |
|:---|:---|
| Python **3.11+** | Runtime |
| Discord **bot token** | Authentication |
| **Message Content** intent | Prefix commands |
| **Server Members** intent | Mod, welcome, security |

**Permissions:** The bot needs **Manage Messages** in the command channel and channel `1553703435000348783` for the automatic cleanup. Role commands require **Manage Roles**, with the bot role above roles it manages.

Only the configured bot owner can use bot commands.

---

## Environment

| Key | Required | Purpose |
|:---|:---:|:---|
| `TOKEN` | Yes | Discord bot token |

All other settings use built-in defaults. In Render, add only `TOKEN`; Render supplies `PORT` automatically.

---

## Project Structure

```text
rem.py              → entry point and health endpoint
core/               → bot class, context, and owner-only checks
cogs/events/        → owner protection and reactions
cogs/moderation/    → moderation actions
cogs/antinuke/      → anti-nuke listeners
cogs/automod/       → automod listeners
utils/              → config, database, and shared helpers
db/                 → SQLite database helper
```

---

## Development

```bash
python -m compileall rem.py cogs utils core
```

Health endpoint: `GET http://127.0.0.1:8080/health`
Logs: `logs/rem.log`

**Security tips:** Never commit `.env` or database files. Regenerate your token if leaked.

---

<p align="center">
  <sub>MIT License</sub>
</p>
