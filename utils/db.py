import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import streamlit as st
from supabase import create_client, Client

# Initialize Supabase client
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

def handle_db_error(func_name: str, e: Exception) -> str:
    """
    Central database error handler. Detects connection problems or Supabase pauses,
    shows a prominent, elegant warning in the Streamlit UI (with French translation),
    and logs details to the terminal.
    """
    error_str = str(e)
    # Detect Cloudflare 521, connection refused, host resolution errors, etc.
    is_paused_or_down = (
        "521" in error_str
        or "Web server is down" in error_str
        or "cpaeihsixhvbhlprtmun.supabase.co" in error_str
        or "ConnectError" in error_str
        or "connection" in error_str.lower()
        or "not known" in error_str.lower()
        or "gaierror" in error_str.lower()
        or "resolution" in error_str.lower()
    )
    
    print(f"[DB ERROR] Exception in {func_name}: {e}")
    
    if is_paused_or_down:
        # Show a beautiful, high-visibility warning in the UI
        st.error(
            "⚠️ **La base de données est actuellement indisponible (Erreur 521 / Pause Supabase).**\n\n"
            "Si vous êtes l'administrateur, il est fort probable que votre **projet gratuit Supabase ait été mis en veille automatique** "
            "après 7 jours d'inactivité.\n\n"
            "**Comment réactiver le service :**\n"
            "1. Connectez-vous à votre [Dashboard Supabase](https://supabase.com/dashboard).\n"
            "2. Sélectionnez le projet `cpaeihsixhvbhlprtmun`.\n"
            "3. Cliquez sur le bouton **'Resume project'** (ou 'Restaurer').\n\n"
            "L'application redeviendra pleinement opérationnelle dans 1 à 2 minutes après cette action."
        )
        return "La base de données est actuellement en veille ou indisponible. Veuillez réessayer plus tard."
    else:
        st.error(f"Une erreur de base de données est survenue dans `{func_name}` : {e}")
        return f"Erreur de base de données : {e}"

def create_reservation(group_type, group_index, user_email, reservation_date, slot_start, slot_end, is_weekend):
    try:
        supabase = get_supabase()
        
        # Check if closed
        res_closed = supabase.table("reservations").select("*", count="exact").match({
            "date": reservation_date,
            "slot_start": slot_start,
            "slot_end": slot_end,
            "group_type": "ferme"
        }).execute()
        
        if res_closed.count >= 1:
            return False, "Ce créneau a été fermé par l'administration."

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
            
        # Active/Hoarding limits apply only to PLBD groups
        if group_type == "plbd":
            today_str = datetime.now(ZoneInfo("Africa/Casablanca")).strftime("%Y-%m-%d")
            res_future_group = supabase.table("reservations").select("*").match({
                "group_type": group_type,
                "group_index": group_index
            }).gte("date", today_str).execute()
            
            now = datetime.now(ZoneInfo("Africa/Casablanca")).replace(tzinfo=None)
            active_weekday_count = 0
            active_weekend_count = 0
            
            for r in res_future_group.data:
                r_date = datetime.strptime(r["date"], "%Y-%m-%d")
                r_end_dt = datetime.strptime(f"{r['date']} {r['slot_end']}", "%Y-%m-%d %H:%M")
                
                if now < r_end_dt:
                    if r_date.weekday() < 5:
                        active_weekday_count += 1
                    else:
                        active_weekend_count += 1
                        
            if not is_weekend and active_weekday_count >= 1:
                return False, "En semaine, les groupes PLBD ne peuvent avoir qu'une seule réservation active à la fois."
            if is_weekend and active_weekend_count >= 2:
                return False, "En week-end, les groupes PLBD ne peuvent avoir que 2 réservations actives à la fois."
        
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
        res = supabase.table("reservations").insert(data).execute()
        if res.data:
            return True, res.data[0]['id']
            
        return True, "Réservation réussie !"
    except Exception as e:
        return False, handle_db_error("create_reservation", e)

def get_reservations(start_date=None, end_date=None):
    try:
        supabase = get_supabase()
        query = supabase.table("reservations").select("*")
        
        if start_date and end_date:
            query = query.gte("date", start_date).lte("date", end_date)
            
        res = query.execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        handle_db_error("get_reservations", e)
        return pd.DataFrame()

def save_token(email, token, expires_at):
    try:
        supabase = get_supabase()
        data = {
            "email": email,
            "token": token,
            "expires_at": expires_at.isoformat()
        }
        # upsert based on email
        supabase.table("auth_tokens").upsert(data, on_conflict="email").execute()
    except Exception as e:
        error_msg = handle_db_error("save_token", e)
        raise Exception(error_msg) from e

