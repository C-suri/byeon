import discord
from discord.ext import commands
import datetime
import pytz
import os  # os 모듈을 사용하여 환경 변수를 가져옵니다.

intents = discord.Intents.default()
intents.messages = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

attendance_dict = {}
log_channel_id = 1292532530511089774  # 여기에 채팅 채널 ID를 입력하세요

def format_time(dt):
    kst = pytz.timezone('Asia/Seoul')
    dt_kst = dt.astimezone(kst)
    return dt_kst.strftime("%Y년 %m월 %d일 %H시 %M분")

def calculate_total_work_time(times):
    total_duration = datetime.timedelta()
    for i in range(len(times["출근"])):
        if i < len(times["퇴근"]):
            check_in_time = times["출근"][i]
            check_out_time = times["퇴근"][i]
            total_duration += check_out_time - check_in_time
    return total_duration

def get_month_work_stats(times, year, month):
    total_duration = datetime.timedelta()
    work_days = 0

    for i in range(len(times["출근"])):
        check_in_time = times["출근"][i].astimezone(pytz.timezone('Asia/Seoul'))

        if check_in_time.year == year and check_in_time.month == month:
            work_days += 1

            if i < len(times["퇴근"]):
                check_out_time = times["퇴근"][i].astimezone(pytz.timezone('Asia/Seoul'))
                total_duration += check_out_time - check_in_time

    hours, remainder = divmod(total_duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return work_days, f"{hours}시간 {minutes}분"

@bot.event
async def on_voice_state_update(member, before, after):
    current_time = datetime.datetime.now(pytz.utc)
    formatted_time = format_time(current_time)
    guild_name = member.guild.name

    color = member.color if member.color else discord.Color.default()
    embed = discord.Embed(color=color)

    bold_display_name = f"**{member.display_name}**"
    embed.set_author(name=bold_display_name)

    if before.channel is None and after.channel is not None:  # 입장
        if member.display_name not in attendance_dict:
            attendance_dict[member.display_name] = {"출근": [], "퇴근": []}

        if not attendance_dict[member.display_name]["출근"]:
            attendance_dict[member.display_name]["출근"].append(current_time)
            embed.description = f"{guild_name} 서버의 {bold_display_name}님이 **출근**했습니다. 시간: **{formatted_time}**"
            log_channel = bot.get_channel(log_channel_id)
            await log_channel.send(embed=embed)

    elif before.channel is not None and after.channel is None:  # 퇴장
        if member.display_name in attendance_dict and attendance_dict[member.display_name]["출근"]:
            if attendance_dict[member.display_name]["퇴근"]:
                last_checkout_time = attendance_dict[member.display_name]["퇴근"][-1]
                if not is_same_day(last_checkout_time, current_time):
                    attendance_dict[member.display_name]["퇴근"].append(current_time)
                else:
                    attendance_dict[member.display_name]["퇴근"][-1] = current_time
            else:
                attendance_dict[member.display_name]["퇴근"].append(current_time)

            total_work_duration = calculate_total_work_time(attendance_dict[member.display_name])
            hours, remainder = divmod(total_work_duration.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            total_work_duration_str = f"{hours}시간 {minutes}분"

            embed.description = f"{guild_name} 서버의 {bold_display_name}님이 **퇴근**했습니다. 시간: **{formatted_time}**, 오늘 총 근무 시간: **{total_work_duration_str}**"
            log_channel = bot.get_channel(log_channel_id)
            await log_channel.send(embed=embed)
        else:
            embed.description = f"{guild_name} 서버의 {bold_display_name}님은 아직 출근 기록이 없습니다."
            log_channel = bot.get_channel(log_channel_id)
            await log_channel.send(embed=embed)

@bot.command(name="출근기록")
async def show_attendance(ctx, *, date: str):
    kst = pytz.timezone('Asia/Seoul')
    current_time = datetime.datetime.now(kst)

    try:
        year, month = map(int, date.split("년")[0]), int(date.split("년")[1].split("월")[0])
    except (ValueError, IndexError):
        await ctx.send("형식이 잘못되었습니다. '2024년 9월' 형식으로 입력해주세요.")
        return

    if attendance_dict:
        attendance_log = ""
        for user, times in attendance_dict.items():
            work_days, total_work_duration_str = get_month_work_stats(times, year, month)
            attendance_log += f"{user}님의 {month}월 출근 횟수: **{work_days}번**, 총 근무 시간: **{total_work_duration_str}**\n"
        await ctx.send(f"{year}년 {month}월 출근 기록:\n{attendance_log}")
    else:
        await ctx.send("아직 출근 기록이 없습니다.")

# Flask 서버를 이용한 keep_alive 코드 추가
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Flask 서버 실행
keep_alive()

# 봇 실행
bot.run(os.getenv("DISCORD_TOKEN"))  # 환경 변수에서 토큰 가져오기
