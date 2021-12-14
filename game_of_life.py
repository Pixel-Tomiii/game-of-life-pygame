import pygame
import numpy
import time
import random
import os
    
def load_pattern(x, y, pattern):
    """Function for loading certain patterns from a text file of
    coordinated with origin 0,0. Each coordinate represents an offset
    from the x and y position given.

    Pattern must be saved in patterns directory.

    Returns:
        A set of cell coordinate tuples."""
    cells = set()
    with open("patterns/" + pattern + ".txt" if not pattern.endswith(".txt") else "") as pattern_map:
        for line in pattern_map:
            line = line.strip()

            # Skip blank lines.
            if not line:
                continue

            offset_x, offset_y = line.split(",")
            cells.add((x+int(offset_x), y+int(offset_y)))
    return cells

def random_cells(width, height):
    """Function for creating a random amount of cells randomly distrubuted."""
    cells = set()
    for cell_num in range(random.randint(width, width * height)):
        cells.add((random.randint(0, width), random.randint(0, height)))
    return cells

def neighbours(x, y, cells, currently_dead):
    """Returns the number of alive cells around the current cell.
    Updates current_dead set.
    If centre cell is dead, alive neighbours is 1 less than absolute."""
    total = -1  # Start at -1 because centre cell is usually alive.

    # work from an offset of x and y
    for y_offset in range(-1, 2):
        for x_offset in range(-1, 2):
            new_pos = (x+x_offset, y+y_offset)
            if new_pos in cells:
                total += 1
            else:
                currently_dead.add(new_pos)
                
    return total

def alive_neighbours(x, y, cells):
    """Returns the number of alive cells around the current cell.
    If centre cell is dead, alive neighbours is 1 less than absolute."""
    total = -1  # Start at -1 because centre cell is usually alive.

    # work from an offset of x and y
    for y_offset in range(-1, 2):
        for x_offset in range(-1, 2):
            new_pos = (x+x_offset, y+y_offset)
            if new_pos in cells:
                total += 1
                
    return total
    
def update(cells):
    """Updates a set of cells, returning a set of alive cells."""
    new_cells = set()
    dead_cells = set()

    # Update every cell.
    for coord in cells:
        num_alive = neighbours(*coord, cells, dead_cells)
        
        # Keep it alive.
        if num_alive == 2 or num_alive == 3:
            new_cells.add(coord)

    # Update every dead cell.
    for coord in dead_cells:
        num_alive = alive_neighbours(*coord, cells)
        if num_alive == 2:
            new_cells.add(coord)

    return new_cells

def render(display, cells, width, height):
    # Initialise grid for writing to each frame.
    grid = numpy.zeros((width, height), dtype=int)
    
    # Insert cells into grid.
    for x, y in cells:
        if 0 <= x < width and 0 <= y < height:
            grid[x, y] = 255

    # Update screen.
    cell_image = pygame.surfarray.make_surface(grid.repeat(cell_size, axis=0).repeat(cell_size, axis=1))
    
    display.blit(cell_image, (0, 0))
    pygame.display.update()

# Initialise window features.
pygame.init()
screen_width = 1000
screen_height = 800
display = pygame.display.set_mode((screen_width, screen_height), pygame.HWSURFACE)
display.fill(0)

# Initialise cell dimensions.
min_size = 1
max_size = 16
cell_size = 8

# Initialise grid boundaries. Round down and add bleeding.
grid_width = (screen_width // cell_size)
grid_height = (screen_height // cell_size)

# Game variables.
cells = load_pattern(grid_width // 2, grid_height // 2, "blom")
#cells = random_cells(grid_width-1, grid_height-1)

# Game loop modifiers.
current = time.time()
last = time.time()
interval = 0
frames = 0
running = False
draw = False

start = time.time()
render(display, cells, grid_width, grid_height)
# Game loop.
while True:
    # Loop through events.
    for event in pygame.event.get():
        
        # Keyboard events.
        if event.type == pygame.KEYDOWN:
            # Ecape to quit.
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                print(f"fps: {round(frames / (time.time() - start), 1)}")
                os._exit(0)
            # Space bar to pause.
            elif event.key == pygame.K_SPACE and not draw:
                running = not running

            # DEL to delete screen and pause.
            elif event.key == pygame.K_DELETE:
                if running:
                    running = False
                    
                cells = set()
                render(display, cells, grid_width, grid_height)

        # Mouse button pressed events.
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Draw a cell when paused.
            if event.button == 1 and not running:
                draw = True
                x, y = event.pos
                grid_x = x // cell_size
                grid_y = y // cell_size

                cells.add((grid_x, grid_y))
                render(display, cells, grid_width, grid_height)
                
            # Zooming in.
            if event.button == 4:
                pass
            # Zooming out
            elif event.button == 5:
                pass

        elif event.type == pygame.QUIT:
            pygame.quit()
            print(f"fps: {round(frames / (time.time() - start), 1)}")
            os._exit(0)

        elif event.type == pygame.MOUSEMOTION:
            if draw:
                x, y = event.pos
                grid_x = x // cell_size
                grid_y = y // cell_size

                cells.add((grid_x, grid_y))
                render(display, cells, grid_width, grid_height)

        # Mouse button up events.
        elif event.type == pygame.MOUSEBUTTONUP:
            # Stop drawing cells.
            if event.button == 1:
                draw = False
            
    # Go back to start if it's not time for a new frame.
    current = time.time()
    if not running or current - last < interval:
        continue
    last = current
    frames += 1

    # Updating the cells.
    cells = update(cells)
    render(display, cells, grid_width, grid_height)
    
