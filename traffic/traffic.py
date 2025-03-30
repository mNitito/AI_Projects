import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 3
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    print("Training in progress...")
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    print("Evaluating model performance...")
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):

    # check if data_dir is exixst
    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} does not exist.")
        return

    # getting a list of all the sub-dirctories in the data_dir
    subdirs = [os.path.join(data_dir, d) for d in os.listdir(
        data_dir) if os.path.isdir(os.path.join(data_dir, d))]

    images = []
    labels = []

    # iterate over every subdir in subdirs
    for subdir in subdirs:
        # get the int of the subdir name
        label = int(os.path.basename(subdir))

        # Iterate over each image file in the subdirectory
        for image_file in os.listdir(subdir):
            # form the full path of the image_file. ex: gtsrb/0/0000.pmm and so on
            image_path = os.path.join(subdir, image_file)

            try:
                # read the image using opencv .. it will be read as a numpy.ndarray (multidimenshional array)
                img = cv2.imread(image_path)

                if img is None:
                    print(f"Unable to read image: {image_path}")
                    continue

                # resize the image
                resized_img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))

                images.append(resized_img)

                labels.append(label)

            except Exception as e:
                print(f"Error reading image {image_path}: {str(e)}")

    return images, labels


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    model = tf.keras.models.Sequential([

        # Convolutional layer. learn 32 filters using 3x3 karnel
        tf.keras.layers.Conv2D(
            32, (3, 3), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
        ),

        # Max-pooling layer, using 2x2 pool size
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

        # Secound Convolutional layer. learn 64 filters using 3x3 karnel
        tf.keras.layers.Conv2D(
            64, (3, 3), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
        ),

        # Secound Max-pooling layer, using 2x2 pool size
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

        # Third Convolutional layer. learn 128 filters using 3x3 karnel
        tf.keras.layers.Conv2D(
            128, (3, 3), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
        ),

        # Third Max-pooling layer, using 2x2 pool size
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),


        # Flattern units
        tf.keras.layers.Flatten(),

        # Add a hiden layer with dropout to prevent the overfitting
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dropout(0.5),

        # Add an output layer with outputs units for all of the NUM_CATEGORIES
        tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax")
    ])

    # Train Neural Network
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


if __name__ == "__main__":
    main()
