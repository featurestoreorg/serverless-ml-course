import pandas as pd
import numpy as np

from datetime import datetime
from math import radians

def haversine_distance(long: float, lat: float, long_prev: float, lat_prev: float):
    """Compute Haversine distance between each consecutive coordinate in (long, lat)."""

    long_diff = long_prev - long
    lat_diff = lat_prev - lat

    a = np.sin(lat_diff/2.0)**2
    b = np.cos(lat) * np.cos(lat_prev) * np.sin(long_diff/2.0)**2
    c = 2*np.arcsin(np.sqrt(a + b))

    return c

def time_delta(prev_datetime: int, current_datetime: int):
    """Compute time difference between each consecutive transaction."""    
    return prev_datetime - current_datetime

def time_delta_to_days(time_delta):
    """."""    
    return time_delta.total_seconds() / 86400

def date_to_timestamp(date_obj):
    return int(date_obj.timestamp() * 1000)

def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp // 1000)

def activity_level(trans_df : pd.DataFrame, lag: int)-> pd.DataFrame:
    
    # Convert coordinates into radians:
    trans_df[["longitude", "latitude"]] = trans_df[["longitude", "latitude"]].applymap(radians)
    
    trans_df.sort_values(["datetime", "cc_num"], inplace=True) 
    
    trans_df[f"loc_delta_t_minus_{lag}"] = trans_df.groupby("cc_num")\
        .apply(lambda x :haversine_distance(x["longitude"], x["latitude"], x["longitude"].shift(-lag), x["latitude"].shift(-lag)))\
        .reset_index(level=0, drop=True)\
        .fillna(0)
    
    trans_df[f"time_delta_t_minus_{lag}"] = trans_df.groupby("cc_num")\
        .apply(lambda x : time_delta(x["datetime"].shift(-lag), x["datetime"]))\
        .reset_index(level=0, drop=True)
    
    trans_df[f"time_delta_t_minus_{lag}"] = trans_df[f"time_delta_t_minus_{lag}"].map(lambda x: time_delta_to_days(x))
    trans_df[f"time_delta_t_minus_{lag}"] = trans_df[f"time_delta_t_minus_{lag}"].fillna(0)
    trans_df = trans_df[["tid","datetime","cc_num","amount", f"loc_delta_t_minus_{lag}", f"time_delta_t_minus_{lag}"]]
    trans_df.datetime = trans_df.datetime.map(lambda x: date_to_timestamp(x))
    return trans_df
