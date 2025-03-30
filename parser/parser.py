import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""


NONTERMINALS = """
S -> NP VP | NP VP Conj NP VP | NP VP Conj VP
VP -> V | VP NP | V PP | Adv V | VP Adv
NP -> N | Det NP | NP PP | Adj NP
PP -> P NP
"""
grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):

    tokens = nltk.word_tokenize(sentence)
    words = [token.lower() for token in tokens if any(char.isalpha() for char in token)]

    return words


def np_chunk(tree):

    # it will only return the subtrees where the label is "NP" -- and  has no subtrees of NP.
    return list(tree.subtrees(
        lambda tree: tree.label() == "NP"
        and not list(tree.subtrees(lambda sub_tree: sub_tree != tree and sub_tree.label() == "NP"))
    ))


if __name__ == "__main__":
    main()
