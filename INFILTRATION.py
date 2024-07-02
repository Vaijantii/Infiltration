import pygame
import game, menu, level_new

gameObj = game.Game()
menuObj = menu.Main_Menu(gameObj)

# def intro(gameObj):
#     scene_length = 5
#     pic1 = pygame.image.load('images/opening1.png')
#     pic2 = pygame.image.load('images/opening2.png')
#     pic3 = pygame.image.load('images/opening3.png')
#     track = pygame.mixer.Sound('sounds/music/intro.wav')
#     track.set_volume(0.3)
#     frame_count = int(scene_length * gameObj.fps)
#     gameObj.screen.fill(gameObj.color['darkest'])
#     gameObj.music_channel.play(track)
#     for i in range(gameObj.fps):
#         gameObj.clock.tick(gameObj.fps)
    
#     for i in range(frame_count - 20 + 1):
#         gameObj.clock.tick(gameObj.fps)
#         gameObj.screen.fill(gameObj.color['darkest'])
#         img = pic1
#         img.set_alpha(int(255*i/(frame_count-20)))
#         gameObj.screen.blit(img, (0,0))
#         pygame.display.update()
    
#     gameObj.screen.fill(gameObj.color['darkest'])
#     gameObj.screen.blit(img, (0,0))
    
#     for i in range(frame_count//2 + 1):
#         gameObj.clock.tick(gameObj.fps)
#         img = pic2
#         img.set_alpha(int(255*i/(frame_count//2)))
#         gameObj.screen.blit(img, (0,0))
#         pygame.display.update()
    
#     for i in range(frame_count + 30):
#         gameObj.clock.tick(gameObj.fps)
#         gameObj.screen.blit(img, (0,0))
#         img = pic3
#         img.set_alpha(int(100*i/(frame_count//2)))
#         pygame.display.update()
#     gameObj.screen.fill(gameObj.color['darkest'])
#     gameObj.screen.blit(img, (0,0))
#     pygame.display.update()
#     for i in range(gameObj.fps):
#         gameObj.clock.tick(gameObj.fps)


##Initial beautification loading screen
##intro(gameObj)

def main():
    global gameObj, menuObj, levelObj
    ##game loop
    while gameObj.isrunning:
        
        try:
            a = menuObj.islevelselector
        except:
            if gameObj.menumode == 'levelselector':
                menuObj = menu.Level_Selector_Menu(gameObj)


        ##stuff other than main gameplay loop
        gameObj.clock.tick(gameObj.fps)
        for e in pygame.event.get():
            if e == pygame.QUIT:
                gameObj.isrunning = False
            if e.type == pygame.KEYDOWN:
                pass


        ##RESET SCREEN
        gameObj.screen.fill(gameObj.color['black'])

        ##all drawing to be done here
        menuObj.update_menu()

        pygame.display.update()
        ##UPDATE SCREEN
        
        if gameObj.isplaying:
            gameObj.music_channel.unpause()
            if not gameObj.menumode == 'pause':
                level_name = gameObj.level_names[gameObj.playing_level_index]
                print(f'{level_name} initialised in main loop')
                levelObj = level_new.Level(gameObj, level_name)
            
            pygame.mouse.set_cursor(3)
            gameObj.menumode = ''

            ##loop
            while gameObj.isplaying:
                ##place for main gameplay loop
                
                gameObj.user_input()
                levelObj.update_world()
                levelObj.render_world()

                pygame.display.update()


                gameObj.clock.tick(gameObj.fps)
            else:
                if gameObj.menumode == 'pause':
                    menuObj = menu.Pause_Menu(gameObj)
                    gameObj.music_channel.pause()
                elif gameObj.menumode == 'win':
                    menuObj = menu.Win_Menu(gameObj, level_name)
                elif gameObj.menumode == 'gamecomplete':
                    menuObj = menu.Game_Complete_Menu(gameObj)
                elif gameObj.menumode == 'gameover':
                    menuObj = menu.Game_Over_Menu(gameObj)
                    gameObj.music_channel.stop()

            


if __name__ == '__main__':
    main()
    pygame.quit() #close the pygame display when main() is terminated 
    
