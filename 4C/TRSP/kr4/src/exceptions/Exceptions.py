class CustomExceptionA(Exception):
    def __init__(self, name: str) -> None:
        self.name: str = name


class CustomExceptionB(Exception):
    def __init__(self, resource_id: int) -> None:
        self.resource_id: int = resource_id
