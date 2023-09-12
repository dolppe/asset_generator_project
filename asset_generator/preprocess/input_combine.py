from generate import group
from generate import theme
from generate import music


def artist_set_list(mapping_dict, planning_dict):

    mapping_group = mapping_dict["groupList"]
    mapping_theme = mapping_dict["theme"]
    planning_group = planning_dict["groupList"]

    mapping_album = mapping_dict["albumList"]

    music_item = planning_dict["musicList"]
    group_list = []
    theme_list = []
    for mapping_group_item in mapping_group:
        mapping_group_item = group.Group(mapping_group_item)
        for planning_group_item in planning_group:
            if mapping_group_item.origin_group_name == planning_group_item["groupName"]:
                mapping_group_item.set_planning_data(planning_group_item)
                theme_item = theme.Theme(mapping_theme)
                theme_item.set_planning_data(planning_group_item)
                group_list.append(mapping_group_item)
                theme_list.append(theme_item)

    music_list = []

    for planning_music_item in music_item:
        music_item = music.Music()
        music_item.set_planning_data(planning_music_item)
        for mapping_album_item in mapping_album:
            if mapping_album_item["albumName"] == music_item.album_name:
                album_item = music.Album(mapping_album_item)
                music_item.set_album(album_item)
                music_list.append(music_item)
                continue
    return group_list, theme_list, music_list


def set_basic(mapping_dict, planning_dict):
    for key, value in mapping_dict.items():
        if not isinstance(value, dict):
            planning_dict[key] = value
    return planning_dict


combine_info_list = [
    {
        "sellType": "bgTypeInfo",
        "tabTitleLocale": "tabTitleInfo",
        "titleLocale": "titleLocaleInfo",
        "itemName": "itemInfo",
    },
    {"type": "missionTypeInfo"},
]


def mission_set_list(mapping_dict, planning_list):
    planning_list = set_list(mapping_dict["mission"], planning_list)
    for planning_event_dict in planning_list:
        planning_event_dict["missionList"] = set_list(mapping_dict["mission"], planning_event_dict["missionList"])
        for planning_mission_dict in planning_event_dict["missionList"]:
            planning_mission_dict["missionItemList"] = set_list(
                mapping_dict["mission"], planning_mission_dict["missionItemList"]
            )
            planning_mission_dict["missionItemList"] = set_list(mapping_dict, planning_mission_dict["missionItemList"])
    return planning_list


def insert_type_value(mapping_info_dict, planning_detail, combine_info):
    # 기획서의 키(planning_key)에 해당하는 정보를 가져올 매핑 데이터 위치(mapping_key)
    for planning_key, mapping_key in combine_info.items():
        planning_key = planning_key.replace(" ", "")
        mapping_key = mapping_key.replace(" ", "")
        if planning_key in planning_detail:
            if not isinstance(planning_detail[planning_key], list):
                planning_value_list = [str(planning_detail[planning_key])]
            else:
                planning_value_list = planning_detail[planning_key]
            for planning_value in planning_value_list:
                if mapping_key in mapping_info_dict:
                    if planning_value in mapping_info_dict[mapping_key]:
                        if isinstance(mapping_info_dict[mapping_key][planning_value], dict):
                            planning_detail.update(mapping_info_dict[mapping_key][planning_value])
                        else:
                            planning_detail[planning_key] = mapping_info_dict[mapping_key][planning_value]
                    elif mapping_key == "itemInfo":
                        if (
                            "rewardQuantity" in planning_detail
                            and str(planning_value) + " " + str(planning_detail["rewardQuantity"])
                            in mapping_info_dict[mapping_key]
                        ):
                            planning_value = str(planning_value) + " " + str(planning_detail["rewardQuantity"])
                            if isinstance(mapping_info_dict[mapping_key][planning_value], dict):
                                planning_detail.update(mapping_info_dict[mapping_key][planning_value])
                            else:
                                planning_detail[planning_key] = mapping_info_dict[mapping_key][planning_value]
                        elif isinstance(planning_value, str):
                            for item_name in mapping_info_dict[mapping_key].keys():
                                if planning_value.find(item_name) != -1:
                                    planning_detail["urlName"] = mapping_info_dict[mapping_key][item_name]["urlName"]
                                    break

    return planning_detail


def set_list(mapping_info_dict, planning_list):
    basic_info = "basicInfo"

    for planning_detail in planning_list:
        if basic_info in mapping_info_dict:
            planning_detail.update(mapping_info_dict[basic_info])
        for combine_info in combine_info_list:
            planning_detail = insert_type_value(mapping_info_dict, planning_detail, combine_info)

    return planning_list


def column_bool_convert(df, col_name):
    sep_idx = 1
    df_pre = df[df.index <= sep_idx]
    df_main = df[df.index > sep_idx]
    df_main[col_name] = df_main[col_name].map(convert_bool)
    df = df_pre.append(df_main)
    return df


def df_type_convert(df):
    df_type = list(df.iloc[0])
    df_columns = df.columns
    sep_idx = 1
    df = df.astype(object)
    df_pre = df[df.index <= sep_idx]
    df_main = df[df.index > sep_idx]
    i = 0
    for df_type_item in df_type:
        column_name = df_columns[i]
        if df_type_item == "Float" or df_type_item == "Double":
            df_main[column_name] = df_main[column_name].map(lambda x: x if x != x else float(x))
        elif df_type_item == "String" or df_type_item == "Timestamp" or df_type_item == "JSONArray":
            df_main[column_name] = df_main[column_name].map(lambda x: x if x != x else str(x))
        elif df_type_item == "Boolean":
            df_main[column_name] = df_main[column_name].map(convert_bool)
        i += 1
    df = df_pre.append(df_main)
    return df


def convert_bool(x):
    if type(x) is bool:
        return x
    elif type(x) is str:
        x = x.replace(" ", "")
        x = x.upper()
        if x == "TRUE":
            return True
        if x == "FALSE":
            return False
