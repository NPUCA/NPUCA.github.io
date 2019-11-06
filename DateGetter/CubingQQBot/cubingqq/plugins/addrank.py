import os
import sys
import pickle
sys.path.append(os.path.abspath("../"))
from Spider import *
from DataBase import *

from nonebot import on_command, CommandSession, on_natural_language, NLPSession, IntentCommand

questioned = False

@on_command('addrank', only_to_me=True, permission=0xF000)
async def addrank(session: CommandSession):
    global questioned
    # print('fuc called')
    people = session.get('people', prompt='你想加入MZR排名嘛？请回复-addrank [WCA id/name]')

    # wca_performance = await get_wca_performance(people)
    wca_id_num = await get_wca_id_num(people)
    if wca_id_num == 1:
        wca_performance = await get_wca_performance(people)
        answer = ""
        if not questioned:
            await session.send("这是你吗？\n" + wca_performance)
            questioned = True
        else:
            questioned = False
        answer = session.get('answer', prompt='回复y/n')
        print("ans: ", answer)
        if answer in ['y', 'Y']:
            await session.send("已加入数据库")
            # print(wca_performance.split('\n'))
            AddId(wca_performance.split('\n'), "../")
        else:
            await session.send("你吼那么大声干嘛")
    else:
        wca_performance = await get_wca_performance(people)
        await session.send("请重新输入-addrank [WCA id/name]\n" + wca_performance)

@addrank.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['people'] = stripped_arg
        return
    else:
        if stripped_arg:
            session.state['answer'] = stripped_arg
        return 
    
    if not stripped_arg:
        session.pause('')

    session.state[session.current_key] = stripped_arg

async def get_wca_performance(people: str) -> str:
    # print(f'{people}')
    name = f'{people}'
    msg = GenMessage(name)
    return msg
async def get_wca_id_num(people: str) -> int:
    name = f'{people}'
    print(name)
    cand_num, cands = GetCandidate(name)
    print(cand_num)
    return cand_num

# @on_command()