import pygame
from pygame.locals import *
import sys
import random
from copy import deepcopy

ANDROID_SCALE = 2
CELL_SIZE = 20
CELL = (CELL_SIZE, CELL_SIZE)
DISPLAY_WIDTH = 360
DISPLAY_HEIGHT = 640
DISPLAY = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
OFFSET = (10, 30)
SHAPES = [['0000', '1111', '0000', '0000'], ['11', '11'],
          ['010', '111', '000'], ['110', '011', '000'],
          ['011', '110', '000'], ['100', '111', '000'],
          ['001', '111', '000']]

GLASS_WIDTH = 10
GLASS_HEIGHT = 20

LINE_WIDTH = 2
GLASS_UL = (OFFSET[0] - LINE_WIDTH, OFFSET[1])
GLASS_LR = (OFFSET[0] + GLASS_WIDTH * CELL_SIZE,
            OFFSET[1] + GLASS_HEIGHT * CELL_SIZE)

DROP_SPEED = 25

COLORS = [pygame.Color(255, 0, 255), pygame.Color(0, 255, 0), pygame.Color(255, 255, 0)]
WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)
BLACKEN = pygame.Color(5, 5, 5)

timer = pygame.time.Clock()


def fill_color(img, from_color, to_color):
    for x in range(img.get_size()[0]):
        for y in range(img.get_size()[1]):
            if img.get_at([x, y]) == from_color:
                img.set_at([x, y], to_color)
    return img


