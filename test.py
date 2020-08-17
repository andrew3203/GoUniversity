from bs4 import BeautifulSoup
import requests as req

resp = req.get("https://priem.mirea.ru/rating/names_rating.php?competition=1660763983762693430")
soup = BeautifulSoup(resp.text, 'html.parser')
data = soup.find_all('tr')
for obj in soup.find_all('tr'):
    name = obj.find("td", {"class": "fio"})
    if name is not None:
        print(name.text)
