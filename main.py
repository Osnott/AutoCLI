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
    def __init__(self, level, max_h, max_he):
        self.level = level
        self.max_h = max_h
        self.curr_h = self.max_h
        self.max_he = max_he
        self.curr_he = 0
        
    def get_level(self):
        return self.level
    
    def set_level(self, level):
        self.level = level
        self.h = (self.level * 100) + 100
        
    def remove_h(self):
        if self.curr_h > 0:
            self.curr_h = self.curr_h - 1
            return True
        return False
    
    def add_h(self, add_h):
        if self.curr_h + add_h <= self.max_h:
            self.curr_h = self.curr_h + add_h
            return True
        return False
    
    def get_max_h(self):
        return self.max_h
    
    def get_curr_h(self):
        return self.curr_h
    
    def remove_he(self):
        if self.curr_he > 0:
            self.curr_he = self.curr_he - 1
            return True
        return False
    
    def add_he(self, add_he):
        if self.curr_he + add_he <= self.max_he:
            self.curr_he = self.curr_he + add_he
            return True
        return False
    
    def get_max_he(self):
        return self.max_he
    
    def get_curr_he(self):
        return self.curr_he

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

def create_new_win(width, height, x, y, border=True):
    window = curses.newwin(height, width, y, x)
    if border:
        window.border()
    return window

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
                game = Game((Container(0, ["", "", "", "", "", "", "", ""]) for i in range(8)), GameState(0, 100, 50))
                file = open("game_save", "w")
                file.write(jsonpickle.encode(game))
                file = open("game_save", "r")
                return jsonpickle.decode(file.read())
            elif char == 110:
                win.clear()
                win.refresh()
                title_screen()
    else:
        game = Game((Container(0, ["", "", "", "", "", "", "", ""]) for i in range(8)), GameState(0, 100, 50))
        file = open("game_save", "wr")
        file.write(jsonpickle.encode(game))
        file = open("game_save", "r")
        return jsonpickle.decode(file.read())

def load_game():
    file = open("game_save", "r")
    return jsonpickle.decode(file.read())

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
    curses.curs_set(1)
    win = create_new_centered_window(50, 16)
    text_win = create_new_centered_window(48, 8, border=False)
    add_string_to_window(win, "Edit Container", y=1)
    box = Textbox(text_win)
    for string in strings:
        for char in string:
            box.do_command(char)
        box.do_command(14)
    for _ in strings:
        box.do_command(16)
    box.do_command(1)
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
    curses.curs_set(0)
    return strings

def do_tick(game, container_list, code_list):
    for i in range(len(code_list)):
        h = 0
        he = 0
        for j in range(len(code_list[i])):
            match code_list[i][j].split(" ")[0]:
                case "get":
                    match code_list[i][j].split(" ")[1]:
                        case "h_pool":
                            if game.get_game_state().remove_h():
                                h = h + 1
                        case "he_pool":
                            if game.get_game_state().remove_he():
                                he = he + 1
                case "fusion":
                    match code_list[i][j].split(" ")[1]:
                        case "h":
                            if h >= 2:
                                he = he + 1
                                h = h - 2
                case "out":
                    match code_list[i][j].split(" ")[1]:
                        case "h":
                            if game.get_game_state().add_h(h):
                                h = 0
                        case "he":
                            if game.get_game_state().add_he(he):
                                he = 0

def start_game(game):
    win = create_new_centered_window(curses.COLS - 6, curses.LINES - 6)
    stats_win_border = create_new_win(20, 6, curses.COLS - 6 - 21, curses.LINES - 6 - 7)
    stats_win = create_new_win(18, 4, curses.COLS - 6 - 20, curses.LINES - 6 - 6, False)
    selected = 1
    active = False
    container_list = list(game.get_containers())
    code_list = []
    for container in container_list:
        code_list.append(list(container.get_code()))
    add_string_to_window(win, "Game Active", y=1)
    add_string_to_window(win, "[s]ave | [q]uit | [o]pen container | [t]oggle active", y=curses.LINES-8, color_pair=3)
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
                code_list[selected] = edit_window(code_list[selected])
            elif char == 115:
                save_win = create_new_centered_window(40, 3)
                try:
                    file = open("game_save", "w")
                    new_containers = (Container(container_list[i].get_tier(), code_list[i]) for i in range(len(code_list)))
                    file.write(jsonpickle.encode(Game(new_containers, game.get_game_state())))
                    add_string_to_window(save_win, "Game Successfully Saved", y=1)
                    save_win.refresh()
                    curses.napms(1000)
                    save_win.clear()
                    save_win.refresh()
                except Exception as e:
                    add_string_to_window(save_win, "Error Occured While Saving Game!", y=1, color_pair=2)
                    print(e)
                    save_win.refresh()
                    curses.napms(1000)
                    save_win.clear()
                    save_win.refresh()
            elif char == 116:
                active = not active
            elif char == 113:
                exit()
        if active:
            do_tick(game, container_list, code_list)
        display_containers(container_list, win, selected)
        stats_win.clear()
        add_string_to_window(stats_win, "Game Stats", y=0)
        add_string_to_window(stats_win, "H: {} / {}".format(game.get_game_state().get_curr_h(), game.get_game_state().get_max_h()), y=1, color_pair=2)
        add_string_to_window(stats_win, "He: {} / {}".format(game.get_game_state().get_curr_he(), game.get_game_state().get_max_he()), y=2, color_pair=2)
        stats_win.refresh()
        stats_win_border.refresh()

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