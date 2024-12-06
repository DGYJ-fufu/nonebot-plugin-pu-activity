import nonebot
import asyncio
from datetime import datetime
from nonebot import get_bot
from .API.Database.CRUD.crud import *
from .API.Database.Models.models import User
from .API.Database.session import AsyncSessionManager
from .API.Network.api_service import APIService


async def add_user(service: APIService, qq: int, username: str, password: str, school: str):
    """添加用户"""
    user_info = {
        "qq": qq,
        "username": username,
        "password": password,
    }

    sids = await service.get_sid()
    for sid_item in sids["data"]["list"]:
        if sid_item["name"] == school:
            user_info["sid"] = sid_item["id"]
            break
        else:
            continue

    user = await service.login(user_info["username"], user_info["password"], user_info["sid"])
    if user is not None and user["code"] == 0:
        user_info["token"], user_info["cid"], user_info["yid"] = (
            user["data"]["token"],
            user["data"]["baseUserInfo"]["cid"],
            user["data"]["baseUserInfo"]["yid"]
        )
    else:
        return 2

    async with AsyncSessionManager() as session:
        # 创建用户
        new_user = User(**user_info)
        session.add(new_user)
        await session.commit()

        # 获取用户
        user = await UserCRUD.get_user(session, qq)
        # 确认用户信息已保存
        if user is not None:
            return 0
        else:
            return 1


async def update_user(service: APIService, qq: int, username: str, password: str, school: str):
    """更新用户"""
    user_info = {
        "qq": qq,
        "username": username,
        "password": password,
    }
    sids = await service.get_sid()
    if sids is not None:
        for sid_item in sids["data"]["list"]:
            if sid_item["name"] == school:
                user_info["sid"] = sid_item["id"]
                break
            else:
                continue
    else:
        return 2

    user = await service.login(user_info["username"], user_info["password"], user_info["sid"])
    if user is not None and user["code"] == 0:
        user_info["token"], user_info["cid"], user_info["yid"] = (
            user["data"]["token"],
            user["data"]["baseUserInfo"]["cid"],
            user["data"]["baseUserInfo"]["yid"]
        )
    else:
        return 2

    async with AsyncSessionManager() as session:
        await UserCRUD.update_user(session, qq, user_info)
        await session.commit()
        return 0


async def get_user(qq: int):
    """获取用户"""
    async with AsyncSessionManager() as session:
        # 查询用户
        user = await UserCRUD.get_user(session, qq)
        if user is not None:
            return user.to_dict()
        else:
            return None


async def update_token(service: APIService, qq: int):
    """刷新token"""
    user = await get_user(qq)
    if user is not None:
        res = await service.login(user["username"], user["password"], user["sid"])
        if res is not None and res["code"] == 0:
            user["token"] = res["data"]["token"]
            async with AsyncSessionManager() as session:
                await UserCRUD.update_user(session, qq, user)
                await session.commit()
                return 0
        else:
            return 2
    else:
        return 1


async def can_join_activity(service: APIService, qq: int):
    """获取可加入活动列表"""
    activity_list = []
    user = await get_user(qq)
    if user is not None:
        activities = await service.get_activity_list_filter(
            token=user["token"],
            sid=user["sid"],
            num=50,
            status=1
        )
        if activities is not None:
            if activities["code"] == 0:
                activities = activities["data"]["list"]
                if len(activities) == 0:
                    print("暂无可参加活动")
                else:
                    for activity in activities:
                        # 去除列表中报名已结束以及报名人数已满活动
                        if (activity["startTimeValue"] == "报名已结束" or
                                activity["allowUserCount"] == activity["joinUserCount"]
                        ):
                            continue
                        else:
                            # 查询初步筛选后的活动详细信息
                            activity_info = await service.get_activity_info(
                                token=user["token"],
                                sid=user["sid"],
                                activity_id=activity["id"]
                            )
                            if activity_info is not None and activity_info["code"] == 0:
                                cid_status = False
                                year_status = False
                                # 判断是否符合参与学院要求
                                if len(activity_info["data"]["baseInfo"]["allowCollege"]) != 0:
                                    for cid in activity_info["data"]["baseInfo"]["allowCollege"]:
                                        if cid["id"] == user["cid"]:
                                            cid_status = True
                                else:
                                    cid_status = True
                                # 判断是否符合参与年级要求
                                if len(activity_info["data"]["baseInfo"]["allowYear"]) != 0:
                                    for year in activity_info["data"]["baseInfo"]["allowYear"]:
                                        if year["id"] == user["yid"]:
                                            year_status = True
                                else:
                                    year_status = True
                                # 将可参与的活动进行输出
                                if cid_status and year_status:
                                    activity_info = activity_info["data"]["baseInfo"]
                                    activity_info["id"] = activity["id"]
                                    activity_list.append(activity_info)
                            else:
                                return 2
                return activity_list
            return 2
        return None
    return 1


