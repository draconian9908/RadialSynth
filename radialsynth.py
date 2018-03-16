"""Created by Jane Sieving (jsieving) on 3/7/18.

Used code from AI & Algorithms Toolbox as base code for working with a grid-like
world in pygame.

This is the most recent working code for our radial synthesizer game. Currently
it can create a grid, draw and delete blocks on the grid, and change the block
type with user input. In progress is a Sweeper class which builds "rings" around
a chosen start square, reads all of the blocks in each ring, and plays sounds
depending on the blocks found, one ring at a time."""

import pygame
import time
import fluidsynth
from math import atan, pi

BLACK = (0, 0, 0)
DKGRAY = (25, 25, 25)
GRAY = (40, 40, 40)
LTGRAY = (100, 100, 100)
WHITE = (240, 240, 240)
YELLOW = (160, 160, 10)
RED = (160, 10, 10)
GREEN = (10, 160, 110)
BLUE = (60, 10, 160)

sound_list = ["sound_files/Drama Piano.sf2", \
                "sound_files/Stratocaster Light Overdrive.SF2", \
                "sound_files/Acoustic Guitar.sf2", \
                "sound_files/Energized.sf2"]

class Grid():
    """ A grid full of cells, where note blocks can be placed by the user
    to 'draw' music."""

    def __init__(self, width=24, height=24, cell_size=36):
        pygame.init()
        screen_size = (width*cell_size + 160, height*cell_size)
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption = ('RadialSynth')
        self.blocks = {}
        self.coords = (0, 0)
        self.width = width
        self.height = height
        self.dim = (width*cell_size, height*cell_size)
        self.cell_size = cell_size
        self._init_cells()
        self._init_buttons()
        self.shape = 'grid'

    def _draw_background(self):
        self.screen.fill(DKGRAY)

    def _init_cells(self):
        self.cells = {}
        for i in range(self.height):
            for j in range(self.width):
                cell_coord = (i*self.cell_size, j*self.cell_size)
                self.cells[(i, j)] = Cell(self.screen, cell_coord, self.cell_size)

    def _add_coords(self, a, b):
        x = (a[0]+b[0])
        y = (a[1]+b[1])
        return (x, y)

    def _init_buttons(self):
        self.buttons = {}
        button_size = (96, 36)
        coord0 = (self.width*self.cell_size + 32, 0 + 36)
        self.buttons['R'] = Button(self, RED, button_size, coord0)
        self.buttons['G'] = Button(self, GREEN, button_size, tuple(map(sum, zip(coord0, (0,72)))))
        self.buttons['B'] = Button(self, BLUE, button_size, tuple(map(sum, zip(coord0, (0,144)))))
        self.buttons['Y'] = Button(self, YELLOW, button_size, tuple(map(sum, zip(coord0, (0,216)))))
        self.buttons['W'] = Button(self, WHITE, (36, 36), tuple(map(sum, zip(coord0, (0,288)))))
        self.buttons['K'] = Button(self, BLACK, (36, 36), tuple(map(sum, zip(coord0, (60 ,288)))))
        self.buttons['X'] = Button(self, RED, (54, 64), (self.dim[0] + 48, 400), 'X')
        self.buttons['P'] = Button(self, GREEN, 64, (self.dim[0] + 48, 500), 'triangle')
        self.buttons['S'] = Button(self, GRAY, (72,72), (self.dim[0] + 44, 612))
        self.buttons['C'] = Button(self, GRAY, 36, (self.dim[0] + 80, 756), 'circle')

    def _draw_buttons(self):
        all_buttons = self.buttons.values()
        for button in all_buttons:
            button.draw()

    def _draw_cells(self):
        all_cells = self.cells.values()
        for cell in all_cells:
            cell.draw()

    def _draw_blocks(self):
        all_blocks = self.blocks.values()
        for block in all_blocks:
            block.draw()

    def _redraw(self):
        self._draw_background()
        self._draw_blocks()
        self._draw_cells()
        self._draw_buttons()
        pygame.display.update()

    def _add_block(self, mouse_pos, shape, color, instr, d):
        coord = (mouse_pos[0]//36, mouse_pos[1]//36)
        self.blocks.pop(coord, None)
        block = Block(coord, self, shape, color, instr, d)
        self.blocks[coord] = block

    def _remove_block(self, mouse_pos):
        coord = (mouse_pos[0]//36, mouse_pos[1]//36)
        self.blocks.pop(coord, None)

    def color_update(self):
        r, g, b = self.color_name
        d = self.d
        self.color = (r+d, g+d, b+d)

    def is_touching(self, coord, thing):
        x = coord[0]
        y = coord[1]
        if thing.shape and thing.shape is 'circle':
            left = thing.coords[0] - thing.dim
            right = thing.coords[0] + thing.dim
            top = thing.coords[1] - thing.dim
            bottom = thing.coords[1] + thing.dim
        elif isinstance(thing.dim, tuple):
            left = thing.coords[0]
            right = thing.coords[0] + thing.dim[0]
            top = thing.coords[1]
            bottom = thing.coords[1] + thing.dim[1]
        else:
            left = thing.coords[0]
            right = thing.coords[0] + thing.dim
            top = thing.coords[1]
            bottom = thing.coords[1] + thing.dim

        if left <= x <= right and top <= y <= bottom:
            return True
        else:
            return False

    def main_loop(self):
        """ Updates graphics and checks for pygame events """
        running = True
        shape = 'square'
        self.color_name = BLUE
        self.color = BLUE
        self.instr = 0
        self.d = 40
        self.mode = 1
        while running:
            self._redraw()
            for event in pygame.event.get():
                if event.type is pygame.QUIT:
                    running = 0
                elif event.type is pygame.MOUSEBUTTONDOWN:
                    if self.is_touching(event.pos, self):
                        if self.mode > 0:
                            if event.button == 1 or event.button == 4:
                                self._add_block(event.pos, shape, self.color, self.instr, self.d)
                            elif event.button == 3 or event.button == 5:
                                self._remove_block(event.pos)
                        else:
                            s.make_rings(event.pos)
                            s.draw_rings()
                    elif self.is_touching(event.pos, self.buttons['R']):
                        self.color_name = RED
                        self.instr = 0
                    elif self.is_touching(event.pos, self.buttons['G']):
                        self.color_name = GREEN
                        self.instr = 1
                    elif self.is_touching(event.pos, self.buttons['B']):
                        self.color_name = BLUE
                        self.instr = 2
                    elif self.is_touching(event.pos, self.buttons['Y']):
                        self.color_name = YELLOW
                        self.instr = 3
                    elif self.is_touching(event.pos, self.buttons['C']):
                        shape = 'circle'
                    elif self.is_touching(event.pos, self.buttons['S']):
                        shape = 'square'
                    elif self.is_touching(event.pos, self.buttons['W']):
                        if self.d < 90:
                            self.d += 10
                    elif self.is_touching(event.pos, self.buttons['K']):
                        if self.d > 30:
                            self.d -= 10
                    elif self.is_touching(event.pos, self.buttons['P']):
                        self.mode *= -1
                    elif self.is_touching(event.pos, self.buttons['X']):
                        self.blocks = {}
                    self.color_update()
            time.sleep(.01)

class Block(object):
    """ A note block with attributes shape and color which determine the type
    of sound created when it is reached by the sweeper."""

    def __init__(self, cell_coordinates, world, shape, color, instr, d):
        """ takes coordinates as a tuple """
        self.cell_coordinates = cell_coordinates
        self.world = world
        self.shape = shape
        self.color = color
        self.instr = instr
        self.d = d

    def draw(self):
        cells = self.world.cells
        cell = cells[self.cell_coordinates]
        screen = self.world.screen
        if self.shape == 'square':
            coords = self.world._add_coords(cell.coordinates, (3, 3))
            rect_dim = (30, 30)
            self.image_rect = pygame.Rect(coords, rect_dim)
            pygame.draw.rect(screen, self.color, self.image_rect, 0)
        elif self.shape == 'circle':
            coords = self.world._add_coords(cell.coordinates, (18, 18))
            pygame.draw.circle(screen, self.color, coords, 16, 0)

class Cell():
    """ Spots in the grid where blocks can be drawn. """
    def __init__(self, draw_screen, coordinates, size):
        self.draw_screen = draw_screen
        self.coordinates = coordinates
        self.dimensions = (size, size)
        self.color = GRAY

    def draw(self):
        line_width = 1
        rect = pygame.Rect(self.coordinates, self.dimensions)
        pygame.draw.rect(self.draw_screen, self.color, rect, line_width)

class Button():
    """ Creates a Button. """
    def __init__(self, world, color, dimensions, coordinates, shape = 'rect'):
        self.world = world
        self.shape = shape
        self.color = color
        self.coords = coordinates
        self.dim = dimensions

    def draw(self):
        screen = self.world.screen
        if self.shape == 'rect':
            rect = pygame.Rect(self.coords, self.dim)
            pygame.draw.rect(screen, self.color, rect, 0)
        elif self.shape == 'circle':
            pygame.draw.circle(screen, self.color, self.coords, self.dim, 0)
        elif self.shape == 'triangle':
            if self.world.mode > 0:
                point_a = self.coords
                point_b = self.coords[0], self.coords[1] + self.dim
                point_c = self.coords[0] + self.dim, self.coords[1] + self.dim//2
                point_list = [point_a, point_b, point_c]
                pygame.draw.polygon(screen, self.color, point_list, 0)
            else:
                rect = pygame.Rect(self.coords, (self.dim, self.dim))
                pygame.draw.rect(screen, RED, rect, 0)
        elif self.shape == 'X':
            a = self.coords
            b = (self.coords[0] + self.dim[0], self.coords[1])
            c = (self.coords[0], self.coords[1] + self.dim[1])
            d = (self.coords[0] + self.dim[0], self.coords[1] + self.dim[1])
            pygame.draw.line(screen, self.color, a, d, 20)
            pygame.draw.line(screen, self.color, b, c, 20)

class Sweeper():
    """ Sweeps through the grid from an origin point, playing all the blocks
    in one 'ring' at a time."""
    def __init__(self, world):
        self.world = world
        self.rings = self.plan_rings(200)

    def overflow(self, a, b):
        x = (a[0]+b[0]) % 24
        y = (a[1]+b[1]) % 24
        return (x, y)

    def plan_rings(self, number):
        rings = {}
        for n in range(number):
            cells = []
            cells.extend([(n, y) for y in range(-n+1, n)])
            cells.extend([(-n, y) for y in range(-n, n)])
            cells.extend([(x, n) for x in range(-n, n)])
            cells.extend([(x, -n) for x in range(-n+1, n+1)])
            cells.append((n, n))
            rings[n] = cells
        return rings

    def make_rings(self, start):
        self.start = (start[0]//36, start[1]//36)
        center = (start[0]//36, start[1]//36)
        new_rings = {}
        number = len(self.rings)
        for n in range(number):
            new_cells = []
            for coord in self.rings[n]:
                new_coord = self.overflow(center, coord)
                new_cells.append(new_coord)
            new_rings[n] = new_cells
        self.new_rings = new_rings

    def pos_to_note(self, coord, offset):
        if coord[1] == self.start[1]:
            if coord[0] >= self.start[0]:
                return 2 + offset
            else:
                return 6 + offset
        else:
            note = atan((coord[0]-self.start[0])/(coord[1]-self.start[1]))
            note = note*4/pi
            if coord[1] < self.start[1]:
                note += 4
            elif coord[0] < self.start[0]:
                note += 8
            return int(note + offset)

    def draw_rings(self):
        cells = self.world.cells
        screen = self.world.screen

        fs = fluidsynth.Synth()
        fs.start(driver="alsa")
        ids = []
        for s in sound_list:
            ids.append(fs.sfload(s))

        for ring in self.new_rings.values():
            for event in pygame.event.get():
                if event.type is pygame.MOUSEBUTTONDOWN \
                and self.world.is_touching(event.pos, self.world.buttons['P']):
                    self.world.mode *= -1
            if self.world.mode > 0:
                break
            short = []
            held = []
            for coord in ring:
                cell = cells[coord]
                coords = self.world._add_coords(cell.coordinates, (3, 3))
                rect_dim = (30, 30)
                image_rect = pygame.Rect(coords, rect_dim)
                pygame.draw.rect(screen, GRAY, image_rect, 0)
                if coord in self.world.blocks.keys():
                    d = self.world.blocks[coord].d
                    pitch = self.pos_to_note(coord, d)
                    color = self.world.blocks[coord].color
                    shape = self.world.blocks[coord].shape
                    instr = self.world.blocks[coord].instr
                    if shape == 'circle':
                        short.append((pitch, ids[instr]))
                    else:
                        held.append((pitch, ids[instr]))
            for note in short:
                fs.program_select(0, note[1], 0, 0)
                fs.noteon(0, note[0], 60)
            for note in held:
                fs.program_select(0, note[1], 0, 0)
                fs.noteon(0, note[0], 60)
            pygame.display.update()
            time.sleep(.3)
            for note in short:
                fs.noteoff(0, note[0])
            self.world._redraw()
        for note in held:
            fs.noteoff(0, note[0])
        self.world.mode = 1
        fs.delete()

if __name__ == "__main__":
    g = Grid()
    s = Sweeper(g)
    g.main_loop()
