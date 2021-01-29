from bs4 import BeautifulSoup as bs
import requests as r
from io import BytesIO
import json
import re
import math
from PIL import Image
import os

import img_manip as im

root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
data_dir = os.path.join(root_dir,'data')

def scrape_data():
    '''
    Collect image hash fingerprints from The Gatherer website
    '''

    # Get parsed webpage using beautifulsoup
    search_url = "https://gatherer.wizards.com/Pages/Search/Default.aspx?page={0}&name=+[%22%22]"
    parser = "html.parser"

    first_page = r.get(search_url)
    first_page_parsed = bs(first_page.content, parser)

    # Calculate number of pages in search result
    termDisplay = first_page_parsed.find("p", attrs={"class": "termdisplay"}).text
    num_cards = int(re.search("\d+", termDisplay).group())
    num_pages = math.ceil(num_cards / 100)

    hash_dict = {}
    # Iterate through pages in search result
    for page_num in range(num_pages):

        print("Scraping page {0}/{1}".format(page_num+1, num_pages))

        page = r.get(search_url.format(page_num))
    
        cards = bs(page.content, parser)

        card_items = cards.find_all("tr", class_="cardItem")
        
        # Iterate through cards on each page
        for each_card in card_items:
            mid_col = each_card.findChild("td", class_="middleCol")
            card_name = mid_col.findChild("div", class_="cardInfo").findChild("span", class_="cardTitle").a.string
            
            left_col = each_card.findChild("td", class_="leftCol")
            relative_src = left_col.a.img.attrs['src']
            img_src = relative_src.replace("../../","https://gatherer.wizards.com/")

            # Generate hash for each card
            img_hash = get_hash_from_img_url(img_src)
            hash_dict[card_name] = img_hash

    hash_json = json.dumps(hash_dict, indent=4)
    update_img_hashes(hash_json)
    
    print("Parse successful")

def get_hash_from_img_url(img_src):
    '''
    Perform hash algorithm given an html link to a card image
    '''
    response = r.get(img_src, stream=True)
    response.raw.decode_content = True
    img = Image.open(BytesIO(response.content))
    img = im.crop_art(img)
    return im.get_hash(img)

def update_img_hashes(hash_json):
    '''
    Used to update the stored image hash file
    '''
    img_hash_file = open(os.path.join(data_dir,"img_hashes.json"), 'w')
    img_hash_file.write(hash_json)

def add_one_img_hash(hash_json):
    '''
    Add one image hash without overwriting entire file
    '''
    img_hash_file = open(os.path.join(data_dir,"img_hashes.json"), 'r+')
    current = json.load(img_hash_file)
    add = json.loads(hash_json)
    merged = {**current, **add}
    json_dump = json.dumps(merged, indent=4)
    img_hash_file.seek(0)
    img_hash_file.write(json_dump)

if __name__ == "__main__":
    scrape_data()