import re
from typing import Generator, List, NamedTuple, Optional
from random import randint

import requests
from route import PATH, Route

__all__ = (
    'Book',
)

S = requests.Session

BOOK_REGEX = re.compile(
    r'(?P<path>https://libraryofbabel\.info/)'
    r'(?P<protocol>book\.cgi)\?(?P<hexagon>[a-z0-9]+)'
    r'-w(?P<wall>[1-4])-s(?P<shelf>[1-5])-v(?P<volume>\d{2}):(?P<page>\d{1,3})'
)
class StateTuple(NamedTuple):
    hexagon: str
    wall: Optional[int]
    shelf: Optional[int]
    volume: Optional[int]
    page: Optional[int]
    session: S

def zeroint(x: int):
    x = str(x)
    return x if len(x) > 1 else f'0{x}'

class Direct:
    @classmethod
    def _tuple_from_state(cls, state):
        match = re.match(BOOK_REGEX, state['Location'])
        groups = match.groupdict()

        hexagon: str = groups.get('hexagon')
        wall = int(groups.get('wall', None))
        shelf = int(groups.get('shelf', None))
        volume = int(groups.get('volume', None))
        page = int(groups.get('page', None))

        return StateTuple(hexagon, wall, shelf, volume, page, state['__session'])
    
    @classmethod
    def _from_tuple(cls, state: StateTuple):
        data = {
            'hex': state.hexagon,
            'wall': state.wall,
            'shelf': state.shelf,
            'volume': state.volume,
            'page': state.page,
            'session': state.session
        }
        return cls(data)
    
    @classmethod
    def _from_state(cls, state):
        groups = cls._tuple_from_state(state)
        inst = cls._from_tuple(groups)
        inst._match = groups
        return inst

class Hexagon(Direct):
    def __init__(self, data) -> None:
        self.hex: str = data.get('hex', '0')
        self._session: S = data.get('session')
        self._data = data
    
    @property
    def walls(self) -> Generator['Wall', None, None]:
        def _():
            for i in range(1, 4):
                data = self._data.copy()
                data['wall'] = i
                yield Wall(data)
        return _()
    
    def get_wall(self, index: int) -> 'Wall':
        data = self._data.copy()
        data['wall'] = index
        return Wall(data)

class Wall(Direct):
    def __init__(self, data) -> None:
        self.hexagon = Hexagon(data)
        self.index = data.get('wall', 1)
        self._data = data

    @property
    def shelfs(self) -> Generator['Shelf', None, None]:
        def _():
            for i in range(1, 5):
                data = self._data.copy()
                data['shelf'] = i
                yield Shelf(data)
        return _()
    
    def get_shelf(self, index: int) -> 'Shelf':
        data = self._data.copy()
        data['shelf'] = index
        return Shelf(data)

class Shelf(Direct):
    def __init__(self, data):
        self.wall = Wall(data)
        self.index = data.get('shelf', 1)
        self._data = data
    
    @property
    def books(self) -> Generator['Book', None, None]:
        def _():
            for i in range(1, 32):
                data = self._data.copy()
                data['volume'] = i
                yield Book(data)
        return _()
    
    def get_book(self, index: int) -> 'Book':
        data = self._data.copy()
        data['volume'] = index
        return Book(data)


class Book(Direct):
    def __init__(self, data) -> None:
        self.shelf = Shelf(data)
        self.index = data.get('volume')
        self.session = data.get('session')
        self.pages: List[str] = None
        self.current_page: int = int(data.get('page', 1))

        self._title = None
    
    @classmethod
    def _from_state(cls, state):
        inst = super()._from_state(state)

        inst.current_page = inst._match.page
        inst._state = state

        return inst
    
    @property
    def title(self) -> str:
        if self._title is None:
            with Route('GET', f'/book.cgi?{self.link}:1', self.session) as route:
                self._title = re.search(r'<TITLE>(?P<mark>[a-z., ]+) 1</TITLE>', route.text).group('mark')
        return self._title

    @property
    def link(self):
        return f'{self.shelf.wall.hexagon.hex}-w{self.shelf.wall.index}-s{self.shelf.index}-v{self.index}'

    
    def __eq__(self, o: object) -> bool:
        return isinstance(o, self) and (o.shelf == self.shelf and o.index == self.index)
    
    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)
    
    @property
    def content(self) -> str:
        if self.pages is None:
            data = {
                'hex': self.shelf.wall.hexagon.hex,
                'wall': str(self.shelf.wall.index),
                'shelf': str(self.shelf.index),
                'volume': zeroint(self.index),
                'title': self.title
            }
            with Route('POST', '/download.cgi', self.session, data = data) as route:
                self._raw_file = route.text
            self.pages = (self._raw_file
                .removeprefix(f'{self.title}\n\n')
                .removesuffix(f'\n\n\nBook Location:{self.link}')
                .split('\n\n')
            )
        return self.pages[self.current_page-1]

    def next_page(self, amount: int = 1) -> str:
        if not self.current_page + amount <= 410:
            raise ValueError(f'the next page ({self.current_page + amount}) does not exists')
        self.current_page += amount
        return self.content

    def previous_page(self, amount: int = 1) -> str:
        if not 1 <= self.current_page - amount:
            raise ValueError(f'the previous page ({self.current_page - amount}) does not exists')
        self.current_page -= amount
        return self.content
    
    def first_page(self) -> str:
        self.current_page = 1
        return self.content
    
    def first_page(self) -> str:
        self.current_page = 410
        return self.content
    
    def random_page(self) -> str:
        self.current_page = randint(1, 410)
        return self.content