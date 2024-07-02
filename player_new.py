import random
import pygame, game

pygame.mixer.init()


collision_tollerence = 10


class Player(pygame.Rect):
    def __init__(self, gameObj : game.Game, x : int, y : int, level_name = None):
        self.gameObj = gameObj
        self.side_length = 50
        pygame.Rect.__init__(self, x, y, self.side_length, self.side_length)
        self.speed = 500
        self.direction = pygame.Vector2()
        self.position = pygame.Vector2(self.x, self.y)
        self.render_pos = pygame.Vector2(650, 360)
        self.velocity = pygame.Vector2()
        self.horizontal_block_check = True
        self.vertical_block_check = True
        self.knife_equiped = True
        self.bomb_equiped = 0
        self.health = 130
        self.max_health = self.health
        self.img = pygame.transform.smoothscale(pygame.image.load('images/player.png'), self.size)

        self.sfx_list_knife = (pygame.mixer.Sound('sounds/SFX/knife1.wav'), pygame.mixer.Sound('sounds/SFX/knife2.wav'), pygame.mixer.Sound('sounds/SFX/knifestab.wav'))
        for i in self.sfx_list_knife:
            i.set_volume(0.2)
    
    
    def direction_update(self):
        self.direction = self.gameObj.INPUTS['mouse_pos'] - self.render_pos - (self.side_length//2, self.side_length//2)
    
    def velocity_update(self):
        D = self.gameObj.INPUTS['movement']
        try:
            self.direction.scale_to_length(self.speed)
            self.velocity = D * self.direction
        except:
            self.velocity.xy = (0,0)
        self.vertical_block_check = True
        self.horizontal_block_check = True
    
    def blockage_check(self, walls : list[pygame.Rect]):
        if self.velocity == (0,0):
            return
        for wall in walls:
            if not (self.horizontal_block_check or self.vertical_block_check):
                return
            if not self.colliderect(wall):
                continue

            if self.horizontal_block_check and self.velocity.x > 0 and (self.right - wall.left <= collision_tollerence):
                self.horizontal_block_check = False
                self.velocity.x = 0

            elif self.horizontal_block_check and self.velocity.x < 0 and (wall.right - self.left <= collision_tollerence):
                self.horizontal_block_check = False
                self.velocity.x = 0

            if self.vertical_block_check and self.velocity.y > 0 and (self.bottom - wall.top <= collision_tollerence):
                self.vertical_block_check = False
                self.velocity.y = 0
            
            elif self.vertical_block_check and self.velocity.y < 0 and (wall.bottom - self.top <= collision_tollerence):
                self.vertical_block_check = False
                self.velocity.y = 0
    
    def position_update(self):
        self.position += self.velocity / self.gameObj.fps
        self.topleft = self.position.xy
    
    def draw_entity(self, cam_x, cam_y):
        plr = (self.x - cam_x, self.y - cam_y)
        self.render_pos = plr
        self.gameObj.screen.blit(self.img, plr)

    def knife_attack(self, others : list[pygame.Rect]):
        if not self.knife_equiped:
            return
        p = self.inflate(100, 100)
        index = p.collidelist(others)
        if index == -1:
            self.sfx_list_knife[random.randint(0,1)].play()
            return
        else:
            self.sfx_list_knife[2].play()
            o = others[index]
            o.health -= 10




    