from flask import Flask, request, render_template, jsonify, flash
from datetime import datetime
app = Flask(__name__)
import time
from urllib.parse import urlparse, parse_qs
import requests
import os
import re
from concurrent.futures import ThreadPoolExecutor
import logging
import threading
import queue

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 创建一个队列
task_queue = queue.Queue()

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
            logging.error(f"download failed err: {e}")
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
            'free_trial': 'FreeTrialFalse',
            '__stripe_mid': 'cc75a684-38d8-4efd-aca1-7d2e41959cd7484817',
            '_gcl_au': '1.1.109408670.1732692199.1897852172.1733467492.1733467868',
            'fd_tk_exp': '1734764019',
            'fd_tk': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzQ3NjQwMTksInN1YiI6IjlhNTA5YTk2OWU3MTM5ZTdkYThlMmEwYjk5MWY3ZjJmIiwibmJmIjoxNzMzNDY4MDE5LCJhdWQiOnsidWlkIjo5NDY3MDIzLCJ1bmlvbmlkIjoiIiwibWNfb3BlbmlkIjoiIiwibmlja25hbWUiOiJGYXN0TW9zc-eUqOaItyIsInJlZ2lvbiI6IlVTIiwiY3JlYXRlZF9hdCI6MTczMzQ2ODAxOCwiY3JlYXRlZF9kYXRlIjoiMjAyNC0xMi0wNiIsImxvZ2luX3NvdXJjZSI6InBjIiwidmlzaXRvcl9pZCI6IjQ1MmE0ZGJkZTM1MTc3MzAyZWU5MmYxOTliNWIxOGRjIiwiaXAiOiI1OC4yNTEuMjAuMjEwIiwiZG9tYWluIjoid3d3LmZhc3Rtb3NzLmNvbSIsImZwX3Zpc2lkIjoiYjg3NmZlMzdhNTJlNmQ5NTI5ZTBlYmE0ODgwNTZhMTIiLCJjcmVhdGVfdGltZSI6MTczMzQ2ODAxOX0sImlhdCI6MTczMzQ2ODAxOSwianRpIjoiOWE1MDlhOTY5ZTcxMzllN2RhOGUyYTBiOTkxZjdmMmYiLCJpc3MiOiJ3d3cuZmFzdG1vc3MuY29tIiwic3RhdHVzIjoxLCJkYXRhIjpudWxsfQ.DzassTr5jAC0hZ6yRY9NGcH6AvuJKOqGygv68QqWfC4',
            'NEXT_LOCALE': 'zh',
            'region': 'Global',
            '_ga_J8P3E5KDGJ': 'GS1.1.1733467468.7.1.1733468144.39.0.525138161',
            '_ga_GD8ST04HB5': 'GS1.1.1733467468.7.1.1733468144.39.0.1415477703',
            'Hm_lpvt_6ada669245fc6950ae4a2c0a86931766': '1733468231',
            '_uetsid': '31d2edc0b05411ef859059c474939c77|d0gbhu|2|frh|0|1797',
            '_uetvid': '6ec88190ac9011ef9f65177761bd263a|1sa5pg0|1733468232752|23|1|bat.bing.com/p/insights/c/k',
        }

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            # 'cookie': 'utm_south=google; utm_id=ggproduct; _src=; fp_visid=452a4dbde35177302ee92f199b5b18dc; fd_id=sH4tmUr5A7gpiW8yRe1qCnSwDGOocN6J; _fbp=fb.1.1732692190061.123470053690447508; _ga=GA1.1.1177071262.1732692199; _tt_enable_cookie=1; _ttp=mNn9Fu0EZ072X7gphbWsyaMUg4n.tt.1; _ss_s_uid=cea9581a6d29086e49cb688dbc0de6af; utm_lang=zh; Hm_lvt_6ada669245fc6950ae4a2c0a86931766=1732692180,1732754778; HMACCOUNT=25778556149293FF; _gcl_aw=GCL.1732841234.CjwKCAiAl4a6BhBqEiwAqvrqutdN-l76yWm3WXzSjKe8yN5-2e3csWm4GsvvO-jQ_CK17mHc5HCcgBoCjLYQAvD_BwE; free_trial=FreeTrialFalse; __stripe_mid=cc75a684-38d8-4efd-aca1-7d2e41959cd7484817; _gcl_au=1.1.109408670.1732692199.1897852172.1733467492.1733467868; fd_tk_exp=1734764019; fd_tk=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzQ3NjQwMTksInN1YiI6IjlhNTA5YTk2OWU3MTM5ZTdkYThlMmEwYjk5MWY3ZjJmIiwibmJmIjoxNzMzNDY4MDE5LCJhdWQiOnsidWlkIjo5NDY3MDIzLCJ1bmlvbmlkIjoiIiwibWNfb3BlbmlkIjoiIiwibmlja25hbWUiOiJGYXN0TW9zc-eUqOaItyIsInJlZ2lvbiI6IlVTIiwiY3JlYXRlZF9hdCI6MTczMzQ2ODAxOCwiY3JlYXRlZF9kYXRlIjoiMjAyNC0xMi0wNiIsImxvZ2luX3NvdXJjZSI6InBjIiwidmlzaXRvcl9pZCI6IjQ1MmE0ZGJkZTM1MTc3MzAyZWU5MmYxOTliNWIxOGRjIiwiaXAiOiI1OC4yNTEuMjAuMjEwIiwiZG9tYWluIjoid3d3LmZhc3Rtb3NzLmNvbSIsImZwX3Zpc2lkIjoiYjg3NmZlMzdhNTJlNmQ5NTI5ZTBlYmE0ODgwNTZhMTIiLCJjcmVhdGVfdGltZSI6MTczMzQ2ODAxOX0sImlhdCI6MTczMzQ2ODAxOSwianRpIjoiOWE1MDlhOTY5ZTcxMzllN2RhOGUyYTBiOTkxZjdmMmYiLCJpc3MiOiJ3d3cuZmFzdG1vc3MuY29tIiwic3RhdHVzIjoxLCJkYXRhIjpudWxsfQ.DzassTr5jAC0hZ6yRY9NGcH6AvuJKOqGygv68QqWfC4; NEXT_LOCALE=zh; region=Global; _ga_J8P3E5KDGJ=GS1.1.1733467468.7.1.1733468144.39.0.525138161; _ga_GD8ST04HB5=GS1.1.1733467468.7.1.1733468144.39.0.1415477703; Hm_lpvt_6ada669245fc6950ae4a2c0a86931766=1733468231; _uetsid=31d2edc0b05411ef859059c474939c77|d0gbhu|2|frh|0|1797; _uetvid=6ec88190ac9011ef9f65177761bd263a|1sa5pg0|1733468232752|23|1|bat.bing.com/p/insights/c/k',
            'fm-sign': '5294eb12ac777d6066f14537ea6a401c',
            'lang': 'ZH_CN',
            'priority': 'u=1, i',
            'referer': 'https://www.fastmoss.com/zh/e-commerce/detail/1729463610654102324',
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
        logging.debug(f"res: {res}")
        return res
            
    except requests.RequestException as e:
        logging.error("请求过程中发生错误：", e)
        return None

