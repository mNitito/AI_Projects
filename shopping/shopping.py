import csv
import sys
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):

    df = pd.read_csv(filename)

    # Mapping dictionaries for columns
    mapping_months = {'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4,
                      'June': 5, 'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11}

    visitor_type = {'Returning_Visitor': 1, 'New_Visitor': 0, 'Other': 0}

    # Apply mappings and converting to DataFrame columns
    df['Month'] = df['Month'].map(mapping_months)
    df['VisitorType'] = df['VisitorType'].map(visitor_type)
    df['Weekend'] = df['Weekend'].astype(int)

    # Convert Revenue to int (label)
    df['Revenue'] = df['Revenue'].astype(int)

    # Extract evidence and labels
    evidences = df.iloc[:, :-1].values.tolist()
    labels = df.iloc[:, -1].values.tolist()

    # Check if the data loaded correctly
    if len(evidences) != len(labels):
        sys.exit('Error occurred in loading data')

    print("Data loaded successfully")
    print("Example evidence:", evidences[0])  # Print the first evidence for verification

    return evidences, labels


def train_model(evidence, labels):

    classifier = KNeighborsClassifier(n_neighbors=1)
    classifier.fit(evidence, labels)

    return classifier


def evaluate(labels, predictions):

    print(labels[0:10])
    print(predictions[0:10])

    TP, TN, FP, FN = 0, 0, 0, 0

    for i in range(len(labels)):

        if labels[i] == 1 and predictions[i] == 1:
            TP += 1
        elif labels[i] == 0 and predictions[i] == 0:
            TN += 1
        elif labels[i] == 0 and predictions[i] == 1:
            FP += 1
        elif labels[i] == 1 and predictions[i] == 0:
            FN += 1

    if (TP + FN) == 0 or (TN + FP) == 0:
        return "the denominator  = zero"

    sensitivity = TP / (TP + FN)
    specificity = TN / (TN + FP)

    return sensitivity, specificity


if __name__ == "__main__":
    main()
