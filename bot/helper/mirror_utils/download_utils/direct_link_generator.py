# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Helper Module containing various sites direct links generators. This module is copied and modified as per need
from https://github.com/AvinashReddy3108/PaperplaneExtended . I hereby take no credit of the following code other
than the modifications. See https://github.com/AvinashReddy3108/PaperplaneExtended/commits/master/userbot/modules/direct_links.py
for original authorship. """

from bot import ALLDEBRID_AGENT, ALLDEBRID_APIKEY
from json import loads as jsnloads, decoder as jsndecoder
from re import search as re_search, compile as re_compile, findall as re_findall, sub as re_sub
from urllib.parse import urlparse, unquote
from os import popen
from random import choice
from time import sleep
from logging import error as log_error, info as log_info

import requests
from requests import get as rget, post as rpost, Session as rSession, exceptions as rexceptions
from bs4 import BeautifulSoup
from hashlib import md5 as hmd5
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


from bot.helper.ext_utils.exceptions import DirectDownloadLinkException


def direct_link_generator(link: str):
    """ direct links generator """
    regexp = re_compile(r'^https?:\/\/.*(\.torrent|\/torrent|\/jav\.php|nanobytes\.org|jackett_apikey|atercache|libertycorp\.org).*')
    if not link:
        raise DirectDownloadLinkException("`No links found!`")
    elif 'zippyshare.com' in link:
        return zippy_share(link)
    elif 'yadi.sk' in link:
        return yandex_disk(link)
    elif 'cloud.mail.ru' in link:
        return cm_ru(link)
    elif 'mediafire.com' in link:
        return mediafire(link)
    elif 'osdn.net' in link:
        return osdn(link)
    elif 'github.com' in link:
        return github(link)
    elif regexp.search(link):
        return torDl(link)
    else:
        raise DirectDownloadLinkException(f'No Direct link function found for {link}')


def zippy_share(url: str) -> str:
    """ ZippyShare direct links generator
    Based on https://github.com/LameLemon/ziggy"""
    dl_url = ''
    try:
        link = re_findall(r'\bhttps?://.*zippyshare\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No ZippyShare links found`\n")
    session = rSession()
    base_url = re_search('http.+.com', link).group()
    response = session.get(link)
    page_soup = BeautifulSoup(response.content, "lxml")
    scripts = page_soup.find_all("script", {"type": "text/javascript"})
    for script in scripts:
        if "getElementById('dlbutton')" in script.text:
            url_raw = re_search(r'= (?P<url>\".+\" \+ (?P<math>\(.+\)) .+);',
                                script.text).group('url')
            math = re_search(r'= (?P<url>\".+\" \+ (?P<math>\(.+\)) .+);',
                             script.text).group('math')
            dl_url = url_raw.replace(math, '"' + str(eval(math)) + '"')
            break
    dl_url = base_url + eval(dl_url)
    name = unquote(dl_url.split('/')[-1])
    return dl_url


def yandex_disk(url: str) -> str:
    """ Yandex.Disk direct links generator
    Based on https://github.com/wldhx/yadisk-direct"""
    try:
        link = re_findall(r'\bhttps?://.*yadi\.sk\S+', url)[0]
    except IndexError:
        reply = "`No Yandex.Disk links found`\n"
        return reply
    api = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}'
    try:
        dl_url = rget(api.format(link)).json()['href']
        return dl_url
    except KeyError:
        raise DirectDownloadLinkException("`Error: File not found / Download limit reached`\n")


def cm_ru(url: str) -> str:
    """ cloud.mail.ru direct links generator
    Using https://github.com/JrMasterModelBuilder/cmrudl.py"""
    reply = ''
    try:
        link = re_findall(r'\bhttps?://.*cloud\.mail\.ru\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No cloud.mail.ru links found`\n")
    command = f'vendor/cmrudl.py/cmrudl -s {link}'
    result = popen(command).read()
    result = result.splitlines()[-1]
    try:
        data = jsnloads(result)
    except jsndecoder.JSONDecodeError:
        raise DirectDownloadLinkException("`Error: Can't extract the link`\n")
    dl_url = data['download']
    return dl_url


def mediafire(url: str) -> str:
    """ MediaFire direct links generator """
    try:
        link = re_findall(r'\bhttps?://.*mediafire\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No MediaFire links found`\n")
    page = BeautifulSoup(rget(link).content, 'lxml')
    info = page.find('a', {'aria-label': 'Download file'})
    dl_url = info.get('href')
    return dl_url


def osdn(url: str) -> str:
    """ OSDN direct links generator """
    osdn_link = 'https://osdn.net'
    try:
        link = re_findall(r'\bhttps?://.*osdn\.net\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No OSDN links found`\n")
    page = BeautifulSoup(
        rget(link, allow_redirects=True).content, 'lxml')
    info = page.find('a', {'class': 'mirror_link'})
    link = unquote(osdn_link + info['href'])
    mirrors = page.find('form', {'id': 'mirror-select-form'}).findAll('tr')
    urls = []
    for data in mirrors[1:]:
        mirror = data.find('input')['value']
        urls.append(re_sub(r'm=(.*)&f', f'm={mirror}&f', link))
    return urls[0]


def github(url: str) -> str:
    """ GitHub direct links generator """
    try:
        re_findall(r'\bhttps?://.*github\.com.*releases\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No GitHub Releases links found`\n")
    download = rget(url, stream=True, allow_redirects=False)
    try:
        dl_url = download.headers["location"]
        return dl_url
    except KeyError:
        raise DirectDownloadLinkException("`Error: Can't extract the link`\n")


def torDl(url: str) -> str:
    fil = url.split("/")[-1]
    file = computeMD5hash(fil)
    dl_url = f"/tmp/{file}.torrent"
    yts = re_compile(r'^https?:\/\/.*(yts).*(torrent\/download).*')
    tgx = re_compile(r'^https?:\/\/.*(watercache).*(get).*')
    if "jackett_apikey" in url:
        try:
            r = rget(url)
        except rexceptions.InvalidSchema as e:
            return str(e).split("'")[1]
    elif yts.search(url):
        return url
    elif tgx.search(url):
        return url
    else:
        r = rget(url)

    open(dl_url, 'wb').write(r.content)
    log_info(f"Torrent dir {dl_url}")
    return dl_url

def computeMD5hash(my_string):
    m = hmd5()
    m.update(my_string.encode('utf-8'))
    return m.hexdigest()


def useragent():
    """
    useragent random setter
    """
    useragents = BeautifulSoup(
        rget(
            'https://developers.whatismybrowser.com/'
            'useragents/explore/operating_system_name/android/').content,
        'lxml').findAll('td', {'class': 'useragent'})
    user_agent = choice(useragents)
    return user_agent.text
