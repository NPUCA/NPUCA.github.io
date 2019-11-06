import time
import requests
from bs4 import BeautifulSoup as BS

#To get HTML Text
def GetHtml(url):
    kv = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',        
    }
    try:
        r = requests.get(url, timeout=7,headers = kv)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        return ""

# search people, get Candidates
def GetCandidate(name):
    search_api = 'https://cubingchina.com/results/person?region=World&gender=all&name='
    search_html = GetHtml(search_api+name)
    search_soup = BS(search_html, 'html.parser')
    
    candidates = []
    candidate_num = 0
    page_template = ''
    search_page_num = 0
    try:
        page_template = 'https://cubingchina.com'+search_soup.find_all('li')[-2].a['href'].replace(';', '&')
        page_template = '='.join(page_template.split('=')[:-1])+'='
        search_page_num = int(search_soup.find_all('li')[-2].a['href'].split('=')[-1])
        candidate_num += (search_page_num-1)*100

        # find the last page's people
        last_page_url = page_template + str(search_page_num)
        page_html = GetHtml(last_page_url)
        page_soup = BS(page_html, 'html.parser')
        for tr in page_soup.find_all('tr')[1:]:
            candidates.append(
                (
                    tr.td.div.label.input['data-name'], 
                    tr.td.div.label.input['data-id'],
                    tr.find_all("td")[-2].string.strip(),
                    tr.find_all("td")[-1].string.strip()
                )
            )
            candidate_num += 1
        
    except:
        # only one page
        for tr in search_soup.find_all('tr')[1:]:
            try:# page have people
                candidates.append(
                    (
                        tr.td.div.label.input['data-name'], 
                        tr.td.div.label.input['data-id'],
                        tr.find_all("td")[-2].string.strip(),
                        tr.find_all("td")[-1].string.strip()
                    )
                )
                candidate_num += 1
            except:
                return 0, []
    
    
    # for i in range(search_page_num):
    #     page_url = page_template + str(i+1)
    #     page_html = GetHtml(page_url)
    #     page_soup = BS(page_html, 'html.parser')
    #     for tr in page_soup.find_all('tr')[1:]:
    #         candidates.append(
    #             (
    #                 tr.td.div.label.input['data-name'], 
    #                 tr.td.div.label.input['data-id'],
    #                 tr.find_all("td")[-2].string.strip(),
    #                 tr.find_all("td")[-1].string.strip()
    #             )
    #         )
    #         candidate_num += 1
    
    return candidate_num, candidates


# get someone's wca perform 
# 返回字典
# event : perform
def GetPerform(wca_id):
    people_root = 'https://cubingchina.com/results/person/'
    people_page = people_root + wca_id
    people_html = GetHtml(people_page)
    people_soup = BS(people_html, 'html.parser')

    event2perform = {}
    try:
        event_list = people_soup.tbody.find_all('tr')
    except:
        print("鸭鸭鸭")
        time.sleep(23)
        return GetPerform(wca_id)
    for event in event_list:
        # 因为不一定就是event的表格
        try:
            if len(event('a')) == 3: # have avg perform
                event2perform[event.td.a['href'][1:]] = (
                    event('a')[1].string, event('a')[2].string
                )
            elif len(event('a')) == 2: # only single perform
                event2perform[event.td.a['href'][1:]] = (
                    event('a')[1].string, ''
                )
        except:
            continue
    event2perform['roa'] = (
        people_soup.find_all('tbody')[1].find_all('tr')[0].find_all('td')[1].string,
        people_soup.find_all('tbody')[1].find_all('tr')[1].find_all('td')[1].string
    )

    solved_trs = people_soup.find_all('tbody')[0].find_all('tr')
    solved_times = 0
    for tr in solved_trs:
        solved_times += int(tr.find_all('td')[-1].string.split('/')[0])

    event2perform['comp_solve'] = (
        people_soup.find_all('span')[6].string, str(solved_times)
    )
    return event2perform

def GenMessage(name):
    message = []
    cand_num, cands = GetCandidate(name)
    
    # fucking you~
    if cand_num == 0:
        message += "找不到鸭"
    elif cand_num == 1:
        message.append(cands[0][0])
        message.append(','.join(cands[0][1:]))

        cand_perform = GetPerform(cands[0][1])
        for i in cand_perform:
            if isinstance(cand_perform[i], tuple) and len(cand_perform[i]) == 2:
                message.append('%s %s|%s'%(i, cand_perform[i][0], cand_perform[i][1]))
            else:
                message.append('%s %s'%(i, cand_perform[i]))
    else:
        message.append('找到了%d个人鸭'%cand_num)
        for i in range(min(5, cand_num)):
            message.append('%s|%s'%(cands[i][1], cands[i][0]))
        if cand_num > 5:
            message.append("...")
    return '\n'.join(message)


