import pygame
import numpy
import time
import random
import os

from pygame.color import Color
from pygame.surfarray import make_surface


pygame.init()
display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
display.fill(Color("#000000"))

cell_size = 6
initial = cell_size
width = 1920 // cell_size
height = 1080 // cell_size
cells = set([(random.randint(0, width-1), random.randint(0, height-1)) for _ in range(int(0.2 * width * height))])

def get_neighbours(x, y):
    global cells
    global width
    global height
    
    alive = []
    dead = []
    
    for y_offset in range(-1, 2):
        for x_offset in range(-1, 2):
            # Every position not including the current position.
            if y_offset == 0 and x_offset == 0:
                continue
            
            new_x = x + x_offset
            new_y = y + y_offset

            # Cell is alive.
            if (new_x, new_y) in cells:
                alive.append((new_x, new_y))
            else:
                dead.append((new_x, new_y))
                    
    return alive, dead

def update_cells():
    global cells
    new_cells = set()
    dead_cells = set()

    for cellx, celly in cells:
        alive_neighbours, dead_neighbours = get_neighbours(cellx, celly)

        # Add dead neighbours to set to work through after working alive cells.
        for neighbour in dead_neighbours:
            if neighbour not in dead_cells:
                dead_cells.add(neighbour)
        
        if not (len(alive_neighbours) < 2 or len(alive_neighbours) > 3):
            new_cells.add((cellx, celly))

    # Reviving dead cells.
    for cellx, celly in dead_cells:
        alive_neighbours, dead_neighbours = get_neighbours(cellx, celly)

        if len(alive_neighbours) == 3:
            new_cells.add((cellx, celly))

    return new_cells

current = time.time()
last = time.time()
interval = 1/30
frames = 0
grid = numpy.zeros((width, height), dtype=int)
running = True
redraw = False
drag = False
pos = (0, 0)
original = (0, 0)

start = time.time()
while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                end = time.time()
                print(f"{frames} frames in {round(end - start, 1)}s")
                print(f"FPS: {round(frames / (end - start))}")
                os._exit(0)
                
            if event.key == pygame.K_SPACE:
                running = not running
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if cell_size != initial:
                    drag = True
                    original = event.pos

            if event.button == 4:
                if cell_size < 16:
                    cell_size *= 2
                    new_width = 1920 // cell_size
                    new_height = 1080 // cell_size

                    translate_x = ((new_width - width) // 2)
                    translate_y = ((new_height - height) // 2)

                    new_cells = set(map(lambda pos: (pos[0]+translate_x, pos[1]+translate_y), new_cells))
                    redraw = True
                    pos = (0, 0)
                   

            if event.button == 5:
                if cell_size > initial:
                    cell_size //= 2
                    new_width = 1920 // cell_size
                    new_height = 1080 // cell_size

                    translate_x = round((new_width - width) / 2)
                    translate_y = round((new_height - height) / 2)

                    new_cells = set(map(lambda pos: (pos[0]+translate_x, pos[1]+translate_y), new_cells))
                    redraw = True
                    pos = (0, 0)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drag = False

        elif event.type == pygame.MOUSEMOTION:
            if drag and event.pos != original:
                x, y = event.pos
                new_x = pos[0] - (original[0] - x)
                new_y = pos[1] - (original[1] - y)

                # TODO: Check movement bounds ?
                pos = (new_x, new_y)
                original = event.pos
                redraw = True
                

    
    # Reset loop.
    current = time.time()
    if current - last < interval:
        continue

    frames += 1
    last = current
    
    # Draw cells.
    if running:
        new_cells = update_cells()
        
    if not redraw:
        different = new_cells.symmetric_difference(cells)
    else:
        grid = numpy.zeros((width, height), dtype=int)
        different = new_cells
        redraw = False

        
    for x, y in different:
        if x < 0 or x >= width:
            continue

        if y < 0 or y >= height:
            continue
        
        if (x, y) in new_cells:
            grid[x, y] = 127
        else:
            grid[x, y] = 0

    display.fill(0)
    display.blit(make_surface(grid.repeat(cell_size, axis=0).repeat(cell_size, axis=1)), pos)
    pygame.display.update()
    cells = new_cells
    
"""
Rewrite main loop for drawing.
The whole thing needs to be redrawn when the size is changed or the view port moves.
Only render things in the view port (rendered inside the numpy array)
Make the bounds of the view port a little extra than the sides of the screen to allow bleeding
Keep a constant grid width and height, only change the cell size / view port.
    Currenty resizes instead of zooms.
Maybe subprocess cell updates?
"""
