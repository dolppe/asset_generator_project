import pandas as pd
import utils


class Group:
    def __init__(self, group_dict):
        self.origin_group_id = int(group_dict["originGroupID"])
        self.origin_group_name = group_dict["originGroupName"]
        self.card_num = int(group_dict["cardNum"])
        self.card_rotation = int(group_dict["cardRotation"])
        self.group_type = int(group_dict["groupType"])
        self.artist = Artist(group_dict, self.group_type)
        self.event_locale = group_dict["eventLocale"]
        self.is_event = "FALSE"
        self.group_locale = group_dict["groupLocale"]
        self.profile_locale = group_dict["profileGroupLocale"]
        self.card_book_locale = group_dict["cardLocale"]
        self.image_group = group_dict["imageGroup"]
        self.group_version = str(group_dict["groupVersion"])

    def set_planning_data(self, planning_dict):
        self.is_event = planning_dict["isEvent"]
        if self.is_event == "TRUE":
            self.group_name = planning_dict["groupName"] + " (EVENT)"
        else:
            self.group_name = planning_dict["groupName"]
            self.group_id = self.origin_group_id
            self.artist.set_artistid(self.artist.artist_id)
        self.group_startat = planning_dict["groupStartAt"]
        self.group_endat = planning_dict["groupEndAt"]
        self.is_profile = planning_dict["isProfile"]

        if self.is_profile == "TRUE":
            self.profile = Profile()
            self.profile.set_profile_name(planning_dict["profileName"])

    def set_order(self, order_index, second_order_index):
        self.order_index = order_index
        self.second_order_index = second_order_index

    def set_groupid(self, group_id):
        self.group_id = int(group_id)

    def find_idx(self, group_df):
        next_row = group_df[group_df["code"] == int(self.origin_group_id) + 1000]
        if next_row.empty:
            idx = group_df.index[-1]
        else:
            idx = group_df[group_df["code"] == int(self.origin_group_id) + 1000].index[0] - 1
        return idx


class Artist:
    def __init__(self, artist_dict, group_type):

        self.origin_artist_id = list(map(int, artist_dict["originArtistID"]))
        self.artist_name = artist_dict["artistName"]
        self.locale_name = artist_dict["localeName"]
        self.locale_birthday = artist_dict["birthday"]
        self.bonus_birthday = artist_dict["bonusBirthday"]
        self.debut = artist_dict["debut"]
        self.debut_album = artist_dict["debutAlbum"]
        if group_type == 0:
            self.position = artist_dict["position"]
        self.image_artist = artist_dict["imageArtist"]

    def set_artistid(self, artist_id):
        self.artist_id = list(map(int, artist_id))


class Profile:
    def __init__(self) -> None:
        pass

    def set_profile_name(self, profile_name):
        self.profile_name_kr = profile_name[0]
        self.profile_name_en = profile_name[1]

    def set_event_code(self, event_code):
        self.event_code = int(event_code)

    def set_profile_code(self, profile_code):
        self.profile_code = list(map(int, profile_code))

    def set_order_index(self, order_index):
        self.order_index = int(order_index)


def make_dict_group(group: Group, code):

    emblem_image = utils.Image.make_fix_image("emblem", group.image_group, group.image_group, group.group_version)
    cardbook_image = utils.Image.make_fix_image("card_book", group.image_group, group.image_group, group.group_version)

    group_dict = {
        "code": code,
        "equipableSlot": group.card_num,
        "groupType": group.group_type,
        "emblemImage": emblem_image,
        "bestCardbookImage": cardbook_image,
    }

    group_dict["localeName"] = group.event_locale
    group_dict["profileGroupName"] = group.profile_locale
    group_dict["cardLocaleName"] = group.card_book_locale
    group_dict["displayStartAt"] = group.group_startat
    group_dict["displayEndAt"] = group.group_endat
    group_dict["analyticsData"] = group.group_name
    group_dict["orderIndex"] = group.order_index
    group_dict["secondOrderIndex"] = group.second_order_index

    group.set_groupid(code)
    return group_dict


