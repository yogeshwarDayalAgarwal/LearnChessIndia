"""
This class is responsible for storing all the information about the current state of a chess game. It will also be
responsible for determing the valid moves at the current state . It will also keep a move log.
"""


class GameState():
    def __init__(self):
        # board is 8*8 2d list. each element of list has 2 character w=white b=black
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunction = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                             'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.movelog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.empassantPossible = ()  # coordinates for the sqare where an empasant capture is possible
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightLog = [CastleRights(self.currentCastlingRights.wks,
                                            self.currentCastlingRights.bks,
                                            self.currentCastlingRights.wqs,
                                            self.currentCastlingRights.bqs)]

    '''
    takes a move as a parameter and executes it (this will not work for castling, pawn promotion, and en-passent)
    '''

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.movelog.append(move)  # log the ove so that we can undo it later
        self.whiteToMove = not self.whiteToMove  # swap player
        # update the king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'  # make it into queen

        # empassant move
        if move.isEmpassantMove:
            self.board[move.startRow][move.endCol] = '--'  # capturing the piece

        # updating enmpassantPossible variable
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:  # only on 2 sqaure pawn advances
            self.empassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.empassantPossible = ()

        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # kingside castle move
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # moves the rook
                self.board[move.endRow][move.endCol + 1] = '--'  # erase the old rook
            else:  # queen side castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # moves the rook
                self.board[move.endRow][move.endCol - 2] = '--'  # erase the old rook
        # update castling rights - whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightLog.append(CastleRights(self.currentCastlingRights.wks,
                                            self.currentCastlingRights.bks,
                                            self.currentCastlingRights.wqs,
                                            self.currentCastlingRights.bqs))

    '''
    undo the last move made
    '''

    def undoMove(self):
        if len(self.movelog) != 0:  # make sure that there is a move to undo
            move = self.movelog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # swap players
            # update the king's location if moved
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo empassant move
            if move.isEmpassantMove:
                self.board[move.endRow][move.endCol] = '--'  # leave empty the landing square
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.empassantPossible = (move.endRow, move.endCol)
            # undo 2 square pawn advance
            if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
                self.empassantPossible = ()

            # undo castling rights
            self.castleRightLog.pop()  # get rid of new castle rights from the move we are undoing
            newRights = self.castleRightLog[-1]  # set the current castle rights to the last one in the list
            self.currentCastlingRights = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # king side
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # queen side
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

    # update the Castle Rights given the move
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRights.bks = False

    '''
    All moves considering checks
    '''

    def getValidMoves(self):
        # temporary storing empassantPossible
        tempEmpassantPossible = self.empassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                        self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        # 1)generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        # 2) for each move, make the move
        for i in range(len(moves) - 1, -1, -1):  # when removing from a list remove backwards general rule of thumb
            self.makeMove(moves[i])
            # 3) generate all opponent's moves
            # 4) for each of your opponent's moves , see if they attack your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])  # 5) if they do attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:  # either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True

        self.empassantPossible = tempEmpassantPossible
        self.currentCastlingRights = tempCastleRights
        return moves

    '''
    Determine if the current player is in checks
    '''

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
    Determine if the enemy can attack the square r, c
    '''

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # square is under attack
                return True
        return False

    '''
        All moves without considering checks
    '''

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of cols in given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunction[piece](r, c, moves)  # calls the appropriate move function based on piece
        return moves

    # Get all the pawn moves for the pawn located at row, col and add these moves to the list
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # white pawn moves
            if self.board[r - 1][c] == "--":  # 1square pawn advance
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # 2 sqaure pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == 'b':  # enemy piece to capture left
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.empassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEmpassantMove=True))
            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == 'b':  # enemy piece too capture right
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.empassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEmpassantMove=True))

        else:  # black pawn movess
            if self.board[r + 1][c] == "--":  # 1square pawn advance
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 sqaure pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))
            # Captures
            if c - 1 >= 0:  # Left side capture
                if self.board[r + 1][c - 1][0] == 'w':  # enemy piece to capture left
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.empassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEmpassantMove=True))
            if c + 1 <= 7:  # Right side capture
                if self.board[r + 1][c + 1][0] == 'w':  # enemy piece too capture right
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.empassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEmpassantMove=True))

    # Get all the Rook moves for the pawn located at row, col and add these moves to the list
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down , right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # enemy piece valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece invalid
                        break
                else:  # off board
                    break

    # Get all the Knight moves for the pawn located at row, col and add these moves to the list
    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # not an ally piece (empty or enemy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    # Get all the Bishop moves for the pawn located at row, col and add these moves to the list
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # 4 diagonals
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):  # bishop can move max of 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # is on the board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # enemy piece valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece invalid
                        break
                else:  # off board
                    break

    # Get all the Queen moves for the pawn located at row, col and add these moves to the list
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    # Get all the King moves for the pawn located at row, col and add these moves to the list
    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # not an ally piece (empty or enemy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    '''
    Generate all valid castle moves for the king at (r,c) and add them to the list of moves
    '''

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return  # can't castle while we are in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (
                not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (
                not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEmpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # pawn promotion setting true or false
        self.isPawnPromotion = False
        if (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7):
            self.isPawnPromotion = True

        # Empassant move
        self.isEmpassantMove = isEmpassantMove
        if self.isEmpassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'
        # castle move
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    '''
    overriding the equals method
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        # you can make it into real chess move db too!!
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
