from nonebot import get_plugin_config, on_keyword, on_command, require, get_bot
from nonebot.adapters import MessageTemplate, Event
from nonebot.adapters.onebot.v11 import Message, Event, Bot
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me, ArgumentParser
from nonebot.params import CommandArg, ArgPlainText
from nonebot.typing import T_State

from .config import Config

from .database import DataBase
from .api import *

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

__plugin_meta__ = PluginMetadata(
    name="pu_activity",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

# 连接数据库
database = DataBase()

user = on_command("添加用户", rule=to_me())
all_activity = on_keyword({"获取全部活动"}, rule=to_me())
academy_activity = on_keyword({"获取学院活动"}, rule=to_me())
activity_info = on_command("活动", rule=to_me())
can_join_activity = on_keyword({"获取可参加活动"}, rule=to_me())
join_activity = on_command("报名", rule=to_me())
auto_push = on_command("活动推送", rule=to_me())
help = on_keyword({"帮助"}, rule=to_me())


@user.handle()
async def _(state: T_State, event: Event):
    state["qq"] = event.get_user_id()


@user.got("user_info", prompt=MessageTemplate("请输入用户信息\n格式如下:\n账号:密码:学校全称"))
async def _(state: T_State, user_info: str = ArgPlainText()):
    # 获取输入的用户信息
    state["username"], state["password"], state["sid"] = user_info.split(":")
    # 查询并返回sid
    state["sid"] = get_sid(state["sid"])
    # 查找QQ是否在库
    if database.find_qq(state["qq"]) is not None:
        # 在库,修改用户信息
        database.user_update(qq=state["qq"], username=state["username"], password=state["password"],
                             sid=state["sid"])
    else:
        # 不在库,添加用户信息
        database.user_add(qq=state["qq"], username=state["username"], password=state["password"],
                          sid=state["sid"])
    database.update_user_token(state["qq"])
    await user.finish(MessageTemplate("添加的用户信息:\n账号:{username}\n密码:{password}\n学校:{sid}"))


@all_activity.handle()
async def handle_function(event: Event):
    qq = event.get_user_id()
    token = database.get_user_token(qq)
    activity_msg = api.get_activity_list(token=token[0], sid=token[1])
    if activity_msg != "-1":
        msg = ""
        for activity in activity_msg["data"]["list"]:
            msg += f'活动名称:{activity["name"]}\n'
            msg += f'活动分值:{activity["credit"]}\n'
            msg += f'报名时间:{activity["joinStartTime"]}\n'
            msg += f'开始时间:{activity["startTime"]}\n'
            msg += f'结束时间:{activity["endTime"]}\n'
            msg += f'可参与人数:{activity["allowUserCount"]}\n'
            msg += f'已报名人数:{activity["joinUserCount"]}\n'
            msg += f'活动状态:{activity["statusName"]}\n'
            msg += f'活动ID:{activity["id"]}\n'
            msg += "\n"
        await all_activity.finish(Message(msg))
    else:
        database.update_user_token(qq)
        await all_activity.finish(Message("获取失败"))


@academy_activity.handle()
async def handle_function(event: Event):
    qq = event.get_user_id()
    token = database.get_user_token(qq)
    cid = database.get_user_cid(qq)
    academy_msg = api.get_academy_list(token=token[0], sid=token[1], cid=cid)
    if academy_msg != "-1":
        msg = ""
        for activity in academy_msg["data"]["list"]:
            msg += f'活动名称:{activity["name"]}\n'
            msg += f'活动分值:{activity["credit"]}\n'
            msg += f'报名时间:{activity["joinStartTime"]}\n'
            msg += f'报名时间:{activity["joinStartTime"]}\n'
            msg += f'开始时间:{activity["startTime"]}\n'
            msg += f'结束时间:{activity["endTime"]}\n'
            msg += f'可参与人数:{activity["allowUserCount"]}\n'
            msg += f'已报名人数:{activity["joinUserCount"]}\n'
            msg += f'活动状态:{activity["statusName"]}\n'
            msg += f'活动ID:{activity["id"]}\n'
            msg += "\n"
        await academy_activity.finish(Message(msg))
    else:
        database.update_user_token(qq)
        await academy_activity.finish(Message("获取失败"))


@activity_info.handle()
async def handle_function(event: Event, args: Message = CommandArg()):
    qq = event.get_user_id()
    token = database.get_user_token(qq)
    if id := args.extract_plain_text():
        activity_msg = api.get_activity_info(token=token[0], sid=token[1], id=id)
        if activity_msg != "-1":
            activity_msg = activity_msg["data"]["baseInfo"]
            msg = f'活动名称:{activity_msg["name"]}\n'
            msg += f'活动分值:{activity_msg["credit"]}\n'
            if activity_msg["allowCollege"]:
                msg += f"所属学院:{activity_msg['allowCollege'][0]['name']}\n"
            else:
                msg += "所属学院:全部\n"
            msg += f'活动类型:{activity_msg["categoryName"]}\n'
            msg += f'可参与人数:{activity_msg["allowUserCount"]}\n'
            msg += f'已报名人数:{activity_msg["joinUserCount"]}\n'
            msg += f'报名开始时间:{activity_msg["joinStartTime"]}\n'
            msg += f'报名结束时间:{activity_msg["joinEndTime"]}\n'
            msg += f'活动开始时间:{activity_msg["startTime"]}\n'
            msg += f'活动结束时间:{activity_msg["endTime"]}\n'
            msg += f'活动地址:{activity_msg["address"]}\n'
            msg += f'活动简介:{activity_msg["description"]}\n'
            msg += f'活动状态:{activity_msg["statusName"]}\n'
            await activity_info.finish(msg)
        else:
            database.update_user_token(qq)
            await activity_info.finish(Message("获取失败"))

    else:
        await activity_info.finish("请输入活动ID")


@can_join_activity.handle()
async def handle_function(event: Event):
    qq = event.get_user_id()
    token = database.get_user_token(qq)
    cid = database.get_user_cid(qq)
    can_join_activity_list = api.get_can_join_activity(token=token[0], sid=token[1], cid=cid)
    if can_join_activity_list != "-1":
        msg = ""
        for activity in can_join_activity_list:
            msg += f'活动名称:{activity["name"]}\n'
            msg += f'活动分值:{activity["credit"]}\n'
            msg += f'报名时间:{activity["joinStartTime"]}\n'
            msg += f'开始时间:{activity["startTime"]}\n'
            msg += f'结束时间:{activity["endTime"]}\n'
            msg += f'可参与人数:{activity["allowUserCount"]}\n'
            msg += f'已报名人数:{activity["joinUserCount"]}\n'
            msg += f'活动状态:{activity["statusName"]}\n'
            msg += f'活动ID:{activity["id"]}\n'
            msg += "\n"
        if msg != "":
            await can_join_activity.finish(Message(msg))
        else:
            await can_join_activity.finish(Message("暂无可参加活动"))
    else:
        database.update_user_token(qq)
        await can_join_activity.finish(Message("获取失败"))


@join_activity.handle()
async def handle_function(event: Event, args: Message = CommandArg()):
    qq = event.get_user_id()
    token = database.get_user_token(qq)
    if id := args.extract_plain_text():
        join_msg = api.join_activity(token=token[0], sid=token[1], id=id)
        if join_msg != "-1":
            await academy_activity.finish(Message(join_msg["message"]))
        else:
            database.update_user_token(qq)
            await academy_activity.finish(Message("请求错误"))


@auto_push.handle()
async def handle_function(event: Event, args: Message = CommandArg()):
    qq = event.get_user_id()
    if args.extract_plain_text() == "开启":
        database.set_auto_push(qq, 1)
        await academy_activity.finish(Message("已开启活动推送"))
    elif args.extract_plain_text() == "关闭":
        database.set_auto_push(qq, 0)
        await academy_activity.finish(Message("已关闭活动推送"))


@help.handle()
async def handle_function(event: Event):
    msg = "指令列表:\n获取全部活动\n获取学院活动\n获取可参加活动\n添加用户\n报名xxxxxxx\n活动xxxxxxx\n活动推送开启/关闭\n注:xxxx为活动ID"
    await academy_activity.finish(Message(msg))


@scheduler.scheduled_job("interval", minutes=1, id="job_10_minutes")
async def update_activity():
    auto_update_list = [row[0] for row in database.get_auto_push()]
    user_info_list = []
    for auto_user in auto_update_list:
        user_info = database.get_user_token(auto_user)
        user_cid = database.get_user_cid(auto_user)
        user_info_list.append({"token": user_info[0], "sid": user_info[1], "cid": user_cid})
    add_activity = database.auto_push(user_info_list)

    cids = []
    for cid in api.get_activity_mapping(user_info_list[0]["token"], user_info_list[0]["sid"])["data"]["list"][2][
        "infoList"]:
        item = {
            "id": cid["id"],
            "name": cid["name"]
        }
        cids.append(item)

    msg = ""
    for activity in add_activity:
        msg += f'活动名称:{activity["name"]}\n'
        msg += f'活动分值:{activity["credit"]}\n'
        msg += f'分值类型:{activity["categoryName"]}\n'
        for college in cids:
            if activity["allow_colleg"] is None:
                activity["allow_colleg"] = "全部学院"
            elif activity["allow_colleg"] == college["id"]:
                activity["allow_colleg"] = college["name"]
        msg += f'所属学院:{activity["allow_colleg"]}\n'
        msg += f'报名时间:{activity["joinStartTime"]}\n'
        msg += f'开始时间:{activity["startTime"]}\n'
        msg += f'结束时间:{activity["endTime"]}\n'
        msg += f'可参与人数:{activity["allowUserCount"]}\n'
        msg += f'已报名人数:{activity["joinUserCount"]}\n'
        msg += f'活动状态:{activity["statusName"]}\n'
        msg += f'活动ID:{activity["id"]}\n'
        msg += "\n"

    if msg != "":
        # 调用主动发送消息的函数
        await send_message_to_users(msg, qq_list=auto_update_list)


# 发送消息函数，放在外部可以复用
async def send_message_to_users(msg: str, qq_list: list):
    # 获取可用的 Bot 实例
    bot = get_bot()
    for qq in qq_list:
        await bot.send_private_msg(user_id=qq, message=msg)
