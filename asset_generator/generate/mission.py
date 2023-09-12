import json
import utils

import pandas as pd

event_management_locale = {
    "eventNameLocale": "eventNameLocale",
    "helpDescLocale": "helpDescLocale",
}

event_mission_locale = {
    "tabTitleLocale": "tabTitleLocale",
    "missionDescLocale": "missionDescLocale",
    "titleLocale": "titleLocale",
    "descLocale": "descLocale",
    "itemName": "itemName",
}

generated_reward_list = {}


def make_df_event_management(
    event_management_df: pd.DataFrame,
    input_dict,
    lobby_bg_store_df,
    locale_df,
):
    update_date = input_dict["updateDate"]
    img_url = input_dict["imageURL"]

    for event_input_dict in input_dict["eventList"]:
        event_management_code = 1 + utils.find_last_value(event_management_df, "code")
        event_code = 1 + utils.find_last_value(
            event_management_df,
            "eventCode",
            column_name="eventType",
            target=event_input_dict["eventType"],
        )
        event_input_dict["eventCode"] = event_code

        new_row = {
            "code": event_management_code,
            "orderIndex": event_input_dict["index"] + 1,
        }
        new_row = utils.insert_matching_data_to_row(
            event_management_df,
            new_row,
            event_input_dict,
            event_management_locale,
        )

        new_row["eventNameLocale"], locale_df = utils.make_locale_simple_increment(
            locale_df, "eventNameLocale", event_input_dict
        )
        new_row["helpDescLocale"], locale_df = utils.make_locale_simple_increment(
            locale_df, "helpDescLocale", event_input_dict
        )

        new_row["eventImageMain"] = utils.make_resource_url(
            img_url,
            update_date,
            "mission",
            "web_event_",
            event_input_dict["theme"][1],
            "_header",
        )
        new_row["eventImageHead"] = new_row["eventImageMain"]
        new_row["eventImageTail"] = utils.make_resource_url(
            img_url,
            update_date,
            "mission",
            "web_event_",
            event_input_dict["theme"][1],
            "_footer",
        )
        new_row["eventImageTailbg"] = utils.make_resource_url(
            img_url,
            update_date,
            "mission",
            "web_event_",
            event_input_dict["theme"][1],
            "_footer_bg",
        )

        # BgStoreData eventManagementID 처리
        lobby_bg_store_df_idx = utils.find_last_index(
            lobby_bg_store_df,
            "eventManagementID",
            event_input_dict["eventNameLocale"][0],
        )
        if lobby_bg_store_df_idx != -1:
            lobby_bg_store_df.loc[lobby_bg_store_df_idx, "eventManagementID"] = event_management_code

        event_management_df = utils.insert_single_row_to_base(event_management_df, new_row)
    return event_management_df, lobby_bg_store_df, locale_df


def make_dict_condition_script(condition_script, group_df, music_df, theme_df, artist_df):
    if "group" in condition_script:
        condition_script["group"] = str(condition_script["group"]).strip()
        if "EVENT" in condition_script["group"]:
            idx = utils.find_last_index(group_df, "analyticsData", condition_script["group"])
        else:
            idx = utils.find_first_index_target_contain(group_df, "analyticsData", condition_script["group"])
        if idx == -1:
            print("conditionScript에 작성된 그룹을 찾을 수 없습니다 : ", condition_script["group"])
            return {"error": -1}
        condition_script["group"] = int(group_df.loc[group_df.index == idx]["code"])
    if "music" in condition_script:
        condition_script["music"] = str(condition_script["music"]).strip()
        idx = utils.find_last_index(music_df, "analyticsData", condition_script["music"])
        if idx == -1:
            print("conditionScript에 작성된 음악을 찾을 수 없습니다 : ", condition_script["music"])
            return {"error": -1}
        condition_script["music"] = int(music_df.loc[music_df.index == idx]["code"])
    if "theme" in condition_script:
        condition_script["theme"] = str(condition_script["theme"]).strip()
        idx = utils.find_first_index_target_contain(theme_df, "analyticsData", condition_script["theme"])
        if idx == -1:
            print("conditionScript에 작성된 테마를 찾을 수 없습니다 : ", condition_script["theme"])
            return {"error": -1}
        condition_script["theme"] = int(list(theme_df.loc[theme_df.index == idx]["code"])[0])
    if "artist" in condition_script:
        condition_script["artist"] = str(condition_script["artist"]).strip()
        idx = utils.find_last_index_targets_contain(artist_df, "analyticsData", condition_script["artist"])
        if idx == -1:
            print("conditionScript에 작성된 아티스트를 찾을 수 없습니다 : ", condition_script["artist"])
            return {"error": -1}
        condition_script["artist"] = int(list(artist_df.loc[artist_df.index == idx]["code"])[0])
    return condition_script


