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
    eur = root.find(".//Valute[CharCode='EUR']")
    if usd is not None:
        return [float(usd.find('Value').text.replace(",", ".")), float(eur.find('Value').text.replace(",", "."))]
    else:
        return "Valute with CharCode 'USD' or 'EUR' not found."


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
    count = 1
    for block in response_json['results']:
        if block['type'] == 'paragraph':
            for item in block['paragraph']['rich_text']:
                content = item['text']['content']
                if item['text']['link'] is not None:
                    link = item['text']['link']['url']
                    result += f'<a href=\'{link}\'>{content}</a>'
                else:
                    result += f'{content}'
        elif block['type'] == 'code':
            for item in block['code']['rich_text']:
                content = item['text']['content']
                result += f'<code>{content}</code>'
        elif block['type'] == 'bulleted_list_item':
            for item in block['bulleted_list_item']['rich_text']:
                content = item['text']['content']
                if item['text']['link'] is not None:
                    link = item['text']['link']['url']
                    result += f'<a href=\'{link}\'>  - {content}</a>'
                else:
                    result += f'  - {content}'
        elif block['type'] == 'numbered_list_item':
            result += f'{count}. '
            for item in block['numbered_list_item']['rich_text']:
                content = item['text']['content']
                if item['text']['link'] is not None:
                    link = item['text']['link']['url']
                    result += f'<a href=\'{link}\'><b>{content}</b></a>'
                else:
                    result += f'{content}'
            count += 1
        elif block['type'] == 'heading_2':
            for item in block['heading_2']['rich_text']:
                content = item['text']['content']
                if item['text']['link'] is not None:
                    link = item['text']['link']['url']
                    result += f'<a href=\'{link}\'>{content}</a>'
                else:
                    result += f'\n<b>{content}</b>'
        result += '\n'
    return result


def retrieve_database(database_id):
    url = f'https://api.notion.com/v1/databases/{database_id}/query'
    payload = {"page_size": 100}
    headers = {
        'Authorization': 'Bearer ' + TOKEN,
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    response = requests.post(url, json=payload, headers=headers)
    response_json = response.json()
    result = []
    for item in response_json['results']:
        result.append(item['properties'])
    return result


page_id = '835134304a624705a6607de0e51ea581'
get_notion_page(page_id)


database_id = '6b8943a4-28c8-49f0-bee4-e5bffb5e7d7d'
