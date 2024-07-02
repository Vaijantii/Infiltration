import pickle
import pygame, game, time

pygame.font.init()
content_font = pygame.font.Font('normal.ttf', 35)
heading_font = pygame.font.Font('normal.ttf', 65)

##menu button command functions
def pass_cmd():
    pass

def new_game_button(menu):
    menu.gameObj.playing_level_index = 0
    menu.gameObj.isplaying = True

def resume_game_button(menu):
    menu.gameObj.isplaying = True

def next_level_button(menu):
    menu.gameObj.playing_level_index += 1
    menu.gameObj.isplaying = True

def start_level_button(menu, n):
    menu.gameObj.playing_level_index = n
    menu.gameObj.isplaying = True

def goto_levelselector(menu):
    menu.gameObj.menumode = 'levelselector'

def quit_button(menu):
    menu.gameObj.isrunning = False

##ui sounds
pygame.mixer.init()
hover_sfx = pygame.mixer.Sound('sounds/SFX/hover.mp3')
hover_sfx.set_volume(0.09)
click_sfx1 = pygame.mixer.Sound('sounds/SFX/click.mp3')
locked_click_sfx = pygame.mixer.Sound('sounds/SFX/click.mp3')
locked_click_sfx.set_volume(0.02)
click_sfx = click_sfx1


class Menu_Button(object):
    def __init__(self, text, color1, color2, x, y, command = None, params = (), font_type = content_font, backcolor = None):
        if command == None:
            command = pass_cmd
            
        self.img1 = font_type.render(text, 1, color1)
        self.img2 = font_type.render(text, 1, color2, backcolor)
        self.img = self.img1
        a, b = self.img1.get_size()
        self.top_left_corner = (x, y)
        self.bottom_right_corner = (x + a, y + b)
        self.command = command
        self.params = params
        self.state = False

    def update_button_state(self):
        x, y = pygame.mouse.get_pos()
        old_state = self.state
        if self.top_left_corner[0] <= x <= self.bottom_right_corner[0] and self.top_left_corner[1] <= y <= self.bottom_right_corner[1]:
            self.state = True
            self.img = self.img2
        else:
            self.state = False
            self.img = self.img1
        if (not old_state) and (self.state):
            return 1
        if old_state and not self.state:
            return -1
        else:
            return 0
        

class Locked_Button(Menu_Button):
    def __init__(self, text, color1, color2, x, y, font_type = content_font, backcolor = None):
        Menu_Button.__init__(self, text, color1, color2, x, y, pass_cmd, (), font_type, backcolor)
    
    def update_button_state(self):
        global click_sfx
        x, y = pygame.mouse.get_pos()
        old_state = self.state
        if self.top_left_corner[0] <= x <= self.bottom_right_corner[0] and self.top_left_corner[1] <= y <= self.bottom_right_corner[1]:
            self.state = True
            self.img = self.img2
        else:
            self.state = False
            self.img = self.img1
        if (not old_state) and (self.state):
            click_sfx = locked_click_sfx
            hover_sfx.set_volume(0.02)
            return 1
        if old_state and not self.state:
            click_sfx = click_sfx1
            hover_sfx.set_volume(0.09)
            return -1
        else:
            return 0
    



class Main_Menu(object):
    def __init__(self, gameObj : game.Game):
        self.gameObj = gameObj
        self.bg = pygame.image.load('images/main_menu_bg.png')
        self.bg = pygame.transform.scale(self.bg, gameObj.screen_size)
        self.buttons = [
                                    Menu_Button('NEW GAME', self.gameObj.color['dark'], self.gameObj.color['lightest'], 100, 100, new_game_button, (self,)),
                                    Menu_Button('EXIT GAME', self.gameObj.color['dark'], self.gameObj.color['lightest'], 100, 600, quit_button, (self,)),
                                    Menu_Button('LEVEL SELECTOR', self.gameObj.color['dark'], self.gameObj.color['lightest'], 100, 300, goto_levelselector, (self,))
                                  ]
        self.keep_track = False


    def update_menu(self):
        self.gameObj.screen.blit(self.bg, (0,0))
        mt = 0
        for button in self.buttons:
            req_sfx = button.update_button_state()
            if req_sfx == 1:
                self.gameObj.UI_channel.set_volume(1)
                self.gameObj.UI_channel.play(hover_sfx)
            elif req_sfx == -1:
                self.gameObj.UI_channel.set_volume(0.1)
                self.gameObj.UI_channel.play(hover_sfx)
            mt += button.state
            self.gameObj.screen.blit(button.img, button.top_left_corner)
            if button.state:
                pygame.mouse.set_cursor(11)
                if pygame.mouse.get_pressed()[0] and not self.keep_track:
                    self.gameObj.UI_channel.set_volume(1)
                    self.gameObj.UI_channel.play(click_sfx)
                    time.sleep(0.5)
                    button.command(*button.params)
        if mt == 0:
            self.keep_track = pygame.mouse.get_pressed()[0]
            pygame.mouse.set_visible(1)
            pygame.mouse.set_cursor(0)


