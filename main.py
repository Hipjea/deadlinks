import csv
import glob
import requests
import yaml
import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

filepath = os.getenv('DIRECTORY')
csvfile = open('results.csv', 'w')
header = ['status', 'url']

structure = ['years', 'ue', 'resources', 'url']

# Write the CSV headers
writer = csv.writer(csvfile)
writer.writerow(header)

# Parse the YAML files
for file in glob.glob(f'{filepath}/**/*.yml', recursive=True):
    with open(file, 'r') as f:
        doc = yaml.safe_load(f)

        if doc.get('years'):
            try:
                for element in doc[structure[0]]:
                    for ue in element[structure[1]]:
                        if ue.get(structure[2]):
                            for resource in ue[structure[2]]:
                                try:
                                    url = resource[structure[-1]]
                                    try:
                                        r = requests.get(url, timeout=20)
                                    except requests.exceptions.RequestException as e:
                                        print(f"Timeout -> {url}")
                                    print(f"URL: {url}")
                                    if r.status_code != 200:
                                        writer.writerow([r.status_code, url])
                                except requests.ConnectionError:
                                    try:
                                        r = requests.get(url, verify=False, timeout=20)
                                    except requests.exceptions.RequestException as e:
                                        print(f"Timeout -> {url}")
                                        writer.writerow([r.status_code, url])
                                    if r.status_code != 200:
                                        writer.writerow([r.status_code, url])
            except BaseException as err:
                print(f"Unexpected {err=}, {type(err)=}")
                raise

csvfile.close()
