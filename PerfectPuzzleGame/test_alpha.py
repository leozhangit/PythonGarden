
import pygame, sys, random
from pygame.locals import *

# 一些用到的常量
WINDOWWIDTH = 1000 #640
WINDOWHEIGHT = 660 #480
FPS = 30
BASICFONTSIZE = 36
def main():
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('TEST')
    BASICFONT = pygame.font.SysFont('simhei', BASICFONTSIZE)    
    
    # 读取图片文件
    background=pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT))
    background.fill((0, 0, 0))
    img = pygame.image.load('TESTBG.png')
    img=img.convert()
    img1 = pygame.image.load('test2.png')
    img1=img1.convert()
    img2 = pygame.image.load('test1.png')
    img2=img2.convert_alpha()
    # rect=image.get_rect()
    # rect2=image2.get_rect()
    # rect2.left=rect.width+1
    
    i = 1
    while True: # 主循环 main game loop
        for event in pygame.event.get(): # 事件（event）检查循环
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        img1.set_alpha(i)
        img2.set_alpha(i)
        # DISPLAYSURF.blit(background, (0,0)) #background.get_rect())
        DISPLAYSURF.blit(img, (0, 0))
        DISPLAYSURF.blit(img1, (0, 0))
        DISPLAYSURF.blit(img2, (500, 0))  
        i+=1
        if i==255:i=1        
        # 更新window界面显示     
        pygame.display.update()
        # pygame.time.delay(20)
        FPSCLOCK.tick(FPS)
        

if __name__ == '__main__':
    main()
    