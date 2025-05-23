HRBot – GosuPanda, Your Condescending Discord HR Rep 😈

HRBot is a Discord bot that embodies the snarky, passive-aggressive spirit of an overworked corporate HR rep. Designed to answer questions, handle mock complaints, and roast users with termination letters, it’s the perfect bot for meme-heavy servers, gaming clans, or anyone needing a sarcastic watchdog.

________________________________________________________________________________________________________________________________________________________________________________________

🧠 Features

- Snarky AI-Powered Replies – Responds to questions with sarcastic HR wisdom using OpenRouter (GPT-3.5).

- Complaint Handling – Collects user complaints and generates a sassy termination letter image.

- Custom Termination Letters – Instantly fire your friends (satirically!) with personalized HR-generated content.

- Chat Cleaning – Authorized users can delete messages with `!clearchat`.

- Welcome Message – Greets new users in a delightfully unwelcoming HR tone.

________________________________________________________________________________________________________________________________________________________________________________________

🚀 Setup

Prerequisites

- Python 3.8+

- A Discord bot token

- [OpenRouter](https://openrouter.ai) API key

- A font (DejaVuSans) and image template (`termination_template.png`)

- Environment variables stored in a `.env` file

Installation

1. Clone the repo

   git clone git@github.com:Ianloschins/hr-bot.git

   cd hr-bot

Install dependencies

pip install -r requirements.txt

Create a .env file

    DISCORD_TOKEN=your_discord_token_here

    OPENROUTER_API_KEY=your_openrouter_api_key_here

Add your termination letter template

Place a termination_template.png image in the project root (1024x1024 preferred).

🧾 Commands

Command	Description

    !askhr <question>	Ask HR anything. Expect sarcasm.

    !complaint @user	Start a complaint process against a user.

    !terminate @user	Immediately generate a termination letter.

    !clearchat <num>	Deletes the specified number of recent messages. Requires Manage Messages permission.

🤖 AI Behavior

    The bot uses a predefined system prompt to act as a curt and bitter HR rep. It never tries to be nice. It’s direct, witty, sarcastic, and passively aggressive.

🧰 Tech Stack

    -Python

    -Discord.py

    -OpenRouter / OpenAI API

    -PIL (Pillow) for image generation

🛡 Disclaimer

    This bot is satirical and meant for entertainment purposes only. It’s not actually managing your HR.

📸 Sample Output

💼 Author

    Built by Ian Loschinskey – a professional with too much sarcasm and not enough PTO.