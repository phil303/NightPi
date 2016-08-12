import time
import curses

from math_utils import vector_distance

def convert_to_strip(matrix):
    strip = []
    for idx, row in enumerate(matrix):
        if idx % 2 == 1:
            row = reversed(row)
        for led in row:
            strip.append(led)
    return strip

@curses.wrapper
def render(screen):
    # makes screen.getch non-blocking
    screen.nodelay(1)

    def _render(matrix):
        count = 0
        while True:
            count = count % 3
            frame = matrix[count]

            screen.clear()
            curses.start_color()
            curses.use_default_colors()

            for i in range(curses.COLORS):
                curses.init_pair(i, i, -1)

            for y, row in enumerate(frame):
                for x, c in enumerate(row):
                    screen.addstr(y, x, "0", curses.color_pair(c))

            count += 1
            time.sleep(0.5)
            screen.getch()

            # todo: convert to it's own function
            #  for i in range(curses.COLORS):
                #  screen.addstr(str(i), curses.color_pair(i))

    return _render

# From https://gist.github.com/MicahElliott/719710#gistcomment-1442838
# Default color levels for the color cube
CUBE_LEVELS = [0x00, 0x5f, 0x87, 0xaf, 0xd7, 0xff]
SNAPS = [(c + CUBE_LEVELS[i + 1]) / 2 for i, c in enumerate(CUBE_LEVELS[:-1])]

def rgb_to_term_colors(r, g, b):
    """ Convert RGB values to the nearest equivalent xterm-256 color. """
    # Using list of snap points, convert RGB value to cube indexes
    r, g, b = [len(tuple(s for s in SNAPS if s < v)) for v in (r, g, b)]
    return r * 36 + g * 6 + b + 16

def convert_piskel_frame_to_rgb_frame(matrix):
    """ Convert an exported matrix from piskel.com to rgb """
    new_matrix = []
    for row in matrix:
        hex_row = []
        for hex_str in row:
            # piskel outputs these backwards for some reason. It also outputs
            # the alpha value, which we're going to ignore for now
            r = int(hex_str[6:], 16)
            g = int(hex_str[4:6], 16)
            b = int(hex_str[2:4], 16)
            hex_row.append((r, g, b))

        new_matrix.append(hex_row)

    return new_matrix

def convert_piskel_matrix_to_term_colors(matrix):
    new_matrix = []
    for frame in matrix:
        frame = convert_piskel_frame_to_rgb_frame(frame)

        new_frame = []
        for row in frame:
            term_row = []
            for rgb in row:
                term_color = rgb_to_term_colors(*rgb)
                term_row.append(term_color)
            new_frame.append(term_row)
        new_matrix.append(new_frame)

    return new_matrix

