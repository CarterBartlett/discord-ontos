# Discord Ontos

## Features
- Dice rolling with dice notation
- Audio bot

## Non-Docker

### Installation
- Run the following commands:
    - `python -m venv venv`
    - `pip install -r requirements.txt`

### Running the bot
- Copy or rename `.env-sample` to `.env` and set environment variables [See Environment Variables section below](#environment-variables)
- Run `python bot.py`

## Docker
- Run `docker-compose up -d -e ENV_VARS` [See Environment Variables section below](#environment-variables)

## Environment Variables
- DISCORD_API_TOKEN (DISCORD_SECRET if using Docker method) - Your Discord bot's API token, ensure privileged intents are allowed
- YOUTUBE_COOKIES - A base64 encoded set of Youtube Cookies (Optional, but highly recommended)
    - For this, I recommend using [cookies.txt](https://addons.mozilla.org/en-GB/firefox/addon/cookies-txt/) for Firefox or [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc?pli=1) for Chromium browsers
    - After obtaining the cookies, encode them into base64 before passing them into the environment variables, using a service such as [base64encode.org](https://www.base64encode.org/)
