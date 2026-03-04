import argparse
import re

import requests, json, time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://pajak.go.id"

def save_href_id():
    response = requests.get(BASE+"/index-belajar-pajak")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        print("Main page loaded successfully.")
        regions = soup.select(".layout__region--first, .layout__region--second, .layout__region--third")
        print(regions)
        if regions :
            href_list = []
            for region in regions:
                for a in region.select("a"):
                    data = {}
                    question = a.string
                    a_href = a.get("href")
                    data["question"] = question
                    data["href"] = a_href
                
                    print(a_href)
                    href_list.append(data)
            with open("href_id.json", "w", encoding="utf-8") as f:
                json.dump(href_list, f, ensure_ascii=False, indent=2)
            print(f"Saved {len(href_list)} hrefs to 'href_id.json'.")
        else:
            print("No regions found on the page.")
                    
        
    else:
        print(f"Failed to load page: {response.status_code}")
        return None 
def save_education():
    with open("href_id.json","r", encoding="utf-8") as f:
        href_list = json.load(f)
        education_data = []
        for item in href_list:
            url = urljoin(BASE, item["href"])
            print(f"Scraping {url}...")
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                content = soup.select_one(".node__content")
                if content:
                    raw_answer = content.get_text(" ", strip=True)
                    clean_answer = re.sub(r'<[^>]+>', ' ', raw_answer) 
                    clean_answer = re.sub(r'\s+', ' ', clean_answer).strip()
                    education_data.append({
                        "question": item["question"],
                        "answer": clean_answer
                    })
                    print(f"Added data for: {item['question']}")
                else:
                    print(f"No content found for: {item['question']}")
            else:
                print(f"Failed to load page: {response.status_code} for {item['question']}")
            time.sleep(3)
        with open("scrap_education.json", "w", encoding="utf-8") as f:
            json.dump(education_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "command",
        help="function to run",
        choices=["href", "education"]
    )

    args = parser.parse_args()

    if args.command == "href":
        save_href_id()

    elif args.command == "education":
        save_education()