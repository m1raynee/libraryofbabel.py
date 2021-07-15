import requests

PATH = 'https://libraryofbabel.info'
class Route:
    def __init__(self, method: str, path: str, session: requests.Session, **kwargs) -> None:
        self._original_path = path
        self.method = method
        self.kwargs = kwargs
        self.session = session

    @property
    def path(self) -> str:
        return f'{PATH}{self._original_path}'
    @path.setter
    def path_s(self, value: str):
        self._original_path = value

    def __enter__(self) -> requests.Response:
        self.response: requests.Response = self.session.request(self.method, self.path, **self.kwargs)
        return self.response

    def __exit__(self, *_):
        self.response.close()