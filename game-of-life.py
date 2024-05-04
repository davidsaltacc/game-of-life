import cv2, numpy as np, keyboard, mouse, time

WIN_SIZE = 1024
WIN_TEXT = "Game of Life"
ALIVE_COLOR = (230, 230, 230)
DEAD_COLOR = (20, 20, 20)
FPS = 30

alive_cells = [
    [0, 0],
    [1, 0],
    [2, 0],
    [2, -1],
    [1, -2]
]

def get_all_neighbors(cell):
    neighbors_pos = []
    for offset in [[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]:
        neighbors_pos.append([cell[0] + offset[0], cell[1] + offset[1]])
    neighbors = []
    for neighbor_pos in neighbors_pos:
        alive = False
        for cell_ in alive_cells:
            if neighbor_pos == cell_:
                alive = True
        neighbors.append([neighbor_pos, alive])
    return neighbors

def get_alive_neighbor_amount(cell):
    amount = 0
    for neighbor in get_all_neighbors(cell):
        if neighbor[1]:
            amount += 1
    return amount

def tick():
    global alive_cells
    
    to_tick = []
    new_cells = []
    
    for cell in alive_cells: 
        to_tick.append([cell, True, get_alive_neighbor_amount(cell)])
        for neighbor in get_all_neighbors(cell):
            to_tick.append([neighbor[0], neighbor[1], get_alive_neighbor_amount(neighbor[0])])
            
    to_tick_ = []
    [to_tick_.append(pos) for pos in to_tick if pos not in to_tick_]
    to_tick = to_tick_
    
    for cell in to_tick:
        if cell[1] and (cell[2] == 2 or cell[2] == 3):
            new_cells.append(cell[0])
        if cell[2] == 3 and not cell[1]:
            new_cells.append(cell[0])

    alive_cells = []
    [alive_cells.append(pos) for pos in new_cells if pos not in alive_cells]


image = np.zeros((WIN_SIZE, WIN_SIZE, 3), dtype = np.uint8)

zoom = 16
offset_x = WIN_SIZE // 2 // zoom
offset_y = WIN_SIZE // 2 // zoom

def cells_to_squares():
    squares = []
    for cell in alive_cells:
        squares.append([[(cell[0] + offset_x) * zoom, (cell[1] + offset_y) * zoom], [(cell[0] + offset_x) * zoom + zoom, (cell[1] + offset_y) * zoom + zoom]])
    return squares

def frame():
    image[:] = DEAD_COLOR

    for square in cells_to_squares():
        cv2.rectangle(image, pt1 = square[0], pt2 = square[1], color = ALIVE_COLOR, thickness = -1)
        
    cv2.imshow(WIN_TEXT, image)
    cv2.waitKey(1)

paused = True
skip_next = False

def move(dir):
    global offset_x, offset_y
    offset_x += dir[0]
    offset_y += dir[1]
    frame()

def pause(): global paused; paused = not paused
keyboard.add_hotkey("space", pause)

mouse_x = -1
mouse_y = -1

def to_cell_pos():
    return [
        int(np.floor(mouse_x / zoom)) - offset_x,
        int(np.floor(mouse_y / zoom)) - offset_y
    ]

def on_mouse():

    
    if mouse_x < 0 or mouse_x > WIN_SIZE or mouse_y < 0 or mouse_y > WIN_SIZE: return 
    
    cell_pos = to_cell_pos()
    
    try:
        alive_cells.remove(cell_pos)
    except ValueError:
        alive_cells.append(cell_pos)
    
    frame()

def mouse_move(event, x, y, *_):
    global mouse_x, mouse_y
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x = x
        mouse_y = y

mouse.on_click(on_mouse)

frame()

cv2.setMouseCallback(WIN_TEXT, mouse_move)

while True:
    
    if keyboard.is_pressed("w"): move([0, 1])
    if keyboard.is_pressed("a"): move([1, 0])
    if keyboard.is_pressed("s"): move([0, -1])
    if keyboard.is_pressed("d"): move([-1, 0])
    
    if keyboard.is_pressed("up"): zoom += 1
    if keyboard.is_pressed("down"): zoom -= 1
    
    frame()
    if not paused:
        tick()
    
    time.sleep(float("%.3f" % (1  / FPS)))
