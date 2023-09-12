import math
import sys
import string
import json
import re

import pandas as pd
import numpy as np


######################### 그룹


# base DataFrame의 idx 위치에 df DataFrame을 끼워넣음
def insert_df(base_df: pd.DataFrame, target_df: pd.DataFrame, idx):
    part1 = base_df[base_df.index <= idx]
    part2 = base_df[base_df.index > idx]
    total = part1.append(target_df)
    total = total.append(part2)
    total = total.reset_index()
    total = total.drop(["index"], axis=1)

    return total


def group_locale_idx(locale_df: pd.DataFrame, start, end, interval, group_code):
    group_code = int(group_code) // 1000
    group_code = group_code * int(interval) + int(start)

    temp_df = locale_df.loc[locale_df["code"] == group_code]
    idx = -1
    if temp_df.empty:
        idx = locale_df.loc[locale_df["code"] == int(end)].index[0] - 1
        while pd.isna(locale_df.loc[locale_df.index == idx]["code"].item()):
            idx -= 1
    else:
        idx = temp_df.index[0] - 1
    return idx


def normal_locale_idx(locale_df: pd.DataFrame, end):
    temp_idx = locale_df.loc[locale_df["code"] == end].index[0] - 1
    while pd.isna(locale_df.loc[locale_df.index == temp_idx]["code"].item()):
        temp_idx -= 1
    return temp_idx


def df_locale(code, korean, english):
    locale_data = {
        "code": code,
        "koKR": korean,
        "enUS": english,
        "esES": english,
        "ptPT": english,
        "idID": english,
        "zhCN": english,
        "zhTW": english,
        "jpJP": english,
        "arAR": english,
        "trTR": english,
        "thTH": english,
    }

    return locale_data


