class Piece:
    source: str
    start: int
    length: int

    def __init__(self, source, start, length):
        self.source = source
        self.start = start
        self.length = length


class PieceTable:
    pieces: Piece = []
    original: str

    def __init__(self, filename: str):
        self.original = open(filename).read()
        self.pieces.append(Piece("original", 0, len(self.original)))

    def append(self, t: str, pos: int):
        self.pieces.append(Piece("append", pos, len(t)))


T = PieceTable()
