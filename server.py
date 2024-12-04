from flask import Flask, request, render_template, jsonify, flash
from datetime import datetime
app = Flask(__name__)
import time
from urllib.parse import urlparse, parse_qs
import requests
import os
import re

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_video_detail(item_id, language='zh-CN',  retry=5):
    url = "https://www.tiktok.com/player/api/v1/items"
    params = {
        "item_ids": item_id,
        "language": language,
        "aid": "1284",
        "app_name": "tiktok_web",
        "device_platform": "web_pc",
        "screen_width": "3440",
        "screen_height": "1440",
        "browser_language": language,
        "browser_platform": "MacIntel",
        "browser_name": "Mozilla",
        "browser_version": "5.0+(Macintosh;+Intel+Mac+OS+X+10_15_7)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/131.0.0.0+Safari/537.36",
        "browser_online": "true",
        "app_language": "en",
        "timezone_name": "Asia/Shanghai",
        "is_page_visible": "true",
        "focus_state": "true",
        "is_fullscreen": "false",
        "history_len": "1",
        "security_verification_aid": ""
    }

    for times in range(retry) :
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logging.error(f"cannont fetch_tiktok_video detail err: {e} item_id {item_id}")
    return None

    
def download_file(url, filename, retry=5):
    dir_path = os.path.dirname(filename)
    if  not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    for times in range(retry) :
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(filename, 'wb') as file:
                    file.write(response.content)
                return True
        except Exception as e:
            logging.error(f"download failed err: {e} url {url}")
    return False

