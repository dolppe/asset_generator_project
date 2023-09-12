import sys
import json
import re
import warnings
import pandas as pd
import utils

from preprocess import group_transfer
from preprocess import input_combine
from preprocess import arrange
from generate import group
from generate import theme
from generate import music
from generate import store
from generate import packaging
from generate import item
from generate import background
from generate import mission

# 임시 WARNING 출력 무시
warnings.filterwarnings(action="ignore")

# 입력

print("Setting input data ...")
if len(sys.argv) == 1:
    INPUT_PATH = "resources/input"
    BASE_DATA_PATH = INPUT_PATH + "/base/SSY_Live_3.7.26_230209.xlsx"
    PLANNING_DATA_PATH = INPUT_PATH + "/planning_0216.xlsx"
    MAPPING_DATA_PATH = INPUT_PATH + "/mapping_test.xlsx"
    OUTPUT_DATA_PATH = "output/output.xlsx"
else:
    if len(sys.argv) != 5:
        print("실행 인자의 개수가 다릅니다.")
        sys.exit()
    BASE_DATA_PATH = sys.argv[1]
    PLANNING_DATA_PATH = sys.argv[2]
    MAPPING_DATA_PATH = sys.argv[3]
    OUTPUT_DATA_PATH = sys.argv[4]

base_data_df = pd.read_excel(BASE_DATA_PATH, sheet_name=None)

print("Previous asset file : " + BASE_DATA_PATH)
print("Planning : " + PLANNING_DATA_PATH)
print("Mapping : " + MAPPING_DATA_PATH)
print("===============================")

# 입력 데이터 전처리

print("Seperating sheets ...")

locale_df = base_data_df["LocaleData"]
lobby_bg_df = base_data_df["LobbyBgData"]
card_pack_df = base_data_df["CardPackData"]
lobby_bg_store_df = base_data_df["LobbyBgStoreData"]
event_management_df = base_data_df["EventManagementData"]
mission_detail_df = base_data_df["MissionDetailData"]
extra_resource_df = base_data_df["ExtraResourceData"]
event_mission_df = base_data_df["EventMissionData"]
point_reward_df = base_data_df["PointRewardData"]
store_menu_df = base_data_df["StoreMenuData"]
store_home_df = base_data_df["StoreHomeData"]
recommend_store_df = base_data_df["RecommendStoreData"]
popup_store_df = base_data_df["PopupStoreData"]
group_df = base_data_df["GroupData"]
profile_df = base_data_df["ProfileData"]
card_pack_year_df = base_data_df["CardPackYearData"]
artist_df = base_data_df["ArtistData"]
theme_df = base_data_df["ThemeData"]
theme_type_df = base_data_df["ThemeTypeData"]
card_df = base_data_df["CardData"]
music_df = base_data_df["MusicData"]

print("Preprocessing input data ...")
planning_df = pd.read_excel(PLANNING_DATA_PATH)
mapping_df = pd.read_excel(MAPPING_DATA_PATH)

planning_dict = json.loads(utils.convert_to_json(planning_df))
mapping_dict = json.loads(utils.convert_to_json(mapping_df))

card_df = input_combine.column_bool_convert(card_df, "myStoreAppear")

# 그룹 제작 시작

utils.Image.set_mapping_data(mapping_dict)
utils.Image.set_planning_data(planning_dict)
group_list, theme_list, music_list = input_combine.artist_set_list(mapping_dict, planning_dict)
group_transfer.group_transfer(mapping_dict, planning_dict, group_df, profile_df, card_df, music_df)
print("===============================")

# 그룹 제작 시작

print("Making GroupData ...")
group_df = group.make_df_group(group_df, group_list, mapping_dict)
print("Making ThemeData ...")
theme_df, theme_type_df, locale_df = theme.make_df_theme(
    theme_df, theme_type_df, mapping_dict, locale_df, group_list, theme_list
)
print("Making ProfileData ...")
profile_df, card_pack_df, card_pack_year_df, locale_df = group.make_df_profile(
    profile_df,
    card_pack_df,
    card_pack_year_df,
    locale_df,
    mapping_dict,
    group_list,
    theme_list,
)
print("Making ArtistData ...")
artist_df = group.make_df_artist(artist_df, group_list, theme_list, mapping_dict)
print("Making CardData ...")
card_df = theme.make_df_card(card_df, group_list, theme_list, mapping_dict)
print("Making MusicData ...")
music_df, locale_df = music.make_df_music(music_df, mapping_dict, locale_df, group_list, music_list)

# 상점 제작 시작

image_url = mapping_dict["imageURL"]
update_date = planning_dict["updateDate"]

menu_list = planning_dict["menuList"]
point_list = planning_dict["pointList"]
home_list = planning_dict["homeList"]
popup_list = planning_dict["popupList"]
recommend_list = planning_dict["itemList"]
card_pack_list = planning_dict["cardList"]

print("Making LocaleData ...")
locale_df, point_locale_dict = utils.point_locale(locale_df, point_list, mapping_dict)
locale_df, menu_locale_dict = utils.menu_locale(locale_df, menu_list, update_date, mapping_dict)
locale_df, recommend_locale_dict = utils.recommend_locale(locale_df, recommend_list, mapping_dict)
locale_df, popup_locale_dict = utils.popup_locale(locale_df, popup_list, mapping_dict)

print("Making CardPackData ...")
card_pack_df = item.make_df_point_card_pack(card_pack_df, theme_df, point_list, mapping_dict)
card_pack_df = item.make_df_card_pack(
    card_pack_df, theme_df, card_df, planning_dict["groupList"], card_pack_list, mapping_dict
)
point_reward_df = item.make_df_point(point_reward_df, card_pack_df, point_list, point_locale_dict)

