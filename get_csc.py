#!/usr/bin/env python3
"""This function analyzes the weather and posts it to slack.
It was written for CUAC team Galactose Intolerance. Feel free to use it as you'd
like. If you'd like to modify the definition of a 'good night', then you
can modify line 106ish and change the variables in bool_stats. You will also
need to modify the client OAuth Access Token"""

__version__ = '3.7.2'
__author__ = "Dylan Gatlin"


import requests
import numpy as np
import datetime as dt
import slack
import astropy.table
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import starcoder42 as s

start = dt.datetime.now()
print("ClearSkies started at {}".format(start))

# Creates a log file
home = Path(__file__).parent.absolute()
log_path = home / 'clear_sky.log'
# print("Log file stored at:", log_path)
log = open(log_path, "a")
log.write("download_csc.py started at {}\n".format(dt.datetime.now()))

channel_names = {'Dylan': '@dylan.gatlin',
                 'Beans': '#general'
                 }
location_names = {"SBO": "http://www.cleardarksky.com/c/SomBoschObCOkey.html?1",
                  "Dunes": "http://www.cleardarksky.com/c/GSDNPCOkey.html?1",
                  "MRS": "https://www.cleardarksky.com/c/MSRApObCOkey.html?1",
                  "APO": "http://www.cleardarksky.com/c/ApachePtNMkey.html"
                  }


