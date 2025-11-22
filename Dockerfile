Google Cloud Run-ന് അനുയോജ്യമായ പൈത്തൺ ഇമേജ്

FROM python:3.11-slim

Working directory കണ്ടെയ്‌നറിനുള്ളിൽ സജ്ജമാക്കുന്നു

WORKDIR /app

ആവശ്യമായ ലൈബ്രറികൾ ഇൻസ്റ്റാൾ ചെയ്യുന്നു

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ആപ്ലിക്കേഷൻ കോഡ് കോപ്പി ചെയ്യുന്നു

COPY . .

Flask ആപ്പ് പ്രവർത്തിപ്പിക്കാൻ Gunicorn ഉപയോഗിക്കുന്നു

8080 പോർട്ടിൽ പ്രവർത്തിപ്പിക്കാൻ Cloud Run ആവശ്യപ്പെടുന്നു

ENV PORT 8080

ആപ്ലിക്കേഷൻ പ്രവർത്തിപ്പിക്കാനുള്ള കമാൻഡ്

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
