from fpdf import FPDF

class GuidePDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 18)
        self.cell(0, 10, "Guide d'Utilisation du MiniFabLab", border=0, align="C")
        self.ln(15)

    def chapter_title(self, num, title):
        self.set_font("helvetica", "B", 14)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 8, f" {num}. {title}", border=0, fill=True, align="L")
        self.ln(10)

    def chapter_body(self, body):
        self.set_font("helvetica", "", 11)
        self.multi_cell(0, 6, body)
        self.ln(5)

pdf = GuidePDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

# Intro
intro_text = "Bienvenue sur l'application de réservation du MiniFabLab ! Ce document vous expliquera comment vous connecter, comment créer et gérer vos réservations, ainsi que les règles du laboratoire."
pdf.set_font("helvetica", "I", 12)
pdf.multi_cell(0, 6, intro_text)
pdf.ln(10)

# Section 1
pdf.chapter_title(1, "Connexion et Identité")
text1 = (
    "L'application utilise un système intelligent de connexion sans mot de passe.\n\n"
    "Pour les Étudiants PLBD :\n"
    "1. Allez sur la page 'Connexion / Identité'.\n"
    "2. Dans l'onglet 'Groupes PLBD', entrez votre email de l'école (format prenom.nom@centrale-casablanca.ma).\n"
    "3. Appuyez sur Entrée ou cliquez sur 'Envoyer le lien de connexion'.\n"
    "4. Allez dans votre boîte Microsoft Outlook, vous allez y recevoir un lien de connexion magique (n'oubliez pas de vérifier vos courriers indésirables/spams !).\n"
    "5. Cliquez sur le lien dans l'email, et vous serez automatiquement authentifié et redirigé vers l'application.\n\n"
    "Pour les Étudiants Bachelor :\n"
    "1. Allez sur l'onglet 'Groupes Bachelor'.\n"
    "2. Sélectionnez le numéro de votre groupe et tapez votre email pour le suivi.\n"
    "3. Appuyez sur Entrée pour définir votre identité dans le navigateur."
)
pdf.chapter_body(text1)

# Section 2
pdf.chapter_title(2, "Règles et Limites de Réservation")
text2 = (
    "Pour offrir à tous un accès équitable aux locaux du MiniFabLab, des limites strictes sont appliquées au niveau de votre GROUPE.\n\n"
    "Limites pour Groupes PLBD :\n"
    "- Semaine (Lundi au Vendredi) : Maximum 3 réservations par semaine, dans la limite d'une (1) réservation par jour.\n"
    "- Week-end (Samedi au Dimanche) : Maximum 5 réservations (pas de limite par jour).\n\n"
    "Limites pour Groupes Bachelor :\n"
    "- Semaine : Maximum 5 réservations, dans la limite d'une (1) par jour.\n"
    "- Week-end : Maximum 6 réservations.\n\n"
    "Créneaux Horaires :\n"
    "- En semaine, 2 créneaux sont disponibles le soir (18:00-20:30, 20:30-23:00).\n"
    "- En week-end, 5 créneaux sont répartis du matin au soir (10:30, 13:00, 15:30, 18:00, 20:30).\n\n"
    "Chaque créneau horaire peut accueillir un maximum absolu de deux (2) groupes de travail simultanément."
)
pdf.chapter_body(text2)

# Section 3
pdf.chapter_title(3, "Comment Réserver et Gérer son Planning")
text3 = (
    "Une fois connecté, vous serez redirigé vers la page 'Faire une Réservation'.\n\n"
    "1. Choisissez la date souhaitée via le calendrier intégré. Vous pouvez réserver jusqu'à 14 jours en avance.\n"
    "2. Les créneaux disponibles s'afficheront en fonction du jour selectionné.\n"
    "3. Si un créneau affiche 'Complet' (2/2 Réservé), le bouton de réservation sera désactivé.\n"
    "4. Si le créneau est disponible, cliquez sur 'Réserver'. L'application vérifiera vos limites et enregistrera le créneau si la demande est valide.\n"
    "5. Un email de confirmation contenant les détails du créneau sera envoyé à votre boîte mail.\n\n"
    "Le tableau de bord global ('Planning Actuel') vous permet en un clin d'oeil de voir l'état des lieux pour la semaine courante ou la semaine prochaine. Vous y verrez un statut clair par jour et créneau (Libre, 1/2, Complet)."
)
pdf.chapter_body(text3)

# Section 4
pdf.chapter_title(4, "Support et Administration")
text4 = (
    "L'application garde votre session active grâce à des cookies persistants. Si vous revenez le lendemain, vous n'aurez plus besoin de demander un email de connexion !\n\n"
    "En de rares occasions, l'administration peut être amenée à suspendre globalement toute réservation pour des raisons de maintenance. Vous en serez avertis via la plateforme.\n\n"
    "Si vous constatez un problème technique d'accès, une erreur dans vos crédits, ou un bug lors d'une annulation de réservation, merci de contacter d'urgence l'administration : \n"
    "- anwar.mounir@centrale-casablanca.ma\n"
    "- yahya.elomari@centrale-casablanca.ma\n"
    "- ahmadmoubarak.tiemtore@centrale-casablanca.ma\n"
    "- yahya.barhoun@centrale-casablanca.ma\n"
    "- meryem.soussi@centrale-casablanca.ma\n"
)
pdf.chapter_body(text4)

# Create PDF
pdf.output("Guide_Utilisation_MiniFabLab.pdf")
print("PDF created successfully!")
