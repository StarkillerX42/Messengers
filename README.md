# Messengers
A library of apps designed to message slack regularly. These used to be many
 different projects, but since they're maintained the same way, it made sense
 to consolidate them. They are best run as cronjobs with a local slack key.

### Author
Dylan Gatlin

dgatlin@apo.nmsu.edu

##TODO

- Create shared utilities for these separate tools to all use to standardize
 slack functionality and other common behaviors

## ClearSkies

A bot to share clear sky chart data with CUAC

### How it works:

This bot uses the clearskychart at
 <http://www.cleardarksky.com/c/SomBoschObCOkey.html?1> to check to see how
 the weather is at APO. It needs to be astronomically clear enough for us to
 use it for observing, so this is a very important bot!

### TODO

- Get this bot to respond to a request for a result, like if someone mentions
 the bot, they will respond. Currently, this won't correctly write to the
 clear_sky.log

## XKCDBot

A bot that parses new xkcd comics and sends them to slack

## CatFactsBot

A bot that downloads a random cat fact and sends it to slack

## DogFactsBot

The same as CatFactsBot but for dogs

## CatanaComicsBot

A bot that downloads the newest Catana Comics and sends it to slack

## GNU License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

