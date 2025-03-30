import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        mine_cell = set()
        if self.count == len(self.cells):
            for cell in self.cells:
                mine_cell.add(cell)
        return mine_cell

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        safe_cell = set()
        if self.count == 0:
            for cell in self.cells:
                safe_cell.add(cell)
        return safe_cell

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def neighbors_cell(self, cell):
        neighbors_cell = set()
        row, col = cell
        count_mines = 0

        # looping over the row (before) and the (current) row and the row (after) [the current cell]
        for i in range(row - 1, row + 2):
            # looping over the coulmn (before) and the (current) coulmn and the coulmn (after) [the current cell]
            for j in range(col - 1, col + 2):

                # ignore the cell it self
                if (i, j) == cell:
                    continue

                # check if the current neigbour is a mine .. if it is then increase the count by 1
                if (i, j) in self.mines:
                    count_mines += 1

                # adding to the neighbors
                # check if the cell is within bounds
                if 0 <= i < self.height and 0 <= j < self.width:
                    # add the neighbor_cell to neighbors_cell if it is not in the (mines or safes) set
                    if (i, j) not in self.mines and (i, j) not in self.safes:
                        neighbors_cell.add((i, j))

        return neighbors_cell, count_mines

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """

        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        self.mark_safe(cell)

        # 3) add a new sentence to the AI's knowledge base

        # getting the neighbors cells of the current cell and the count_mines
        undetermined_neighbors, count_mines = self.neighbors_cell(cell)
        new_sentence_cells = set()

        # looping over the undetermined_neighbors and added to the new_sentence_cells
        for neighbor in undetermined_neighbors:
            new_sentence_cells.add(neighbor)

        # check if new_sentence_cells has cell inside to avoide error
        if new_sentence_cells:
            self.knowledge.append(Sentence(new_sentence_cells, count - count_mines))

            # 4) loop over every sentence in KB and ---
            # --- mark any additional cells as safe or as mines to infer ---
            # --- any additional knowledge ( only if we can [mark cell as (mine || safe)])

            inferenced_needed = True
            while inferenced_needed:

                # setting it to false because to make sure to iterate over every sentence one times---
                # --- if there is no cell can marked as a (mine or cell)
                inferenced_needed = False

                for sentence in self.knowledge:
                    if sentence.known_mines():
                        for cell in sentence.known_mines().copy():
                            self.mark_mine(cell)
                            inferenced_needed = True

                    if sentence.known_safes():
                        for cell in sentence.known_safes().copy():
                            self.mark_safe(cell)
                            inferenced_needed = True

            # 5) add any new sentences to the AI's knowledge base
            # if they can be inferred from existing knowledge
            # Note: this can made by the (subset method)

            # Create a list to store new sentences
            new_sentences = []

            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    if sentence1 != sentence2 and sentence1.cells.issubset(sentence2.cells):
                        new_cells = sentence2.cells - sentence1.cells
                        new_count = sentence2.count - sentence1.count
                        infer_sentence = Sentence(new_cells, new_count)
                        if infer_sentence not in self.knowledge:
                            new_sentences.append(infer_sentence)

            self.knowledge.extend(new_sentences)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # choose a cell from the safe cells (self.safes)
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
         # return none .. if no safe_cell to pick up!
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # creating a list to append all cells that are valid
        random_cell = []

        # looping over every cell in the board
        for row in range(self.height):
            for col in range(self.width):
                cell = (row, col)
                # check if this cell has not been choosen before and not mine
                if cell not in self.moves_made and cell not in self.mines:
                    random_cell.append(cell)

        # choose random from the valid cells
        random_choosen_cell = random.choice(random_cell)
        return random_choosen_cell
