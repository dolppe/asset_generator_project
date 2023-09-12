import pandas as pd
import utils
import numpy as np


def make_df_point(point_df: pd.DataFrame, card_pack_df: pd.DataFrame, point_planning_list, point_locale_dict):

    new_list = []
    for i, planning_item in enumerate(point_planning_list):
        idx = utils.find_lastidx(point_df)
        reward_kr = planning_item["reward"][0]
        reward_name = reward_kr.replace("(랜덤)", "").strip()
        new_row = {
            "Unnamed: 0": reward_kr,
            "code": point_df.loc[utils.find_lastidx(point_df) - 1]["code"] + 1,
            "pointMaximum": planning_item["pointMaximum"],
            "description": point_locale_dict["description"][i],
            "reward": card_pack_df[card_pack_df["name"].str.contains(reward_name, na=False)]["code"].to_string(
                index=False
            ),
            "quantity": 1,
            "rewardName": point_locale_dict["rewardName"][i],
            "pointColor": "0xF6445EFF",
            "rewardTitle": 181490001,
            "rewardMsg": point_locale_dict["rewardMsg"][i],
            "rewardMsgPeriod": "30",
            "saveStartAt": planning_item["saveStartAt"],
            "saveEndAt": planning_item["saveEndAt"],
        }
        new_list.append(new_row)
        point_df.loc[idx] = new_list[i]

    return point_df


def make_df_point_card_pack(card_pack_df: pd.DataFrame, theme_df: pd.DataFrame, point_planning_list, mapping):

    for i, planning_item in enumerate(point_planning_list):
        new_list = []
        next_code = mapping["pointCode"]["endCode"]
        reward_kr, reward_en = planning_item["reward"][0], planning_item["reward"][1]
        if "선택권" in reward_kr:
            idx = utils.find_idx(card_pack_df, next_code)
            dic = {
                "name": reward_kr,
                "code": card_pack_df.iloc[idx - 1]["code"] + 1,
                "category": 62,
                "cardGrade": 4 if "R" in reward_kr else 2,
                "groupLimited": "FALSE",
                "nameKR": reward_kr,
                "nameEN": reward_en,
                "rateDisplay": "FALSE",
                "themeList": theme_df[theme_df["analyticsData"].str.contains(planning_item["theme"], na=False)][
                    "code"
                ].to_list(),
            }
            new_list.append(dic)
            card_pack_df.loc[idx] = new_list[i]
    return card_pack_df


