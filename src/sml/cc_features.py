# +
import pandas as pd
import numpy as np
from math import radians

def card_owner_age(trans_df : pd.DataFrame, profiles_df : pd.DataFrame)-> pd.DataFrame:
    age_df = trans_df.merge(profiles_df, on="cc_num", how="left")
    trans_df["age_at_transaction"] = (age_df["datetime"] - age_df["birthdate"]) / np.timedelta64(1, "Y")
    return trans_df

def expiry_days(trans_df : pd.DataFrame, credit_cards_df : pd.DataFrame)-> pd.DataFrame:
    card_expiry_df = trans_df.merge(credit_cards_df, on="cc_num", how="left")
    card_expiry_df["expires"] = pd.to_datetime(card_expiry_df["expires"], format="%m/%y")
    trans_df["days_until_card_expires"] = (card_expiry_df["expires"] - card_expiry_df["datetime"]) / np.timedelta64(1, "D")
    return trans_df
    
def haversine(long, lat):
    """Compute Haversine distance between each consecutive coordinate in (long, lat)."""

    long_shifted = long.shift()
    lat_shifted = lat.shift()
    long_diff = long_shifted - long
    lat_diff = lat_shifted - lat

    a = np.sin(lat_diff/2.0)**2
    b = np.cos(lat) * np.cos(lat_shifted) * np.sin(long_diff/2.0)**2
    c = 2*np.arcsin(np.sqrt(a + b))

    return c


def distance_between_consectutive_transactions(trans_df : pd.DataFrame)-> pd.DataFrame:

    trans_df.sort_values("datetime", inplace=True)
    trans_df[["longitude", "latitude"]] = trans_df[["longitude", "latitude"]].applymap(radians)

    trans_df["loc_delta"] = trans_df.groupby("cc_num")\
        .apply(lambda x : haversine(x["longitude"], x["latitude"]))\
        .reset_index(level=0, drop=True)\
        .fillna(0)
    return trans_df


def activity_level(trans_df : pd.DataFrame, window_len)-> pd.DataFrame:
    
    cc_group = trans_df[["cc_num", "amount", "datetime"]].groupby("cc_num").rolling(window_len, on="datetime")

    # Moving average of transaction volume.
    df_4h_mavg = pd.DataFrame(cc_group.mean())
    df_4h_mavg.columns = ["trans_volume_mavg", "datetime"]
    df_4h_mavg = df_4h_mavg.reset_index(level=["cc_num"])
    df_4h_mavg = df_4h_mavg.drop(columns=["cc_num", "datetime"])
    df_4h_mavg = df_4h_mavg.sort_index()

    # Moving standard deviation of transaction volume.
    df_4h_std = pd.DataFrame(cc_group.mean())
    df_4h_std.columns = ["trans_volume_mstd", "datetime"]
    df_4h_std = df_4h_std.reset_index(level=["cc_num"])
    df_4h_std = df_4h_std.drop(columns=["cc_num", "datetime"])
    df_4h_std = df_4h_std.fillna(0)
    df_4h_std = df_4h_std.sort_index()
    window_aggs_df = df_4h_std.merge(df_4h_mavg,left_index=True, right_index=True)

    # Moving average of transaction frequency.
    df_4h_count = pd.DataFrame(cc_group.mean())
    df_4h_count.columns = ["trans_freq", "datetime"]
    df_4h_count = df_4h_count.reset_index(level=["cc_num"])
    df_4h_count = df_4h_count.drop(columns=["cc_num", "datetime"])
    df_4h_count = df_4h_count.sort_index()
    window_aggs_df = window_aggs_df.merge(df_4h_count,left_index=True, right_index=True)

    # Moving average of location difference between consecutive transactions.
    cc_group = trans_df[["cc_num", "loc_delta", "datetime"]].groupby("cc_num").rolling(window_len, on="datetime").mean()
    df_4h_loc_delta_mavg = pd.DataFrame(cc_group)
    df_4h_loc_delta_mavg.columns = ["loc_delta_mavg", "datetime"]
    df_4h_loc_delta_mavg = df_4h_loc_delta_mavg.reset_index(level=["cc_num"])
    df_4h_loc_delta_mavg = df_4h_loc_delta_mavg.drop(columns=["cc_num", "datetime"])
    df_4h_loc_delta_mavg = df_4h_loc_delta_mavg.sort_index()
    window_aggs_df = window_aggs_df.merge(df_4h_loc_delta_mavg,left_index=True, right_index=True)

    window_aggs_df = window_aggs_df.merge(trans_df[["cc_num", "datetime"]].sort_index(),left_index=True, right_index=True)
    return window_aggs_df


def convert_datetime(trans_df : pd.DataFrame, window_aggs_df : pd.DataFrame)-> pd.DataFrame:
    trans_df.datetime = trans_df.datetime.values.astype(np.int64) // 10 ** 6
    window_aggs_df.datetime = window_aggs_df.datetime.values.astype(np.int64) // 10 ** 6
    return window_aggs_df
    
    
