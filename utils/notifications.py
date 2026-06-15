from utils.admin import ADMIN_EMAILS

def send_reservation_notification_to_admin(group_label, date, slot, reserved_by_email, is_admin_created=False):
    from utils.email_utils import send_email
    subject = f"[MiniFabLab] Nouvelle réservation - {group_label}"
    creator_type = "Administrateur" if is_admin_created else "Utilisateur"
    body = f"""\
<html>
  <body>
    <h3>Nouvelle Réservation Confirmée</h3>
    <p>Une nouvelle réservation a été effectuée sur la plateforme MiniFabLab.</p>
    <p><b>Groupe :</b> {group_label}</p>
    <p><b>Date :</b> {date}</p>
    <p><b>Créneau :</b> {slot}</p>
    <p><b>Créé par :</b> {reserved_by_email or 'Non spécifié'} ({creator_type})</p>
    <br>
    <p>MiniFabLab ECC</p>
  </body>
</html>"""
    for admin_email in ADMIN_EMAILS:
        send_email(admin_email, subject, body)
