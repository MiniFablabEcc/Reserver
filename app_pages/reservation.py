import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from utils.db import create_reservation, get_reservations, delete_reservation, get_reservations_paused
from utils.email_utils import send_reservation_confirmation

st.header("📅 Faire une Réservation")

if not st.session_state.get("group_type"):
    st.warning("Veuillez d'abord définir votre identité ou vous connecter.")
    if st.button("Aller à la Connexion"):
        st.switch_page("app_pages/login.py")
    st.stop()

group_type = st.session_state.group_type
group_index = st.session_state.group_index
user_email = st.session_state.get("user_email")
group_label = f"{group_type} {group_index}"

st.info(f"Réservation pour : **{group_label}**")

if get_reservations_paused():
    st.error("🔴 **Les réservations sont actuellement suspendues par l'administrateur.** Vous ne pouvez pas effectuer de nouvelles réservations pour le moment.")
    st.stop()

# Date selection
today = date.today()
max_date = today + timedelta(days=14) # Allow booking 2 weeks in advance
selected_date = st.date_input("Sélectionner une Date", min_value=today, max_value=max_date, value=today)

# Determine if weekend
is_weekend = selected_date.weekday() >= 5 # 5=Saturday, 6=Sunday

# Define slots
if is_weekend:
    slots = [
        ("10:30", "13:00"),
        ("13:00", "15:30"),
        ("15:30", "18:00"),
        ("18:00", "20:30"),
        ("20:30", "23:00")
    ]
else:
    slots = [
        ("18:00", "20:30"),
        ("20:30", "23:00")
    ]

# Get existing reservations for the selected date to show availability
reservations_df = get_reservations(selected_date.strftime("%Y-%m-%d"), selected_date.strftime("%Y-%m-%d"))

st.subheader("Créneaux Disponibles")
st.write("Chaque créneau peut accueillir jusqu'à 2 groupes simultanément.")

for start, end in slots:
    # Count existing reservations for this slot
    if not reservations_df.empty and 'slot_start' in reservations_df.columns:
        slot_res = reservations_df[(reservations_df['slot_start'] == start) & (reservations_df['slot_end'] == end)]
        count = len(slot_res)
    else:
        count = 0
    
    col1, col2, col3 = st.columns([2, 1, 1])
    col1.write(f"**{start} - {end}**")
    
    if count >= 2:
        col2.error("Complet")
        col3.write("Indisponible")
    else:
        col2.success(f"{count}/2 Réservé(s)")
        if col3.button("Réserver", key=f"btn_{start}_{selected_date}"):
            success, message = create_reservation(
                group_type,
                group_index,
                user_email, 
                selected_date.strftime("%Y-%m-%d"), 
                start, 
                end, 
                is_weekend
            )
            if success:
                st.success(message)
                # Send confirmation email if user is PLBD (has email)
                if user_email:
                    send_reservation_confirmation(user_email, group_label, selected_date.strftime("%Y-%m-%d"), f"{start}-{end}")
                st.rerun()
            else:
                st.error(message)

st.divider()

# My Reservations Section
st.subheader("Réservations de mon Groupe")
all_res = get_reservations()

if not all_res.empty and 'group_type' in all_res.columns:
    my_res = all_res[(all_res['group_type'] == group_type) & (all_res['group_index'] == group_index)]
else:
    my_res = pd.DataFrame()

if not my_res.empty:
    # Filter for future or today's reservations
    my_res = my_res.copy()
    my_res['date_parsed'] = my_res['date'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").date() if isinstance(x, str) else x)
    future_res = my_res[my_res['date_parsed'] >= today].sort_values('date_parsed')
    
    if not future_res.empty:
        for idx, row in future_res.iterrows():
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.write(f"{row['date']}")
            c2.write(f"{row['slot_start']} - {row['slot_end']}")
            
            res_dt = datetime.strptime(f"{row['date']} {row['slot_start']}", "%Y-%m-%d %H:%M")
            cannot_cancel = datetime.now() > res_dt - timedelta(hours=1)
            
            if c3.button("Annuler", key=f"del_{row['id']}", disabled=cannot_cancel, help="Annulation impossible à moins d'1h" if cannot_cancel else "Annuler cette réservation"):
                if delete_reservation(row['id'], group_type, group_index):
                    st.success("Réservation annulée.")
                    st.rerun()
                else:
                    st.error("Échec de l'annulation.")
    else:
        st.write("Aucune réservation à venir.")
else:
    st.write("Vous n'avez fait aucune réservation pour le moment.")
