"""Driver File. Responsible for handling user input and current game state"""

import pygame as p
import Chess_Engine, Chess_AI
from multiprocessing import Process, Queue
import asyncio

# p.init()
BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15 #for animations
IMAGES = {}

"""
Initialize a global dict of images and will be called exactly once
"""
def load_images():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #We can access an image by using the dictionary

"""
Main driver for the code.
Handles user input and updates the graphics"""

async def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    p.display.set_caption("Chess")
    icon = p.image.load("bp.png")
    p.display.set_icon(icon)
    move_log_font = font = p.font.SysFont("comicsansms", 14, False, False)
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gstate = Chess_Engine.GameState()
    valid_moves = gstate.get_valid_moves()
    move_made = False #flag for when a move is made
    animate = False #flag to animate
    load_images() #Done only once before while loop
    game_is_on = True
    selected_square = ()
    playerClicks = [] #Keep track of player clicks
    game_over = False
    player_1 = False #If a human is playing white, it'd be true
    player_2 = True #same as above but for black
    AI_thinking = False
    move_finder_process = None
    move_undone = False


    while game_is_on:
        human_turn = (gstate.whiteToMove and player_1) or (not gstate.whiteToMove and player_2)
        for e in p.event.get():
            if e.type == p.QUIT:
                game_is_on = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos() #mouse location (x, y)
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if selected_square == (row, col) or col >= 8: #User clicked on the same square twice
                        selected_square = () #deselect
                        playerClicks = [] #Clear player clicks
                    else:
                        selected_square = (row, col)
                        playerClicks.append(selected_square) #append for both clicks
                    if len(playerClicks) == 2 and human_turn: #after 2nd click
                        move = Chess_Engine.Move(playerClicks[0], playerClicks[1], gstate.board)
                        #print(move.get_chess_notation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gstate.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                selected_square = () #reset player clicks
                                playerClicks = []

                        if not move_made:
                            playerClicks = [selected_square]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #Undo a move when the letter z is pressed
                    gstate.undoMove()
                    selected_square = ()
                    playerClicks = []
                    move_made = True
                    animate = False
                    game_over = False
                    if AI_thinking:
                        move_finder_process.terminate()
                        AI_thinking = False
                    move_undone = True

                if e.key == p.K_r: #reset the board when 'r' is pressed
                    gstate = Chess_Engine.GameState()
                    valid_moves = gstate.get_valid_moves()
                    selected_square = ()
                    playerClicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if AI_thinking:
                        move_finder_process.terminate()
                        AI_thinking = False
                    move_undone = True

        #AI move
        if not game_over and not human_turn and not move_undone:
            if not AI_thinking:
                AI_thinking = True
                print("Thinking...")
                return_queue = Queue()
                move_finder_process = Process(target=Chess_AI.find_best_move_, args=(gstate, valid_moves, return_queue))
                move_finder_process.start() #call
                # AI_move = Chess_AI.find_best_move_(gstate, valid_moves)
            if not move_finder_process.is_alive():
                print("done")
                AI_move = return_queue.get()
                if AI_move is None:
                    AI_move = Chess_AI.find_random_moves(valid_moves)
                gstate.make_move(AI_move)
                move_made = True
                animate = True
                AI_thinking = False

        if move_made:
            if animate:
                animate_move(gstate.movelog[-1], screen, gstate.board, clock)
            valid_moves = gstate.get_valid_moves()
            move_made = False
            animate = False
            move_undone = False

        draw_stage(screen, gstate, valid_moves, selected_square, move_log_font)

        if gstate.check_mate or gstate.stale_mate:
            game_over = True
            if gstate.stale_mate:
                text = '.....Stalemate.....'
            else:
                if gstate.whiteToMove:
                    text = 'Checkmate..... Black wins .....'

                else:
                    text = 'Checkmate..... White wins .....'

            draw_end_game_text(screen, text)


        clock.tick(MAX_FPS)
        p.display.flip()
        await asyncio.sleep(0)
"""
Responsible for all the graphics within a current game state"""
def draw_stage(screen, gstate, valid_moves, sq_selected, move_log_font):
    draw_board(screen) #draw the squares on the board
    highlight_squares(screen, gstate, valid_moves, sq_selected)
    draw_pieces(screen, gstate.board) #draw pieces on top of the squares
    draw_move_log(screen, gstate, move_log_font)

""""Draws the squares on the board"""
def draw_board(screen):
    global colors
    colors = [p.Color("white"), p.Color("grey")]

    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""Highlight square selected and moves for piece selected"""

def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"): #sq_selected is a piece that can be moved
            #highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #transparency value. 0 transparent fully, 255 opaque fully
            s.fill(p.Color('brown4'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color('bisque2'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col*SQ_SIZE, move.end_row*SQ_SIZE))


"""Draws the pieces on the board using the current GameState.board"""
def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]

            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(col*SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
"""
Draws the move log
"""
def draw_move_log(screen, gstate, font):
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("beige"), move_log_rect)
    move_log = gstate.movelog
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i//2 + 1) + "." + str(move_log[i]) + " "
        if i + 1 < len(move_log): #ensuring black made a move
            move_string += str(move_log[i+1]) + " "
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i+j]
        text_object = font.render(text, True, p.Color('black'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height()

"""Animating a move"""
def animate_move(move, screen, board, clock):
    global colors
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    frames_per_square = 10 #frames to move one square
    frames_count = (abs(dR) + abs(dC)) * frames_per_square

    for frame in range(frames_count+1):
        r, c = (move.start_row + dR*frame/frames_count, move.start_col + dC*frame/frames_count)
        draw_board(screen)
        draw_pieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        #draw captured piece onto rectangle
        if move.place_captured != "--":
            if move.is_enpassent_move:
                en_passent_row = move.end_row + 1 if move.place_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_col * SQ_SIZE, en_passent_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.place_captured], end_square)

        #draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(80)

def draw_end_game_text(screen, text):
    font = p.font.SysFont("comicsansms", 32, True, False)
    text_object = font.render(text, 0, p.Color('Gray'))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2, BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color('Black'))
    screen.blit(text_object, text_location.move(2, 2))


if __name__ == "__main__":
    asyncio.run(main())
