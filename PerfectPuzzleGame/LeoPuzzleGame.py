# 动画效果的拼图游戏 - Leo Zhang 2020.10.1
# 以网上获取的Al Sweigart编写的Python游戏Slide Puzzle为基础修改
# 2020.10.5 增加确认对话框（仅限windows平台）

import pygame, sys, random
from pygame.locals import *

import win32api,win32con  #win32接口用于弹出消息提醒

# 一些用到的常量
BOARDWIDTH = 3 # 将拼图切分成几列
BOARDHEIGHT = 3 # 将拼图切分成几行
TILESIZE = 540//BOARDWIDTH #136 #80
WINDOWWIDTH = 1000 #640
WINDOWHEIGHT = 660 #480
FPS = 30
BLANK = None

#                 R    G    B
BLACK =         (  0,   0,   0)
WHITE =         (255, 255, 255)
GRAY =          (192, 192, 192)
DARKGRAY =      (128, 128, 128)
BRIGHTBLUE =    (  0,  50, 255)
DARKTURQUOISE = (  3,  54,  73)
GREEN =         (  0, 204,   0)
RED =           (255,   0,   0)

BGCOLOR = DARKTURQUOISE
TILECOLOR = GRAY
TEXTCOLOR = WHITE
BORDERCOLOR = GRAY
BASICFONTSIZE = 36 
TILEFONTSIZE = TILESIZE // 3 - 2

BUTTONCOLOR = DARKGRAY
BUTTONTEXTCOLOR = WHITE
MESSAGECOLOR = WHITE

XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 3)
YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 3 * 2)

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, TILEFONT, PUZZLE_IMG, SMALL_IMG, PIC_RECT    
    global RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT 

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('完美拼图 【2020双节版-2020.10.1】')
    BASICFONT = pygame.font.SysFont('simhei', BASICFONTSIZE)
    TILEFONT = pygame.font.SysFont('simhei', TILEFONTSIZE)
    hwnd = pygame.display.get_wm_info()['window'] #获取当前window句柄handle
    
    # 读取图片文件
    img = pygame.image.load('test1.png')
    # 修改图片尺寸
    n_width = TILESIZE*BOARDWIDTH
    n_height = TILESIZE*BOARDHEIGHT
    PUZZLE_IMG = pygame.transform.scale(img, (n_width, n_height)) #图片缩放
    SMALL_IMG = pygame.transform.scale(img, (XMARGIN, XMARGIN)) #图片缩放

    # 计算三个按钮（option buttens）应该安放的位置
    text_X = XMARGIN + BOARDWIDTH * TILESIZE + XMARGIN // 2
    text_Y = YMARGIN + BOARDHEIGHT * TILESIZE - BASICFONTSIZE
    # 生成三个按钮（option buttons) 并保存到全局变量
    RESET_SURF, RESET_RECT = makeText(' 退回重玩 ',    BUTTONTEXTCOLOR, BUTTONCOLOR, text_X, text_Y - BASICFONTSIZE * 4)
    NEW_SURF,   NEW_RECT   = makeText(' 再来一局 ', BUTTONTEXTCOLOR, BUTTONCOLOR, text_X, text_Y - BASICFONTSIZE * 2)
    SOLVE_SURF, SOLVE_RECT = makeText(' 解题演示 ',    BUTTONTEXTCOLOR, BUTTONCOLOR, text_X, text_Y)
    
    # 开始动画
    splashscreen('完 美','拼 图','欢迎来到完美拼图！按任意键继续...')
    
    # 根据分割方块的个数，确定开始时初始化时的滑动次数，并初始化
    numSlides = BOARDWIDTH * BOARDHEIGHT * 5
    mainBoard, solutionSeq = generateNewPuzzle(numSlides)
    SOLVEDBOARD = getStartingBoard() 
    PIC_RECT = getpicrect()
    allMoves = [] # 保存所有开始后的移动记录


    while True: # 主循环 main game loop
        slideTo = None
        msg = '点击方块 或 按方向键 移动...'  
        
        if mainBoard == SOLVEDBOARD:
            if len(allMoves) > 0:
                msg = '成功完成拼图！共滑动方块' +str(len(allMoves))+ '次。'
                splashscreen('任 务','完 成',msg)
                # win32api.MessageBox(hwnd, msg, "完美拼图",win32con.MB_OK)
                
            msg = '请选择【再来一局】开始新的拼图游戏'
            allMoves = []
            solutionSeq = []
        drawBoard(mainBoard, msg)

        checkForQuit()
        for event in pygame.event.get(): # 事件（event）检查循环
            if event.type == MOUSEBUTTONUP:
                spotx, spoty = getSpotClicked(mainBoard, event.pos[0], event.pos[1])

                if (spotx, spoty) == (None, None):
                    # 检查是否按了命令按钮
                    if RESET_RECT.collidepoint(event.pos):  
                        if len(allMoves)>0:
                            rc = win32api.MessageBox(hwnd, "是否恢复最初拼图画面", "完美拼图",win32con.MB_YESNO)
                            if rc == win32con.IDYES:
                                animationSpeed=int(TILESIZE / 2) # 设置合理的移动速度
                                resetAnimation(mainBoard, allMoves,animationSpeed)
                                allMoves = []
                    elif NEW_RECT.collidepoint(event.pos): 
                        if len(solutionSeq) == 0:
                            rc = win32con.IDYES
                        else:
                            rc = win32api.MessageBox(hwnd, "是否放弃，开始新的拼图游戏？", "完美拼图",win32con.MB_YESNO)
                        if rc == win32con.IDYES:
                            numSlides = BOARDWIDTH * BOARDHEIGHT * 5 #计算合理的滑动次数
                            mainBoard, solutionSeq = generateNewPuzzle(numSlides) 
                            allMoves = []
                    elif SOLVE_RECT.collidepoint(event.pos):                        
                        if len(solutionSeq)>0:
                            rc = win32api.MessageBox(hwnd, "是否观看自动拼图演示？", "完美拼图",win32con.MB_YESNO)
                            if rc == win32con.IDYES:
                                animationSpeed=int(TILESIZE / 5) # 设置合理的移动速度
                                resetAnimation(mainBoard, solutionSeq + allMoves, animationSpeed) 
                                allMoves = []
                                solutionSeq = []
                else:
                    # 检查按的方块是否在空格旁边，且判断方块移动方向
                    blankx, blanky = getBlankPosition(mainBoard)
                    if spotx == blankx + 1 and spoty == blanky:
                        slideTo = LEFT
                    elif spotx == blankx - 1 and spoty == blanky:
                        slideTo = RIGHT
                    elif spotx == blankx and spoty == blanky + 1:
                        slideTo = UP
                    elif spotx == blankx and spoty == blanky - 1:
                        slideTo = DOWN

            elif event.type == KEYUP:
                # 检查方向按键是否被按
                if event.key in (K_LEFT, K_a) and isValidMove(mainBoard, LEFT):
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d) and isValidMove(mainBoard, RIGHT):
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w) and isValidMove(mainBoard, UP):
                    slideTo = UP
                elif event.key in (K_DOWN, K_s) and isValidMove(mainBoard, DOWN):
                    slideTo = DOWN

        if slideTo: #如果方块被移动
            animationSpeed=int(TILESIZE / 5) # 设置合理的移动速度
            slideAnimation(mainBoard, slideTo, '点击方块 或 按方向键 移动...', animationSpeed) 
            makeMove(mainBoard, slideTo)
            allMoves.append(slideTo) # 记录移动过程
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def checkForQuit():
    for event in pygame.event.get(QUIT): # 退出事件处理
        pygame.quit()
        sys.exit()
    for event in pygame.event.get(KEYUP): # 获得所有KEYUP事件
        pygame.event.post(event) # 将其他KEYUP事件post回去


def getStartingBoard():
    # 返回一个拼图数据结构，例如3阶的返回如下    
    #  [[1, 4, 7], [2, 5, 8], [3, 6, BLANK]]
    counter = 1
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(counter)
            counter += BOARDWIDTH
        board.append(column)
        counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1

    board[BOARDWIDTH-1][BOARDHEIGHT-1] = BLANK
    return board


