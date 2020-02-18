import requests
import csv

url = 'https://quality.data.gov.tw/dq_download_csv.php?nid=116285&md5_url=2150b333756e64325bdbc4a5fd45fad1'

web_data = requests.get(url)

sotreList = list(csv.reader(web_data.text.split('\n'), delimiter=','))