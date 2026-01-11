import requests
import re
import csv
import base64
from bs4 import BeautifulSoup

DUMP_NAME = "output/output_%s.csv"

# which track for ICSE, RE20, etc - technical, seng in practice, seng in society, all of them?
# should i include track in the source?
RESEARCHR_RE_URL = [
    #RE, RESEARCH
    ["https://conf.researchr.org/track/RE-2024/RE-2024-Research-Papers?",[2024]],
    ["https://conf.researchr.org/track/RE-2025/RE-2025-Research-Papers?#event-overview",[2025]]
]
RESEARCHR_ICSE_URL = [
    #ICSE, SEIS
  ["https://conf.researchr.org/track/icse-2025/icse-2025-software-engineering-in-society?#event-overview",[2025]],
    #ICSE, RESEARCH
    ["https://conf.researchr.org/track/icse-2025/icse-2025-research-track?#event-overview", [2025]]
]
RESEARCHR_FSE_URL = [
    #FSE
    ["https://conf.researchr.org/track/fse-2025/fse-2025-research-papers?#event-overview",[2025]]
]

# scraped via tampermonkey userscript
'''
["https://re20.org/index.php/accepted-papers/", {
    "row":"div.cmsmasters_toggle_wrap:nth-child(-n+3) table tbody tr",
    "title":"td.ninja_column_1 > strong",
    "author":"td.ninja_column_1 > em",
    "track":"td.ninja_column_2",
    "yr":"2020"
}]
'''

results = []

def scrapeResearchr(base_url, range):
    for yr in range:
        url = base_url.replace("%s", str(yr))
        print("Scraping %s..." % url)
        soup = getResponse(url) # python object to parse dom
        #a lovely mess to get the track
        src = soup.select_one("#content > div.page-header > h1 > span").decode_contents().rsplit(" ", 1)[0] + " - " + soup.select_one("#content > div.page-header > h1").find(string=True, recursive=False)
        for row in soup.select("#event-overview > table tr td:nth-child(2)"):
            results.append({
                "Title" : row.select_one("a:nth-child(1)").text,
                "Author(s)" : getAuthorString(row.select("div.performers > a")),
                "Publication Year" : yr,
                "Publication Source" : src,
                "Retrieval Link" : url
            })

def getAuthorString(souplist):
    str = ""
    for auth in souplist:
        str += auth.find(string=True, recursive=False)
        str += ", "
    return str[:-2]


# sends web request and returns response, copy/pasted from old project
def getResponse(url):
    # Headers spoof an actual response. I just stole the ones my browser sent in a manual visit.
    x = requests.get(url, headers = {
        "Connection":"keep-alive",
        "Cache-Control":"max-age=0",
        "sec-ch-ua":'"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile":"?0",
        "sec-ch-ua-platform":'"Windows"',
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site":"none",
        "Sec-Fetch-Mode":"navigate",
        "Sec-Fetch-User":"?1",
        "Sec-Fetch-Dest":"document",
        "Accept-Encoding":"gzip, deflate, br, zstd",
        "Accept-Language":"en-US,en;q=0.9",
        "Referer":"https://www.google.com/" #shouldn't matter
    })
    encoding = x.encoding if 'charset' in x.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(x.content, "html.parser", from_encoding=encoding)
    return soup

def outputData(id):
    name = DUMP_NAME.replace("%s", id)
    with open(name, "w", newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(list(results[0].keys()))
        for res in results:
            w.writerow(list(res.values()))
    results.clear()
    print("Results saved in %s." % name)

# == Main ==
for row in RESEARCHR_RE_URL:
    scrapeResearchr(row[0], row[1])
outputData("re")

for row in RESEARCHR_ICSE_URL:
    scrapeResearchr(row[0], row[1])
outputData("icse")

for row in RESEARCHR_FSE_URL:
    scrapeResearchr(row[0], row[1])
outputData("fse")

'''
for row in SCIDIRECT_URL:
    for issue in range(row[1][0], row[1][1]+1):
        scrapeSD(row[0], issue)
outputData("scidirect")
'''

'''for row in SPRINGER_URL:
    for volume in range(row[1][0], row[1][1]+1):
        for issue in range(1, row[2]+1):
            scrapeSpringer(row[0], volume, issue)
outputData("ese")'''