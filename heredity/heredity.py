import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def parent_prob_pass_theGene(parent, one_gene, two_genes):
    if parent in two_genes:
        # if parent has 2 genes so he likely will pass a gene with 1.00 - 0.01(mutation_gene)
        return 1 - PROBS["mutation"]
    elif parent in one_gene:
        # if parent has 1 gene .. likely he may pass a gene with 0.5
        return 0.5
    else:
        # if he does not has copies of gene (0 copies) so he can pass the gene with the mutation (0.01)
        return PROBS["mutation"]


def joint_probability(people, one_gene, two_genes, have_trait):

    Joint_probability = 1

    for person in people:
        mother = people[person]["mother"]
        father = people[person]["father"]

        gene_copy = (
            2 if person in two_genes else
            1 if person in one_gene else
            0
        )

        # if the person's parent are unknown
        if mother is None and father is None:
            gene_prob = PROBS["gene"][gene_copy]

            # computing the probability of having the trait
            has_trait = person in have_trait
            trait_probability = PROBS["trait"][gene_copy][has_trait]

        # else person have known parents
        else:
            # the probabilities of parent to pass the gene
            mother_pass_prob = parent_prob_pass_theGene(mother, one_gene, two_genes)
            father_pass_prob = parent_prob_pass_theGene(father, one_gene, two_genes)

            # the probabilities of the person to get the diff. copies of the gene from his parents
            if person in two_genes:
                gene_prob = (mother_pass_prob * father_pass_prob)
            elif person in one_gene:
                gene_prob = ((1 - mother_pass_prob) * (father_pass_prob)) + \
                    ((1 - father_pass_prob) * (mother_pass_prob))
            else:
                gene_prob = (1 - mother_pass_prob) * (1 - father_pass_prob)

            # computing the probability of having the trait
            has_trait = person in have_trait
            trait_probability = PROBS["trait"][gene_copy][has_trait]

        # probability of this person to have a particular copy of the gene and to exhibit the trait
        probability = gene_prob * trait_probability

        Joint_probability *= probability

    return Joint_probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        num_genes = (
            2 if person in two_genes else
            1 if person in one_gene else
            0
        )

        probabilities[person]["gene"][num_genes] += p
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        probs_gene_summation = probabilities[person]["gene"][0] + \
            probabilities[person]["gene"][1] + probabilities[person]["gene"][2]

        # checking the summation of the diff. copies of gene != 1
        if probs_gene_summation != 1:
            probabilities[person]["gene"][0] /= probs_gene_summation
            probabilities[person]["gene"][1] /= probs_gene_summation
            probabilities[person]["gene"][2] /= probs_gene_summation

        probs_trait_summation = sum(probabilities[person]["trait"].values())
        if probs_trait_summation != 1:
            for trait in probabilities[person]["trait"]:
                probabilities[person]["trait"][trait] /= probs_trait_summation


if __name__ == "__main__":
    main()
