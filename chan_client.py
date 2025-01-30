# 4chan API client that has minimal functionality to collect data

import logging
import requests

# logger setup
logger = logging.getLogger("4chan client")
logger.propagate = False
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)
logger.addHandler(sh)

fh = logging.FileHandler("crawler.log")
fh.setLevel(logging.INFO)  
fh.setFormatter(formatter)
logger.addHandler(fh)

class ChanClient:
    API_BASE = "http://a.4cdn.org"

    """
    Get json for a given thread
    """
    def get_thread(self, board, thread_number):
        # Sample API call: http://a.4cdn.org/pol/thread/124205675.json
        # make an http request to the url
        request_pieces = [board, "thread", f"{thread_number}.json"]
        api_call = self.build_request(request_pieces)
        return self.execute_request(api_call)

    """
    Get catalog json for a given board
    """
    def get_catalog(self, board):
        request_pieces = [board, "catalog.json"]
        api_call = self.build_request(request_pieces)
        return self.execute_request(api_call)

    """
    Build a request from pieces
    """
    def build_request(self, request_pieces):
        api_call = "/".join([self.API_BASE] + request_pieces)
        return api_call

    """
    This executes an HTTP request and returns json
    """
    def execute_request(self, api_call):
        try:
            resp = requests.get(api_call)
            if resp.status_code == 200:
                json_data = resp.json()  # Successfully retrieved JSON data
                logger.info(f"Successfully retrieved data from: {api_call}")
                return json_data
            else:
                logger.error(f"Failed request with status code: {resp.status_code}")
                return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None

if __name__ == "__main__":
    client = ChanClient()

    catalog = client.get_catalog("pol")
    print(f"Catalog: {catalog}")
    
    thread_data = client.get_thread("pol", 124205675)
    print(thread_data)
