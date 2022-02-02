# Game of life

import pygame
import time
import math




FPS = 60
BG_COLOR = (30, 30, 30)
CELL_COLOR = (140, 255, 0)
COLORKEY = (0, 0, 0)
CELL_SIZE = 8


def scale_render(render):
    """Scales a rendered surface of cells."""
    return pygame.transform.scale(render, (render.get_width() * CELL_SIZE, render.get_height() * CELL_SIZE))


def generate_render(width, height, colorkey):
    """Generates an Surface of which the cells will be drawn to."""
    padding = 0 # cells rendered outside the surface.
    # Calculate width and height.
    render_width = math.ceil(width / CELL_SIZE) + padding
    render_height = math.ceil(height / CELL_SIZE) + padding
    # Create render surface and update colorkey.
    render = pygame.Surface((render_width, render_height)).convert_alpha()
    render.set_colorkey(colorkey)
    return render


def render_cells(render, cells, color, view):
    """Draws the cells onto the image."""
    width = render.get_width()
    height = render.get_height()

    for point in cells:
        if (0 <= point[0] - view[0] < width and
            0 <= point[1] - view[1] < height):
            # Render point.
            render_point = (point[0] - view[0], point[1] - view[1])
            render.set_at(render_point, color)
            

def screen_to_grid(pos, view):
    """Converts the screen coordinates to an  x, y position"""
    x = pos[0] // CELL_SIZE
    y = pos[1] // CELL_SIZE
    return (view[0] + x, view[1] + y)


# -- GAME UPDATES ------------------------------------------------------
def get_dead_neighbours(x, y, cells):
    """Finds the neighbours that are dead around the current cell."""
    offset = range(-1, 0, -1)
    dead_cells = set()
    
    # Loop through the neighbourhood.
    for y_offset in offset:
        for x_offset in offset:
            point = (x + x_offset, y + y_offset)
            if point in cells:
                continue
            dead_cells.add(point)

    return dead_cells


def combine_cells(set1, set2):
    """Adds the smaller set of cells to the bigger set.
    Returns the bigger set."""
    if len(set1) < len(set2):
        set1, set2 = set2, set1

    # Loop through smaller set.
    for cell in set2:
        if cell not in set1:
            set1.add(cell)

    return set1


def neighbourhood(x, y, cells):
    """Returns a set of alive cells and a set of dead cells surrounding
    the current x, y position."""
    offset = range(-1, 2)
    dead_cells = set()
    alive_cells = set()

    # Loop through the neighbourhood.
    for y_offset in offset:
        for x_offset in offset:
            point = (x + x_offset, y + y_offset)
            if point in cells:
                alive_cells.add(point)
                continue
            dead_cells.add(point)

    return (alive_cells, dead_cells)
        
    
def update_cells(alive):
    """Updates the set of cells. Returns the new set of alive cells and
    the new set of dead cells."""
    new_alive = set()
    dead = set()
    # Update alive cells first.
    for point in alive:
        alive_neighbours, dead_neighbours = neighbourhood(*point, alive)
        dead = combine_cells(dead, dead_neighbours)

        # Cell lives.
        if 2 < len(alive_neighbours) < 5:
            new_alive.add(point)
            continue

    # Update dead cells.
    for point in dead:
        alive_neighbours, dead_neighbours = neighbourhood(*point, alive)

        # Cell revives.
        if len(alive_neighbours) == 3:
            new_alive.add(point)
            continue
    return new_alive


def update_cell(point, cells):
    """Inserts a cell into the game."""
    if point in cells:
        cells.remove(point)
    else:
        cells.add(point)
        

# Window initialisation.
pygame.init
screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)

width = screen.get_width()
height = screen.get_height()

old_view = (0, 0)
view = (0, 0)
drag_start = ()

# Control flags.
control = {
    "running":True,
    "paused":True,
    "draw":False,
    "drag":False
    }

# Frame rendering control.
interval = 1 / FPS
next_frame = time.time()
frames = 0
next_second = time.time()

# Game variables.
cells = set()
dead_cells = set()
updated = set()

while control["running"]:
    # Handle events.
    for event in pygame.event.get():

        # Quit event.
        if event.type == pygame.QUIT:
            control["running"] = False
            break

        # Key pressed.
        if event.type == pygame.KEYDOWN:
            # Quit on ESCAPE pressed.
            if event.key == pygame.K_ESCAPE:
                control["running"] = False
                break

            # Pause on p pressed.
            if event.key == pygame.K_p:
                control["paused"] = not control["paused"]
                continue

        # Mouse pressed.
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Draw on left click.
            if event.button == 1 and not control["drag"]:
                control["draw"] = True
                # Fill initial cell.
                point = screen_to_grid(event.pos, view)
                if point not in updated:
                    update_cell(point, cells)
                    updated.add(point)
                continue
            # Move render on right click.
            if event.button == 3 and not control["draw"]:
                control["drag"] = True
                drag_start = screen_to_grid(event.pos, view)
                continue
            
        # Mouse released
        if event.type == pygame.MOUSEBUTTONUP:
            # Stop drawing.
            if event.button == 1:
                control["draw"] = False
                updated = set()
                continue
            # Stop dragging.
            if event.button == 3:
                control["drag"] = False
                old_view = view
                continue

        # Mouse moved.
        if event.type == pygame.MOUSEMOTION:
            # If drawing, fill line.
            if control["draw"]:
                # FIX ME: Convert to line.
                point = screen_to_grid(event.pos, view)
                if point not in updated:
                    update_cell(point, cells)
                    updated.add(point)
                continue

            # If drawing, move render by offset amount.
            if control["drag"]:
                x1, y1 = drag_start
                x2, y2 = screen_to_grid(event.pos, old_view)
                
                diff_x = x1 - x2
                diff_y = y1 - y2
                view = (old_view[0] + diff_x, old_view[1] + diff_y)
                continue
            

    # Update screen.
    current = time.time()
    if current >= next_frame:
        # Framerate correction.
        while current >= next_frame:
            next_frame += interval

        frames += 1

        # Update cells if not paused.
        if not control["paused"]:
            cells = update_cells(cells)

        # Wiping screen and rendering cells.
        screen.fill(BG_COLOR)
        
        render = generate_render(width, height, COLORKEY)
        render_cells(render, cells, CELL_COLOR, view)
        render = scale_render(render)
        render_pos = ((width - render.get_width()) / 2, (height - render.get_height()) / 2)
        
        screen.blit(render, render_pos)
        pygame.display.update()

    if current > next_second:
        next_second += 1
        print(frames)
        frames = 0

pygame.quit()