def getpicrect():
    # 返回图片切分的rect数据结构，把小图片赋予每个方块
    counter = 1
    p_rect = [] #图片切分的rect数据结构    
    for y in range(BOARDHEIGHT):
        for x in range(BOARDWIDTH):
            rect_area = pygame.Rect((TILESIZE*x+1,TILESIZE*y+1), (TILESIZE-2, TILESIZE-2))
            p_rect.append(rect_area)
            counter += 1
    return p_rect

def getBlankPosition(board):
    # 检查并返回空格方块的（X,Y)顺序位置
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == BLANK:
                return (x, y)


def makeMove(board, move):
    # 不检查，直接交换两个方块的位置.
    blankx, blanky = getBlankPosition(board)
    if move == UP:
        board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
    elif move == DOWN:
        board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
    elif move == LEFT:
        board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
    elif move == RIGHT:
        board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]


def isValidMove(board, move):
    # 如果空格在最边上，就会有方向是不能用的，返回False
    blankx, blanky = getBlankPosition(board)
    return (move == UP and blanky != len(board[0]) - 1) or \
           (move == DOWN and blanky != 0) or \
           (move == LEFT and blankx != len(board) - 1) or \
           (move == RIGHT and blankx != 0)


def getRandomMove(board, lastMove=None):
    # 返回一个随机移动方向（排除来的方向 和 不能用的方向）
    validMoves = [UP, DOWN, LEFT, RIGHT]
    if lastMove == UP or not isValidMove(board, DOWN):
        validMoves.remove(DOWN)
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)
    return random.choice(validMoves)


def getLeftTopOfTile(tileX, tileY):
    left = XMARGIN + (tileX * TILESIZE) + (tileX - 1)
    top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)
    return (left, top)


def getSpotClicked(board, x, y):
    # 通过点击的坐标位置，获取方块的（X,Y)顺序位置    
    for tileX in range(len(board)):
        for tileY in range(len(board[0])):
            left, top = getLeftTopOfTile(tileX, tileY)
            tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tileRect.collidepoint(x, y):
                return (tileX, tileY)
    return (None, None)


def drawTile(tilex, tiley, number, adjx=0, adjy=0):
    # 按照预定位置切分整个大图并画小方块
    left, top = getLeftTopOfTile(tilex, tiley)    
    pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adjx, top + adjy, TILESIZE, TILESIZE))  
    PIC_RECT = getpicrect() # 获取大图中当前方块的切割图像部分的rect
    DISPLAYSURF.blit(PUZZLE_IMG, (left + adjx + 1, top + adjy + 1), PIC_RECT[number-1])

def makeText(text, color, bgcolor, top, left):
    # 生成并返回文字的 图片Surface 和 矩形Rect对象
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)


def drawBoard(board, message):
    # 画出整个游戏图板
    DISPLAYSURF.fill(BGCOLOR)
    if message:
        textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(textSurf, textRect)

    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            if board[tilex][tiley]:
                drawTile(tilex, tiley, board[tilex][tiley])

    left, top = getLeftTopOfTile(0, 0)
    width = BOARDWIDTH * TILESIZE
    height = BOARDHEIGHT * TILESIZE
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 8, top - 8, width + 17, height + 17), 4)


    image_X = XMARGIN + BOARDWIDTH * TILESIZE + XMARGIN // 2 + 5
    DISPLAYSURF.blit(SMALL_IMG, (image_X, top))
    pygame.draw.rect(DISPLAYSURF, BRIGHTBLUE, (image_X - 5, top - 5, XMARGIN + 11, XMARGIN + 11), 4)
    
    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
    DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)
    ll,tt,ww,hh = RESET_RECT
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (ll - 3, tt - 3, ww + 7, hh + 7), 2)
    ll,tt,ww,hh = NEW_RECT
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (ll - 3, tt - 3, ww + 7, hh + 7), 2)
    ll,tt,ww,hh = SOLVE_RECT
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (ll - 3, tt - 3, ww + 7, hh + 7), 2)


