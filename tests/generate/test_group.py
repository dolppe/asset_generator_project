from context import group
from context import utils
from context import group_transfer
import pandas as pd
import pytest
import json

INPUT_PATH = "tests/resources/input"
BASE_DATA_PATH = INPUT_PATH + "/group/test_group_base.xlsx"
PLANNING_DATA_PATH = INPUT_PATH + "/group/test_group_planning.xlsx"
MAPPING_DATA_PATH = INPUT_PATH + "/group/test_group_mapping.xlsx"
OUTPUT_DATA_PATH = "output/output.xlsx"


@pytest.fixture
def get_planning_dict():
    planning_df = pd.read_excel(PLANNING_DATA_PATH)
    planning_dict = json.loads(utils.convert_to_json(planning_df))
    return planning_dict


@pytest.fixture
def get_mapping_dict():
    mapping_df = pd.read_excel(MAPPING_DATA_PATH)
    mapping_dict = json.loads(utils.convert_to_json(mapping_df))
    return mapping_dict


@pytest.fixture
def dict_preprocess(get_planning_dict, get_mapping_dict):
    base_data_df = pd.read_excel(BASE_DATA_PATH, sheet_name=None)
    group_df = base_data_df["GroupData"]
    profile_df = base_data_df["ProfileData"]
    card_pack_df = base_data_df["CardPackData"]
    card_pack_year_df = base_data_df["CardPackYearData"]
    artist_df = base_data_df["ArtistData"]
    card_df = base_data_df["CardData"]
    music_df = base_data_df["MusicData"]
    locale_df = base_data_df["LocaleData"]

    group_transfer.group_transfer(get_mapping_dict, get_planning_dict, group_df, profile_df, card_df, music_df)

    df_dict = dict()
    df_dict["group_df"] = group_df
    df_dict["profile_df"] = profile_df
    df_dict["card_pack_df"] = card_pack_df
    df_dict["card_pack_year_df"] = card_pack_year_df
    df_dict["artist_df"] = artist_df
    df_dict["locale_df"] = locale_df

    return df_dict


@pytest.fixture
def image_set(get_planning_dict, get_mapping_dict):
    utils.Image.set_mapping_data(get_mapping_dict)
    utils.Image.set_planning_data(get_planning_dict)


@pytest.fixture
def get_group_list(get_mapping_dict, get_planning_dict):
    mapping_group = get_mapping_dict["groupList"]
    planning_group = get_planning_dict["groupList"]
    group_list = []
    for mapping_group_item in mapping_group:
        group_item = group.Group(mapping_group_item)
        for planning_group_item in planning_group:
            if planning_group_item["groupName"] == group_item.origin_group_name:
                group_item.set_planning_data(planning_group_item)
                group_list.append(group_item)

    return group_list


def find_group(get_group_list, group_name):
    for group_item in get_group_list:
        if group_item.origin_group_name == group_name:
            return group_item


@pytest.fixture
def last_group_cls(get_group_list):
    group_name = "CHANHYUK"
    return find_group(get_group_list, group_name)


@pytest.fixture
def solo_group_cls(get_group_list):
    group_name = "CHANHYUK"
    return find_group(get_group_list, group_name)


@pytest.fixture
def normal_group_cls(get_group_list):
    group_name = "SECHSKIES"
    return find_group(get_group_list, group_name)


def test_make_df_artist_아티스트_카드_개수_테스트(image_set, get_group_list, dict_preprocess, themelist_stub):
    artist_df = dict_preprocess["artist_df"]
    pre_artist_length = len(artist_df.index)
    total_card_num = 0
    TEMP_GROUP_CODE = 9999
    for group_item in get_group_list:
        total_card_num += group_item.card_num
        group_item.set_groupid(TEMP_GROUP_CODE)

    artist_df = group.make_df_artist(artist_df, get_group_list, themelist_stub)

    artist_length = len(artist_df.index)

    assert artist_length == total_card_num + pre_artist_length


def test_make_list_artist_솔로_그룹_아티스트데이터_포지션_생성_테스트(image_set, solo_group_cls, themelist_stub):
    ARTISTDATA_LENGTH = 16
    CODE = 9999
    solo_group_cls.set_groupid(CODE)

    dict_list = group.make_list_artist(solo_group_cls, themelist_stub[0], CODE)

    for dict_list_item in dict_list:
        assert dict_list_item["position"] is not None


def test_make_list_artist_필수_아티스트데이터_생성_개수_테스트(image_set, normal_group_cls, themelist_stub):
    ARTISTDATA_LENGTH = 16
    size = 0
    CODE = 9999
    normal_group_cls.set_groupid(CODE)

    dict_list = group.make_list_artist(normal_group_cls, themelist_stub[0], CODE)
    for dict_list_item in dict_list:
        size += len(dict_list_item)
    artist_length = ARTISTDATA_LENGTH * normal_group_cls.card_num

    assert size >= artist_length


