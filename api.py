from .hander import Headers_getlist, Headers_login
# from hander import Headers_getlist, Headers_login
from .tools import *
# from tools import *

import http.client
import json


# 获取sid
def get_sid(school_name):
    try:
        conn = http.client.HTTPSConnection("apis.pocketuni.net")
        payload = ''
        conn.request("GET", "/uc/school/list", payload, headers=Headers_login)
        res = conn.getresponse()
        data = res.read()
    except Exception as e:
        return "-1"
    for item in json.loads(data)["data"]["list"]:
        if item["name"] == school_name:
            return item["id"]


# 用户登录
def login(username, password, sid):
    try:
        conn = http.client.HTTPSConnection("apis.pocketuni.net")
        payload = json.dumps({
            "userName": username,
            "password": password,
            "sid": sid,
            "device": "pc"
        })
        conn.request("POST", "/uc/user/login", payload, headers=Headers_login)
        res = conn.getresponse()
        data = res.read()
        res = json.loads(data)
        if res["code"] == 0:
            return {
                "token": res["data"]["token"],
                "cid": res["data"]["baseUserInfo"]["cid"]
            }
        else:
            return "-2"
    except Exception as e:
        return "-1"


# 获取全部活动列表
def get_activity_list(token, sid):
    try:
        conn = http.client.HTTPSConnection("apis.pocketuni.net")
        payload = json.dumps({
            "sort": 0,
            "page": 1,
            "limit": 40,
            "puType": 0
        })
        headers = Headers_getlist.copy()
        headers["Authorization"] = f"Bearer {token}:{sid}"
        conn.request("POST", "/apis/activity/list", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        if json.loads(data)["code"] == 0:
            return json.loads(data)
        else:
            return "-2"
    except Exception as e:
        return "-1"


# 学院筛选查询
def get_academy_list(token, sid, cid):
    try:
        conn = http.client.HTTPSConnection("apis.pocketuni.net")
        payload = json.dumps({
            "sort": 0,
            "page": 1,
            "limit": 10,
            "puType": 0,
            "cids": [cid]
        })
        headers = Headers_getlist.copy()
        headers["Authorization"] = f"Bearer {token}:{sid}"
        conn.request("POST", "/apis/activity/list", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        if json.loads(data)["code"] == 0:
            return json.loads(data)
        else:
            return "-2"
    except Exception as e:
        return "-1"


# 活动详情查询
def get_activity_info(token, sid, id):
    try:
        conn = http.client.HTTPSConnection("apis.pocketuni.net")
        payload = json.dumps({
            "id": int(id)
        })
        headers = Headers_getlist.copy()
        headers["Authorization"] = f"Bearer {token}:{sid}"
        conn.request("POST", "/apis/activity/info", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        if json.loads(data)["code"] == 0:
            return json.loads(data)
        else:
            return "-2"
    except Exception as e:
        return "-1"


# 获取可参加活动
def get_can_join_activity(token, sid, cid):
    try:
        activities = []
        activity_list = get_activity_list(token, sid)["data"]["list"]
        if activity_list == "-1":
            return "-1"
        elif activity_list == "-2":
            return "-2"
        else:
            for activity in activity_list:
                if activity["statusName"] != "已结束" and activity["allowUserCount"] != activity["joinUserCount"]:
                    info = get_activity_info(token, sid, activity["id"])["data"]["baseInfo"]
                    if info == "-1":
                        return "-1"
                    elif info == "-2":
                        return "-2"
                    else:
                        if compare_datetime(get_datetime(), info["joinEndTime"]):
                            if info["allowCollege"] is None or (
                                    isinstance(info["allowCollege"], list) and not info["allowCollege"]):
                                activities.append(activity)
                            else:
                                if info["allowCollege"][0]["id"] == cid:
                                    activities.append(activity)
            return activities
    except Exception as e:
        return "-1"


# 报名活动
def join_activity(token, sid, id):
    try:
        conn = http.client.HTTPSConnection("apis.pocketuni.net")
        payload = json.dumps({
            "activityId": int(id)
        })
        headers = Headers_getlist.copy()
        headers["Authorization"] = f"Bearer {token}:{sid}"
        conn.request("POST", "/apis/activity/join", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        if json.loads(data)["code"] == 401:
            return "-2"
        else:
            return json.loads(data)
    except Exception as e:
        return "-1"


# 获取活动分类
def get_activity_mapping(token, sid):
    try:
        conn = http.client.HTTPSConnection("apis.pocketuni.net")
        payload = json.dumps({
            "key": "eventFilter",
            "puType": 0
        })
        headers = Headers_getlist.copy()
        headers["Authorization"] = f"Bearer {token}:{sid}"
        conn.request("POST", "/apis/mapping/data", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        if json.loads(data)["code"] == 0:
            return json.loads(data)
        else:
            return "-2"
    except Exception as e:
        return "-1"


# 查询我的活动(未开始)
def find_not_started_activity(token, sid):
    try:
        conn = http.client.HTTPSConnection("apis.pocketuni.net")
        payload = json.dumps({
            "type": 1,
            "page": 1,
            "limit": 20
        })
        headers = Headers_getlist.copy()
        headers["Authorization"] = f"Bearer {token}:{sid}"
        conn.request("POST", "/apis/activity/myList/new", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        if json.loads(data)["code"] == 0:
            return json.loads(data)
        else:
            return "-2"
    except Exception as e:
        return "-1"


# 查询我的活动(待审核)
def find_waiting_for_review_activity(token, sid):
    try:
        conn = http.client.HTTPSConnection("apis.pocketuni.net")
        payload = json.dumps({
            "type": 5,
            "page": 1,
            "limit": 20
        })
        headers = Headers_getlist.copy()
        headers["Authorization"] = f"Bearer {token}:{sid}"
        conn.request("POST", "/apis/activity/myList/new", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        if json.loads(data)["code"] == 0:
            return json.loads(data)
        else:
            return "-2"
    except Exception as e:
        return "-1"