def make_df_card_pack(
    card_pack_df: pd.DataFrame,
    theme_df: pd.DataFrame,
    card_df: pd.DataFrame,
    group_planning_list,
    card_planning_list,
    mapping_dict,
):
    item_dict = mapping_dict["itemInfo"]
    basic_list = mapping_dict["basicCard"]
    theme_list = []

    for group_item in group_planning_list:
        theme_list.append(group_item["themeName"])

    next_code = mapping_dict["cardCode"]["endCode"]

    for theme_item in theme_list:

        # 기본 카드
        for basic_item in basic_list:
            df_idx = utils.find_idx(card_pack_df, next_code)
            name_kr, name_en = item_dict[basic_item]["name"][0], item_dict[basic_item]["name"][1]
            new_row = {
                "name": theme_item + " " + name_kr,
                "category": item_dict[basic_item]["category"],
                "groupLimited": "FALSE",
                "theme1": theme_df[theme_df["analyticsData"].str.contains(theme_item, na=False)]["code"].to_string(
                    index=False
                ),
                "nameKR": theme_item + " " + name_kr,
                "nameEN": theme_item + " " + name_en,
                "rateDisplay": "TRUE",
                "code": card_pack_df.iloc[df_idx - 1]["code"] + 1,
            }

            if item_dict[basic_item]["category"] == 2:
                new_row["cardGrade"] = item_dict[basic_item]["cardGrade"]

            temp1 = card_pack_df[card_pack_df.index < df_idx]
            temp2 = card_pack_df[card_pack_df.index >= df_idx]

            card_pack_df = temp1.append(new_row, ignore_index=True).append(temp2, ignore_index=True)

        # 추가 카드
        for planning_item in card_planning_list:
            if planning_item["theme"] == theme_item:
                name_kr, name_en = planning_item["name"][0], planning_item["name"][1]

                # 테마리스트 넣기
                theme_list_str = make_theme_list(planning_item, card_df, theme_df)
                df_idx = utils.find_idx(card_pack_df, next_code)
                new_row = {
                    "code": card_pack_df.iloc[df_idx - 1]["code"] + 1,
                    "name": theme_item + " " + name_kr,
                    "groupLimited": "FALSE",
                    "nameKR": name_kr,
                    "nameEN": name_en,
                    "rateDisplay": "TRUE",
                    "themeList": theme_list_str,
                }

                if planning_item["prism"] == 1:
                    name_kr = "프리즘 " + name_kr
                    name_kr = name_kr.strip()
                    percentage = planning_item["prism_percent"]
                    print(name_kr)
                    print("per: ", percentage)

                for key in item_dict.keys():

                    if key in name_kr:
                        if planning_item["prism"] == 1:
                            per_list = item_dict[name_kr]["percentage"]
                            print(per_list)
                            idx = per_list.index(percentage)
                            print(item_dict[name_kr]["category"][idx])
                            new_row["category"] = item_dict[name_kr]["category"][idx]
                        else:
                            new_row["category"] = item_dict[key]["category"]
                            if item_dict[key]["category"] == 2:
                                new_row["cardGrade"] = item_dict[key]["cardGrade"]

                temp1 = card_pack_df[card_pack_df.index < df_idx]
                temp2 = card_pack_df[card_pack_df.index >= df_idx]
                card_pack_df = temp1.append(new_row, ignore_index=True).append(temp2, ignore_index=True)

    return card_pack_df


def make_theme_list(planning_item, card_df, theme_df):
    theme_type = planning_item["type"]
    if theme_type == 1:
        theme_list = make_normal_theme_list(planning_item, theme_df)
    elif theme_type == 2:
        theme_list = make_limited_theme_list(planning_item, card_df, theme_df)
    elif theme_type == 3:
        theme_list = make_mixed_theme_list(planning_item, card_df, theme_df)
    theme_list_str = ",".join(str(s) for s in theme_list)
    return "[" + theme_list_str + "]"


