import streamlit as st
import numpy as np
import pandas as pd
from pandas_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report


def app():
    st.image('eda.png',width=200)
    st.title('''
    Exploratory Data Analysis App
    ''')

    # Upload CSV data
    st.set_option('deprecation.showfileUploaderEncoding', False)
    st.sidebar.header('1. Upload your CSV data')
    uploaded_file = st.sidebar.file_uploader("Upload your input CSV file", type=["csv"])
    st.sidebar.markdown("""
    [Example CSV input file](https://raw.githubusercontent.com/dataprofessor/data/master/delaney_solubility_with_descriptors.csv)
    """)

        # Pandas Profiling Report
    if uploaded_file is not None:
        @st.cache
        def load_csv():
            csv = pd.read_csv(uploaded_file)
            return csv
        df = load_csv()
        pr = ProfileReport(df, explorative=True)
        st.header('**Input DataFrame**')
        st.write(df)
        st.write('---')
        st.header('**Pandas Profiling Report**')
        st_profile_report(pr)
    else:
        st.info('Awaiting for CSV file to be uploaded.')
        if st.button('Press to use Example Dataset'):
            # Example data
            @st.cache
            def load_data():
                a = pd.DataFrame(
                np.random.rand(100, 5),
                columns=['a', 'b', 'c', 'd', 'e']
                )
                return a
            df = load_data()
            pr = ProfileReport(df, explorative=True)
            st.header('**Input DataFrame**')
            st.write(df)
            st.write('---')
            st.header('**Pandas Profiling Report**')
            st_profile_report(pr)