async def get_activity_list(service: APIService, qq: int):
    """获取活动列表"""
    activity_list = []
    user = await get_user(qq)
    if user is not None:
        activities = await service.get_activity_list(
            token=user["token"],
            sid=user["sid"],
            num=40
        )
        if activities is not None:
            if activities["code"] == 0:
                activities = activities["data"]["list"]
                if len(activities) == 0:
                    return None
                else:
                    for activity in activities:
                        if activity["startTimeValue"] != "报名已结束":
                            res = await service.get_activity_info(
                                token=user["token"],
                                sid=user["sid"],
                                activity_id=activity["id"]
                            )
                            res = res["data"]["baseInfo"]
                            res["id"] = activity["id"]
                            activity_list.append(res)
                        else:
                            continue
                return activity_list
            return 2
        return None
    return 1


async def get_activity_info(service: APIService, qq: int, activity_id: int):
    """获取活动详情"""
    user = await get_user(qq)
    if user is not None:
        activity_info = await service.get_activity_info(
            token=user["token"],
            sid=user["sid"],
            activity_id=activity_id
        )
        if activity_info is not None:
            if activity_info["code"] == 0:
                return activity_info
            return 2
        else:
            return None
    return 1


async def get_my_activity(service: APIService, qq: int):
    """获取我的活动"""
    user = await get_user(qq)
    if user is not None:
        my_activity_list = []
        res = await service.get_my_activity_list(
            token=user["token"],
            sid=user["sid"],
            type_id=5
        )
        my_activity_list.append(res["data"]["list"])

        res = await service.get_my_activity_list(
            token=user["token"],
            sid=user["sid"]
        )

        if res["code"] == 0:
            my_activity_list.append(res["data"]["list"])
        else:
            return 2
        return my_activity_list

    return 1


async def join_activity(service: APIService, qq: int, activity_id: int):
    """活动报名"""
    user = await get_user(qq)
    if user is not None:
        res = await service.join(user["token"], user["sid"], activity_id)
        if res is None:
            return None
        elif res["code"] == 401:
            return 2
        elif res["code"] == 500:
            return 3
        else:
            nonebot.logger.info(res["message"])
            return res["message"]
    return 1


async def send_message_to_users(msg: str, qq_list: list):
    """发送消息函数，放在外部可以复用"""
    bot = get_bot()
    for qq in qq_list:
        await bot.send_private_msg(user_id=qq, message=msg)


async def send_message_to_group(msg: str, group_list: list):
    """发送群消息函数，可以复用"""
    bot = get_bot()
    for group in group_list:
        await bot.send_group_msg(group_id=group, message=msg)


async def database_get_activities():
    """获取数据库中活动列表"""
    async with AsyncSessionManager() as session:
        activities = await ActivityCRUD.get_activities(session)
        if len(activities) == 0:
            return None
        else:
            return activities