store_menu_df, menu_list = store.make_df_store_menu(
    store_menu_df, point_reward_df, menu_list, menu_locale_dict, image_url, update_date
)

print("Making PopupStoreData ...")
popup_store_df = packaging.make_df_popup_store(popup_store_df, popup_list, popup_locale_dict, image_url, update_date)

print("Making StoreHomeData ...")
store_home_df = store.make_df_store_home(store_home_df, store_menu_df, home_list, image_url, update_date)
print("Making RecommendStoreData ...")
recommend_store_df = packaging.make_df_recommend_store(
    recommend_store_df,
    store_menu_df,
    point_reward_df,
    card_pack_df,
    mapping_dict,
    recommend_list,
    recommend_locale_dict,
    update_date,
    image_url,
    planning_dict["groupList"],
)


# 미션 및 배경 제작 시작

print("Making LobbyBgData ...")
input_dict = input_combine.set_basic(mapping_dict, planning_dict)
input_dict["bgList"] = input_combine.set_list(mapping_dict["bg"], planning_dict["bgList"])
input_dict["eventList"] = input_combine.mission_set_list(mapping_dict, planning_dict["eventList"])
event_management_df = arrange.event_management_arrange(
    event_management_df, input_dict["updateDate"], len(input_dict["bgList"])
)

for bg_dict in input_dict["bgList"]:
    for g in group_list:
        if bg_dict["group"][0] == g.origin_group_name:
            bg_dict["groupID"] = g.origin_group_id
            break
    if "groupID" not in bg_dict:
        print("배경에 해당하는 그룹이 없습니다.")
        exit()

for event_dict in input_dict["eventList"]:
    for g in group_list:
        if event_dict["group"][0] == g.origin_group_name:
            event_dict["eventGroupCode"] = g.origin_group_id
            break
    if "eventGroupCode" not in event_dict:
        print("미션 이벤트에 해당하는 그룹이 없습니다.")
        exit()

    for mission_group_dict in event_dict["missionList"]:
        for mission_detail_dict in mission_group_dict["missionItemList"]:
            if "conditionScript" in mission_detail_dict:
                mission_detail_dict["conditionScript"] = mission.make_dict_condition_script(
                    mission_detail_dict["conditionScript"], group_df, music_df, theme_df, artist_df
                )
                if "error" in mission_detail_dict["conditionScript"]:
                    exit()
            if "menu" in mission_detail_dict:
                if mission_detail_dict["menu"] == "상점 홈":
                    mission_detail_dict["menu"] = 0
                else:
                    for menu in input_dict["menuList"]:
                        if menu["name"][0] == mission_detail_dict["menu"]:
                            mission_detail_dict["menu"] = menu["newcode"]

lobby_bg_df, locale_df = background.make_df_lobby_bg(lobby_bg_df, input_dict, locale_df)
print("Making CardPackData for background ...")
card_pack_df = background.make_df_card_pack(card_pack_df, input_dict)
print("Making LobbyBgStoreData ...")
lobby_bg_store_df, locale_df = background.make_lobby_bg_store_df(lobby_bg_store_df, input_dict, locale_df)

print("Making EventManagementData ...")
event_management_df, lobby_bg_store_df, locale_df = mission.make_df_event_management(
    event_management_df,
    input_dict,
    lobby_bg_store_df,
    locale_df,
)
print("Making EventDetailData ...")
for event_input_dict in input_dict["eventList"]:
    mission_detail_df = mission.make_df_mission_detail(mission_detail_df, event_input_dict)

print("Making EventMissionData ...")
event_mission_df, extra_resource_df, locale_df, card_pack_df = mission.make_df_event_mission(
    event_mission_df, input_dict, extra_resource_df, locale_df, card_pack_df
)

# 제작된 시트 저장

print("Combining all sheets ...")
base_data_df["LocaleData"] = locale_df
base_data_df["LobbyBgData"] = lobby_bg_df
base_data_df["CardPackData"] = card_pack_df
base_data_df["LobbyBgStoreData"] = lobby_bg_store_df
base_data_df["EventManagementData"] = event_management_df
base_data_df["MissionDetailData"] = mission_detail_df
base_data_df["ExtraResourceData"] = extra_resource_df
base_data_df["EventMissionData"] = event_mission_df
base_data_df["PointRewardData"] = point_reward_df
base_data_df["StoreMenuData"] = store_menu_df
base_data_df["StoreHomeData"] = store_home_df
base_data_df["RecommendStoreData"] = recommend_store_df
base_data_df["PopupStoreData"] = popup_store_df
base_data_df["GroupData"] = group_df
base_data_df["ProfileData"] = profile_df
base_data_df["CardPackYearData"] = card_pack_year_df
base_data_df["ArtistData"] = artist_df
base_data_df["ThemeData"] = theme_df
base_data_df["ThemeTypeData"] = theme_type_df
base_data_df["CardData"] = card_df
base_data_df["MusicData"] = music_df

print("Make success!")
print("===============================")

print("Preparing writer ...")

writer = pd.ExcelWriter(OUTPUT_DATA_PATH, engine="openpyxl")

print("Saving all sheets ...")
for key, df in base_data_df.items():
    df = df.rename(columns=lambda x: re.sub("^Unnamed: [0-9]*", "", x))
    if key == "CommonData":
        df.rename(columns={"code.1": "code"}, inplace=True)
    df.to_excel(writer, sheet_name=key, index=False)

writer.save()
print("All process done!")
print("Output file : " + OUTPUT_DATA_PATH)
