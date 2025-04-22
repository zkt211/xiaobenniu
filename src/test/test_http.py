
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from network.http_client import HttpClient

def testhttp():
    client = HttpClient(timeout = 30)
    response = client.get(
        url="https://jsonplaceholder.typicode.com/posts/1",
        headers={"Accept": "application/json"}
        )
    if response.status_code == 200:
        print(response.body)
    else:
        print(response.exception)
    client.close()
if __name__ == "__main__" :
    testhttp()
