#!/usr/bin/env python

import argparse
import json
import os
import re
import sys

try:
    from urllib.request import Request, urlopen, urlretrieve
except ImportError:
    from urllib import urlretrieve
    from urllib2 import Request, urlopen


class RedditScrape(object):
    PROFILE_URL = 'https://www.reddit.com/user/{}/submitted.json'

    def __init__(self, username, directory, dry_run):
        self.username = username
        self.directory = directory
        self.dry_run = dry_run

    def scrape(self):
        user_url = self.PROFILE_URL.format(self.username)

        count = 0

        while True:
            req = Request(user_url)
            req.add_header('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0')
            response = urlopen(req)
            payload = json.loads(response.read())

            posts = payload['data']['children']

            for post in posts:
                url = post['data']['url']
                if re.search('(jpg|jpeg|png|gif)', url):
                    filename = re.match('https://i.redd.it\/(\w+\.\w+)', url)
                    if not filename:
                        # Old imgur links
                        filename = re.match('http://i.imgur.com\/(\w+\.\w+)', url)
                    try:
                        filename = filename.group(1)
                    except AttributeError:
                        # Unknown url format
                        continue

                    if not self.dry_run:
                        urlretrieve(url, os.path.join(self.directory, filename))

                    sys.stdout.write('.')
                    sys.stdout.flush()
                    count += 1

            if payload['data']['after']:
                user_url = self.PROFILE_URL.format(self.username) + '?after={}'.format(payload['data']['after'])
            else:
                break

        sys.stdout.write('\n')
        print('{} saved.'.format(count))

def main():
    parser = argparse.ArgumentParser(description="Reddit simple media scraper.")
    parser.add_argument('username', type=str)
    parser.add_argument('directory', nargs='?', default=os.path.dirname(os.path.realpath(__file__)))
    parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                        default=False, help='Dry run')
    args = parser.parse_args()

    scraper = RedditScrape(args.username, args.directory, args.dry_run)
    scraper.scrape()


if __name__ == '__main__':
    main()
