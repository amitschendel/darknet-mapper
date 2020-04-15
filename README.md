# Darknet mapper

Darknet mapper is a project I did in order to research about the darknet.<br />
After exploring a bit inside the darknet I saw that is very hard to search for<br />
links. Moreover, even if you find links a lot of them dosen't work.<br />
So I decided to build a crawler that will search links for me and store a little bit of information on each link.<br />

## How it works

The way it works is by recursively extract all links from a web page and store them in a database<br />
with the following information:<br />

1. url<br />
2. title<br />
3. description<br />
4. emails<br />
5. telegram links<br />
6. bitcoin wallets<br />
7. gathered links<br />
8. date<br />
9. tags (category of the website by keywords)<br />

## Terminology

**Clearnet** - publicly accessible Internet.<br />
**Deep Web** - parts of the World Wide Web whose contents are not indexed by standard web search-engines.<br />
**Darknet** - overlay network within the Internet that can only be accessed with specific software, configurations, or <br />authorization, and often uses a unique customised communication protocol.

![darknet_ice](https://user-images.githubusercontent.com/58078857/79280206-7168d780-7eb8-11ea-90f9-16205992a004.png)

## Installation

If you dont have mongodb installed make sure to install it:<br />
```https://docs.mongodb.com/manual/installation/```

```bash
pip install -r requirements.txt
```

## Usage

```bash
python3 crawler.py
```

## Poc

After 12 hours of total run time I was able to get 1500 links as you can see in the json file (darknet_unique.json).

## Disclaimer

This project is for educational purposes only, we are not responsible for any kind of abuse.