class Pause_Menu(Main_Menu):
    def __init__(self, gameObj : game.Game):
        Main_Menu.__init__(self, gameObj)
        self.bg = pygame.transform.smoothscale(pygame.image.load('images/level_clear.png'), self.gameObj.screen_size)
        img = heading_font.render(f'GAME PAUSED', 1, self.gameObj.color['dark'])
        self.bg.blit(img, (640 - img.get_width()//2, 60))
        self.buttons = [
            Menu_Button('RESUME GAME', self.gameObj.color['dark'], self.gameObj.color['lightest'], 100, 200, resume_game_button, (self,)),
            Menu_Button('LEVEL SELECTOR', self.gameObj.color['dark'], self.gameObj.color['lightest'], 100, 400, goto_levelselector, (self,)),
            Menu_Button('QUIT GAME', self.gameObj.color['dark'], self.gameObj.color['lightest'], 100, 600, quit_button, (self,))
        ]
        y = 300
        for btn in self.buttons:
            a, b = btn.img1.get_size()
            btn.top_left_corner = (640 - a//2, y)
            btn.bottom_right_corner = (640 - a//2 + a, y + b)
            y += 150


class Win_Menu(Main_Menu):
    def __init__(self, gameObj: game.Game, level_name : str):
        Main_Menu.__init__(self, gameObj)
        self.bg = pygame.transform.smoothscale(pygame.image.load('images/level_clear.png'), self.gameObj.screen_size)
        img = heading_font.render(f'{level_name} CLEARED', 1, self.gameObj.color['dark'])
        self.bg.blit(img, (40, 60))
        self.buttons = [
            Menu_Button('NEXT LEVEL', self.gameObj.color['dark'], self.gameObj.color['lightest'], 40, 400, next_level_button, (self,)),
            Menu_Button('EXIT GAME', self.gameObj.color['dark'], self.gameObj.color['lightest'], 440, 400, quit_button, (self,)),
            Menu_Button('PLAY AGAIN', self.gameObj.color['dark'], self.gameObj.color['lightest'], 840, 400, resume_game_button, (self,)),
            Menu_Button('LEVEL SELECTOR', self.gameObj.color['dark'], self.gameObj.color['lightest'], 40, 600, goto_levelselector, (self,))
        ]

class Game_Complete_Menu(Main_Menu):
    def __init__(self, gameObj: game.Game):
        Main_Menu.__init__(self, gameObj)

        self.buttons = [
            Menu_Button('NEW GAME', self.gameObj.color['dark'], self.gameObj.color['lightest'], 40, 400, new_game_button, (self,)),
            Menu_Button('EXIT GAME', self.gameObj.color['dark'], self.gameObj.color['lightest'], 440, 400, quit_button, (self,)),
            Menu_Button('LEVEL SELECTOR', self.gameObj.color['dark'], self.gameObj.color['lightest'], 840, 400, goto_levelselector, (self,))
        ]

        self.bg = pygame.transform.smoothscale(pygame.image.load('images/level_clear.png'), self.gameObj.screen_size)
        img = heading_font.render(f'FULL GAME COMPLETE', 1, self.gameObj.color['dark'])
        self.bg.blit(img, (40, 60))


class Game_Over_Menu(Main_Menu):
    def __init__(self, gameObj : game.Game):
        Main_Menu.__init__(self, gameObj)
        self.bg = pygame.transform.smoothscale(pygame.image.load('images/level_clear.png'), self.gameObj.screen_size)
        img = heading_font.render(f'YOU JUST COULD NOT MAKE IT', 1, self.gameObj.color['dark'])
        self.bg.blit(img, (40, 60))
        self.buttons = [
            Menu_Button('LEVEL SELECTOR', self.gameObj.color['dark'], self.gameObj.color['lightest'], 840, 400, goto_levelselector, (self,)),
            Menu_Button('EXIT GAME', self.gameObj.color['dark'], self.gameObj.color['lightest'], 440, 400, quit_button, (self,)),
            Menu_Button('TRY AGAIN', self.gameObj.color['dark'], self.gameObj.color['lightest'], 40, 400, resume_game_button, (self,)) 
        ]


class Level_Selector_Menu(Main_Menu):
    def __init__(self, gameObj : game.Game):
        Main_Menu.__init__(self, gameObj)
        self.bg = pygame.transform.smoothscale(pygame.image.load('images/level_clear.png'), self.gameObj.screen_size)
        img = heading_font.render('LEVEL SELECTOR', 1, self.gameObj.color['dark'])
        self.bg.blit(img, (40, 60))

        self.buttons = []
        x = 40; y = 300
        with open('Max-Level-Unlocked', 'rb') as f:
            max_lev = pickle.load(f)
        for i in range(max_lev + 1):
            self.buttons.append(
                Menu_Button(self.gameObj.level_names[i], self.gameObj.color['dark'], self.gameObj.color['lightest'], x, y, start_level_button, (self, int(i)))
            )
            x += self.buttons[-1].img.get_width() + 30
            if x > 970:
                x = 40
                y += self.buttons[-1].img.get_height() + 20
        
        for i in range(max_lev + 1, len(self.gameObj.level_names)):
            self.buttons.append(
                Locked_Button(self.gameObj.level_names[i], self.gameObj.color['light'], self.gameObj.color['light-2'], x, y)
            )
            x += self.buttons[-1].img.get_width() + 30
            if x > 970:
                x = 40
                y += self.buttons[-1].img.get_height() + 20
        
        self.buttons.append(
            Menu_Button('EXIT GAME', self.gameObj.color['dark'], self.gameObj.color['lightest'], 40, 650, quit_button, (self,))
        )
        self.islevelselector = True



        
