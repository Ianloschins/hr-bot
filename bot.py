import os
import io
import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import random

# Load secrets from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
HResponse = os.getenv("OPENROUTER_API_KEY")

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Complaint sessions tracking
pending_complaints = {}
emoji_reactions = ["📉", "🔥", "😬", "💀", "💼", "✍️", "🤡", "🧃", "🔪"]

@bot.event
async def on_ready():
    print(f"🤖 {bot.user} is online and ready to HR roast!")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="hr-violations")
    if channel:
        await channel.send(f"👋 Welcome {member.mention} to the server. I’m **Petrie Dish - HR**, your least favorite person here. My job? Terminating dreams and forwarding complaints. Enjoy your stay. 💼")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Handle complaint follow-up
    if message.author.id in pending_complaints:
        target_name, channel_id = pending_complaints[message.author.id]
        if message.channel.id == channel_id:
            reason = message.content
            await message.channel.send(f"📄 Filing official complaint against {target_name}...\n\"{reason}\" 😤📎")
            image_stream = await generate_custom_termination(target_name, reason)
            await message.channel.send(file=discord.File(image_stream, filename=f"termination_{target_name}.png"))
            del pending_complaints[message.author.id]
            return

    # Automatic HR responses in specific channels or DMs
    if message.channel.name == "hr-violations" or isinstance(message.channel, discord.DMChannel):
        msg = message.content.lower()
        if "complaint" in msg:
            await message.channel.send("📋 Complaint received. Filed directly into the shredder. 🔥🗑️")
        elif "help" in msg:
            await message.channel.send("🚨 HR is currently hiding under the desk. Try again later. 😵‍💫")
        elif "fired" in msg:
            await message.channel.send("🔥 You're not fired. Yet. But you're on thin ice. 🧊👀")
        else:
            await message.channel.send("📝 Your message has been forwarded to our 'do not care' folder. 🤷‍♂️📎")

    await bot.process_commands(message)

# !terminate command
@bot.command()
async def terminate(ctx, member: discord.Member):
    await ctx.send(f"📄 Generating termination letter for {member.display_name}... 💼💀")
    image_stream = await generate_meme_termination(member.display_name)
    await ctx.send(file=discord.File(image_stream, filename=f"termination_{member.display_name}.png"))

# !complaint command
@bot.command()
async def complaint(ctx, member: discord.Member):
    pending_complaints[ctx.author.id] = (member.display_name, ctx.channel.id)
    await ctx.send(f"📝 What is your complaint about {member.display_name}? Please reply in this channel. 📎")

# !askhr command (AI roast)
@bot.command()
async def askhr(ctx, *, question: str):
    await ctx.send("📠 Forwarding your question to our only HR Rep...")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://yourdiscordserver.com",
        "X-Title": "GosuPandaHR"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are GosuPanda, the most condescending HR rep in Discord history. "
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
        emoji = random.choice(emoji_reactions)
        await ctx.send(f"🧾 HR Response {emoji}:\n{reply}")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("❌ HR ran away. Probably out on a smoke break. 🫠")

# !clearchat command
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clearchat(ctx, amount: int = 10):
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Deleted {len(deleted) - 1} messages (not counting the command). HR sweep complete. 💨")

# Generate termination meme
async def generate_meme_termination(name):
    img = Image.open("termination_template.png").convert("RGBA")
    draw = ImageDraw.Draw(img)

    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=38)
    font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size=23)

    title = "Termination Notice"
    body = f"""Dear {name},

You have been TERMINATED
for violating HR meme policy.

Effective immediately, your services are no longer required."""

    signature = "Best,\n\nGosuPanda\nHR – Petri Dish Server"

    draw.text((50, 60), title, font=font_title, fill="black")
    draw.multiline_text((50, 250), body, font=font_text, fill="black", spacing=5)
    draw.multiline_text((50, 650), signature, font=font_text, fill="black", spacing=4)

    stream = io.BytesIO()
    img.save(stream, format='PNG')
    stream.seek(0)
    return stream

# Generate complaint-based termination letter
async def generate_custom_termination(name, reason):
    img = Image.open("termination_template.png").convert("RGBA")
    draw = ImageDraw.Draw(img)

    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=38)
    font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size=23)

    title = "Termination Notice"
    body = f"""Dear {name},

Following a formal review of conduct within the Petri Dish Server,
it has been brought to our attention that the following incident occurred:

\"{reason}\"

Upon evaluation, we have concluded that this behavior constitutes
a severe violation of both common decency and server policy.

Effective immediately, your digital employment has been terminated.
We wish you all the best in your future infractions elsewhere."""

    signature = "Respectfully,\n\nGosuPanda\nHR – Petri Dish Server"

    draw.text((50, 40), title, font=font_title, fill="black")
    draw.multiline_text((50, 110), body, font=font_text, fill="black", spacing=5)
    draw.multiline_text((50, 460), signature, font=font_text, fill="black", spacing=4)

    stream = io.BytesIO()
    img.save(stream, format='PNG')
    stream.seek(0)
    return stream

# Start bot
bot.run(TOKEN)
