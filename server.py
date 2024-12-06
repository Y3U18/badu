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
            'fp_visid': '68e07a174825b8bc0ee0769ef6ee03fc',
            'fd_id': 'UrfKhQSzs6eI415nBOjF8TkCMladVAqP',
            'Hm_lvt_6ada669245fc6950ae4a2c0a86931766': '1732585434',
            'HMACCOUNT': 'DE784806A161133E',
            '_fbp': 'fb.1.1732585434257.605751515129595828',
            '_ga': 'GA1.1.468739000.1732585453',
            '_tt_enable_cookie': '1',
            '_ttp': 'bmZ0vYQWnabrDogGvJTDTpl5yFa.tt.1',
            'utm_lang': 'zh',
            '_ss_s_uid': '8ea7c8961ea34162544ea58a6f611740',
            '_gcl_aw': 'GCL.1733106169.CjwKCAiAl4a6BhBqEiwAqvrqutdN-l76yWm3WXzSjKe8yN5-2e3csWm4GsvvO-jQ_CK17mHc5HCcgBoCjLYQAvD_BwE',
            '_gcl_au': '1.1.1894929420.1732585453.17552096.1733279143.1733279143',
            'fd_tk_exp': '1734575248',
            'fd_tk': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzQ1NzUyNDgsInN1YiI6IjI3YmJhN2MwMTYwZmI4ZjIwZDhjNmFmYTkyN2RlMGFkIiwibmJmIjoxNzMzMjc5MjQ4LCJhdWQiOnsidWlkIjo5MzY3NzIyLCJ1bmlvbmlkIjoiIiwibWNfb3BlbmlkIjoiIiwibmlja25hbWUiOiJGYXN0TW9zc-eUqOaItyIsInJlZ2lvbiI6IlVTIiwiY3JlYXRlZF9hdCI6MTczMzI3OTI0NywiY3JlYXRlZF9kYXRlIjoiMjAyNC0xMi0wNCIsImxvZ2luX3NvdXJjZSI6InBjIiwidmlzaXRvcl9pZCI6IjY4ZTA3YTE3NDgyNWI4YmMwZWUwNzY5ZWY2ZWUwM2ZjIiwiaXAiOiIxNjMuMTI1LjE5My4yNiIsImRvbWFpbiI6Ind3dy5mYXN0bW9zcy5jb20iLCJmcF92aXNpZCI6Ijk0MjhiZDM1OTZhNjdmZTk1MmJmNjNiZDAxOTg1NDAyIiwiY3JlYXRlX3RpbWUiOjE3MzMyNzkyNDh9LCJpYXQiOjE3MzMyNzkyNDgsImp0aSI6IjI3YmJhN2MwMTYwZmI4ZjIwZDhjNmFmYTkyN2RlMGFkIiwiaXNzIjoid3d3LmZhc3Rtb3NzLmNvbSIsInN0YXR1cyI6MSwiZGF0YSI6bnVsbH0.Me2RuVMdUHjWnsKygAjsgV6auqB9qB4ocoUcRCOmNms',
            'NEXT_LOCALE': 'zh',
            'region': 'Global',
            '_ga_J8P3E5KDGJ': 'GS1.1.1733279135.10.1.1733279270.34.0.1197439520',
            '_ga_GD8ST04HB5': 'GS1.1.1733279135.10.1.1733279270.34.0.411894322',
            'Hm_lpvt_6ada669245fc6950ae4a2c0a86931766': '1733327778',
            '_uetsid': 'e5a09f30ab9711ef965fe55fae453704|jksuoi|2|frf|0|1791',
            '_uetvid': 'e5a098e0ab9711efb467d595a47500a2|gik53o|1733327778576|70|1|bat.bing.com/p/insights/c/k',
        }


        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            # 'cookie': 'utm_south=google; utm_id=ggproduct; _src=; fp_visid=68e07a174825b8bc0ee0769ef6ee03fc; fd_id=UrfKhQSzs6eI415nBOjF8TkCMladVAqP; Hm_lvt_6ada669245fc6950ae4a2c0a86931766=1732585434; HMACCOUNT=DE784806A161133E; _fbp=fb.1.1732585434257.605751515129595828; _ga=GA1.1.468739000.1732585453; _tt_enable_cookie=1; _ttp=bmZ0vYQWnabrDogGvJTDTpl5yFa.tt.1; utm_lang=zh; _ss_s_uid=8ea7c8961ea34162544ea58a6f611740; _gcl_aw=GCL.1733106169.CjwKCAiAl4a6BhBqEiwAqvrqutdN-l76yWm3WXzSjKe8yN5-2e3csWm4GsvvO-jQ_CK17mHc5HCcgBoCjLYQAvD_BwE; _gcl_au=1.1.1894929420.1732585453.17552096.1733279143.1733279143; fd_tk_exp=1734575248; fd_tk=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzQ1NzUyNDgsInN1YiI6IjI3YmJhN2MwMTYwZmI4ZjIwZDhjNmFmYTkyN2RlMGFkIiwibmJmIjoxNzMzMjc5MjQ4LCJhdWQiOnsidWlkIjo5MzY3NzIyLCJ1bmlvbmlkIjoiIiwibWNfb3BlbmlkIjoiIiwibmlja25hbWUiOiJGYXN0TW9zc-eUqOaItyIsInJlZ2lvbiI6IlVTIiwiY3JlYXRlZF9hdCI6MTczMzI3OTI0NywiY3JlYXRlZF9kYXRlIjoiMjAyNC0xMi0wNCIsImxvZ2luX3NvdXJjZSI6InBjIiwidmlzaXRvcl9pZCI6IjY4ZTA3YTE3NDgyNWI4YmMwZWUwNzY5ZWY2ZWUwM2ZjIiwiaXAiOiIxNjMuMTI1LjE5My4yNiIsImRvbWFpbiI6Ind3dy5mYXN0bW9zcy5jb20iLCJmcF92aXNpZCI6Ijk0MjhiZDM1OTZhNjdmZTk1MmJmNjNiZDAxOTg1NDAyIiwiY3JlYXRlX3RpbWUiOjE3MzMyNzkyNDh9LCJpYXQiOjE3MzMyNzkyNDgsImp0aSI6IjI3YmJhN2MwMTYwZmI4ZjIwZDhjNmFmYTkyN2RlMGFkIiwiaXNzIjoid3d3LmZhc3Rtb3NzLmNvbSIsInN0YXR1cyI6MSwiZGF0YSI6bnVsbH0.Me2RuVMdUHjWnsKygAjsgV6auqB9qB4ocoUcRCOmNms; NEXT_LOCALE=zh; region=Global; _ga_J8P3E5KDGJ=GS1.1.1733279135.10.1.1733279270.34.0.1197439520; _ga_GD8ST04HB5=GS1.1.1733279135.10.1.1733279270.34.0.411894322; Hm_lpvt_6ada669245fc6950ae4a2c0a86931766=1733327778; _uetsid=e5a09f30ab9711ef965fe55fae453704|jksuoi|2|frf|0|1791; _uetvid=e5a098e0ab9711efb467d595a47500a2|gik53o|1733327778576|70|1|bat.bing.com/p/insights/c/k',
            'fm-sign': '219fe10a9b2e42171c2aa651cd65b9af',
            'lang': 'ZH_CN',
            'priority': 'u=1, i',
            'referer': 'https://www.fastmoss.com/zh/e-commerce/detail/1729991365114368343',
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
            # task_queue.put((product_id, res['data']['list']))
            r['ok'] = True
            date = time.strftime("%Y%m%d", time.localtime())
            r["save_link"] = f"http://120.79.221.205:6801/files/tk_videos/{date}/{product_id}/"
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
