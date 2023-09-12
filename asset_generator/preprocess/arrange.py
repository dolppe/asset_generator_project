import datetime
import pandas as pd


def store_menu_arrange(store_menu_df: pd.DataFrame, update_date):

    update = datetime.datetime.strptime(update_date, "%Y-%m-%d %H:%M:%S")
    base_time_list = store_menu_df[store_menu_df["tabGroup"] == 1]["displayEndAt"].tolist()
    base_code = store_menu_df[store_menu_df["tabGroup"] == 1]["code"].tolist()

    real_base_time = []
    valid_code_list = []
    used_code_list = []

    # 기간에 맞지 않는 추천 상품 삭제
    for idx, base_time_list in enumerate(base_time_list):
        real_base_time.append(datetime.datetime.strptime(base_time_list, "%Y-%m-%d %H:%M:%S"))
        if real_base_time[idx] <= update:
            valid_code_list.append(base_code[idx])
            store_menu_df = store_menu_df[store_menu_df["code"] != base_code[idx]]
        else:
            used_code_list.append(base_code[idx])

    return store_menu_df, valid_code_list, used_code_list


def store_home_arrange(store_home_df: pd.DataFrame, update_date):

    update = datetime.datetime.strptime(update_date, "%Y-%m-%d %H:%M:%S")
    store_home_df = store_home_df.iloc[2:]
    base_time_list = store_home_df["displayEndAt"].tolist()
    real_base_time = []

    for idx, base_time in enumerate(base_time_list):
        real_base_time.append(datetime.datetime.strptime(base_time, "%Y-%m-%d %H:%M:%S"))
        if real_base_time[idx] <= update:
            store_home_df = store_home_df[store_home_df["displayEndAt"] != base_time]

    return store_home_df


def event_management_arrange(event_management_df: pd.DataFrame, update_date, bg_list_size):
    update = datetime.datetime.strptime(update_date, "%Y-%m-%d %H:%M:%S")
    base_time_list = event_management_df["eventEndAt"].tolist()
    idx_order_index_target = []
    for idx, base_time in enumerate(base_time_list):
        if idx < 2 or not isinstance(base_time, str):
            continue
        if datetime.datetime.strptime(base_time, "%Y-%m-%d %H:%M:%S") > update:
            idx_order_index_target.append((idx, event_management_df.loc[idx, "orderIndex"]))
    idx_order_index_target.sort(key=lambda x: x[1])
    for order, target in enumerate(idx_order_index_target):
        event_management_df.loc[target[0], "orderIndex"] = order + bg_list_size + 1

    return event_management_df
