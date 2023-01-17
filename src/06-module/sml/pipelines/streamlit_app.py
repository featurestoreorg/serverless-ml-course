import datetime
from math import radians
from sml import cc_features

import pandas as pd
import numpy as np
import plotly.express as px
from matplotlib import pyplot
import warnings

import hopsworks
from sml import synthetic_data

import streamlit as st

import folium
from streamlit_folium import st_folium
import json

time_now = int(datetime.datetime.now().timestamp() * 1000)
synthetic_data.set_random_seed(12345)
credit_cards = [cc["cc_num"] for cc in synthetic_data.generate_list_credit_card_numbers()]
lat = 0
long = 0

warnings.filterwarnings("ignore")


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def retrive_dataset():
    st.write(36 * "-")
    print_fancy_header('\n💾 Dataset Retrieving...')
    feature_view = fs.get_feature_view("transactions_fraud_online_fv", 1)
    batch_data = feature_view.get_batch_data()
    return batch_data


@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def get_feature_views():
    fv = fs.get_feature_view("transactions_fraud_online_fv", 1)
    latest_record_fv = fs.get_feature_view("latest_recorded_transactions_fraud_online_fv", 1)
    return fv, latest_record_fv


@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def get_deployment(project):
    mr = project.get_model_registry()
    ms = project.get_model_serving()
    deployment = ms.get_deployment("fraudonlinemodeldeployment")
    return deployment


def explore_data():
    st.write(36 * "-")
    print_fancy_header('\n👁 Data Exploration...')
    labels = ["Normal", "Fraudulent"]
    unique, counts = np.unique(test_mar_y.fraud_label.values, return_counts=True)
    values = counts.tolist()

    def plot_pie(values, labels):
        fig = px.pie(values=values, names=labels, title='Distribution of fraud transactions')
        return fig

    fig1 = plot_pie(values, labels)
    st.plotly_chart(fig1)


def process_input_vector(cc_num, current_datetime, amount, long, lat):
    long = radians(long)
    lat = radians(lat)

    current_coordinates = pd.DataFrame({
        "datetime": [int(current_datetime)],
        "cc_num": [cc_num],
        "latitude": [long],
        "longitude": [lat]

    })

    # get fv for the latest recorded transactions 
    latest_record_vector = latest_record_fv.get_feature_vector({"cc_num": cc_num})
    # compute deltas between previous and current
    loc_delta_t_minus_1 = cc_features.haversine_distance(long=long, lat=lat, prev_long=latest_record_vector[3],
                                                         prev_lat=latest_record_vector[2])
    time_delta_t_minus_1 = cc_features.time_delta(cc_features.timestamp_to_date(latest_record_vector[0]),
                                                  cc_features.timestamp_to_date(current_datetime))
    time_delta_t_minus_1 = cc_features.time_delta_to_days(time_delta_t_minus_1)
    # get all features
    feature_vector = fv.get_feature_vector({"cc_num": cc_num},
                                           passed_features={"amout": amount,
                                                            "loc_delta_t_minus_1": loc_delta_t_minus_1,
                                                            "time_delta_t_minus_1": time_delta_t_minus_1})

    # drop extra features
    indexes_to_remove = [0, 1]
    return {"inputs": [i for j, i in enumerate(feature_vector) if j not in indexes_to_remove]}, current_coordinates


def print_fancy_header(text, font_size=24):
    res = f'<span style="color:#ff5f27; font-size: {font_size}px;">{text}</span>'
    st.markdown(res, unsafe_allow_html=True)


progress_bar = st.sidebar.header('⚙️ Working Progress')
progress_bar = st.sidebar.progress(0)
st.title('🆘 Fraud transactions detection 🆘')

st.write(36 * "-")
print_fancy_header('\n📡 Connecting to Hopsworks Feature Store...')

project = hopsworks.login()
fs = project.get_feature_store()
progress_bar.progress(15)

st.write(36 * "-")
print_fancy_header('\n🤖 Connecting to Model Registry on Hopsworks...')
deployment = get_deployment(project)
deployment.start()
st.write("✅ Connected!")

progress_bar.progress(40)

st.write(36 * "-")
print_fancy_header('\n✨ Feature view retrieving...')
fv, latest_record_fv = get_feature_views()
st.write("✅ Retrieved!")

progress_bar.progress(55)

st.write(36 * "-")
print_fancy_header('\n🧠 On map bellow select location of ATM machine')
with st.form(key="Selecting cc_num"):
    cc_num = st.selectbox(
        'Select a credit card number.',
        (credit_cards)
    )

    amount = st.slider(
        '💶 Select withdrawal amount',
        5, 1000)

    # my_map = folium.Map(location=[41, -73.5], zoom_start=8)
    my_map = folium.Map(location=[52, 24], zoom_start=3)

    my_map.add_child(folium.LatLngPopup())
    folium.TileLayer('Stamen Terrain').add_to(my_map)
    folium.TileLayer('Stamen Toner').add_to(my_map)
    folium.TileLayer('Stamen Water Color').add_to(my_map)
    folium.TileLayer('cartodbpositron').add_to(my_map)
    folium.TileLayer('cartodbdark_matter').add_to(my_map)
    folium.LayerControl().add_to(my_map)

    res_map = st_folium(my_map, height=300, width=600)

    try:
        lat, long = res_map["last_clicked"]["lat"], res_map["last_clicked"]["lng"]

        st.print_fancy_header("🏧 Withdrawal coordinates:")
        st.write(f"Latitude: {lat}")
        st.write(f"Longitude: {long}")
    except Exception as err:
        print(err)
        pass

    submit_button = st.form_submit_button(label='Withdraw')

progress_bar.progress(70)

st.write(36 * "-")

# run code below if deployment doesnt work
# print_fancy_header("Initialise serving...")
# fv.init_serving(1)
# time_now = int(datetime.datetime.now().timestamp()*1000)

data, current_coordinates = process_input_vector(cc_num=int(cc_num),
                            current_datetime=int(time_now),
                            amount=amount,
                            lat=lat, long=long)

if st.button('📊 Make a prediction'):
    res = deployment.predict(data)
    progress_bar.progress(80)
    negative = "**👌 Not a suspicious**"
    positive = "**🆘 Fraudulent**"
    res = negative if res["predictions"][0] == 0 else positive
    print_fancy_header(res + " transaction!")
    progress_bar.progress(100)
    deployment.stop()
    st.write(36 * "-")
    st.write("Stopping the deployment...")
    st.write("")
    st.write('\n🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')

    # update fg
    latest_recorded_transactions_fraud_online_fg = fs.get_or_create_feature_group(
        name="latest_recorded_transactions_fraud_online",
        version=1
    )
    latest_recorded_transactions_fraud_online_fg.insert(current_coordinates)

st.button("Re-run")