def fetch_videos(product_id, page):
    try:
        # 使用函数
        url = "https://www.fastmoss.com/api/goods/v3/video"
        params = {
            'page':page,
            "product_id": product_id,
            'order': "2,2",
            'd_type': 0,
            "pagesize": 10,
            'is_promoted':-1,
            'date_type':28,
            "_time": 1733218606,
            "cnonce": 13228345
        }
        cookies = {
            'utm_south': 'google',
            'utm_id': 'ggproduct',
            '_src': '',
            'fp_visid': '452a4dbde35177302ee92f199b5b18dc',
            'fd_id': 'sH4tmUr5A7gpiW8yRe1qCnSwDGOocN6J',
            '_fbp': 'fb.1.1732692190061.123470053690447508',
            '_ga': 'GA1.1.1177071262.1732692199',
            '_tt_enable_cookie': '1',
            '_ttp': 'mNn9Fu0EZ072X7gphbWsyaMUg4n.tt.1',
            '_ss_s_uid': 'cea9581a6d29086e49cb688dbc0de6af',
            'utm_lang': 'zh',
            'Hm_lvt_6ada669245fc6950ae4a2c0a86931766': '1732692180,1732754778',
            'HMACCOUNT': '25778556149293FF',
            '_gcl_aw': 'GCL.1732841234.CjwKCAiAl4a6BhBqEiwAqvrqutdN-l76yWm3WXzSjKe8yN5-2e3csWm4GsvvO-jQ_CK17mHc5HCcgBoCjLYQAvD_BwE',
            'Hm_lpvt_6ada669245fc6950ae4a2c0a86931766': '1733274355',
            '_gcl_au': '1.1.109408670.1732692199.1378703260.1733280994.1733280994',
            'fd_tk_exp': '1734577124',
            'fd_tk': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzQ1NzcxMjQsInN1YiI6IjJlNTc0OTZiMDIxY2U5YWUxNzY0ZjE3OTBiY2NiNDQwIiwibmJmIjoxNzMzMjgxMTI0LCJhdWQiOnsidWlkIjo5MzY5NDgwLCJ1bmlvbmlkIjoiIiwibWNfb3BlbmlkIjoiIiwibmlja25hbWUiOiJGYXN0TW9zc-eUqOaItyIsInJlZ2lvbiI6IlVTIiwiY3JlYXRlZF9hdCI6MTczMzI4MTEyMywiY3JlYXRlZF9kYXRlIjoiMjAyNC0xMi0wNCIsImxvZ2luX3NvdXJjZSI6InBjIiwidmlzaXRvcl9pZCI6IjQ1MmE0ZGJkZTM1MTc3MzAyZWU5MmYxOTliNWIxOGRjIiwiaXAiOiI1LjM0LjIxNi4xMTgiLCJkb21haW4iOiJ3d3cuZmFzdG1vc3MuY29tIiwiZnBfdmlzaWQiOiJiODc2ZmUzN2E1MmU2ZDk1MjllMGViYTQ4ODA1NmExMiIsImNyZWF0ZV90aW1lIjoxNzMzMjgxMTI0fSwiaWF0IjoxNzMzMjgxMTI0LCJqdGkiOiIyZTU3NDk2YjAyMWNlOWFlMTc2NGYxNzkwYmNjYjQ0MCIsImlzcyI6Ind3dy5mYXN0bW9zcy5jb20iLCJzdGF0dXMiOjEsImRhdGEiOm51bGx9.swFc7YqNrrXMNDycKcakCo1Ayn0m78mt73CRYruH30M',
            'free_trial': 'FreeTrialFalse',
            'NEXT_LOCALE': 'zh',
            'region': 'Global',
            '_ga_J8P3E5KDGJ': 'GS1.1.1733280990.6.1.1733281214.60.0.1625003845',
            '_ga_GD8ST04HB5': 'GS1.1.1733280990.6.1.1733281214.60.0.244846493',
            '__stripe_mid': 'cc75a684-38d8-4efd-aca1-7d2e41959cd7484817',
            '__stripe_sid': '27771cfe-f894-4032-8651-705dc81e3173bd55c4',
            '_uetsid': '31d2edc0b05411ef859059c474939c77|d0gbhu|2|frf|0|1797',
            '_uetvid': '6ec88190ac9011ef9f65177761bd263a|yoa2vk|1733281245994|13|1|bat.bing.com/p/insights/c/k',
        }

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            # 'cookie': 'utm_south=google; utm_id=ggproduct; _src=; fp_visid=452a4dbde35177302ee92f199b5b18dc; fd_id=sH4tmUr5A7gpiW8yRe1qCnSwDGOocN6J; _fbp=fb.1.1732692190061.123470053690447508; _ga=GA1.1.1177071262.1732692199; _tt_enable_cookie=1; _ttp=mNn9Fu0EZ072X7gphbWsyaMUg4n.tt.1; _ss_s_uid=cea9581a6d29086e49cb688dbc0de6af; utm_lang=zh; Hm_lvt_6ada669245fc6950ae4a2c0a86931766=1732692180,1732754778; HMACCOUNT=25778556149293FF; _gcl_aw=GCL.1732841234.CjwKCAiAl4a6BhBqEiwAqvrqutdN-l76yWm3WXzSjKe8yN5-2e3csWm4GsvvO-jQ_CK17mHc5HCcgBoCjLYQAvD_BwE; Hm_lpvt_6ada669245fc6950ae4a2c0a86931766=1733274355; _gcl_au=1.1.109408670.1732692199.1378703260.1733280994.1733280994; fd_tk_exp=1734577124; fd_tk=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzQ1NzcxMjQsInN1YiI6IjJlNTc0OTZiMDIxY2U5YWUxNzY0ZjE3OTBiY2NiNDQwIiwibmJmIjoxNzMzMjgxMTI0LCJhdWQiOnsidWlkIjo5MzY5NDgwLCJ1bmlvbmlkIjoiIiwibWNfb3BlbmlkIjoiIiwibmlja25hbWUiOiJGYXN0TW9zc-eUqOaItyIsInJlZ2lvbiI6IlVTIiwiY3JlYXRlZF9hdCI6MTczMzI4MTEyMywiY3JlYXRlZF9kYXRlIjoiMjAyNC0xMi0wNCIsImxvZ2luX3NvdXJjZSI6InBjIiwidmlzaXRvcl9pZCI6IjQ1MmE0ZGJkZTM1MTc3MzAyZWU5MmYxOTliNWIxOGRjIiwiaXAiOiI1LjM0LjIxNi4xMTgiLCJkb21haW4iOiJ3d3cuZmFzdG1vc3MuY29tIiwiZnBfdmlzaWQiOiJiODc2ZmUzN2E1MmU2ZDk1MjllMGViYTQ4ODA1NmExMiIsImNyZWF0ZV90aW1lIjoxNzMzMjgxMTI0fSwiaWF0IjoxNzMzMjgxMTI0LCJqdGkiOiIyZTU3NDk2YjAyMWNlOWFlMTc2NGYxNzkwYmNjYjQ0MCIsImlzcyI6Ind3dy5mYXN0bW9zcy5jb20iLCJzdGF0dXMiOjEsImRhdGEiOm51bGx9.swFc7YqNrrXMNDycKcakCo1Ayn0m78mt73CRYruH30M; free_trial=FreeTrialFalse; NEXT_LOCALE=zh; region=Global; _ga_J8P3E5KDGJ=GS1.1.1733280990.6.1.1733281214.60.0.1625003845; _ga_GD8ST04HB5=GS1.1.1733280990.6.1.1733281214.60.0.244846493; __stripe_mid=cc75a684-38d8-4efd-aca1-7d2e41959cd7484817; __stripe_sid=27771cfe-f894-4032-8651-705dc81e3173bd55c4; _uetsid=31d2edc0b05411ef859059c474939c77|d0gbhu|2|frf|0|1797; _uetvid=6ec88190ac9011ef9f65177761bd263a|yoa2vk|1733281245994|13|1|bat.bing.com/p/insights/c/k',
            'fm-sign': 'a78c099e14dbf13c13bcd38b3e8c0810',
            'lang': 'ZH_CN',
            'priority': 'u=1, i',
            'referer': 'https://www.fastmoss.com/zh/e-commerce/detail/1729829773915949142',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'source': 'pc',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }

        response = requests.get(
            url,
            params=params,
            cookies=cookies,
            headers=headers,
        )

        # 检查请求是否成功
        if response.status_code != 200:
            return None
    
        res = response.json()
        logging.info(f"res: {res}")
        if res['code'] != 200:
            logging.error(f"fetch_videos {res['msg']}")
        return res['data']['list']
            
    except requests.RequestException as e:
        logging.error("请求过程中发生错误：", e)
        return None