class ClearSky:
    """Connects and reads the clear sky chart, as well as sends it to a desired
    party

    Methods:
        __init__: Takes location and channel name, then downlaods the forecast
        send: Sends the message"""

    def __init__(self, location, channel, test):
        self.location_name = location
        self.location = location_names[location]
        self.channel = channel_names[channel]
        self.sunset_time = ''
        self.post_line = ''
        self.test = test
        # print(home / 'bean_clear_skies.key')
        try:
            self.oauth_token = (home / 'beancc_clearskies.key').open(
                'r').readline()
        except Exception as e:
            print(e)
        if self.oauth_token is None:
            raise s.GatlinError('No oauth token found')
        # Download from website using requests)
        # print(self.location)
        np.random.choice
        header = {"user-agent": np.random.choice([
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101"
            " Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/605.1.15"
            " (KHTML, like Gecko) Version/14.0 Safari/605.1.15 Midori/6"
        ]),
            "referer": "http://google.com"
        }
        r = requests.get(self.location, headers=header)
        # print(r)
        # print(r.content)
        # print(r.text)
        # The content of the image
        soup = BeautifulSoup(r.text, 'html.parser')
        if "Mod_Security" in str(soup):
            raise s.GatlinError("Request declined by CSC")
        subset = soup.find('map')
        # print(subset)
        log.write("Clear Skies successfully reached.\n")

        # Check to see how long useful values is
        # There may be anywhere between 44 and 65 items in each line
        # Some lines might be longer than others at APO
        # print(subset)
        self.n_times = []
        self.includes_ecmwf = 'Cloud' in str(subset)
        self.includes_smoke = 'Smoke' in str(subset)
        loc = 0
        for i, line in enumerate(subset):
            if i == 0:
                continue
            if line == '\n':
                continue
            # print(line)
            line = str(line)
            split_line = line.split(',')
            if int(split_line[1]) != loc:
                loc = int(split_line[1])
                self.n_times.append(1)
                # print(loc)
            else:
                self.n_times[-1] += 1

        # print(subset)
        # print()
        s.iprint("There are {} times in the record".format(self.n_times), 1)
        # TODO User BeautifulSoup to iterate instead of manually indexing

        self.useful_values = str(subset).split(">\n<")[1:]
        # print(self.useful_values)
        # print(self.useful_values[self.ntimes])
        # Cloud Cover, percentage
        n_loops = 0
        clouds = []
        for line in self.useful_values[:self.n_times[n_loops]]:
            # print(line)
            val = line.split('title=')[-1].split(':')[-1]
            # print(val)
            if "Clear" in val:
                clouds.append(0)
            elif "Overcast" in val:
                clouds.append(100)
            elif "Too cloudy" in val:
                clouds.append(100)
            else:
                clouds.append(int(val.split("%")[0]))
        clouds = np.array(clouds)
        # print(clouds)
        n_loops += 1

        # ECMWF Cloud
        ecmwf_clouds = []
        for line in self.useful_values[sum(self.n_times[:n_loops]):
                                       sum(self.n_times[:n_loops+1])]:
            # print(line)
            val = line.split('title=')[-1].split('Cloud ')[-1].strip('%"/')
            # print(val)
            if 'Clear Sky' in str(val):
                ecmwf_clouds.append(0)
            elif 'Overcast' in str(val):
                ecmwf_clouds.append(100)
            else:
                ecmwf_clouds.append(int(val))
        ecmwf_clouds = np.array(ecmwf_clouds)
        n_loops += 1

        # Transparency
        # 1 is bad, 5 is good
        trans = []
        # print('Transparency')
        for line in self.useful_values[sum(self.n_times[:n_loops]):
                                       sum(self.n_times[:n_loops+1])]:
            # print(line)
            # s.iprint(line.split(":"), 1)
            val = line.split(":")[2].split('"')[0].split(" (")[0][1:]
            # s.iprint(val, 1)
            if val == "Transparent":
                trans.append(5)
            elif val == "Above average":
                trans.append(4)
            elif val == "Average":
                trans.append(3)
            elif val == "Below Average":
                trans.append(2)
            elif val == 'Too cloudy to forecast' or val == 'Poor':
                trans.append(1)
            else:
                # s.iprint("printing else", 1)
                s.iprint(f"Unable to parse: {line}", 1)
        trans = np.array(trans)
        n_loops += 1

        # Seeing
        # 1 is bad, 5 is good
        seens = []
        # print('Seeing')
        for line in self.useful_values[sum(self.n_times[:n_loops]):
                                       sum(self.n_times[:n_loops+1])]:
            # print(line)
            val = line.split(':')[-1]
            if val == "Bad 1/5":
                seens.append(1)
            elif val == "Poor 2/5":
                seens.append(2)
            elif val == "Average 3/5":
                seens.append(3)
            elif val == "Good 4/5":
                seens.append(4)
            else:
                seens.append(5)
        seens = np.array(seens)
        # print(seens)
        n_loops += 1

        # Only run with smoke if it finds the first value to contain smoke
        # if self.includes_smoke:

        # Smoke (which may not always be there)
        smokes = []
        # print('Smoke')
        for line in self.useful_values[sum(self.n_times[:n_loops]):
                                       sum(self.n_times[:n_loops+1])]:
            # print(line)
            val = line.split(':')[-1]
            if 'No Smoke' in val:
                smokes.append(0)
            else:
                smokes.append(1)
        n_loops += 1

        # Wind
        # Lower limit
        winds = []
        # print('Wind')
        for line in self.useful_values[sum(self.n_times[:n_loops]):
                                       sum(self.n_times[:n_loops+1])]:
            # print(line)
            val = line.split(':')[-1]
            # print(val)
            if ">" in val:
                winds.append(45)
            elif 'Smoke' in val:
                winds.append(0)
            else:
                # print(val.split())
                winds.append(int(val.split()[2]))
        winds = np.array(winds)
        n_loops += 1

        # Humidity
        humids = []
        # print('Humidity')
        for line in self.useful_values[sum(self.n_times[:n_loops]):
                                       sum(self.n_times[:n_loops+1])]:
            # print(line)
            val = line.split(':')[-1]
            # print(val)
            if ("<" not in val) and ('&lt;' not in val):
                # print("ran")
                humids.append(int((val.split()[2]).strip('%"/')))
            else:
                humids.append(10)
        humids = np.array(humids)
        n_loops += 1

        # Temperatures
        temps = []
        # print('Temps')
        for line in self.useful_values[sum(self.n_times[:n_loops]):
                                       sum(self.n_times[:n_loops+1])]:
            # print(line)
            val = line.split(':')[-1]
            # print(val)
            if "<" in val:
                temps.append(s.fahr2cel(-40))
            elif ">" in val:
                temps.append(s.fahr2cel(113))
            else:
                temp = int(val.split()[2].strip('F"/'))
                temps.append(s.fahr2cel(temp))
        temps = np.array(temps)
        # print(temps)

        log.write("Values successfully unpacked\n")

        # Times
        times = []
        for line in self.useful_values[sum(self.n_times[:n_loops]):
                                       sum(self.n_times[:n_loops+1])]:
            time = line.split('title="')[-1].split(':')[0]
            times.append(int(time))
        # print(times)
        # Creates a list of the days using times
        days = []
        date = 1
        for i, time in enumerate(times):
            if date == 1 and time < 23:
                days.append("Today")
            elif time == 23:
                date += 1
                days.append(days[-1])
            elif date == 2 and time < 23:
                days.append("Tomorrow")
            elif time == 23:
                date += 1
                days.append(" Today")
            elif date == 3 and time < 23:
                days.append("The Next")

        times = np.array(times)
        days = np.array(days)
        shortest = np.min([len(days), len(times), len(clouds), len(trans),
                           len(seens), len(temps), len(winds), len(humids)])
        if shortest == 0:
            raise s.GatlinError(
                f"One of the arrays is of length 0:"
                f" Days: {len(days)}, Times: {len(times)},"
                f" Clouds: {len(clouds)},"
                f" Transparency: {len(trans)}, Seeing: {len(seens)},"
                f" Temperature: {len(temps)}, Wind: {len(winds)},"
                f" Humidity: {len(humids)}")

        # print(len(days[:shortest]))
        # print(len(clouds[:shortest]))
        # if self.includes_ecmwf:
        #     print(len(ecmwf_clouds[:shortest]))
        # print(len(trans[:shortest]))
        # print(len(seens[:shortest]))
        # print(len(winds[:shortest]))
        # print(len(humids[:shortest]))
        # print(len(times[:shortest]))
        # print(len(days[:shortest]))

        self.weather = astropy.table.Table([days[:shortest], times[:shortest],
                                            clouds[:shortest], trans[:shortest],
                                            seens[:shortest], temps[:shortest],
                                            winds[:shortest], humids[:shortest],
                                            ],
                                           names=["Day", "Time", "CloudCover",
                                                  "Transparency", "Seeing",
                                                  "Temperature", "Wind",
                                                  "Humidity"])
        bool_stats = ((self.weather['CloudCover'] <= 30)
                      & (self.weather['Transparency'] >= 3)
                      & (self.weather['Seeing'] >= 3)
                      & (self.weather['Wind'] <= 25)
                      & (self.weather['Humidity'] <= 80))
        qualities = ((10 - self.weather['CloudCover'] / 10)
                     + 2 * self.weather['Transparency']
                     + 2 * self.weather['Seeing']
                     + 5 * (self.weather['Wind'] < 25)
                     + (5 - self.weather['Humidity'] / 20))
        bool_temps = (-10 <= self.weather['Temperature'])\
            & (self.weather['Temperature'] <= 25)
        bool_times = np.logical_or(20 <= times, times <= 6)[:shortest]
        self.good_times = bool_stats & bool_temps & bool_times
        self.weather.add_column(astropy.table.Column(qualities, name="Rating"))
        self.weather["Rating"].format = ".0f"
        self.weather.add_column(astropy.table.Column(self.good_times,
                                                     name="IsGood"))
        log.write("Forecast:\n")
        log.write(str(self.weather))
        # s.iprint(str(self.weather).replace("\n", "\n    "), 1)

    def get_sunset(self):
        r = requests.get('https://www.timeanddate.com/sun/@5493452')
        soup = BeautifulSoup(r.text, 'html.parser')
        tab = soup.find('table', {'class': 'table'})
        self.sunset_time = tab.findAll('tr')[-1].findAll(
            'td')[0].text.split()[0]
        s.iprint(f'Sunset is at {self.sunset_time}', 1)

    def compose(self):
        if sum(self.good_times) > 0:
            self.post_line += ("These are the times with good conditions at"
                               " {}:\n```        Date: Time: Score:\n".format(
                                   self.location_name))
            for da, ti, qu in zip(self.weather['Day'][self.good_times],
                                  self.weather['Time'][self.good_times],
                                  self.weather['Rating'][self.good_times]):
                self.post_line += "{: >8}: {: >6.0f}  {: >8.0f}\n".format(
                    da, ti, qu)
            self.post_line += "```\n"
        else:
            self.post_line += ("There are no good times for observing in the "
                               "next few days at {}. Good weather means seeing "
                               "is a 3/5, transparency is a 3/5, cloud cover "
                               "is below 30%, humidity is below 60%, winds are "
                               "below 20mph, and the temperature is "
                               "reasonable. Perfect weather has a score of "
                               "40.\n".format(self.location_name))
        self.post_line += f'Sunset is at {self.sunset_time}\n'
        self.post_line += self.location
        s.iprint(self.post_line, 1)
        log.write(self.post_line + "\n")

    def send(self):
        """This function sends post_line to the selected chnnl"""
        s.iprint("Sending to {}".format(self.channel), 1)
        # print(self.oauth_token)
        sc = slack.WebClient(token=self.oauth_token)
        if not self.test:
            response = sc.chat_postMessage(channel=self.channel,
                                           text=self.post_line)
            if response["ok"]:
                log.write("Successfully sent to {}\n\n".format(self.channel))
                s.iprint("Successfully sent to {}".format(self.channel), 1)
            else:
                log.write(response["error"] + "\n\n")
                s.iprint(response["error"], 1)


def main():
    if len(sys.argv) == 3:
        # print(sys.argv)
        path, site, chnnl = sys.argv

    else:
        site = "APO"
        chnnl = 'Beans'
    if "--test" in sys.argv:
        test = True
    else:
        test = False
    weather = ClearSky(site, chnnl, test)
    try:
        weather.get_sunset()
    except Exception as e:
        s.iprint(e, 1)
        weather.sunset_time = ''
    weather.compose()
    weather.send()
    # except Exception as e:
    #     log.write(str(e))
    #     s.iprint(e, 1)


if __name__ == '__main__':
    main()
