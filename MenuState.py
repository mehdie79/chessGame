import Server
import Client
import GameState

import sys
class MenuState():
    WIDTH = HEIGHT =512
    DIMENSION = 8
    LOG_WIDTH = 250
    LOG_HEIGHT = HEIGHT
    SQ_SIZE = HEIGHT // DIMENSION
    MAX_FPS = 15

    white = (255, 255, 255)
    black = (0, 0, 0)
    gray = (200, 200, 200)
    highlight = (255, 255, 150)
    history_background_color = (230, 191, 131)

    def __init__(self,p, clock):
        self.p = p
        self.image_menu, self.history_image = self.loadMenuImage()
        self.button_color_1= self.gray
        self.button_color_2= self.gray
        self.button_color_3= self.gray
        self.button_color_4= self.gray
        self.button_rect_1, self.button_text_1, self.button_text_rect_1= self.createMenuButton(150, 130, 250,70, "Play vs Computer", 24)
        self.button_rect_2, self.button_text_2, self.button_text_rect_2= self.createMenuButton(150, 260, 250,70, "Play vs Human", 24)
        self.button_rect_3, self.button_text_3, self.button_text_rect_3= self.createMenuButton(150, 390, 250,70, "Chess History", 24)
        self.history_rect, self.chess_history = self.chessHistoryMenu()
        self.button_rect_4, self.button_text_4, self.button_text_rect_4= self.createMenuButton(20, 360, 200,70, "Return to Main menu", 18) 
        self.running= True
        self.isGameRunning = False
        self.isMenuRunning = True
        self.isHistoryMenuRunning = False
        self.clock = clock

        self.multiplayer_running = False
        self.gameState = GameState.GameState(self.p, self.clock)
        


    def menu_control_user_selection(self, screen):
        if self.isMenuRunning:
            #print("RUN MENU")
            self.runMenu(screen)
        elif self.gameState.running:
            
            self.gameState.runGame(screen)
            if not self.gameState.running:
                self.isMenuRunning = True
            if self.gameState.player_quit:
                self.running = False
                
        elif self.isHistoryMenuRunning:
            self.runChessHistoryMenu(screen)

    def run_multiplayer(self, screen):
        self.multiplayer_running = True
        self.server = Server.Server(self.p, self.clock)
        if not self.server.server_already_running:
            self.server.start_server()
        self.client = Client.Client(self.p, self.clock)
        self.client.get_server_info(screen)
        self.client.run_client(screen)
        self.client.display_client_game(screen)

        # if not self.server.server_already_running:
        #     self.server.server_thread.join()
        self.client.receive_thread.join()
        
    def runMenu(self, screen):
        self.drawMenuState(screen)
        for e in self.p.event.get():
            if e.type== self.p.QUIT:
                self.p.quit()
                sys.exit()
            if e.type == self.p.MOUSEMOTION:
                if self.button_rect_1.collidepoint(e.pos):
                    self.button_color_1 = self.highlight
                else:
                    self.button_color_1 = self.gray
                if self.button_rect_2.collidepoint(e.pos):
                    self.button_color_2 = self.highlight
                else:
                    self.button_color_2 = self.gray
                if self.button_rect_3.collidepoint(e.pos):
                    self.button_color_3 = self.highlight
                else:
                    self.button_color_3 = self.gray
                    
            elif e.type == self.p.MOUSEBUTTONUP:
                if self.button_rect_1.collidepoint(e.pos):
                    self.gameState.running = True
                    self.isMenuRunning = False
                elif self.button_rect_2.collidepoint(e.pos):
                    self.run_multiplayer(screen)
                elif self.button_rect_3.collidepoint(e.pos):
                    self.isMenuRunning = False
                    self.isHistoryMenuRunning = True


    def runChessHistoryMenu(self, screen):
        self.drawHistoryMenuState(screen)
        for e in self.p.event.get():
            if e.type== self.p.QUIT:
                self.running = False
            elif e.type == self.p.MOUSEMOTION:
                if self.button_rect_4.collidepoint(e.pos):
                    self.button_color_4 = self.highlight
                else:
                    self.button_color_4 = self.gray
                    
            elif e.type == self.p.MOUSEBUTTONUP:
                if self.button_rect_4.collidepoint(e.pos):
                    self.running = True
                    self.isMenuRunning = True 
                    self.isHistoryMenuRunning = False
                    self.button_color_4 = self.gray      

    def createMenuButton(self, pos_x, pos_y, width, height, text, font_size):
        # Font
        font = self.p.font.SysFont("Arial", font_size, True, False)
        
        button_rect = self.p.Rect(pos_x, pos_y, width, height)
        button_text = font.render(text, True, self.black)
        button_text_rect = button_text.get_rect(center=button_rect.center)

        return button_rect, button_text,button_text_rect


    def chessHistoryMenu(self):
        font = self.p.font.SysFont("Arial", 12, True, False)
        history_rect = self.p.Rect(0, 0, self.WIDTH+ self.LOG_WIDTH, self.HEIGHT)
        chess_history = """
        Chess is a two-player strategy board game that traces its origins back to ancient India, around the 6th century. It was known as "chaturanga" and was played on an 8x8 grid with different pieces representing infantry, cavalry, elephants, and chariots.

        Over the centuries, the game evolved and spread to various cultures, each adapting its rules and pieces. In the 15th century, chess underwent significant changes in Europe, including the introduction of the powerful queen and the modern rules governing movement.

        The Staunton design, a standardized set of chess pieces, was introduced in the 19th century by Howard Staunton, a British chess player. This design is still widely recognized and used today.

        With the advent of computers, chess experienced a new era. In 1997, IBM's Deep Blue defeated world champion Garry Kasparov in a historic match, showcasing the potential of artificial intelligence in gaming.

        In recent years, computer engines like Stockfish and AlphaZero have demonstrated remarkable prowess in chess, refining strategies and contributing to the game's theory. These engines employ complex algorithms and deep neural networks to evaluate positions and make optimal moves.

        Today, chess is enjoyed by millions of players worldwide, from casual enthusiasts to professional players competing in international tournaments. It remains a fascinating blend of strategy, skill, and creativity, showcasing the rich history of human intellectual development.
        """
        words = chess_history.split()
        self.wrapped_lines = []
        self.current_line = ''
        for word in words:
            test_line = self.current_line + word + ' '
            font = self.p.font.SysFont("Arial", 14, True, False)
            test_surface = font.render(test_line, True, self.white)
            if test_surface.get_width() <= (self.WIDTH + self.LOG_WIDTH) -20 :
                self.current_line = test_line
            else:
                self.wrapped_lines.append(self.current_line)
                self.current_line = word + ' '
        
        self.wrapped_lines.append(self.current_line)


        return history_rect, chess_history

        
        

    def loadMenuImage(self):
        IMAGE_MENU = self.p.transform.scale(self.p.image.load("images/menu_image.jpg"), (self.WIDTH + self.LOG_WIDTH, self.HEIGHT))
        IMAGE_HISTORY_MENU = self.p.transform.scale(self.p.image.load("images/history_image.jpg"), (self.WIDTH + self.LOG_WIDTH, self.HEIGHT))
        return IMAGE_MENU, IMAGE_HISTORY_MENU

    def drawMenuState(self, screen):
        
        screen.blit(self.image_menu, self.p.Rect(0,0, self.WIDTH + self.LOG_WIDTH, self.HEIGHT))

        # Corner radius
        corner_radius = 15
        self.p.draw.rect(screen, self.button_color_1, self.button_rect_1, border_radius=corner_radius)
        screen.blit(self.button_text_1, self.button_text_rect_1)

        self.p.draw.rect(screen, self.button_color_2, self.button_rect_2, border_radius=corner_radius)
        screen.blit(self.button_text_2, self.button_text_rect_2)

        self.p.draw.rect(screen, self.button_color_3, self.button_rect_3, border_radius=corner_radius)
        screen.blit(self.button_text_3, self.button_text_rect_3)

        font = self.p.font.SysFont("Arial", 36, True, False)
        welcome_text = font.render("Welcome to Chess Master", True, (255,255,255))
        text_x = (self.WIDTH + self.LOG_WIDTH - welcome_text.get_width()) // 2
        text_y =  40
        screen.blit(welcome_text, (text_x, text_y))

    def drawHistoryMenuState(self, screen):
        screen.blit(self.history_image, self.p.Rect(0,0, self.WIDTH + self.LOG_WIDTH, self.HEIGHT))
        font = self.p.font.SysFont("Arial", 14, True, False)
        y=20
        for line in self.wrapped_lines:
            text_surface = font.render(line, True, self.white)
            screen.blit(text_surface, (20, y))
            y += 20  # Spacing between lines
        # Corner radius
        corner_radius = 15
        self.p.draw.rect(screen, self.button_color_4, self.button_rect_4, border_radius=corner_radius)
        screen.blit(self.button_text_4, self.button_text_rect_4)

