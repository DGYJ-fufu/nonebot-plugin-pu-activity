import httpx
import logging
import orjson
from typing import Optional, Any, Dict

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_headers() -> Dict[str, str]:
    """获取请求头信息"""
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        # "Connection": "keep-alive",
        "DNT": "1",
        "Host": "apis.pocketuni.net",
        "Origin": "https://class.pocketuni.net",
        "Referer": "https://class.pocketuni.net/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
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
        self.client = httpx.AsyncClient()

    async def close(self):
        """关闭HTTP客户端连接"""
        await self.client.aclose()

    async def _request(self, method: str, endpoint: str, json: Optional[Dict[str, Any]] = None,
                       params: Optional[Dict[str, Any]] = None, token: Optional[str] = None,
                       sid: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """通用请求方法，用于发送网络请求"""
        headers = get_headers()
        if token and sid:
            headers["Authorization"] = f"Bearer {token}:{sid}"

        response = None  # 初始化响应变量为None
        try:
            if method == 'GET':
                response = await self.client.get(f"{self.base_url}{endpoint}", headers=headers, params=params)
            elif method == 'POST':
                response = await self.client.post(f"{self.base_url}{endpoint}", json=json, headers=headers)

            response.raise_for_status()
            return orjson.loads(response.content)
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP错误发生: {exc.response.status_code} - {exc.response.text}")
        except Exception as exc:
            logger.error(f"发生错误: {exc}")
        return None  # 返回None以表示请求失败

    async def get_sid(self) -> Optional[Dict[str, Any]]:
        """获取SID列表"""
        return await self._request('GET', "/uc/school/list")

    async def login(self, username: str, password: str, sid: int) -> Optional[Dict[str, Any]]:
        """用户登录"""
        return await self._request(
            'POST',
            "/uc/user/login",
            json={
                "userName": username,
                "password": password,
                "sid": sid,
                "device": "pc"
            }
        )

    async def get_year(self, token: str, sid: int) -> Optional[Dict[str, Any]]:
        """获取学年ID"""
        return await self._request(
            'GET',
            "/apis/mapping/year-list",
            token=token,
            sid=sid
        )

    async def get_classification(self, token: str, sid: int) -> Optional[Dict[str, Any]]:
        """获取活动分类"""
        return await self._request(
            'POST',
            "/apis/mapping/data",
            json={
                "key": "eventFilter",
                "puType": 0
            },
            token=token,
            sid=sid
        )

    async def get_activity_list(self, token: str, sid: int, num: int = 20) -> Optional[Dict[str, Any]]:
        """获取活动列表"""
        return await self._request(
            'POST',
            "/apis/activity/list",
            json={
                "sort": 0,
                "page": 1,
                "puType": 0,
                "limit": num,
            },
            token=token,
            sid=sid
        )

    async def get_activity_list_filter(self, token: str, sid: int, num: int = 20, **kwargs) -> Optional[Dict[str, Any]]:
        """获取活动列表（筛选查询）"""
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
            'POST',
            "/apis/activity/list",
            json=body,
            token=token,
            sid=sid
        )

    async def get_activity_info(self, token: str, sid: int, activity_id: int) -> Optional[Dict[str, Any]]:
        """获取活动详情"""
        return await self._request(
            'POST',
            "/apis/activity/info",
            json={"id": activity_id},
            token=token,
            sid=sid
        )

    async def get_my_activity_list(self, token: str, sid: int, type_id: int = 1, num: int = 20) -> Optional[
        Dict[str, Any]]:
        """获取我的活动列表"""
        return await self._request(
            'POST',
            "/apis/activity/myList/new",
            json={
                "type": type_id,
                "page": 1,
                "limit": num
            },
            token=token,
            sid=sid
        )

    async def get_activity_credit(self, token: str, sid: int, year: int = 0):
        """获取活动类分数"""
        return await self._request(
            'GET',
            "/apis/credit/activity",
            params={
                "puType": 0,
                "year": year
            },
            token=token,
            sid=sid
        )

    async def get_apply_credit(self, token: str, sid: int, year: int = 0):
        """获取成果类分数"""
        return await self._request(
            'GET',
            "/apis/credit/apply",
            params={
                "puType": 0,
                "year": year
            },
            token=token,
            sid=sid
        )

    async def join(self, token: str, sid: int, activity_id: int):
        """活动报名"""
        return await self._request(
            'POST',
            "/apis/activity/join",
            json={"activityId": activity_id},
            token=token,
            sid=sid
        )



