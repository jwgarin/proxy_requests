"""
This module provides utility functions for chrome driver

Available functions:
- update_chromedriver: downloads and update chromedriver in the working folder
- get_chromedriver: initiate a driver instance
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
import shutil
from zipfile import ZipFile
from selenium.common.exceptions import TimeoutException
import logging
import os
import requests
from bs4 import BeautifulSoup
import re
import random
import zipfile
import platform
import argparse
#import undetected_chromedriver as uc
import sys
import platform
if platform.system() == 'Windows':
    import chromedriver_binary


update = None
logging.basicConfig(level=logging.INFO, format=" %(asctime)s - %(levelname)s - %(message)s ")


def update_chromedriver():
    logging.info('downloading latest chromedriver')
    os.makedirs('cache', exist_ok=True)
    headers = {
        'authority': 'chromedriver.storage.googleapis.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.6',
        'referer': 'https://chromedriver.storage.googleapis.com/index.html?path=109.0.5414.74/',
        'sec-ch-ua': '"Not_A Brand";v="99", "Brave";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }
    r = requests.get('https://chromedriver.chromium.org/downloads')
    s = BeautifulSoup(r.text, 'html.parser')
    #latest_stable_release = s.find(string='stable').find_parent('p').find('a')['href']
    latest_stable_release = s.find(string=re.compile('ChromeDriver 1')).find_parent('a')['href']
    version = re.search(r'(\d+.)*\d+', latest_stable_release).group()
    r = requests.get('https://chromedriver.storage.googleapis.com/?delimiter=/&prefix={}/'.format(version), headers=headers)
    xmlfile = '{}\\chromedrivers.xml'.format('cache')
    with open(xmlfile, 'wb') as f:
        f.write(r.content)
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    chromedriver_link = urljoin('https://chromedriver.storage.googleapis.com/', [el for el in [el for el in root if len(el) > 0] if ('win32' in el[0].text and platform.system() == 'Windows') or ('linux64' in el[0].text and platform.system() == "Linux")][0][0].text)
    os.makedirs(os.path.join('chromedrivers', version), exist_ok=True)
    chrome_dir = os.path.join('chromedrivers', version, 'chromedriver.zip')
    r = requests.get(chromedriver_link)
    with open(chrome_dir, 'wb') as f:
        f.write(r.content)
    with ZipFile(chrome_dir, 'r') as zip_ref:
        zip_ref.extractall(os.getcwd())
    logging.info('download complete')


def get_chromedriver(use_proxy=False, user_agent=None, headless=False):
    #chrome_options = webdriver.ChromeOptions()
    options = Options()
    if use_proxy:
        with open('proxies.txt') as f:
            proxy_list = f.read().splitlines()
        proxy = random.choice(proxy_list)
        parts = proxy.replace('http:', '').replace('//', '').replace('@', ':').split(':')
        if len(parts) == 4:
            ip = parts[2]
            port = parts[3]
            username = parts[0]
            password = parts[1]
        else:
            ip = parts[0]
            port = parts[1]
            username = ''
            password = ''
        PROXY_HOST = ip  # rotating proxy or host
        PROXY_PORT = port  # port
        PROXY_USER = username  # username
        PROXY_PASS = password  # password
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """
        background_js = """
            var config = {
                    mode: "fixed_servers",
                    rules: {
                    singleProxy: {
                        scheme: "http",
                        host: "%s",
                        port: parseInt(%s)
                    },
                    bypassList: ["localhost"]
                    }
                };
    
            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    
            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "%s",
                        password: "%s"
                    }
                };
            }
    
            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
            );
            """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        options.add_extension(pluginfile)
    path = os.path.dirname(os.path.abspath(__file__))
    if user_agent:
        #chrome_options.add_argument('--user-agent=%s' % user_agent)
        options.add_argument('--user-agent=%s' % user_agent)
    #options.headless = headless
    if headless:
        options.add_argument('--headless')
    chrome_driver = 'chromedriver.exe' if platform.system() == 'Windows' else 'chromedriver'
    chrome_dir = os.path.join(path, chrome_driver)
    if float(sys.version_info[0] + sys.version_info[1]/10) <= 3.7:
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(executable_path='/cse/runtime/node_modules/chromedriver/lib/chromedriver/chromedriver', options=options)
    else:
        driver = webdriver.Chrome(executable_path=chromedriver_binary.chromedriver_filename, options=options)
    return driver


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Chromedriver')
    parser.add_argument('--update', action='store_true', default=False, dest="update")
    args = parser.parse_args()
    update = args.update
    if update:
        update_chromedriver()
    else:
        pass
