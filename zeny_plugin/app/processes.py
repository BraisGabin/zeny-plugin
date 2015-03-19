import re

from django.conf import settings


def get_no_merchantable_item_ids():
    try:
        with open(settings.PATH_ITEM_TRADE_TXT) as f:
            lines = f.readlines()
    except IOError as e:
        if settings.PATH_ITEM_TRADE_TXT == './item_trade.txt':
            raise TypeError("Did you set PATH_ITEM_TRADE_TXT in the settings.py?")
        else:
            raise e
    return get_item_ids(lines)


def get_item_ids(lines):
    pattern = re.compile('^([0-9]+),([0-9]+),([0-9]+)')
    l = set()
    for line in lines:
        match = pattern.match(line)
        if match:
            flags = int(match.group(2))
            if not is_merchantable(flags):
                l.add(int(match.group(1)))
    return l


def is_merchantable(flags):
    return not ((flags & 32) == 0 and (flags & 2) != 0)
