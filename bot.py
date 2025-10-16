import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, Any, List, Tuple

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

TRACKS_LIST = {
    "Mario Bros. Circuit":"MBC",
    "Crown City":"CC",
    "Whistlestop Summit":"WS",
    "DK Spaceport":"DKS",
    "Desert Hills (DS)":"rDH",
    "Shy Guy Bazaar (3DS)":"rSGB",
    "Wario Stadium (N64)":"rWS",
    "Airship Fortress (DS)":"rAF",
    "DK Pass (DS)":"rDKP",
    "Starview Peak":"SP",
    "Sky High Sundae (Tour/NSW)":"rSHS",
    "Wario Shipyard (3DS)":"rWSh",
    "Koopa Troopa Beach (SNES)":"rKTB",
    "Faraway Oasis":"FO",
    "Peach Stadium":"PS",
    "Peach Beach (GCN)":"rPB",
    "Salty Salty Speedway":"SSS",
    "Dino Dino Jungle (GCN)":"rDDJ",
    "Great Question Block Ruins":"GBR",
    "Cheep Cheep Falls":"CCF",
    "Dandelion Depths":"DD",
    "Boo Cinema":"BCi",
    "Dry Bones Burnout":"DBB",
    "Moo Moo Meadows (Wii)":"rMMM",
    "Choco Mountain (N64)":"rCM",
    "Toad's Factory (Wii)":"rTF",
    "Bowser's Castle":"BC",
    "Acorn Heights":"AH",
    "Mario Circuit (SNES)":"rMC",
    "Rainbow Road":"RR"
}

wrs = {
    "MBC": "1:48.446",
    "CC": "2:04.448",
    "WS": "1:44.686",
    "DKS": "1:29.740",
    "rDH": "1:32.336",
    "rSGB": "1:51.242",
    "rWS": "2:01.088",
    "rAF": "1:54.513",
    "rDKP": "2:00.044",
    "SP": "2:12.255",
    "rSHS": "1:52.985",
    "rWSh": "2:16.968",
    "rKTB": "1:27.650",
    "FO": "1:56.974",
    "PS": "2:15.419",
    "rPB": "1:40.796",
    "SSS": "1:56.471",
    "rDDJ": "1:44.327",
    "GBR": "2:02.490",
    "CCF": "1:55.546",
    "DD": "2:19.228",
    "BCi": "2:04.664",
    "DBB": "2:06.634",
    "rMMM": "1:53.944",
    "rCM": "2:01.742",
    "rTF": "1:51.336",
    "BC": "2:11.302",
    "AH": "1:57.957",
    "rMC": "1:03.766",
    "RR": "3:55.127"
}

thumbnail_tracks = {
    "MBC": "https://mario.wiki.gallery/images/c/ca/MKWorld_Icon_Mario_Bros_Circuit.png",
    "CC": "https://mario.wiki.gallery/images/e/e8/MKWorld_Icon_Crown_City.png",
    "WS": "https://mario.wiki.gallery/images/9/98/MKWorld_Icon_Whistlestop_Summit.png",
    "DKS": "https://mario.wiki.gallery/images/9/99/MKWorld_Icon_DK_Spaceport.png",
    "rDH": "https://mario.wiki.gallery/images/3/34/MKWorld_Icon_Desert_Hills.png",
    "rSGB": "https://mario.wiki.gallery/images/0/03/MKWorld_Icon_Shy_Guy_Bazaar.png",
    "rWS": "https://mario.wiki.gallery/images/f/f6/MKWorld_Icon_Wario_Stadium.png",
    "rAF": "https://mario.wiki.gallery/images/1/1f/MKWorld_Icon_Airship_Fortress.png",
    "rDKP": "https://mario.wiki.gallery/images/7/71/MKWorld_Icon_DK_Pass.png",
    "SP": "https://mario.wiki.gallery/images/a/a6/MKWorld_Icon_Starview_Peak.png",
    "rSHS": "https://mario.wiki.gallery/images/7/7e/MKWorld_Icon_Sky-High_Sundae.png",
    "rWSh": "https://mario.wiki.gallery/images/f/fc/MKWorld_Icon_Wario_Shipyard.png",
    "rKTB": "https://mario.wiki.gallery/images/3/31/MKWorld_Icon_Koopa_Troopa_Beach.png",
    "FO": "https://mario.wiki.gallery/images/f/f6/MKWorld_Icon_Faraway_Oasis.png",
    "PS": "https://mario.wiki.gallery/images/f/fd/MKWorld_Icon_Peach_Stadium.png",
    "rPB": "https://mario.wiki.gallery/images/1/1a/MKWorld_Icon_Peach_Beach.png",
    "SSS": "https://mario.wiki.gallery/images/e/e0/MKWorld_Icon_Salty_Salty_Speedway.png",
    "rDDJ": "https://mario.wiki.gallery/images/5/51/MKWorld_Icon_Dino_Dino_Jungle.png",
    "GBR": "https://mario.wiki.gallery/images/8/83/MKWorld_Icon_Great_Question_Block_Ruins.png",
    "CCF": "https://mario.wiki.gallery/images/0/01/MKWorld_Icon_Cheep_Cheep_Falls.png",
    "DD": "https://mario.wiki.gallery/images/3/33/MKWorld_Icon_Dandelion_Depths.png",
    "BCi": "https://mario.wiki.gallery/images/a/a8/MKWorld_Icon_Boo_Cinema.png",
    "DBB": "https://mario.wiki.gallery/images/f/f7/MKWorld_Icon_Dry_Bones_Burnout.png",
    "rMMM": "https://mario.wiki.gallery/images/e/eb/MKWorld_Icon_Moo_Moo_Meadows.png",
    "rCM": "https://mario.wiki.gallery/images/1/16/MKWorld_Icon_Choco_Mountain.png",
    "rTF": "https://mario.wiki.gallery/images/2/2f/MKWorld_Icon_Toads_Factory.png",
    "BC": "https://mario.wiki.gallery/images/c/cc/MKWorld_Icon_Bowsers_Castle.png",
    "AH": "https://mario.wiki.gallery/images/2/2a/MKWorld_Icon_Acorn_Heights.png",
    "rMC": "https://mario.wiki.gallery/images/3/31/MKWorld_Icon_Mario_Circuit.png",
    "RR": "https://mario.wiki.gallery/images/2/25/MKWorld_Icon_Rainbow_Road.png"
}

