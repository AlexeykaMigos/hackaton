import pandas as pd
import json
from datetime import datetime, date

input_file = 'itemdata.xlsx'
output_file = 'items.json'

df = pd.read_excel(input_file, sheet_name=0, parse_dates=False)

df.columns = df.columns.str.strip().str.replace(' ', '_')

def make_serializable(val):
    if pd.isna(val):
        return None
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    if hasattr(val, 'item'): 
        return val.item()
    return val

records = []
for _, row in df.iterrows():
    clean_row = {}
    for key, val in row.items():
        clean_row[key] = make_serializable(val)
    records.append(clean_row)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=4)

print(f"✅ Успешно обработано {len(records)} записей. Результат в файле: {output_file}")