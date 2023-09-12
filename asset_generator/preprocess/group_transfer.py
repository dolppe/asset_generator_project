import pandas as pd
from generate import group as g


# list => order순 IDX, 원 idx, 정렬된column
# 순서대로 쭉 정렬해줌
def arrange_order(raw_df, column, exception_num):
    value_list = sort_list(raw_df, column)
    value_list = value_list.reset_index()
    for value_list_idx in range(0, len(value_list) - exception_num):
        group_idx = value_list["index"][value_list_idx]
        raw_df.loc[group_idx, column] = value_list_idx
    return raw_df


# df, 컬럼명을 입력으로 받음
# 해당 컬럼의 idx - order로 연결해서 기존 idx순으로 되어있는 것을 order순으로 정렬
def sort_list(raw_df, column):
    temp = raw_df.iloc[2:].astype({column: "int"})
    temp = temp[column].sort_values()

    return temp


# Order, secondOrder를 제일 끝으로 변경해줌
# exception_num => Dalcomsoft라는 그룹이 존재하고, 이의 order가 9999이기 때문에 이를 제외해줌
def group_order_transfer(group_df, exception_num, group_code):
    value_list = sort_list(group_df, "orderIndex")
    idx = group_df.loc[group_df["code"] == group_code].index

    ex_num = 1 + exception_num

    group_df.loc[idx, "orderIndex"] = value_list.iloc[-(ex_num)] + 1
    group_df.loc[idx, "secondOrderIndex"] = value_list.iloc[-(ex_num)] + 1
    group_df = arrange_order(group_df, "orderIndex", 1)
    group_df = arrange_order(group_df, "secondOrderIndex", 1)
    return group_df


def profile_transfer(profile_df, group: g.Group):

    last_idx = profile_df.loc[profile_df["groupID"] == group.origin_group_id].index[-1]

    for idx in range(0, int(group.card_num)):
        profile_df.loc[last_idx - idx, "profileType"] = 0
    return profile_df


def card_transfer(card_df, group: g.Group):
    if card_df.loc[card_df["groupID"] == group.group_id].empty:
        return card_df

    first_idx = card_df.loc[card_df["groupID"] == group.group_id].index[0]

    is_normal = False

    if card_df.loc[first_idx, "percentage"] == 1:
        is_normal = True

    for idx in range(0, int(group.card_num)):
        card_df.loc[first_idx + idx, "groupID"] = group.origin_group_id
        card_df.loc[first_idx + idx, "artistID"] = group.artist.origin_artist_id[idx]
        if is_normal:
            card_df.loc[first_idx + idx, "isSelect"] = "TRUE"

    return card_df


def music_transfer(music_df, group: g.Group):
    if music_df.loc[music_df["groupData"] == group.group_id].empty:
        return music_df
    first_idx = music_df.loc[music_df["groupData"] == group.group_id].index[0]
    music_df.loc[first_idx, "groupData"] = group.origin_group_id
    music_df.loc[first_idx, "localeDisplayGroupName"] = group.group_locale
    return music_df


def group_transfer(
    mapping_dict,
    planning_dict,
    group_df: pd.DataFrame,
    profile_df,
    card_df,
    music_df,
):
    transfer_dict = planning_dict["transferList"]
    mapping_group = mapping_dict["groupList"]
    for transfer in transfer_dict:
        transfer_group_name = transfer["GroupName"]
        for mapping_group_item in mapping_group:
            group = g.Group(mapping_group_item)
            if group.origin_group_name == transfer_group_name:
                transfer_group = group
        transfer_group_idx = transfer_group.find_idx(group_df)
        transfer_group.set_groupid(group_df.loc[transfer_group_idx, "code"])

        group_df = group_order_transfer(group_df, 1, transfer_group.group_id)
        profile_df = profile_transfer(profile_df, transfer_group)
        card_df = card_transfer(card_df, transfer_group)
        music_df = music_transfer(music_df, transfer_group)

    return group_df, profile_df, card_df, music_df