cups = [
    "Flower Cup",
    "Star Cup",
    "Shell Cup",
    "Banana Cup",
    "Leaf Cup",
    "Lightning Cup",
    "Special Cup"
]

DATA_FILE = "times.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def parse_time(time_str: str) -> int:
    """Convert 'M:SS.mmm' or 'SS.mmm' to milliseconds."""
    try:
        if ":" in time_str:
            minutes, rest = time_str.split(":")
            seconds, millis = rest.split(".")
        else:
            minutes = 0
            seconds, millis = time_str.split(".")

        total_score_ms = (int(minutes) * 60 + int(seconds)) * 1000 + int(millis)
        return total_score_ms
    except ValueError:
        raise ValueError("Invalid time format. Use M:SS.mmm or SS.mmm")

def format_time(ms: int) -> str:
    """Convert milliseconds back to 'M:SS.mmm'."""
    if ms < 3599999:
        minutes = ms // 60000
        seconds = (ms % 60000) // 1000
        millis = ms % 1000
        return f"{minutes}:{seconds:02d}.{millis:03d}"
    else:
        hours = ms // 3600000
        minutes = (ms % 3600000) // 60000
        seconds = (ms % 60000) // 1000
        millis = ms % 1000
        return f"{hours}:{minutes:02d}:{seconds:02d}.{millis:03d}"

color_map = {
    "WR": discord.Color.from_rgb(138, 43, 226),
    "X": discord.Color.from_rgb(153, 50, 204),
    "S+": discord.Color.from_rgb(75, 0, 130),
    "S": discord.Color.from_rgb(65, 105, 225),
    "S-": discord.Color.from_rgb(30, 144, 255),
    "A+": discord.Color.from_rgb(0, 191, 255),
    "A": discord.Color.from_rgb(102, 205, 170),
    "A-": discord.Color.from_rgb(50, 205, 50),
    "B+": discord.Color.from_rgb(173, 255, 47),
    "B": discord.Color.from_rgb(255, 215, 0),
    "B-": discord.Color.from_rgb(240, 230, 140),
    "C+": discord.Color.from_rgb(255, 165, 0),
    "C": discord.Color.from_rgb(255, 140, 0),
    "C-": discord.Color.from_rgb(255, 99, 71),
    "D+": discord.Color.from_rgb(255, 69, 0),
    "D": discord.Color.from_rgb(220, 20, 60),
}

RANKS_INDV = {
    0: "WR",
    0.5: "X",
    1: "S+",
    1.5: "S",
    2: "S-",
    2.75: "A+",
    3.5: "A",
    4.25: "A-",
    5: "B+",
    6: "B",
    7: "B-",
    8.5: "C+",
    10: "C",
    12.5: "C-",
    15: "D+",
}

RANKS_OVR = {
    0: "WR",
    0.75: "X",
    1.5: "S+",
    2.25: "S",
    3: "S-",
    4: "A+",
    5: "A",
    6: "A-",
    8: "B+",
    10: "B",
    12: "B-",
    15: "C+",
    20: "C",
    25: "C-",
    30: "D+",
}

def get_rank(percentage: float):
    for limit in RANKS_INDV:
        if percentage <= limit:
            return RANKS_INDV.get(limit)
    return "D"

def get_rank_ovr(percentage: float):
    for limit in RANKS_OVR:
        if percentage <= limit:
            return RANKS_OVR.get(limit)
    return "D"

async def track_autocomplete(interaction: discord.Interaction, current: str):
    matches = [t for t in TRACKS_LIST if current.lower() in t.lower()]
    return [
        discord.app_commands.Choice(name=t, value=t)
        for t in matches[:25]
    ]

@client.event
async def on_ready():
    await tree.sync()
    print(f"logged as {client.user}")

