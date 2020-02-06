#!/usr/bin/env python3
import requests
import starcoder42 as s
import datetime as dt
#from gtts import gTTS
import json
import subprocess as sub
from pathlib import Path
import slack

__version__ = 3.6
__author__ = "Dylan Gatlin"

start = dt.datetime.now()
print("Download CatFacts started at {}".format(start))


class CatFact:
    def __init__(self):
        cat_url = "https://cat-fact.herokuapp.com/facts/random"
        fact_page = json.loads(requests.get(cat_url).text)
        try:
            self.fact = fact_page['text']
        except:
            fact_page = json.loads(requests.get(cat_url).text)
            self.fact = fact_page['text']


    def make_mp3(self, filename: str = "fact.mp3"):
        self.filename = filename
        tts = gTTS(text=self.fact, lang="en")
        tts.save(filename)
    
    def play_mp3(self):
        sub.call(['play', '-q', self.filename])
        sub.call(['rm', self.filename])

    def send_daily(self, key_file="beancc_catfacts.key"):
        key_file = Path(__file__).parent / Path(key_file)
        key = key_file.open('r').read().strip('\n')
        sc = slack.WebClient(key)
        response = sc.chat_postMessage(channel="#general",
                               text=self.fact)
        return response


def main():
    fct = CatFact()
    response = fct.send_daily()
    if response["ok"]:
        s.iprint('Cat fact sent to Beans', 1)


if __name__ == '__main__':
    main()