async def database_get_push_user():
    """获取订阅用户"""
    async with AsyncSessionManager() as session:
        push_user_list = []
        sids = await UserCRUD.get_push_user_sids(session)
        if sids is not None:
            for sid in sids:
                users = await UserCRUD.get_push_user(session, sid)
                push_user_list.append({
                    "sid": sid,
                    "users": users
                })
        return push_user_list


async def database_switch_push(qq: int, status: int):
    """切换推送状态"""
    user = await get_user(qq)
    if user is not None:
        user["push"] = status
        async with AsyncSessionManager() as session:
            await UserCRUD.update_user(session, qq, user)
            await session.commit()
            return 0
    return 1


async def database_get_activity(activity_id: int):
    """查询活动是否在库"""
    async with AsyncSessionManager() as session:
        activity = await ActivityCRUD.get_activity(session, activity_id)
        if activity is None:
            return None
        else:
            return activity


async def database_add_activity(activity_id: int):
    """新活动入库"""
    activity = {
        "activity_id": activity_id
    }
    async with AsyncSessionManager() as session:
        activity = await ActivityCRUD.create_activity(session, activity)
        if activity is None:
            return None
        else:
            return activity


async def get_reservation_qq(qq: int):
    """获取预约信息"""
    async with AsyncSessionManager() as session:
        reservations = await ReservationCRUD.get_reservation_qq(session, qq)
        if len(reservations) == 0:
            return None
        else:
            msg = ""
            for reservation in reservations:
                msg += f'预约ID:{reservation.id}\n'
                msg += f'活动ID:{reservation.activity_id}\n'
                msg += f'预约时间:{datetime.strftime(reservation.reservation_time, "%Y-%m-%d %H:%M:%S")}\n'
                if reservation.status == 0:
                    msg += "任务状态:等待执行"
                elif reservation.status == 1:
                    msg += "任务状态:执行结束"
                elif reservation.status == 2:
                    msg += "任务状态:执行错误"
                if reservation != reservations[len(reservations) - 1]:
                    msg += '\n\n'
            return msg


async def modify_reservation_status(qq: int, activity_id: int, status: int):
    """修改活动预约状态"""
    async with AsyncSessionManager() as session:
        activity_info = await ReservationCRUD.get_reservation_qq_id(session, qq, activity_id)
        if activity_info is None:
            return None
        else:
            activity_info = activity_info.to_dict()
            activity_info["status"] = status
            await ReservationCRUD.update_reservation(session, activity_info["id"], activity_info)
            return activity_info


async def reservation_add_activity(service: APIService, qq: int, activity_id: int, scheduler):
    """添加活动预约"""
    activity = {
        'user_id': qq,
        'activity_id': activity_id,
        'created_at': datetime.now()
    }
    activity_info = await get_activity_info(service, qq, activity_id)
    if activity_info is not None and activity_info != 2 and activity_info != 1:
        reservation_time = datetime.strptime(activity_info["data"]["baseInfo"]["joinStartTime"],
                                             "%Y-%m-%d %H:%M:%S")

        try:
            # 添加定时任务
            scheduler.add_job(
                reservation_join,
                "date",
                run_date=reservation_time,
                id=f"{qq}_{activity_id}",
                args=[service, qq, int(activity_id)]
            )
        except Exception as e:
            return 1

        # 预约任务持久化
        activity["reservation_time"] = reservation_time
        async with AsyncSessionManager() as session:
            activity = await ReservationCRUD.create_reservation(session, activity)
            if activity is None:
                return None
            else:
                return activity


