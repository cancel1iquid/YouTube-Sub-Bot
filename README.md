
## Star Goals

| ⭐ Goal        | Unlocks                                        | Status |
|---------------|------------------------------------------------|----|
| 50 Stars      | Add YouTube **Comment Bot**                    | 🔒 |
| 100 Stars     | Release **Discord Bot Source**                 | 🔒 |
| 250 Stars     | Release **Gmail Generator / UD Chrome Driver** | 🔒 |

Please star and follow (:

# YouTube Sub Bot

Python based tool that does youtube subs and youtube likes. Includes a cookie refresher for refreshing cookies, the main purpose of this was for my server subsavr which was a discord bot, I ended the project early due to another project i have spent 100% of my time on. Devs you can add me on discord: z4mb1ee . 
## Features

- Supports two modes: `sub` (subscribe to a channel) and `like` (like a specific video)
- Automatically tests and uses valid `x-goog-authuser` values per cookie
- Uses real browser headers and context values
- Rotates proxies if provided
- Threading
- Includes a full Selenium-based login refresher for keeping cookies alive

## File Overview

- `aio.py`: YouTube Sub & Like Bot
- `refresh.py`: Keeps `refresh.txt` updated by logging into Google accounts.
- `refresh.txt`: Live cookies pulled from active Gmail sessions.
- `gmails.txt`: List of Gmail accounts in either `email:pass:recovery` or `email|pass|recovery` format.
- `proxies.txt`: List of proxies to use (supports both `user:pass@ip:port` and `ip:port`).

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Add your Gmail accounts to `gmails.txt`.

3. (Optional) Add working proxies to `proxies.txt`.

4. Start the refresher script:

```bash
python refresh.py
```

This will log into each account and continuously update `refresh.txt` with working cookies.

5. Start the bot:

```bash
python aio.py
```

Follow the prompts to choose `sub` or `like`, then enter a YouTube channel or video URL.

## Notes

- Only valid and working cookies will be used.
- `aio.py` reads from `refresh.txt`, which is updated live by `refresh.py`.
- Make sure cookies are actually subscribed to YouTube or have accepted terms.

## Legal Notice

This tool is for testing, research, and educational use only. Use it at your own risk. The developer is not responsible for any misuse or violations of third-party terms.

Lol told chatgpt to make this readme i aint doing allat
