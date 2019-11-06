import re
import time
import pandas as pd
from Spider import *

def DevideTemp():
    html_file = open("../mzr_plus_temp.html", encoding='utf-8')
    html = "".join("".join(html_file.readlines()).split('\n'))
    
    html_parts = re.split("<table.*?.</table>", html)
    return html_parts

def Rank2Html(rank, raw2perform, event, mode):
    titles = ['排名', '姓名', '成绩']
    idxes = [i+1 for i in range(len(rank))]
    names = [i for i in rank]
    perfs = [raw2perform[i][event][mode] for i in rank]
    t_dict = {}
    t_dict[titles[0]] = idxes
    t_dict[titles[1]] = names
    t_dict[titles[2]] = perfs

    df = pd.DataFrame(t_dict)
    df = df[titles]
    h = df.to_html(index=False)
    h = h.replace('dataframe', 'dataframe mystyle')
    for i in rank:
        h = h.replace(i,
            '<a href="https://cubingchina.com/results/person/%s">%s</a>'%(
                i.split(',')[0], i.split(',')[-1]
            )
        )
    return h

if __name__ == "__main__":
    # get cubers
    f = open("wca_id.csv", encoding='utf-8')
    raw_list = f.readlines()
    # raw_list = raw_list[:10]
    raw_list = [i[:-1] for i in raw_list]
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
    num2chn = {
        0: '单次',
        1: '平均',
    }

    html_parts = DevideTemp()
    for event in eng2chn:
        
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
            print(ranked_lambs)
            print()
            t_table = Rank2Html(ranked_lambs, raw2perform, event, mode)
            if event != 'comp_solve':
                t_table = "<hr><nav><h2>%s%s</h2></nav>"%(eng2chn[event], num2chn[mode]) + t_table
            else:
                t_table = "<hr><nav><h2>%s</h2></nav>"%(eng2chn[event].split('|')[mode]) + t_table
            html_parts.insert(-1, t_table)
    
    f = open("../mzr_plus.html", encoding='utf-8', mode='w') 
    f.write("".join(html_parts))
    