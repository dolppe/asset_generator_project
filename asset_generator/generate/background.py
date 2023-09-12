import utils


bg_locale = {"bgName": "bgName", "itemName": "bgName"}

bg_store_locale = {"sellName": "sellName", "description": "description"}


def make_df_lobby_bg(lobby_bg_df, input_dict, locale_df):

    update_date = input_dict["updateDate"]

    for bg_input_dict in input_dict["bgList"]:
        if "appendType" not in bg_input_dict:
            print(
                "mapping에 없는 타입의 배경이 포함되어 있습니다. bgName : [ "
                + bg_input_dict["bgName"][0]
                + " ], sellType : [ "
                + bg_input_dict["sellType"]
                + " ]"
            )
            bg_input_dict["appendType"] = -1
            continue
        elif bg_input_dict["appendType"] == 1:
            append_type = 1
            lobby_bg_code = 1 + utils.find_last_value(lobby_bg_df, "code")
        else:
            append_type = 2
            df_idx = utils.find_last_index(
                lobby_bg_df, "groupID", bg_input_dict["groupID"]
            )  # groupID는 초기 입력값이 아니라, 받아와서 저장한 값
            lobby_bg_code = 1 + utils.find_last_value(
                lobby_bg_df,
                "code",
                column_name="groupID",
                target=bg_input_dict["groupID"],
            )

        new_row = {
            "code": lobby_bg_code,
            "analyticsData": bg_input_dict["bgName"][1],
        }
        new_row = utils.insert_matching_data_to_row(lobby_bg_df, new_row, bg_input_dict, bg_locale)

        if bg_input_dict["appendType_bgName"] == 1:
            new_row["bgName"], locale_df = utils.make_locale_simple_increment(locale_df, "bgName", bg_input_dict)
        else:
            new_row["bgName"], locale_df = utils.make_locale_group_seperation(locale_df, "bgName", bg_input_dict)

        new_row["itemName"] = new_row["bgName"]

        new_row["bgImageSmall"] = utils.make_resource_url(
            input_dict["imageURL"],
            update_date,
            "mission",
            "mylobby_bg_",
            bg_input_dict["theme"][1],
            "_s",
        )
        new_row["bgImageLarge"] = utils.make_resource_url(
            input_dict["imageURL"],
            update_date,
            "mission",
            "mylobby_bg_",
            bg_input_dict["theme"][1],
            "_l",
        )

        bg_input_dict["lobbyBgID"] = lobby_bg_code
        if append_type == 1:
            lobby_bg_df = utils.insert_single_row_to_base(lobby_bg_df, new_row)
        else:
            lobby_bg_df = utils.insert_single_row_to_base(lobby_bg_df, new_row, df_idx)

    return lobby_bg_df, locale_df


def make_df_card_pack(card_pack_df, input_dict):
    for bg_input_dict in input_dict["bgList"]:
        if bg_input_dict["appendType"] == -1:
            continue
        elif bg_input_dict["appendType_cardPackCode"] == 1:
            df_idx, pre_card_pack_code = utils.find_last_index_and_new_code(
                card_pack_df, bg_input_dict["next_cardPackCode"]
            )
        else:
            df_idx, pre_card_pack_code = utils.find_last_index_and_new_code(
                card_pack_df,
                bg_input_dict["groupID"] + 1000 + bg_input_dict["increment_cardPackCode"],
                True,
                bg_input_dict["next_cardPackCode"],
            )

        pre_card_pack_code += 1

        new_row = {
            "code": pre_card_pack_code,
            "name": bg_input_dict["bgName"][0],
            "nameKR": bg_input_dict["bgName"][0],
            "nameEN": bg_input_dict["bgName"][1],
        }
        new_row = utils.insert_matching_data_to_row(card_pack_df, new_row, bg_input_dict)

        bg_input_dict["product"] = pre_card_pack_code
        card_pack_df = utils.insert_single_row_to_base(card_pack_df, new_row, df_idx)
    return card_pack_df


def make_lobby_bg_store_df(lobby_bg_store_df, input_dict, locale_df):
    for bg_input_dict in input_dict["bgList"]:
        if bg_input_dict["appendType"] == -1:
            continue

        df_idx = utils.find_last_index(lobby_bg_store_df, "lobbyBgID", bg_input_dict["lobbyBgID"] - 1)
        lobby_bg_store_code = 1 + utils.find_last_value(
            lobby_bg_store_df,
            "code",
            column_name="lobbyBgID",
            target=bg_input_dict["lobbyBgID"] - 1,
        )

        sell_type = bg_input_dict["sellType"]

        new_row = {
            "code": lobby_bg_store_code,
            "analyticsData": bg_input_dict["bgName"][1],
        }

        # orderIndex
        lobby_bg_store_sell_type_df = lobby_bg_store_df.loc[lobby_bg_store_df["sellType"] == sell_type]
        if sell_type == 2:  # 이벤트
            bg_input_dict["orderIndex"] = lobby_bg_store_sell_type_df["orderIndex"].min() - 1
        else:
            bg_input_dict["orderIndex"] = lobby_bg_store_sell_type_df["orderIndex"].max() + 1

        new_row = utils.insert_matching_data_to_row(lobby_bg_store_df, new_row, bg_input_dict, bg_store_locale)

        if "fixed_description" in bg_input_dict:
            new_row["description"] = bg_input_dict["fixed_description"]
        else:
            new_row["description"], locale_df = utils.make_locale_simple_increment(
                locale_df, "description", bg_input_dict
            )

            if sell_type == 2:  # 이벤트
                new_row["sellName"], locale_df = utils.make_locale_simple_increment(
                    locale_df, "sellName", bg_input_dict
                )

        if "paymentType" in new_row:
            if new_row["paymentType"] == 1:
                new_row["paymentCategory"] = 4
            elif new_row["paymentType"] == 3:
                new_row["paymentCategory"] = 5

        lobby_bg_store_df = utils.insert_single_row_to_base(lobby_bg_store_df, new_row, df_idx)
    return lobby_bg_store_df, locale_df
