#!/usr/bin/env python3
import requests
import slack
import datetime as dt
from bs4 import BeautifulSoup
from pathlib import Path
import starcoder42 as s


print(f'Get XKCD Run at {dt.datetime.now()}')



class XKCD:
    def __init__(self):
        self.is_new = True

    def fetch(self):
        # Get a new comic
        r = requests.get('https://www.xkcd.com')
        soup = BeautifulSoup(r.text, 'html.parser')
        image = soup.find(id='comic').find_all()[0]
        self.alt_text = str(image).split('title=')[1].strip('">\n</img>')
        self.alt_text =self.alt_text.replace('&quot;', '"')
        self.img_url = str(image).split('src=')[-1].split()[0][3:-1]
        self.here = Path(__file__).parent.absolute()

        # Check to see if I already got the comic
        self.images_file = self.here / 'shown_xkcd_comics.txt'
        images_list = self.images_file.open('r').readlines()
        # print(images_list)
        if f'{self.img_url}\n' not in images_list:
            self.is_new = True
        else:
            self.is_new = False
            s.iprint('XKCD is not new', 1)

    def send(self):
        key_file = self.here / 'beancc_xkcd.key'
        key = key_file.open('r').readline().strip('\n')
        # print(key)
        sc = slack.WebClient(token=key)
        response = sc.chat_postMessage(channel='#general', text=self.alt_text,
                               attachments=[{'title': 'xkcd', 'image_url': 'http://' + self.img_url}])
        if response['ok']:
            s.iprint('xkcd successfully sent to Slack', 1)
            self.images_file.open('a').write(f'{self.img_url}\n')
        else:
            s.iprint(response['error'], 1)

def main():
    xkcd = XKCD()
    xkcd.fetch()
    if xkcd.is_new:
        xkcd.send()


if __name__ == '__main__':
    main()
