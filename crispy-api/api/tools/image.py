import numpy as np
from PIL import Image, ImageFilter


def compare_image(path1: str, path2: str) -> bool:
    """Compare 2 images using the correlation system to find similarities.
    Images must be the same size.

    :param path1: path of the first image
    :param path2: path of the second image
    :return: the correlation factor of the images
    """
    image1 = Image.open(path1)
    image2 = Image.open(path2)

    blur1 = image1.filter(ImageFilter.GaussianBlur(radius=7))
    blur2 = image2.filter(ImageFilter.GaussianBlur(radius=7))

    data1 = np.asarray(blur1)
    data2 = np.asarray(blur2)

    # https://stackoverflow.com/questions/51248810/python-why-would-numpy-corrcoef-return-nan-values
    corrcoef = np.corrcoef(data1.flat, data2.flat)
    if np.isnan(corrcoef).all():
        return True

    return bool((1 + corrcoef[0, 1]) / 2 > 0.8)
