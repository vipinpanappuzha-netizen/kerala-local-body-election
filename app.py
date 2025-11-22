from flask import Flask, jsonify, request
import requests
import csv
import io
from datetime import datetime

app = Flask(__name__)

# Google Sheets-ൻ്റെ CSV Export URL.
CSV_URL = "https://docs.google.com/spreadsheets/d/1n2i4ExiyLtIT_ZM6-RwN0g0IRg9iUkM80661S24fQJ8/export?format=csv&gid=764343976"

def fetch_and_process_data():
    """Google Sheet-ൽ നിന്ന് ഡാറ്റാ ഫെച്ച് ചെയ്ത് JSON list ആയി നൽകുന്നു."""
    try:
        # 1. Google Sheet-ൽ നിന്ന് ഡാറ്റ ഡൗൺലോഡ് ചെയ്യുന്നു
        response = requests.get(CSV_URL)
        response.raise_for_status() # HTTP പിശകുകൾ ഒഴിവാക്കുന്നു

        # 2. CSV ഡാറ്റ സ്ട്രിംഗ് രൂപത്തിൽ എടുക്കുന്നു
        csv_data = response.content.decode('utf-8')
        
        # 3. CSV ഡാറ്റ വായിക്കുന്നു
        csv_file = io.StringIO(csv_data)
        lines = csv_file.readlines()
        if not lines:
             return []
             
        # 4. ഹെഡറുകൾ തിരുത്തി എഴുതുന്നു (Fixing Headers)
        new_headers = ['BODY', 'LDF', 'UDF', 'NDA', 'OTH'] 
        modified_data = [','.join(new_headers)] 
        
        # ഡാറ്റ വരികൾ ചേർക്കുന്നു
        for line in lines[1:]: # Original header line ഒഴിവാക്കുന്നു
            row_data = line.strip().split(',')
            # Google Sheet ക്രമം: [Body, Total, LDF, UDF, NDA, OTH]
            if len(row_data) >= 6:
                processed_row = [
                    row_data[0], # BODY
                    row_data[2], # LDF (Column 3)
                    row_data[3], # UDF (Column 4)
                    row_data[4], # NDA (Column 5)
                    row_data[5]  # OTH (Column 6)
                ].join(',')
                modified_data.append(processed_row)
            
        # 5. JSON list ഉണ്ടാക്കുന്നു
        election_results = []
        
        # പുതിയ CSV ഡാറ്റ ഒരു StringIO റീഡറിലേക്ക് നൽകുന്നു
        fixed_csv_file = io.StringIO('\n'.join(modified_data))
        reader = csv.DictReader(fixed_csv_file)

        for row in reader:
            if not any(row.values()): continue 
            
            record = {}
            record['BODY'] = row.get('BODY', 'N/A').upper()
            record['LDF']  = int(row.get('LDF', 0))
            record['UDF']  = int(row.get('UDF', 0))
            record['NDA']  = int(row.get('NDA', 0))
            record['OTH']  = int(row.get('OTH', 0))
            
            election_results.append(record)
            
        return election_results
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        # ഈ API-യുടെ ഔട്ട്പുട്ട് കൃത്യമായ JSON ആയിരിക്കണം
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

@app.route('/api/election-results', methods=['GET'])
def get_election_results():
    """
    JSON API Endpoint.
    CMS-ൽ CORS പ്രശ്നമില്ലാതെ പ്രവർത്തിക്കാൻ CORS ഹെഡറുകൾ ചേർക്കുന്നു.
    """
    data = fetch_and_process_data()

    # --- CORS Headers ചേർക്കുന്നു ---
    response = jsonify(data)
    # ഏത് ഡൊമൈനിനും ഈ API ഉപയോഗിക്കാൻ അനുവാദം നൽകുന്നു
    response.headers.add('Access-Control-Allow-Origin', '*') 
    # കാഷിംഗ് ഒഴിവാക്കാൻ
    response.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')
    response.headers.add('Pragma', 'no-cache')
    response.headers.add('Expires', '0')

    return response

if __name__ == '__main__':
    # Cloud Run/Gunicorn ഉപയോഗിക്കുമ്പോൾ ഇത് പ്രവർത്തിക്കില്ല. 
    # ലോക്കൽ ടെസ്റ്റിംഗിനായി മാത്രം:
    app.run(debug=True, host='0.0.0.0', port=5000)