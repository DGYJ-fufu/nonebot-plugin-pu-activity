from typing import Type

import nonebot
from nonebot import get_plugin_config, on_keyword, on_command, require, get_bot
from nonebot.adapters import MessageTemplate, Event
from nonebot.adapters.onebot.v11 import Message, Event, Bot
from nonebot.internal.matcher import Matcher
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me, ArgumentParser
from nonebot.params import CommandArg, ArgPlainText
from nonebot.typing import T_State
from .services import *


def user_add_handler(matcher: Type[Matcher], service: APIService):
    """添加或更新用户数据消息事件处理函数"""

    @matcher.handle()
    async def _(state: T_State, event: Event):
        state["qq"] = event.get_user_id()

    @matcher.got("user_info", prompt=MessageTemplate("⚙️请输入用户信息\n格式如下:\n账号:密码:学校全称"))
    async def _(state: T_State, user_info: str = ArgPlainText()):
        """添加或更新用户信息"""
        state["username"], state["password"], state["school"] = user_info.split(":")  # 获取输入的用户信息
        user = await get_user(state["qq"])
        if user is None:
            res = await add_user(service, int(state["qq"]), state["username"], state["password"], state["school"])
            if res == 2:
                await matcher.finish(MessageTemplate("账号信息错误"))
            elif res == 1:
                await matcher.finish(MessageTemplate("账号数据保存异常"))
            elif res == 0:
                await matcher.finish(MessageTemplate("用户数据添加成功"))
        else:
            res = await update_user(service, int(state["qq"]), state["username"], state["password"], state["school"])
            if res == 2:
                await matcher.finish(MessageTemplate("账号信息错误"))
            elif res == 0:
                await matcher.finish(MessageTemplate("用户数据更新成功"))


def all_activity_handlers(matcher: Type[Matcher], service: APIService):
    """获取活动消息事件处理函数"""

    @matcher.handle()
    async def _(event: Event):
        qq = int(event.get_user_id())
        user = await get_user(qq)
        if user is not None:
            res = await get_activity_list(service, qq)
            if res == 1:
                await matcher.finish(MessageTemplate("用户数据错误,请检查用户数据"))
            elif res == 2:
                await update_token(service, qq)
                await matcher.finish(MessageTemplate("请求错误,刷新token,请重试"))
            elif res is None:
                await update_token(service, qq)
                await matcher.finish(MessageTemplate("请求错误,刷新token,请重试"))
            else:
                msg = ""
                for activity in res:
                    msg += f'✨活动名称:{activity["name"]}\n'
                    msg += f'🏷️️活动类型:{activity["categoryName"]}\n'
                    msg += f'💯活动分值:{activity["credit"]}\n'
                    msg += f'🕐报名开始时间:{activity["joinStartTime"]}\n'
                    msg += f'🕐报名结束时间:{activity["joinEndTime"]}\n'
                    msg += f'🕒活动开始时间:{activity["startTime"]}\n'
                    msg += f'🕓活动结束时间:{activity["endTime"]}\n'
                    msg += f'👉可参与人数:{activity["allowUserCount"]}\n'
                    msg += f'🤚已报名人数:{activity["joinUserCount"]}\n'
                    msg += f'🏫活动院系:'
                    if len(activity["allowCollege"]) > 0:
                        msg += '\n'
                        for allowCollege in activity["allowCollege"]:
                            msg += f'\t{allowCollege["name"]}\n'
                    else:
                        msg += '全部院系\n'
                    msg += f'🧸活动年级:'
                    if len(activity["allowYear"]) > 0:
                        msg += '\n\t'
                        for allowYear in activity["allowYear"]:
                            msg += f'{allowYear["name"]}'
                            if allowYear != activity["allowYear"][len(activity["allowYear"]) - 1]:
                                msg += ','
                            else:
                                msg += '\n'
                    else:
                        msg += '全部年级\n'
                    msg += f'⛱️活动地址:{activity["address"]}\n'
                    msg += f'⭐活动状态:{activity["statusName"]}\n'
                    msg += f'🆔活动ID:{activity["id"]}'
                    if activity != res[len(res) - 1]:
                        msg += "\n\n"
                await matcher.finish(MessageTemplate(msg))
        else:
            await matcher.finish(MessageTemplate("用户数据错误,请检查用户数据"))


