import ChessEngine
import ChessAI

class GameState():
    WIDTH = HEIGHT =512
    DIMENSION = 8
    LOG_WIDTH = 250
    LOG_HEIGHT = HEIGHT
    SQ_SIZE = HEIGHT // DIMENSION
    MAX_FPS = 15
    IMAGES = {}
    highlight_color = (255, 255, 150)
    gray = (200,200,200)
    black = (0, 0, 0)
   
    def __init__(self, p, clock):
        self.p = p
        self.logFont = p.font.SysFont("Arial", 12, True, False)
        self.gs= ChessEngine.GameState()
        self.validMoves = self.gs.getValidMoves()
        self.moveMade = False
        self.loadImages()
        self.running = False
        self.sqSelected = ()
        self.playerClicks = []
        self.gameOver = False
        self.animation = False
        self.playerOne = True # If it's true we are human false is AI
        self.playerTwo = True # If it's true we are human false is AI
        self.player_quit = False
        self.player_select_restart = False
        self.player_select_menu = False
        self.clock = clock
        self.button_rect_1, self.button_text_1, self.button_text_rect_1= self.createMenuButton(80, 330, 120,60, "Rematch", 24)
        self.button_rect_2, self.button_text_2, self.button_text_rect_2= self.createMenuButton(270, 330, 200,60, "Return to Menu", 24)
        self.button_color_1 = self.gray
        self.button_color_2 = self.gray
    
    '''
    Load the images to the global variable IMAGES
    '''
    def loadImages(self):
        pieces= ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
        for piece in pieces:
            self.IMAGES[piece] = self.p .transform.scale(self.p.image.load("images/"+ piece+ ".png"), (self.SQ_SIZE, self.SQ_SIZE))
    
    def drawText(self, screen, text):
        font = self.p.font.SysFont("Helvitca", 32, True, False)
        textObject = font.render(text, 0, self.p.Color("Gray"))
        textLocation = self.p.Rect(0,0, self.WIDTH, self.HEIGHT).move(self.WIDTH / 2 - textObject.get_width()/2, self.HEIGHT/2 - textObject.get_height()/2)
        screen.blit(textObject, textLocation)
        textObject = font.render(text, 0, self.p.Color("Black"))
        screen.blit(textObject, textLocation.move(2,2))

    def drawGameState(self,screen):
        self.drawBoard(screen)
        self.highlight(screen)

        self.drawPieces(screen)
        self.drawMoveLog(screen)

    def drawBoard(self, screen):
        colors = [self.p.Color("white"), self.p.Color("gray")]
        for r in range(self.DIMENSION):
            for c in range(self.DIMENSION):
                color = colors[((r+c) % 2)]
                self.p.draw.rect(screen, color, self.p.Rect(c*self.SQ_SIZE, r* self.SQ_SIZE, self.SQ_SIZE,self.SQ_SIZE))

    def drawPieces(self, screen):

        for r in range(self.DIMENSION):
            for c in range(self.DIMENSION):
                piece = self.gs.board[r][c]
                if piece != "--":
                    screen.blit(self.IMAGES[piece], self.p.Rect(c* self.SQ_SIZE, r* self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))


    def highlight(self, screen):
        if self.sqSelected == ():
            return
        r, c = self.sqSelected
        if self.gs.board[r][c][0] == ('w' if self.gs.whiteToMove else 'b'):
            s = self.p.Surface((self.SQ_SIZE, self.SQ_SIZE))
            s.set_alpha(150)
            s.fill(self.p.Color('blue'))
            screen.blit(s, (c*self.SQ_SIZE, r*self.SQ_SIZE))
            s.fill(self.p.Color('yellow'))
            for move in self.validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*self.SQ_SIZE, move.endRow*self.SQ_SIZE))

    def drawMoveLog(self,screen):
        moveLogRect = self.p.Rect(self.WIDTH, 0, self.LOG_WIDTH, self.LOG_HEIGHT)
        self.p.draw.rect(screen, self.p.Color("black"), moveLogRect)
        moveTexts = []
        padding = 5
        lineSpacing = 2
        textY = padding
        movePerRow = 3

        for i in range(0, len(self.gs.moveLog), 2):
                
            moveString =  " " + str(i // 2 + 1) + ". " + self.gs.moveLog[i].getChessNotation() + "  "
            if i+1 < len(self.gs.moveLog):
                moveString += self.gs.moveLog[i+1].getChessNotation()
            moveTexts.append(moveString)
                
        for i in range(0, len(moveTexts), movePerRow):
            text = ""
            for j in range(movePerRow):
                if i + j < len(moveTexts):
                    text += moveTexts[i+j]

            textObject = self.logFont.render(text, 1, self.p.Color("white"))
            textLocation = moveLogRect.move(padding, textY)
            screen.blit(textObject, textLocation)
            textY += textObject.get_height() + lineSpacing
    

    def animateMove(self,screen):
        move = self.gs.moveLog[-1]
        colors = [self.p.Color("white"), self.p.Color("gray")]
        dRow = move.endRow - move.startRow
        dColumn = move.endCol - move.startCol

        framesPerSquare = 10
        frameCount = (abs(dRow) + abs(dColumn)) * framesPerSquare
        for frame in range(frameCount + 1):
            r, c = (move.startRow +dRow * frame / frameCount, move.startCol + dColumn * frame / frameCount)
            self.drawBoard(screen)
            self.drawPieces(screen)
            color = colors[(move.endRow + move.endCol)% 2]
            endSquare = self.p.Rect(move.endCol * self.SQ_SIZE, move.endRow * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE)
            self.p.draw.rect(screen, color, endSquare)

            if move.pieceCaptured != '--':
                if move.isEnpassantMove:
                    enpassantRow = (move.endRow +1) if move.pieceCaptured[0] == 'b' else (move.endRow - 1)
                    endSquare = self.p.Rect(move.endCol * self.SQ_SIZE, enpassantRow * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE)
                screen.blit(self.IMAGES[move.pieceCaptured], endSquare)  # Draw the capture piece
            
            screen.blit(self.IMAGES[move.pieceMoved],self.p.Rect(c * self.SQ_SIZE, r * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))
            self.p.display.flip()
            self.clock.tick(60)
    
    def control_player_clicks(self, location_1, location_2):   
        
        col = location_1 // self.SQ_SIZE
        row = location_2 // self.SQ_SIZE
        if self.sqSelected == (row, col) or col >= 8:
            self.sqSelected = ()
            self.playerClicks = []
        else:
            self.sqSelected=(row,col)
            self.playerClicks.append(self.sqSelected)
            if len(self.playerClicks) == 2:
                print(self.playerClicks[0])
                print(self.playerClicks[1])
                move = ChessEngine.Move(self.playerClicks[0], self.playerClicks[1], self.gs.board)
                print(move.getChessNotation())

                for i in range(len(self.validMoves)):
                    if move == self.validMoves[i]:
                        self.gs.makeMove(self.validMoves[i])
                        self.moveMade = True
                        self.animation = True
                        self.sqSelected = ()
                       
                    
                if not self.moveMade:
                    self.playerClicks = [self.sqSelected]

    def resetartGame(self):
        self.gs = ChessEngine.GameState()
        self.validMoves = self.gs.getValidMoves()
        self.sqSelected = ()
        self.playerClicks = []
        self.moveMade = False
        self.animation = False
        self.gameOver = False


    def createMenuButton(self, pos_x, pos_y, width, height, text, font_size):
        # Font
        font = self.p.font.SysFont("Arial", font_size, True, False)
        
        button_rect = self.p.Rect(pos_x, pos_y, width, height)
        button_text = font.render(text, True, self.black)
        button_text_rect = button_text.get_rect(center=button_rect.center)

        return button_rect, button_text,button_text_rect

    def controlEndPageButtonColor(self):
        for e in self.p.event.get():
            # Mouse Handler
            if e.type == self.p.QUIT:
                self.running = False
                self.player_quit = True
            elif e.type == self.p.MOUSEMOTION:
                if self.button_rect_1.collidepoint(e.pos):
                    self.button_color_1 = self.highlight_color
                else:
                    self.button_color_1 = self.gray
                if self.button_rect_2.collidepoint(e.pos):
                    self.button_color_2 = self.highlight_color
                else:
                    self.button_color_2 = self.gray

            elif e.type == self.p.MOUSEBUTTONDOWN:
                if self.button_rect_1.collidepoint(e.pos):
                    self.resetartGame()
                    self.player_select_restart = True
                elif self.button_rect_2.collidepoint(e.pos):
                    self.running = False
                    self.player_select_menu = True
                    self.resetartGame()



    def drawEndGamePage(self, screen, text):
        self.drawText(screen, text)
         # Corner radius
        corner_radius = 15
        self.p.draw.rect(screen, self.button_color_1, self.button_rect_1, border_radius=corner_radius)
        screen.blit(self.button_text_1, self.button_text_rect_1)

        self.p.draw.rect(screen, self.button_color_2, self.button_rect_2, border_radius=corner_radius)
        screen.blit(self.button_text_2, self.button_text_rect_2)
    
    def runGame(self, screen):
        
        humanTurn = (self.gs.whiteToMove and self.playerOne) or(not self.gs.whiteToMove and self.playerTwo)
        if not self.gameOver:
            for e in self.p.event.get():
                if e.type == self.p.QUIT:
                        self.running = False
                        self.player_quit = True
                elif e.type == self.p.MOUSEBUTTONDOWN:
                
                    if humanTurn:
                        location = self.p.mouse.get_pos()
                        
                        self.control_player_clicks(location[0], location[1])     
                        # Key Handler
                elif e.type == self.p.KEYDOWN:
                    if e.key == self.p.K_z:
                        self.gs.undoMove()
                        self.moveMade = True
                        self.animation = False
                        self.gameOver = False
                    if e.key == self.p.K_r: # Resets the game
                        self.resetartGame()
        if not self.gameOver and not humanTurn:
            AIMove = ChessAI.findBestMoveMinMax(self.gs,self.validMoves)
            self.gs.makeMove(AIMove)
            self.moveMade = True
            self.animation = True

        if self.moveMade:
            if self.animation:
                self.animateMove(screen)
            self.validMoves = self.gs.getValidMoves()
            self.moveMade = False
            self.animation = False
            self.playerClicks = []

        
        self.drawGameState(screen)
        
        if self.gs.checkMate:
            self.gameOver = True
            self.controlEndPageButtonColor()
            if self.gs.whiteToMove:
                
                self.drawEndGamePage(screen, "Black Wins by Checkmate")
            else:
                self.drawEndGamePage(screen, "White Wins by Checkmate")
        elif self.gs.staleMate:
            self.controlEndPageButtonColor()
            self.gameOver = True
            self.drawEndGamePage(screen, "Stalemate")
        
        if self.gs.draw:
            self.gameOver = True
            self.controlEndPageButtonColor()
            self.drawEndGamePage(screen, "Draw")
            

        
        self.clock.tick(self.MAX_FPS)
    
      
    