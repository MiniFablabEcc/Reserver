import streamlit as st
import pandas as pd
from utils.db import get_reservations
from datetime import date, timedelta

st.header("📊 Planning Actuel")

# Week selector
today = date.today()
monday = today - timedelta(days=today.weekday())
sunday = monday + timedelta(days=6)

week_options = {
    "Cette semaine": monday,
    "Semaine prochaine": monday + timedelta(days=7),
}
selected_week = st.selectbox("Sélectionner la Semaine", list(week_options.keys()))
week_start = week_options[selected_week]
week_end = week_start + timedelta(days=6)

st.write(f"Affichage des réservations : **{week_start.strftime('%a %d %b')}** au **{week_end.strftime('%a %d %b %Y')}**")

df = get_reservations(week_start.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d"))

# Define all possible slots
weekday_slots = [("18:00", "20:30"), ("20:30", "23:00")]
weekend_slots = [
    ("10:30", "13:00"), ("13:00", "15:30"), ("15:30", "18:00"),
    ("18:00", "20:30"), ("20:30", "23:00")
]

# Build the schedule table
days = []
current_day = week_start
while current_day <= week_end:
    days.append(current_day)
    current_day += timedelta(days=1)

# Create a table for each day
for day in days:
    is_weekend = day.weekday() >= 5
    slots = weekend_slots if is_weekend else weekday_slots
    day_label = day.strftime("%A %d %b")
    weekend_tag = " 🟢" if is_weekend else ""
    
    st.subheader(f"{day_label}{weekend_tag}")
    
    if df.empty:
        day_df = pd.DataFrame()
    else:
        day_df = df[df['date'] == day.strftime("%Y-%m-%d")]
    
    # Build table data for this day
    table_data = []
    for start, end in slots:
        slot_label = f"{start} - {end}"
        if day_df.empty:
            groups = []
        else:
            slot_rows = day_df[(day_df['slot_start'] == start) & (day_df['slot_end'] == end)]
            groups = (slot_rows['group_type'] + " " + slot_rows['group_index'].astype(str)).tolist()
        
        occupancy = len(groups)
        group_1 = groups[0] if len(groups) >= 1 else "—"
        group_2 = groups[1] if len(groups) >= 2 else "—"
        
        if occupancy >= 2:
            status = "🔴 Complet"
        elif occupancy == 1:
            status = "🟡 1/2"
        else:
            status = "🟢 Libre"
        
        table_data.append({
            "Créneau": slot_label,
            "Groupe 1": group_1,
            "Groupe 2": group_2,
            "Statut": status
        })
    
    table_df = pd.DataFrame(table_data)
    st.table(table_df)
