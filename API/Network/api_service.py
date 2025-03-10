import hashlib
import time

import httpx
import logging
import orjson
import nonebot
from datetime import datetime
from typing import Optional, Any, Dict

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_headers() -> Dict[str, str]:
    """普通请求头"""
    return {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Authorization': 'Bearer :0',
        'DNT': '1',
        'Host': 'apis.pocketuni.net',
        'Origin': 'https://class.pocketuni.net',
        'Referer': 'https://class.pocketuni.net/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
        'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Content-Type': 'application/json'
    }


def get_headers_2() -> Dict[str, str]:
    """multipart/form-data请求头"""
    return {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'DNT': '1',
        'Host': 'pocketuni.net',
        'Origin': 'https://pc.pocketuni.net',
        'Referer': 'https://pc.pocketuni.net/',
        'Sec-Ch-Ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
    }


def get_headers_3() -> Dict[str, str]:
    """x-www-form-urlencoded请求头"""
    return {
        'Accept-Encoding': 'gzip',
        'User-Agent': 'client:Android version:7.1.16 Brand:OnePlus Product:PHB110 OsVersion:9',
        'Host': 'pocketuni.net',
        'Content-Type': 'application/x-www-form-urlencoded'
    }


class APIService:
    _instance = None

    def __new__(cls, base_url: str):
        if cls._instance is None:
            cls._instance = super(APIService, cls).__new__(cls)
            cls._instance.__init__(base_url)
        return cls._instance

    def __init__(self, base_url: str):
        """初始化API服务，设置基础URL和创建HTTP客户端"""
        self.base_url = base_url
        # 设置超时为2s，PU口袋服务器的请求限制大概为2s左右
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(2.0))

    async def close(self):
        """关闭HTTP客户端连接"""
        await self.client.aclose()

    async def _request(self,
                       mod: int,
                       method: str,
                       endpoint: str,
                       json: Optional[Dict[str, Any]] = None,
                       params: Optional[Dict[str, Any]] = None,
                       token: Optional[str] = None,
                       sid: Optional[int] = None,
                       oauth_token: Optional[str] = None,
                       oauth_token_secret: Optional[str] = None,
                       form_data: Optional[Dict[str, Any]] = None,
                       data: Optional[Dict[str, Any]] = None
                       ) -> Optional[Dict[str, Any]]:
        """
        通用请求方法
        :param mod: 请求模式：
                - 0: 普通请求（JSON请求体或查询参数）
                - 1: multipart/form-data请求体
                - 2: x-www-form-urlencoded请求体
        :param method: 请求方式，支持 'GET' 和 'POST'。
        :param endpoint: 接口路径（API的路径部分）。
        :param json: 请求体的JSON 数据。默认为 None。
        :param params: URL查询参数。默认为 None。
        :param token: 用于 Authorization 头中的 Bearer token 的值。默认为 None。
        :param sid: 会话 ID，通常与 token 一起使用。默认为 None。
        :param oauth_token: OAuth 认证令牌，用于某些需要OAuth验证的接口。默认为 None。
        :param oauth_token_secret: OAuth 认证令牌的密钥，通常与 oauth_token 一起使用。默认为 None。
        :param form_data: 用于发送 multipart/form-data 类型请求体的数据。默认为 None。
        :param data: 用于发送 application/x-www-form-urlencoded 类型请求体的数据。默认为 None。
        :return: 如果请求成功，返回解析后的 JSON 数据。失败时返回 None。
        """

        url = f"{self.base_url}{endpoint}"
        headers = None
        body = None
        response = None

        # 获取基础请求头
        if mod == 0:
            headers = get_headers()
            if token and sid:
                headers["Authorization"] = f"Bearer {token}:{sid}"
        elif mod == 1:
            headers = get_headers_2()
            if form_data and mod == 1:
                boundary = "----WebKitFormBoundarynKjSmHnvnjzUAUHa"
                headers = headers or {}
                headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
                body_parts = []
                for key, value in form_data.items():
                    body_parts.append(f"--{boundary}")
                    body_parts.append(f'Content-Disposition: form-data; name="{key}"')
                    body_parts.append("")
                    body_parts.append(value)
                body_parts.append(f"--{boundary}--")
                body = "\r\n".join(body_parts).encode("utf-8")
        elif mod == 2:
            headers = get_headers_3()
            if oauth_token and oauth_token_secret:
                headers["oauth_token"] = oauth_token
                headers["oauth_token_secret"] = oauth_token_secret
        elif mod == 3:
            headers = get_headers_2()
            headers["Priority"] = "u=1, i"
            del headers["Accept-Encoding"]
        try:
            if method.upper() == "POST":
                response = await self.client.post(
                    url,
                    content=body,
                    json=json,
                    headers=headers,
                    params=params,
                    data=data
                )
            elif method.upper() == "GET":
                response = await self.client.get(
                    url,
                    headers=headers,
                    params=params
                )
            response.raise_for_status()
            return orjson.loads(response.content)
        except httpx.HTTPStatusError as exc:
            print(f"HTTP错误: {exc.response.status_code} - {exc.response.text}")
        except Exception as exc:
            print(f"请求发生异常: {exc}")
        return None

    async def get_sid(self) -> Optional[Dict[str, Any]]:
        """获取SID列表"""
        return await self._request(mod=0, method='GET', endpoint="/uc/school/list")

    async def get_go_id(self):
        """
        获取go_id(原sid)
        :return:请求响应
        """
        params = {
            'app': 'api',
            'mod': 'Sitelist',
            'act': 'getSchools'
        }
        return await self._request(mod=3, method='GET', endpoint="/index.php", params=params)

    async def login(self,
                    is_go: int, username: Optional[str] = None,
                    password: Optional[str] = None,
                    sid: Optional[int] = None,
                    school: Optional[str] = None
                    ) -> Optional[Dict[str, Any]]:
        """
        用户登陆
        :param is_go: go_id状态
        :param username: 账号
        :param password: 密码
        :param sid: go_id
        :param school: 学校邮箱
        :return: 请求响应
        """
        if is_go == 0:
            form_data = {
                "email": username + school,
                "password": password,
                "usernum": username,
                "sid": '',
                "school": school,
                "type": "pc",
            }
            params = {
                "app": "api",
                "mod": "Sitelist",
                "act": "login"
            }
            return await self._request(
                mod=1,
                method="POST",
                endpoint="/index.php",
                params=params,
                form_data=form_data
            )
        elif is_go == 1:
            return await self._request(
                mod=0,
                method='POST',
                endpoint="/uc/user/login",
                json={
                    "userName": username,
                    "password": password,
                    "sid": sid,
                    "device": "pc"
                }
            )

    async def get_year(self, token: str, sid: int) -> Optional[Dict[str, Any]]:
        """
        获取学年ID
        :param token: 用户令牌
        :param sid: go_id
        :return: 请求响应
        """
        return await self._request(
            mod=0,
            method='GET',
            endpoint="/apis/mapping/year-list",
            token=token,
            sid=sid
        )

    async def get_classification(self,
                                 is_go: int,
                                 token: Optional[str] = None,
                                 sid: Optional[int] = None,
                                 oauth_token: Optional[str] = None,
                                 oauth_token_secret: Optional[str] = None
                                 ) -> Optional[Dict[str, Any]]:
        """
        获取活动分类
        :param is_go: go_id状态
        :param token: 用户令牌
        :param sid: go_id
        :param oauth_token: OAuth认证令牌
        :param oauth_token_secret: OAuth认证令牌密钥
        :return: 请求响应
        """
        if is_go == 0:
            params = {
                'app': 'api',
                'mod': 'Event',
                'act': 'newEventListHeader',
                'oauth_token': oauth_token,
                'oauth_token_secret': oauth_token_secret
            }
            return await self._request(mod=2, method='POST', endpoint="/index.php", params=params)

        elif is_go == 1:
            return await self._request(
                mod=0,
                method='POST',
                endpoint="/apis/mapping/data",
                json={
                    "key": "eventFilter",
                    "puType": 0
                },
                token=token,
                sid=sid
            )

    async def get_activity_list(self,
                                is_go: int,
                                token: Optional[str] = None,
                                sid: Optional[int] = None,
                                oauth_token: Optional[str] = None,
                                oauth_token_secret: Optional[str] = None,
                                num: int = 20
                                ) -> Optional[Dict[str, Any]]:
        """
        获取活动列表
        :param is_go: go_id状态
        :param token: 用户令牌
        :param sid: go_id
        :param oauth_token: OAuth认证令牌
        :param oauth_token_secret: OAuth认证令牌密钥
        :param num: 获取的活动数量
        :return: 请求响应
        """
        if is_go == 0:
            params = {
                'app': 'api',
                'mod': 'Event',
                'act': 'newEventListWithRecomm',
            }
            data = {
                "oauth_token": oauth_token,
                "oauth_token_secret": oauth_token_secret,
                "page": 1,
                "count": num
            }
            return await self._request(mod=2,
                                       method='POST',
                                       endpoint="/index.php",
                                       params=params,
                                       data=data,
                                       oauth_token=oauth_token,
                                       oauth_token_secret=oauth_token_secret
                                       )

        elif is_go == 1:
            return await self._request(
                mod=0,
                method='POST',
                endpoint="/apis/activity/list",
                json={
                    "sort": 0,
                    "page": 1,
                    "puType": 0,
                    "limit": num,
                },
                token=token,
                sid=sid
            )

    async def get_activity_list_filter(self,
                                       is_go: int,
                                       token: Optional[str] = None,
                                       sid: Optional[int] = None,
                                       oauth_token: Optional[str] = None,
                                       oauth_token_secret: Optional[str] = None,
                                       num: int = 20,
                                       **kwargs):
        """
        获取活动列表（筛选查询）
        :param is_go: go_id状态
        :param token: 用户令牌
        :param sid: go_id
        :param oauth_token: OAuth认证令牌
        :param oauth_token_secret: OAuth认证令牌密钥
        :param num: 获取的活动数量
        :param kwargs: 筛选条件:
                - is_go = 0:
                    - eventStatus: 活动状态ID
                    - catagoryId: 活动分类ID
                    - orgaId: 归属组织ID
                    - years: 年纪ID
                - is_go = 1:
                    - status: 活动状态ID
                    - cids: 归属院系ID
                    - oids: 归属组织ID
                    - categorys: 活动分类ID
        :return: 请求响应
        """
        if is_go == 0:
            params = {
                'app': 'api',
                'mod': 'Event',
                'act': 'newEventListWithRecomm',
            }
            data = {
                "oauth_token": oauth_token,
                "oauth_token_secret": oauth_token_secret,
                "page": 1,
                "count": num
            }
            for key in ["eventStatus", "catagoryId", "orgaId", "years"]:
                if key in kwargs and kwargs[key]:
                    data[key] = kwargs[key]  # 添加筛选条件
            return await self._request(mod=2,
                                       method='POST',
                                       endpoint="/index.php",
                                       params=params,
                                       data=data,
                                       oauth_token=oauth_token,
                                       oauth_token_secret=oauth_token_secret
                                       )
        elif is_go == 1:
            body = {
                "sort": 0,
                "page": 1,
                "puType": 0,
                "limit": num,
            }
            for key in ["status", "cids", "oids", "categorys"]:
                if key in kwargs and kwargs[key]:
                    body[key] = kwargs[key]  # 添加筛选条件
            return await self._request(
                mod=0,
                method='POST',
                endpoint="/apis/activity/list",
                json=body,
                token=token,
                sid=sid
            )

    async def get_activity_info(self,
                                is_go: int,
                                activity_id: int,
                                token: Optional[str] = None,
                                sid: Optional[int] = None,
                                oauth_token: Optional[str] = None,
                                oauth_token_secret: Optional[str] = None
                                ) -> Optional[Dict[str, Any]]:
        """
        获取活动详情
        :param is_go: go_id状态
        :param activity_id: 活动ID
        :param token: 用户令牌
        :param sid: go_id
        :param oauth_token: OAuth认证令牌
        :param oauth_token_secret: OAuth认证令牌密钥
        :return: 请求响应
        """
        if is_go == 0:
            params = {
                'app': 'api',
                'mod': 'Event',
                'act': 'queryActivityDetailById',
                "oauth_token": oauth_token,
                "oauth_token_secret": oauth_token_secret
            }
            data = {
                "oauth_token": oauth_token,
                "oauth_token_secret": oauth_token_secret,
                "actiId": activity_id
            }
            return await self._request(mod=2,
                                       method='POST',
                                       endpoint="/index.php",
                                       params=params,
                                       data=data,
                                       oauth_token=oauth_token,
                                       oauth_token_secret=oauth_token_secret
                                       )

        elif is_go == 1:
            return await self._request(
                mod=0,
                method='POST',
                endpoint="/apis/activity/info",
                json={"id": activity_id},
                token=token,
                sid=sid
            )

    async def get_my_activity_list(self,
                                   is_go: int,
                                   token: Optional[str] = None,
                                   sid: Optional[int] = None,
                                   oauth_token: Optional[str] = None,
                                   oauth_token_secret: Optional[str] = None,
                                   uid: Optional[int] = None,
                                   type_id: int = 1,
                                   num: int = 20
                                   ):
        """
        获取我的活动列表
        :param is_go: go_id状态
        :param token: 用户令牌
        :param sid: go_id
        :param oauth_token: OAuth认证令牌
        :param oauth_token_secret: OAuth认证令牌密钥
        :param uid: 用户id
        :param type_id: 活动类型ID
                    - 1: 未开始活动
                    - 2: 进行中互动
                    - 3: 已结束活动
                    - 4: 已完结互动
                    - 5: 待审核活动
        :param num: 请求的活动数量
        :return: 请求响应
        """
        if is_go == 0:
            params = {
                'app': 'api',
                'mod': 'Event',
                'act': 'myEventList'
            }
            data = {
                "uid": uid,
                "oauth_token": oauth_token,
                "count": num,
                "action": "join",
                "oauth_token_secret": oauth_token_secret,
                "page": 1,
                "status": type_id
            }
            return await self._request(mod=2,
                                       method='POST',
                                       endpoint="/index.php",
                                       params=params,
                                       data=data,
                                       oauth_token=oauth_token,
                                       oauth_token_secret=oauth_token_secret
                                       )

        elif is_go == 1:
            return await self._request(
                mod=0,
                method='POST',
                endpoint="/apis/activity/myList/new",
                json={
                    "type": type_id,
                    "page": 1,
                    "limit": num
                },
                token=token,
                sid=sid
            )

    async def get_activity_credit(self, token: str, sid: int, year: int = 0):
        """
        获取活动类分数
        :param token: 用户令牌
        :param sid: go_id
        :param year: 查询学年ID
        :return: 请求响应
        """
        return await self._request(
            mod=0,
            method='GET',
            endpoint="/apis/credit/activity",
            params={
                "puType": 0,
                "year": year
            },
            token=token,
            sid=sid
        )

    async def get_apply_credit(self, token: str, sid: int, year: int = 0):
        """
        获取成果类分数
        :param token: 用户令牌
        :param sid: go_id
        :param year: 查询学年ID
        :return: 请求响应
        """
        return await self._request(
            mod=0,
            method='GET',
            endpoint="/apis/credit/apply",
            params={
                "puType": 0,
                "year": year
            },
            token=token,
            sid=sid
        )

    async def join(self,
                   is_go: int,
                   activity_id: int,
                   token: Optional[str] = None,
                   sid: Optional[int] = None,
                   uid: Optional[int] = None,
                   oauth_token: Optional[str] = None,
                   oauth_token_secret: Optional[str] = None
                   ):
        """
        活动报名
        :param is_go: go_id状态
        :param activity_id: 活动ID
        :param token: 用户令牌
        :param sid: go_id
        :param uid: 用户ID
        :param oauth_token: OAuth认证令牌
        :param oauth_token_secret: OAuth认证令牌密钥
        :return: 请求响应
        """
        if is_go == 0:
            keys = 's25ycjfxcehwzs60yookgq8fx1es05af'
            timestamp = int(time.time())
            sign = hashlib.md5((str(uid) + str(activity_id) + str(timestamp) + keys).encode('utf-8')).hexdigest()
            form_data = {
                "id": f'{activity_id}',
                "time": f'{timestamp}',
                "sign": f'{sign}',
                "oauth_token": oauth_token,
                "oauth_token_secret": oauth_token_secret
            }
            params = {
                "app": "api",
                "mod": "Event",
                "act": "join2"
            }
            return await self._request(
                mod=1,
                method="POST",
                endpoint="/index.php",
                params=params,
                form_data=form_data
            )
        elif is_go == 1:
            return await self._request(
                mod=0,
                method='POST',
                endpoint="/apis/activity/join",
                json={"activityId": activity_id},
                token=token,
                sid=sid
            )

    async def info(self,
                   is_go: int,
                   token: Optional[str] = None,
                   sid: Optional[int] = None,
                   oauth_token: Optional[str] = None,
                   oauth_token_secret: Optional[str] = None
                   ):
        """
        用户信息
        :param is_go: go_id状态
        :param token: 用户令牌
        :param sid: go_id
        :param oauth_token: OAuth认证令牌
        :param oauth_token_secret: OAuth认证令牌密钥
        :return: 请求响应
        """
        if is_go == 0:
            params = {
                "oauth_token": oauth_token,
                "oauth_token_secret": oauth_token_secret
            }
            return await self._request(
                mod=2,
                method="POST",
                endpoint="/api/User/personalCenter",
                params=params,
                oauth_token=oauth_token,
                oauth_token_secret=oauth_token_secret
            )

        elif is_go == 1:
            return await self._request(
                mod=0,
                method='POST',
                endpoint="/apis/user/pc-info",
                token=token,
                sid=sid
            )
