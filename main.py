import csv
import glob
import requests
import yaml
import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

TIMEOUT_DELAY = 20

filepath = os.getenv('DIRECTORY')
csvfile = open('results.csv', 'w')
header = ['url', 'status']
unique_urls = []

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
                                                writer.writerow([url], e)
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
print("nombre d'URL :", len(unique_urls))