def get_can_join_activity_handler(matcher: Type[Matcher], service: APIService):
    """获取可参加活动消息事件处理函数"""

    @matcher.handle()
    async def _(event: Event):
        qq = int(event.get_user_id())
        user = await get_user(qq)
        if user is not None:
            res = await can_join_activity(service, qq)
            if res is None:
                await update_token(service, qq)
                await matcher.finish(MessageTemplate("请求错误,刷新token,请重试"))
            elif res == 1:
                await matcher.finish(MessageTemplate("用户数据错误,请检查用户数据"))
            elif res == 2:
                await update_token(service, qq)
                await matcher.finish(MessageTemplate("请求错误,刷新token,请重试"))
            else:
                msg = ""
                for activity in res:
                    msg += f'✨活动名称:{activity["name"]}\n'
                    msg += f'🏷️️活动类型:{activity["categoryName"]}\n'
                    msg += f'💯活动分值:{activity["credit"]}\n'
                    msg += f'🕐报名开始时间:{activity["joinStartTime"]}\n'
                    msg += f'🕐报名结束时间:{activity["joinEndTime"]}\n'
                    msg += f'🕒活动开始时间:{activity["startTime"]}\n'
                    msg += f'🕓活动结束时间:{activity["endTime"]}\n'
                    msg += f'👉可参与人数:{activity["allowUserCount"]}\n'
                    msg += f'🤚已报名人数:{activity["joinUserCount"]}\n'
                    msg += f'🏫活动院系:'
                    if len(activity["allowCollege"]) > 0:
                        msg += '\n'
                        for allowCollege in activity["allowCollege"]:
                            msg += f'\t{allowCollege["name"]}\n'
                    else:
                        msg += '全部院系\n'
                    msg += f'🧸活动年级:'
                    if len(activity["allowYear"]) > 0:
                        msg += '\n\t'
                        for allowYear in activity["allowYear"]:
                            msg += f'{allowYear["name"]}'
                            if allowYear != activity["allowYear"][len(activity["allowYear"]) - 1]:
                                msg += ','
                            else:
                                msg += '\n'
                    else:
                        msg += '全部年级\n'
                    msg += f'⛱️活动地址:{activity["address"]}\n'
                    msg += f'⭐活动状态:{activity["statusName"]}\n'
                    msg += f'🆔活动ID:{activity["id"]}'
                    if activity != res[len(res) - 1]:
                        msg += "\n\n"
                if msg != "":
                    await matcher.finish(MessageTemplate(msg))
                else:
                    await matcher.finish(Message("暂无可参加活动"))
        else:
            await matcher.finish(MessageTemplate("用户数据错误,请检查用户数据"))


def auto_push_handler(matcher: Type[Matcher]):
    """活动推送消息事件处理函数"""

    @matcher.handle()
    async def _(event: Event, args: Message = CommandArg()):
        qq = int(event.get_user_id())
        if status := args.extract_plain_text():
            res = None
            if status == "开启":
                res = await database_switch_push(qq, 1)
            elif status == "关闭":
                res = await database_switch_push(qq, 0)
            if res == 0:
                await matcher.finish(MessageTemplate("操作成功"))
            else:
                await matcher.finish(MessageTemplate("操作失败"))


def my_activity_handler(matcher: Type[Matcher], service: APIService):
    """我的活动消息事件处理函数"""

    @matcher.handle()
    async def _(event: Event):
        qq = int(event.get_user_id())
        user = await get_user(qq)
        if user is not None:
            res = await get_my_activity(service, qq)
            if res is None:
                await update_token(service, qq)
                await matcher.finish(MessageTemplate("请求错误,刷新token,请重试"))
            elif res == 1:
                await matcher.finish(MessageTemplate("用户数据错误,请检查用户数据"))
            elif res == 2:
                await update_token(service, qq)
                await matcher.finish(MessageTemplate("请求错误,刷新token,请重试"))
            else:
                msg = f'📋未开始活动:\n\n'
                if len(res[1]) > 0:
                    for activity in res[1]:
                        msg += f'✨活动名称:{activity["name"]}\n'
                        msg += f'🕑开始时间:{activity["startTime"]}\n'
                        msg += f'🕓结束时间:{activity["endTime"]}\n'
                        msg += f'⛱️活动地址:{activity["address"]}\n'
                        msg += f'🆔活动ID:{activity["id"]}\n\n'
                else:
                    msg += "暂无活动\n\n"

                msg += f'📝待审核活动:\n\n'
                if len(res[0]) > 0:
                    for activity in res[0]:
                        msg += f'✨活动名称:{activity["name"]}\n'
                        msg += f'🕑开始时间:{activity["startTime"]}\n'
                        msg += f'🕓结束时间:{activity["endTime"]}\n'
                        msg += f'⛱️活动地址:{activity["address"]}\n'
                        msg += f'🆔活动ID:{activity["id"]}'
                        if activity != res[len(res[0]) - 1]:
                            msg += "\n\n"
                else:
                    msg += "暂无活动"

                await matcher.finish(MessageTemplate(msg))

        else:
            await matcher.finish(MessageTemplate("用户数据错误,请检查用户数据"))


