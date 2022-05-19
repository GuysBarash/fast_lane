import requests
import json
import re


url = r'https://fastlane.co.il/PageMethodsService.asmx/GetCurrentPrice'
response = requests.post(url)
pattern = r'<string[^>]*>(.*?)</string>'
response_str = re.search(pattern, response.text).group(1)
json_data = json.loads(response_str)
price = float(json_data['Price'])

