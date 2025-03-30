from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # TODO

    # encoding the statement
    # And(AKnight, AKnave)

    # the strcture (rules)
    Or(AKnight, AKnave),  # A can be either AKnight or ANave
    Not(And(AKnight, AKnave)),  # But can not be both

    # encoding the information we have
    # if AKnight then he sopkes truth .. if AKnave then he lies

    # if AKnight then [And(AKnight,AKnave)] must be true .. which in the fact it is not be true -
    # - since the rules we wrote up
    Implication(AKnight, And(AKnight, AKnave)),

    # if AKnave the [And(AKnight,AKnave)] must not be true
    Implication(AKnave, Not(And(AKnight, AKnave)))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # TODO

    # rules
    Or(AKnight, AKnave),         # A is a Knight either A is a Knave
    Not(And(AKnight, AKnave)),   # but not both
    Or(BKnight, BKnave),         # B is a Knight either B is a Knave
    Not(And(BKnight, BKnave)),   # but not both

    # information

    # if Aknave then (And(AKnave,BKnave)) must be false and also B must be knight
    Implication(AKnave, Not(And(AKnave, BKnave))),

    # if Aknight then (And(AKnave,BKnave)) must be true which will not ..  and also B must be knave
    Implication(AKnight, (And(AKnave, BKnave))),

    # Additional  information for more (accuracy)
    Implication(AKnave, BKnight),
    Implication(AKnight, BKnave)

)


# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # TODO

    # rules
    Or(AKnight, AKnave),         # A is a Knight either A is a Knave
    Not(And(AKnight, AKnave)),   # but not both
    Or(BKnight, BKnave),         # B is a Knight either B is a Knave
    Not(And(BKnight, BKnave)),   # but not both

    # encoding the information

    # the information from A
    Implication(AKnight, And(AKnight, BKnight)),
    Implication(AKnave, Not(And(AKnave, BKnave))),

    # the information from B
    Implication(BKnight, And(Or(AKnight, BKnight), Not(And(AKnight, BKnight)))),
    Implication(BKnave, Not(And(Or(AKnight, BKnight), Not(And(AKnight, BKnight)))))

)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # TODO

    # rules
    Or(AKnight, AKnave),         # A is a Knight either A is a Knave
    Not(And(AKnight, AKnave)),   # but not both
    Or(BKnight, BKnave),         # B is a Knight either B is a Knave
    Not(And(BKnight, BKnave)),   # but not both
    Or(CKnight, CKnave),         # C is a Knight either C is a Knave
    Not(And(CKnight, CKnave)),   # but not both


    # Encoding the knowlage

    # A says either "I am a knight." or "I am a knave.", but you don't know which.
    Implication(AKnight, Or(AKnight, AKnave)),
    Implication(AKnave, Or(AKnight, AKnave)),


    # B says "A said 'I am a knave'."


    # since (BKNight) (Says the truth), Then actually (A) said i'am a Knave, Also, Since (BKnight), Then indeed (A) is Knave ---
    # --- Since (AKnave) (does not says the truth), Thus (A) must not be a (knave) As he said
    Implication(BKnight, Not(AKnave)),

    # Since BKnave (Says lies), Then A does not Says i'am a Knave .. Then (A) does not a Knave, i.e: indeed (A) is Knight
    Implication(BKnave, Not(AKnave)),

    # B says "C is a knave."
    Implication(BKnight, CKnave),
    Implication(BKnave, Not(CKnave)),

    # C says "A is a knight."
    Implication(CKnight, AKnight),
    Implication(CKnave, Not(AKnight))

)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
