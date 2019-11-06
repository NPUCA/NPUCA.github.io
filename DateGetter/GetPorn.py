# 毒鸡汤getter
from Spider import *

def GetPron():
    porn_html = GetHtml("https://8zt.cc/")
    porn_soup = BS(porn_html, 'html.parser')

    porn = porn_soup.find_all('span')[0].string.strip()
    print(porn)
    return porn

def GetPronToSet(result:set):
    set.add(GetPron())

if __name__ == "__main__":
    f = open("./Porns.txt", mode='r', encoding='utf-8')
    lines = f.readlines()
    lines = [i.strip() for i in lines]

    porns = set(lines)
    for i in range(3):
        GetPronToSet(porns)
        time.sleep(3)

    f = open("./Porns.txt", mode='w', encoding='utf-8')
    for porn in porns:
        f.write(porn+'\n')
