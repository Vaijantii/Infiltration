import pickle
import pygame


##game handling class
class Game(object):
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF) 
        self.screen_size = self.screen.get_size()
        pygame.display.set_icon(pygame.image.load('images/icon.ico'))
        pygame.display.set_caption('THE INFILTRATION')
        self.isrunning = True
        self.isplaying = False
        self.menumode = 'startup' # startup, pause, win, lose
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.color = {
                        'red' : (255, 0, 0),    'blue' : (0, 0, 255),   'green' : (0, 255, 0),'hlt_green' : (46, 163, 54),  
                        'grey': (80, 80, 80),   'white' : (255, 255, 255),  'offwhite' : (200, 200, 200),
                        'seaBlue' : (100, 200, 200),    'lightgrey' : (120, 120, 120),      'black' : (0,0,0),
                        'lightest' : (247,240,245), 'light' : (222,203,183), 'light-2' : (200,181,161), 
                        'mid' : (143,133,125), 'dark' : (92,85,82), 'darkest' : (67,54,51)
                    }
        self.screen.fill(self.color['black'])

        self.INPUTS = {'movement' : 0, 'mouse_pos' : pygame.Vector2(), 'trigger_action' : False, 'plant_bomb' : False, 'knife' : False, 'detonate' : False}
        self.make_new_node = False
        
        self.music_channel = pygame.mixer.Channel(0)
        self.UI_channel = pygame.mixer.Channel(1)
        self.mission_pass_channel = pygame.mixer.Channel(2)
        self.player_SFX_attack = pygame.mixer.Channel(3)

        self.level_names = []
        with open('Levels/Level-Names.txt', 'r') as f:
            raw_data = f.read().split('\n')
        for i in raw_data:
            if i[0] != '#':
                self.level_names.append(i)
        self.playing_level_index = 0

        try:
            with open('Max-Level-Unlocked', 'rb') as f:
                pass
        except FileNotFoundError:
            with open('Max-Level-Unlocked', 'wb') as f:
                pickle.dump(0, f)

    def user_input(self):
        ##Single Frame Events
        self.INPUTS['trigger_action'] = False
        self.INPUTS['plant_bomb'] = False
        self.INPUTS['knife'] = False
        self.INPUTS['detonate'] = False
        self.make_new_node = False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.isplaying = False
                    self.menumode = 'pause'
                elif event.key == pygame.K_SPACE:
                    self.INPUTS['detonate'] = True
                elif event.key == pygame.K_TAB:
                    self.make_new_node = True
                if event.key == pygame.K_e:
                    self.INPUTS['trigger_action'] = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                b = event.button
                if b == 1: 
                    self.INPUTS['plant_bomb'] = True
                elif b == 3:
                    self.INPUTS['knife'] = True
            elif event == pygame.QUIT:
                self.isplaying = False
                self.isrunning = False

        ##Tracking The Key Press Events (Multiple Frames)
        keys = pygame.key.get_pressed()
        
        ##movements
        self.INPUTS['movement'] = keys[pygame.K_w] - keys[pygame.K_s]

        ##mouse position
        self.INPUTS['mouse_pos'].xy = pygame.mouse.get_pos()
