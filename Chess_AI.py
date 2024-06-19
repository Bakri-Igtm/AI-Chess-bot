import random

piece_score = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2

'''
Picks and return a random move
'''
def find_random_moves(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves)-1)]

"""
Find the nest move based on material alone."""
def find_best_move(gstate, valid_moves):
    turn_multiplier = 1 if gstate.whiteToMove else -1
    opponent_minmax_score = CHECKMATE
    best_player_move = None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        gstate.make_move(player_move)
        opponents_moves = gstate.get_valid_moves()
        if gstate.stale_mate:
            opponent_max_score = STALEMATE
        elif gstate.check_mate:
            opponent_max_score = -CHECKMATE
        else:
            opponent_max_score = -CHECKMATE
            for opponent_move in opponents_moves:
                gstate.make_move(opponent_move)
                gstate.get_valid_moves()
                if gstate.check_mate:
                    score = CHECKMATE
                elif gstate.stale_mate:
                    score = STALEMATE
                else:
                    score = -turn_multiplier * score_material(gstate.board)
                if score > opponent_max_score:
                    opponent_max_score = score
                gstate.undoMove()
            if opponent_max_score < opponent_minmax_score:
                opponent_minmax_score = opponent_max_score
                best_player_move = player_move
        gstate.undoMove()
    return best_player_move

'''Helper method to make the first recursive call'''
def find_best_move_(gstate, valid_moves):
    global next_move, counter
    next_move = None
    # find_move_minmax(gstate, valid_moves, DEPTH, gstate.whiteToMove)
    counter = 0
    find_move_negamax_alpha_beta(gstate, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gstate.whiteToMove else -1)
    print(counter)
    return next_move

def find_move_minmax(gstate, valid_moves, depth, whiteToMove):
    global next_move
    if depth == 0:
        return score_material(gstate.board)

    if whiteToMove:
        max_score = -CHECKMATE
        for move in valid_moves:
            gstate.make_move(move)
            next_moves = gstate.get_valid_moves()
            score = find_move_minmax(gstate, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gstate.undoMove()
        return max_score

    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gstate.make_move(move)
            next_moves = gstate.get_valid_moves()
            score = find_move_minmax(gstate, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gstate.undoMove()
        return min_score

def find_move_negamax(gstate, valid_moves, depth, turn_multiplier):
    global next_move, counter
    counter += 1
    if depth == 0:
        return turn_multiplier * score_board(gstate)

    max_score = -CHECKMATE
    for move in valid_moves:
        gstate.make_move(move)
        next_moves = gstate.get_valid_moves()
        score = -find_move_negamax(gstate, next_moves, depth-1, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move

        gstate.undoMove()

    return max_score

def find_move_negamax_alpha_beta(gstate, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move, counter
    counter += 1
    if depth == 0:
        return turn_multiplier * score_board(gstate)

    #move ordering - to be done later
    max_score = -CHECKMATE
    for move in valid_moves:
        gstate.make_move(move)
        next_moves = gstate.get_valid_moves()
        score = -find_move_negamax_alpha_beta(gstate, next_moves, depth-1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move

        gstate.undoMove()
        #pruning
        alpha = max(max_score, alpha)
        if alpha >= beta:
            break

    return max_score
"""
A positive score is good for white, a negative score is good for black"""
def score_board(gstate):
    if gstate.check_mate:
        if gstate.whiteToMove:
            return -CHECKMATE #black wins
        else:
            return CHECKMATE #white wins
    elif gstate.stale_mate:
        return STALEMATE

    score = 0
    for row in gstate.board:
        for square in row:
            if square[0] == 'w':
                score += piece_score[square[1]]
            elif square[0] == 'b':
                score -= piece_score[square[1]]

    return score


"""
Score the board based on material."""

def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += piece_score[square[1]]
            elif square[0] == 'b':
                score -= piece_score[square[1]]

    return score