
import random


pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p":1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2

knightPositionScores = [[1,1,1,1,1,1,1,1], 
                        [1,2,2,2,2,2,2,1],
                        [1,2,3,3,3,3,2,1],
                        [1,2,3,4,4,3,2,1],
                        [1,2,3,4,4,3,2,1],
                        [1,2,3,3,3,3,2,1],
                        [1,2,2,2,2,2,2,1],
                        [1,1,1,1,1,1,1,1]]

bishopPositionScores = [[4,3,2,1,1,2,3,4], 
                        [3,4,3,2,2,3,4,3],
                        [2,3,4,3,3,4,3,2],
                        [1,2,3,4,4,3,2,1],
                        [1,2,3,4,4,3,2,1],
                        [2,3,4,3,3,4,3,2],
                        [3,4,3,2,2,3,4,3],
                        [4,3,2,1,1,2,3,4]]
queenPositionScores = [[1,1,1,3,1,1,1,1], 
                        [1,2,3,3,3,1,1,1],
                        [1,4,3,3,3,4,2,1],
                        [1,2,3,3,3,2,2,1],
                        [1,2,3,3,3,3,2,1],
                        [1,4,3,3,3,4,2,1],
                        [1,2,3,3,3,1,1,1],
                        [1,1,1,3,1,1,1,1]]

rookPositionScores = [[4,3,4,4,4,4,3,4],
                      [4,4,4,4,4,4,4,4],
                      [1,1,2,3,3,2,1,1],
                      [1,2,3,4,4,3,2,1],
                      [1,2,3,4,4,3,2,1],
                      [1,1,2,2,2,2,2,1],
                      [4,4,4,4,4,4,4,4],
                      [4,3,4,4,4,4,3,4]]

whitePawnPositionScores = [[8,8,8,8,8,8,8,8], 
                        [8,8,8,8,8,8,8,8],
                        [5,6,6,7,7,6,6,5],
                        [2,3,3,5,5,3,3,2],
                        [1,2,3,4,4,3,2,1],
                        [1,1,2,3,3,2,1,1],
                        [1,1,1,0,0,1,1,1],
                        [0,0,0,0,0,0,0,0]]

blackPawnPositionScores = [[0,0,0,0,0,0,0,0],
                           [1,1,1,0,0,1,1,1],
                           [1,1,2,3,3,2,1,1],
                           [1,2,3,4,4,3,2,1],
                           [2,3,3,5,5,3,3,2],
                           [5,6,6,7,7,6,6,5],
                           [8,8,8,8,8,8,8,8],
                           [8,8,8,8,8,8,8,8]]

piecePositionScores = {"N": knightPositionScores, "Q": queenPositionScores, "B":bishopPositionScores, "R": rookPositionScores, "bp": blackPawnPositionScores, "wp": whitePawnPositionScores}

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def findBestMove(gameState,validMoves):
    turnMultiplier = 1 if gameState.whiteToMove else -1
    opponentMinMaxscore = CHECKMATE
    bestMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gameState.makeMove(playerMove)
        opponentsMoves = gameState.getValidMoves()
        opponentMaxscore = -CHECKMATE
        for opponentMove in opponentsMoves:
            gameState.makeMove(opponentMove)
            if gameState.checkMate:
                score = -turnMultiplier * CHECKMATE
            elif gameState.staleMate:
                score = STALEMATE
            else:
                score = -turnMultiplier * scoreMaterial(gameState)

            if score > opponentMaxscore:
                opponentMaxscore = score
                
            gameState.undoMove()
        if opponentMinMaxscore > opponentMaxscore:
            opponentMinMaxscore = opponentMaxscore
            bestMove = playerMove
        gameState.undoMove()
    

    return bestMove


def findMoveNegaMaxAlphaBeta(gameState, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreMaterial(gameState)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gameState.makeMove(move)
        nextMoves = gameState.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gameState, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gameState.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break

    return maxScore


def findBestMoveMinMax(gameState, validMoves):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    
    
    findMoveNegaMaxAlphaBeta(gameState, validMoves, DEPTH, -CHECKMATE, CHECKMATE ,1 if gameState.whiteToMove else -1)
    
    if nextMove == None:
        return findBestMove(gameState, validMoves)

    return nextMove

def findMoveMinMax(gameState, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gameState)
    
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gameState.makeMove(move)
            nextMoves = gameState.getValidMoves()
            score = findMoveMinMax(gameState, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gameState.undoMove()
        return maxScore

    else:
        minScore = CHECKMATE
        for move in validMoves:
            gameState.makeMove(move)
            nextMoves = gameState.getValidMoves()
            score = findMoveMinMax(gameState, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gameState.undoMove()
        return minScore




# Score based on the material

def scoreMaterial(gameState):
    score = 0
    if gameState.checkMate:
        if gameState.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gameState.staleMate:
        return STALEMATE
    score = 0

    for row in range(len(gameState.board)):
        for col in range(len(gameState.board[row])):
            square = gameState.board[row][col]
            if square != "--":
                piecePositionScore = 0
                if square[1] != "K":
                    if square[1] == "p":
                        piecePositionScore = piecePositionScores[square][row][col]
                    else:
                        piecePositionScore = piecePositionScores[square[1]][row][col]
            if square[0] == 'w':
                score += pieceScore[square[1]] + piecePositionScore * 0.1

            elif square[0] == 'b':
                score -= pieceScore[square[1]] + piecePositionScore * 0.1
    
    return score