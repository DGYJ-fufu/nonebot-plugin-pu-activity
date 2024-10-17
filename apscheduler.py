import nonebot
from datetime import datetime
from .API.Network.api_service import APIService
from .services import *


# 周期任务
async def push_handler(service: APIService):
    """周期检测活动更新"""
    add_activity_list = []
    nonebot.logger.info("Start time:{}", datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))  # 日志输出
    push_user_list = await database_get_push_user()
    for push_user_info in push_user_list:
        activities = await get_activity_list(service, push_user_info["users"][0].qq)
        if activities:
            if activities == 2:
                await update_token(service, push_user_info["users"][0].qq)
                return
            else:
                # 获取新活动
                activity_list = []
                for activity in activities:
                    result = await database_get_activity(activity["id"])
                    if result is not None:
                        continue
                    else:
                        activity_list.append(activity)
                        await database_add_activity(activity["id"])
                # 获取新活动推送对象
                push_users = []
                for user in push_user_info["users"]:
                    push_users.append(user.qq)
                # 数据封装
                add_activity_list.append(
                    {
                        "push_activities": activity_list,
                        "push_users": push_users
                    }
                )
    # 输出推送列表
    nonebot.logger.info(add_activity_list)
    # 活动推送
    for add_push_list in add_activity_list:
        if add_push_list["push_activities"]:
            msg = ""
            for activity in add_push_list["push_activities"]:
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
                if activity != add_push_list["push_activities"][len(add_push_list["push_activities"]) - 1]:
                    msg += "\n\n"
            await send_message_to_users(msg, add_push_list["push_users"])
    nonebot.logger.info("End time:{}", datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))  # 日志输出


async def reservation_info_update(service: APIService):
    """周期检查预约活动时间是否有更改"""
    async with AsyncSessionManager() as session:
        reservations = await ReservationCRUD.get_all_reservations(session)
        for reservation in reservations:
            res = await get_activity_info(service, reservation.user_id, reservation.activity_id)
            if res is not None and res != 1 and res != 2:
                if datetime.strptime(res["data"]["baseInfo"]["joinStartTime"],
                                     "%Y-%m-%d %H:%M:%S") != reservation.reservation_time:
                    cache = reservation.to_dict()
                    cache["reservation_time"] = datetime.strptime(res["data"]["baseInfo"]["joinStartTime"],
                                                                  "%Y-%m-%d %H:%M:%S")
                    await ReservationCRUD.update_reservation(session, reservation.id, cache)
