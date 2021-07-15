import re
from enum import Enum

SEARCH_REGEX = re.compile(
    r"<PRE class = \"textsearch\" style = \"text-align: left\">Title: <b>(?P<title>[a-z,. ]+)</b> Page: <b>\d{1,3}</b><br>Location: <a class = \"intext\" style = \"cursor:pointer\" onclick = \"postform\('(?P<hexagon>[a-z0-9]+)','(?P<wall>[1-4])','(?P<shelf>[1-5])','(?P<volume>\d{2})','(?P<page>\d{1,3}).+</PRE>"
)

class SearchMethod(Enum):
    EXACT = 'e'
    WITH_RANDOM_CHARACTERS = 'c'
    WITH_RANDOM_WORDS = 'w'
    TITLE = 't'