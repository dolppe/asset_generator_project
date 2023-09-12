import pandas as pd

import utils


class Theme:
    def __init__(self, theme_dict):
        self.emblem_position = theme_dict["emblemPosition"]

    def set_normal(self):
        self.select_rate = 1
        self.theme_percentage = 20
        self.theme_typeid = 0
        self.limited_type = 0
        self.percentage = 1
        self.select = False  # 그룹이전 신경써야함
        self.my_store = True

    def set_limited(self):
        self.select_rate = 0
        self.theme_percentage = 0
        self.limited_type = 1
        self.select_ticket = "2099-01-01 23:59:59"
        self.percentage = 0
        self.select = False  # 그룹이전 신경써야함
        self.my_store = True

    def set_event_limited(self):
        self.select_rate = 0
        self.theme_percentage = 0
        self.limited_type = 1
        self.select_ticket = "2099-01-01 23:59:59"
        self.percentage = 0
        self.select = False  # 그룹이전 신경써야함
        self.my_store = False

    def set_planning_data(self, planning_dict):
        self.theme_name = planning_dict["themeName"]
        self.theme_startat = planning_dict["groupStartAt"]
        self.theme_endat = planning_dict["groupEndAt"]
        self.theme_type = int(planning_dict["themeType"])
        self.image_theme = planning_dict["imageTheme"]
        self.cardbook_markcode = planning_dict["themeCardbookMark"]
        self.rehearsal = planning_dict["themeRehearsal"]

        if self.theme_type == 0:
            self.select_ticket = planning_dict["selectTicket"]
            self.select_start = planning_dict["groupStartAt"]
            self.set_normal()

        elif self.theme_type == 1:
            self.sell_startat = planning_dict["groupStartAt"]
            self.sell_endat = "2999-02-19 14:00:00"
            self.set_limited()

        elif self.theme_type == 2:
            self.sell_startat = planning_dict["groupStartAt"]
            self.sell_endat = "2999-02-19 14:00:00"
            self.set_event_limited()

    def set_theme_typeid(self, theme_typeid):
        self.theme_typeid = int(theme_typeid)

    def set_themeid(self, theme_id):
        self.theme_id = int(theme_id)

    def set_order_index(self, order_index):
        self.order_index = order_index


def make_row_theme(theme: Theme, group, theme_code):

    theme_image_s = utils.Image.make_flow_image("theme/theme_s_", theme.image_theme)
    theme_image_l = utils.Image.make_flow_image("theme/theme_l_", theme.image_theme)

    new_row = {
        "code": theme_code,
        "orderIndex": theme.order_index,
        "selectRate": theme.select_rate,
        "analyticsData": group.origin_group_name + "_" + theme.theme_name,
        "themeTypeCode": theme.theme_typeid,
        "themePercentage": theme.theme_percentage,
        "cardbookMarkCode": theme.cardbook_markcode,
        "limitedType": theme.limited_type,
        "rehearsalTheme": theme.rehearsal,
        "nameImageSmall": theme_image_s,
        "nameImageLarge": theme_image_l,
    }
    if theme.theme_type == 0:
        new_row["selectTicketStartAt"] = theme.select_ticket

    if theme.theme_type in (1, 2):
        new_row["selectTicketStartAt"] = theme.sell_endat

    theme.set_themeid(theme_code)

    return new_row


def make_row_theme_type(theme: Theme, theme_type_code):
    theme_c_card_image = utils.Image.make_flow_image("theme/limitednewframe_", theme.image_theme, "c")
    theme_b_card_image = utils.Image.make_flow_image("theme/limitednewframe_", theme.image_theme, "b")
    theme_a_card_image = utils.Image.make_flow_image("theme/limitednewframe_", theme.image_theme, "a")
    theme_s_card_image = utils.Image.make_flow_image("theme/limitednewframe_", theme.image_theme, "s")
    theme_r_card_image = utils.Image.make_flow_image("theme/limitednewframe_", theme.image_theme, "r")

    new_row = {
        "code": theme_type_code,
        "emblemPosition": theme.emblem_position,
        "gradeC": theme_c_card_image,
        "gradeB": theme_b_card_image,
        "gradeA": theme_a_card_image,
        "gradeS": theme_s_card_image,
        "gradeR": theme_r_card_image,
    }

    return new_row


