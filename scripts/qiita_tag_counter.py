#!/usr/bin/env python

import argparse
import json
import os
import urllib
from collections import Counter
from datetime import date

import requests
import pandas


class _REST(object):
    BASE_URL = 'https://qiita.com'

    def __init__(self, headers: dict, **kwargs):
        self.queries = {}
        self.headers = headers
        self.base_url = self.BASE_URL.format(**kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def set_query(self, queries: dict):
        self.queries.update(queries)
        return self

    def get(self, _id) -> dict:
        url = self.base_url
        if self.queries:
            url = '?'.join([url, urllib.parse.urlencode(self.queries)])
        url = '/'.join([url, _id])
        response = requests.get(url, headers=self.headers)
        return json.loads(response.text)

    def list(self) -> dict:
        url = self.base_url
        if self.queries:
            url = '?'.join([url, urllib.parse.urlencode(self.queries)])
        response = requests.get(url, headers=self.headers)
        return json.loads(response.text)


class Items(_REST):
    BASE_URL = 'https://qiita.com/api/v2/users/{user_id}/items'


class Users(_REST):
    BASE_URL = 'https://qiita.com/api/v2/users'


def _args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-u', dest='user', default='itkr')
    return parser.parse_args()


def _get_or_create_items(user_id):
    # ファイルから
    output_path = './output/likes_{}.json'.format(date.today().strftime('%Y-%m-%d'))
    if os.path.exists(output_path):
        return pandas.read_json(output_path)

    # APIから
    headers = {}
    items_count = Users(headers).get(user_id)['items_count']
    items = Items(headers, user_id=user_id).set_query({'page': 1, 'per_page': items_count}).list()
    tags = {
        'name': [],
        'likes_count': [],
    }
    for item in items:
        for tag in item['tags']:
            tags['name'].append(tag['name'])
            tags['likes_count'].append(int(item['likes_count']))
    df = pandas.DataFrame.from_dict(tags)

    # 保存
    df.to_json(output_path)
    return df


def _print_tags(user_id):
    df = _get_or_create_items(user_id)
    group = df.groupby('name')
    print(group.count().sort_values(by=['likes_count', 'name'], ascending=[False, False]))


def _print_tag_contributes(user_id):
    df = _get_or_create_items(user_id)
    group = df.groupby('name')
    print(group.sum().sort_values(by=['likes_count', 'name'], ascending=[False, False]))


def main():
    # TODO: pandas
    args = _args()
    print('--')
    _print_tags(args.user)
    print('--')
    _print_tag_contributes(args.user)
    print('--')


if __name__ == '__main__':
    main()
