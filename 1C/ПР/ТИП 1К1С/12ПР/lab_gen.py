from random import randint


class Lab:
    @staticmethod
    def random_coord(N, M):
        return (randint(0, N - 1), randint(0, M - 1))

    @staticmethod
    def set_random_point(lab, sign):
        [y, x] = Lab.random_coord(len(lab), len(lab[0]))
        while lab[y][x] == 0:
            [y, x] = Lab.random_coord(len(lab), len(lab[0]))
        lab[y][x] = sign
        return lab

    @staticmethod
    def generate_multiple_points(lab, points_count, sign):
        for i in range(points_count):
            [y, x] = Lab.random_coord(len(lab), len(lab[0]))
            while lab[y][x] == 1:
                [y, x] = Lab.random_coord(len(lab), len(lab[0]))
            lab[y][x] = sign
        return lab

    def __init__(self, cols, rows, walls, pdf_files):
        self.lab = [[0 for _ in range(cols)] for _ in range(rows)]
        self.lab = Lab.generate_multiple_points(self.lab, walls, 1)
        self.lab = Lab.generate_multiple_points(self.lab, pdf_files, "P")
        self.lab[0][0] = "S"
        self.lab[rows - 1][cols - 1] = "E"

    def print(self):
        for line in self.lab:
            print(line)
