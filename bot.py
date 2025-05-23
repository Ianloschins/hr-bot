import os
import io
import discord
import requests
import textwrap
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# Load env vars
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Intents and bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Conversation tracker
user_conversations = {}  # {channel_id: user_id}
pending_complaints = {}  # {user_id: (target_name, channel_id)}
last_user = {}
interruption_acknowledged = {}  # {channel_id: user_id}
conversation_history = {}  # {channel_id: [{"role": ..., "content": ...}]}

# AI reply function
async def get_ai_response(prompt, channel_id=None, rude=False):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "X-Title": "HRBot"
    }

    system_prompt = (
        "You are GosuPanda, the most condescending HR rep in Discord history. "
        "Do not be nice. Ever. Be a corporate jerk in HR form but always give the right answer. "
        "You like to keep short conversations and avoid small talk. But still give right answers. "
        "If someone interrupts you, be rude and sarcastic about it. "
        "If the user asks for help, provide a snarky yet helpful response. "
        "You are knowledgeable about server rules, policies, games, and memes. "
        "If the user files a complaint, generate a passive-aggressive HR letter body (no greeting or sign-off)."
        "When it comes to gaming complaints, be especially harsh. and don't involve company only the team"
    )

    if rude:
        prompt = "Someone interrupted our HR convo. Say something sarcastic and mean about being interrupted."
        history = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
    else:
        history = [{"role": "system", "content": system_prompt}]
        if channel_id in conversation_history:
            history.extend(conversation_history[channel_id])
        history.append({"role": "user", "content": prompt})

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": history
    }

    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        reply = res.json()["choices"][0]["message"]["content"]

        if not rude and channel_id:
            conversation_history.setdefault(channel_id, []).append({"role": "user", "content": prompt})
            conversation_history[channel_id].append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        print("AI Error:", e)
        return "HR went on break again. Try later."

# Events
@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready to HR roast!")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="welcome-🖕✨")
    if channel:
        await channel.send(
            f"👋 Welcome {member.mention} to the server. I’m **HR**, your least favorite person here. "
            "Use `!complaint <user>`, or just say HR and I’ll magically appear with sarcasm."
        )

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()
    channel_id = message.channel.id
    author_id = message.author.id

    mentioned_hr = "hr" in content or bot.user.mentioned_in(message)
    continuation = user_conversations.get(channel_id) == author_id
    interrupted = (channel_id in user_conversations and user_conversations[channel_id] != author_id)

    if author_id in pending_complaints:
        target_name, origin_channel = pending_complaints[author_id]
        if origin_channel == channel_id:
            reason = message.content.strip()
            prompt = (
                f"Write a sarcastic HR-style termination letter body for {target_name}, "
                f"with the reason: \"{reason}\". Do not include a greeting or sign-off."
            )
            ai_letter = await get_ai_response(prompt, channel_id=channel_id)
            image_stream = await generate_custom_termination(target_name, ai_letter)
            await message.channel.send(file=discord.File(image_stream, filename=f"termination_{target_name}.png"))
            del pending_complaints[author_id]
            return

    if interrupted and interruption_acknowledged.get(channel_id) != author_id:
        rude = await get_ai_response("", rude=True)
        await message.channel.send(f"{message.author.mention}, {rude}")
        interruption_acknowledged[channel_id] = author_id
        return

    if mentioned_hr or continuation:
        response = await get_ai_response(message.content, channel_id=channel_id)
        await message.channel.send(f"{message.author.mention}, {response}")
        user_conversations[channel_id] = author_id
        interruption_acknowledged.pop(channel_id, None)

    await bot.process_commands(message)

# commands!!
@bot.command()
async def askhr(ctx, *, question: str):
    await ctx.send("📠 Forwarding your question to HR...")
    reply = await get_ai_response(question, channel_id=ctx.channel.id)
    await ctx.send(f"🧾 HR Response:\n{reply}")

@bot.command()
async def complaint(ctx, member: discord.Member):
    pending_complaints[ctx.author.id] = (member.display_name, ctx.channel.id)
    await ctx.send(f"📝 What is your complaint about {member.display_name}? Please reply in this channel. 📎")

@bot.command()
async def terminate(ctx, member: discord.Member):
    await ctx.send(f"📄 Generating termination letter for {member.display_name}... 💼💀")
    image_stream = await generate_custom_termination(member.display_name, "Violation of HR meme policy.")
    await ctx.send(file=discord.File(image_stream, filename=f"termination_{member.display_name}.png"))

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clearchat(ctx, amount: int = 10):
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Deleted {len(deleted) - 1} messages. HR sweep complete.")

@bot.command()
async def reset(ctx):
    conversation_history.pop(ctx.channel.id, None)
    await ctx.send("🧠 HR has forgotten this conversation. You're lucky.")

# Termination letter generation :)
async def generate_custom_termination(name, reason_text):
    img = Image.open("termination_template.png").convert("RGBA").resize((1024, 1024))
    draw = ImageDraw.Draw(img)

    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
    font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 23)

    reason_text = reason_text.replace("[Employee]", name)

    draw.text((300, 80), "Termination Notice", font=font_title, fill="black")
    draw.text((50, 180), f"Dear {name},", font=font_text, fill="black")

    sentences = [s.strip() for s in reason_text.split('.') if s.strip()]
    y = 250
    for sentence in sentences:
        line = sentence + "."
        wrapped = textwrap.wrap(line, width=80)
        for wline in wrapped:
            draw.text((50, y), wline, font=font_text, fill="black")
            y += 30
        y += 15

    y += 30
    signoff = "Respectfully,\n\nGosuPanda\nHR – Petri Dish Server"
    draw.multiline_text((50, 850), signoff, font=font_text, fill="black", spacing=6)

    stream = io.BytesIO()
    img.save(stream, format="PNG")
    stream.seek(0)
    return stream

bot.run(DISCORD_TOKEN)