def make_df_mission_detail(mission_detail_df, event_input_dict):
    mission_detail_code = 1 + utils.find_last_value(mission_detail_df, "code")

    new_df = pd.DataFrame(columns=mission_detail_df.columns)
    new_df_idx = 0
    for mission_input_dict in event_input_dict["missionList"]:
        for mission_detail_dict in mission_input_dict["missionItemList"]:
            new_row = {"code": mission_detail_code}
            new_row = utils.insert_matching_data_to_row(mission_detail_df, new_row, mission_detail_dict)

            if "conditionScript" not in new_row or not new_row["conditionScript"]:
                new_row["conditionScript"] = ""

            new_row["conditionScript"] = str(new_row["conditionScript"]).replace("'", '"')

            new_df.loc[new_df_idx] = new_row
            mission_detail_dict["conditionCode"] = mission_detail_code

            new_df_idx += 1
            mission_detail_code += 1

    mission_detail_df = utils.insert_data_frame_to_base(mission_detail_df, new_df)
    return mission_detail_df


def make_df_extra_resource(extra_resource_df, item_dict):
    extra_resource_code = 1 + utils.find_last_value(extra_resource_df, "code")

    new_row = {"code": extra_resource_code, "url": item_dict["url"]}

    extra_resource_df = utils.insert_single_row_to_base(extra_resource_df, new_row)
    return extra_resource_code, extra_resource_df


def make_dict_mission_reward(
    mission_detail_dict,
    update_date,
    image_url,
    theme_url_name,
    extra_resource_df,
    locale_df,
    card_pack_df,
):
    if not isinstance(mission_detail_dict["itemName"], list):
        return mission_detail_dict, extra_resource_df, locale_df, card_pack_df

    item_name_kr = mission_detail_dict["itemName"][0]

    # 임시
    item_url_name = []
    item_url_name.append("_")
    item_url_name.append(mission_detail_dict["urlName"])
    item_url_name = "".join(item_url_name)

    # 매핑 데이터에 해당 아이템이 없는 경우
    # itemIcon
    # ExtraResource > url 만들기
    mission_detail_dict["url"] = utils.make_resource_url(
        image_url, update_date, "mission", "icon_mission_", theme_url_name, item_url_name
    )

    # itemIcon, itemName : 새로 생성하거나 이미 만들어진 코드 가져옴
    if item_name_kr not in generated_reward_list:
        item_info = {}
        extra_resource_code, extra_resource_df = make_df_extra_resource(extra_resource_df, mission_detail_dict)
        item_info["itemIcon"] = extra_resource_code
        item_info["itemName"], locale_df = utils.make_locale_simple_increment(
            locale_df, "itemName", mission_detail_dict
        )
        generated_reward_list[item_name_kr] = item_info

    mission_detail_dict["itemIcon"] = generated_reward_list[item_name_kr]["itemIcon"]
    mission_detail_dict["itemName"] = generated_reward_list[item_name_kr]["itemName"]

    item_name_kr = item_name_kr.replace("\n", " ")
    mission_detail_dict["item"] = utils.find_last_value(card_pack_df, "code", "nameKR", item_name_kr)
    if mission_detail_dict["item"] == -1:
        print("EventMissionData > Item : [ " + item_name_kr + " ] 에 해당하는 아이템을 CardPackData 에서 찾지 못하였습니다.")
        mission_detail_dict["item"] = item_name_kr

    return mission_detail_dict, extra_resource_df, locale_df, card_pack_df


