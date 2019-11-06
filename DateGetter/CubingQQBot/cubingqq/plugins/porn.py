import os
import sys
import pickle
import random
sys.path.append(os.path.abspath("../"))
from Spider import *
# from GetPorn import *

from nonebot import on_command, CommandSession, on_natural_language,NLPSession, IntentCommand

async def get_porn()->str:
    porn_html = GetHtml("https://8zt.cc/")
    porn_soup = BS(porn_html, 'html.parser')

    porn = porn_soup.find_all('span')[0].string.strip()
    print(porn)
    return porn

@on_command('porn', only_to_me=False)
async def wca(session: CommandSession):
    porn = await get_porn()
    await session.send(porn)

