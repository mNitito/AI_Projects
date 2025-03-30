import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):

        for variable in self.domains:
            values_to_remove = []

            for value in self.domains[variable]:
                if len(value) != variable.length:
                    values_to_remove.append(value)

            for value in values_to_remove:
                self.domains[variable].remove(value)

    def revise(self, x, y):

        overlap = self.crossword.overlaps[x, y]

        if overlap is None:
            return False

        i = overlap[0]
        j = overlap[1]
        revised = False

        domain_x_copy = self.domains[x].copy()

        for value_x in domain_x_copy:
            is_consistent = False

            for value_y in self.domains[y]:
                if value_x[i] == value_y[j]:
                    is_consistent = True
                    break

            if not is_consistent:
                self.domains[x].remove(value_x)
                revised = True

        return revised

    def ac3(self, arcs=None):

        if arcs is None:
            arcs = list(self.crossword.overlaps.keys())

        queue = arcs

        while queue:
            (x, y) = queue.pop(0)

            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False

                for z in self.crossword.neighbors(x):
                    queue.append((z, x))

        return True

    def assignment_complete(self, assignment):

        for var in self.domains:
            if var not in assignment:
                return False

        return True

    def consistent(self, assignment):

        words_used = set()
        for variable in assignment:
            word = assignment[variable]

            # check if the len(domain_value) equal len(variable)
            if len(word) != variable.length:
                return False

            # checking if the domain value is in more than one variable
            if word in words_used:
                return False

            words_used.add(word)

        # check that is no conflict between the neighbours
        for variable in assignment:
            for neighbor in self.crossword.neighbors(variable):

                if neighbor in assignment.keys():

                    overlap = self.crossword.overlaps.get((variable, neighbor))
                    if overlap is None:
                        continue

                    i, j = overlap

                    if assignment[variable][i] != assignment[neighbor][j]:
                        return False

        return True

    def order_domain_values(self, var, assignment):

        values_counter = []

        # getting all the neighbors of the var
        neighbors = self.crossword.neighbors(var)

        # Iterate over every value of the var
        for value in self.domains[var]:
            # initilize a zero counter
            count = 0

            # iterate over every neighbor and check if they valid (not assigned yet)
            for neighbor in neighbors:
                if neighbor not in assignment:
                    # getting the overlap of this neighbor and the var and for sure that for the unassigned var only
                    overlap = self.crossword.overlaps[var, neighbor]

                    if overlap:
                        i, j = overlap

                        # check if this overlap is conisitent or not
                        # looping over neigbor values to see if it is consitent with the variabl of the var
                        for neighbor_value in self.domains[neighbor]:
                            if value[i] != neighbor_value[j]:
                                # increament the count of ruled-out neighbour if we assigned this value to the var
                                count += 1

            values_counter.append((value, count))

        values_counter.sort(key=lambda x: x[1])
        return [value for value, count in values_counter]

    def select_unassigned_variable(self, assignment):

        # Initialize a list to store unassigned variables and their metrics
        unassigned_variables = []

        # getting the unassigned variable
        for variable in self.domains:
            if variable not in assignment:

                # calculate the number of the domain values of this variable
                values_num = len(self.domains[variable])

                # calculate the degree of the variable (no. of neighbors)
                degree = len(self.crossword.neighbors(variable))

                # append the variable's values_num and degree to the unassigned_variables
                unassigned_variables.append((variable, values_num, degree))

        # sorting this according to the min remainig values .. if variables tie in number_values --
        # -- we will order this varible who tied according to the highest degree .. if tied .. then choose random
        unassigned_variables.sort(key=lambda x: (x[1], x[-2]))

        # return the unassigned variable based on our choice
        return unassigned_variables[0][0]

    def backtrack(self, assignment):
        """  this function will assign a value for each var and check if it is consistent and make the 3 constraines if not --
            -- it will call it self again recursively and try to assign another value for this var --
            -- if the domain values ended so it will return None .. indecating that there is no possible solution!  """

        # Check if assignment is complete
        VARIABLES = [var for var in self.domains]
        if len(assignment) == len(VARIABLES):
            return assignment

        # Try a new variable
        var = self.select_unassigned_variable(assignment)
        for value in self.domains[var]:
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
