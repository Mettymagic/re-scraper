import requests
import re
import csv
import base64
from bs4 import BeautifulSoup

MIN_YEAR = 2025
MAX_YEAR = 2025
DUMP_NAME = "output/output_%s.csv"

# which track for ICSE, RE20, etc - technical, seng in practice, seng in society, all of them?
# should i include track in the source?
RESEARCHR_RE_URL = [
    #RE, RESEARCH
    ["https://conf.researchr.org/track/RE-2021/RE-2021-papers?#event-overview", [2021]],
    ["https://conf.researchr.org/track/RE-%s/RE-%s-Research-Papers?#event-overview", [2022, 2023, 2024]],
]
RESEARCHR_ICSE_URL = [
    #ICSE, SEIS
    ["https://conf.researchr.org/track/icse-%s/icse-%s-Software-Engineering-in-Society#event-overview", [2018, 2019]],
    ["https://%s.icse-conferences.org/track/icse-%s-Software-Engineering-in-Society#event-overview", [2020, 2021]],
    ["https://conf.researchr.org/track/icse-2022/icse-2022-seis---software-engineering-in-society?#event-overview", [2022]],
    ["https://conf.researchr.org/track/icse-2023/icse-2023-SEIS?#event-overview", [2023]],
    ["https://conf.researchr.org/track/icse-2024/icse-2024-software-engineering-in-society?#event-overview", [2024]],
    #ICSE, RESEARCH
    ["https://conf.researchr.org/track/icse-2025/icse-2025-research-track#Accepted-papers-First-and-Second-Cycle", [2025]],
]
RESEARCHR_FSE_URL = [
    #FSE
    ["https://2018.fseconference.org/track/fse-2018-research-papers#event-overview", [2018]],
    ["https://%s.esec-fse.org/track/fse-%s-papers?#event-overview", [2020, 2021]],
    ["https://%s.esec-fse.org/track/fse-%s-research-papers?#event-overview", [2022, 2023, 2024]],
]

#include selectors
RE_URL = [
    ["https://re18.org/acceptedPapers.html", {
        "row":"#all > div > div > table > tbody > tr:not(:nth-child(-n+1))",
        "title":"td:nth-child(2) > p > strong, td:nth-child(2) > strong",
        "author":"td:nth-child(2) > p, td:nth-child(2)",
        "track":"td:nth-child(3)",
        "yr":"2018"
    }],
    ["http://re19.ajou.ac.kr/pages/conference/accepted_papers/", {
        "row":"#papers-table > tbody > tr",
        "title":"td:nth-child(2) > strong",
        "author":"td:nth-child(2)",
        "track":"td:nth-child(3)",
        "yr":"2019"
    }]
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

#cloudflare, anti-scraper - will take more work
SCIDIRECT_URL = [
    ["https://www.sciencedirect.com/journal/information-and-software-technology/vol/%s/", [93, 178]],
    ["https://www.sciencedirect.com/journal/journal-of-systems-and-software/vol/%s/", [135, 220]]
]

#ESE
SPRINGER_URL = [
    ["https://link.springer.com/journal/10664/volumes-and-issues/%s-%s", [23, 30], 7]
]

results = []

def scrapeSpringer(base_url, vol, issue):
    url = base_url % (vol, issue)
    soup = getResponse(url) # python object to parse dom
    #return on page not found
    if soup.find(attrs={"data-test":"springer-not-found-page"}): return
    print("Scraping %s..." % url)
    yr = soup.select_one("#main > div > div > div > div.app-journal-latest-issue > header > time").text.split(" ")[1]
    for row in soup.select("#main > div > div > div > section > ol > li"):
        title = row.select_one("article > div.app-card-open__main > h3 > a").text
        author_list = row.select("article > div.app-card-open__main > div.app-card-open__text-container > div.app-card-open__authors > span > ul > li")
        author = getAuthorString(author_list)
        results.append({
            "Title" : title,
            "Author(s)" : author.strip(),
            "Publication Year" : yr,
            "Publication Source" : "ESE'"+yr+" - Vol. "+str(vol)+", Issue. "+str(issue),
            "Retrieval Link" : url
        })


def scrapeSD(base_url, vol):
    url = base_url.replace("%s", str(vol))
    src = ""
    if "journal-of-systems-and-software" in url: src = "JSS'" 
    else: src = "IST'"
    print("Scraping %s..." % url)
    soup = getResponse(url) # python object to parse dom
    yr_str = soup.select_one("#react-root > div > div > div > main > section:nth-child(2) > div > div > div > h3").text
    regex = r'.*\(.* (\d*)\)'
    yr = re.search(".*\(.* (\d*)\)", yr_str).group(1)
    for row in soup.select("ol.article-list-items > li.js-section-level-0:last-child > ol.article-list > li.js-article-list-item"):
        title = row.select_one("span.js-article-title").text
        author = row.select_one("div.js-article__item__authors").find(string=True, recursive=False)
        results.append({
            "Title" : title,
            "Author(s)" : author.strip(),
            "Publication Year" : yr,
            "Publication Source" : src+yr+" - Vol. "+vol,
            "Retrieval Link" : url
        })

def scrapeRE(url, selectors):
    print("Scraping %s..." % url)
    soup = getResponse(url) # python object to parse dom
    for row in soup.select(selectors["row"]):
        title = row.select_one(selectors["title"]).text.split(". ")[0].replace(", Data Challenge", "").replace(", Data show case", "")
        author = row.select(selectors["author"])[-1].text.split("\n")
        if "18" in url: author = author[-1]
        elif "19" in url: author = author[2]
        track = row.select_one(selectors["track"]).text
        results.append({
            "Title" : title,
            "Author(s)" : author.strip(),
            "Publication Year" : selectors["yr"],
            "Publication Source" : "RE'"+selectors["yr"]+" - "+track,
            "Retrieval Link" : url
        })

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
for row in RE_URL:
    scrapeRE(row[0], row[1])
for row in RESEARCHR_RE_URL:
    scrapeResearchr(row[0], row[1])
outputData("re")
exit()

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

for row in SPRINGER_URL:
    for volume in range(row[1][0], row[1][1]+1):
        for issue in range(1, row[2]+1):
            scrapeSpringer(row[0], volume, issue)
outputData("ese")