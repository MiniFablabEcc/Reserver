import pandas as pd
import json
import unicodedata

def clean_name(name):
    if pd.isna(name): return ""
    name = str(name).strip().lower()
    # remove accents
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    # replace spaces with nothing or hyphens? Usually central emails replace spaces with hyphens or squash them. 
    # Let's replace spaces in multi-part names with hyphens, which is a common french standard, 
    # OR maybe they squash them. For now, let's just replace spaces with hyphens as it's safe.
    name = name.replace(" ", "-").replace("'", "")
    return name

df = pd.read_excel('1A.xlsx', header=None)
header_row_idx = None
for idx, row in df.iterrows():
    row_vals = [str(x).strip() for x in row.values]
    if 'Equipe' in row_vals and 'Nom' in row_vals and 'Prénom' in row_vals:
        header_row_idx = idx
        break

df.columns = [str(x).strip() for x in df.iloc[header_row_idx].values]
df = df.iloc[header_row_idx+1:].reset_index(drop=True)
df['Equipe'] = df['Equipe'].ffill()

new_data = {}
for index, row in df.iterrows():
    equipe = row['Equipe']
    nom = row['Nom']
    prenom = row['Prénom']
    
    if pd.isna(equipe) or pd.isna(nom) or pd.isna(prenom):
        continue
        
    try:
        group_num = int(float(equipe))
        group_key = f"plbd{group_num}"
    except (ValueError, TypeError):
        continue
        
    nom_clean = clean_name(nom)
    prenom_clean = clean_name(prenom)
    if not nom_clean or not prenom_clean: continue
    
    email_str = f"{prenom_clean}.{nom_clean}@centrale-casablanca.ma"
    
    if group_key not in new_data:
        new_data[group_key] = set()
    new_data[group_key].add(email_str)

with open('plbd_emails.json', 'r') as f:
    existing_data = json.load(f)

# Flatten existing emails to easily check if someone is already in there
flat_existing = set()
for grp, emails in existing_data.items():
    for e in emails:
        flat_existing.add(e.strip().lower())

added_count = 0
for group_key, new_emails in new_data.items():
    if group_key not in existing_data:
        existing_data[group_key] = []
        
    for e in new_emails:
        if e not in flat_existing:
            existing_data[group_key].append(e)
            flat_existing.add(e)
            added_count += 1
            print(f"Added: {e} to {group_key}")

with open('plbd_emails.json', 'w') as f:
    json.dump(existing_data, f, indent=4)

print(f"\nMerge successful! Generated and added {added_count} missing emails based on names to plbd_emails.json")