def download_videos(product_id):
    videos = fetch_videos(product_id, 1)
    res = []
    for v in videos:
        res.append(download_video(product_id, v['video_id']))
    date = time.strftime("%Y%m%d", time.localtime())
    logging.info(f"please go to http://120.79.221.205:6801/files/tk_videos/{date}/{product_id}/")

    return {'link': f"http://120.79.221.205:6801/files/tk_videos/{date}/{product_id}/", 'detail':res}

def download_video(product_id, video_id):
    logging.info(f"downloading video_id:{video_id}")
    result = {'ok':False, 'video_id':video_id}
    video_detail = fetch_video_detail(video_id)
    if video_detail['status_code'] != 0:
        result["msg"] = f"fetch_tiktok_video failed {video_detail['status_msg']}"
        return result
    try:
        vedio_url =  video_detail['items'][0]['video_info']['url_list'][0]
        desc = video_detail['items'][0]['desc']
        
        logging.debug(f"downloading  vedio_url:{vedio_url}")
        date = time.strftime("%Y%m%d", time.localtime())
        if not download_file(vedio_url, f"tk_videos/{date}/{product_id}/{video_id}.mp4") :
            result["msg"] = f"download_file failed url:{vedio_url}"
            return result
        
        with open(f"tk_videos/{date}/{product_id}/text", 'a') as file:
            file.write(f'{desc}\n')  
        result['ok']  = True
        return result
    except Exception as e:
        result["msg"] = f"fetch_tiktok_video failed {e}"
        logging.error(f'download_video error: {e}')
        return result
    
    
    
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

def extract_product_id(url):
    pattern = r'\d+$'
    match = re.search(pattern, url)
    if match:
        return match.group()
    else:
        return None
    
@app.route('/download', methods=['POST'])
def download():
    product_link = request.form['product_name'] 
    #product_link = "https://www.fastmoss.com/zh/e-commerce/detail/1729488621914722962"
    if product_link is None or len(product_link) == 0 :
        return jsonify({"ok": False, "error": "No product_link provided"}) 
    
    product_id = extract_product_id(product_link)
    logging.info(f"product_link:{product_link} product_id:{product_id}")
    data = download_videos(product_id)  
    return jsonify({"ok": True, "data": data})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001, debug=False)
