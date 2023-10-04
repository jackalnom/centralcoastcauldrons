import requests
import os
import logging



base_route = "http://127.0.0.1:3000"
headers = {'Access_token': f'{os.environ.get("API_KEY")}'}


def testconnection():
  url = base_route + "/"
  response = requests.get(url)
  assert response.status_code == 200, "Should return status code 200"


def testroutes():
  url = base_route + "/catalog/"
  response = requests.get(url)
  assert response.status_code == 200, "Should return status code 200"
  assert isinstance(response.json(), list)

  

def testauth():
  url = base_route + "/audit/inventory"
  response = requests.get(url, headers=headers)
  logging.info(f'response is {response.text}')
  assert response.status_code == 200, "Should return status code 200"
 
 