def verify_token(token):
    try:
        supabase = get_supabase()
        now_dt = datetime.now(ZoneInfo("Africa/Casablanca"))
        now = now_dt.isoformat()
        res = supabase.table("auth_tokens").select("email").match({"token": token}).gt("expires_at", now).execute()
        
        if res.data:
            return res.data[0]['email']
    except Exception as e:
        handle_db_error("verify_token", e)
    return None

def clean_expired_tokens():
    """Housekeeping: remove expired tokens from DB"""
    try:
        supabase = get_supabase()
        now = datetime.now(ZoneInfo("Africa/Casablanca")).isoformat()
        supabase.table("auth_tokens").delete().lt("expires_at", now).execute()
    except Exception as e:
        print(f"[DB HOUSEKEEPING ERROR] in clean_expired_tokens: {e}")

def delete_reservation(res_id, group_type, group_index):
    try:
        supabase = get_supabase()
        res = supabase.table("reservations").delete().match({
            "id": res_id,
            "group_type": group_type,
            "group_index": group_index
        }).execute()
        return len(res.data) > 0
    except Exception as e:
        handle_db_error("delete_reservation", e)
        return False

def admin_delete_reservation(res_id):
    """Admin: delete any reservation by ID regardless of group."""
    try:
        supabase = get_supabase()
        res = supabase.table("reservations").delete().eq("id", res_id).execute()
        return len(res.data) > 0
    except Exception as e:
        handle_db_error("admin_delete_reservation", e)
        return False

def admin_create_reservation(group_type, group_index, user_email, reservation_date, slot_start, slot_end):
    """Admin: create a reservation bypassing all limits (still checks slot capacity)."""
    try:
        supabase = get_supabase()
        
        # Check if slot is closed (for non-ferme reservations)
        if group_type != "ferme":
            res_closed = supabase.table("reservations").select("*", count="exact").match({
                "date": reservation_date,
                "slot_start": slot_start,
                "slot_end": slot_end,
                "group_type": "ferme"
            }).execute()
            if res_closed.count >= 1:
                return False, "Ce créneau est fermé par l'administration. Réouvrez-le d'abord."
            
            # Check if slot is full (max 2)
            res = supabase.table("reservations").select("*", count="exact").match({
                "date": reservation_date,
                "slot_start": slot_start,
                "slot_end": slot_end
            }).execute()
            
            if res.count >= 2:
                return False, "Ce créneau est déjà complet (max 2 groupes)."
        else:
            # Dedup: check if already closed
            res_dup = supabase.table("reservations").select("*", count="exact").match({
                "date": reservation_date,
                "slot_start": slot_start,
                "slot_end": slot_end,
                "group_type": "ferme"
            }).execute()
            if res_dup.count >= 1:
                return False, "Ce créneau est déjà fermé."
        
        data = {
            "group_type": group_type,
            "group_index": group_index,
            "user_email": user_email,
            "date": reservation_date,
            "slot_start": slot_start,
            "slot_end": slot_end
        }
        res = supabase.table("reservations").insert(data).execute()
        if res.data:
            return True, res.data[0]['id']
            
        return True, "Réservation (Admin) réussie !"
    except Exception as e:
        return False, handle_db_error("admin_create_reservation", e)

def reopen_slot(reservation_date, slot_start, slot_end):
    """Admin: delete all ferme entries for a slot to reopen it."""
    try:
        supabase = get_supabase()
        res = supabase.table("reservations").delete().match({
            "date": reservation_date,
            "slot_start": slot_start,
            "slot_end": slot_end,
            "group_type": "ferme"
        }).execute()
        return len(res.data) > 0
    except Exception as e:
        handle_db_error("reopen_slot", e)
        return False

def get_reservations_paused():
    """Check if reservations are globally paused."""
    try:
        supabase = get_supabase()
        res = supabase.table("app_settings").select("value").eq("key", "reservations_paused").execute()
        if res.data:
            return res.data[0]["value"] == "true"
    except Exception as e:
        print(f"[DB ERROR] in get_reservations_paused: {e}")
    return False

def set_reservations_paused(paused):
    """Set global reservations pause state."""
    try:
        supabase = get_supabase()
        supabase.table("app_settings").upsert({
            "key": "reservations_paused",
            "value": "true" if paused else "false"
        }, on_conflict="key").execute()
        return True
    except Exception as e:
        handle_db_error("set_reservations_paused", e)
        return False

def save_material_request(reservation_id, materials):
    """Save a material request linked to a reservation."""
    try:
        supabase = get_supabase()
        data = {
            "reservation_id": reservation_id,
            "materials": materials
        }
        supabase.table("material_requests").insert(data).execute()
        return True
    except Exception as e:
        handle_db_error("save_material_request", e)
        return False

def get_material_requests():
    """Fetch all material requests."""
    try:
        supabase = get_supabase()
        res = supabase.table("material_requests").select("*").execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        handle_db_error("get_material_requests", e)
        return pd.DataFrame()