@tree.command(name="hello_slash", description="Slash command for hello")
async def hello(interaction: discord.Interaction):
    user = interaction.user
    await interaction.response.send_message(f"Hello {user.mention}!")

@tree.command(name="wr", description="Display wr for a track")
@discord.app_commands.describe(track="The abreviation of a track")
@discord.app_commands.autocomplete(track=track_autocomplete)
async def wr(interaction: discord.Interaction, track: str = None):
    
    if track:
        embed_output = discord.Embed(
            title=f"World Record Time",
            description=f"**{TRACKS_LIST.get(track)}** — {wrs.get(TRACKS_LIST.get(track))}",
            color=discord.Color.from_rgb(231,181,69)
        )
        embed_output.set_thumbnail(url=thumbnail_tracks[TRACKS_LIST.get(track)])
        await interaction.response.send_message(embed=embed_output)
    else:
        
        track_list = "__Mushroom Cup__\n"
        cup_counter = 0
        for i in wrs:
            track_list += f"**{i}** - `{wrs.get(i)}`\n"
            if i in ["DKS", "rAF", "rWSh", "PS", "GBR", "DBB", "BC"]:
                track_list += f"__{cups[cup_counter]}__\n"
                cup_counter += 1

        embed_output = discord.Embed(
            title=f"World Record Times",
            description=track_list,
            color=discord.Color.from_rgb(231,181,69)
        )
        await interaction.response.send_message(embed=embed_output)

@tree.command(name="save", description="Save your time for a track")
@discord.app_commands.describe(track="The abreviation of a track", time="Your time (e.g. 1:23.456)")
@discord.app_commands.autocomplete(track=track_autocomplete)
async def save(interaction: discord.Interaction, track: str, time: str):
    user_id = str(interaction.user.id)
    data = load_data()
    time = parse_time(time)

    if user_id not in data:
        data[user_id] = {}
    
    data[user_id][TRACKS_LIST.get(track)] = time
    save_data(data)

    embed_output = discord.Embed(
        title="Time Saved",
        description=f"{interaction.user.display_name} saved `{format_time(time)}` on **{track}**",
        color=discord.Color.from_rgb(231,181,69)
    )
    embed_output.set_thumbnail(url=thumbnail_tracks[TRACKS_LIST.get(track)])
    await interaction.response.send_message(embed=embed_output)

@tree.command(name="score", description="Show your score for a track or in general")
@discord.app_commands.describe(track="The abreviation of a track")
@discord.app_commands.autocomplete(track=track_autocomplete)
async def score(interaction: discord.Interaction, track: str = None):
    user_id = str(interaction.user.id)
    data = load_data()
    if track:
        if user_id in data and TRACKS_LIST.get(track) in data[user_id]:
            time = data[user_id][TRACKS_LIST.get(track)]
            diff = time - parse_time(wrs.get(TRACKS_LIST.get(track)))
            track_score = (time/parse_time(wrs.get(TRACKS_LIST.get(track))) - 1) * 100

            embed_output = discord.Embed(
                title=f"{interaction.user.display_name} Score",
                description=f"**{track}**: `{format_time(time)}` - Score: `{round(track_score, 3)}`, __**{get_rank(track_score)}**__",
                color=color_map.get(get_rank(track_score), discord.Color.light_gray())
            )
            embed_output.set_thumbnail(url=thumbnail_tracks[TRACKS_LIST.get(track)])
            await interaction.response.send_message(embed=embed_output)
        else:
            await interaction.response.send_message(
                f"You don't have a saved time for **{track}** yet."
            )
    else:
        output = "__Mushroom Cup__\n"
        total_score = 0
        counter = 0
        total_time = 0
        cup_counter = 0
        if user_id in data:
            for i in wrs:
                if i in ["rDH", "rDKP", "rKTB", "rPB", "CCF", "rMMM", "AH"]: #To trzeba zmienić, będzie słabo działać gdy uzyt. nie będzie mieć wszędzie czasów zapisanych
                    output += f"__{cups[cup_counter]}__\n"
                    cup_counter += 1
                if i in data[user_id]:
                    time = data[user_id][i]
                    diff = time - parse_time(wrs.get(i))
                    track_score = (time/parse_time(wrs.get(i)) - 1) * 100
                    output += f"**{i}**: `{format_time(time)}`\n ^ Score: `{round(track_score, 3)}`, __**{get_rank(track_score)}**__\n"
                    counter += 1
                    total_score += track_score
                    total_time += time
                    
            if counter == 30:
                output += f"\n**Total Time**: `{format_time(total_time)}`\n**Overall Score**: `{round(total_score/counter, 3)}`, __**{get_rank_ovr(total_score/counter)}**__"

            embed_output = discord.Embed(
                    title=f"{interaction.user.display_name} Score",
                    description=output,
                    color=color_map.get(get_rank_ovr(total_score/counter), discord.Color.light_gray())
                )
            embed_output.set_thumbnail(url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed_output)
        else:
            await interaction.response.send_message("You don't have any times saved yet.")

client.run(token)