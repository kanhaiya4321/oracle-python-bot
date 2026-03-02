import requests
import json
import logging

class BinanceAPI:
    def __init__(self, portfolio_id):
        self.url = "https://www.binance.com/bapi/futures/v1/friendly/future/copy-trade/lead-portfolio/order-history"
        self.portfolio_id = portfolio_id
        
        # Taking headers from the provided cURL request
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'bnc-location': '',
            'bnc-time-zone': 'Asia/Calcutta',
            'bnc-uuid': '73cb286b-028b-4f78-bb46-1a0cd982250b',
            'clienttype': 'web',
            'content-type': 'application/json',
            'csrftoken': 'd41d8cd98f00b204e9800998ecf8427e',
            'device-info': 'eyJzY3JlZW5fcmVzb2x1dGlvbiI6IjkwMCwxNDQwIiwiYXZhaWxhYmxlX3NjcmVlbl9yZXNvbHV0aW9uIjoiODY5LDE0NDAiLCJzeXN0ZW1fdmVyc2lvbiI6Ik1hYyBPUyAxMC4xNS43IiwiYnJhbmRfbW9kZWwiOiJ1bmtub3duIiwic3lzdGVtX2xhbmciOiJlbi1HQiIsInRpbWV6b25lIjoiR01UKzA1OjMwIiwidGltZXpvbmVPZmZzZXQiOi0zMzAsInVzZXJfYWdlbnQiOiJNb3ppbGxhLzUuMCAoTWFjaW50b3NoOyBJbnRlbCBNYWMgT1MgWCAxMF8xNV83KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTQzLjAuMC4wIFNhZmFyaS81MzcuMzYiLCJsaXN0X3BsdWdpbiI6IlBERiBWaWV3ZXIsQ2hyb21lIFBERiBWaWV3ZXIsQ2hyb21pdW0gUERGIFZpZXdlcixNaWNyb3NvZnQgRWRnZSBQREYgVmlld2VyLFdlYktpdCBidWlsdC1pbiBQREYiLCJjYW52YXNfY29kZSI6IjY3N2Y0M2JiIiwid2ViZ2xfdmVuZG9yIjoiR29vZ2xlIEluYy4gKEFwcGxlKSIsIndlYmdsX3JlbmRlcmVyIjoiQU5HTEUgKEFwcGxlLCBBTkdMRSBNZXRhbCBSZW5kZXJlcjogQXBwbGUgTTEsIFVuc3BlY2lmaWVkIFZlcnNpb24pIiwiYXVkaW8iOiIxMjQuMDQzNDgxNTU4NzY1MDUiLCJwbGF0Zm9ybSI6Ik1hY0ludGVsIiwid2ViX3RpbWV6b25lIjoiQXNpYS9DYWxjdXR0YSIsImRldmljZV9uYW1lIjoiQ2hyb21lIFYxNDMuMC4wLjAgKE1hYyBPUykiLCJmaW5nZXJwcmludCI6IjQwMGE3ZmU1ZWE3MGI5Zjk4Y2Y2ZGMxYmNlM2QzNjE2IiwiZGV2aWNlX2lkIjoiIiwicmVsYXRlZF9kZXZpY2VfaWRzIjoiIn0=',
            'dnt': '1',
            'fvideo-id': '330a1341c558aa7192531f61f3969fcfee008be2',
            'fvideo-token': 'gFjajBOEDRDDmONZzsOvDWATrgkd3ATSE3i1KaArg9FKITTlI6cqbGMiKcYBP6b/LXYIEGuTr4zAZbVMxFE5QQLWeek77xfcY8x9dzfJFFhPSLzY+2zsnqRJed7ySpMWHsvM96j8CA7rGDYneRlh+kSxURXOC3BmUS7l0lpXQWukF+q6dg5LfcDkMAiD3Ffog=7c',
            'lang': 'en-IN',
            'origin': 'https://www.binance.com',
            'priority': 'u=1, i',
            'referer': 'https://www.binance.com/en-IN/copy-trading/lead-details/4649626508338132480?timeRange=30D&isSmartFilter=true',
            'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'x-passthrough-token': '',
            'x-trace-id': 'b14a4296-ebb0-44f5-9a2e-dce3ab15d1fb',
            'x-ui-request-trace': 'b14a4296-ebb0-44f5-9a2e-dce3ab15d1fb',
            'cookie': '__BNC_USER_DEVICE_ID__={"d4c7dc88112d77ab59721b9b7f28f56b":{"date":1738783936585,"value":""}}; aws-waf-token=caf66d40-c7c9-4176-8592-fe773eca1fff:BQoAh1Q33ncYAAAA:G7nyDH7wSz8uIpkid/eYt2JkTACrL+Oao4MnIYAfnvxyYjxxWD37nsZjN57mt+3v1a0LbP9HaVVp12dyrm3V45YkDabBkcoYamGpZcpF7RjIVWLwTFOQGl4vu1I0hYs+p8wJzbf+2L72glq1Jdo4Qz1ltaVlqsxQKzz1Xc4WjlalFhXgO1e3kthgzC6m2asYASdPqnp8HQ==; theme=dark; bnc-uuid=73cb286b-028b-4f78-bb46-1a0cd982250b; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2219ca34d42622203-0d18eecaf953ed8-1c525631-1296000-19ca34d426326af%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTljYTM0ZDQyNjIyMjAzLTBkMThlZWNhZjk1M2VkOC0xYzUyNTYzMS0xMjk2MDAwLTE5Y2EzNGQ0MjYzMjZhZiJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%7D; BNC_FV_KEY=330a1341c558aa7192531f61f3969fcfee008be2; BNC_FV_KEY_T=101-kriOY8Q%2FYc8wRjZJzWzNCNu%2B%2B7Sg5H8ywXjIjTCQkEvQQNEAE9vkgulAB0yCn6YHzCzHBhfe5nOl%2FEYNZ%2B5q2g%3D%3D-yn2C28oznZ%2BeAE0tPe245Q%3D%3D-bc; BNC_FV_KEY_EXPIRE=1772287875862; OptanonAlertBoxClosed=2026-02-28T08:11:25.402Z; _gid=GA1.2.400057014.1772266285; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Feb+28+2026+13%3A54%3A24+GMT%2B0530+(India+Standard+Time)&version=202506.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=72eee3a4-269e-409e-a417-94cb675b33de&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1&intType=1&geolocation=IN%3BUP&AwaitingReconsent=false; _gat_UA-162512367-1=1; g_state={"i_l":0,"i_ll":1772267064602,"i_b":"83bGLj4q/7+mBZLhCjVlSmhPOcamHFqBJ6vUIbwEcAY","i_e":{"enable_itp_optimization":0}}; _ga_3WP50LGEEC=GS2.1.s1772266286$o1$g1$t1772267064$j60$l0$h0; _ga=GA1.1.946321045.1772266285'
        }

    def fetch_orders(self, start_time: int, end_time: int, page_size: int = 100):
        # We can configure the page size up as needed, keeping it at 100 for broader sweeps
        payload = {
            "portfolioId": self.portfolio_id,
            "startTime": start_time,
            "endTime": end_time,
            "pageSize": page_size
        }
        
        try:
            response = requests.post(self.url, headers=self.headers, data=json.dumps(payload))
            response.raise_for_status()
            data = response.json()
            
            if data.get("success") and "data" in data and "list" in data["data"]:
                return data["data"]["list"]
            else:
                logging.error(f"Failed to fetch data or non-success response: {data}")
                return []
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Error making request to Binance API: {e}")
            return []
