# app.py
import streamlit as st
import pandas as pd
from log_parser import parse_log_file
from config import CEID_MAP
from analyzer import analyze_data, perform_eda

# ... (st.set_page_config and sidebar code remain unchanged) ...

if uploaded_file:
    # ... (parsing and summary logic remain unchanged) ...

    # --- Exploratory Data Analysis (EDA) Section ---
    with st.expander("Show Exploratory Data Analysis (EDA)"):
        st.subheader("Event Frequency")
        # ... (unchanged) ...

        st.subheader("Alarm Analysis")
        if not eda_results.get('alarm_counts', pd.Series()).empty:
            st.write("Alarm Counts:")
            st.bar_chart(eda_results['alarm_counts'])
            st.write("Alarm Events Log:")
            st.dataframe(eda_results['alarm_table'], use_container_width=True)

            # --- START OF HIGHLIGHTED ADDITION ---
            st.subheader("Predictive Analysis: Alarm Correlations")
            correlation_df = eda_results.get('alarm_correlations', pd.DataFrame())
            if not correlation_df.empty:
                st.write("Common event sequences that occurred just before an alarm:")
                st.dataframe(correlation_df, hide_index=True, use_container_width=True)
            else:
                st.info("No recurring event patterns leading to alarms were found.")
            # --- END OF HIGHLIGHTED ADDITION ---
            
        else:
            st.success("✅ No Alarms Found in Log")

    # ... (The rest of the app remains unchanged) ...
