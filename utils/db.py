import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from supabase import create_client, Client

# Initialize Supabase client
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

def create_reservation(group_name, user_email, reservation_date, slot_start, slot_end, is_weekend):
    supabase = get_supabase()
    
    # Check if the slot is already full (max 2 groups)
    res = supabase.table("reservations").select("*", count="exact").match({
        "reservation_date": reservation_date,
        "slot_start": slot_start,
        "slot_end": slot_end
    }).execute()
    
    count = res.count
    if count >= 2:
        return False, "This slot is already fully booked (max 2 groups)."
    
    # Check if the group has reached its limit for the week
    date_obj = datetime.strptime(reservation_date, "%Y-%m-%d")
    monday = date_obj - timedelta(days=date_obj.weekday())
    monday_str = monday.strftime("%Y-%m-%d")
    sunday = monday + timedelta(days=6)
    sunday_str = sunday.strftime("%Y-%m-%d")
    
    res_group = supabase.table("reservations").select("*", count="exact").match({
        "group_name": group_name,
        "is_weekend": is_weekend
    }).gte("reservation_date", monday_str).lte("reservation_date", sunday_str).execute()
    
    group_count = res_group.count
    
    # Limits
    if group_name.startswith("plbd"):
        limit = 5 if is_weekend else 3
    else: # bachelor
        limit = 6 if is_weekend else 5
        
    if group_count >= limit:
        period = "weekend" if is_weekend else "weekdays"
        return False, f"Group {group_name} has reached the limit of {limit} reservations for {period} this week."
    
    # Create reservation
    data = {
        "group_name": group_name,
        "user_email": user_email,
        "reservation_date": reservation_date,
        "slot_start": slot_start,
        "slot_end": slot_end,
        "is_weekend": is_weekend
    }
    supabase.table("reservations").insert(data).execute()
    
    return True, "Reservation successful!"

def get_reservations(start_date=None, end_date=None):
    supabase = get_supabase()
    query = supabase.table("reservations").select("*")
    
    if start_date and end_date:
        query = query.gte("reservation_date", start_date).lte("reservation_date", end_date)
    
    res = query.execute()
    return pd.DataFrame(res.data)

def save_token(email, token, expires_at):
    supabase = get_supabase()
    data = {
        "email": email,
        "token": token,
        "expires_at": expires_at.isoformat()
    }
    try:
        # upsert based on email
        supabase.table("auth_tokens").upsert(data, on_conflict="email").execute()
    except Exception as e:
        st.error(f"Database error in save_token: {e}")
        raise

def verify_token(token):
    supabase = get_supabase()
    now = datetime.now().isoformat()
    res = supabase.table("auth_tokens").select("email").match({"token": token}).gt("expires_at", now).execute()
    
    if res.data:
        return res.data[0]['email']
    return None

def delete_reservation(res_id, group_name):
    supabase = get_supabase()
    res = supabase.table("reservations").delete().match({"id": res_id, "group_name": group_name}).execute()
    return len(res.data) > 0
