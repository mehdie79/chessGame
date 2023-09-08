
import socket
import sys
import threading
import time
import GameState

class Client():
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY =(200,200,200)
    highlight = (255, 255, 150)
    
    WIDTH = HEIGHT =512
    DIMENSION = 8
    LOG_WIDTH = 250
    LOG_HEIGHT = HEIGHT
    SQ_SIZE = HEIGHT // DIMENSION
    MAX_FPS = 15

    def __init__(self, p, clock):
        # Fonts
        self.font = p.font.Font(None, 28)
        self.input_font = p.font.Font(None, 24)
        self.ip_text = self.font.render("Enter Server IP:", True, self.WHITE)
        self.port_text = self.font.render("Enter Port #:", True, self.WHITE)
        self.error_text = self.font.render("Invalid input. Please enter valid values.", True, (255, 0, 0))
        # Input rectangles
        self.ip_rect = p.Rect(200, 300, 130, 30)
        self.port_rect = p.Rect(200, 350, 130, 30)
        self.submit_rect = p.Rect(200, 400, 120, 60)
        self.submit_button_text = self.font.render("Submit", True, self.BLACK)
        self.submit_text_rect = self.submit_button_text.get_rect(center=self.submit_rect.center)
        self.submit_button_color = self.GRAY
        self.IMAGE_MULTIPLAYER =  None
        self.p = p
        self.load_multiplayer_image()

        # Input variable
        self.server_ip = ""
        self.port_number = ""
        self.input_active = None
        
        self.gameState = GameState.GameState(self.p, clock)

        self.game_ended = False

        self.other_player_started = False
        self.clock = clock
        self.your_turn = False

        self.other_player_moved = False
        self.other_player_location1_x = None
        self.other_player_location1_y = None
        self.other_player_location2_x = None
        self.other_player_location2_x = None
        

        self.other_player_quit = False
        self.player_quit = False
    
    def connect_server(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # get ip from user
        self.conn.connect((self.server_ip, int(self.port_number)))

    def waiting_to_connect(self, screen):
        text = "Waiting for the player 2 to connect"
        font = self.p.font.SysFont("Helvitca", 32, True, False)
        textObject = font.render(text, 0, self.p.Color("Gray"))
        textLocation = self.p.Rect(0,0, self.WIDTH, self.HEIGHT).move(self.WIDTH / 2 - textObject.get_width()/2, self.HEIGHT/2 - textObject.get_height()/2)
        screen.blit(textObject, textLocation)
        textObject = font.render(text, 0, self.p.Color("Black"))
        screen.blit(textObject, textLocation.move(2,2))

    def process_message(self, msg):
        d_msg = msg.decode()
        command = d_msg.split(" ")
        # ignores irrelevant message

        if command[0] == 'start':    
            print(self.other_player_started)        
            self.other_player_started = True
            
        elif (command[0] == 'your_turn' and command[1] =='w') or (command[0] == "your_turn" and command[1] == "b"):
            self.your_turn = True
    
        elif command[0] == 'other_player_moved':
            self.other_player_moved = True
            self.other_player_location1_x = int(command[1])
            self.other_player_location1_y = int(command[2])
            self.other_player_location2_x = int(command[3])
            self.other_player_location2_y = int(command[4])
            message = "your_turn"
            self.conn.sendall(message.encode('utf-8'))
        elif command[0] == "check_mate":
            self.other_player_moved = True
            
        
        elif command[0] == "stale_mate":
            self.gameState.gameOver = True
            self.other_player_moved = True
            
        elif command[0] == "draw":
            self.other_player_moved = True
           
        elif command[0] == "player_quit":
            self.gameState.gameOver = True
            
            self.other_player_quit = True
            


    def run_client(self):
        self.receive_thread = threading.Thread(target=self.communicate_server)
        self.receive_thread.start()

    def control_client_end_game(self):
        message = ""
        if self.gameState.player_select_menu:
             message = "quit"
             self.game_running = False
             self.game_ended = True
             self.gameState.player_select_menu = False
             self.other_player_quit = False
        elif self.gameState.player_select_restart:
            message = "restart"
            self.gameState.player_select_restart = False
            self.other_player_started = False
            self.other_player_quit = False
        elif self.gameState.player_quit:
            self.game_running = False    
            message = "quit" 
            self.conn.sendall(message.encode('utf-8'))
            self.game_ended = True
            self.player_quit = True
            self.receive_thread.join()
            self.p.quit()
            sys.exit()
        
        self.conn.sendall(message.encode('utf-8'))


    def display_client_game(self, screen):
        self.game_running = True
        while self.game_running:
            if self.other_player_moved:
                
                self.gameState.control_player_clicks(self.other_player_location1_y, self.other_player_location1_x)
                self.gameState.control_player_clicks(self.other_player_location2_y, self.other_player_location2_x)
                if self.gameState.moveMade:
                    
                    if self.gameState.animation:
                        self.gameState.animateMove(screen)
                    self.gameState.validMoves = self.gameState.gs.getValidMoves()
                    self.gameState.moveMade = False
                    self.gameState.animation = False
                    self.gameState.playerClicks = []
                self.other_player_moved = False
            
            if not self.gameState.gameOver:
                for event in self.p.event.get():
                    if event.type == self.p.QUIT:
                        self.game_running = False    
                        message = "player_quit" 
                        self.conn.sendall(message.encode('utf-8'))
                        self.game_ended = True
                        self.player_quit = True
                        self.receive_thread.join()
                        self.p.quit()
                        sys.exit()
                        

                        #self.p.quit()
                        # wait until thread is completely executed
                        
                        #self.receive_thread.join()
                            # if not self.server.server_already_running:
                            #     self.server.server_thread.join()
                        
                        #sys.exit()
           

                    if self.your_turn and not self.other_player_moved and not self.gameState.gs.checkMate:
                        
                        # Mouse Handler
                        if event.type == self.p.MOUSEBUTTONDOWN:     
                            location = self.p.mouse.get_pos()
                            self.gameState.control_player_clicks(location[0], location[1])
                    
                    
                        if self.gameState.moveMade:
                            if self.gameState.animation:
                                self.gameState.animateMove(screen)
                            self.gameState.validMoves = self.gameState.gs.getValidMoves()
                            self.gameState.moveMade = False
                            self.gameState.animation = False
                            self.your_turn = False
                            
                            message = "mouse_button_down" + " " + str(self.gameState.playerClicks[0][0] * self.SQ_SIZE) + " " + str(self.gameState.playerClicks[0][1]* self.SQ_SIZE) + " " + str(self.gameState.playerClicks[1][0]* self.SQ_SIZE) + " " + str(self.gameState.playerClicks[1][1]* self.SQ_SIZE)
                            
                            self.conn.sendall(message.encode('utf-8'))
                            self.gameState.playerClicks = []
                        if self.gameState.gs.checkMate:
                            self.gameState.gameOver = True
                            if self.gameState.gs.whiteToMove:
                                message = "check_mate" + " " + "b"
                                self.conn.sendall(message.encode('utf-8'))
                            else:
                                message = "check_mate" + " " + "w"
                                self.conn.sendall(message.encode('utf-8'))
                                
                        elif self.gameState.gs.staleMate:
                            message = "stale_mate"
                            self.conn.sendall(message.encode('utf-8'))
                        elif self.gameState.gs.draw:
                            message = "draw"
                            self.conn.sendall(message.encode('utf-8'))
                

            self.gameState.drawGameState(screen)
            

            if self.other_player_quit:
                self.gameState.controlEndPageButtonColor()
                self.control_client_end_game()
                self.gameState.drawEndGamePage(screen, "You won the second player resigned")

            if self.gameState.gs.checkMate:
                    self.gameState.gameOver = True
                    # self.game_running = False
                    self.gameState.controlEndPageButtonColor()
                    self.control_client_end_game()
                    if self.gameState.gs.whiteToMove:
                        self.gameState.drawEndGamePage(screen, "Black Wins by Checkmate")
                    else:
                        self.gameState.drawEndGamePage(screen, "White Wins by Checkmate")
            elif self.gameState.gs.staleMate:
                    # self.game_running = False
                    self.gameState.controlEndPageButtonColor()
                    self.control_client_end_game()
                    self.gameState.drawEndGamePage(screen, "Stalemate")
            elif self.gameState.gs.draw:
                    self.gameState.controlEndPageButtonColor()
                    self.control_client_end_game()
                    self.gameState.drawEndGamePage(screen, "Draw")


            if not self.other_player_started:
                self.waiting_to_connect(screen)

            self.clock.tick(self.MAX_FPS)
            self.p.display.flip()

    # receive message from server
    def communicate_server(self):
    
        self.connect_server()

        # we need to end this thread, by a signal
        while not self.game_ended:
            try:
                data = self.conn.recv(1024)
                if self.game_ended:
                    break
                # process message
                self.process_message(data)
            except:
                pass
        # close the connection
        self.conn.close()

    def load_multiplayer_image(self):
        self.IMAGE_MULTIPLAYER = self.p.transform.scale(self.p.image.load("images/multiplayer_image.jpg"), (self.WIDTH + self.LOG_WIDTH, self.HEIGHT))

    def get_server_info(self, screen):
        submit_clicked = False
        error_message = ""    
        while not submit_clicked:
            for event in self.p.event.get():
                if event.type == self.p.QUIT:
                    self.p.quit()
                    sys.exit()
                if event.type == self.p.MOUSEMOTION:
                    if self.submit_rect.collidepoint(event.pos):
                        self.submit_button_color = self.highlight
                    else:
                        self.submit_button_color = self.GRAY


                if event.type == self.p.MOUSEBUTTONDOWN:
                    if self.ip_rect.collidepoint(event.pos):
                        self.input_active = "ip"
                    elif self.port_rect.collidepoint(event.pos):
                        self.input_active = "port"
                    elif self.submit_rect.collidepoint(event.pos):
                        if self.server_ip and self.port_number.isdigit():
                            submit_clicked = True
                        else:
                            error_message = "Invalid input. Please enter valid values."
                            
                    else:
                        self.input_active = None
                        error_message  = ""

                if event.type == self.p.KEYDOWN:
                    if self.input_active == "ip":
                        if event.key == self.p.K_RETURN:
                            self.input_active = "port"
                        elif event.key == self.p.K_BACKSPACE:
                            self.server_ip = self.server_ip[:-1]
                        else:
                            self.server_ip += event.unicode
                    elif self.input_active == "port":
                        if event.key == self.p.K_RETURN:
                            try:
                                self.port_number = int(self.port_number)
                            except ValueError:
                                self.port_number = ""
                            self.input_active = None
                        elif event.key == self.p.K_BACKSPACE:
                            self.port_number = self.port_number[:-1]
                        else:
                            self.port_number += event.unicode

            screen.blit(self.IMAGE_MULTIPLAYER, self.p.Rect(0,0, self.WIDTH + self.LOG_WIDTH, self.HEIGHT))

            
            self.p.draw.rect(screen, self.WHITE, self.ip_rect)
            
            self.p.draw.rect(screen, self.WHITE, self.port_rect)

            
           
            corner_radius = 12
            self.p.draw.rect(screen, self.submit_button_color, self.submit_rect, border_radius=corner_radius)

            screen.blit(self.ip_text, (50, 300))
            screen.blit(self.port_text, (50, 350))
            screen.blit(self.input_font.render(self.server_ip, True, self.BLACK), (self.ip_rect.x + 10, self.ip_rect.y + 5))
            screen.blit(self.input_font.render(str(self.port_number), True, self.BLACK), (self.port_rect.x + 10, self.port_rect.y + 5))


            if error_message:
                print("Here")
                screen.blit(self.error_text, (350, 320))

            
            
            screen.blit(self.submit_button_text, self.submit_text_rect)

            self.p.display.flip()

            if error_message:
                time.sleep(1)
                error_message = ""

        # Go to the next phase of the game
        if submit_clicked:
            print("Server IP:", self.server_ip)
            print("Port Number:", self.port_number)
            print("Proceeding to the next phase of the game...")



