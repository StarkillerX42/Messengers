#!/usr/bin/env python3
import requests
import datetime
import slack
import starcoder42 as s
from bs4 import BeautifulSoup
from pathlib import Path

print(f'Get Catana run at {datetime.datetime.now()}')


class Catana:
    def __init__(self):
        self.is_new = True
        self.caption = ''
        self.img_link = ''
        self.here = Path(__file__).parent.absolute()

    def fetch(self):
        r = requests.get('https://catanacomics.com/')  # to find the instagram temporary link to the individual comic
        soup = BeautifulSoup(r.text, 'html.parser')
        article = soup.find('div', {'id': 'page'}).find('div', {'id': 'content'}).find('div', {'id': 'primary'}).find(
            'main', {'id': 'main'}).find('article')
        # s.iprint(article)
        insta_link = article.find('div', {'class': 'entry-content'}).find('blockquote').attrs['data-instgrm-permalink']
        r2 = requests.get(insta_link)  # To find the raw image link and the caption
        soup2 = BeautifulSoup(r2.text, 'html.parser')
        self.img_link = str(soup2).split('" property="og:image">')[0].split('"')[-1]
        self.caption = str(soup2).split('" property="og:title">')[0].split('"Catana on Instagram: ')[-1]
        captions_file = self.here / 'shown_catana_comics.txt'
        captions_list = captions_file.open('r').readlines()
        if f'{self.caption}\n' not in captions_list:
            self.is_new = True
            captions_file.open('a').write(f'{self.caption}\n')
            s.iprint(self.caption, 1)
        else:
            self.is_new = False
            s.iprint('Catana Comic is not new', 1)

    def send(self):
        key_file = self.here / 'beancc_catana.key'
        key = key_file.open('r').readline().strip('\n')
        sc = slack.WebClient(token=key)
        response = sc.chat_postMessage(channel='#general',
                               text=self.caption, attachments=[{'title': 'Catana', 'image_url': self.img_link}])
        if response['ok']:
            s.iprint('Catana comic successfully sent to slack', 1)
        else:
            s.iprint(response['error'], 1)


def main():
    cat = Catana()
    cat.fetch()
    if cat.is_new:
        cat.send()


if __name__ == '__main__':
    main()
