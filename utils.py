import os

import requests
from datetime import datetime
import xml.etree.ElementTree as ET

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('NOTION_TOKEN')


def usd_course():
    url = "https://cbr.ru/scripts/XML_daily.asp/"
    now = datetime.now()
    current_date = now.strftime("%d/%m/%Y")
    params = {
        "date_req": current_date,
    }
    r = requests.get(url, params=params).text
    root = ET.fromstring(r)
    usd = root.find(".//Valute[CharCode='USD']")
    if usd is not None:
        return float(usd.find('Value').text.replace(",", "."))
    else:
        return "Valute with CharCode 'USD' not found."


def get_notion_page(block_id):
    url = f'https://api.notion.com/v1/blocks/{block_id}/children?page_size=100'
    headers = {
        'Authorization': 'Bearer ' + TOKEN,
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    result = ''
    response = requests.get(url, headers=headers)
    response_json = response.json()
    for block in response_json['results']:
        if block['type'] == 'paragraph':
            for item in block['paragraph']['rich_text']:
                content = item['text']['content']
                if item['text']['link'] is not None:
                    link = item['text']['link']['url']
                    result += f'<a href=\'{link}\'>{content}</a>'
                else:
                    result += f'{content}'
            result += '\n'
    return result


# page_id = '9c1d96bf8fef469394d4db2ac617a183'
# get_notion_page(page_id)