def make_list_profile(group: Group, theme, code):

    profile_list = []
    profile_code_list = []
    for profile_idx in range(0, int(group.card_num)):
        profile_image = utils.Image.make_flow_image(
            "card/p_", theme.image_theme, group.artist.image_artist[profile_idx]
        )

        profile_dict = {
            "code": code + profile_idx,
            "groupID": group.origin_group_id,
            "artistID": group.artist.origin_artist_id[profile_idx],
            "orderIndex": group.profile.order_index,
            "eventType": group.profile.event_code,
            "profileType": 1,
            "purchase": 0,
            "price": 0,
            "analyticsData": group.origin_group_name + "_" + group.artist.artist_name[profile_idx],
            "profileImage": profile_image,
        }

        profile_code_list.append(code + profile_idx)
        profile_list.append(profile_dict)
    group.profile.set_profile_code(profile_code_list)
    return profile_list


def make_dict_card_pack_profile(group: Group, code):
    card_pack_dict = {
        "code": code,
        "name": group.profile.profile_name_kr,
        "category": 27,
        "groupLimited": "FALSE",
        "selectedCode": group.profile.profile_code,
        "nameKR": group.profile.profile_name_kr,
        "nameEN": group.profile.profile_name_en,
        "rateDisplay": "FALSE",
    }
    return card_pack_dict


def make_dict_card_pack_yaer_profile(name_locale, code):
    card_pack_year_dict = {"code": code, "category": 27, "name": name_locale}
    return card_pack_year_dict


def make_list_artist(group: Group, theme, code):

    artist_list = []
    artist_id_list = []
    for artist_idx in range(0, int(group.card_num)):
        name_image = utils.Image.make_fix_image(
            "artistname", group.image_group, group.artist.image_artist[artist_idx], group.group_version
        )
        profile_image = utils.Image.make_fix_image(
            "profile", group.image_group, group.artist.image_artist[artist_idx], group.group_version
        )

        empty_image_s = utils.Image.make_flow_image(
            "card/c_s_", theme.image_theme, group.artist.image_artist[artist_idx] + "_em"
        )
        empty_image_l = utils.Image.make_flow_image(
            "card/c_l_", theme.image_theme, group.artist.image_artist[artist_idx] + "_em"
        )

        artist_dict = {
            "code": code + artist_idx,
            "localeName": group.artist.locale_name[artist_idx],
            "birthday": group.artist.locale_birthday[artist_idx],
            "bonusBirthday": group.artist.bonus_birthday[artist_idx],
            "bonusBirthdayUse": "TRUE",
            "debut": group.artist.debut[artist_idx],
            "debutAlbum": group.artist.debut_album[artist_idx],
            "orderIndex": artist_idx,
            "group": group.group_id,
            "isProfileImage": "FALSE",
            "analyticsData": group.group_name + "_" + group.artist.artist_name[artist_idx],
            "mapping": group.group_name + "_" + group.artist.artist_name[artist_idx],
            "nameImage": name_image,
            "profileImage": profile_image,
            "emptyImageSmall": empty_image_s,
            "emptyImageLarge": empty_image_l,
        }

        artist_id_list.append(code + artist_idx)

        if group.group_type == 0:
            artist_dict["position"] = artist_idx  # 보완필요

        artist_list.append(artist_dict)

    group.artist.set_artistid(artist_id_list)
    return artist_list


def make_df_group(group_df, group_list, mapping_dict):

    for group_item in group_list:
        # 들어갈 index 찾음
        if group_item.is_event == "FALSE":
            break
        group_data = mapping_dict["groupData"]
        if group_data["appendType"] == 1:
            group_idx = utils.normal_append_find_idx(group_df, group_data["endCode"])
        elif group_data["appendType"] == 2:
            group_idx = utils.unnamed_find_idx(group_df, group_data["unnamed_idx"], group_item.group_name)

        group_code = group_df.iloc[group_idx]["code"] + 1

        origin_group_idx = group_df.loc[group_df["code"] == group_item.origin_group_id].index[0]
        origin_group_order = group_df.loc[origin_group_idx, "orderIndex"]
        origin_group_second_order = group_df.loc[origin_group_idx, "secondOrderIndex"]
        group_df = utils.add_order(group_df, "orderIndex", origin_group_order, 1)
        group_df = utils.add_order(group_df, "secondOrderIndex", origin_group_second_order, 1)

        group_item.set_order(origin_group_order + 1, origin_group_second_order + 1)
        # group_code 설정
        group_item.set_groupid(group_code)

        # 입력 데이터 기반으로 dataFrame 생성
        new_df = pd.DataFrame(columns=group_df.columns)

        new_df.loc[0] = make_dict_group(group_item, group_code)

        # df 삽입
        group_df = utils.insert_df(group_df, new_df, group_idx)
    return group_df


