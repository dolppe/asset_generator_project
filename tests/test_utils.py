from context import utils


def test_change_type_of_int_확인():
    target: int = 1234
    assert type(utils.change_type_of(target)) is int


def test_change_type_of_int_변환_확인():
    target: str = "1234"
    assert type(utils.change_type_of(target)) is int


def test_change_type_of_float_확인():
    target: float = 12.34
    assert type(utils.change_type_of(target)) is float


def test_change_type_of_float_변환_확인():
    target: str = "12.34"
    assert type(utils.change_type_of(target)) is float


def test_change_type_of_str_확인():
    target: str = "string"
    assert type(utils.change_type_of(target)) is str
