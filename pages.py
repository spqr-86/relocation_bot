import os

import requests

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('NOTION_TOKEN')

MENU = {
    'visa': 'b7e80c5d-eb4a-409f-8482-0a0884781cdb',
    'apartment': 'cb8484ac-a18e-4c15-9972-9443576ff5dc',
    'education': '40a2dce3-2d5c-4450-b0b6-3acff70921a6',
    'children': 'c4daaddf-0ff0-4e2d-8405-0a89393562c7',
    'business': '545ddc27-e749-4918-b579-2505890babb8',
    'coast': 'feb4585d-2144-43a6-ae61-eda791fceb91',
    'job': '4db02f87-51a2-48d0-b743-a87a01281ce6',
    'medical_care': '32dcdf74-97f4-4bba-8607-94013ec17058',
    'other': 'dd7b552a-50ca-4f87-b25d-e13915b3428d'
}

EDUCATION_MENU = {}
JOB_MENU = {}


def get_notion_page(block_id, menu):
    url = f'https://api.notion.com/v1/blocks/{block_id}/children?page_size=100'
    headers = {
        'Authorization': 'Bearer ' + TOKEN,
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    response = requests.get(url, headers=headers)
    response_json = response.json()
    for block in response_json['results']:
        if block['type'] == 'toggle':
            menu[block['toggle']['rich_text'][0]['text']['content']] = block['id']


education_page_id = '6729396821bd49418f1c49c4c9f563bc'
get_notion_page(education_page_id, EDUCATION_MENU)
job_page_id = 'c45c8570f69642d781c05ba275f398d1'
get_notion_page(job_page_id, JOB_MENU)
# print(EDUCATION_MENU)
