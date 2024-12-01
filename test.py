
import requests

# 目标URL
url = 'http://localhost:5001/down_tk_video'

# POST请求的数据
json_data = {
    'name': '123',
    'url': 'https://www.fastmoss.com/zh/media-source/video/7429549391100284191'
}


# 如果你发送的是JSON数据，使用json参数
response = requests.post(url, json=json_data)

# 打印响应的文本内容
print(response.text)

# 打印响应的状态码
print(response.status_code)

# 打印响应的JSON内容（如果响应是JSON格式）
# print(response.json())