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

# Write the CSV headers
writer = csv.writer(csvfile)
writer.writerow(header)

# Parse the YAML files
for file in glob.glob(f'{filepath}/**/*.yml', recursive=True):
    with open(file, 'r') as f:
        doc = yaml.safe_load(f)

        if doc.get('years'):
            try:
                for element in doc["years"]:
                    for ue in element["ue"]:
                        for resource in ue["resources"]:
                            try:
                                r = requests.get(resource["url"])
                                if r.status_code != 200:
                                    writer.writerow([r.status_code, resource["url"]])
                            except requests.ConnectionError:
                                print("failed to connect : ", resource["url"])
                                try:
                                    r = requests.get(resource["url"], verify=False)
                                    if r.status_code != 200:
                                        writer.writerow([r.status_code, resource["url"]])
                                except requests.ConnectionError:
                                    writer.writerow([r.status_code, resource["url"]])
            except BaseException as err:
                print(f"Unexpected {err=}, {type(err)=}")
                raise