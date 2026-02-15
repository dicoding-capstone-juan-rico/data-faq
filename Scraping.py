import requests, json, time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://pajak.go.id"


def get_faq_list(page):
    url = f"{BASE}/id/faq-page?page={page}"
    soup = BeautifulSoup(requests.get(url).text, "html.parser")

    faqs = []
    for a in soup.select("td.views-field-title a"):
        faqs.append({
            "question": a.get_text(strip=True),
            "detail_url": urljoin(BASE, a["href"])
        })

    return faqs


def scrape_detail(url):
    soup = BeautifulSoup(requests.get(url).text, "html.parser")

    node = soup.select_one("div.node__content")
    if not node:
        return None, None, None

    answer_text = node.get_text(" ", strip=True)

    answer_html = str(node)

    pdf_link = None
    pdf = soup.select_one("a[href$='.pdf']")
    if pdf:
        pdf_link = pdf["href"]

    return answer_text, answer_html, pdf_link

def main():
    results = []
    page = 0

    while True:
        print(f"\nScraping list page {page}...")

        faq_list = get_faq_list(page)
        if not faq_list:
            print("Tidak ada data lagi,")
            break

        for faq in faq_list:
            print(" →", faq["question"])

            answer_text, answer_html, pdf_link = scrape_detail(faq["detail_url"])

            results.append({
                "question": faq["question"],
                "answer_text": answer_text,
                "answer_html": answer_html,
                "pdf_link": pdf_link,
                "detail_url": faq["detail_url"]
            })

            time.sleep(0.5) 

        page += 1

    with open("faq_pajak.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("DONE!")


if __name__ == "__main__":
    main()