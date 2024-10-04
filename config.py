from pydantic import BaseModel

Headers_getlist = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Authorization': 'Bearer ',
    'DNT': '1',
    'Origin': 'https://class.pocketuni.net',
    'Referer': 'https://class.pocketuni.net/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
    'Content-Type': 'application/json',
    'Host': 'apis.pocketuni.net',
    'Connection': 'keep-alive'
}

Headers_login = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Origin': 'https://class.pocketuni.net',
    'Connection': 'keep-alive',
    'Referer': 'https://class.pocketuni.net/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Content-Type': 'application/json',
    'Host': 'apis.pocketuni.net'
}


class Config(BaseModel):
    """Plugin Config Here"""
