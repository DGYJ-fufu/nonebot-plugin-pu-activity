import asyncio

import nonebot
from nonebot import get_plugin_config, on_keyword, on_command, require
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
update_token = on_keyword({"刷新token"}, rule=to_me())  # 刷新token
help_cmd = on_keyword({"帮助"}, rule=to_me())

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
update_token_handler(update_token, service)  # 刷新token
help_cmd_handler(help_cmd)

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
