from flask import Flask, request, render_template, jsonify, flash
from datetime import datetime
app = Flask(__name__)
import time
from urllib.parse import urlparse, parse_qs
from curl_cffi import requests
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
            "pagesize": 5,
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
            'free_trial': 'FreeTrialFalse',
            '_gcl_au': '1.1.1894929420.1732585453.1048364009.1734007656.1734007655',
            'fd_tk_exp': '1735303764',
            'fd_tk': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzUzMDM3NjQsInN1YiI6ImEzNGYwMTIzZTQ5OTlmMTc5MjZmYTM5ZTQ3Nzc0NzA0IiwibmJmIjoxNzM0MDA3NzY0LCJhdWQiOnsidWlkIjo5Njg4OTIxLCJ1bmlvbmlkIjoiIiwibWNfb3BlbmlkIjoiIiwibmlja25hbWUiOiJGYXN0TW9zc-eUqOaItyIsInJlZ2lvbiI6IlVTIiwiY3JlYXRlZF9hdCI6MTczNDAwNzc2MywiY3JlYXRlZF9kYXRlIjoiMjAyNC0xMi0xMiIsImxvZ2luX3NvdXJjZSI6InBjIiwidmlzaXRvcl9pZCI6IjY4ZTA3YTE3NDgyNWI4YmMwZWUwNzY5ZWY2ZWUwM2ZjIiwiaXAiOiIyNy4zOC4xOTMuMjMxIiwiZG9tYWluIjoid3d3LmZhc3Rtb3NzLmNvbSIsImZwX3Zpc2lkIjoiOTQyOGJkMzU5NmE2N2ZlOTUyYmY2M2JkMDE5ODU0MDIiLCJjcmVhdGVfdGltZSI6MTczNDAwNzc2NH0sImlhdCI6MTczNDAwNzc2NCwianRpIjoiYTM0ZjAxMjNlNDk5OWYxNzkyNmZhMzllNDc3NzQ3MDQiLCJpc3MiOiJ3d3cuZmFzdG1vc3MuY29tIiwic3RhdHVzIjoxLCJkYXRhIjpudWxsfQ.glLPoVGVvGq04aQdPyenzCGdilFyUQEfHBcw9-1LuNw',
            'NEXT_LOCALE': 'zh',
            'region': 'Global',
            '_ga_J8P3E5KDGJ': 'GS1.1.1734007652.19.1.1734007781.42.0.900730503',
            '_ga_GD8ST04HB5': 'GS1.1.1734007652.19.1.1734007781.42.0.512634539',
            'Hm_lpvt_6ada669245fc6950ae4a2c0a86931766': '1734007840',
            '_uetsid': '4195b8a0b88711ef93601ba472862014|qewdtw|2|frn|0|1807',
            '_uetvid': 'e5a098e0ab9711efb467d595a47500a2|os2b6h|1734007840926|6|1|bat.bing.com/p/insights/c/k',
        }

        
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            # 'cookie': 'utm_south=google; utm_id=ggproduct; _src=; fp_visid=68e07a174825b8bc0ee0769ef6ee03fc; fd_id=UrfKhQSzs6eI415nBOjF8TkCMladVAqP; Hm_lvt_6ada669245fc6950ae4a2c0a86931766=1732585434; HMACCOUNT=DE784806A161133E; _fbp=fb.1.1732585434257.605751515129595828; _ga=GA1.1.468739000.1732585453; _tt_enable_cookie=1; _ttp=bmZ0vYQWnabrDogGvJTDTpl5yFa.tt.1; utm_lang=zh; _ss_s_uid=8ea7c8961ea34162544ea58a6f611740; _gcl_aw=GCL.1733106169.CjwKCAiAl4a6BhBqEiwAqvrqutdN-l76yWm3WXzSjKe8yN5-2e3csWm4GsvvO-jQ_CK17mHc5HCcgBoCjLYQAvD_BwE; free_trial=FreeTrialFalse; _gcl_au=1.1.1894929420.1732585453.1048364009.1734007656.1734007655; fd_tk_exp=1735303764; fd_tk=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzUzMDM3NjQsInN1YiI6ImEzNGYwMTIzZTQ5OTlmMTc5MjZmYTM5ZTQ3Nzc0NzA0IiwibmJmIjoxNzM0MDA3NzY0LCJhdWQiOnsidWlkIjo5Njg4OTIxLCJ1bmlvbmlkIjoiIiwibWNfb3BlbmlkIjoiIiwibmlja25hbWUiOiJGYXN0TW9zc-eUqOaItyIsInJlZ2lvbiI6IlVTIiwiY3JlYXRlZF9hdCI6MTczNDAwNzc2MywiY3JlYXRlZF9kYXRlIjoiMjAyNC0xMi0xMiIsImxvZ2luX3NvdXJjZSI6InBjIiwidmlzaXRvcl9pZCI6IjY4ZTA3YTE3NDgyNWI4YmMwZWUwNzY5ZWY2ZWUwM2ZjIiwiaXAiOiIyNy4zOC4xOTMuMjMxIiwiZG9tYWluIjoid3d3LmZhc3Rtb3NzLmNvbSIsImZwX3Zpc2lkIjoiOTQyOGJkMzU5NmE2N2ZlOTUyYmY2M2JkMDE5ODU0MDIiLCJjcmVhdGVfdGltZSI6MTczNDAwNzc2NH0sImlhdCI6MTczNDAwNzc2NCwianRpIjoiYTM0ZjAxMjNlNDk5OWYxNzkyNmZhMzllNDc3NzQ3MDQiLCJpc3MiOiJ3d3cuZmFzdG1vc3MuY29tIiwic3RhdHVzIjoxLCJkYXRhIjpudWxsfQ.glLPoVGVvGq04aQdPyenzCGdilFyUQEfHBcw9-1LuNw; NEXT_LOCALE=zh; region=Global; _ga_J8P3E5KDGJ=GS1.1.1734007652.19.1.1734007781.42.0.900730503; _ga_GD8ST04HB5=GS1.1.1734007652.19.1.1734007781.42.0.512634539; Hm_lpvt_6ada669245fc6950ae4a2c0a86931766=1734007889; _uetsid=4195b8a0b88711ef93601ba472862014|qewdtw|2|frn|0|1807; _uetvid=e5a098e0ab9711efb467d595a47500a2|os2b6h|1734007890311|7|1|bat.bing.com/p/insights/c/k',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
 
        response = requests.get(url,params=params,cookies=cookies,headers=headers,impersonate="chrome")
        logging.info(response.text)

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
    logging.info("download")
    product_links = request.form['product_links'] 
    if product_links is None or len(product_links) == 0 :        
        return jsonify({"ok": False, "error": "No product_links provided"}) 
    
    links = product_links.splitlines(keepends=False)

    product_ids = []
    for link  in links:
        r = {"ok": False, 'link': link}
        logging.info(link)
        if '/e-commerce/detail/' in link:
            product_id = extract_product_id(link)
            if product_id == None:
                r['msg'] =  "link has no product_id"
                return jsonify({"ok": False, "error": f"{link} no product_id"}) 
            product_ids.append(product_id)
        else:
            return jsonify({"ok": False, "error": f"{link} is not product link."}) 
    logging.info(f"download {product_ids}")    
    rs =[]
    for product_id  in product_ids:
        r = {"ok": False, 'link': link, 'product_id':product_id}
        res = fetch_videos(product_id, 1)
        logging.info('fetch_videos {res}')
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
