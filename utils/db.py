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

def create_reservation(group_type, group_index, user_email, reservation_date, slot_start, slot_end, is_weekend):
    supabase = get_supabase()
    
    # Check if the slot is already full (max 2 groups)
    res = supabase.table("reservations").select("*", count="exact").match({
        "date": reservation_date,
        "slot_start": slot_start,
        "slot_end": slot_end
    }).execute()
    
    count = res.count
    if count >= 2:
        return False, "Ce créneau est déjà complet (max 2 groupes)."
        
    # Check if this group already booked this exact slot (no double booking a slot)
    res_slot_group = supabase.table("reservations").select("*", count="exact").match({
        "date": reservation_date,
        "slot_start": slot_start,
        "slot_end": slot_end,
        "group_type": group_type,
        "group_index": group_index
    }).execute()
    
    if res_slot_group.count >= 1:
        return False, "Votre groupe a déjà une réservation pour ce créneau. Vous ne pouvez pas réserver les deux places."
        
    # On weekdays, a group can only reserve 1 slot per day
    if not is_weekend:
        res_day_group = supabase.table("reservations").select("*", count="exact").match({
            "date": reservation_date,
            "group_type": group_type,
            "group_index": group_index
        }).execute()
        
        if res_day_group.count >= 1:
            return False, "En semaine, votre groupe ne peut réserver qu'un seul créneau par jour."
    
    # Check if the group has reached its limit for the week
    date_obj = datetime.strptime(reservation_date, "%Y-%m-%d")
    monday = date_obj - timedelta(days=date_obj.weekday())
    monday_str = monday.strftime("%Y-%m-%d")
    sunday = monday + timedelta(days=6)
    sunday_str = sunday.strftime("%Y-%m-%d")
    
    res_group = supabase.table("reservations").select("*", count="exact").match({
        "group_type": group_type,
        "group_index": group_index
    }).gte("date", monday_str).lte("date", sunday_str).execute()
    
    group_count = res_group.count
    
    # Limits
    if group_type == "plbd":
        limit = 5 if is_weekend else 3
    else:  # bachelor
        limit = 6 if is_weekend else 5
        
    if group_count >= limit:
        period = "le week-end" if is_weekend else "la semaine"
        group_label = f"{group_type} {group_index}"
        return False, f"Le groupe {group_label} a atteint la limite de {limit} réservations pour {period} cette semaine."
    
    # Create reservation
    data = {
        "group_type": group_type,
        "group_index": group_index,
        "user_email": user_email,
        "date": reservation_date,
        "slot_start": slot_start,
        "slot_end": slot_end
    }
    try:
        supabase.table("reservations").insert(data).execute()
    except Exception as e:
        return False, f"Erreur de base de données : {e}"
    
    return True, "Réservation réussie !"

def get_reservations(start_date=None, end_date=None):
    supabase = get_supabase()
    query = supabase.table("reservations").select("*")
    
    if start_date and end_date:
        query = query.gte("date", start_date).lte("date", end_date)
    
    try:
        res = query.execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"Database error in get_reservations: {e}")
        return pd.DataFrame()

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

def delete_reservation(res_id, group_type, group_index):
    supabase = get_supabase()
    res = supabase.table("reservations").delete().match({
        "id": res_id,
        "group_type": group_type,
        "group_index": group_index
    }).execute()
    return len(res.data) > 0

def admin_delete_reservation(res_id):
    """Admin: delete any reservation by ID regardless of group."""
    supabase = get_supabase()
    res = supabase.table("reservations").delete().eq("id", res_id).execute()
    return len(res.data) > 0

def admin_create_reservation(group_type, group_index, user_email, reservation_date, slot_start, slot_end):
    """Admin: create a reservation bypassing all limits (still checks slot capacity)."""
    supabase = get_supabase()
    
    # Still check if slot is full (max 2)
    res = supabase.table("reservations").select("*", count="exact").match({
        "date": reservation_date,
        "slot_start": slot_start,
        "slot_end": slot_end
    }).execute()
    
    if res.count >= 2:
        return False, "Ce créneau est déjà complet (max 2 groupes)."
    
    data = {
        "group_type": group_type,
        "group_index": group_index,
        "user_email": user_email,
        "date": reservation_date,
        "slot_start": slot_start,
        "slot_end": slot_end
    }
    try:
        supabase.table("reservations").insert(data).execute()
    except Exception as e:
        return False, f"Erreur de base de données : {e}"
    
    return True, "Réservation (Admin) réussie !"

def get_reservations_paused():
    """Check if reservations are globally paused."""
    supabase = get_supabase()
    try:
        res = supabase.table("app_settings").select("value").eq("key", "reservations_paused").execute()
        if res.data:
            return res.data[0]["value"] == "true"
    except Exception:
        pass
    return False

def set_reservations_paused(paused):
    """Set global reservations pause state."""
    supabase = get_supabase()
    try:
        supabase.table("app_settings").upsert({
            "key": "reservations_paused",
            "value": "true" if paused else "false"
        }, on_conflict="key").execute()
        return True
    except Exception as e:
        st.error(f"Error updating settings: {e}")
        return False
