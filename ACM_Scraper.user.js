// ==UserScript==
// @name         ACM Search Scraper
// @version      2024-10-04
// @description  Grabs info from ACM search
// @author       Mettymagic
// @match        https://dl.acm.org/action/doSearch?*
// @match        https://dl-acm-org.ezproxy.lib.ucalgary.ca/action/doSearch?*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=acm.org
// @require      https://code.jquery.com/jquery-3.6.0.min.js
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_deleteValue
// @grant        GM_setClipboard
// ==/UserScript==

GM_deleteValue("data")
GM_deleteValue("csv")
scrapePage()
toCSV()

function toCSV() {
    let arr = GM_getValue("data")
    let csv = arr.map( v => v.map(x => `"${x}"`).join(",")).join('\n');
    GM_setClipboard(csv, "csv")
}

function scrapePage() {
    let content = Array.from($("#skip-to-main-content div.search-result.doSearch div.issue-item.issue-item--search"))
    let results = GM_getValue("data", [])
    for (let entry of content) {
        if(entry.querySelector(".icon-get-access")) {
            results.push([
                entry.querySelector(".issue-item__title").innerText, //title
                "N/A",
                entry.querySelector(".bookPubDate").innerHTML.split(" ")[1], //pub year
                "N/A",
                "NO ACCESS"
            ])
        }
        else if(entry.querySelector(".issue-heading").innerHTML == "proceeding") {
             results.push([
                 entry.querySelector(".issue-item__title").innerText, //title
                "N/A",
                entry.querySelector(".bookPubDate").innerHTML.split(" ")[1], //pub year
                "N/A",
                "NO ACCESS"
             ])
        }
        else {
            let authors = entry.querySelectorAll("span.hlFld-ContribAuthor a span")
            let authorString = ""
            for(let author of authors) {
                authorString += author.innerHTML
                authorString += ", "
            }
            authorString = authorString.slice(0, -2)

            if(entry.querySelector(".issue-heading").innerHTML == "proceeding") {
                var data = [
                    entry.querySelector(".issue-item__title").innerText, //title
                    authorString, //authors
                    entry.querySelector(".bookPubDate").innerHTML.split(" ")[1], //pub year
                    "N/A",
                    "EXCLUDED PROCEEDING"
                ]
            }
            else {
                data = [
                    entry.querySelector(".issue-item__title").innerText, //title
                    authorString, //authors
                    entry.querySelector(".bookPubDate").innerHTML.split(" ")[1], //pub year
                    entry.querySelector(".epub-section__title").innerHTML, //pub src
                    entry.querySelector(".btn--icon.simple-tooltip__block--b.red.btn").href //pdf link
                ]
            }
            results.push(data)
        }
    }
    GM_setValue("data", results)
}
