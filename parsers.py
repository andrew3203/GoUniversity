from bs4 import BeautifulSoup
import requests as req


def mirea_parser(fio, link):
    try:
        resp = req.get(link)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for obj in soup.find_all('tr'):
            name = obj.find("td", {"class": "fio"})
            if name is not None:
                ans = name.text.strip().split(' ')
                if len(ans) == 3 and \
                        ans[0] == fio['last__name'] and \
                        ans[1] == fio['first_name'] and \
                        ans[2] == fio['middle_name']:
                    accepted = obj.find("td", {"class": "accepted"})
                    pos = obj.find("td", {"class": "num"})
                    score = obj.find("td", {"class": "sum"})
                    print(pos)
                    return [pos.text, accepted.text, score.text]
    except Exception as e:
        print(e)
    return ['ошибка', 'ошибка', 'ошибка']


def get_current_state(fio, link, edkey):
    print(link)
    if link.split('//')[1][:14] == 'priem.mirea.ru':
        return mirea_parser(fio, link)

    return [24, 'нет', 2]

