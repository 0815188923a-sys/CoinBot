import discord
from discord.ext import commands
import sqlite3
import random
import os

# ตั้งค่าบอท
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# เชื่อม Database
conn = sqlite3.connect("coinbot.db")
cursor = conn.cursor()

# สร้างตาราง
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    discord_id TEXT PRIMARY KEY,
    ชื่อ TEXT,
    เงิน INTEGER DEFAULT 0,
    exp INTEGER DEFAULT 0,
    อาชีพ TEXT DEFAULT 'ชาวบ้าน'
)
""")
conn.commit()

# ข้อมูลอาชีพ
jobs = {
    "คนเลี้ยงหมู": {"ราคา": 1000,     "emoji": "🐷", "work_min": 100,  "work_max": 300},
    "ช่างตีเหล็ก": {"ราคา": 3000,     "emoji": "⚒️", "work_min": 200,  "work_max": 500},
    "นักรบ":       {"ราคา": 7000,     "emoji": "🗡️", "work_min": 300,  "work_max": 700},
    "จอมเวทย์":    {"ราคา": 15000,    "emoji": "🧙", "work_min": 500,  "work_max": 1000},
    "กษัตริย์":    {"ราคา": 15000000, "emoji": "👑", "work_min": 1000, "work_max": 2000},
}

# GIFs แต่ละระบบ
gifs = {
    "start":       [
        "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExY2hpM2ZydWFydmducHZmYjdqdHZ2aDUzMmtwaXd1ZG9manF5cG13ZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/132tfJl4NAMiU8/giphy.gif",
        "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWpjb2lzZWhnMW5ka2RkaGhmNXNkcmF5bWY1eGxrbmtlYXcxcm80ZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/zj0BxstyhGufC/giphy.gif",
    ],
    "work":        [
        "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcTYwaHVmaTl5NDB5Z290ZXV4d3EzZGYxcGp3MmwyM2o5dXUwaGptaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/LZmMH7lmHeNFe/giphy.gif",
        "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExejE4Z2RzODNhdGk1NTBzYnEzYTdnNzVsM2w1cG80N2h0eG0xaWxjNCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ruYMwmyOtpIxa/giphy.gif",
    ],
    "balance":     [
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExYXRxd2x4bHpnOThkbWU2NWF3d3Q2cXQwenYycmx3ZGxyODRibXdtaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BkqSYWqv8Zfva/giphy.gif",
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExc3dmbDU0bmtsa2VwemRmNjF4bDV1dnQ5bmY4NGFhZ3ZsZGxzMjkwZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9miyhIx8956y4/giphy.gif",
    ],
    "pay":         [
        "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExcWh2bmhkeW1sMXBwM25meWVibnl5M2ZqNzRlMmRrNXd3NXBuYXBtbSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dDzcbYi058lJS/giphy.gif",
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExbjdyeTV6Z2h6cWI2ZTdibGoxYWdrZTZ3cm9lc3piZmo3dXZrMjc0eiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/RZo6HXDTlBftS/giphy.gif",
    ],
    "leaderboard": [
        "https://media.tenor.com/QBQcOaH5FDEAAAAM/trophy-award.gif",
        "https://media.tenor.com/ypfMbBs_lhkAAAAM/winner.gif",
    ],
    "joblist":     [
        "https://media.tenor.com/g9Zs7IxSCiMAAAAM/thinking-hmm.gif",
    ],
    "buyjob":      [
        "https://media.tenor.com/IZEjBMcPpgIAAAAM/level-up.gif",
        "https://media.tenor.com/gBxRFt0WSZIAAAAM/upgrade.gif",
    ],
    "error":       [
        "https://media.tenor.com/2Yoyw3cByzkAAAAM/sad-cry.gif",
        "https://media.tenor.com/MKMBCaAFLNAAAAAM/no-no-no.gif",
    ],
}

def get_gif(key):
    return random.choice(gifs.get(key, gifs["error"]))

# ข้อความน่ารักแบบสุ่ม
cute_work = [
    "ทำงานเก่งมากเลยนะคะ~ 🥺💕",
    "หนูภูมิใจในตัวเธอมากเลย! 🌸",
    "ขยันจังเลยนะคะ ชอบมากๆ! ✨",
    "เธอทำได้ดีมากเลยค่ะ~ 💖",
]

cute_start = [
    "ยินดีต้อนรับสู่ครอบครัว CoinBot นะคะ~ 🌸",
    "หนูดีใจที่เธอมาเลยค่ะ! 💕",
    "เพื่อนใหม่แล้ว! หนูรักเธอเลยนะ~ 🥺",
]

cute_buy = [
    "โอ้โห! เธอรวยขึ้นแล้วนะคะ~ ✨",
    "เก่งมากเลย! อาชีพใหม่รอเธออยู่นะคะ 💖",
    "หนูดีใจด้วยเลยค่ะ~ 🌸",
]

# บอทพร้อม
@bot.event
async def on_ready():
    print(f"✅ CoinBot พร้อมแล้ว!")

# ลงทะเบียน
@bot.command()
async def start(ctx):
    discord_id = str(ctx.author.id)
    cursor.execute("SELECT * FROM players WHERE discord_id = ?", (discord_id,))
    ผู้เล่น = cursor.fetchone()

    embed = discord.Embed(color=0xff9ecd)
    embed.set_image(url=get_gif("start"))

    if ผู้เล่น:
        embed.title = f"⚠️ เธอลงทะเบียนแล้วนะคะ~"
        embed.description = f"หนูจำ {ctx.author.name} ได้อยู่แล้วค่ะ 🥺💕"
    else:
        cursor.execute("INSERT INTO players VALUES (?, ?, ?, ?, ?)",
                      (discord_id, ctx.author.name, 0, 0, "ชาวบ้าน"))
        conn.commit()
        embed.title = f"✅ ยินดีต้อนรับ {ctx.author.name} นะคะ~"
        embed.description = f"{random.choice(cute_start)}\nอาชีพเริ่มต้น: 🧑‍🌾 ชาวบ้าน"

    await ctx.send(embed=embed)

# ทำงานหาเงิน
@bot.command()
async def work(ctx):
    discord_id = str(ctx.author.id)
    cursor.execute("SELECT อาชีพ FROM players WHERE discord_id = ?", (discord_id,))
    ผู้เล่น = cursor.fetchone()

    embed = discord.Embed(color=0xffd700)

    if not ผู้เล่น:
        embed.title = "⚠️ เธอยังไม่ได้ลงทะเบียนเลยนะคะ~"
        embed.description = "พิมพ์ !start ก่อนนะคะ 🥺"
        embed.set_image(url=get_gif("error"))
        await ctx.send(embed=embed)
        return

    อาชีพ = ผู้เล่น[0]
    if อาชีพ in jobs:
        เงิน = random.randint(jobs[อาชีพ]["work_min"], jobs[อาชีพ]["work_max"])
    else:
        เงิน = random.randint(50, 200)

    exp = random.randint(10, 30)
    cursor.execute("UPDATE players SET เงิน = เงิน + ?, exp = exp + ? WHERE discord_id = ?",
                  (เงิน, exp, discord_id))
    conn.commit()

    embed.title = f"💰 {ctx.author.name} ทำงานแล้วนะคะ~"
    embed.description = f"ได้รับ **{เงิน:,} เหรียญ** และ **{exp} EXP** ค่ะ!\n{random.choice(cute_work)}"
    embed.set_image(url=get_gif("work"))
    await ctx.send(embed=embed)

# ดูยอดเงิน
@bot.command()
async def balance(ctx):
    discord_id = str(ctx.author.id)
    cursor.execute("SELECT เงิน, exp, อาชีพ FROM players WHERE discord_id = ?", (discord_id,))
    ผู้เล่น = cursor.fetchone()

    embed = discord.Embed(color=0x00ff99)

    if not ผู้เล่น:
        embed.title = "⚠️ เธอยังไม่ได้ลงทะเบียนเลยนะคะ~"
        embed.description = "พิมพ์ !start ก่อนนะคะ 🥺"
        embed.set_image(url=get_gif("error"))
        await ctx.send(embed=embed)
        return

    emoji = jobs[ผู้เล่น[2]]["emoji"] if ผู้เล่น[2] in jobs else "🧑‍🌾"
    embed.title = f"💵 กระเป๋าของ {ctx.author.name} ค่ะ~"
    embed.description = (
        f"💰 เงิน: **{ผู้เล่น[0]:,} เหรียญ**\n"
        f"⭐ EXP: **{ผู้เล่น[1]:,}**\n"
        f"{emoji} อาชีพ: **{ผู้เล่น[2]}**"
    )
    embed.set_image(url=get_gif("balance"))
    await ctx.send(embed=embed)

# โอนเงิน
@bot.command()
async def pay(ctx, member: discord.Member, amount: int):
    sender_id = str(ctx.author.id)
    receiver_id = str(member.id)

    embed = discord.Embed(color=0xff6699)

    if sender_id == receiver_id:
        embed.title = "⚠️ โอนให้ตัวเองไม่ได้นะคะ~"
        embed.description = "เธอตลกมากเลยค่ะ 555 🥺"
        embed.set_image(url=get_gif("error"))
        await ctx.send(embed=embed)
        return

    if amount <= 0:
        embed.title = "⚠️ จำนวนเงินต้องมากกว่า 0 นะคะ~"
        embed.set_image(url=get_gif("error"))
        await ctx.send(embed=embed)
        return

    cursor.execute("SELECT เงิน FROM players WHERE discord_id = ?", (sender_id,))
    sender = cursor.fetchone()

    if not sender:
        embed.title = "⚠️ เธอยังไม่ได้ลงทะเบียนเลยนะคะ~"
        embed.description = "พิมพ์ !start ก่อนนะคะ 🥺"
        embed.set_image(url=get_gif("error"))
        await ctx.send(embed=embed)
        return

    if sender[0] < amount:
        embed.title = "⚠️ เงินไม่พอนะคะ~"
        embed.description = f"เธอมีแค่ **{sender[0]:,} เหรียญ** ค่ะ 🥺"
        embed.set_image(url=get_gif("error"))
        await ctx.send(embed=embed)
        return

    cursor.execute("UPDATE players SET เงิน = เงิน - ? WHERE discord_id = ?", (amount, sender_id))
    cursor.execute("UPDATE players SET เงิน = เงิน + ? WHERE discord_id = ?", (amount, receiver_id))
    conn.commit()

    embed.title = f"💸 โอนเงินสำเร็จแล้วค่ะ~"
    embed.description = f"{ctx.author.name} โอน **{amount:,} เหรียญ** ให้ {member.name} แล้วนะคะ 💕"
    embed.set_image(url=get_gif("pay"))
    await ctx.send(embed=embed)

# อันดับ
@bot.command()
async def leaderboard(ctx):
    cursor.execute("SELECT ชื่อ, เงิน, อาชีพ FROM players ORDER BY เงิน DESC LIMIT 10")
    players = cursor.fetchall()

    embed = discord.Embed(
        title="✨💖 อันดับคนรวยแห่ง CoinBot 💖✨",
        color=0xff85c1
    )

    if not players:
        embed.description = "💔 ยังไม่มีผู้เล่นเลยค่ะ~\nชวนเพื่อนมาเล่นด้วยกันนะคะ หนูรออยู่นะ 🥺💕"
        embed.set_image(url=get_gif("error"))
        await ctx.send(embed=embed)
        return

    cute_lb = [
        "สู้ๆ นะคะทุกคน หนูเชียร์อยู่นะ~ 💕",
        "ใครจะได้อันดับ 1 ต่อไปนะคะ~ 🥺✨",
        "ขยันๆ หน่อยนะคะ เดี๋ยวก็ได้อันดับ 1 ค่ะ 🌸",
    ]

    msg = "```\n"
    for i, p in enumerate(players, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"  {i}."
        emoji = jobs[p[2]]["emoji"] if p[2] in jobs else "🧑‍🌾"
        msg += f"{medal} {p[0]:<15} 💰 {p[1]:>10,} เหรียญ  {emoji} {p[2]}\n"
    msg += "```"

    embed.description = msg + f"\n{random.choice(cute_lb)}"
    embed.set_footer(text="CoinBot 💖 | อัปเดตทุกครั้งที่พิมพ์คำสั่ง~")
    embed.set_image(url=get_gif("leaderboard"))
    await ctx.send(embed=embed)

# ดูรายการอาชีพ
@bot.command()
async def joblist(ctx):
    embed = discord.Embed(color=0x9b59b6)
    embed.title = "📋 รายการอาชีพทั้งหมดค่ะ~"

    msg = "🧑‍🌾 ชาวบ้าน = เริ่มต้น (ฟรี) | หาเงิน: 50-200\n"
    for ชื่อ, ข้อมูล in jobs.items():
        msg += f"{ข้อมูล['emoji']} {ชื่อ} = {ข้อมูล['ราคา']:,} เหรียญ | หาเงิน: {ข้อมูล['work_min']}-{ข้อมูล['work_max']}\n"
    msg += "\nพิมพ์ `!buyjob ชื่ออาชีพ` เพื่อซื้อนะคะ 💕"

    embed.description = msg
    embed.set_image(url=get_gif("joblist"))
    await ctx.send(embed=embed)

# ซื้ออาชีพ
@bot.command()
async def buyjob(ctx, *, ชื่ออาชีพ: str):
    discord_id = str(ctx.author.id)

    embed = discord.Embed(color=0x00bfff)

    if ชื่ออาชีพ not in jobs:
        embed.title = "⚠️ ไม่มีอาชีพนี้นะคะ~"
        embed.description = "พิมพ์ !joblist ดูรายการได้เลยค่ะ 🥺"
        embed.set_image(url=get_gif("error"))
        await ctx.send(embed=embed)
        return

    cursor.execute("SELECT เงิน, อาชีพ FROM players WHERE discord_id = ?", (discord_id,))
    ผู้เล่น = cursor.fetchone()

    if not ผู้เล่น:
        embed.title = "⚠️ เธอยังไม่ได้ลงทะเบียนเลยนะคะ~"
        embed.description = "พิมพ์ !start ก่อนนะคะ 🥺"
        embed.set_image(url=get_gif("error"))
        await ctx.send(embed=embed)
        return

    if ผู้เล่น[1] == ชื่ออาชีพ:
        embed.title = f"⚠️ เธอเป็น {ชื่ออาชีพ} อยู่แล้วนะคะ~"
        embed.description = "ลองอาชีพอื่นดูนะคะ 💕"
        embed.set_image(url=get_gif("error"))
        await ctx.send(embed=embed)
        return

    ราคา = jobs[ชื่ออาชีพ]["ราคา"]

    if ผู้เล่น[0] < ราคา:
        embed.title = "⚠️ เงินไม่พอนะคะ~"
        embed.description = f"ต้องการ **{ราคา:,} เหรียญ** แต่มีแค่ **{ผู้เล่น[0]:,} เหรียญ** ค่ะ 🥺\nสู้ๆ นะคะ!"
        embed.set_image(url=get_gif("error"))
        await ctx.send(embed=embed)
        return

    cursor.execute("UPDATE players SET เงิน = เงิน - ?, อาชีพ = ? WHERE discord_id = ?",
                  (ราคา, ชื่ออาชีพ, discord_id))
    conn.commit()

    emoji = jobs[ชื่ออาชีพ]["emoji"]
    embed.title = f"{emoji} เปลี่ยนอาชีพสำเร็จแล้วค่ะ~"
    embed.description = f"{ctx.author.name} เป็น **{ชื่ออาชีพ}** แล้วนะคะ!\n{random.choice(cute_buy)}"
    embed.set_image(url=get_gif("buyjob"))
    await ctx.send(embed=embed)

# คำสั่งทั้งหมด
@bot.command(name="help", aliases=["ช่วยเหลือ"])
async def help_command(ctx):
    cute_greet = [
        f"หนูยินดีช่วยเลยค่ะ {ctx.author.name}~ 💕",
        f"มีอะไรให้หนูช่วยมั้ยคะ {ctx.author.name}~ 🥺",
        f"หนูอยู่ตรงนี้เสมอนะคะ {ctx.author.name} 💖",
    ]

    embed = discord.Embed(
        title="✨💖 CoinBot คำสั่งทั้งหมดค่ะ~ 💖✨",
        description=random.choice(cute_greet),
        color=0xff85c1
    )

    embed.add_field(
        name="👤 ระบบผู้เล่น",
        value=(
            "🌸 `!start` — ลงทะเบียนเริ่มเล่นค่ะ~\n"
            "💵 `!balance` — ดูเงิน EXP และอาชีพค่ะ~"
        ),
        inline=False
    )

    embed.add_field(
        name="💰 ระบบเงิน",
        value=(
            "⚒️ `!work` — ทำงานหาเงินนะคะ~\n"
            "💸 `!pay @คน จำนวน` — โอนเงินให้เพื่อนค่ะ~"
        ),
        inline=False
    )

    embed.add_field(
        name="⚔️ ระบบอาชีพ",
        value=(
            "📋 `!joblist` — ดูรายการอาชีพทั้งหมดค่ะ~\n"
            "🛒 `!buyjob ชื่ออาชีพ` — ซื้ออาชีพใหม่นะคะ~"
        ),
        inline=False
    )

    embed.add_field(
        name="📊 ระบบอันดับ",
        value="🏆 `!leaderboard` — ดู Top 10 คนรวยสุดค่ะ~",
        inline=False
    )

    embed.set_footer(text="CoinBot 💖 | พัฒนาโดย ไก่ POP 🐔 | หนูรักทุกคนนะคะ~ 🌸")
    embed.set_thumbnail(url="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExMmp4dHl3b2NjbWZ5NG1oOXgzcG5hbnh1czVmaWh5Mml0bXIwN2QxdSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jleNxE9BsJVO8/giphy.gif")

    await ctx.send(embed=embed)

bot.run(os.environ.get("TOKEN"))