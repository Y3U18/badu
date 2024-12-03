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

def fetch_tiktok_video(item_id, language='zh-CN',  retry=5):
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

def download_video(name, link):
    result = {'ok':False, "link":link}
    match = re.search(r'\d{19}', link)

    # 如果找到匹配项，打印结果
    if not match:
        result["msg"] = "not found video_id"
        return result
    
    video_id = match.group()
    logging.info(f"downloading video_id:{video_id}")
    
    
    video_detail = fetch_tiktok_video(video_id)
    if video_detail['status_code'] != 0:
        result["msg"] = f"fetch_tiktok_video failed {video_detail['status_msg']}"
        return result
    try:
        vedio_url =  video_detail['items'][0]['video_info']['url_list'][0]
        desc = video_detail['items'][0]['desc']
        
        logging.info(f"downloading  vedio_url:{vedio_url}")
        date = time.strftime("%Y%m%d", time.localtime())
        if not download_file(vedio_url, f"tk_videos/{date}/{name}/{video_id}.mp4") :
            result["msg"] = f"download_file failed url:{vedio_url}"
            return result
        
        with open(f"tk_videos/{date}/{name}/text", 'a') as file:
            file.write(f'{desc}\n')
        logging.info(f"please go to http://120.79.221.205:6801/files/tk_videos/{date}/{name}/")
        
        result['ok']  = True
        return result
    except Exception as e:
        result["msg"] = f"fetch_tiktok_video failed {e}"
        logging.error("download_video ")
        return result
    
    
    
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/down_tk_video', methods=['POST'])
def down_tk_video():
    data = request.get_json()  # 获取JSON数据
    if data is None:
        return jsonify({"error": "No JSON data provided"}), 400

    name      =  data.get('name')
    if name is None:
        return jsonify({"error": "name provided"}), 400
    url  = data.get('url')
    if url is None:
        return jsonify({"error": "No url provided"}), 400
    vedio_urls=[]
    cloud_url = download_video(name, url)
    vedio_urls.append(cloud_url)

    return jsonify({"ok": True, "vedio_urls": vedio_urls})

@app.route('/download', methods=['POST'])
def download():
    product_name = request.form['product_name'] 
    if product_name is None or len(product_name) == 0 :
        return jsonify({"ok": False, "error": "No product_name provided"})
    product_links = request.form['product_link']
    if product_links is None or len(product_name) == 0:
        return jsonify({"ok": False, "error": "No product_link provided"})
    
    logging.info(f"product_name:{product_name}")
    data = []
    links = product_links.splitlines(keepends=False)
    for link  in links:
        data.append(download_video(product_name, link))
    return jsonify({"ok": True, "data": data})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001, debug=False)