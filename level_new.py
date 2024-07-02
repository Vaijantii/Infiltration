from Levels import *

import pickle, player_new, random, game, enemy_new, pygame


def rotate_img(img : pygame.Surface, angle : int, x1 : int, y1 : int) -> tuple[pygame.Surface, tuple[int,int]]:
    image2 = pygame.transform.rotozoom(img, angle, 1)
    w1,h1 = img.get_size()
    w2,h2 = image2.get_size()
    x,y = x1 + w1/2 - w2/2, y1 + h1/2 - h2/2
    return image2, (x,y)


class Level(object):
    def __init__(self, gameObj : game.Game, level_name : str):
        self.gameObj = gameObj
        with open(f'Levels/{level_name}/{level_name}.map', 'rb') as f:
            map_data = pickle.load(f)
        self.walls = map_data['walls']
        self.path_nodes = map_data['path_nodes']
        self.path_lines = map_data['path_lines']
        self.mission_sequence = map_data['mission_pointers']
        self.trigger_event = Trigger_event(gameObj, self, level_name, self.mission_sequence)
        self.bg_pics = {}
        self.arrow = pygame.transform.smoothscale(pygame.image.load('images/arrow_blue.png'), (80,50))
        for i in self.walls:
            self.bg_pics[i] = pygame.image.load(f'Levels/{level_name}/{level_name}-bgpics/{level_name}-{i[0]}-{i[1]}.png').convert()
        for i in self.walls:
            wl = self.walls[i]
            for j in range(len(wl)):
                wall_data = wl[j]
                x, y = wall_data['top_left']
                w = wall_data['bottom_right'][0] - x
                h = wall_data['bottom_right'][1] - y
                wall = pygame.Rect(x, y, w, h)
                wl[j] = wall
        self.player = player_new.Player(self.gameObj, map_data['player_data'][0], map_data['player_data'][1] ,level_name)
        self.player_grid = (1, 0)
        self.cam_x = self.player.centerx - self.gameObj.screen_size[0]//2
        self.cam_y = self.player.centery - self.gameObj.screen_size[1]//2

        self.enemies = []
        ed = map_data['enemy_data']
        for e in ed:
            if e[2] == 'basic':
                self.enemies.append(enemy_new.Enemy_Basic(self.gameObj, e[0], e[1], level_name))
            else:
                self.enemies.append(enemy_new.Enemy_Weak(self.gameObj, e[0], e[1], level_name))

        
        self.bombs = Bomb(self, map_data['bomb_positions'])
        self.screen_shake_val = 0

        self.reset_bg_color = self.gameObj.color['mid']

        ##ui elements
        self.ui_bomb_pic = pygame.transform.smoothscale(pygame.image.load('images/bomb2.png'), (30, 30))
        pygame.font.init()
        self.font = pygame.font.Font('normal.ttf', 20)


        with open('Max-Level-Unlocked', 'rb') as f:
            max_lev = pickle.load(f)
        if self.gameObj.playing_level_index > max_lev:
            max_lev = self.gameObj.playing_level_index
        with open('Max-Level-Unlocked', 'wb') as f:
            pickle.dump(max_lev, f)

    
    
    def update_world(self):
        if self.player.health < 0:
            self.gameObj.isplaying = False
            self.gameObj.menumode = 'gameover'
        
        a, b = self.player.topleft
        self.player_grid = (a//1280, b//720)
        self.player.direction_update()
        self.player.velocity_update()
        self.player.blockage_check(self.walls[self.player_grid])
        self.player.position_update()

        if self.gameObj.INPUTS['detonate']:
            self.bombs.cause_explosion(self.enemies + [self.player])

        self.bombs.check_pickup()
        
        if self.gameObj.INPUTS['plant_bomb']:
            self.bombs.plant_bomb()

        enemies = list(self.enemies)
        for enemy in enemies:
            if enemy.health < 0:
                self.enemies.remove(enemy)
                continue
            enemy.update_anger_state(self.player)
            enemy.velocity_update(self.player, self.walls[enemy.x//1280, enemy.y//720])
            enemy.position_update()

        if self.gameObj.INPUTS['knife']:
            self.player.knife_attack(self.enemies)

        self.trigger_event.check_trigger_event()
        
    

    def screen_shake(self, cam_x, cam_y):
        self.screen_shake_val -= 1
        cam_x += random.randint(-5, 5)
        cam_y += random.randint(-5, 5)
        return cam_x, cam_y

    def render_world(self):
        self.cam_x += (self.player.centerx - self.gameObj.screen_size[0]//2 - self.cam_x)/10
        self.cam_y += (self.player.centery - self.gameObj.screen_size[1]//2 - self.cam_y)/10

        cam_x = int(self.cam_x)
        cam_y = int(self.cam_y)
        if self.screen_shake_val:
            cam_x, cam_y = self.screen_shake(cam_x, cam_y)

        self.gameObj.screen.fill(self.reset_bg_color)
        
        Gx, Gy = self.player_grid

        for gx in (Gx-1, Gx, Gx+1):
            for gy in (Gy-1, Gy, Gy+1):
                pic = self.bg_pics.get((gx, gy))
                if pic != None:
                    self.gameObj.screen.blit(pic, (gx*1280 - cam_x, gy*720 - cam_y))
        
        
        if self.trigger_event.num_frames > 0:
            self.trigger_event.multiframe_function(*self.trigger_event.params)
            self.trigger_event.num_frames -= 1
        
        for enemy in self.enemies:
            enemy.draw_entity(cam_x, cam_y)
        
        self.player.draw_entity(cam_x, cam_y)

        self.bombs.render_bombs(cam_x, cam_y)

        ##ui rendering
        x, y = self.trigger_event.trigger_pos
        pos_x, pos_y = x - 5 - cam_x,  y - 5 - cam_y
        if pos_x not in range (0, 1280) or pos_y not in range(0, 720):
            v = (x, y) - self.player.position
            r, phi = v.as_polar()
            self.gameObj.screen.blit(*rotate_img(self.arrow, -phi, 100, 620)) #draws the arrow
        pygame.draw.rect(self.gameObj.screen, (10, 255, 120), (pos_x, pos_y,  10, 10)) # draws the green dot
        pygame.draw.rect(self.gameObj.screen, self.gameObj.color['hlt_green'], (1130, 20, self.player.health, 10)) #health bar
        pygame.draw.rect(self.gameObj.screen, self.gameObj.color['red'], (1129, 19, 132, 12), 1) # health bar border
        for i in range(self.player.bomb_equiped):
            self.gameObj.screen.blit(self.ui_bomb_pic, (1150, 40))
            self.gameObj.screen.blit(self.font.render(f'x   {self.player.bomb_equiped}', 1, self.gameObj.color['seaBlue']), (1200, 40))
            break






class Trigger_event(object):
    def __init__(self, gameObj : game.Game, levelObj : Level, level_name : str, sequence : list[tuple[int, int]]):
        self.gameObj = gameObj
        self.levelObj = levelObj
        self.sequence = sequence
        self.functions_list = []
        for i in range(len(sequence)):
            self.functions_list.append(eval(f'{level_name}.func{i}'))
        self.params = (0,)
        self.num_frames = -1

        self.update_trigger()
    
    def update_trigger(self):
        try:
            self.trigger_pos = self.sequence.pop(0)
            self.trigger_func = self.functions_list.pop(0)
        except IndexError:
            self.gameObj.isplaying = False
            self.gameObj.menumode = 'win'
            
            if self.gameObj.playing_level_index + 1 == len(self.gameObj.level_names):
                self.gameObj.menumode = 'gamecomplete'
    
    def multiframe_function(self, *args):
        pass
    
    def check_trigger_event(self):
        if self.levelObj.player.collidepoint(self.trigger_pos):
            self.multiframe_function, self.params, self.num_frames = self.trigger_func(self.gameObj, self.levelObj)
            self.update_trigger()



class Bomb(object):
    def __init__(self, levelObj : Level, positions : list[tuple[int, int]]):
        self.levelObj = levelObj
        self.positions = positions
        self.planted = []
        self.planted_temp = []
        self.exploded = []
        self.influence = 100
        self.pic_pickup = pygame.transform.smoothscale(pygame.image.load('images/bomb2.png'), (30, 30))
        self.pic_planted = pygame.transform.smoothscale(pygame.image.load('images/bomb1.png'), (20, 20))
        self.exploded_pics = []
        self.blast_img_width = pygame.transform.rotozoom(pygame.image.load('images/blasts/blast0.png'), 0, 3.5).get_width()
        self.blast_img_height = pygame.transform.rotozoom(pygame.image.load('images/blasts/blast0.png'), 0, 3.5).get_height()
        for i in range(24):
            self.exploded_pics.append(pygame.transform.rotozoom(pygame.image.load(f'images/blasts/blast{i}.png'), 0, 3.5))
        self.blast_sfx = pygame.mixer.Sound('sounds/SFX/bomb.mp3')
        self.plant_sfx = pygame.mixer.Sound('sounds/SFX/bombplantbeep.mp3')
        self.pickup_sfx = pygame.mixer.Sound('sounds/SFX/bomb_pickup.wav')
        self.pickup_sfx.set_volume(1)
        self.plant_sfx.set_volume(0.2)

    def check_pickup(self):
        P = self.levelObj.player
        B = list(self.positions)
        for b in B:
            if P.collidepoint((b[0], b[1])):
                self.pickup_sfx.play()
                self.levelObj.player.bomb_equiped += 1
                self.positions.remove(b)
                break

    def plant_bomb(self):
        if self.levelObj.player.bomb_equiped:
            p = self.levelObj.player
            f = pygame.Rect(0,0,300,300)
            f.center = p.center
            self.plant_sfx.play(1)
            self.planted.append(f)
            self.planted_temp.append([f, 60])
            self.levelObj.player.bomb_equiped -= 1
    
    def cause_explosion(self, others : list[enemy_new.Enemy_Basic]):
        for bomb in self.planted:
            self.exploded.append([0, bomb])
            for en in bomb.collidelistall(others):
                others[en].health -= 50
            self.blast_sfx.play()
            self.levelObj.screen_shake_val = 40
        self.planted.clear()
        
    
    def render_bombs(self, cam_x, cam_y):
        g = self.levelObj.gameObj.screen
        b = self.pic_pickup ; p = self.pic_planted ; ex = self.exploded_pics
        blast_width = self.blast_img_width // 2 ; blast_height = self.blast_img_height // 2
        for i in self.positions:
            g.blit(b, (i[0] - cam_x, i[1] - cam_y))
        for i in self.planted:
            g.blit(p, (i.centerx - cam_x, i.centery - cam_y))
        for i in self.planted_temp:
            if i[1]:
                pygame.draw.rect(g, (255,0,0), [i[0].x - cam_x, i[0].y - cam_y, i[0].width, i[0].height], 1)
                i[1] -= 1
            else:
                self.planted_temp.remove(i)
        dummy_exploded = list(self.exploded)
        for i in dummy_exploded:
            try:
                x, y = i[1].center
                g.blit(ex[int(i[0])], (x - blast_width  - cam_x, y - blast_height - cam_y))
                i[0] += 1
            except IndexError:
                self.exploded.remove(i)