def test_find_group_정상_그룹_찾기(get_group_list):

    group_name = "CHANHYUK"

    test_group = find_group(get_group_list, group_name)

    assert test_group is not None


def test_find_group_없는_그룹_찾기(get_group_list):

    group_name = "NOTGROUP"

    test_group = find_group(get_group_list, group_name)

    assert test_group is None


def test_find_group_마지막_그룹일때_그룹인덱스_찾기(last_group_cls, dict_preprocess):

    group_df = dict_preprocess["group_df"]
    LAST_GROUP_CODE = 24001

    group_idx = last_group_cls.find_idx(group_df)

    assert group_df.loc[group_idx, "code"] == LAST_GROUP_CODE


def test_find_group_일반_그룹인덱스_찾기(normal_group_cls, dict_preprocess):

    group_df = dict_preprocess["group_df"]
    NORMAL_GROUP_CODE = 6008

    group_idx = normal_group_cls.find_idx(group_df)

    assert group_df.loc[group_idx, "code"] == NORMAL_GROUP_CODE


def test_set_planning_data_본그룹_객체_생성_이름확인(get_mapping_dict, get_planning_dict):
    mapping_group = get_mapping_dict["groupList"]
    planning_group = get_planning_dict["groupList"]
    mapping_group_item = mapping_group[0]
    group_item = group.Group(mapping_group_item)
    for planning_group_item in planning_group:
        if planning_group_item["groupName"] == group_item.origin_group_name:
            planning_group_item["isEvent"] = "False"
            group_item.set_planning_data(planning_group_item)
            temp_group = group_item
            break

    assert temp_group.group_name == temp_group.origin_group_name


def test_set_planning_data_프로필_없는_그룹객체_생성(get_mapping_dict, get_planning_dict):
    mapping_group = get_mapping_dict["groupList"]
    planning_group = get_planning_dict["groupList"]
    mapping_group_item = mapping_group[0]
    group_item = group.Group(mapping_group_item)

    for planning_group_item in planning_group:
        if planning_group_item["groupName"] == group_item.origin_group_name:
            planning_group_item["isProfile"] = "False"
            group_item.set_planning_data(planning_group_item)
            not_profile = group_item
            break

    assert not hasattr(not_profile, "profile")


def test_Group_솔로_그룹_포지션_테스트(get_mapping_dict):
    group_name = "ROSE"
    mapping_group = get_mapping_dict["groupList"]
    for mapping_group_item in mapping_group:
        temp_group = group.Group(mapping_group_item)
        if temp_group.origin_group_name == group_name:
            solo_group = temp_group

    assert hasattr(solo_group.artist, "position")


def test_make_dict_group_필수_그룹데이터_생성_개수_테스트(normal_group_cls, image_set):
    CODE = 6009
    ORDER = 10
    SECOND_ORDER = 10
    GROUPDATA_LENGTH = 13

    normal_group_cls.set_order(ORDER, SECOND_ORDER)
    group_dict = group.make_dict_group(normal_group_cls, CODE)

    assert len(group_dict) == GROUPDATA_LENGTH


def test_make_df_group_그룹리스트만큼_DF생성확인(get_group_list, dict_preprocess):
    group_df = dict_preprocess["group_df"]
    pre_group_count = group_df.index[-1]
    group_length = len(get_group_list)

    group_df = group.make_df_group(group_df, get_group_list)
    group_count = group_df.index[-1]

    assert group_count == pre_group_count + group_length


class ThemeStub:
    def __init__(self, image_theme="test", theme_name="test_theme"):
        self.image_theme = image_theme
        self.theme_name = theme_name


@pytest.fixture
def themelist_stub(get_group_list):
    group_count = len(get_group_list)
    themelist = []
    for i in range(0, group_count):
        themelist.append(ThemeStub())
    return themelist


def test_make_list_profile_필수_프로필데이터_생성_개수_테스트(image_set, normal_group_cls, themelist_stub):
    CODE = 1111
    PROFILEDATA_LENGTH = 10
    ORDER = 1000
    EVENTCODE = 25001

    normal_group_cls.profile.set_order_index(ORDER)
    normal_group_cls.profile.set_event_code(EVENTCODE)
    profile_list = group.make_list_profile(normal_group_cls, themelist_stub[0], CODE)
    size = 0
    for i in range(0, normal_group_cls.card_num):
        size += len(profile_list[i])
    profile_list_length = PROFILEDATA_LENGTH * normal_group_cls.card_num

    assert size == profile_list_length


def test_make_list_profile_프로필_카드_수량_테스트(image_set, normal_group_cls, themelist_stub):
    CODE = 1111
    ORDER = 1000
    EVENTCODE = 25001

    normal_group_cls.profile.set_order_index(ORDER)
    normal_group_cls.profile.set_event_code(EVENTCODE)
    profile_list = group.make_list_profile(normal_group_cls, themelist_stub[0], CODE)

    assert len(profile_list) == normal_group_cls.card_num


