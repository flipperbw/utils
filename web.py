import requests
from time import sleep, time
from typing import Iterable

# noinspection PyProtectedMember
from bs4 import (
    BeautifulSoup, SoupStrainer,
    Tag,
    Comment, CData, ProcessingInstruction, Doctype
)

# - Requests

SLEEP_DELAY = 0.5

LAST_REQUEST = None

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36',
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)


# - Soup

CLEAN_TAGS = ('head', 'script', 'link', 'style', 'noscript', 'meta', 'iframe')
EXTRA_TAGS = ('img',)


def get_txt(href: str, delay: float = SLEEP_DELAY):
    global LAST_REQUEST

    if not LAST_REQUEST:
        sleep_time = 0
    else:
        curr_time = time()
        sdiff = curr_time - LAST_REQUEST
        sleep_time = delay - sdiff

    if sleep_time > 0:
        sleep(sleep_time)

    txt = SESSION.get(href).text

    #todo handle non 200s

    LAST_REQUEST = time()

    return txt


def make_strainer(el: str, d: dict):
    return SoupStrainer(el, d)


def clean_soup(soup: BeautifulSoup, tags: Iterable[str] = CLEAN_TAGS, extra_tags: Iterable[str] = EXTRA_TAGS, remove_comments: bool = True):
    tags = list(tags)
    if extra_tags:
        tags += list(extra_tags)

    for tag in soup(tags):  # type: Tag
        tag.decompose()

    if remove_comments:
        for com in soup.find_all(string=lambda t: isinstance(t, (Comment, CData, ProcessingInstruction, Doctype))):  # type: Tag
            com.decompose()

    return soup


def get_soup(txt: str, clean: bool = True, strainer: SoupStrainer = None):
    if strainer:
        soup = BeautifulSoup(txt, 'lxml', parse_only=strainer)
    else:
        soup = BeautifulSoup(txt, 'lxml')

    if clean:
        soup = clean_soup(soup)

    return soup
