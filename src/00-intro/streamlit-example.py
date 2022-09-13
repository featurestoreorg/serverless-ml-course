# +
import pandas as pd
import streamlit as st
import numpy as np

st.title("Streamlit for ServerlessML")
st.header("Easy UI in Python with Streamlit")

chart_data = pd.DataFrame(np.random.randn(30, 3),
columns=["Data Engineers", "Data Scientists", "ML Engineers"])

st.bar_chart(chart_data)
