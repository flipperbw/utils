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

LAST_REQUEST = None

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)


# - Soup

CLEAN_TAGS = ('head', 'script', 'link', 'style', 'noscript', 'meta', 'iframe')
EXTRA_TAGS = ('img',)


def get_req(url: str, delay: float = 0.5):
    global LAST_REQUEST

    if not LAST_REQUEST:
        sleep_time = 0
    else:
        curr_time = time()
        sdiff = curr_time - LAST_REQUEST
        sleep_time = delay - sdiff

    if sleep_time > 0:
        sleep(sleep_time)

    req = SESSION.get(url)

    #todo handle non 200s

    LAST_REQUEST = time()

    return req

def get_txt(url: str, delay: float = 0.5):
    return get_req(url, delay).text


def make_strainer(el: str, d: dict):
    return SoupStrainer(el, d)


def clean_soup(
        soup: BeautifulSoup,
        tags: Iterable[str] = CLEAN_TAGS,
        extra_tags: Iterable[str] = EXTRA_TAGS,
        remove_imgs: bool = True,
        remove_comments: bool = True,
        *_args, **_kwargs
):
    tags = list(tags)
    extra_tags = list(extra_tags)
    if not remove_imgs and 'img' in extra_tags:
        extra_tags.remove('img')
    if extra_tags:
        tags += list(extra_tags)

    for tag in soup(tags):  # type: Tag
        tag.decompose()

    if remove_comments:
        for com in soup.find_all(string=lambda t: isinstance(t, (Comment, CData, ProcessingInstruction, Doctype))):  # type: Tag
            com.extract()

    return soup


def get_soup(txt: str, clean: bool = True, strainer: SoupStrainer = None, *args, **kwargs):
    if strainer:
        soup = BeautifulSoup(txt, 'lxml', parse_only=strainer)
    else:
        soup = BeautifulSoup(txt, 'lxml')

    if clean:
        soup = clean_soup(soup, *args, **kwargs)

    return soup


def get_and_clean(url: str, *args, **kwargs):
    return get_soup(get_txt(url), *args, **kwargs)
