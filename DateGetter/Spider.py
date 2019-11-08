import json
import time
import requests
from lxml import etree

# 返回html文本
def GetHtml(url:str)->str:
    kv = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',        
    }
    # 异常处理防止get请求没有返回（被ban的情况etc）
    try:
        r = requests.get(url, timeout=7,headers = kv)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        return ""

# 按 id/name 粗略查询, 返回所有candidate
# 返回 candidate_num:int, candidates:list
# candidate 为一个元组, 格式为( name, wcaid, country, gender )
def GetCandidate(name:str)->(int, list):
    # 不直接json.loads(GetHtml(xxx)), 便于处理异常
    result = GetHtml(
        'http://wcads.lz1998.xin/wcaPerson/searchPeople?q=%s'%name
    )
    if result == "":
        time.sleep(5) # 通过递归处理get请求没有返回的异常, 但是要加sleep, 不然stack overflow
        return GetCandidate(name) 
    
    result_json = json.loads(result)
    if (result_json['msg'] != 'ok'): # 异常处理, 原因类似上面
        time.sleep(5)
        return GetCandidate(name)
    
    char2chinese = {
        'm':'男',
        'f':'女'
    }

    can_num = result_json['totalElements']
    cans = [
        (i['name'], i['id'], i['countryId'], char2chinese[i['gender']])
        for i in result_json['data']
    ]
    return can_num, cans


# get someone's wca perform 
# 返回 event2perform:dict
# 每个项目对应成绩 {event : perform}
# perform:(single, avg), 没有avg使用''空字符串代替
def GetPerform(wca_id:str)->dict:
    event2perform = {}
    comp = set()
    solv = 0
    
    # 以下基本与GetCandidate类似
    result = GetHtml(
        'http://wcads.lz1998.xin/wcaResult/findResultsByPersonId?personId=%s'%wca_id
    )
    if result == "":
        time.sleep(5) 
        return GetPerform(wca_id) 
    
    result_json = json.loads(result)
    if (result_json['msg'] != 'ok'):
        time.sleep(5)
        return GetPerform(wca_id)

    # 对数据进行简单清洗
    def deco(sig_raw:int, avg_raw:int)->(str, str):
        sig_raw /= 100
        avg_raw /= 100
        sig = ''
        avg = ''
        if sig_raw <= 0:
            sig = ''
        else:
            sig = '%.2f'%sig_raw
        if avg_raw <= 0:
            avg = ''
        else:
            avg = '%.2f'%avg_raw
        return (sig, avg)
    def MyMin(v1:str, v2:str)->str:
        if v1 == '':
            return v2
        if v2 == '':
            return v1
        return str(min(float(v1), float(v2)))


    for rnd in result_json['data']: # 对于每一轮
        if rnd['eventId'] not in event2perform: # 之前没出现这个项目
            event2perform[rnd['eventId']] = deco(rnd['best'], rnd['average'])
        else: # 之前出现过
            sig, avg = event2perform[rnd['eventId']]
            new_sig, new_avg = deco(rnd['best'], rnd['average'])
            sig = MyMin(sig, new_sig)
            avg = MyMin(avg, new_avg)
            event2perform[rnd['eventId']] = (sig, avg)

        # 添加这场比赛, 注意使用的是set, 所以不会加重
        comp.add(rnd['competitionId']) 

        # 看六把成绩, 判断是否有效, 计算复原次数
        for i in range(1, 6):
            if rnd['value%d'%i] > 0:
                solv += 1
    
    # 接下来是roa, lzdl的api没有, 使用xpath爬粗饼获得
    html = GetHtml('https://cubingchina.com/results/person/%s'%wca_id)
    html = etree.HTML(html)
    event2perform['roa'] = (
        html.xpath('//*[@id="yw1"]/table/tbody/tr[1]/td[6]/a/text()')[0],
        html.xpath('//*[@id="yw1"]/table/tbody/tr[2]/td[6]/a/text()')[0]
    )

    # 参赛次数和复原次数
    event2perform['comp_solve'] = (
        str(len(comp)), str(solv)
    )
    return event2perform

if __name__ == "__main__":
    # html = GetHtml('http://wcads.lz1998.xin/wcaPerson/searchPeople?q=彭')
    # data = json.loads(html)
    # print(html)
    # print(data['msg'])
    # print(len(data['data']))
    # num, can = GetCandidate("彭伟聪")
    # print(can)
    
    # html = GetHtml('https://cubingchina.com/results/person/2012DEMU01')
    # html = etree.HTML(html)
    # print(html.xpath('//*[@id="yw1"]/table/tbody/tr[1]/td[2]/a/text()'))
    # '//*[@id="yw1"]/table/tbody/tr[1]/td[2]/a'
    # //*[@id="yw1"]/table/tbody/tr[2]/td[2]/a

    perf = GetPerform('2017YANG16')
    print(perf)