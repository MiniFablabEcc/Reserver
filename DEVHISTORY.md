# Historique de Développement - MiniFabLab Reservation System

Ce document retrace l'évolution technique du système de réservation MiniFabLab, de son implémentation initiale aux stabilisations de production.

---

## 🛠 Phase 1 : Fondations et Architecture (20 Avril 2024)

### Implémentation Initiale (`e45d6a1`)
- Mise en place de la structure Streamlit avec navigation par pages.
- Intégration de **Supabase** comme base de données (Tables: `reservations`, `auth_tokens`).
- Système d'authentification par "Magic Link" envoyé par email.
- Premier système de réservation avec gestion des créneaux (matin/après-midi).

### Débogage Critique et SMTP (`4c742db` - `20a4765`)
- Correction de bugs sur le parsing du fichier `plbd_emails.json`.
- Transition forcée de l'envoi d'emails : Outlook SMTP → **Gmail SMTP** suite à des problèmes de blocage.
- Amélioration de la remontée d'erreurs SMTP dans l'interface utilisateur.

### Alignement Schema Supabase (`bb7b966`)
- Refactoring majeur pour aligner le code Python avec les colonnes réelles de Supabase (`date`, `group_type`, `group_index`).

---

## 🚀 Phase 2 : Fonctionnalités Avancées et UX (21 Avril 2024)

### Session Persistante et Cookies (`3ec9c65` - `dd65afb`)
- Implémentation d'un système de cookies JavaScript pour maintenir la session utilisateur après rafraîchissement de la page ou fermeture du navigateur.
- Migration vers une approche "zéro dépendance" pour les cookies afin d'éviter les conflits avec les composants Streamlit tiers.

### Système Administratif (`890c6a9`)
- Création du **Panneau d'Admin**.
- Fonctions d'administration : pause globale des réservations, suppression de n'importe quel créneau, bypass des limites de réservation.

### Internationalisation et Ergonomie (`6eb9f47` - `bacf2b3`)
- Traduction intégrale de l'interface et des emails en **Français**.
- Soumission du formulaire de connexion par la touche "Entrée".
- Amélioration de la navigation dynamique (redirection auto après login).

### Documentation et Guide Utilisateur (`d06b457` - `703a4e1`)
- Création d'un script de génération de PDF (`generate_pdf.py`) utilisant ReportLab.
- Publication du **Guide d'Utilisation MiniFabLab**.

---

## 🔒 Phase 3 : Sécurité et Logique métier (21 Avril - 22 Avril 2024)

### Durcissement de la Logique Métier (`116605a` - `9d2dd9e`)
- **Limite d'annulation** : Impossible d'annuler une réservation moins d'une heure avant le début.
- **Limites anti-thésaurisation (Anti-hoarding)** :
    - PLBD : 1 seule réservation active en semaine, 2 le week-end.
    - Bachelors : Exemptés des limites strictes d'activité mais soumis aux limites hebdomadaires.
- Interdiction stricte de réserver deux fois le même créneau pour un même groupe.

### Sécurité Session (`4360af0`)
- Implémentation d'une signature **HMAC** pour les cookies de session.
- Empêche l'escalade de privilèges (spoofing du `group_type` en administrateur).

### Optimisation Administrative (`f2937c8`)
- Forçage de la timezone sur `Africa/Casablanca` pour éviter les décalages Serveur/Client.
- Ajout de l'export CSV des réservations pour la gestion administrative.
- Nettoyage automatique des tokens d'authentification expirés.

---

## 📧 Phase 4 : Fiabilité Email et Production (22 Avril 2024)

### Migration Brevo et Retour Gmail (`474aa35` - `c727507`)
- Essai de migration vers Brevo SMTP pour augmenter les quotas.
- Retour rapide vers Gmail SMTP avec **Mots de passe d'application** suite aux restrictions de Brevo sur les domaines personnalisés.

### Délivrabilité Outlook (`03394f2`)
- Correction critique pour les destinataires Outlook.
- Ajout des headers standards : `Message-ID`, `Date`, `Reply-To`.
- Implémentation de `multipart/alternative` avec version texte brut pour éviter les filtres anti-spam agressifs de Microsoft.

---

## 🛠 Phase 5 : Demande de Matériel (Optionnel) (22 Avril 2024 - 21 Mai 2026)
- **Formulaire post-réservation** : Ajout d'une étape optionnelle permettant aux groupes de lister le matériel nécessaire (outils, multimètres, etc.).
- **Persistance en base de données** : Nouvelle table `material_requests` liée directement à l'identifiant de la réservation.
- **Intégration administrative** : Affichage clair des demandes de matériel au sein du panneau d'administration pour chaque réservation.

---

## 🔒 Phase 6 : Résilience Base de Données & Diagnostic Veille (21 Mai 2026)
- **Gestionnaire centralisé `handle_db_error`** : Création d'un utilitaire interceptant toutes les exceptions de base de données.
- **Diagnostic automatique (Erreur 521)** : Détection des erreurs de veille des instances gratuites de Supabase (Cloudflare 521 / DNS Resolution issues).
- **Alerte UI Streamlit premium** : Affichage d'une boîte d'information esthétique en cas d'indisponibilité, expliquant à l'administrateur la procédure exacte pour restaurer le service depuis le Dashboard Supabase.
- **Robustesse globale (Zéro-Crash)** : Encapsulation de toutes les requêtes (`select`, `insert`, `delete`, `upsert`) dans des blocs `try-except` avec fallbacks de sécurité (DataFrames vides ou indicateurs d'erreur), éliminant les tracebacks utilisateur.
- **Maintien d'activité automatisé** : Déploiement d'un workflow GitHub Actions (`keep_alive.yml`) s'exécutant toutes les 72 heures pour pinguer l'API et empêcher la mise en veille automatique de Supabase.

---

## 📧 Phase 7 : Notifications de Réservation & Fiabilité SMTP (7 Juin 2026)
- **Notification d'administration** : Envoi automatique d'un email de notification à `anwar.mounir@centrale-casablanca.ma` à chaque nouvelle réservation confirmée (pour les réservations utilisateurs et administrateur).
- **Auto-détection de l'hôte SMTP** : Amélioration de la fonction d'envoi d'emails pour détecter dynamiquement l'hôte SMTP approprié (ex. `smtp-relay.brevo.com` pour les identifiants Brevo) sans dépendre exclusivement d'un hôte Gmail codé en dur.
- **Accélération du Keep-Alive** : Ajustement de la fréquence du workflow GitHub Actions à 12 heures (au lieu de 72 heures) afin d'assurer une activité régulière et d'éviter les veilles automatiques de la base de données.



