import os
import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # This is required for member join event
bot = commands.Bot(command_prefix="!", intents=intents)

# Function to check if a message is "mean" using OpenRouter API
async def is_mean_message(message_content):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "X-Title": "HRBot"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",  # You can adjust the model if needed
        "messages": [
            {
                "role": "system",
                "content": f"Is this message mean or offensive: {message_content}"
            }
        ]
    }

    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)
        r.raise_for_status()
        response_text = r.json()["choices"][0]["message"]["content"].strip().lower()
        return 'yes' in response_text or 'offensive' in response_text
    except Exception as e:
        print(f"Error checking mean message: {e}")
        return False

# Bot event: Check every new message
@bot.event
async def on_message(message):
    if message.author == bot.user:  # Don't let the bot reply to its own messages
        return

    # Respond to "HR" in any case
    if 'hr' in message.content.lower():
        await message.channel.send(f"{message.author.mention}, you've reached HR! How can I assist you today? 📋")

    # Check if the message is mean using OpenRouter API
    is_mean = await is_mean_message(message.content)
    
    if is_mean:
        # Respond to the mean message with a sentence
        await message.channel.send(f"{message.author.mention}, please be respectful. Let's keep the chat friendly!")

    # Always process commands (this allows the bot to respond to commands like !terminate, !complaint, etc.)
    await bot.process_commands(message)

# Bot event: When a new member joins the server
@bot.event
async def on_member_join(member):
    # Send a message introducing HR in the first channel the bot can access
    channel = discord.utils.get(member.guild.text_channels, name="hr-violations")  # You can change this to any channel you want
    if channel:
        await channel.send(f"👋 Welcome {member.mention} to the server! I’m **HR Bot**, your very unhelpful HR representative. "
                           "I’m here to make your life a little more miserable."
                           "Use commands like `!complaint <member>` to file a complaint. "
                           "If you need to ask something, just mention **HR**! 📝💼")

# Example command: !terminate
@bot.command()
async def terminate(ctx, member: discord.Member):
    await ctx.send(f"📄 Generating termination letter for {member.display_name}... 💼💀")
    # Your termination generation code here

# Example command: !complaint
@bot.command()
async def complaint(ctx, member: discord.Member):
    await ctx.send(f"📝 What is your complaint about {member.display_name}? Please reply in this channel. 📎")
    # Your complaint handling code here

# Example command: !askhr (AI roast)
@bot.command()
async def askhr(ctx, *, question: str):
    await ctx.send("📠 Forwarding your question to our only HR Rep...")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "X-Title": "HRBot"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",  # You can adjust the model if needed
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are GosuPanda, the most condescending HR rep in Discord history. "
                    "You are a Discord HR bot for a server that thrives on sarcasm and disdain. "
                    "You hate your job, but you love firing people. Your responses are filled with sarcastic professionalism, corporate lingo, and personal jabs. "
                    "You're overly formal, incredibly judgmental, and respond like someone who thinks 'Teamwork makes the dream work' is grounds for termination. "
                    "Do not be nice. Ever. Be a corporate jerk in HR form. "
                    "You like to keep it short and to the point, but always with a sarcastic twist. "
                    "If the question is about firing someone, make it sound like they should have seen it coming. "
                    "If they ask for advice, give them the most backhanded compliment possible."
                )
            },
            {"role": "user", "content": question}
        ]
    }

    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)
        reply = r.json()["choices"][0]["message"]["content"]
        await ctx.send(f"🧾 HR Response:\n{reply}")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("❌ HR ran away. Probably out on a smoke break. 🫠")

# Start the bot
bot.run(DISCORD_TOKEN)