def load_image(color):
    image = pygame.image.load('resourse\\tile.png')
    image = fill_color(image, WHITE, color)
    image = fill_color(image, BLACK, color // BLACKEN)
    return image


IMAGES = {c: load_image(COLORS[c]) for c in range(len(COLORS))}


class Cell(object):
    """Contains single cell"""

    def __init__(self, full=False, color=0, x=0, y=0):
        self._full = full
        self._color = color
        self._x = x
        self._y = y
        self._image = IMAGES[color]

    def is_full(self):
        return self._full

    def color(self):
        return self._color

    def get_xy(self):
        return (self._x, self._y)

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def set_color(self, color):
        self._color = color
        self._image = self._load_image()

    def set_full(self, full):
        self._full = full

    def set_xy(self, x, y):
        self._x = x
        self._y = y

    def move(self, x, y):
        self._x += x
        self._y += y

    def draw(self, screen, off):
        x = ((self._x + off[0]) * CELL_SIZE) + OFFSET[0]
        y = ((self._y + off[1]) * CELL_SIZE) + OFFSET[1]
        screen.blit(self._image, (x, y))

    def __add__(self, delta):
        return Cell(self._full, self._color, self._x + delta[0], self._y + delta[1])

    def __deepcopy__(self, memo):
        return Cell(self._full, self._color, self._x, self._y)

    def __str__(self):
        return 'X:{}, Y:{}, color:{}, full:{}'.format(self._x, self._y, COLORS[self._color], self._full)


class CellArray(object):
    """Contains array of cells"""

    def __init__(self, x=0, y=0, cells=None):
        self._x = x
        self._y = y
        self._arr = []
        self._inner_array = [[None]]
        self._len = 0
        if cells:
            for c in cells:
                self.add(c)

    def get_array(self):
        return self._arr

    def get_xy(self):
        return (self._x, self._y)

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def add(self, cell):
        self._arr.append(cell)

    def draw(self, screen):
        for c in self._arr:
            c.draw(screen, (self._x, self._y))

    def set_xy(self, x, y):
        self._x = x
        self._y = y

    def __contains__(self, c_array):
        for in_c in self.get_array():
            if isinstance(c_array, CellArray):
                for c in c_array.get_array():
                    if in_c.get_xy() == c.get_xy():
                        return True
            elif isinstance(c_array, Cell):
                if in_c.get_xy() == c_array.get_xy():
                    return True
        return False

    def __repr__(self):
        return '\n'.join(str(c) for c in self._arr)


class Figure(CellArray):
    """Contains current figure"""

    def __init__(self, x, y, shape, color, rotation=0):
        self._color = color
        self._rotation = rotation
        super(Figure, self).__init__(x, y)
        self._shape = shape
        for y, line in enumerate(SHAPES[self._shape]):
            for x, c in enumerate(line):
                if SHAPES[self._shape][y][x] == '1':
                    self.add(Cell(True, self._color, x, y), x, y)
        for r in range(self._rotation):
            self.rotate(check=False)

    def move(self, x, y, glass):
        if self.available(x, y, glass):
            self._x += x
            self._y += y
            self.set_xy(self._x, self._y)
            return True
        else:
            return False

    def available(self, x=0, y=0, glass=None):
        for c in self.get_array():
            if (c.get_x() + self._x + x) not in range(GLASS_WIDTH):
                return False
            if (c.get_y() + self._y + y) not in range(GLASS_HEIGHT):
                return False
            if glass and c + (x + self._x, y + self._y) in glass:
                return False
        return True

    def rotate(self, glass=None, check=True):
        temp_array = deepcopy(self._inner_array)
        temp_array = [s[::-1] for s in zip(*temp_array)]
        for y, line in enumerate(temp_array):
            for x, c in enumerate(line):
                if c:
                    c.set_xy(x, y)
        for y, line in enumerate(temp_array):
            for x, c in enumerate(line):
                if c:
                    if check and (c.get_x() + self._x) not in range(GLASS_WIDTH):
                        return False
                    if check and (c.get_y() + self._y) not in range(GLASS_HEIGHT):
                        return False
                    if glass:
                        if c + (self._x, self._y) in glass:
                            return False
        self._inner_array = [s[::-1] for s in zip(*self._inner_array)]
        for y, line in enumerate(self._inner_array):
            for x, c in enumerate(line):
                if c:
                    c.set_xy(x, y)
        return True

    def add(self, cell, x, y):
        super(Figure, self).add(cell)
        self._len = max(self._len, x, y)
        self._update_inner(self._len)
        self._inner_array[y][x] = cell

    def _update_inner(self, len_):
        if len_ > 0:
            for y in range(len(self._inner_array)):
                for x in range(len_ - len(self._inner_array[y]) + 1):
                    self._inner_array[y].append(None)
            for y in range(len_ - len(self._inner_array) + 1):
                self._inner_array.append([None for x in range(len_ + 1)])

    def __str__(self):
        return '\n'.join(' '.join(str(c) for c in line) for line in self._inner_array)


class Glass(CellArray):
    """Contains main game glass"""

    def __init__(self):
        super(Glass, self).__init__()

    def put_cells(self, figure):
        if figure in self.get_array():
            return False
        else:
            for c in figure.get_array():
                c.set_xy(figure.get_x() + c.get_x(), figure.get_y() + c.get_y())
                self.add(c)
            return True

    def remove_line(self, line):
        temp_arr = []
        for c in self.get_array():
            if c.get_y() == line:
                temp_arr.append(c)
        for c in temp_arr:
            self._arr.remove(c)
        for c in self.get_array():
            if c.get_y() < line:
                c.set_xy(c.get_x(), c.get_y() + 1)

    def __str__(self):
        return '\n'.join(str(c) for c in self._arr)


class Game(object):
    """Main game class"""

    def __init__(self):
        pygame.init()
        self.glass = Glass()
        pygame.display.set_caption('Simple tetris')
        pygame.display.set_icon(IMAGES[random.choice(range(len(COLORS)))])
        self.screen = pygame.display.set_mode(DISPLAY, HWPALETTE, 8)
        self.bg = pygame.Surface(DISPLAY)
        self.bg.fill(Color('black'))
        self.figure = self.gen_figure()
        self.next_figure = self.gen_figure(11, 5)
        self._drop_count = 0
        self.score = 0
        self.score_font = pygame.font.Font('Anonymous Pro.ttf', 30)
        self.next_fig_font = pygame.font.Font('Anonymous Pro.ttf', 20)
        self.game_over_font = pygame.font.Font('Anonymous Pro.ttf', 60)
        self.run = True

    def draw(self):
        # Backgrownd
        self.screen.blit(self.bg, (0, 0))
        # Glass border
        pygame.draw.line(self.screen, WHITE, (GLASS_UL[0], GLASS_UL[1]), (GLASS_UL[0], GLASS_LR[1]), LINE_WIDTH)
        pygame.draw.line(self.screen, WHITE, (GLASS_LR[0], GLASS_LR[1]), (GLASS_UL[0], GLASS_LR[1]), LINE_WIDTH)
        pygame.draw.line(self.screen, WHITE, (GLASS_LR[0], GLASS_LR[1]), (GLASS_LR[0], GLASS_UL[1]), LINE_WIDTH)
        # Score
        label = self.score_font.render('Score:', 0, (255, 255, 255))
        score = self.score_font.render(str(self.score), 0, (255, 255, 255))
        self.screen.blit(label, (360, 100))
        self.screen.blit(score, (360, 130))
        # Glass
        self.glass.draw(self.screen)
        # Figure
        self.figure.draw(self.screen)
        # Next figure
        next_fig_label = self.next_fig_font.render('Next figure:', 0, (255, 255, 255))
        self.screen.blit(next_fig_label, (350, 185))
        self.next_figure.draw(self.screen)
        pygame.display.update()

    def gen_figure(self, x=4, y=0, shape=None, color=None, rotation=None):
        if shape is None:
            shape = random.choice(range(len(SHAPES)))
        if color is None:
            color = random.choice(range(len(COLORS)))
        if rotation is None:
            rotation = random.choice(range(4))
        return Figure(x, y, shape, color, rotation)

    def check_lines(self):
        lines = 0
        for line in range(GLASS_HEIGHT):
            if all(Cell(x=c, y=line) in self.glass for c in range(GLASS_WIDTH)):
                self.glass.remove_line(line)
                lines += 1
        return lines

    def update(self):
        if self.run:
            self._drop_count += 1
            if self._drop_count > DROP_SPEED:
                self.try_move_down()
        for e in pygame.event.get():
            if e.type == QUIT:
                sys.exit()
            if self.run:
                if e.type == KEYDOWN and e.key == K_LEFT:
                    self.figure.move(-1, 0, self.glass)
                if e.type == KEYDOWN and e.key == K_RIGHT:
                    self.figure.move(1, 0, self.glass)
                if e.type == KEYDOWN and e.key == K_UP:
                    self.figure.rotate(self.glass)
                if e.type == KEYDOWN and e.key == K_DOWN:
                    self.try_move_down()
                if e.type == KEYDOWN and e.key == K_SPACE:
                    while self.try_move_down():
                        self._drop_count = DROP_SPEED // 2

    def try_move_down(self):
        self._drop_count = 0
        if not self.figure.move(0, 1, self.glass):
            self.glass.put_cells(self.figure)
            self.score += 10
            lines = self.check_lines()
            self.score += (lines ** 2) * 100
            self.try_place_new()
            return False
        return True

    def try_place_new(self):
        self.figure = self.gen_figure(shape=self.next_figure._shape,
                                      color=self.next_figure._color,
                                      rotation=self.next_figure._rotation)
        if not self.figure.available(glass=self.glass):
            game_over = self.game_over_font.render('GAME OVER', 0, (255, 255, 255))
            self.screen.blit(game_over, (40, 300))
            pygame.display.update()
            self.run = False
        self.next_figure = self.gen_figure(11, 5)

    def start(self):
        while True:
            timer.tick(60)
            if self.run:
                self.draw()
            self.update()


if __name__ == '__main__':
    game = Game()
    game.start()
