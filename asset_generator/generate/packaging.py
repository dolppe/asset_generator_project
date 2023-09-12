import utils

import pandas as pd


def make_package_item(card_pack_df: pd.DataFrame, mapping_dict, planning_item, theme_type):

    item_info_df = mapping_dict["itemInfo"]
    item_list = planning_item["packageItem"]
    theme = planning_item["theme"]
    group = planning_item["group"]
    quantity_list = planning_item["quantity"]
    code_list = []
    if isinstance(item_list, str):
        item_list = [item_list]

    if isinstance(quantity_list, int):
        quantity_list = [quantity_list]

    for idx, item in enumerate(item_list):
        if item in item_info_df:
            code_list.append(item_info_df[item]["item"])
        else:
            if (theme not in item) and (group not in item):
                item = theme + " " + item

            code = card_pack_df[card_pack_df["name"] == item]["code"].to_string(index=False)

            if "\n" in code:
                code = code.split("\n")
                if theme_type == 0:
                    code = code[-1]
                else:
                    code = code[0]

            code_list.append(code)

    package_item = ""

    for i in range(len(item_list)):
        pack = '{"p":' + str(code_list[i]) + ',"q":' + str(quantity_list[i]) + ',"b":0 }'
        if i != len(item_list) - 1:
            package_item += pack + ","
        else:
            package_item += pack

    package_item = "[" + package_item + "]"

    return package_item


def make_df_recommend_store(
    recommend_store_df: pd.DataFrame,
    store_menu_df: pd.DataFrame,
    point_reward_df: pd.DataFrame,
    card_pack_df: pd.DataFrame,
    mapping_dict,
    recommend_planning_list,
    recommend_locale_dict,
    update_base,
    url,
    group_planning_list,
):

    new_list = []
    for planning_idx, planning_item in enumerate(recommend_planning_list):
        idx = utils.find_lastidx(recommend_store_df)
        name_kr, name_en = planning_item["name"][0], planning_item["name"][1]
        theme_type_dict = {}
        for group_item in group_planning_list:
            theme_type_dict[group_item["themeName"]] = group_item["themeType"]

        new_row = {
            "code": recommend_store_df.iloc[idx - 1]["code"] + 1,
            "orderIndex": planning_item["orderIndex"],
            "storeMenuID": store_menu_df[store_menu_df["Unnamed: 1"].str.contains(planning_item["theme"], na=False)][
                "code"
            ].to_string(index=False),
            "packageItem": make_package_item(
                card_pack_df, mapping_dict, planning_item, theme_type_dict[planning_item["theme"]]
            ),
            "badgeIconType": 3 if planning_item["badgeIconType"] == "LIMITED" else 2,
            "sizeType": 1,
            "descriptionType": 2 if planning_item["descriptionType"] == "TRUE" else 1,
            "onedaySell": planning_item["onedaySell"],
            "buyCount": planning_item["buyCount"],
            "paymentType": 1,
            "sellStartAt": store_menu_df[store_menu_df["Unnamed: 1"].str.contains(planning_item["theme"], na=False)][
                "displayStartAt"
            ].to_string(index=False),
            "sellEndAt": store_menu_df[store_menu_df["Unnamed: 1"].str.contains(planning_item["theme"], na=False)][
                "displayEndAt"
            ].to_string(index=False),
            "analyticsData": name_kr,
            "bonusQuantity": 0,
            "nameKR": name_kr,
            "nameEN": name_en,
            "productName": recommend_locale_dict["productName"][planning_idx],
            "productDescription": recommend_locale_dict["productDescription"][planning_idx],
            "description": recommend_locale_dict["description"][planning_idx],
            "productImage": utils.make_resource_url(url, update_base, "recommend", "shop_", name_en, ""),
            "productBgImage": utils.make_resource_url(url, update_base, "recommend", "shop_bg_", name_en, ""),
        }

        if "프로필" in name_kr:
            new_row["descriptionImage"] = utils.make_resource_url(
                url, update_base, "notice", "notice_profile_", planning_item["theme"], ""
            )
        else:
            new_row["descriptionImage"] = utils.make_resource_url(
                url, update_base, "notice", "notice_theme_", planning_item["theme"], ""
            )

        if planning_item["point"] != 0:
            new_row["pointReward"] = point_reward_df[
                point_reward_df["Unnamed: 0"].str.contains(planning_item["theme"], na=False)
            ]["code"].to_string(index=False)
            new_row["getPoint"] = planning_item["point"]

        if planning_item["currencyCode"] == "KRW":  # 인앱 구매 상품
            new_row["sellType"] = 2
            new_row["quantity"] = 1
            new_row["price"] = planning_item["price"]
            new_row["analyticsPrice"] = planning_item["analyticsPrice"]
            new_row["currencyCode"] = planning_item["currencyCode"]
            sku_value_list = []
            for k in range(3):
                idx = utils.find_lastidx(recommend_store_df)
                if k == 0:
                    new_row["sku"] = planning_item["unknownsku"]
                    new_row["targetDevice"] = 0
                    new_row["code"] = recommend_store_df.iloc[idx - 1]["code"] + 1
                    new_list.append(new_row)

                elif k == 1:
                    new_row["sku"] = planning_item["applesku"]
                    new_row["targetDevice"] = 1
                    new_row["code"] = recommend_store_df.iloc[idx - 1]["code"] + 1

                else:
                    new_row["sku"] = planning_item["googlesku"]
                    new_row["targetDevice"] = 2
                    new_row["code"] = recommend_store_df.iloc[idx - 1]["code"] + 1

                sku_value_list.append(new_row)
                recommend_store_df.loc[idx] = sku_value_list[k]

        elif planning_item["currencyCode"] == "dia":  # dia
            new_row["paymentIcon"] = 608
            new_row["targetDevice"] = 3
            new_row["sellType"] = 0
            new_row["quantity"] = 0
            new_row["price"] = planning_item["price"]
            new_list.append(new_row)
            recommend_store_df.loc[idx] = new_list[planning_idx]
        else:  # rp
            new_row["paymentIcon"] = 609
            new_row["targetDevice"] = 3
            new_row["paymentType"] = 3
            new_row["sellType"] = 0
            new_row["quantity"] = 0
            new_row["price"] = planning_item["price"]
            new_list.append(new_row)
            recommend_store_df.loc[idx] = new_list[planning_idx]

    return recommend_store_df


