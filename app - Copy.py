
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Page config and logo
st.set_page_config(page_title="Straight Razor Draft 2025", layout="wide")
st.image("Straight_Razor_Draft_2025.jpg", width=300)

st.markdown("<h1 style='color:#1a1a1a;'>🏈 Straight Razor Draft 2025</h1>", unsafe_allow_html=True)
st.markdown("Live leaderboard tracking the 2025 NFL First Round Draft Picks!")

# Load Google Sheet
@st.cache_data(ttl=60)
def load_draft_results(sheet_url):
    try:
        df = pd.read_csv(sheet_url)
        return df
    except Exception as e:
        st.error(f"Failed to load draft results: {e}")
        return pd.DataFrame()

# Load participant entries (local Excel file)
@st.cache_data
def load_entries(path):
    try:
        df = pd.read_excel(path, engine="openpyxl")
        return df
    except Exception as e:
        st.error(f"Failed to load entries: {e}")
        return pd.DataFrame()

# SCORE CALCULATION
def calculate_scores(entries_df, results_df):
    scores = []
    for i, row in entries_df.iterrows():
        name = row['Name']
        user_picks = row[3:].values.tolist()
        total_score = 0
        correct = 0
        for pos, player in enumerate(user_picks):
            if player in results_df['Player'].values:
                actual_pos = results_df[results_df['Player'] == player]['Pick'].values[0]
                diff = abs((pos+1) - actual_pos)
                score = 32 if diff == 0 else max(0, 32 - diff)
                total_score += score
                if diff == 0:
                    correct += 1
        scores.append({"Name": name, "Score": total_score, "Correct Picks": correct})
    return pd.DataFrame(scores).sort_values(by=["Score", "Correct Picks"], ascending=False)

# Sidebar - refresh data
st.sidebar.title("Controls")
if st.sidebar.button("🔄 Refresh Draft Results"):
    st.cache_data.clear()

# Load data
sheet_url = "https://docs.google.com/spreadsheets/d/1UZkdBJlZ0T4Wd0TM9q6U5HBfyeQOH7ORE8y7QZOI4PQ/export?format=csv"
entries_df = load_entries("Straight_Razor_Entries.xlsx")
results_df = load_draft_results(sheet_url)

# Show draft picks
st.subheader("📋 Live Draft Picks")
if not results_df.empty:
    st.dataframe(results_df)

# Show leaderboard
if not entries_df.empty and not results_df.empty:
    leaderboard = calculate_scores(entries_df, results_df)
    st.subheader("🏆 Leaderboard")
    st.dataframe(leaderboard)