def download_video_thread(product_id, video_id):
    try:
        result = download_video(product_id, video_id)
        return result
    except Exception as e:
        logging.error(f"Failed to download video {video_id}: {e}")
        return None





def download_video(product_id, video_id):
    logging.info(f"{product_id}:{video_id} begining download video")
    video_detail = fetch_video_detail(video_id)
    if video_detail['status_code'] != 0:
        logging.warn(f"fetch_tiktok_video failed {video_detail['status_msg']}")
        return
    try:
        vedio_url =  video_detail['items'][0]['video_info']['url_list'][0]
        desc = video_detail['items'][0]['desc']
        date = time.strftime("%Y%m%d", time.localtime())
        filename = f"tk_videos/{date}/{product_id}/{video_id}.mp4"
        
        if  os.path.exists(filename):
            logging.info(f"{product_id}:{video_id} already downloaded!")
            return True
    
        if not download_file(vedio_url, filename) :
            logging.info(f"{product_id}:{video_id}  already downloaded!")
            return
        
        with open(f"tk_videos/{date}/{product_id}/text", 'a') as file:
            file.write(f'{desc}\n')  
        logging.info(f"{product_id}:{video_id}  download video success")
    except Exception as e:
        logging.error(f"{product_id}:{video_id} begining download video {e}")

def consumer_thread(task_queue):
    while True:
        # 获取任务，如果队列为空，则等待
        product_id, videos = task_queue.get()
        if product_id is None:
            break  # 如果接收到None，则退出循环
    
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(download_video_thread, product_id, v['video_id']) for v in videos]

    task_queue.task_done()  # 标记任务为完成


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

@app.route('/get_task_status', methods=['GET'])
def get_task_status():
    # 将所有日志信息返回给前端
    # log='\n'.join(log_messages)
    # log_messages.clear()
    #return log
    pass

@app.route('/download', methods=['POST'])
def download():
    product_links = request.form['product_links'] 
    if product_links is None or len(product_links) == 0 :        
        return jsonify({"ok": False, "error": "No product_links provided"}) 
    
    links = product_links.splitlines(keepends=False)

    product_ids = []
    for link  in links:
        r = {"ok": False, 'link': link}
        product_id = extract_product_id(link)
        if product_id == None:
            r['msg'] =  "link has no product_id"
            return jsonify({"ok": False, "error": f"{link} no product_id"}) 
        product_ids.append(product_id)
        
    rs =[]
    for product_id  in product_ids:
        r = {"ok": False, 'link': link, 'product_id':product_id}
        res = fetch_videos(product_id, 1)
        if res['code'] == 200:
            task_queue.put((product_id, res['data']['list']))
            r['ok'] = True
            date = time.strftime("%Y%m%d", time.localtime())
            save_dir = f'tk_videos/{date}/{product_id}'
            if  not os.path.exists(save_dir):
                os.makedirs(save_dir)
            r["save_link"] = f"http://120.79.221.205:6800/{save_dir}/"
            r['down_link'] = f"http://120.79.221.205:6800/{save_dir}/?op=archive" 
        else:
            r['msg'] = res['msg']
        rs.append(r)

    return jsonify({'ok':True, 'data': rs})

def app_run():
    logging.info("Flask app is running")
    app.run(app.run(host='0.0.0.0', port=5001, debug=False))

flask_thread = threading.Thread(target=app_run)
flask_thread.start()

consumer = threading.Thread(target=consumer_thread, args=(task_queue,))
consumer.start()

flask_thread.join()
consumer.join()
