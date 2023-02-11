import curses
from curses import wrapper
from curses.textpad import Textbox
import sys
import math
import jsonpickle
import os.path

GAME_VERSION = "0.1a"

class Container:
    def __init__(self, tier, code):
        self.MAX_TIER = 1
        self.tier = tier
        self.code = code
    
    def modify_code(self, new_code):
        self.code = new_code
    
    def get_tier(self):
        return self.tier
    
    def get_code(self):
        return self.code
    
    def upgrade_tier(self):
        if self.tier < self.MAX_TIER:
            self.tier = self.tier + 1
    
    def set_tier(self, new_tier):
        self.tier = new_tier

class GameState:
    def __init__(self, level):
        self.level = level
        
    def get_level(self):
        return self.level
        
class Game:
    def __init__(self, containers, game_state):
        self.containers = containers
        self.game_state = game_state
        self.version = GAME_VERSION
        
    def get_containers(self):
        return self.containers
    
    def get_game_state(self):
        return self.game_state
    
    def get_version(self):
        return self.version

def get_offset_from_center(center, offset):
    return math.floor(center/2) - math.floor(offset/2)
    
def center_string(string, offset):
    return math.floor(offset/2) - math.floor(len(string)/2)

def add_string_to_window(window, string, center_mode = True, format = curses.A_NORMAL, color_pair = 1, y = None, x = None):
    height, width = window.getmaxyx()
    if y == None:
        y = math.floor(height/2)
    if x == None:
        x = math.floor(width/2)
    if center_mode:
        window.addstr(y, center_string(string, width), string, curses.color_pair(color_pair) | format)
    else:
        window.addstr(y, x, string, curses.color_pair(color_pair) | format)

def create_new_centered_window(width, height, border=True):
    window = curses.newwin(height, width, get_offset_from_center(curses.LINES, height), get_offset_from_center(curses.COLS, width))
    if border:
        window.border()
    return window

def instructions_screen():
    win = create_new_centered_window(100, 40)
    add_string_to_window(win, "Instructions", y=1)
    add_string_to_window(win, "Welcome to AutoCLI, the automation game in your terminal!", y=2, color_pair=2)
    add_string_to_window(win, "We are currently working on the instructions for the game, come back later!", y=3, color_pair=2)
    add_string_to_window(win, "[b]ack", y=38, color_pair=3)
    
    char = 0
    while (char != 98):
        char = win.getch()
        if char == 98:
            win.clear()
            win.refresh()
            title_screen()
            
def new_game():
    if os.path.isfile("game_save"):
        win = create_new_centered_window(50, 5)
        add_string_to_window(win, "Are you sure?", y=1)
        add_string_to_window(win, "This action will overwrite any previous game save!", y=2, color_pair=2)
        add_string_to_window(win, "[y]es | [n]o", y=3, color_pair=3)
        char = 0
        while (char != 121 or char != 110):
            char = win.getch()
            if char == 121:
                win.clear()
                win.refresh()
                game = Game((Container(0, ["", "", "", "", "", "", "", ""]) for i in range(8)), GameState(0))
                file = open("game_save", "w")
                file.write(jsonpickle.encode(game))
                return game
            elif char == 110:
                win.clear()
                win.refresh()
                title_screen()

def load_game():
    file = open("game_save", "r")
    return jsonpickle.decode(file.read())

# def do_tick():

def display_containers(container_list, win, selected):
    left_arrow = "\u2190"
    default_box = "+"
    i = 0
    for container in container_list:
        if i == selected:
            add_string_to_window(win, default_box, color_pair=7, y=3, x=i+2, center_mode=False)
        else:
            add_string_to_window(win, default_box, color_pair=container.get_tier() + 5, y=3, x=i+2, center_mode=False)
        i = i + 1
    win.refresh()

def edit_window(strings):
    win = create_new_centered_window(50, 16)
    text_win = create_new_centered_window(48, 13, border=False)
    add_string_to_window(win, "Edit Container", y=1)
    box = Textbox(text_win)
    for string in strings:
        for char in string:
            box.do_command(char)
        box.do_command(14)
    win.refresh()
    text_win.refresh()
    box.edit()
    text = box.gather()
    strings = text.split('\n')[:7]
    while len(strings) < 8:
        strings.append("")
    win.clear()
    text_win.clear()
    win.refresh()
    text_win.refresh()

def start_game(game):
    win = create_new_centered_window(curses.COLS - 6, curses.LINES - 6)
    active = True
    selected = 1
    container_list = list(game.get_containers())
    code_list = []
    for container in container_list:
        code_list.append(list(container.get_code()))
    add_string_to_window(win, "Game Active", y=1)
    while True:
        curses.halfdelay(2)
        win.keypad(1)
        char = win.getch()
        if char != -1:
            if char == curses.KEY_RIGHT and selected != 8 - 1:
                selected = selected + 1
            elif char == curses.KEY_LEFT and selected != 0:
                selected = selected - 1
            elif char == 111:
                edit_window(code_list[selected])
        display_containers(container_list, win, selected)
        

def title_screen():
    test_win = create_new_centered_window(60, 6)

    add_string_to_window(test_win, "AutoCLI", y = 1)
    add_string_to_window(test_win, "Ver {}".format(GAME_VERSION), y = 2, color_pair = 2)
    test_win.refresh()
    
    add_string_to_window(test_win, "[i]nstructions | [n]ew game | [l]oad game | [q]uit", y = 4, color_pair = 3)
    
    while (True):
        char = test_win.getch()
        if char == 105:
            test_win.clear()
            test_win.refresh()
            instructions_screen()
            break;
        elif char == 110:
            game = new_game()
            test_win.clear()
            test_win.refresh()
            start_game(game)
        elif char == 108:
            game = load_game()
            test_win.clear()
            test_win.refresh()
            start_game(game)
        elif char == 113:
            test_win.clear()
            test_win.refresh()
            exit(0)

def curses_init():
    # initialize color pairs
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    curses.init_pair(7, curses.COLOR_RED, curses.COLOR_WHITE)
    title_screen()

def main(stdscr):
    curses.curs_set(0)
    curses_init()
    
    
    
wrapper(main)