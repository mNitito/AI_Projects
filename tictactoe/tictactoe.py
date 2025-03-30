"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    count_X = 0
    count_O = 0

    # iterating over every cell in the board
    for row in board:
        for coulmn in row:
            if coulmn == X:
                count_X += 1
            elif coulmn == O:
                count_O += 1

    if count_X > count_O:
        return O
    elif count_O > count_X:
        return X
    # return X if all cells is empty which in this case count_X and count_O are equal
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actiones = set()
    for row in range(len(board)):
        for coulmn in range(len(board)):
            if board[row][coulmn] == EMPTY:
                possible_actiones.add((row, coulmn))
    return possible_actiones


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # making a deepcopy of the boared
    deep_copy_board = copy.deepcopy(board)

    # get the current player from the player(board) function
    current_palyer = player(board)

    # checking if the action is valid
    possible_actions = actions(board)
    if action not in possible_actions:
        raise Exception("This is not a valid action")

    # updating the action(i,j) with the next player (X / O)
    deep_copy_board[action[0]][action[1]] = current_palyer

    # return the deep_copy_board that result from taking action(i,j)
    return deep_copy_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # One can win the game with three of their moves in a row horizontally, vertically, or diagonally.

    # checking horizontally
    for row in board:
        # if every cell in the row equal to the first cell ..
        # (if the condition is true) .. then all() will return True
        if all(cell == row[0] for cell in row) and row[0] != EMPTY:
            return row[0]

    # checking vertically
    for coulmn in range(len(board)):
        if all(board[row][coulmn] == board[0][coulmn] for row in range(len(board))):
            return board[0][coulmn]

    # checking diagonally

    # checking for the left digonal
    if all(board[i][i] == board[0][0] for i in range(len(board))):
        return board[0][0]

    # checking for the right digonal
    # we will try to get the colmn dynimaclly by modifying the row
    if all(board[row][len(board) - 1 - row] == board[0][len(board) - 1] for row in range(len(board))):
        return board[0][len(board) - 1]

    # check for the game if ( is ongoing || ended as a draw )
    for row in board:
        for cell in row:
            # if cell is Empty then the game is not yet ended as a draw
            if cell is EMPTY:
                # return None as found an Empty cell thus game is ongoing
                return None
    # return None as there is no  an Empty cell found thus the game is finished but no one win!
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    terminal_result = winner(board)
    # return true if there is a winner either (X || O)
    if terminal_result != None:
        return True

    for row in board:
        for cell in row:
            if cell is EMPTY:
                # return False as found an Empty cell thus game is ongoing
                return False
    # return True if game is ended as a tie
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    the_winner = winner(board)
    if the_winner == X:
        return 1
    elif the_winner == O:
        return -1
    else:
        return 0

# Note THAT THE MIN_PLAYER(board) && MAX_PLAYER(board) should return the value of the result action to be used in their opponent
# AND it should return the action (best_action)(i,j) to use it in the minimax function


def MIN_PLAYER(board, alpha, beta):
    # if the board is terminal board
    is_terminal = terminal(board)
    if is_terminal:
        return utility(board), None  # Return a tuple with utility value and no action

    # Function Min-Value(state):
    best_action = None
    v = float('inf')
    for action in actions(board):
        # getting only the value(new_value) from the tuple
        new_value, _ = MAX_PLAYER(result(board, action), alpha, beta)
        if new_value < v:
            v = new_value
            best_action = action
        beta = min(beta, v)
        if beta <= alpha:
            break
    return v, best_action  # Return a tuple with the minimum value and the best action


def MAX_PLAYER(board, alpha, beta):
    # if the board is terminal board
    is_terminal = terminal(board)
    if is_terminal:
        return utility(board), None  # Return a tuple with utility value and no action

    # function Max-Value
    best_action = None
    v = float('-inf')
    for action in actions(board):
        # getting only the value(new_value) from the tuple
        new_value, _ = MIN_PLAYER(result(board, action), alpha, beta)
        if new_value > v:
            v = new_value
            best_action = action
        alpha = max(alpha, v)
        if beta <= alpha:
            break
    return v, best_action  # Return a tuple with the maximum value and the best action


def minimax(board, alpha=float('-inf'), beta=float('inf')):
    # if the board is terminal board
    is_terminal = terminal(board)
    if is_terminal:
        return None

    # determining the current player (MAX-PLAYER  || MIN-PLAYER)
    current_player = player(board)
    if current_player == X:
        # getting from the tubel that MAX_PLAYER(board,alpha,beta) will produce the best_action only and not the value with it
        _, best_action = MAX_PLAYER(board, alpha, beta)
        return best_action
    elif current_player == O:
        # getting from the tubel that MAX_PLAYER(board,alpha,beta) will produce the best_action only and not the value with it
        _, best_action = MIN_PLAYER(board, alpha, beta)
        return best_action
