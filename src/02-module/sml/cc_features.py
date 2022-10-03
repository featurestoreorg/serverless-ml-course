import pandas as pd
import numpy as np

from datetime import datetime, date
from math import radians

# +
def card_owner_age(trans_df : pd.DataFrame, profiles_df : pd.DataFrame)-> pd.DataFrame:
    """Used only in feature pipelines (not online inference). 
       Unit test with DataFrames and sample data.
    """
    age_df = trans_df.merge(profiles_df, on="cc_num", how="left")
    trans_df["age_at_transaction"] = (age_df["datetime"] - age_df["birthdate"]) / np.timedelta64(1, "Y")
    return trans_df

def expiry_days(trans_df : pd.DataFrame, credit_cards_df : pd.DataFrame)-> pd.DataFrame:
    """Used only in feature pipelines (not online inference). 
       Unit test with DataFrames and sample data.
    """
    card_expiry_df = trans_df.merge(credit_cards_df, on="cc_num", how="left")
    card_expiry_df["expires"] = pd.to_datetime(card_expiry_df["expires"], format="%m/%y")
    trans_df["days_until_card_expires"] = (card_expiry_df["expires"] - card_expiry_df["datetime"]) / np.timedelta64(1, "D")
    return trans_df


# -

def haversine_distance(long: float, lat: float, prev_long: float, prev_lat: float)-> float:
    """Compute Haversine distance between each consecutive coordinate in (long, lat)."""

    if isinstance(long, pd.Series):
        long = long.map(lambda x: (x))
    else:
        long = radians(long)
    
    if isinstance(lat, pd.Series):
        lat = lat.map(lambda x: (x))
    else:
        lat = radians(lat)

    if isinstance(long, pd.Series):
        prev_long = prev_long.map(lambda x: (x))
    else:
        prev_long = radians(prev_long)

    if isinstance(lat, pd.Series):
        prev_lat = prev_lat.map(lambda x: (x))
    else:
        prev_lat = radians(prev_lat)

    long_diff = prev_long - long
    lat_diff = prev_lat - lat

    a = np.sin(lat_diff/2.0)**2
    b = np.cos(lat) * np.cos(prev_lat) * np.sin(long_diff/2.0)**2
    c = 2*np.arcsin(np.sqrt(a + b))

    return c


def time_delta(prev_datetime: int, current_datetime: int)-> int:
    """Compute time difference between each consecutive transaction."""        
    return prev_datetime - current_datetime

def time_delta_to_days(time_delta: datetime)-> float:
    """."""    
    return time_delta.total_seconds() / 86400

def date_to_timestamp(date_obj: datetime)-> int:
    return int(date_obj.timestamp() * 1000)

def timestamp_to_date(timestamp: int)-> datetime:
    return datetime.fromtimestamp(timestamp // 1000)

def activity_level(trans_df : pd.DataFrame, lag: int)-> pd.DataFrame:
    
    # Convert coordinates into radians:
    trans_df[["longitude", "latitude"]] = trans_df[["longitude", "latitude"]].applymap(radians)
    
    trans_df.sort_values(["datetime", "cc_num"], inplace=True) 

    # When we call `haversine_distance`, we want to pass as params, the long/lat of the current row, and the long/lat of the most
    # recent prior purchase. By grouping the DF by cc_num, apart from the first transaction (which will be NaN and we fill that with 0 at the end),
    # we can access the previous lat/long using Panda's `shift` operation, which gives you the previous row (long/lang).
    trans_df[f"loc_delta_t_minus_{lag}"] = trans_df.groupby("cc_num")\
        .apply(lambda x :haversine_distance(x["longitude"], x["latitude"], x["longitude"].shift(-lag), x["latitude"].shift(-lag)))\
        .reset_index(level=0, drop=True)\
        .fillna(0)

    # Use the same `shift` operation in Pandas to get the previous row for a given cc_number
    trans_df[f"time_delta_t_minus_{lag}"] = trans_df.groupby("cc_num")\
        .apply(lambda x : time_delta(x["datetime"].shift(-lag), x["datetime"]))\
        .reset_index(level=0, drop=True)
#        .fillna(0) # handle the first datetime, which has no previous row when you call `shift`

    # Convert time_delta from seconds to days
    trans_df[f"time_delta_t_minus_{lag}"] = trans_df[f"time_delta_t_minus_{lag}"].map(lambda x: time_delta_to_days(x))
    trans_df[f"time_delta_t_minus_{lag}"] = trans_df[f"time_delta_t_minus_{lag}"].fillna(0)    
    trans_df = trans_df[["tid","datetime","cc_num","category", "amount", "city", "country", "age_at_transaction"\
                         ,"days_until_card_expires", f"loc_delta_t_minus_{lag}", f"time_delta_t_minus_{lag}"]]
    # Convert datetime to timestamp, because of a problem with UTC. Hopsworks assumes you use UTC, but if you don't use UTC
    # on your Python environment, the datetime will be wrong. With timestamps, we don't have the UTC problems when performing PIT Joins.
    trans_df.datetime = trans_df.datetime.map(lambda x: date_to_timestamp(x))
    return trans_df


def aggregate_activity_by_hour(trans_df : pd.DataFrame, window_len)-> pd.DataFrame:
    
    cc_group = trans_df[["cc_num", "amount", "datetime"]].groupby("cc_num").rolling(window_len, on="datetime")

    # Moving average of transaction volume.
    df_mavg = pd.DataFrame(cc_group.mean())
    df_mavg.columns = ["trans_volume_mavg", "datetime"]
    df_mavg = df_mavg.reset_index(level=["cc_num"])
    df_mavg = df_mavg.drop(columns=["cc_num", "datetime"])
    df_mavg = df_mavg.sort_index()

    # Moving standard deviation of transaction volume.
    df_std = pd.DataFrame(cc_group.mean())
    df_std.columns = ["trans_volume_mstd", "datetime"]
    df_std = df_std.reset_index(level=["cc_num"])
    df_std = df_std.drop(columns=["cc_num", "datetime"])
    df_std = df_std.fillna(0)
    df_std = df_std.sort_index()
    window_aggs_df = df_std.merge(df_mavg,left_index=True, right_index=True)

    # Moving average of transaction frequency.
    df_count = pd.DataFrame(cc_group.mean())
    df_count.columns = ["trans_freq", "datetime"]
    df_count = df_count.reset_index(level=["cc_num"])
    df_count = df_count.drop(columns=["cc_num", "datetime"])
    df_count = df_count.sort_index()
    window_aggs_df = window_aggs_df.merge(df_count,left_index=True, right_index=True)

    # Moving average of location difference between consecutive transactions.
    cc_group = trans_df[["cc_num", "loc_delta_t_minus_1", "datetime"]].groupby("cc_num").rolling(window_len, on="datetime").mean()
    df_loc_delta_mavg = pd.DataFrame(cc_group)
    df_loc_delta_mavg.columns = ["loc_delta_mavg", "datetime"]
    df_loc_delta_mavg = df_loc_delta_mavg.reset_index(level=["cc_num"])
    df_loc_delta_mavg = df_loc_delta_mavg.drop(columns=["cc_num", "datetime"])
    df_loc_delta_mavg = df_loc_delta_mavg.sort_index()
    window_aggs_df = window_aggs_df.merge(df_loc_delta_mavg,left_index=True, right_index=True)

    window_aggs_df = window_aggs_df.merge(trans_df[["cc_num", "datetime"]].sort_index(),left_index=True, right_index=True)
 
    return window_aggs_df
