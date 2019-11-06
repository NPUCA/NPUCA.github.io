import re
import time
import pickle
from Spider import *

def DevideTemp():
    html_file = open("../fmzr_temp.html", encoding='utf-8')
    html = "".join("".join(html_file.readlines()).split('\n'))
    
    html_parts = re.split("<table.*?.</table>", html)
    table = re.findall("<table.*?.</table>", html)
    return html_parts, table[0]

def Rank2Html(ranks, raw2perform, event):
    # padding
    for i in range(2):
        while len(ranks[i]) < 3:
            ranks[i].append('')

    _, table_temp = DevideTemp()
    for i in range(3):
        table_temp = table_temp.replace("SIG%d_NAME"%(i+1),
            '<a href="https://cubingchina.com/results/person/%s">%s</a>'%(
                ranks[0][i].split(',')[0], ranks[0][i].split(',')[-1]
            )
        )
        try:
            table_temp = table_temp.replace("SIG%d_PERF"%(i+1),
                raw2perform[ranks[0][i]][event][0]
            )
        except:
            table_temp = table_temp.replace("SIG%d_PERF"%(i+1),
                ''
            )
        table_temp = table_temp.replace("AVG%d_NAME"%(i+1),
            '<a href="https://cubingchina.com/results/person/%s">%s</a>'%(
                ranks[1][i].split(',')[0], ranks[1][i].split(',')[-1]
            )
        )
        try:
            table_temp = table_temp.replace("AVG%d_PERF"%(i+1),
                raw2perform[ranks[1][i]][event][1]
            )
        except:
            table_temp = table_temp.replace("AVG%d_PERF"%(i+1),
                ''
            )
    if event == 'comp_solve':
        table_temp = table_temp.replace('单次', '参赛次数')
        table_temp = table_temp.replace('平均', '复原次数')
    return table_temp

if __name__ == "__main__":
    # get cubers
    f = open("wca_id.csv", encoding='utf-8')
    rraw_list = f.readlines()
    rraw_list = [i[:-1] for i in rraw_list]

    raw_list = []
    for i in rraw_list:
        _, c = GetCandidate(i.split(',')[0])
        if c[0][-1] == '女':
            raw_list.append(i)

    name_list = [i.split(',')[1] for i in raw_list]
    id_list = [i.split(',')[0] for i in raw_list] # which also means the links
    # get Performs
    perform_list = []
    for i in id_list:
        print(i)
        perform_list.append(GetPerform(i))
    raw2perform = dict(zip(raw_list, perform_list))

    print(raw2perform)
    eng2chn = {
        '333':'三阶',
        '222':'二阶',
        '444':'四阶',
        '555':'五阶',
        '666':'六阶',
        '777':'七阶',
        '333bf':'三盲',
        '333fm':'最少步',
        '333oh':'单手',
        '333ft':'脚拧',
        'clock':'魔表',
        'minx':'五魔方',
        'pyram':'金字塔',
        'skewb':'斜转',
        'sq1':'SQ1',
        '444bf':'四盲',
        '555bf':'五盲',
        '333mbf':'多盲',
        'roa':'全项目',
        'comp_solve':'参赛次数|复原次数',
    } 

    html_parts, _ = DevideTemp()
    for event in eng2chn:
        ranks = []
        for mode in range(2):
            print(event, mode)
            lambs = []
            for lamb in raw_list:
                if event in raw2perform[lamb] and raw2perform[lamb][event][mode] != '':
                    lambs.append(lamb)
            print(lambs)

            def sort_key(lamb):
                try:
                    return float(raw2perform[lamb][event][mode])
                except:
                    return float(raw2perform[lamb][event][mode].split(':')[0])*60.0 + float(raw2perform[lamb][event][mode].split(':')[1])

            # sort part
            if event != 'comp_solve':
                ranked_lambs = sorted(lambs, key=sort_key)
            else:
                ranked_lambs = sorted(lambs, key=sort_key, reverse=True)
            ranks.append(ranked_lambs[:3])
            print(ranked_lambs)
            print()
        t_table = Rank2Html(ranks, raw2perform, event)
        t_table = "<hr><nav><h2>%s</h2></nav>"%eng2chn[event] + t_table
        html_parts.insert(-1, t_table)
    
    f = open("../fmzr.html", encoding='utf-8', mode='w') 
    f.write("".join(html_parts))
    