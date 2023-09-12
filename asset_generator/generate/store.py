import pandas as pd

from preprocess import arrange
import utils


def make_df_store_menu(
    store_menu_df: pd.DataFrame, point_reward_df: pd.DataFrame, menu_planning_list, menu_locale_dict, url, update_base
):

    new_list = []
    store_menu_df, valid_code_list, used_code_list = arrange.store_menu_arrange(store_menu_df, update_base)
    num = 0

    for i, planning_item in enumerate(menu_planning_list):

        name_kr, name_en = planning_item["name"][0].strip(), planning_item["name"][1].strip()
        # 이번에 새로 업데이트 하는 것들만 추가
        if planning_item["displayStartAt"] == update_base:

            idx = 3 + i
            temp1 = store_menu_df[store_menu_df.index < idx]
            temp2 = store_menu_df[store_menu_df.index >= idx]

            if valid_code_list and num < len(valid_code_list):
                store_menu_code = valid_code_list[num]
            else:
                for code in range(101, 1999):
                    if code not in used_code_list:
                        store_menu_code = code
                        break

            new_row = {
                "Unnamed: 1": name_kr,
                "code": store_menu_code,
                "unLock": "TRUE",
                "tabGroup": 1,
                "orderIndex": planning_item["index"],
                "tabGroupName": 64000001,
                "tabName": menu_locale_dict[num],
                "badgeIcon": 0,
                "storeType": 1,
                "displayStartAt": planning_item["displayStartAt"],
                "displayEndAt": planning_item["displayEndAt"],
                "bannerContentsKR": utils.make_resource_url(
                    url, update_base, "recommend", "topbanner_", name_en, "_kr"
                ),
                "bannerContentsUS": utils.make_resource_url(
                    url, update_base, "recommend", "topbanner_", name_en, "_en"
                ),
            }
            planning_item["newcode"] = store_menu_code

            if planning_item["pointReward"] != 0:
                point_code = point_reward_df[
                    point_reward_df["Unnamed: 0"].str.contains(planning_item["pointReward"], na=False)
                ]["code"].to_list()
                new_row["pointRewardID"] = point_code

            new_list.append(new_row)
            store_menu_df = temp1.append(new_list[num], ignore_index=True).append(temp2, ignore_index=True)
            num += 1
        else:
            idx = store_menu_df.index[(store_menu_df["Unnamed: 1"] == name_kr)].tolist()
            store_menu_df.at[idx[0], "orderIndex"] = planning_item["index"]
            planning_item["newcode"] = store_menu_df.at[idx[0], "code"]

    return store_menu_df, menu_planning_list


def make_df_store_home(store_home_df: pd.DataFrame, store_menu_df: pd.DataFrame, home_planning_list, url, update_base):

    store_home_head = store_home_df.iloc[:2]
    store_home_tail = arrange.store_home_arrange(store_home_df, update_base)
    store_home_df = pd.merge(store_home_head, store_home_tail, how="outer")

    new_list = []

    for i, planning_item in enumerate(home_planning_list):

        code = store_menu_df[
            store_menu_df["Unnamed: 1"].str.contains(
                planning_item["LinkedStore"].replace("[", "\[").replace("]", "\]"), na=False
            )
        ]["code"].to_string(index=False)

        name_kr, name_en = planning_item["name"][0].strip(), planning_item["name"][1].strip()

        if planning_item["displayStartAt"] == update_base:

            idx = i + 2
            temp1 = store_home_df[store_home_df.index < idx]
            temp2 = store_home_df[store_home_df.index >= idx]

            new_row = {
                "Unnamed: 0": name_kr,
                "code": planning_item["index"] + 1,
                "orderIndex": planning_item["index"] + 1,
                "storeMenuID": 0,
                "LinkedStore": code,
                "displayStartAt": planning_item["displayStartAt"],
                "displayEndAt": planning_item["displayEndAt"],
                "bannerContentsKR": utils.make_resource_url(
                    url, update_base, "recommend", "shop_main_", name_en, "_kr"
                ),
                "bannerContentsUS": utils.make_resource_url(
                    url, update_base, "recommend", "shop_main_", name_en, "_en"
                ),
            }

            new_list.append(new_row)
            store_home_df = temp1.append(new_list[i], ignore_index=True).append(temp2, ignore_index=True)
        else:
            idx = store_home_df.index[(store_home_df["Unnamed: 0"] == name_kr)].tolist()
            store_home_df.at[idx[0], "orderIndex"] = planning_item["index"] + 1
            store_home_df.at[idx[0], "code"] = planning_item["index"] + 1

    return store_home_df
