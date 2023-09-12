import pandas as pd
import utils


class Music:
    def __init__(self) -> None:
        pass

    def set_planning_data(self, planning_dict):
        self.music_name = planning_dict["musicName"]
        self.pattern_count = list(map(int, planning_dict["patternCount"]))
        self.album_name = planning_dict["albumName"]
        self.track_num = planning_dict["trackNum"]
        self.music_type = planning_dict["musicType"]
        self.is_event = planning_dict["isEvent"]
        self.image_music = planning_dict["imageMusic"]
        self.difficulty = int(planning_dict["musicDifficulty"])
        self.my_recode = planning_dict["myRecode"]
        self.world_recode = planning_dict["worldRecode"]

    def set_album(self, album):
        self.album = album


class Album:
    def __init__(self, album_dict):
        self.album_name = album_dict["albumName"]
        self.release_date = album_dict["releaseDate"]
        self.album_bg_color = album_dict["albumBgColor"]
        self.album_font_color = album_dict["albumFontColor"]
        self.image_group = album_dict["imageGroup"]
        self.image_album = album_dict["imageAlbum"]
        self.locale_album = album_dict["localeAlbum"]
        self.album_version = str(album_dict["albumVersion"])


def make_dict_music(music: Music, album: Album, group, code):

    music_ogg = utils.Image.make_flow_image("music/", group.image_group, music.image_music, ".ogg")
    preview_ogg = utils.Image.make_flow_image("music/", group.image_group, music.image_music, "_preview.ogg")
    easy_seq = utils.Image.make_flow_image("music/", group.image_group, music.image_music, "_4.seq")
    normal_seq = utils.Image.make_flow_image("music/", group.image_group, music.image_music, "_7.seq")
    hard_seq = utils.Image.make_flow_image("music/", group.image_group, music.image_music, "_13.seq")

    album_image = utils.Image.make_fix_image("album", album.image_group, album.image_album, album.album_version)
    back_image = utils.Image.make_fix_image(
        "music_background_image",
        album.image_group,
        album.image_album,
        album.album_version,
    )

    music_dict = {
        "code": code,
        "isLocked": "FALSE",
        "isHidden": "FALSE",
        "challengable": "TRUE",
        "easyPatternCount": int(float(music.pattern_count[0])),
        "normalPatternCount": int(float(music.pattern_count[1])),
        "hardPatternCount": int(float(music.pattern_count[2])),
        "musicBattlePatternCount": 0,
        "myrecordQualifyingScore": music.my_recode,
        "worldrecordQualifyingScore": music.world_recode,
        "parentsGroupData": group.origin_group_id,
        "trackNumber": music.track_num,
        "releaseDate": album.release_date,
        "musicType": music.music_type,
        "cardRotation": group.card_rotation,
        "isMultiTempo": "FALSE",
        "artistCode": group.artist.origin_artist_id,
        "albumBgColor": album.album_bg_color,
        "albumFontColor": album.album_font_color,
        "oneStarMaxMiss": "100",
        "twoStarMaxMiss": "5",
        "threeStarMaxMiss": "0",
        "analyticsData": music.music_name,
        "isDalcomStage": "TRUE",
        "isMusicBattle": "FALSE",
        "sound": music_ogg,
        "previewSound": preview_ogg,
        "seqEasy": easy_seq,
        "seqNormal": normal_seq,
        "seqHard": hard_seq,
        "orderIndex": 0,
        "secondOrderIndex": music.difficulty,
        "image": back_image,
        "album": album_image,
        "albumName": album.locale_album,
    }
    if music.is_event == "TRUE":
        music_dict["localeDisplayGroupName"] = group.event_locale
        music_dict["groupData"] = group.group_id
    else:
        music_dict["localeDisplayGroupName"] = group.group_locale
        music_dict["groupData"] = group.origin_group_id

    return music_dict


def make_df_music(music_df, mapping_dict, locale_df, group_list, music_list):

    for music_item_idx in range(len(music_list) - 1, -1, -1):
        group_item = group_list[0]
        music_data = mapping_dict["musicData"]
        if music_data["appendType"] == 1:
            music_df_idx = utils.normal_append_find_idx(music_df, music_data["endCode"])
        elif music_data["appendType"] == 2:
            music_df_idx = utils.unnamed_find_idx(
                music_df, music_data["unnamed_idx"], group_item.origin_group_name
            )
        music_code = music_df.iloc[music_df_idx]["code"] + 1

        utils.add_order(music_df, "orderIndex", -1, 0)
        utils.add_order(music_df, "secondOrderIndex", music_list[music_item_idx].difficulty - 1, 0)
        dict_list = make_dict_music(
            music_list[music_item_idx],
            music_list[music_item_idx].album,
            group_item,
            music_code,
        )

        locale_code = music_df.loc[music_df_idx, "localeName"]
        locale_idx = locale_df.loc[locale_df["code"] == locale_code].index[0]

        locale_df, locale_code = utils.make_locale_df(
            locale_df, locale_idx, music_list[music_item_idx].music_name, music_list[music_item_idx].music_name
        )

        dict_list["localeName"] = locale_code

        new_df = pd.DataFrame(columns=music_df.columns)
        new_df.loc[0] = dict_list

        music_df = utils.insert_df(music_df, new_df, music_df_idx)

    return music_df, locale_df