def make_list_card(theme: Theme, group, card_code):

    new_list = []
    for card_idx in range(0, int(group.card_num)):

        card_image_s = utils.Image.make_flow_image("card/c_s_", theme.image_theme, group.artist.image_artist[card_idx])
        card_image_l = utils.Image.make_flow_image("card/c_l_", theme.image_theme, group.artist.image_artist[card_idx])

        new_row = {
            "code": card_code + card_idx,
            "groupID": group.group_id,
            "parentsGroupID": group.origin_group_id,
            "artistID": group.artist.artist_id[card_idx],
            "percentage": theme.percentage,
            "material": 0,
            "theme": theme.theme_id,
            "isSelect": theme.select,
            "myStoreAppear": theme.my_store,
            "intensifyPercentage": 0,
            "cardImageSmall": card_image_s,
            "cardImageLarge": card_image_l,
        }

        if theme.theme_type in (1, 2):
            new_row["sellStartAt"] = theme.sell_startat
            new_row["sellEndAt"] = theme.sell_endat

        elif theme.theme_type == 0:
            new_row["selectStartAt"] = theme.theme_start
        new_list.append(new_row)

    return new_list


def make_df_theme(theme_df, theme_type_df, mapping_dict, locale_df, group_list, theme_list):

    for group_idx, group_item in enumerate(group_list):
        theme_type_data = mapping_dict["themeTypeData"]
        if theme_type_data["appendType"] == 1:
            theme_type_idx = utils.normal_append_find_idx(theme_type_df, theme_type_data["endCode"])
        elif theme_type_data["appendType"] == 2:
            theme_type_idx = utils.unnamed_find_idx(
                theme_type_df, theme_type_data["unnamed_idx"], group_item.origin_group_name
            )
        theme_type_code = theme_type_df.iloc[theme_type_idx]["code"]

        theme_data = mapping_dict["themeData"]
        if theme_data["appendType"] == 1:
            theme_idx = utils.normal_append_find_idx(theme_df, theme_data["endCode"])
        elif theme_data["appendType"] == 2:
            theme_idx = utils.unnamed_find_idx(theme_df, theme_data["unnamed_idx"], group_item.origin_group_name)
        theme_code = theme_df.iloc[theme_idx]["code"] + 1

        theme_order = theme_df.iloc[theme_idx]["orderIndex"] + 1
        theme_list[group_idx].set_order_index(theme_order)

        if theme_list[group_idx].theme_type in (1, 2):
            theme_type_code = theme_type_code + 1
            theme_list[group_idx].set_theme_typeid(theme_type_code)
            themetype_temp = pd.DataFrame(columns=theme_type_df.columns)
            themetype_temp.loc[0] = make_row_theme_type(theme_list[group_idx], theme_type_code)
            theme_type_df = utils.insert_df(theme_type_df, themetype_temp, theme_type_idx)
            theme_type_idx = theme_type_idx + 1

        locale_code = theme_df.loc[theme_idx, "localeName"]
        locale_idx = locale_df.loc[locale_df["code"] == locale_code].index[0]

        locale_df, locale_code = utils.make_locale_df(
            locale_df, locale_idx, theme_list[group_idx].theme_name, theme_list[group_idx].theme_name
        )

        new_df = pd.DataFrame(columns=theme_df.columns)
        dict_list = make_row_theme(theme_list[group_idx], group_item, theme_code)
        dict_list["localeName"] = locale_code

        new_df.loc[0] = dict_list

        theme_df = utils.insert_df(theme_df, new_df, theme_idx)

    return theme_df, theme_type_df, locale_df


def make_df_card(card_df, group_list, theme_list, mapping_dict):
    for group_idx, group_item in enumerate(group_list):
        card_data = mapping_dict["cardData"]
        if card_data["appendType"] == 1:
            card_idx = utils.normal_append_find_idx(card_df, card_data["endCode"])
        elif card_data["appendType"] == 2:
            card_idx = utils.unnamed_find_idx(card_df, card_data["unnamed_idx"], group_item.origin_group_name)
        card_code = card_df.iloc[card_idx]["code"] + 1

        new_df = pd.DataFrame(columns=card_df.columns)
        dict_list = make_list_card(theme_list[group_idx], group_item, card_code)

        for group_idx, dict_item in enumerate(dict_list):
            new_df.loc[group_idx] = dict_item

        card_df = utils.insert_df(card_df, new_df, card_idx)

    return card_df