def test_make_df_profile_is_profile_스킵_테스트(
    image_set, dict_preprocess, get_mapping_dict, get_group_list, themelist_stub
):
    profile_df = dict_preprocess["profile_df"]
    card_pack_df = dict_preprocess["card_pack_df"]
    card_pack_year_df = dict_preprocess["card_pack_year_df"]
    locale_df = dict_preprocess["locale_df"]

    pre_profile_length = profile_df.index[-1]

    is_profile_count = 0

    for group_item in get_group_list:
        assert group_item.is_profile
        if group_item.is_profile == "True":
            is_profile_count += group_item.card_num

    profile_df, card_pack_df, card_pack_year_df, locale_df = group.make_df_profile(
        profile_df, card_pack_df, card_pack_year_df, locale_df, get_mapping_dict, get_group_list, themelist_stub
    )

    profile_length = profile_df.index[-1]

    assert profile_length == pre_profile_length + is_profile_count


def test_make_df_profile_프로필_카드팩_카드팩이어_연동_테스트(
    image_set, dict_preprocess, get_mapping_dict, get_group_list, themelist_stub
):
    profile_df = dict_preprocess["profile_df"]
    card_pack_df = dict_preprocess["card_pack_df"]
    card_pack_year_df = dict_preprocess["card_pack_year_df"]
    locale_df = dict_preprocess["locale_df"]

    is_profile_group_count = 0

    for group_item in get_group_list:
        if group_item.is_profile == "True":
            is_profile_group_count += 1

    profile_df, card_pack_df, card_pack_year_df, locale_df = group.make_df_profile(
        profile_df, card_pack_df, card_pack_year_df, locale_df, get_mapping_dict, get_group_list, themelist_stub
    )
    total_index_size = len(card_pack_year_df[card_pack_year_df["category"] == 27].index)

    index_list = card_pack_year_df[card_pack_year_df["category"] == 27].index[
        -1 : total_index_size - is_profile_group_count - 1 : -1
    ]
    card_pack_year_code_list = []

    for index_list_item in index_list:
        card_pack_year_code_list.append(card_pack_year_df.loc[index_list_item, "code"])

    total_index_size = len(card_pack_df[card_pack_df["category"] == 27].index)

    index_list = card_pack_df[card_pack_df["category"] == 27].index[
        -1 : total_index_size - is_profile_group_count - 1 : -1
    ]
    card_pack_code_list = []

    for index_list_item in index_list:
        card_pack_code_list.append(card_pack_df.loc[index_list_item, "code"])

    assert card_pack_code_list == card_pack_year_code_list


def test_make_df_profile_프로필_로케일_생성_테스트(image_set, dict_preprocess, get_mapping_dict, get_group_list, themelist_stub):
    profile_df = dict_preprocess["profile_df"]
    card_pack_df = dict_preprocess["card_pack_df"]
    card_pack_year_df = dict_preprocess["card_pack_year_df"]
    locale_df = dict_preprocess["locale_df"]

    is_profile_group_count = 0

    for group_item in get_group_list:
        if group_item.is_profile == "True":
            is_profile_group_count += 1

    profile_df, card_pack_df, card_pack_year_df, locale_df = group.make_df_profile(
        profile_df, card_pack_df, card_pack_year_df, locale_df, get_mapping_dict, get_group_list, themelist_stub
    )

    index_list = card_pack_year_df[card_pack_year_df["category"] == 27].index[-1:is_profile_group_count:-1]
    locale_code_list = []

    for index_list_item in index_list:
        locale_code_list.append(card_pack_year_df.loc[index_list_item, "name"])

    for locale_code_list_item in locale_code_list:
        if (locale_df["code"] == locale_code_list_item).any():
            assert True
        else:
            assert False


def test_make_df_profile_프로필_카드팩_카드팩이어_생성_테스트(
    image_set, dict_preprocess, get_mapping_dict, get_group_list, themelist_stub
):
    profile_df = dict_preprocess["profile_df"]
    card_pack_df = dict_preprocess["card_pack_df"]
    card_pack_year_df = dict_preprocess["card_pack_year_df"]
    locale_df = dict_preprocess["locale_df"]

    pre_card_pack_length = card_pack_df.index[-1]
    pre_card_pack_year_length = card_pack_year_df.index[-1]

    is_profile_group_count = 0

    for group_item in get_group_list:
        if group_item.is_profile == "True":
            is_profile_group_count += 1

    profile_df, card_pack_df, card_pack_year_df, locale_df = group.make_df_profile(
        profile_df, card_pack_df, card_pack_year_df, locale_df, get_mapping_dict, get_group_list, themelist_stub
    )

    card_pack_length = card_pack_df.index[-1]
    card_pack_year_length = card_pack_year_df.index[-1]

    assert card_pack_length == pre_card_pack_length + is_profile_group_count
    assert card_pack_year_length == pre_card_pack_year_length + is_profile_group_count
