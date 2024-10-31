import os

import pytest

from api.tools.image import compare_image


@pytest.mark.parametrize(
    "file, expected",
    [
        ("1-ok.jpg", True),
        ("2-ok.jpg", True),
        ("1-no.jpg", False),
        ("2-no.jpg", False),
        ("3-no.jpg", False),
    ],
    ids=[
        "0.1 second before",
        "0.01 second before",
        "1 seconds after",
        "3 seconds after",
        "rocket league",
    ],
)
async def test_compare_image(file, expected):
    """
    Compare two images
    compare their correlation which should be over > 0.95
    """
    root_expected = os.path.join(
        "tests",
        "assets",
        "images",
    )
    base_image = os.path.join("tests", "assets", "images", "main-image.jpg")

    assert os.path.exists(root_expected) and os.path.exists(base_image)

    image = os.path.join(root_expected, file)
    assert compare_image(base_image, image) == expected
