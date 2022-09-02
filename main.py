import csv
import requests
import yaml


csvfile = open('results.csv', 'w')
header = ['url', 'status']

writer = csv.writer(csvfile)
writer.writerow(header)

with open('parcours-hybridation/arts-lettres-et-langues/36-licence-mention-humanites.yml', 'r') as f:
    doc = yaml.safe_load(f)

    for element in doc["years"] :
        for ue in element["ue"] :
            for resource in ue["resources"] :
                try:
                    r = requests.get(resource["url"])
                    if r.status_code != 200:
                        writer.writerow([resource["url"], r.status_code])
                except requests.ConnectionError:
                    print("failed to connect : ", resource["url"])
                    try:
                        r = requests.get(resource["url"], verify=False)
                        if r.status_code != 200:
                            writer.writerow([resource["url"], r.status_code])
                    except requests.ConnectionError:
                        writer.writerow([resource["url"], r.status_code])
