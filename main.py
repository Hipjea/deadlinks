import csv
import glob
import requests
import yaml
import os
import smtplib
from dotenv import load_dotenv
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

TIMEOUT_DELAY = 20

def has_smtp(user, password):
    if user and password:
        return True
    return False


filename = 'results.csv'
filepath = os.getenv('DIRECTORY')
csvfile = open(filename, 'w')
header = ['url', 'status']
unique_urls = []

smtp_user = os.getenv('SMTP_USER')
smtp_pass = os.getenv('SMTP_PASS')

# Write the CSV headers
writer = csv.writer(csvfile)
writer.writerow(header)

# Parse the YAML files
for file in glob.glob(f'{filepath}/**/*.yml', recursive=True):
    with open(file, 'r') as f:
        doc = yaml.safe_load(f)

        if doc.get('years'):
            try:
                for element in doc['years']:
                    if element.get('ue'):
                        for ue in element['ue']:
                            if ue.get('resources'):
                                for resource in ue['resources']:
                                    try:
                                        if resource.get('url'):
                                            url = resource['url']
                                            # Append the resource URL to unique_urls
                                            if not url in unique_urls:
                                                unique_urls.append(url)
                                                try:
                                                    r = requests.get(url, timeout=TIMEOUT_DELAY)
                                                    print(f"URL: {url}")
                                                    if r.status_code != 200:
                                                        writer.writerow([url, r.status_code])
                                                except requests.exceptions.RequestException as e:
                                                    print(f"Timeout -> {url}")
                                                    writer.writerow([url, e])
                                        else:
                                            writer.writerow([url, 'URL manquante'])
                                    except requests.ConnectionError:
                                        try:
                                            r = requests.get(url, verify=False, timeout=TIMEOUT_DELAY)
                                        except requests.exceptions.RequestException as e:
                                            print(f"Timeout -> {url}")
                                            writer.writerow([url, r.status_code])
                                        if r.status_code != 200:
                                            writer.writerow([url, r.status_code])
            except BaseException as err:
                print(f"Unexpected {err=}, {type(err)=}")
                raise

csvfile.close()
print("Nombre de liens parcourus :", len(unique_urls))

if has_smtp(smtp_user, smtp_pass):
    # Send the infos by email
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = os.getenv('SMTP_PORT')
    sender = os.getenv('SENDER')
    receiver = os.getenv('RECEIVER')

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        text = 'Détection des liens morts'
        message = MIMEMultipart()
        message['Subject'] = text
        message['From'] = sender
        message['To'] = receiver
        message.attach(MIMEText(text + '\n\n' + 'Nombre de liens parcourus : ' + str(len(unique_urls)) + '\n\n'))

        with open(filename, "rb") as file:
            part = MIMEApplication(file.read(), Name=filename)
            file.close()
        part['Content-Disposition'] = 'attachment; filename="%s"' % filename
        message.attach(part)

        server.login(smtp_user, smtp_pass)
        server.sendmail(sender, receiver, message.as_string())
        server.close()
