import nonebot
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
        else:
            nonebot.logger.info(res["message"])
            return res["message"]
    return 1


async def send_message_to_users(msg: str, qq_list: list):
    """发送消息函数，放在外部可以复用"""
    bot = get_bot()
    for qq in qq_list:
        await bot.send_private_msg(user_id=qq, message=msg)


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
            activity_info["status"] = status
            await ReservationCRUD.update_reservation(session, activity_info["reservation_id"], activity_info)
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

        # 添加定时任务
        scheduler.add_job(
            reservation_join,
            "date",
            run_date=reservation_time,
            args=[service, qq, int(activity_id)]
        )

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
    res = await join_activity(service, qq, activity_id)
    if res is None:
        await send_message_to_users("请求失败", [qq])
        await modify_reservation_status(qq, activity_id, 2)
    elif res == 1:
        await send_message_to_users("用户信息错误", [qq])
        await modify_reservation_status(qq, activity_id, 2)
    elif res == 2:
        await send_message_to_users("用户token失效", [qq])
        await modify_reservation_status(qq, activity_id, 2)
    else:
        await send_message_to_users(str(res), [qq])
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
                    args=[service, reservation.user_id, int(reservation.activity_id)]
                )
    nonebot.logger.info('预约任务初始化完成')
    nonebot.logger.info(f'预约任务数量:{len(scheduler.get_jobs())}')
