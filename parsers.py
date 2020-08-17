from bs4 import BeautifulSoup
import requests as req


def mirea_parser(fio, link):
    try:
        name1, last_name1, middle_name1, ege = fio.split('. ')
        resp = req.get(link)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for obj in soup.find_all('tr'):
            name = obj.find("td", {"class": "fio"})
            if name is not None:
                ans = name.text.strip().split(' ')
                if len(ans) == 3 and \
                        ans[0] == last_name1 and ans[1] == name1 and ans[2] == middle_name1:
                    accepted = obj.find("td", {"class": "accepted"})
                    pos = obj.find("td", {"class": "num"})
                    score = obj.find("td", {"class": "sum"})
                    return [pos.text, accepted.text, score.text]
    except Exception as e:
        print(e)
    return ['ошибка', 'ошибка', 'ошибка']


def get_current_state(fio, link, edkey):
    if link.split('//')[1][:14] == 'priem.mirea.ru':
        return mirea_parser(fio, link)

    return [24, 'нет', 2]

