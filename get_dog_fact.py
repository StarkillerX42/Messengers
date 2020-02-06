#!/usr/bin/env python3
import requests
import slack
import datetime as dt
import subprocess as sub
from bs4 import BeautifulSoup
from pathlib import Path

import starcoder42 as s


__version__ = 3.6
__author__ = "Dylan Gatlin"

start = dt.datetime.now()
print("Download DogFact started at {}".format(start))


class DogFact:
    def __init__(self):
        self.filename = ''
        dog_url = "https://fungenerators.com/random/facts/dogs"
        fact_page = BeautifulSoup(requests.get(dog_url).text, 'html.parser')
        fact_html = fact_page.find(attrs={'class': 'wow fadeInUp animated'})
        self.fact = list(fact_html.children)[0]

    def make_mp3(self, filename: str = "fact.mp3"):
        self.filename = filename
        tts = gTTS(text=self.fact, lang="en")
        tts.save(filename)
    
    def play_mp3(self):
        sub.call(['play', '-q', self.filename])
        sub.call(['rm', self.filename])

    def send_daily(self, key_file="beancc_dogfacts.key"):
        key_file = Path(__file__).parent / Path(key_file)
        key = key_file.open('r').read().strip('\n')
        sc = slack.WebClient(token=key)
        response = sc.chat_postMessage(channel="#general",
                               text=self.fact)
        return response


def main():
    fct = DogFact()
    response = fct.send_daily()
    if response["ok"]:
        s.iprint('Dog fact sent to Beans', 1)


if __name__ == '__main__':
    main()