def activity_info_handler(matcher: Type[Matcher], service: APIService):
    """活动信息消息事件处理函数"""

    @matcher.handle()
    async def _(event: Event, args: Message = CommandArg()):
        qq = int(event.get_user_id())
        user = await get_user(qq)
        if user is not None:
            if activity_id := args.extract_plain_text():
                res = await get_activity_info(service, qq, int(activity_id))
                if res is None:
                    await update_token(service, qq)
                    await matcher.finish(MessageTemplate("请求错误,刷新token,请重试"))
                elif res == 1:
                    await matcher.finish(MessageTemplate("用户数据错误,请检查用户数据"))
                elif res == 2:
                    await update_token(service, qq)
                    await matcher.finish(MessageTemplate("请求错误,刷新token,请重试"))
                else:
                    activity_msg = res["data"]["baseInfo"]
                    msg = f'✨活动名称:{activity_msg["name"]}\n'
                    msg += f'🏷️️活动类型:{activity_msg["categoryName"]}\n'
                    msg += f'💯活动分值:{activity_msg["credit"]}\n'
                    msg += f'🕐报名开始时间:{activity_msg["joinStartTime"]}\n'
                    msg += f'🕐报名结束时间:{activity_msg["joinEndTime"]}\n'
                    msg += f'🕒活动开始时间:{activity_msg["startTime"]}\n'
                    msg += f'🕓活动结束时间:{activity_msg["endTime"]}\n'
                    msg += f'👉可参与人数:{activity_msg["allowUserCount"]}\n'
                    msg += f'🤚已报名人数:{activity_msg["joinUserCount"]}\n'
                    msg += f'🏫活动院系:'
                    if len(activity_msg["allowCollege"]) > 0:
                        msg += '\n'
                        for allowCollege in activity_msg["allowCollege"]:
                            msg += f'\t{allowCollege["name"]}\n'
                    else:
                        msg += '全部院系\n'
                    msg += f'🧸活动年级:'
                    if len(activity_msg["allowYear"]) > 0:
                        msg += '\n\t'
                        for allowYear in activity_msg["allowYear"]:
                            msg += f'{allowYear["name"]}'
                            if allowYear != activity_msg["allowYear"][len(activity_msg["allowYear"]) - 1]:
                                msg += ','
                            else:
                                msg += '\n'
                    else:
                        msg += '全部年级\n'
                    msg += f'⛱️活动地址:{activity_msg["address"]}\n'
                    msg += f'⭐活动状态:{activity_msg["statusName"]}'
                    await matcher.finish(MessageTemplate(msg))
            else:
                await matcher.finish(MessageTemplate("请输入活动ID"))
        else:
            await matcher.finish(MessageTemplate("用户数据错误,请检查用户数据"))


def join_activity_handler(matcher: Type[Matcher], service: APIService):
    """报名消息事件处理函数"""

    @matcher.handle()
    async def _(event: Event, args: Message = CommandArg()):
        qq = int(event.get_user_id())
        user = await get_user(qq)
        if user is not None:
            if activity_id := args.extract_plain_text():
                res = await join_activity(service, qq, int(activity_id))
                if res is None:
                    await update_token(service, qq)
                    await matcher.finish(MessageTemplate("请求错误,刷新token,请重试"))
                elif res == 2:
                    await update_token(service, qq)
                    await matcher.finish(MessageTemplate("请求错误,刷新token,请重试"))
                elif res == 1:
                    await matcher.finish(MessageTemplate("用户数据错误,请检查用户数据"))
                else:
                    await matcher.finish(MessageTemplate(res))
        else:
            await matcher.finish(MessageTemplate("用户数据错误,请检查用户数据"))


def reservation_handler(matcher: Type[Matcher], service: APIService, scheduler):
    """预约消息事件处理函数"""

    @matcher.handle()
    async def _(event: Event, args: Message = CommandArg()):
        qq = int(event.get_user_id())
        user = await get_user(qq)
        if user is not None:
            if activity_id := args.extract_plain_text():
                res = await reservation_add_activity(service, qq, int(activity_id), scheduler)
                if res is None:
                    await matcher.finish(MessageTemplate("添加任务失败"))
                elif res == 1:
                    await matcher.finish(MessageTemplate("任务添加错误,请检查任务信息是否重复"))
                else:
                    await matcher.finish(MessageTemplate("添加成功"))