def make_column_mission_uri(mission_detail_dict, new_row):
    num_of_value = 0

    if "uriParameters" in mission_detail_dict:
        new_row["uri"] = mission_detail_dict["uri"]
        uri_parameters = json.loads(mission_detail_dict["uriParameters"])
        for uri_parameter in uri_parameters:

            parameter_value = ""
            if uri_parameter in mission_detail_dict["conditionScript"]:
                parameter_value = str(mission_detail_dict["conditionScript"][uri_parameter])
            elif uri_parameter in mission_detail_dict:
                parameter_value = str(mission_detail_dict["menu"])

            if parameter_value:
                if num_of_value != 0:
                    new_row["uri"] += "&"
                else:
                    new_row["uri"] += "?"
                new_row["uri"] += uri_parameter + "=" + parameter_value
                num_of_value += 1

    return new_row


def make_df_event_mission(
    event_mission_df,
    input_dict,
    extra_resource_df,
    locale_df,
    card_pack_df,
):
    update_date = input_dict["updateDate"]
    image_url = input_dict["imageURL"]

    event_mission_code = 1 + utils.find_last_value(event_mission_df, "code")
    new_df = pd.DataFrame(columns=event_mission_df.columns)
    pre_mission_desc_locale_code = utils.find_last_value(event_mission_df, "missionDescLocale")
    pre_desc_locale_code = utils.find_last_value(event_mission_df, "descLocale", ignore_zero=True)

    new_df_idx = 0
    for event_input_dict in input_dict["eventList"]:
        theme_url_name = event_input_dict["theme"][1]

        for mission_group_dict in event_input_dict["missionList"]:
            for mission_detail_dict in mission_group_dict["missionItemList"]:
                new_row = {
                    "code": event_mission_code,
                    "eventCode": event_input_dict["eventCode"],
                    "groupCode": mission_group_dict["index"] + 1,
                    "orderIndex": mission_detail_dict["index"] + 1,
                }

                mission_detail_dict, extra_resource_df, locale_df, card_pack_df = make_dict_mission_reward(
                    mission_detail_dict,
                    update_date,
                    image_url,
                    theme_url_name,
                    extra_resource_df,
                    locale_df,
                    card_pack_df,
                )

                new_row = utils.insert_matching_data_to_row(event_mission_df, new_row, mission_detail_dict)

                if mission_detail_dict["index"] == 0:
                    new_row["tabTitleLocale"] = mission_group_dict["tabTitleLocale"]

                    mission_group_dict["previous_missionDescLocale"] = pre_mission_desc_locale_code
                    new_row["missionDescLocale"], locale_df = utils.make_locale_repeat(
                        locale_df, "missionDescLocale", mission_group_dict
                    )
                    pre_mission_desc_locale_code += 1

                    new_row["backgroundImage"] = utils.make_resource_url(
                        image_url,
                        update_date,
                        "mission",
                        "web_event_",
                        theme_url_name,
                        "_list" + str(mission_group_dict["index"] + 1),
                    )

                new_row["titleLocale"] = mission_detail_dict["titleLocale"]

                mission_detail_dict["previous_descLocale"] = pre_desc_locale_code
                new_row["descLocale"], locale_df = utils.make_locale_repeat(
                    locale_df, "descLocale", mission_detail_dict
                )
                pre_desc_locale_code += 1

                new_row = make_column_mission_uri(mission_detail_dict, new_row)

                new_df.loc[new_df_idx] = new_row
                event_mission_code += 1
                new_df_idx += 1

        new_row = {
            "code": event_mission_code,
            "eventCode": event_input_dict["eventCode"],
            "groupCode": event_input_dict["missionList"][-1]["index"] + 2,
            "orderIndex": 1,
            "tabTitleLocale": event_input_dict["final_tabTitleLocale"],
            "titleLocale": 0,
            "descLocale": 0,
            "conditionCode": 0,
            "value": 0,
            "itemName": 0,
            "itemIcon": 0,
            "item": 0,
            "rewardQuantity": 0,
        }

        new_df.loc[new_df_idx] = new_row
        event_mission_code += 1
        new_df_idx += 1

    event_mission_df = utils.insert_data_frame_to_base(event_mission_df, new_df)
    return event_mission_df, extra_resource_df, locale_df, card_pack_df
