import csv

FAMILIES_DATA_FILE = 'family.csv'

def read_family_data():
    try:
        with open(FAMILIES_DATA_FILE, 'r', newline='', encoding='utf-8') as file:
            return list(csv.DictReader(file))
    except FileNotFoundError:
        return []

def write_family_data(families):
    with open(FAMILIES_DATA_FILE, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['husband', 'wife', 'wedding_date']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(families)
