import pytest

from context import input_combine


@pytest.fixture
def bgmission_mapping_dict():
    return {
        "bg": {
            "basicInfo": {"기본정보1": "정보", "기본정보2": "정보"},
            "bgTypeInfo": {
                "무료": {"sellType": 3, "startCardPackCode": 801001},
                "기본": {"sellType": 0, "startCardPackCode": 801002},
            },
            "tabTitleInfo": {"Mission 1": 7009001, "Mission 2": 7009002},
            "titleLocaleInfo": {
                "Song Clear": {"titleLocale": 70010000, "type": 5001},
                "Obtain Card": {"titleLocale": 70010007, "type": 5002},
            },
            "missionTypeInfo": {
                "5001": {"uri": "ss://selectmusic", "uriParameters": ["group", "music", "difficult"]},
                "5002": {"uri": "ss://store?", "uriParameters": ["menu"]},
            },
        },
        "mission": {"tabTitleInfo": {"Mission 1": 7009001, "Mission 2": 7009002}},
    }


@pytest.fixture
def bgmission_planning_dict():
    return {
        "bgList": [
            {
                "bgName": ["[무료] TREASURE (HELLO)배경", "[무료] TREASURE (HELLO) Wallpaper"],
                "sellType": "무료",
                "tabTitleLocale": ["미션 1", "Mission 1"],
                "titleLocale": ["곡 클리어", "Song Clear"],
            },
            {
                "bgName": ["[이벤트] SECHKSKIES We're done 배경", "[Event] SECHKSKIES We're done Wallpaper"],
                "sellType": "기본",
                "tabTitleLocale": ["미션 2", "Mission 2"],
                "titleLocale": ["카드 획득", "Obtain Card"],
            },
        ],
        "missionList": [{"tabTitleLocale": ["미션 1", "Mission 1"]}, {"tabTitleLocale": ["미션 2", "Mission 2"]}],
    }


@pytest.fixture
def bg_combined_input():
    return [
        {
            "bgName": ["[무료] TREASURE (HELLO)배경", "[무료] TREASURE (HELLO) Wallpaper"],
            "sellType": 3,
            "startCardPackCode": 801001,
            "tabTitleLocale": 7009001,
            "titleLocale": 70010000,
            "type": 5001,
            "uri": "ss://selectmusic",
            "uriParameters": ["group", "music", "difficult"],
            "기본정보1": "정보",
            "기본정보2": "정보",
        },
        {
            "bgName": ["[이벤트] SECHKSKIES We're done 배경", "[Event] SECHKSKIES We're done Wallpaper"],
            "sellType": 0,
            "startCardPackCode": 801002,
            "tabTitleLocale": 7009002,
            "titleLocale": 70010007,
            "type": 5002,
            "uri": "ss://store?",
            "uriParameters": ["menu"],
            "기본정보1": "정보",
            "기본정보2": "정보",
        },
    ]


def test_입력_병합_확인_set_list(bgmission_mapping_dict, bgmission_planning_dict, bg_combined_input):
    assert bg_combined_input == input_combine.set_list(bgmission_mapping_dict["bg"], bgmission_planning_dict["bgList"])