def group_locale(locale_df: pd.DataFrame, mapping_dict, locale_name, group_code, korean, english):
    mapping = mapping_dict[locale_name]
    group_code = int(group_code)
    interval = int(mapping["interval"])

    locale_idx = group_locale_idx(locale_df, mapping["startCode"], mapping["endCode"], interval, group_code)

    locale_code = locale_df.iloc[locale_idx]["code"]
    temp = str(locale_code // interval)
    temp1 = int(temp[-1])
    temp2 = int(temp[-2]) * 10
    locale_gc = temp1 + temp2
    if locale_gc == (group_code // 1000):
        locale_code = locale_df.iloc[locale_idx]["code"] + 1
    else:
        locale_code = (
            locale_df.iloc[locale_idx]["code"] + interval
        ) // 100 * 100 + 1  # 반례 => 로케일 코드가 꼬여있어서 최신 코드는 21인데 추가하려는 코드가 25이면 22로 추가될듯?
    temp = pd.DataFrame(columns=locale_df.columns)
    temp.loc[0] = df_locale(locale_code, korean, english)
    locale_df = insert_df(locale_df, temp, locale_idx)

    return locale_df, locale_code


def normal_locale(locale_df: pd.DataFrame, mapping_dict, locale_name, korean, english):
    mapping = mapping_dict[locale_name]
    end = int(mapping["endCode"])
    locale_idx = normal_locale_idx(locale_df, end)
    locale_code = locale_df.iloc[locale_idx]["code"] + 1
    temp = pd.DataFrame(columns=locale_df.columns)
    temp.loc[0] = df_locale(locale_code, korean, english)
    locale_df = insert_df(locale_df, temp, locale_idx)

    return locale_df, locale_code


def make_locale_df(locale_df, locale_idx, korean, english):
    locale_code = int(locale_df.iloc[locale_idx]["code"]) + 1
    temp = pd.DataFrame(columns=locale_df.columns)
    temp.loc[0] = df_locale(locale_code, korean, english)
    locale_df = insert_df(locale_df, temp, locale_idx)

    return locale_df, locale_code


class Image:
    base = ""
    version = ""
    updateDate = ""

    def __init__(self) -> None:
        pass

    @classmethod
    def set_mapping_data(cls, mapping_dict):
        cls.base = str(mapping_dict["imageURL"])

    @classmethod
    def set_planning_data(cls, planning_dict):
        cls.version = str(planning_dict["imageVersion"])
        cls.updateDate = str(planning_dict["updateDate"])

    @staticmethod
    def make_fix_image(category, group_name, feature_name, version_time):
        temp = (
            Image.base
            + "images/"
            + category
            + "/"
            + group_name
            + "/"
            + category
            + "_"
            + feature_name
            + ".png?v="
            + version_time
        )
        return temp

    @staticmethod
    def make_flow_image(category, value1, value2="", extension=".png"):
        year = Image.updateDate[0:4]
        r_date = Image.updateDate[2:4] + Image.updateDate[5:7] + Image.updateDate[8:10]
        if value2 == "":
            temp = (
                Image.base + "live/" + year + "/" + r_date + "/" + category + value1 + extension + "?v=" + Image.version
            )
        else:
            temp = (
                Image.base
                + "live/"
                + year
                + "/"
                + r_date
                + "/"
                + category
                + value1
                + "_"
                + value2
                + extension
                + "?v="
                + Image.version
            )
        return temp


# list => order순 IDX, 원 idx, 정렬된column
# 예외 부분 제외하고 정렬
def arrange_order(base_df: pd.DataFrame, column, exception_num):
    target_list = sort_list(base_df, column)
    target_list = target_list.reset_index()
    for list_idx in range(0, len(target_list) - exception_num):
        origin_idx = target_list["index"][list_idx]
        base_df.loc[origin_idx, column] = list_idx

    return base_df


def pd_to_int_without_null(value):
    if math.isnan(value):
        return np.NaN
    if isinstance(value, int):
        return value
    value = int(value)
    return value


# df, 컬럼명을 입력으로 받음
# 해당 컬럼의 idx - order로 연결해서 기존 idx순으로 되어있는 것을 order순으로 정렬
def sort_list(base_df: pd.DataFrame, column):
    temp = base_df[column]
    temp = temp.iloc[2:]
    temp = temp.apply(pd_to_int_without_null)

    temp = temp.sort_values()

    return temp


# value보다 더 큰값은 +1
def add_order(base_df: pd.DataFrame, column, value, exception_num):
    target_list = sort_list(base_df, column)
    target_list = target_list.reset_index()

    for list_idx in range(value + 1, len(target_list) - exception_num):
        if np.isnan(target_list.loc[list_idx, column]):
            continue
        origin_idx = target_list["index"][list_idx]
        base_df.loc[origin_idx, column] = list_idx + 1

    return base_df


######################### 상점


# 이것의 문제점: 사이에 빈칸이 있냐 없냐를 파악해야함
def find_idx(
    base_df: pd.DataFrame, end_code
):  # base는 cardpack/locale, st_idx는 해당 정보가 시작하는 code, end_code는 다음 정보 시작하는 code
    i = base_df.index[base_df["code"] == end_code].tolist()
    return i[0] - 1  # 추가할 idx 인데 이거는 빈칸이 있다는 가정하에 이러는 것


def find_idx_reverse(base_df: pd.DataFrame, start_code):
    i = base_df.index[base_df["code"] == start_code].tolist()
    return i[0] + 1  # 추가할 idx 인데 이거는 빈칸이 있다는 가정하에 이러는 것 -> i[0]+1


# 마지막 행 이후  추가할 index 를 찾음
def find_lastidx(base_df: pd.DataFrame):
    i = base_df.shape[0]
    return i


def make_locale_dic(code, korean, english):
    dic = {
        "code": code,
        "koKR": korean,
        "enUS": english,
        "esES": english,
        "ptPT": english,
        "idID": english,
        "zhCN": english,
        "zhTW": english,
        "jpJP": english,
        "arAR": english,
        "trTR": english,
        "thTH": english,
    }

    return dic


def make_resource_url(parent_url, update_date, folder, start_name, theme, item):
    if update_date[0] == "'":
        update_date = update_date[1:]
    short_date = str(update_date[2:4]) + str(update_date[5:7]) + str(update_date[8:10])
    theme = (
        theme.translate(str.maketrans("", "", string.punctuation.replace("_", ""))).lower().strip().replace(" ", "_")
    )
    url = (
        parent_url
        + "live/"
        + update_date[0:4]
        + "/"
        + short_date
        + "/"
        + folder
        + "/"
        + start_name
        + theme
        + item
        + ".png?v="
        + short_date
        + "01"
    )
    return url


def normal_append_find_idx(df, end_code=0):
    if end_code == 0:
        return df.index[-1]
    end_idx = df.loc[df["code"] == end_code].index[0]
    if df.index[-1] == end_idx:
        return end_idx
    temp_idx = df.loc[df["code"] == end_code].index[0] - 1
    while pd.isna(df.loc[df.index == temp_idx]["code"].item()):
        temp_idx -= 1
    return temp_idx


def unnamed_find_idx(df, unnamed_idx, find_name):
    col_name = "Unnamed: " + str(unnamed_idx)
    return df.loc[df[col_name] == find_name].index[-1]


############################ 상점 로케일


def point_locale(base_df: pd.DataFrame, data_list, locale_list):
    point_des_loc = []
    point_name_loc = []
    point_msg_loc = []

    list1 = []
    list2 = []
    list3 = []

    des = locale_list["pointDesLocale"]["startCode"]
    name = locale_list["pointNameLocale"]["endCode"]
    msg = locale_list["pointMsgLocale"]["endCode"]

    for data_idx, data in enumerate(data_list):
        idx = find_idx_reverse(base_df, des)
        temp1 = base_df[base_df.index < idx]
        temp2 = base_df[base_df.index >= idx]
        code = base_df.iloc[idx]["code"] - 1
        point_des_loc.append(code)
        description_kr, description_en = data["description"][0], data["description"][1]
        dic = make_locale_dic(code, description_kr, description_en)
        list1.append(dic)
        base_df = temp1.append(list1[data_idx], ignore_index=True).append(temp2, ignore_index=True)

        idx = find_idx(base_df, name)
        temp1 = base_df[base_df.index < idx]
        temp2 = base_df[base_df.index >= idx]
        code = base_df.iloc[idx - 1]["code"] + 1
        point_name_loc.append(code)
        reward_kr, reward_en = data["reward"][0], data["reward"][1]
        dic2 = make_locale_dic(code, reward_kr, reward_en)
        list2.append(dic2)
        base_df = temp1.append(list2[data_idx], ignore_index=True).append(temp2, ignore_index=True)

        idx = find_idx(base_df, msg)
        temp1 = base_df[base_df.index < idx]
        temp2 = base_df[base_df.index >= idx]
        code = base_df.iloc[idx - 1]["code"] + 1
        point_msg_loc.append(code)
        msg_kr, msg_en = data["msg"][0], data["msg"][1]
        dic3 = make_locale_dic(code, msg_kr, msg_en)
        list3.append(dic3)
        base_df = temp1.append(list3[data_idx], ignore_index=True).append(temp2, ignore_index=True)

    loc_dict = {
        "description": point_des_loc,
        "rewardName": point_name_loc,
        "rewardMsg": point_msg_loc,
    }
    return base_df, loc_dict


def menu_locale(base_df: pd.DataFrame, data_list, update_date, loacle_list):
    menu_name_loc = []
    list1 = []

    name = loacle_list["menuLocale"]["endCode"]

    for data_idx, data in enumerate(data_list):
        if data["displayStartAt"] == update_date:
            idx = find_idx(base_df, name)
            temp1 = base_df[base_df.index < idx]
            temp2 = base_df[base_df.index >= idx]
            code = base_df.iloc[idx - 1]["code"] + 1
            menu_name_loc.append(code)
            name_kr, name_en = data["name"][0], data["name"][1]
            dic = make_locale_dic(code, name_kr, name_en)
            list1.append(dic)
            base_df = temp1.append(list1[data_idx], ignore_index=True).append(temp2, ignore_index=True)
    return base_df, menu_name_loc


def recommend_locale(base_df: pd.DataFrame, data_list, locale_list):
    list1 = []
    list2 = []
    list3 = []

    recommend_name_loc = []
    recommend_prod_loc = []
    recommend_des_loc = []

    product_name = locale_list["productNameLocale"]["endCode"]
    product_des = locale_list["productDesLocale"]["endCode"]
    des = locale_list["DesLocale"]["endCode"]

    for data_idx, data in enumerate(data_list):
        idx = find_idx(base_df, product_name)
        temp1 = base_df[base_df.index < idx]
        temp2 = base_df[base_df.index >= idx]
        code = base_df.iloc[idx - 1]["code"] + 1
        recommend_name_loc.append(code)
        name_kr, name_en = data["name"][0], data["name"][1]
        dic = make_locale_dic(code, name_kr, name_en)
        list1.append(dic)
        base_df = temp1.append(list1[data_idx], ignore_index=True).append(temp2, ignore_index=True)

        idx = find_idx(base_df, product_des)
        temp1 = base_df[base_df.index < idx]
        temp2 = base_df[base_df.index >= idx]
        code = base_df.iloc[idx - 1]["code"] + 1
        recommend_prod_loc.append(code)
        product_description_kr, product_description_en = (
            data["productDescription"][0],
            data["productDescription"][1],
        )
        dic = make_locale_dic(code, product_description_kr, product_description_en)
        list2.append(dic)
        base_df = temp1.append(list2[data_idx], ignore_index=True).append(temp2, ignore_index=True)

        idx = find_idx(base_df, des)
        temp1 = base_df[base_df.index < idx]
        temp2 = base_df[base_df.index >= idx]
        code = base_df.iloc[idx - 1]["code"] + 1
        recommend_des_loc.append(code)
        description_kr, description_en = (
            data["description"][0],
            data["description"][1],
        )
        dic = make_locale_dic(code, description_kr, description_en)
        list3.append(dic)
        base_df = temp1.append(list3[data_idx], ignore_index=True).append(temp2, ignore_index=True)

    loc_dict = {
        "productName": recommend_name_loc,
        "productDescription": recommend_prod_loc,
        "description": recommend_des_loc,
    }

    return base_df, loc_dict


def popup_locale(base_df: pd.DataFrame, data_list, locale_list):
    list1 = []
    list2 = []
    list3 = []

    popup_name_loc = []
    popup_msg_loc = []
    popup_des_loc = []

    name = locale_list["popupNameLocale"]["endCode"]
    msg = locale_list["popupMsgLocale"]["endCode"]
    des = locale_list["popupDesLocale"]["endCode"]

    for data_idx, data in enumerate(data_list):
        idx = find_idx(base_df, name)
        temp1 = base_df[base_df.index < idx]
        temp2 = base_df[base_df.index >= idx]
        code = base_df.iloc[idx - 1]["code"] + 1
        popup_name_loc.append(code)
        name_kr, name_en = data["name"][0], data["name"][1]
        dic = make_locale_dic(code, name_kr, name_en)
        list1.append(dic)
        base_df = temp1.append(list1[data_idx], ignore_index=True).append(temp2, ignore_index=True)

        idx = find_idx(base_df, msg)
        temp1 = base_df[base_df.index < idx]
        temp2 = base_df[base_df.index >= idx]
        code = base_df.iloc[idx - 1]["code"] + 1
        popup_msg_loc.append(code)
        popup_message_kr, popup_message_en = (
            data["popupMessage"][0],
            data["popupMessage"][1],
        )
        dic = make_locale_dic(code, popup_message_kr, popup_message_en)
        list2.append(dic)
        base_df = temp1.append(list2[data_idx], ignore_index=True).append(temp2, ignore_index=True)

        idx = find_idx(base_df, des)
        temp1 = base_df[base_df.index < idx]
        temp2 = base_df[base_df.index >= idx]
        code = base_df.iloc[idx - 1]["code"] + 1
        popup_des_loc.append(code)
        description_kr, description_en = (
            data["description"][0],
            data["description"][1],
        )
        dic = make_locale_dic(code, description_kr, description_en)
        list3.append(dic)
        base_df = temp1.append(list3[data_idx], ignore_index=True).append(temp2, ignore_index=True)

    loc_dict = {
        "productName": popup_name_loc,
        "productMessage": popup_msg_loc,
        "description": popup_des_loc,
    }

    return base_df, loc_dict


######################### 미션


def change_type_of(value):
    if isinstance(value, (float, int)):
        return value
    if value.isdecimal():
        return int(value)
    try:
        return float(value)
    except ValueError:
        return str(value)


def sub_convert_mission_list(idx, raw_data):
    mission_group_idx = 0
    mission_detail_idx = 0
    result = []
    while raw_data.iloc[idx, 1] != "missionListEnd":
        key = raw_data.iloc[idx, 1]
        if "제목 및 탭 문구" in key:
            mission_group = {
                "index": mission_group_idx,
                "tabTitleLocale": list(filter(None, raw_data.iloc[idx, :].to_list()[2:])),
            }
            idx += 1
            mission_group["missionDescLocale"] = list(filter(None, raw_data.iloc[idx, :].to_list()[2:]))
            idx += 1

            mission_detail_list = []
            key = raw_data.iloc[idx, 1]
            while not any(word in key for word in ["제목 및 탭 문구", "이미지", "missionListEnd"]):
                mission_detail = {
                    "index": mission_detail_idx,
                    "titleLocale": list(filter(None, raw_data.iloc[idx, :].to_list()[2:4])),
                }
                idx += 1
                info_list = list(filter(None, raw_data.iloc[idx, 1:].to_list()))
                if len(info_list) != 9:
                    print("미션에 필요한 값을 모두 입력하지 않았습니다. 해당 미션 : " + mission_detail["titleLocale"][0])

                mission_detail["descLocale"] = info_list[1:3]
                mission_detail["value"] = info_list[3]
                mission_detail["itemName"] = info_list[4:6]
                mission_detail["rewardQuantity"] = int(info_list[7])
                mission_detail["menu"] = info_list[8]

                mission_detail_list.append(mission_detail)
                idx += 1
                mission_detail_idx += 1
                key = raw_data.iloc[idx, 1]

            mission_group["missionItemList"] = mission_detail_list

            while "이미지" in raw_data.iloc[idx, 1]:
                idx += 1
            mission_detail_idx = 0

        result.append(mission_group)
        mission_group_idx += 1

    idx += 2
    result.sort(key=lambda x: x["index"])
    return idx, result


def sub_convert(idx, raw_data, is_list=False):
    start_re = "Start$"
    end_re = "End$"
    list_re = "List$"

    if is_list:
        result = []
    else:
        result = {}

    while idx < len(raw_data):
        key = change_type_of(raw_data.iloc[idx, 1])

        # 새로운 자식 생성의 경우
        if re.search(start_re, str(key)):
            child_key = change_type_of(raw_data.iloc[idx, 2])
            if child_key == "missionList":
                idx, child_item = sub_convert_mission_list(idx + 1, raw_data)
                if raw_data.iloc[idx, 1] != "conditionScriptListStart":
                    idx, conditionScriptList = sub_convert(idx, raw_data, is_list=True)
                    cidx = 0
                    for mission_group in child_item:
                        for mission_detail in mission_group["missionItemList"]:
                            if cidx >= len(conditionScriptList):
                                break
                            del conditionScriptList[cidx]["index"]
                            mission_detail["conditionScript"] = conditionScriptList[cidx]
                            cidx += 1
            elif re.search(list_re, str(child_key)):
                idx, child_item = sub_convert(idx + 1, raw_data, is_list=True)
            else:
                idx, child_item = sub_convert(idx + 1, raw_data)

            if is_list:
                result.append(child_item)
            else:
                result[child_key] = child_item

        # 현재 딕셔너리가 끝나는 지점인 경우
        elif re.search(end_re, str(key)):
            return idx, result

        # value가 있는 경우
        elif raw_data.iloc[idx, 2] != "":
            if raw_data.iloc[idx, 3] == "":
                values = change_type_of(raw_data.iloc[idx, 2])
            else:
                values = list(filter(None, raw_data.iloc[idx, :].to_list()[2:]))
            result[key] = values
        idx += 1

    if is_list:
        result.sort(key=lambda x: x["index"])
    return idx, result


def convert_to_json(raw_data):
    home_dict = {}

    raw_data = raw_data.fillna("")

    is_valid, home_dict = sub_convert(0, raw_data)

    if is_valid < len(raw_data):
        print("데이터를 다 읽지 못했습니다.")
        print("마지막으로 읽은 데이터 위치 : ", is_valid, "전체 데이터 길이 : ", len(raw_data))
        print("모든 값에 대해 Start, End 처리가 되어있는지 확인해주세요")
        sys.exit()

    if home_dict == {}:
        print("인식된 데이터가 없습니다.")
        sys.exit()

    return json.dumps(home_dict, ensure_ascii=False)


# base_data에서 어떤 컬럼(column_name)이 target값을 '포함'하는 가장 처음 인덱스 반환
def find_first_index_target_contain(base_df: pd.DataFrame, column_name, target):
    for item in base_df[column_name].items():
        if str(target) in str(item[1]).replace("(", "\(").replace(")", "\)"):
            target = str(item[1])
            break
    result = base_df.loc[base_df[column_name] == target]
    if result.empty:
        return -1
    return result.index[0]


# base_data에서 어떤 컬럼(column_name)이 target값을 '포함'하는 가장 마지막 인덱스 반환
def find_last_index_targets_contain(base_df: pd.DataFrame, column_name, targets_str):
    targets = targets_str.split(",")
    new_target = ""
    find = True
    for item in reversed(list(base_df[column_name].items())):
        for target in targets:
            if str(target) not in str(item[1]).replace("(", "\(").replace(")", "\)"):
                find = False
                break
        if find:
            new_target = str(item[1])
            break
        find = True

    result = base_df.loc[base_df[column_name] == new_target]
    if result.empty:
        return -1
    return result.index[-1]


# base_data에서 어떤 컬럼(column_name)이 target값을 가지는 가장 마지막 인덱스 반환
def find_last_index(base_df: pd.DataFrame, column_name, target, is_group=False, limit=-1):
    if isinstance(target, int):
        result = base_df.loc[base_df[column_name] == target]
        if limit != -1:
            _, limit_value = find_last_index_and_new_code(base_df, limit)
        while result.empty and is_group:
            target += 1000
            if target > limit_value:
                result = base_df.loc[base_df[column_name] == limit_value]
                break
            result = base_df.loc[base_df[column_name] == target]
    else:
        result = base_df.loc[base_df[column_name] == target]
    if result.empty:
        return -1
    return result.index[0]


# base_data에서 특정 컬럼(column_to_get)의 마지막 값 반환
# 어떤 컬럼(column_name)이 target값을 가지는 데이터로 한정 가능, 0 값을 무시할지 선택 가능
def find_last_value(base_df: pd.DataFrame, column_to_get, column_name="", target="", ignore_zero=False):
    if column_name == "":
        result = base_df[column_to_get].tail(1)
        idx = base_df[column_to_get].index[-1]
        if pd.isna(result.item()):
            idx -= 1
            while pd.isna(base_df.loc[base_df.index == idx][column_to_get].item()):
                idx -= 1
        if ignore_zero and result.item() == 0:
            idx -= 1
            while int(base_df.loc[base_df.index == idx][column_to_get]) == 0:
                idx -= 1
        result = base_df.loc[base_df.index == idx][column_to_get]
    else:
        result = base_df.loc[base_df[column_name] == target][column_to_get].tail(1)
    if result.empty:
        return -1
    return int(result)


# base_data에 특정 data_frame을 삽입
# cut_idx로 삽입 위치 지정 가능
def insert_data_frame_to_base(base_df: pd.DataFrame, data_frame: pd.DataFrame, cut_idx=""):
    if cut_idx != "":
        previous_part = base_df[base_df.index <= cut_idx]
        next_part = base_df[base_df.index > cut_idx]
        new_data = previous_part.append(data_frame).append(next_part)
    else:
        new_data = base_df.append(data_frame)
    new_data = new_data.reset_index()
    new_data = new_data.drop(["index"], axis=1)
    return new_data


# base_data에서 한 행을 삽입
# cut_idx로 삽입 위치 지정 가능
def insert_single_row_to_base(base_df: pd.DataFrame, row_dict, cut_idx=""):
    target_df = pd.DataFrame(columns=base_df.columns)
    target_df.loc[0] = row_dict
    return insert_data_frame_to_base(base_df, target_df, cut_idx)


# base_data와 input_data에 키가 같은 값들을 row에 반영
# locale 제외 설정 가능
def insert_matching_data_to_row(base_df: pd.DataFrame, row_dict, input_dict, locale_dict=None):
    if locale_dict is None:
        locale_dict = {}
    for column in base_df.columns:
        if column in input_dict and column not in locale_dict:
            row_dict[column] = input_dict[column]
    return row_dict


# base_data에서 코드 값이 next_code를 넘지않는 직전의 인덱스값과 새로운 코드값을 반환
def find_last_index_and_new_code(base_df: pd.DataFrame, next_code, is_group=False, limit=-1):
    next_start_idx = find_last_index(base_df, "code", next_code, is_group, limit)
    next_start_idx -= 1
    while pd.isna(base_df.loc[base_df.index == next_start_idx]["code"].item()):
        next_start_idx -= 1
    return (
        next_start_idx,
        int(base_df.loc[base_df.index == next_start_idx]["code"]),
    )


# 그룹별 추가
# mapping_data를 참고해서 추가 위치를 파악하고 input_data[column]값을 추가
def make_locale_group_seperation(locale_df: pd.DataFrame, column, input_dict: dict):
    if input_dict["groupID"] + 1000 == input_dict["endGroupID"]:
        cut_idx, locale_code = find_last_index_and_new_code(locale_df, input_dict["next_" + column])
    else:
        cut_idx, locale_code = find_last_index_and_new_code(
            locale_df, input_dict["groupID"] + 1000 + input_dict["increment_" + column]
        )
    locale_code += 1
    locale_df = add_locale_data_item(locale_df, input_dict[column], cut_idx, locale_code)
    return locale_code, locale_df


# locale_data 단순 추가
# locale_data에서 mapping_data를 참고해서 추가 위치를 파악하고 input_data[column]값을 추가
def make_locale_simple_increment(locale_df: pd.DataFrame, column, input_dict: dict):
    cut_idx, locale_code = find_last_index_and_new_code(locale_df, input_dict["next_" + column])
    locale_code += 1
    locale_df = add_locale_data_item(locale_df, input_dict[column], cut_idx, locale_code)
    return locale_code, locale_df


# locale_data 전에 사용한 곳을 기준으로 덮어쓰기
def make_locale_repeat(locale_df: pd.DataFrame, column, input_dict):
    locale_code = input_dict["previous_" + column] + 1
    if locale_code == input_dict["next_" + column]:
        locale_code = input_dict["start_" + column]
    target_index = find_last_index(locale_df, "code", locale_code)
    for key in locale_df.columns:
        if not re.search("^Unnamed", str(key)):
            locale_df.loc[target_index, key] = input_dict[column][1]
    locale_df.loc[target_index, "code"] = locale_code
    locale_df.loc[target_index, "koKR"] = input_dict[column][0]
    return locale_code, locale_df


# locale_data에 cut_idx위치에 locale_code의 code값으로 values값 추가
def add_locale_data_item(locale_df: pd.DataFrame, value_list, cut_idx, locale_code):
    row = {}
    for column in locale_df.columns:
        if not re.search("^Unnamed", str(column)):
            row[column] = value_list[1]
    row["code"] = locale_code
    row["koKR"] = value_list[0]
    return insert_single_row_to_base(locale_df, row, cut_idx)


def base_dataframe(base_name):
    return pd.DataFrame(base_name)
