import hopsworks
import streamlit as st
import plotly.express as px
from matplotlib import pyplot

import pandas as pd
import numpy as np
import warnings


warnings.filterwarnings("ignore")

progress_bar = st.sidebar.header('⚙️ Working Progress')
progress_bar = st.sidebar.progress(0)
st.title('Fraud transactions detection')

st.write(36 * "-")
st.header('\n📡 Connecting to Hopsworks Feature Store...')
project = hopsworks.login()
fs = project.get_feature_store()
progress_bar.progress(35)


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def retrive_dataset():
    st.write(36 * "-")
    st.header('\n💾 Dataset Retrieving...')
    feature_view = fs.get_feature_view("transactions_fraud_online_fv", 1)
    test_mar_x, test_mar_y = feature_view.get_training_data(2) # for demonstration purposes I will retrieve
                                                               # only test data
    return feature_view, test_mar_x, test_mar_y


feature_view, test_mar_x, test_mar_y = retrive_dataset()
# show concatenated training dataset (label is a 'fraud_label' feature)
st.dataframe(pd.concat([test_mar_x.head(),(test_mar_y.head())], axis=1))
progress_bar.progress(55)


def explore_data():
    st.write(36 * "-")
    st.header('\n👁 Data Exploration...')
    labels = ["Normal", "Fraudulent"]
    unique, counts = np.unique(test_mar_y.fraud_label.values, return_counts=True)
    values = counts.tolist()

    def plot_pie(values, labels):
        fig = px.pie(values=values, names=labels, title='Distribution of fraud transactions')
        return fig

    fig1 = plot_pie(values, labels)
    st.plotly_chart(fig1)
    progress_bar.progress(70)


explore_data()


st.write(36 * "-")
st.header('\n🤖 Connecting to Model Registry on Hopsworks...')
@st.cache(suppress_st_warning=True)
def get_deployment(project):
    mr = project.get_model_registry()
    ms = project.get_model_serving()
    deployment = ms.get_deployment("fraudonlinemodeldeployment")
    deployment.start()
    return deployment

deployment = get_deployment(project)

progress_bar.progress(85)


st.write(36 * "-")
st.header('\n🧠 Interactive predictions...')
with st.form(key="Selecting cc_num"):
    option = st.selectbox(
         'Select a credit card to get a fraud analysis.',
         (test_mar_x.cc_num.sample(5).values)
         )
    submit_button = st.form_submit_button(label='Submit')
if submit_button:
    st.write('You selected:', option)
    data = {"inputs": [str(option)]}
    res = deployment.predict(data)
    negative = "**👌 Not a suspicious**"
    positive = "**🆘 Fraudulent**"
    res = negative if res["predictions"][0] == -1 else positive
    st.write(res, "transaction.")
    deployment.stop()
    progress_bar.progress(100)
    st.write(36 * "-")
    st.header('\n🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')