def make_df_popup_store(popup_store_df: pd.DataFrame, popup_planning_list, popup_locale_dict, url, update_base):

    new_list = []
    for planning_idx, planning_item in enumerate(popup_planning_list):
        new_list = []

        package_code_list = planning_item["packageCode"]
        quantity_list = planning_item["quantity"]

        package_item = ""

        for i in range(len(package_code_list)):
            pack = '{"p":' + str(package_code_list[i]) + ',"q":' + str(quantity_list[i]) + ',"b":0 }'
            if i != len(package_code_list) - 1:
                package_item += pack + ","
            else:
                package_item += pack

        package_item = "[" + package_item + "]"

        df_idx = utils.find_lastidx(popup_store_df)
        name_kr, name_en = planning_item["name"][0], planning_item["name"][1]
        new_row = {
            "price": planning_item["price"],
            "analyticsPrice": planning_item["analyticsPrice"],
            "currencyCode": planning_item["currencyCode"],
            "buyCount": planning_item["buyCount"],
            "quantity": 1,
            "bonusQuantity": 0,
            "sellStartAt": planning_item["sellStartAt"],
            "sellEndAt": planning_item["sellEndAt"],
            "onedaySell": "FALSE",
            "orderIndex": planning_item["orderIndex"],
            "printSight": 0,
            "actionType": 0,
            "actionCount": 1,
            "dayCount": 1,
            "isLimited": "TRUE",
            "regionProduct": "FALSE",
            "userCheck": 0,
            "analyticsData": name_kr,
            "nameKR": name_kr,
            "nameEN": name_en,
            "popupSubject": popup_locale_dict["productName"][planning_idx],
            "popupMessage": popup_locale_dict["productMessage"][planning_idx],
            "description": popup_locale_dict["description"][planning_idx],
            "packageItem": package_item,
            "productImage": utils.make_resource_url(url, update_base, "popup", "popshop_", name_en, ""),
        }
        sku_value_list = []

        for k in range(3):

            df_idx = utils.find_lastidx(popup_store_df)

            if k == 0:
                new_row["sku"] = planning_item["unknownsku"]
                new_row["targetDevice"] = 0
                new_row["code"] = popup_store_df.iloc[df_idx - 1]["code"] + 1
                new_list.append(new_row)
                sku_value_list.append(new_row)
                popup_store_df.loc[df_idx] = sku_value_list[k]
            elif k == 1:
                new_row["sku"] = planning_item["googlesku"]
                new_row["targetDevice"] = 1
                new_row["code"] = popup_store_df.iloc[df_idx - 1]["code"] + 1
                sku_value_list.append(new_row)
                popup_store_df.loc[df_idx] = sku_value_list[k]
            else:
                new_row["sku"] = planning_item["applesku"]
                new_row["targetDevice"] = 2
                new_row["code"] = popup_store_df.iloc[df_idx - 1]["code"] + 1
                sku_value_list.append(new_row)
                popup_store_df.loc[df_idx] = sku_value_list[k]

    return popup_store_df
