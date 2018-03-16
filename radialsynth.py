"""Created by Jane Sieving (jsieving) on 3/7/18.

This is "Radial Synth", a game made by Lydia Hodges and Jane Sieving for our
Interactive Programming project.

Used code from AI & Algorithms Toolbox as base code for working with a grid-like
world in pygame.

"""

import pygame
import time
import fluidsynth
from math import atan, pi

BLACK = (0, 0, 0)
DKGRAY = (25, 25, 25)
GRAY = (40, 40, 40)
LTGRAY = (100, 100, 100)
WHITE = (240, 240, 240)
BLUE = (24, 160, 160)
RED = (200, 24, 80)
GREEN = (120, 200, 24)
VIOLET = (120, 24, 200)

sound_list = ["sound_files/Kawai Grand Piano.sf2", \
                "sound_files/Full Grand Piano.sf2", \
                "sound_files/flutey_synth.sf2", \
                "sound_files/Energized.sf2"]

class Grid():
    """ A grid full of cells, where note blocks can be placed by the user
    to 'draw' music."""

    def __init__(self, width=24, height=24, cell_size=36):
        pygame.init()
        screen_size = (width*cell_size + 160, height*cell_size)
        self.screen = pygame.display.set_mode(screen_size)
        self.blocks = {}
        self.coords = (0, 0)
        self.width = width
        self.height = height
        self.dim = (width*cell_size, height*cell_size)
        self.cell_size = cell_size
        self.init_cells()
        self.init_buttons()
        self.shape = 'grid'

    def draw_background(self):
        self.screen.fill(DKGRAY)

    def add_coords(self, a, b):
        x = (a[0]+b[0])
        y = (a[1]+b[1])
        return (x, y)

    def init_cells(self):
        """ Creates a grid of Cell objects."""
        self.cells = {}
        for i in range(self.height):
            for j in range(self.width):
                cell_coord = (i*self.cell_size, j*self.cell_size)
                self.cells[(i, j)] = Cell(self.screen, cell_coord, self.cell_size)

    def init_buttons(self):
        """ Creates the buttons for user control of blocks and music playback."""
        self.buttons = {}
        button_size = (96, 36)
        coord0 = (self.width*self.cell_size + 32, 0 + 36)
        self.buttons['R'] = Button(self, RED, button_size, coord0)
        self.buttons['V'] = Button(self, VIOLET, button_size, tuple(map(sum, zip(coord0, (0,72)))))
        self.buttons['B'] = Button(self, BLUE, button_size, tuple(map(sum, zip(coord0, (0,144)))))
        self.buttons['G'] = Button(self, GREEN, button_size, tuple(map(sum, zip(coord0, (0,216)))))
        self.buttons['W'] = Button(self, WHITE, (36, 36), tuple(map(sum, zip(coord0, (0,288)))))
        self.buttons['K'] = Button(self, BLACK, (36, 36), tuple(map(sum, zip(coord0, (60 ,288)))))
        self.buttons['X'] = Button(self, RED, (54, 64), (self.dim[0] + 48, 400), 'X')
        self.buttons['P'] = Button(self, GREEN, 64, (self.dim[0] + 48, 500), 'triangle')
        self.buttons['S'] = Button(self, LTGRAY, (72,72), (self.dim[0] + 44, 612))
        self.buttons['C'] = Button(self, LTGRAY, 36, (self.dim[0] + 80, 756), 'circle')

    def draw_buttons(self):
        all_buttons = self.buttons.values()
        for button in all_buttons:
            button.draw()

    def draw_cells(self):
        all_cells = self.cells.values()
        for cell in all_cells:
            cell.draw()

    def draw_blocks(self):
        all_blocks = self.blocks.values()
        for block in all_blocks:
            block.draw()

    def redraw(self):
        """ Updates the screen by redrawing al objects."""
        self.draw_background()
        self.draw_blocks()
        self.draw_cells()
        self.draw_buttons()
        pygame.display.update()

    def add_block(self, mouse_pos, shape, color, instr, d):
        """ Adds a note block to the grid, with attributes controlled by the
        user clicking buttons."""
        coord = (mouse_pos[0]//36, mouse_pos[1]//36)
        self.blocks.pop(coord, None)
        block = Block(coord, self, shape, color, instr, d)
        self.blocks[coord] = block

    def remove_block(self, mouse_pos):
        """ Deletes a note block from the screen."""
        coord = (mouse_pos[0]//36, mouse_pos[1]//36)
        self.blocks.pop(coord, None)

    def color_update(self):
        """ Adjusts the color given by color_name by the darkness value d, which
        corresponds to the pitch offset. A lower d value will place note blocks
        in a lower octave with a darker color."""
        r, g, b = self.color_name
        d = 2 * (self.d - 64)
        self.color = (r+d, g+d, b+d)

    def is_touching(self, coord, thing):
        """ Checks if the mouse position (coord) is within the range of an
        object's x and y bounds."""
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
        """ Updates graphics and checks for pygame events. """
        running = True
        shape = 'circle'
        self.color_name = BLUE
        self.color = BLUE
        self.instr = 0
        self.d = 64
        self.mode = 1

        while running:
            self.redraw()
            for event in pygame.event.get():
                if event.type is pygame.QUIT:
                    running = 0
                elif event.type is pygame.MOUSEBUTTONDOWN:
                    if self.is_touching(event.pos, self): # Touching the grid
                        if self.mode > 0: # When paused
                            if event.button == 1 or event.button == 4:
                                self.add_block(event.pos, shape, self.color, self.instr, self.d)
                            elif event.button == 3 or event.button == 5:
                                self.remove_block(event.pos)
                        else: # During playback
                            s.make_rings(event.pos)
                            s.draw_rings()
                    # Other cases: touching a button
                    elif self.is_touching(event.pos, self.buttons['R']):
                        self.color_name = RED
                        self.instr = 0
                    elif self.is_touching(event.pos, self.buttons['G']):
                        self.color_name = GREEN
                        self.instr = 1
                    elif self.is_touching(event.pos, self.buttons['B']):
                        self.color_name = BLUE
                        self.instr = 2
                    elif self.is_touching(event.pos, self.buttons['V']):
                        self.color_name = VIOLET
                        self.instr = 3
                    elif self.is_touching(event.pos, self.buttons['C']):
                        shape = 'circle'
                    elif self.is_touching(event.pos, self.buttons['S']):
                        shape = 'square'
                    elif self.is_touching(event.pos, self.buttons['W']):
                        if self.d < 88:
                            self.d += 12
                    elif self.is_touching(event.pos, self.buttons['K']):
                        if self.d > 52:
                            self.d -= 12
                    elif self.is_touching(event.pos, self.buttons['P']):
                        self.mode *= -1
                    elif self.is_touching(event.pos, self.buttons['X']):
                        self.blocks = {}
                    self.color_update()
            time.sleep(.01)

class Block():
    """ A note block whose attributes shape, instr and d determine the type of
    sound created when it is reached by the sweeper."""

    def __init__(self, cell_coords, world, shape, color, instr, d):
        """ Creates a block. """
        self.cell_coords = cell_coords
        self.world = world
        self.shape = shape
        self.color = color
        self.instr = instr
        self.d = d

    def draw(self):
        """ Draws the block to the screen. """
        cells = self.world.cells
        cell = cells[self.cell_coords]
        screen = self.world.screen
        if self.shape == 'square':
            coords = self.world.add_coords(cell.coords, (3, 3))
            rect_dim = (30, 30)
            image_rect = pygame.Rect(coords, rect_dim)
            pygame.draw.rect(screen, self.color, image_rect, 0)
        elif self.shape == 'circle':
            coords = self.world.add_coords(cell.coords, (18, 18))
            pygame.draw.circle(screen, self.color, coords, 16, 0)

class Cell():
    """ Spots in the grid where blocks can be drawn. """

    def __init__(self, draw_screen, coords, size):
        """ Creates a single cell. """
        self.draw_screen = draw_screen
        self.coords = coords
        self.dim = (size, size)
        self.color = GRAY

    def draw(self):
        """ Draws cells to create the grid. """
        line_width = 1
        rect = pygame.Rect(self.coords, self.dim)
        pygame.draw.rect(self.draw_screen, self.color, rect, line_width)

class Button():
    """ Buttons which respond to user input to change the attributes of note
    blocks and control music playback."""
    def __init__(self, world, color, dim, coords, shape = 'rect'):
        """ Creates a Button. """
        self.world = world
        self.shape = shape
        self.color = color
        self.coords = coords
        self.dim = dim

    def draw(self):
        """ Draws a Button to the screen, depending on what shape the button is. """
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
    """ Sweeps through the grid from a starting point, playing all the note
    blocks in one 'ring' at a time."""

    def __init__(self, world):
        self.world = world
        self.rings = self.plan_rings(200)

    def overflow(self, a, b):
        """ Returns new grid coordinates which are adjusted to be within the
        bounds of the grid by translating "out of range" coordinates to the
        opposite side."""
        x = (a[0]+b[0]) % 24
        y = (a[1]+b[1]) % 24
        return (x, y)

    def plan_rings(self, number):
        """ Plans a dictionary with lists of the coordinates for each cell in
        each of 'number' rings. The rings are centered around (0, 0)."""
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
        """ Offsets each coordinate in the list of ring coordinates by the start
        position. If any of the resulting coordinates is out of range of the
        grid, it is translated to the other side of the grid. The result is a
        list of rings which move in waves across the grid from the start."""
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
        """ Returns a note based on the angle of a note block from the starting
        position of the rings. The offset determines what octave the note is in
        and is determined by the darkness value of the note block."""
        scale = [0, 2, 4, 5, 7, 9, 11, 12]
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
            return scale[int(note)] + offset

    def draw_rings(self):
        """ Draws the rings outward from the starting position and plays the
        notes in each ring."""
        cells = self.world.cells
        screen = self.world.screen

        # Initialize the synthesizer and load sound fonts
        fs = fluidsynth.Synth()
        fs.start(driver="alsa")
        ids = []
        for s in sound_list:
            ids.append(fs.sfload(s))
        short = []
        held = []

        # Loops through each ring
        for ring in self.new_rings.values():
            # Checks if stop button is pressed to stop playback
            for event in pygame.event.get():
                if event.type is pygame.MOUSEBUTTONDOWN \
                and self.world.is_touching(event.pos, self.world.buttons['P']):
                    self.world.mode *= -1
            # Breaks playback loop if stopped
            if self.world.mode > 0:
                break
            # Colors the cells in the current ring gray and adds the notes
            # represented by note blocks to lists to be played
            for coord in ring:
                cell = cells[coord]
                coords = self.world.add_coords(cell.coords, (2, 2))
                rect_dim = (32, 32)
                image_rect = pygame.Rect(coords, rect_dim)
                pygame.draw.rect(screen, GRAY, image_rect, 0)
                if coord in self.world.blocks.keys():
                    d = self.world.blocks[coord].d
                    pitch = self.pos_to_note(coord, d)
                    shape = self.world.blocks[coord].shape
                    instr = self.world.blocks[coord].instr
                    if shape == 'circle':
                        short.append((pitch, ids[instr]))
                    else:
                        held.append((pitch, ids[instr]))
            # Plays notes in the lists for the current ring
            for note in short:
                fs.program_select(0, note[1], 0, 0)
                fs.noteon(0, note[0], 60)
            for note in held:
                fs.program_select(0, note[1], 0, 0)
                fs.noteon(0, note[0], 60)
            # Allows the gray rings to be drawn
            pygame.display.update()
            time.sleep(.3)
            # Ends any notes in the 'short' list
            for note in short:
                fs.noteoff(0, note[0])
            short = []
            # Clears the gray rings by redrawing everything else
            self.world.redraw()
        # At the end, stops any held notes, sets the mode to paused, and stops the Synth
        for note in held:
            fs.noteoff(0, note[0])
        held = []
        self.world.mode = 1
        fs.delete()

if __name__ == "__main__":
    g = Grid()
    s = Sweeper(g)
    g.main_loop()
