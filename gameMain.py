"""
This is the Main drive file.
"""

import pygame as p
import ChessEngine as ChessEngine
import MenuState
import sys




WIDTH = HEIGHT =512
DIMENSION = 8
LOG_WIDTH = 250
LOG_HEIGHT = HEIGHT
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15

    
    
    

   



def main():
    p.init()
    p.display.set_caption("Chess Master")
    screen = p.display.set_mode((WIDTH + LOG_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    menuState = MenuState.MenuState(p, clock)
    

    while menuState.running: 
        menuState.menu_control_user_selection(screen)
        
        p.display.flip()




if __name__ == "__main__":
    main()

