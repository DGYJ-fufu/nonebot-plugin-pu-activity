import asyncio

import nonebot
from nonebot import get_plugin_config, on_keyword, on_command, on_request, require
from nonebot.adapters.onebot.v11 import FriendRequestEvent
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import *
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me

from .config import Config

from .handlers import *
from .API.Network.api_service import APIService

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from .apscheduler import *

service = APIService('https://apis.pocketuni.net')

__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_apscheduler",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

# 定义消息事件响应器
user_add = on_command("添加用户", rule=to_me())  # 添加或更新用户数据
all_activity = on_keyword({"获取活动"}, rule=to_me())  # 获取活动
get_can_join_activity = on_keyword({"获取可参加活动"}, rule=to_me())  # 获取可参加活动
auto_push = on_command("活动推送", rule=to_me())  # 活动推送开关
my_activity = on_keyword({"我的活动"}, rule=to_me())  # 我的活动
activity_info = on_command("活动", rule=to_me())  # 活动信息
join_activity = on_command("报名", rule=to_me())  # 活动报名
reservation = on_command("预约", rule=to_me())  # 活动预约
find_reservation = on_keyword({"查询预约"}, rule=to_me())  # 查询预约
remove_reservation = on_command("删除预约", rule=to_me())  # 删除预约
update_token = on_keyword({"刷新token"}, rule=to_me())  # 刷新token
my_credit = on_keyword({"查询分数"}, rule=to_me())  # 查询分数
help_cmd = on_keyword({"帮助"}, rule=to_me())  # 帮助
# 添加群推送
group_add = on_command(
    "添加群推送",
    rule=to_me(),
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER
)
# 活动推送开关（群推送）
auto_push_group = on_command(
    "群推送",
    rule=to_me(),
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER
)

# 消息事件处理函数
user_add_handler(user_add, service)  # 添加或更新用户数据
all_activity_handlers(all_activity, service)  # 获取活动
get_can_join_activity_handler(get_can_join_activity, service)  # 获取可参加活动
auto_push_handler(auto_push)  # 活动推送开关
my_activity_handler(my_activity, service)  # 我的活动
activity_info_handler(activity_info, service)  # 活动信息
join_activity_handler(join_activity, service)  # 活动报名
reservation_handler(reservation, service, scheduler)  # 活动预约
find_reservation_handler(find_reservation, scheduler)  # 查询预约
remove_reservation_handler(remove_reservation, scheduler)  # 删除预约
update_token_handler(update_token, service)  # 刷新token
my_credit_handler(my_credit, service)  # 查询分数
group_add_handler(group_add, service)  # 添加群推送
auto_push_group_handler(auto_push_group)  # 活动推送开关（群推送）
help_cmd_handler(help_cmd)  # 帮助

# 定时任务初始化
asyncio.run(reservation_init(service, scheduler))

# 周期任务
scheduler.add_job(  # 新活动提醒
    push_handler,
    "interval",
    minutes=5,
    id="job_1",
    args=[service]
)
scheduler.add_job(  # 周期检查预约时间
    reservation_info_update,
    "interval",
    hours=1,
    id="job_2",
    args=[service, scheduler]
)
scheduler.add_job(  # 周期检查token是否失效
    cyclic_update_token,
    "interval",
    hours=4,
    id="job_3",
    args=[service]
)

# 自动通过好友申请
auto_accept_friend = on_request()


@auto_accept_friend.handle()
async def handle_friend_request(event: FriendRequestEvent):
    await event.approve()
