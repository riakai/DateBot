import datetime
import os
import sys

from apscheduler.triggers.interval import IntervalTrigger
from discord.ext import commands
from discordbot.bot_utils import checks
from sqlitedict import SqliteDict


class Timer:
    def __init__(self, bot_obj):
        self.bot = bot_obj
        self.time_dict = SqliteDict('./time.db', autocommit=True)
        if self.time_dict["start_date"]:
            self.bot.scheduler.add_job(func=self.update_time,
                                       trigger=IntervalTrigger(seconds=10800, start_date=self.time_dict["first_time"]),
                                       args=[self.time_dict["start_date"], self.time_dict["made_time"],
                                             self.time_dict["channel"]])

    def update_time(self, start, made, channel):
        time_diff = datetime.datetime.now() - start
        t_cycle = time_diff.total_seconds() // 24000 + made
        # A sweep is 100 stages, a stage is 10 cycles, and a cycle is 10800 seconds
        t_stage, cycle = (t_cycle // 10, t_cycle % 10)
        t_sweep, stage = (t_stage // 100, t_stage % 100)

        self.bot.send_message(channel, content=f"{t_sweep}:{stage}:{cycle}")

    @checks.is_owner()
    @commands.command(pass_context=True)
    async def set_time(self, ctx):
        '''Sets made-up time. Takes in total cycles'''
        await self.bot.send_typing(ctx.message.channel)
        try:
            self.time_dict["start_date"] = datetime.datetime.now()
            self.time_dict["made_time"] = int(ctx.message.content.split()[1])
            self.time_dict["channel"] = ctx.message.channel
            self.bot.scheduler.remove_all_jobs()
            self.bot.scheduler.add_job(func=self.update_time,
                                       trigger=IntervalTrigger(seconds=10800, start_date=self.time_dict["first_time"]),
                                       args=[self.time_dict["start_date"], self.time_dict["made_time"],
                                             self.time_dict["channel"]])
            await self.bot.responses.success()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            await self.bot.responses.failure(
                    title=f"At L{exc_tb.tb_lineno} file {os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]}",
                    message=repr(e))
            raise e
        # finally:
        #     self.bot.scheduler.add_job(func=self.bot.delete_message,
        #                                trigger=DateTrigger(datetime.datetime.now() + datetime.timedelta(seconds=5),
        #                                                    timezone=pytz.utc),
        #                                args=[msg])

    @checks.is_owner()
    @commands.command(pass_context=True)
    async def get_time(self, ctx):
        await self.bot.send_typing(ctx.message.channel)
        try:
            self.update_time(self.time_dict["start_date"], self.time_dict["made_time"], ctx.message.channel)
            await self.bot.responses.success()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            await self.bot.responses.failure(
                    title=f"At L{exc_tb.tb_lineno} file {os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]}",
                    message=repr(e))
            raise e


def setup(bot):
    bot.add_cog(Timer(bot))