def slideAnimation(board, direction, message, animationSpeed):
    # 展示移动动画效果（不检查是否不合理）
    blankx, blanky = getBlankPosition(board)
    if direction == UP:
        movex = blankx
        movey = blanky + 1
    elif direction == DOWN:
        movex = blankx
        movey = blanky - 1
    elif direction == LEFT:
        movex = blankx + 1
        movey = blanky
    elif direction == RIGHT:
        movex = blankx - 1
        movey = blanky

    # 为动画复制一个新画布baseSurf
    drawBoard(board, message)
    baseSurf = DISPLAYSURF.copy()
    # 在新画布上擦除将要移动的方块
    moveLeft, moveTop = getLeftTopOfTile(movex, movey)
    pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, TILESIZE, TILESIZE))

    for i in range(0, TILESIZE, animationSpeed):
        # 显示方块移动的动画
        checkForQuit()
        DISPLAYSURF.blit(baseSurf, (0, 0))
        if direction == UP:
            drawTile(movex, movey, board[movex][movey], 0, -i)
        if direction == DOWN:
            drawTile(movex, movey, board[movex][movey], 0, i)
        if direction == LEFT:
            drawTile(movex, movey, board[movex][movey], -i, 0)
        if direction == RIGHT:
            drawTile(movex, movey, board[movex][movey], i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def splashscreen(word1,word2,msg):

    # 显示拼图界面
    board = getStartingBoard()
    drawBoard(board, msg)
    pygame.display.update()
    # 为动画复制一个新画布baseSurf
    baseSurf = DISPLAYSURF.copy()
    # 计算显示位置
    left, top = getLeftTopOfTile(0, 0)    
    width = BOARDWIDTH * TILESIZE
    height = BOARDHEIGHT * TILESIZE
    lastMove = None
    for multicolor in (RED,BRIGHTBLUE,GREEN,GRAY)*20:
        # 在新画布上显示图片并循环显示彩色边框10秒        
        pygame.draw.rect(baseSurf, multicolor, (left - 10, top - 10, width + 21, height + 21))
        baseSurf.blit(PUZZLE_IMG, (left, top))
                
        # 显示自由运动的【完美拼图】字样        
        blankx, blanky = getBlankPosition(board)
        tileLeft, tileTop = getLeftTopOfTile(blankx, blanky) 
        textSurf = TILEFONT.render(word1, True, multicolor)
        textRect = textSurf.get_rect()
        textRect.center = (tileLeft+TILESIZE//2,tileTop+TILESIZE//4)    
        baseSurf.blit(textSurf, textRect)
        textSurf = TILEFONT.render(word2, True, multicolor)
        textRect = textSurf.get_rect()
        textRect.center = (tileLeft+TILESIZE//2,tileTop+TILESIZE//4*3)    
        baseSurf.blit(textSurf, textRect)
        
        pygame.draw.rect(baseSurf, multicolor, (tileLeft+5, tileTop+5, TILESIZE-11, TILESIZE-11),3)
    
        move = getRandomMove(board, lastMove)
        makeMove(board, move)
        lastMove = move
        
        #更新显示
        DISPLAYSURF.blit(baseSurf, (0, 0))
        pygame.display.update()   
        
        # 按任意键退出
        checkForQuit()
        isbreak = False
        for event in pygame.event.get(): # 事件（event）检查循环
            if event.type in (MOUSEBUTTONUP,KEYUP):
                isbreak = True 
        if isbreak:
            break
        pygame.time.delay(500)

def generateNewPuzzle(numSlides):
    # 从原图经过预定次数（numSlides）的移动生成新的拼图puzzle
    sequence = []
    board = getStartingBoard()
    drawBoard(board, '')
    pygame.display.update()
    pygame.time.wait(500) # 暂停等待500毫秒(ms)
    lastMove = None
    for i in range(numSlides):
        move = getRandomMove(board, lastMove)
        slideAnimation(board, move, '生成新的拼图puzzle...', animationSpeed=int(TILESIZE / 2))
        makeMove(board, move)
        sequence.append(move)
        lastMove = move
    return (board, sequence)


def resetAnimation(board, allMoves, animationSpeed):
    # 退回所有已做的移动（动画效果）
    revAllMoves = allMoves[:] # 获得allMoves的一个copy list
    revAllMoves.reverse()

    for move in revAllMoves:
        if move == UP:
            oppositeMove = DOWN
        elif move == DOWN:
            oppositeMove = UP
        elif move == RIGHT:
            oppositeMove = LEFT
        elif move == LEFT:
            oppositeMove = RIGHT
        slideAnimation(board, oppositeMove, '', animationSpeed)
        makeMove(board, oppositeMove)


if __name__ == '__main__':
    main()