def find_reservation_handler(matcher: Type[Matcher], scheduler):
    """查询预约消息事件处理函数"""

    @matcher.handle()
    async def _(event: Event):
        jobs = scheduler.get_jobs()
        for job in jobs:
            nonebot.logger.info(job)

        qq = int(event.get_user_id())
        res = await get_reservation_qq(qq)
        if res is None:
            await matcher.finish(MessageTemplate("暂无预约任务"))
        else:
            await matcher.finish(MessageTemplate(res))


def remove_reservation_handler(matcher: Type[Matcher], scheduler):
    """删除预约"""

    @matcher.handle()
    async def _(event: Event, args: Message = CommandArg()):
        qq = int(event.get_user_id())
        if activity_id := args.extract_plain_text():
            res = await remove_reservation(qq, int(activity_id), scheduler)
            if res is None:
                await matcher.finish(MessageTemplate("删除失败,请检查活动信息"))
            else:
                await matcher.finish(MessageTemplate(f"{activity_id}删除成功"))


def update_token_handler(matcher: Type[Matcher], service: APIService):
    """刷新令牌消息事件处理函数"""

    @matcher.handle()
    async def _(event: Event):
        qq = int(event.get_user_id())
        user = await get_user(qq)
        if user is not None:
            res = await update_token(service, qq)
            if res == 0:
                await matcher.finish(MessageTemplate("Token刷新成功"))
            elif res == 1:
                await matcher.finish(MessageTemplate("用户数据错误,请检查用户数据"))
            elif res == 2:
                await matcher.finish(MessageTemplate("用户数据错误,请检查用户数据"))
        else:
            await matcher.finish(MessageTemplate("用户数据错误,请检查用户数据"))


def my_credit_handler(matcher: Type[Matcher], service: APIService):
    """查询分数"""

    @matcher.handle()
    async def _(event: Event):
        qq = int(event.get_user_id())
        res = await find_my_credit(service, qq)
        if res is None:
            await update_token(service, qq)
            await matcher.finish(MessageTemplate("请求错误,刷新token,请重试"))
        elif res == 1:
            await matcher.finish(MessageTemplate("用户数据错误,请检查用户数据"))
        elif res == 2:
            await update_token(service, qq)
            await matcher.finish(MessageTemplate("请求错误,刷新token,请重试"))
        else:
            msg = f'实践学分:{res["credit"]}\n'
            msg += f'诚信值:{res["cx"]}'
            await matcher.finish(MessageTemplate(msg))


def group_add_handler(matcher: Type[Matcher], service: APIService):
    """添加群推送"""

    @matcher.got("school", prompt=MessageTemplate("⚙️请输入学校全称"))
    async def _(event: Event, school: str = ArgPlainText()):
        if school:
            group_id = event.get_session_id().split("_")[1]
            nonebot.logger.info("GroupID:" + group_id)
            res = await create_group(service, int(group_id), school)
            if res == 0:
                await matcher.finish(MessageTemplate("添加完成"))
            else:
                await matcher.finish(MessageTemplate("添加失败，请检查信息"))


def auto_push_group_handler(matcher: Type[Matcher]):
    """切换群推送状态"""

    @matcher.handle()
    async def _(event: Event, args: Message = CommandArg()):
        group_id = int(event.get_session_id().split("_")[1])
        nonebot.logger.info("GroupID:" + str(group_id))
        if status := args.extract_plain_text():
            if status == "开启":
                res = await switch_group_push(group_id, 1)
                if res is None:
                    await matcher.finish(MessageTemplate("失败"))
                else:
                    await matcher.finish(MessageTemplate("成功"))

            elif status == "关闭":
                res = await switch_group_push(group_id, 0)
                if res is None:
                    await matcher.finish(MessageTemplate("失败"))
                else:
                    await matcher.finish(MessageTemplate("成功"))


def help_cmd_handler(matcher: Type[Matcher]):
    """帮助消息事件处理函数"""

    @matcher.handle()
    async def _():
        msg = (
            "📝指令列表:\n"
            "✨添加用户\n"
            "✨获取活动\n"
            "✨获取可参加活动\n"
            "✨活动推送开启/关闭\n"
            "✨我的活动\n"
            "✨活动🆔\n"
            "✨报名🆔\n"
            "✨预约🆔\n"
            "✨查询预约\n"
            "✨删除预约🆔\n"
            "✨刷新token\n"
            "✨查询分数\n"
            "⚠️注:🆔为活动ID"
        )
        await matcher.finish(Message(msg))
