import logging
import requests
from jsonpath_rw import jsonpath, parse

from .constants import BASE_URL, BATCH_SIZE, LEAGUE, ITEM

def fetch_item_ids(user, league, item):
    url = f'{BASE_URL}/search/{league}'
    params = {
        'query': {
            'type': item,
            'filters': {
                'trade_filters': {
                    'filters': {
                        'account': {
                            'input': user
                        }
                    },
                    'disabled': False
                }
            }
        },
        'sort': {
            'price': 'asc'
        }
    }
    response = requests.post(url, json=params)
    json = response.json()
    result = {
        'ids': json['result'],
        'query': json['id'],
        'count': json['total']
    }
    return result


def fetch_items_batch(ids, query):
    url = f'{BASE_URL}/fetch/' + ','.join(ids)
    params = { 'query': query }
    response = requests.get(url, params=params)
    json = response.json()
    json_path = parse('$.result[*].listing.price')
    result = [match.value for match in json_path.find(json) if match.value]
    return result


def fetch_items(ids, query, count):
    batch_size = BATCH_SIZE
    items = []
    for i in range(0, count, batch_size):
        ids_batch = ids[i:i+batch_size]
        items_batch = fetch_items_batch(ids_batch, query)
        items.extend(items_batch)
        logging.info(f'fetched {len(ids_batch)} items')
    return items


def fetch(user, league=LEAGUE, item=ITEM, **kwargs):
    data = fetch_item_ids(user, league, item)
    count = data['count']
    logging.info(f'fetched {count} item ids')
    items = fetch_items(**data)
    return items
