import requests
import hashlib
import time
import random
import re
import concurrent.futures
import colorama
from colorama import Fore
import os
colorama.init()
os.system('cls')

class yt:
    def __init__(self):
        def ui():
            os.system('cls')
            self.proxies = []
            try:
                with open('proxies.txt', 'r') as f:
                    self.proxies = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                pass
            print(f'''{Fore.LIGHTMAGENTA_EX}
               ┌─┐┬ ┬┌┐ ┌─┐┌─┐┬  ┬┬─┐
               └─┐│ │├┴┐└─┐├─┤└┐┌┘├┬┘
               └─┘└─┘└─┘└─┘┴ ┴ └┘ ┴└─{Fore.RESET}
            ''')
            self.mode = input(f'   {Fore.RESET}[ {Fore.LIGHTMAGENTA_EX}?{Fore.RESET} ] Option (sub/like): ').strip().lower()
            if self.mode not in ['sub', 'like']:
                print('Invalid mode.')
                ui()
        ui()
        self.channel_url = input(f'   {Fore.RESET}[ {Fore.LIGHTMAGENTA_EX}?{Fore.RESET} ] YouTube URL: ').strip()
        with open('refresh.txt', 'r') as f:
            self.cookies_list = [line.strip() for line in f if line.strip()]

        if self.mode == 'sub':
            self.channel_id = self.find_channel_id()

    def vid_id(self, url):
        match = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11})', url)
        if match:
            return match.group(1)
        print('Invalid video URL')
        exit()

    def getproxy(self):
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        if "@" in proxy:
            auth, host_port = proxy.split("@")
            user, password = auth.split(":")
            return {
                'http': f'http://{user}:{password}@{host_port}',
                'https': f'http://{user}:{password}@{host_port}',
            }
        else:
            return {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}',
            }


    def setup(self, raw):
        jar = {}
        for item in raw.split('; '):
            if '=' in item:
                key, val = item.split('=', 1)
                jar[key] = val
        return jar
    
    def fetch(self, raw_cookie):
        cookies = self.setup(raw_cookie)

        try:
            response = requests.get(
                "https://www.youtube.com/",
                headers={
                },
                cookies=cookies,
                proxies=self.getproxy(),
                timeout=10
            )
            html = response.text
    
            def extract(pattern, fallback=""):
                ma = re.search(pattern, html)
                return ma.group(1) if ma else fallback

            return {
                'clientVersion': extract(r'"INNERTUBE_CONTEXT_CLIENT_VERSION":"([^"]+)"'),
                'clientName': extract(r'"INNERTUBE_CONTEXT_CLIENT_NAME":(\d+)'),
                'visitorData': extract(r'"VISITOR_DATA":"([^"]+)"'),
                'clickTrackingParams': extract(r'"clickTrackingParams":"([^"]+)"'),
                'appInstallData': extract(r'"appInstallData":"([^"]+)"'),
                'coldConfigData': extract(r'"coldConfigData":"([^"]+)"'),
                'coldHashData': extract(r'"coldHashData":"([^"]+)"'),
                'hotHashData': extract(r'"hotHashData":"([^"]+)"'),
                'rolloutToken': cookies.get('__Secure-ROLLOUT_TOKEN', ''),
                'browserVersion': extract(r'"browserVersion":"([^"]+)"'),
                'deviceExperimentId': extract(r'"deviceExperimentId":"([^"]+)"'),
                'osName': extract(r'"osName":"([^"]+)"', 'Windows'),
                'osVersion': extract(r'"osVersion":"([^"]+)"', '10.0'),
                'platform': extract(r'"platform":"([^"]+)"', 'DESKTOP'),
                'clientFormFactor': extract(r'"clientFormFactor":"([^"]+)"', 'UNKNOWN_FORM_FACTOR'),
                'screenDensityFloat': extract(r'"screenDensityFloat":([0-9.]+)', '1.25'),
                'userInterfaceTheme': extract(r'"userInterfaceTheme":"([^"]+)"', 'USER_INTERFACE_THEME_LIGHT'),
            }  
        except:
            return {}


    def authorization(self, sapisid):
        t = int(time.time())
        raw = f'{t} {sapisid} https://www.youtube.com'
        return f'SAPISIDHASH {t}_{hashlib.sha1(raw.encode()).hexdigest()}'

    def find_channel_id(self):
        try:
            r = requests.get(self.channel_url, headers={'user-agent': 'Mozilla/5.0'}, proxies=self.getproxy(), timeout=5)
            m = re.search(r'channel_id=([\w-]{24})', r.text)
            if m:
                print(f'\n   {Fore.RESET}[ {Fore.LIGHTMAGENTA_EX}- {Fore.RESET}] Found channel ID: {Fore.LIGHTMAGENTA_EX}{m.group(1)}{Fore.RESET}')
                return m.group(1)

            a = re.search(r'rssUrl.*?channel_id=([\w-]{24})', r.text)
            if a:
                print(f'\n   {Fore.RESET}[ {Fore.LIGHTMAGENTA_EX}- {Fore.RESET}] Found channel ID: {Fore.LIGHTMAGENTA_EX}{a.group(1)}{Fore.RESET}')
                return a.group(1)
        except Exception as e:
            print(e)

        print('Failed to find channel id')
        exit()

    def test(self, args):
        raw, authuser = args
        cookies = self.setup(raw)
        auth = self.authorization(cookies.get('SAPISID'))

        try:
            res = requests.post(
                'https://www.youtube.com/youtubei/v1/notification/modify_channel_preference',
                headers={
                    'authorization': auth,
                    'x-goog-authuser': str(authuser),
                    'x-origin': "https://www.youtube.com",
                    'x-youtube-client-name': '1',
                    'x-youtube-client-version': '2.20250324.09.00',
                    'user-agent': 'Mozilla/5.0',
                    'content-type': 'application/json',
                    'origin': "https://www.youtube.com",
                    'referer': 'https://www.youtube.com/',
                },
                cookies=cookies,
                timeout=5,
                json={
                    "channelId": "",
                    "pref": 2,
                    "context": {
                        "client": {
                            "clientName": "WEB",
                            "clientVersion": "2.20250324.09.00"
                        }
                    }
                }
            )
            if res.status_code in (400, 500):
                return (raw, authuser)
        except:
            pass
        return None

    def subreq(self, raw, authuser):
        cookies = self.setup(raw)
        auth = self.authorization(cookies.get('SAPISID'))
        ctx = self.fetch(raw)
        try:
            res = requests.post(
                'https://www.youtube.com/youtubei/v1/subscription/subscribe',
                headers={
                    'accept': '*/*',
                    'accept-language': 'en-US,en;q=0.9',
                    'authorization': auth,
                    'content-type': 'application/json',
                    'origin': 'https://www.youtube.com',
                    'priority': 'u=1, i',
                    'referer': self.channel_url,
                    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                    'sec-ch-ua-arch': '"x86"',
                    'sec-ch-ua-bitness': '"64"',
                    'sec-ch-ua-form-factors': '"Desktop"',
                    'sec-ch-ua-full-version': '"134.0.6998.118"',
                    'sec-ch-ua-full-version-list': '"Chromium";v="134.0.6998.118", "Not:A-Brand";v="24.0.0.0", "Google Chrome";v="134.0.6998.118"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-model': '""',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-ch-ua-platform-version': '"15.0.0"',
                    'sec-ch-ua-wow64': '?0',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'same-origin',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                    'x-goog-authuser':  str(authuser),
                    'x-goog-visitor-id': ctx.get('visitorData'),
                    'x-origin': 'https://www.youtube.com',
                    'x-youtube-bootstrap-logged-in': 'true',
                    'x-youtube-client-name': '1',
                    'x-youtube-client-version': '2.20250324.09.00',
                },
                cookies=cookies,
                timeout=5,
                proxies=self.getproxy(),
                params={'prettyPrint': 'false'},
                json={
                    'context': {
                        'client': {
                            'hl': 'en',
                            'gl': 'US',
                            'remoteHost': '',
                            'deviceMake': '',
                            'deviceModel': '',
                            'visitorData': ctx.get('visitorData'),
                            'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36,gzip(gfe)',
                            'clientName': ctx.get('clientName'),
                            'clientVersion': ctx.get('clientVersion'),
                            'osName': 'Windows',
                            'osVersion': ctx.get('osName'),
                            'originalUrl': self.channel_url,
                            'screenPixelDensity': 1,
                            'platform': ctx.get('platform'),
                            'clientFormFactor': ctx.get('clientFormFactor'),
                            'configInfo': {
                                'appInstallData': ctx.get('appInstallData'),
                                'coldConfigData': ctx.get('coldConfigData'),
                                'coldHashData': ctx.get('coldHashData'),
                                'hotHashData': ctx.get('hotHashData'),
                            },
                            'screenDensityFloat': float(ctx.get('screenDensityFloat')),
                            'userInterfaceTheme': ctx.get('userInterfaceTheme'),
                            'timeZone': 'America/New_York',
                            'browserName': 'Chrome',
                            'browserVersion': ctx.get('browserVersion'),
                            'acceptHeader': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                            'deviceExperimentId': ctx.get('deviceExperimentId'), 
                            'rolloutToken': ctx.get('rolloutToken'),
                            'screenWidthPoints': random.randint(700, 1920),
                            'screenHeightPoints': random.randint(600, 1080),
                            'utcOffsetMinutes': random.choice([-720, -480, -300, -240, -180, 0, 60, 330, 480, 540, 600, 660, 720]),
                            'connectionType': 'CONN_CELLULAR_4G',
                            'memoryTotalKbytes': '8000000',
                            'mainAppWebInfo': {
                                'graftUrl': self.channel_url,
                                'pwaInstallabilityStatus': 'PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED',
                                'webDisplayMode': 'WEB_DISPLAY_MODE_BROWSER',
                                'isWebNativeShareAvailable': True,
                            },
                        },
                        'user': {
                            'lockedSafetyMode': False,
                        },
                        'request': {
                            'useSsl': True,
                            'internalExperimentFlags': [],
                            'consistencyTokenJars': [],
                        },
                        'clientScreenNonce': 'CZXFJAaJBq43ru6L', 
                        'clickTracking': { 
                            'clickTrackingParams': ctx.get('clickTrackingParams'),
                        },
                        'adSignalsInfo': {
                                     'params': [                      
                                         {'key': 'dt', 'value': str(int(time.time() * 1000))},
                                         {'key': 'flash', 'value': '0'},
                                         {'key': 'frm', 'value': '0'},
                                         {'key': 'u_tz', 'value': '-240'},
                                         {'key': 'u_his', 'value': str(__import__('random').randint(3, 10))},
                                         {'key': 'u_h', 'value': '864'},
                                         {'key': 'u_w', 'value': '1536'},
                                         {'key': 'u_ah', 'value': '816'},
                                         {'key': 'u_aw', 'value': '1536'},
                                         {'key': 'u_cd', 'value': '24'},
                                         {'key': 'bc', 'value': '31'},
                                         {'key': 'bih', 'value': str(__import__('random').randint(600, 1000))},
                                         {'key': 'biw', 'value': str(__import__('random').randint(700, 1600))},
                                         {'key': 'brdim', 'value': f"0,0,0,0,1536,0,1536,816," + str(__import__('random').randint(700, 1600)) + "," + str(__import__('random').randint(600, 1000))},
                                         {'key': 'vis', 'value': '1'},
                                         {'key': 'wgl', 'value': 'true'},
                                         {'key': 'ca_type', 'value': 'image'}

                            ],
                            'bid': 'ANyPxKr2jRgzs-X_ikbBYYBYuORP6qTBtrM3Y8qbWQqONoI7DFIExOxr5lSE8Yn2NlqBfnF-A8VtkKWDyjWmyPfSkNEQnAqb8A',
                        },
                    },
                    'channelIds': [
                        [self.channel_id],
                    ],
                    'params': 'EgIIAhgA',
                },
            )
            c = re.search(r'SID=([^;]+)', raw)
            x = c.group(1)[:20] + "..." 
            print(f'   [ {Fore.LIGHTMAGENTA_EX}\{Fore.RESET} ] {Fore.LIGHTMAGENTA_EX}{res.status_code}{Fore.RESET} | Cookie: {Fore.LIGHTMAGENTA_EX}{x}{Fore.RESET} | {Fore.LIGHTMAGENTA_EX}{authuser}{Fore.RESET}')
        except Exception as e:
            print(f'[{authuser}] Error: {e}')

    def lparam(self, video_id):
        response = requests.get(f"https://www.youtube.com/watch?v={video_id}", proxies=self.getproxy(),)
        i = re.search(r'"likeParams":"(.*?)"', response.text)

        if i:
            x = i.group(1)
            return x
        else:
            return None

    def likereq(self, raw, authuser, video_id):
        cookies = self.setup(raw)
        auth = self.authorization(cookies.get('SAPISID'))
        like_param = self.lparam(video_id)
        ctx = self.fetch(raw)
        try:
            res = requests.post(
                'https://www.youtube.com/youtubei/v1/like/like',
                headers={
                    'accept': '*/*',
                    'accept-language': 'en-US,en;q=0.9',
                    'authorization': auth,
                    'content-type': 'application/json',
                    'origin': 'https://www.youtube.com',
                    'priority': 'u=1, i',
                    'referer': f'https://www.youtube.com/watch?v={video_id}',
                    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                    'sec-ch-ua-arch': '"x86"',
                    'sec-ch-ua-bitness': '"64"',
                    'sec-ch-ua-form-factors': '"Desktop"',
                    'sec-ch-ua-full-version': '"134.0.6998.166"',
                    'sec-ch-ua-full-version-list': '"Chromium";v="134.0.6998.166", "Not:A-Brand";v="24.0.0.0", "Google Chrome";v="134.0.6998.166"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-model': '""',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-ch-ua-platform-version': '"15.0.0"',
                    'sec-ch-ua-wow64': '?0',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'same-origin',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                    'x-goog-authuser': str(authuser),
                    'x-goog-visitor-id': ctx.get('visitorData'),
                    'x-origin': 'https://www.youtube.com',
                    'x-youtube-bootstrap-logged-in': 'true',
                    'x-youtube-client-name': '1',
                    'x-youtube-client-version': '2.20250324.09.00',
                },
                cookies=cookies,
                timeout=5,
                proxies=self.getproxy(),
                params={'prettyPrint': 'false'},
                json = {
                    'context': {
                        'client': {    
                            'hl': 'en',
                            'gl': 'US',
                            'remoteHost': '',
                            'deviceMake': '',
                            'deviceModel': '',
                            'visitorData': ctx.get('visitorData'),
                            'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36,gzip(gfe)',
                            'clientName': ctx.get('clientName'),
                            'clientVersion': ctx.get('clientVersion'),
                            'osName': 'Windows',
                            'osVersion': ctx.get('osName'),
                            'originalUrl': self.channel_url,
                            'screenPixelDensity': 1,
                            'platform': ctx.get('platform'),
                            'clientFormFactor': ctx.get('clientFormFactor'),
                            'configInfo': {
                                'appInstallData': ctx.get('appInstallData'),
                                'coldConfigData': ctx.get('coldConfigData'),
                                'coldHashData': ctx.get('coldHashData'),
                                'hotHashData': ctx.get('hotHashData'),
                            },
                            'screenDensityFloat': float(ctx.get('screenDensityFloat')),
                            'userInterfaceTheme': ctx.get('userInterfaceTheme'),
                            'timeZone': 'America/New_York',
                            'browserName': 'Chrome',
                            'browserVersion': ctx.get('browserVersion'),
                            'acceptHeader': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                            'deviceExperimentId': ctx.get('deviceExperimentId'), 
                            'rolloutToken': ctx.get('rolloutToken'),
                            'screenWidthPoints': random.randint(700, 1920),
                            'screenHeightPoints': random.randint(600, 1080),
                            'utcOffsetMinutes': random.choice([-720, -480, -300, -240, -180, 0, 60, 330, 480, 540, 600, 660, 720]),
                            'connectionType': 'CONN_CELLULAR_4G',
                            'memoryTotalKbytes': '8000000',
                            'mainAppWebInfo': {
                                'graftUrl': f'https://www.youtube.com/watch?v={video_id}',
                                'pwaInstallabilityStatus': 'PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED',
                                'webDisplayMode': 'WEB_DISPLAY_MODE_BROWSER',
                                'isWebNativeShareAvailable': True,
                            },
                        },
                        'user': {
                            'lockedSafetyMode': False,
                        },
                        'request': {
                            'useSsl': True,
                            'internalExperimentFlags': [],
                            'consistencyTokenJars': [],
                        },
                        'clickTracking': {
                            'clickTrackingParams': ctx.get('clickTrackingParams'),
                        },
                        'adSignalsInfo': {
                                     'params': [                      
                                         {'key': 'dt', 'value': str(int(time.time() * 1000))},
                                         {'key': 'flash', 'value': '0'},
                                         {'key': 'frm', 'value': '0'},
                                         {'key': 'u_tz', 'value': '-240'},
                                         {'key': 'u_his', 'value': str(__import__('random').randint(3, 10))},
                                         {'key': 'u_h', 'value': '864'},
                                         {'key': 'u_w', 'value': '1536'},
                                         {'key': 'u_ah', 'value': '816'},
                                         {'key': 'u_aw', 'value': '1536'},
                                         {'key': 'u_cd', 'value': '24'},
                                         {'key': 'bc', 'value': '31'},
                                         {'key': 'bih', 'value': str(__import__('random').randint(600, 1000))},
                                         {'key': 'biw', 'value': str(__import__('random').randint(700, 1600))},
                                         {'key': 'brdim', 'value': f"0,0,0,0,1536,0,1536,816," + str(__import__('random').randint(700, 1600)) + "," + str(__import__('random').randint(600, 1000))},
                                         {'key': 'vis', 'value': '1'},
                                         {'key': 'wgl', 'value': 'true'},
                                         {'key': 'ca_type', 'value': 'image'}
                            ],
                            'bid': 'ANyPxKqa71-j5kGBl9vqIZPfCqmU_DtNcUHEz8R_luK-0fmQMoGniHzhzXlYnQYB3p8kqcI_gE3FXlKY1R8OCKkUKqgsBaaJ5w',
                        },
                    },
                    'target': {
                        'videoId': video_id,
                    },
                    'params': like_param,
                }

            )
            # print(res.json())
            sid = re.search(r'SID=([^;]+)', raw)
            tag = sid.group(1)[:20] + "..." 
            print(f'   [ {Fore.LIGHTMAGENTA_EX}+{Fore.RESET} ] Like | {Fore.LIGHTMAGENTA_EX}{res.status_code}{Fore.RESET} | Cookie: {Fore.LIGHTMAGENTA_EX}{tag}{Fore.RESET} | {Fore.LIGHTMAGENTA_EX}{authuser}{Fore.RESET}')
        except Exception as e:
            print(f'[Like:{authuser}] Error: {e}')

    def run(self):
        print(f'\n   {Fore.RESET}[ {Fore.LIGHTMAGENTA_EX}-{Fore.RESET} ] Checking all cookies for working accounts\n')

        args = [(cookie, i) for cookie in self.cookies_list for i in range(10)]
        acc = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(self.test, args))

        for r in results:
            if r:
                acc.append(r)

        if not acc:
            print(f'   {Fore.RESET}[ {Fore.LIGHTMAGENTA_EX}- {Fore.RESET}] No valid cookies found')
            return

        print(f'   {Fore.RESET}[ {Fore.LIGHTMAGENTA_EX}\\{Fore.RESET} ] Found {Fore.LIGHTMAGENTA_EX}{len(acc)}{Fore.RESET} Accounts in Cookies...\n')

        if self.mode == 'sub':
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                for raw, authuser in acc:
                    executor.submit(self.subreq, raw, authuser)

        elif self.mode == 'like':
            video_id = self.vid_id(self.channel_url)
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                for raw, authuser in acc:
                    executor.submit(self.likereq, raw, authuser, video_id)


if __name__ == "__main__":
    yt().run()