async def reservation_join(service: APIService, qq: int, activity_id: int):
    """预约活动报名"""
    request_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    res = await join_activity(service, qq, activity_id)
    nonebot.logger.info("POST End time:{}", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])  # 日志输出
    nonebot.logger.info("POST Msg", str(res))
    if res is None:
        await send_message_to_users(
            f'请求失败,开始尝试挣扎一下\n请求时间:{str(request_start_time)}',
            [qq]
        )
        count = 0
        while True:
            # 重试4分钟，直到收到响应
            if count < 120:
                try:
                    nonebot.logger.info("POST Start:{}", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])  # 日志输出
                    nonebot.logger.info("POST Num:{}", count)  # 日志输出
                    res = await join_activity(service, qq, activity_id)
                    if res is None:
                        count += 1
                    elif res != 1 and res != 2:
                        await send_message_to_users(str(res), [qq])
                        await modify_reservation_status(qq, activity_id, 1)
                        return
                except Exception as e:
                    count += 1
                    nonebot.logger.info("Error:{}", str(e))
            else:
                await send_message_to_users("疑似PU接口问题,放弃挣扎了", [qq])
                await modify_reservation_status(qq, activity_id, 2)
                return

    elif res == 1:
        await send_message_to_users("用户信息错误", [qq])
        await modify_reservation_status(qq, activity_id, 2)
    elif res == 2:
        await send_message_to_users("用户token失效", [qq])
        await modify_reservation_status(qq, activity_id, 2)
    else:
        await send_message_to_users(
            f"{str(res)}\n"
            f"请求时间:{str(request_start_time)}\n"
            f'响应时间:{str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])}',
            [qq]
        )
        await modify_reservation_status(qq, activity_id, 1)


async def reservation_init(service: APIService, scheduler):
    """预约任务初始化"""
    async with AsyncSessionManager() as session:
        reservation_list = await ReservationCRUD.get_all_reservations(session)
        if reservation_list is not None:
            for reservation in reservation_list:
                # 添加定时任务
                scheduler.add_job(
                    reservation_join,
                    "date",
                    run_date=reservation.reservation_time,
                    id=f"{reservation.user_id}_{reservation.activity_id}",
                    args=[service, reservation.user_id, int(reservation.activity_id)]
                )
    nonebot.logger.info('预约任务初始化完成')
    nonebot.logger.info(f'预约任务数量:{len(scheduler.get_jobs())}')


async def remove_reservation(qq: int, activity_id: int, scheduler):
    """删除预约活动"""
    async with AsyncSessionManager() as session:
        activity_info = await ReservationCRUD.get_reservation_qq_id(session, qq, activity_id)
        if activity_info is not None:
            activity_info = activity_info.to_dict()
            await ReservationCRUD.delete_reservation(session, activity_info["id"])
            scheduler.remove_job(f"{qq}_{activity_id}")
            return 1
        else:
            return None


async def find_my_credit(service: APIService, qq: int):
    """查询分数"""
    user = await get_user(qq)
    if user is not None:
        info = await service.info(user["token"], user["sid"])
        if info is not None:
            if info["code"] == 0:
                return info["data"]
            else:
                return 2
        else:
            return None
    else:
        return 1


async def get_push_group():
    """获取订阅群号"""
    async with AsyncSessionManager() as session:
        push_group_list = []
        sids = await GroupCRUD.get_push_sids(session)
        if sids is not None:
            for sid in sids:
                groups = await GroupCRUD.get_push_sid(session, sid)
                push_group_list.append({
                    "sid": sid,
                    "groups": groups
                })
                nonebot.logger.info("群推送列表:" + str(push_group_list))
        return push_group_list


async def create_group(service: APIService, group_id: int, school: str):
    """添加群推送"""
    group = {
        'group_id': group_id
    }

    sids = await service.get_sid()
    for sid_item in sids["data"]["list"]:
        if sid_item["name"] == school:
            group["sid"] = sid_item["id"]
            break
        else:
            continue

    async with AsyncSessionManager() as session:
        result = await GroupCRUD.create_group(session, group)
        if result is not None:
            return 0
        else:
            return 1


async def switch_group_push(group_id: int, status: int):
    """切换群推送状态"""
    async with AsyncSessionManager() as session:
        group = await GroupCRUD.get_groups_id(session, group_id)
        if group is None:
            return None
        else:
            group = group.to_dict()
            group["push"] = status
            await GroupCRUD.update_group(session, group_id, group)
            return 0