def make_normal_theme_list(planning_item, theme_df):
    theme = planning_item["theme"]
    percent = planning_item["percent"]
    normal_theme_list = get_normal_theme_list(theme_df)
    theme_code = find_theme_code(theme, theme_df)
    for i in range(0, (percent // 100) - 1):
        normal_theme_list.append(theme_code)
    return normal_theme_list


# 업데이트 테마가 이한테인 경우를 대비하여 해당 테마가 추가 됐는지 확인하고 리스트 생성 해야함
def make_limited_theme_list(planning_item, card_df, theme_df):
    theme = planning_item["theme"]
    theme_code = find_theme_code(theme, theme_df)

    if "condition" not in planning_item:
        theme_list, theme_count = get_condition_theme_list(card_df, theme_code)

    else:
        condition = planning_item["condition"]
        condition_length = len(condition)

        if condition_length == 2:
            theme_list, theme_count = get_condition_theme_list(card_df, theme_code, condition[0], condition[1])

        else:
            theme_list, theme_count = get_condition_theme_list(card_df, theme_code, condition)

    return theme_list


def make_mixed_theme_list(planning_item, card_df, theme_df):
    theme = planning_item["theme"]
    theme_code = find_theme_code(theme, theme_df)
    percent = planning_item["percent"]

    if "condition" not in planning_item:
        theme_list, theme_count = get_condition_theme_list(card_df, theme_code)

    else:
        condition = planning_item["condition"]
        condition_length = len(condition)

        if condition_length == 2:
            theme_list, theme_count = get_condition_theme_list(card_df, theme_code, condition[0], condition[1])

        else:
            theme_list, theme_count = get_condition_theme_list(card_df, theme_code, condition)

    normal_list = get_normal_theme_list(theme_df)
    normal_count = get_normal_theme_count(card_df)
    theme_iter, normal_iter = calc_theme_per(theme_count, normal_count, percent)
    total_theme_list = iter_theme_list(theme_list, theme_iter)
    total_normal_list = iter_theme_list(normal_list, normal_iter)

    total_normal_list.extend(total_theme_list)

    return total_normal_list


def iter_theme_list(theme_list, iter_count):
    total_list = []
    for i in range(0, iter_count):
        total_list.extend(theme_list)
    return total_list


def calc_theme_per(theme_count, normal_count, target_per):
    theme_iter = 1
    normal_iter = 1
    target_per = float(target_per) * 0.01
    allow_low_per = target_per - 0.001
    allow_up_per = target_per + 0.001
    cur_per = float(theme_count * theme_iter) / float(theme_count * theme_iter + normal_count * normal_iter)
    while (cur_per < allow_low_per) or (cur_per > allow_up_per):
        if cur_per < allow_low_per:
            theme_iter += 1
        elif cur_per > allow_up_per:
            normal_iter += 1
        cur_per = float(theme_count * theme_iter) / float(theme_count * theme_iter + normal_count * normal_iter)

    return theme_iter, normal_iter


def get_normal_theme_count(card_df):
    normal_list = card_df.loc[card_df.percentage == 1, "code"]
    return len(normal_list.index)


def get_normal_theme_list(theme_df):
    normal_code = theme_df.loc[theme_df.limitedType == 0, "code"]
    normal_theme_list = []  # 리스트? 스트링?
    for normal_code_item in normal_code:
        normal_theme_list.append(normal_code_item)
    return normal_theme_list


def find_theme_code(theme_name, theme_df):
    idx = -1
    for theme_df_item in theme_df["analyticsData"]:
        idx += 1
        if theme_name in theme_df_item:
            break
    return theme_df.loc[idx, "code"]


def get_condition_theme_list(card_df, theme_code, first_time="", second_time=""):
    # 처음부터 first_time 전까지만

    limited_theme_list = card_df.loc[card_df.percentage == 0, ["percentage", "sellStartAt", "theme", "myStoreAppear"]]
    limited_theme_list = limited_theme_list.loc[
        card_df.myStoreAppear == True, ["myStoreAppear", "sellStartAt", "theme"]
    ]
    condition_pass_list = []
    if first_time == "":
        update_card_df = card_df.loc[card_df.theme == theme_code, ["sellStartAt", "myStoreAppear", "theme"]]
        for index, update_card_df_item in update_card_df.iterrows():
            condition_pass_list.append(update_card_df_item)
        theme_count = len(condition_pass_list)
        theme_set = set()
        for condition_pass_list_item in condition_pass_list:
            theme_set.add(condition_pass_list_item["theme"])
        return list(theme_set), theme_count

    fyear = int(first_time[0:4])
    fmonth = int(first_time[5:7])
    if second_time == "":
        for index, limited_theme_list_item in limited_theme_list.iterrows():
            year = int(limited_theme_list_item["sellStartAt"][0:4])
            month = int(limited_theme_list_item["sellStartAt"][5:7])
            if year < fyear:
                condition_pass_list.append(limited_theme_list_item)
            elif year == fyear:
                if month < fmonth:
                    condition_pass_list.append(limited_theme_list_item)
    # first_time ~ second_time-1
    else:
        syear = int(second_time[0:4])
        smonth = int(second_time[5:7])
        for index, limited_theme_list_item in limited_theme_list.iterrows():
            year = int(limited_theme_list_item["sellStartAt"][0:4])
            month = int(limited_theme_list_item["sellStartAt"][5:7])
            if year > fyear and year < syear:
                condition_pass_list.append(limited_theme_list_item)
            elif year == fyear and year == syear:
                if month >= fmonth and month < smonth:
                    condition_pass_list.append(limited_theme_list_item)
            elif year == fyear:
                if month >= fmonth:
                    condition_pass_list.append(limited_theme_list_item)
            elif year == syear:
                if month < smonth:
                    condition_pass_list.append(limited_theme_list_item)

    theme_count = len(condition_pass_list)
    theme_set = set()
    for condition_pass_list_item in condition_pass_list:
        theme_set.add(condition_pass_list_item["theme"])
    return list(theme_set), theme_count

