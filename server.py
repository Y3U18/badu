from flask import Flask, request, jsonify
from datetime import datetime
app = Flask(__name__)
import time
from urllib.parse import urlparse, parse_qs
import requests
import os

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_tiktok_video(item_id, language='zh-CN'):
    url = "https://www.tiktok.com/player/api/v1/items"
    # 构建请求参数
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

    # 发送GET请求
    response = requests.get(url, params=params)

    # 检查响应状态码
    if response.status_code == 200:
        # 将响应内容解析为JSON
        return response.json()
    else:
        return {"error": f"请求失败，状态码：{response.status_code}"}

def download_file(url, filename):
    dir_path = os.path.dirname(filename)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # 发送HTTP GET请求
    response = requests.get(url)
    
    # 检查请求是否成功
    if response.status_code == 200:
        # 打开一个文件用于写入
        with open(filename, 'wb') as file:
            # 将内容写入文件
            file.write(response.content)
        print(f"文件已下载到：{filename}")
    else:
        print("文件下载失败")

def download_videos(url, name):
    parsed_url = urlparse(url)
    path = parsed_url.path
    video_id = path.split('/')[-1]
    logging.info(f"downloading video_id:{video_id}")
    result = fetch_tiktok_video(video_id)
    vedio_url =  result['items'][0]['video_info']['url_list'][0]
    logging.info(f"downloading  vedio_url:{vedio_url}")
    date = time.strftime("%Y%m%d", time.localtime())
    
    download_file(vedio_url, f"tk_videos/{date}/{name}/{video_id}.mp4")
    return f"http://120.79.221.205:6801/files/tk_videos/{date}/{name}/{video_id}.mp4"
    

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
    cloud_url = download_videos(url, name)
    vedio_urls.append(cloud_url)

    return jsonify({"ok": True, "vedio_urls": vedio_urls})

if __name__ == '__main__':
    app.run(port=5001, debug=True)