import re
from search import SEARCH_REGEX, SearchMethod
import requests
from route import Route
from elements import Book, Hexagon


__all__ = (
    'LibOfBabel',
    'client',
    'from_session'
)


class LibOfBabel:
    def __init__(self, session: requests.Session = None) -> None:
        self.session = session
        if session is None:
            self.session = requests.session()
        self._last_state = None

    @property
    def random_book(self) -> Book:
        with Route('GET', '/random.cgi', self.session, allow_redirects = False) as route:
            state = route.headers
        state['__session'] = self.session
        self._last_state = state
        return Book._from_state(state)
    
    def get_hexagon(self, hex: str) -> Hexagon:
        data = {
            'hex': hex,
            'session': self.session
        }
        return Hexagon(data)
    
    def get_book(self, hex: str, wall: int, shelf: int, volume: int, page: int = 1) -> Book:
        data = {
            'hex': hex,
            'wall': wall,
            'shelf': shelf,
            'volume': volume,
            'page': page,
            'session': self.session
        }
        return Book(data)

    def search(self, find: str, method: SearchMethod = SearchMethod.EXACT, length: int = 20):
        data = {
            'find': find,
            'method': method.value,
            'content-length': length
        }
        with Route('POST', '/search.cgi', self.session, data = data) as route:
            for match in re.finditer(SEARCH_REGEX, route.text):
                data = {
                    'hex': match.group('hexagon'),
                    'wall': match.group('wall'),
                    'shelf': match.group('shelf'),
                    'volume': match.group('volume'),
                    'page': match.group('page'),
                    'session': self.session
                }
                yield Book(data)


def client() -> LibOfBabel:
    return LibOfBabel()

def from_session(session: requests.Session) -> LibOfBabel:
    return LibOfBabel(session)
