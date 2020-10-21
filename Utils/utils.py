import colorsys
import cv2
import h5py
from keras import Model
import numpy as np
import os
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb
from PIL import Image, ImageFont, ImageDraw
from timeit import default_timer as timer

min_logo_size = (10, 10)


def detect_object(yolo, img_path, save_img, save_img_path="./", postfix=""):
    """
    Call YOLO logo detector on input image, optionally save resulting image.

    Args:
      yolo: keras-yolo3 initialized YOLO instance
      img_path: path to image file
      save_img: bool to save annotated image
      save_img_path: path to directory where to save image
      postfix: string to add to filenames
    Returns:
      prediction: list of bounding boxes in format (xmin,ymin,xmax,ymax,class_id,confidence)
      image: unaltered input image as (H,W,C) array
    """
    try:
        image = Image.open(img_path)
        if image.mode != "RGB":
            image = image.convert("RGB")
        image_array = np.array(image)
    except:
        print("File Open Error! Try again!")
        return None, None

    prediction, new_image = yolo.detect_image(image)

    return prediction, image_array


def parse_input():
    """
    Ask user input for input images: pass path to individual images, directory
    """
    out = []
    while True:
        ins = input("Enter path (q to quit):").strip()
        if ins in ["q", "quit"]:
            break
        if not os.path.exists(ins):
            print("Error: file not found!")
        elif os.path.isdir(ins):
            out = [
                os.path.abspath(os.path.join(ins, f))
                for f in os.listdir(ins)
                if f.endswith((".jpg", ".png"))
            ]
            break
        elif ins.endswith((".jpg", ".png")):
            out.append(os.path.abspath(ins))
        print(out)
    return out


def load_extractor_model(model_name="InceptionV3", flavor=1):
    """Load variant of InceptionV3 or VGG16 model specified.

    Args:
      model_name: string, either InceptionV3 or VGG16
      flavor: int specifying the model variant and input_shape.
        For InceptionV3, the map is {0: default, 1: 200*200, truncate last Inception block,
        2: 200*200, truncate last 2 blocks, 3: 200*200, truncate last 3 blocks, 4: 200*200}
        For VGG16, it only changes the input size, {0: 224 (default), 1: 128, 2: 64}.
"""
    start = timer()
    if model_name == "InceptionV3":
        from keras.applications.inception_v3 import InceptionV3
        from keras.applications.inception_v3 import preprocess_input

        model = InceptionV3(weights="imagenet", include_top=False)

        trunc_layer = [-1, 279, 248, 228, -1]
        i_layer = flavor
        model_out = Model(
            inputs=model.inputs, outputs=model.layers[trunc_layer[i_layer]].output
        )
        input_shape = (299, 299, 3) if flavor == 0 else (200, 200, 3)

    elif model_name == "VGG16":
        from keras.applications.vgg16 import VGG16
        from keras.applications.vgg16 import preprocess_input

        model_out = VGG16(weights="imagenet", include_top=False)
        input_length = [224, 128, 64][flavor]
        input_shape = (input_length, input_length, 3)

    end = timer()
    print("Loaded {} feature extractor in {:.2f}sec".format(model_name, end - start))
    return model_out, preprocess_input, input_shape


def chunks(l, n, preprocessing_function=None):
    """Yield successive n-sized chunks from l.

    General purpose function modified for Keras: made infinite loop,
    add preprocessing, returns np.array instead of list

    Args:
      l: iterable
      n: number of items to take for each chunk
      preprocessing_function: function that processes image (3D array)
    Returns:
      generator with n-sized np.array preprocessed chunks of the input
    """

    func = (lambda x: x) if (preprocessing_function is None) else preprocessing_function

    # in predict_generator, steps argument sets how many times looped through "while True"
    while True:
        for i in range(0, len(l), n):
            yield np.array([func(el) for el in l[i : i + n]])


def load_features(filename):
    """
    Load pre-saved HDF5 features for all logos in the LogosInTheWild database
    """

    start = timer()
    # get database features
    with h5py.File(filename, "r") as hf:
        brand_map = list(hf.get("brand_map"))
        input_shape = list(hf.get("input_shape"))
        features = hf.get("features")
        features = np.array(features)
    end = timer()
    print(
        "Loaded {} features from {} in {:.2f}sec".format(
            features.shape, filename, end - start
        )
    )

    return features, brand_map, input_shape


def save_features(filename, features, brand_map, input_shape):
    """
    Save features to compressed HDF5 file for later use
    """

    print("Saving {} features into {}... ".format(features.shape, filename), end="")
    # reduce file size by saving as float16
    features = features.astype(np.float16)
    start = timer()
    with h5py.File(filename, "w") as hf:
        hf.create_dataset("features", data=features, compression="lzf")
        hf.create_dataset("brand_map", data=brand_map)
        hf.create_dataset("input_shape", data=input_shape)

    end = timer()
    print("done in {:.2f}sec".format(end - start))

    return None


def features_from_image(img_array, model, preprocess, batch_size=100):
    """
    Extract features from image array given a decapitated keras model.
    Use a generator to avoid running out of memory for large inputs.

    Args:
      img_array: (N, H, W, C) list/array of input images
      model: keras model, outputs
    Returns:
      features: (N, F) array of 1D features
    """

    if len(img_array) == 0:
        return np.array([])

    steps = len(img_array) // batch_size + 1
    img_gen = chunks(img_array, batch_size, preprocessing_function=preprocess)
    features = model.predict_generator(img_gen, steps=steps)

    # if the generator has looped past end of array, cut it down
    features = features[: len(img_array)]

    # reshape features: flatten last three dimensions to one
    features = features.reshape(features.shape[0], np.prod(features.shape[1:]))
    return features


