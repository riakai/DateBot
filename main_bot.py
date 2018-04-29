import discord.py
import logging
import logging.config
import os
import pathlib

import discordbot.bot_utils
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from colorama import init


class ColorFormatter(logging.Formatter):
    from colorama import Fore, Back, Style
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    COLORS = {
        'WARNING' : (Style.DIM + Fore.BLACK, Back.YELLOW),
        'INFO'    : (Style.BRIGHT + Fore.WHITE, Back.CYAN),
        'DEBUG'   : (Style.NORMAL + Fore.WHITE, Back.BLUE),
        'CRITICAL': (Style.DIM + Fore.BLACK, Back.YELLOW),
        'ERROR'   : (Style.BRIGHT + Fore.WHITE, Back.RED),
    }

    CCOLORS = {
        "BLACK"  : BLACK,
        "RED"    : RED,
        "GREEN"  : GREEN,
        "YELLOW" : YELLOW,
        "BLUE"   : BLUE,
        "MAGENTA": MAGENTA,
        "CYAN"   : CYAN,
        "WHITE"  : WHITE,
    }

    COLOR_SEQ = "\033[1;%dm"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record):
        levelname = record.levelname
        color = self.COLORS[levelname][0]
        bg_color = self.COLORS[levelname][1]
        message = logging.Formatter.format(self, record)
        message = message.replace("$RESET", self.Style.RESET_ALL) \
            .replace("$BRIGHT", self.Style.BRIGHT) \
            .replace("$COLOR", color) \
            .replace("$BGCOLOR", bg_color)
        for k, v in self.CCOLORS.items():
            message = message.replace("$" + k, self.COLOR_SEQ % (v + 30)) \
                .replace("$BG" + k, self.COLOR_SEQ % (v + 40))
        return message + self.Style.RESET_ALL


client = discordbot.DiscordBot()
client.scheduler = AsyncIOScheduler(event_loop=client.loop, timezone=pytz.utc)

# Start
if __name__ == '__main__':
    if not pathlib.Path("./c_log/").exists():
        os.mkdir("./c_log/")
    init()
    logging.ColorFormatter = ColorFormatter
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger(__name__)

    client.scheduler.start()
    client.load_cogs()
    client.run()
