import datetime
import os
import time

import requests


ES_BASE_URL = "{}://{}:{}".format(
    os.environ.get('ELASTICSEARCH_PROTOCOL', 'http'),
    os.environ.get('ELASTICSEARCH_HOST', 'esdata'),
    os.environ.get('ELASTICSEARCH_PORT', 9200)
)

TTL_DAYS = int(os.environ.get('TTL_DAYS', 14))

INDEX_PATTERN = os.environ.get('INDEX_PATTERN', 'logstash-%Y.%m.%d')

LOOP_ENABLED = bool(int(os.environ.get('LOOP_ENABLED', True)))

SLEEP_BETWEEN = int(os.environ.get('SLEEP_BETWEEN', 86400))

MIN_SLEEP = int(os.environ.get('MIN_SLEEP', 3600))


def main():
    while True:
        for index in filter(is_logstash_index, get_indices(ES_BASE_URL)):
            print(index, ':', get_date_part(index), is_date_older_then(index, TTL_DAYS) and 'is older' or 'is not older')
            if is_date_older_then(index, TTL_DAYS):
                delete_index(ES_BASE_URL, index)
        if not LOOP_ENABLED:
            break
        time.sleep(max(SLEEP_BETWEEN, MIN_SLEEP))

def delete_index(baseurl, index):
    result = requests.delete("{}/{}".format(baseurl, index))
    if result.status_code == 200:
        print('Index "{}" deleted'.format(index))
    else:
        print('Got status code: {}'.format(result.status_code))

def get_indices(baseurl):
    result = requests.get("{}/{}".format(baseurl, '*'))
    return result.json().keys()

def is_logstash_index(name):
    return name.startswith('logstash-')

def get_date_part(name):
    return name.split('-')[-1]

def is_date_older_then(date, days):
    check = datetime.datetime.strptime(date, INDEX_PATTERN).date()
    then = datetime.date.today() - datetime.timedelta(days)
    return check < then


if __name__ == "__main__":
    main()