def make_df_profile(
    profile_df,
    card_pack_df,
    card_pack_year_df,
    locale_df,
    mapping_dict,
    group_list,
    theme_list,
):
    cardpack_data = mapping_dict["cardpackProfile"]
    cardpack_idx = utils.normal_append_find_idx(card_pack_df, cardpack_data["endCode"])
    event_idx = cardpack_idx
    event_code = card_pack_df.iloc[event_idx]["code"]

    for group_idx, group_item in enumerate(group_list):
        if group_item.is_profile == "False":
            continue
        profile_data = mapping_dict["profileData"]
        if profile_data["appendType"] == 1:
            profile_idx = utils.normal_append_find_idx(profile_df, profile_data["endCode"])
        elif profile_data["appendType"] == 2:
            profile_idx = utils.unnamed_find_idx(profile_df, profile_data["unnamed_idx"], group_item.origin_group_name)
        if group_item.group_type == 0:
            profile_order = profile_df.iloc[profile_idx]["orderIndex"] + 1000
        else:
            profile_order = profile_df.iloc[profile_idx]["orderIndex"] + 1
        profile_code = profile_df.iloc[profile_idx]["code"] + 1
        group_item.profile.set_order_index(profile_order)
        event_code = event_code + 1
        group_item.profile.set_event_code(event_code)

        new_df = pd.DataFrame(columns=profile_df.columns)
        dict_list = make_list_profile(group_item, theme_list[group_idx], profile_code)

        for dict_idx, dict_item in enumerate(dict_list):
            new_df.loc[dict_idx] = dict_item

        profile_df = utils.insert_df(profile_df, new_df, profile_idx)

        card_pack_temp = pd.DataFrame(columns=card_pack_df.columns)
        card_pack_dic = make_dict_card_pack_profile(group_item, event_code)
        card_pack_temp.loc[0] = card_pack_dic

        theme_name = theme_list[group_idx].theme_name
        card_pack_year_idx = card_pack_year_df.loc[card_pack_year_df["code"] == (event_code - 1)].index[0]
        locale_code = card_pack_year_df.loc[card_pack_year_idx, "name"]
        locale_idx = locale_df.loc[locale_df["code"] == locale_code].index[0]
        locale_df, locale_code = utils.make_locale_df(
            locale_df, locale_idx, theme_name + " 프로필 패키지 상품", theme_name + " Profile Package Offer"
        )

        card_pack_yaer_make_df_idx = card_pack_year_idx
        card_pack_year_temp = pd.DataFrame(columns=card_pack_year_df.columns)
        card_pack_year_dic = make_dict_card_pack_yaer_profile(locale_code, event_code)
        card_pack_year_temp.loc[0] = card_pack_year_dic
        card_pack_year_df = utils.insert_df(card_pack_year_df, card_pack_year_temp, card_pack_yaer_make_df_idx)

        card_pack_df = utils.insert_df(card_pack_df, card_pack_temp, event_idx)
        event_idx = event_idx + 1

    return profile_df, card_pack_df, card_pack_year_df, locale_df


def make_df_artist(artist_df, group_list, theme_list, mapping_dict):

    for group_idx, group_item in enumerate(group_list):
        artist_data = mapping_dict["artistData"]
        if artist_data["appendType"] == 1:
            artist_idx = utils.normal_append_find_idx(artist_df, artist_data["endCode"])
        elif artist_data["appendType"] == 2:
            artist_idx = utils.unnamed_find_idx(artist_df, artist_data["unnamed_idx"], group_item.group_name)
        artist_code = artist_df.iloc[artist_idx]["code"] + 1
        
        new_df = pd.DataFrame(columns=artist_df.columns)
        dict_list = make_list_artist(group_item, theme_list[group_idx], artist_code)

        for group_idx, dict_item in enumerate(dict_list):
            new_df.loc[group_idx] = dict_item

        artist_df = utils.insert_df(artist_df, new_df, artist_idx)

    return artist_df
