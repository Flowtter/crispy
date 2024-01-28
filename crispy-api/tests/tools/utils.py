from api.tools.utils import levenstein_distance


async def test_levenshtein_distance():
    assert levenstein_distance("", "") == 0
    assert levenstein_distance("test", "test") == 0

    assert levenstein_distance("test", "tst") == 1
    assert levenstein_distance("test", "tast") == 1
    assert levenstein_distance("test", "teest") == 1

    assert levenstein_distance("test", "yolo") == 4

    assert levenstein_distance("test", "y") == 4
    assert levenstein_distance("y", "test") == 4
    assert levenstein_distance("test", "t") == 3
    assert levenstein_distance("t", "test") == 3
    assert levenstein_distance("test", "") == 4
    assert levenstein_distance("", "test") == 4
