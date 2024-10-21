from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..Models.models import User, Reservation, Activity, Group


class UserCRUD:
    @staticmethod
    async def create_user(session: AsyncSession, user_data: dict):
        """创建用户并保存到数据库。"""
        user = User(**user_data)
        session.add(user)
        await session.commit()  # 提交事务
        await session.refresh(user)  # 刷新以获取数据库中的新数据
        return user

    @staticmethod
    async def get_user(session: AsyncSession, qq: int):
        """根据 QQ 号获取用户信息。"""
        result = await session.execute(select(User).where(User.qq == qq))
        return result.scalar_one_or_none()  # 获取单个用户或 None

    @staticmethod
    async def get_push_user(session: AsyncSession, sid: int):
        """根据sid获取数据库订阅用户信息."""
        result = await session.execute(select(User).where((User.sid == sid) & (User.push == 1)))
        return result.scalars().all()

    @staticmethod
    async def get_push_user_sids(session: AsyncSession):
        """获取订阅用户sid列表"""
        result = await session.execute(select(User.sid).where(User.push == 1))
        return result.scalars().all()

    @staticmethod
    async def update_user(session: AsyncSession, qq: int, update_data: dict):
        """更新用户信息。"""
        user = await UserCRUD.get_user(session, qq)
        if user:
            for key, value in update_data.items():
                setattr(user, key, value)  # 更新用户属性
            await session.commit()  # 提交事务
            await session.refresh(user)  # 刷新以获取数据库中的新数据
        return user

    @staticmethod
    async def delete_user(session: AsyncSession, qq: int):
        """删除用户。"""
        user = await UserCRUD.get_user(session, qq)
        if user:
            await session.delete(user)  # 删除用户
            await session.commit()  # 提交事务
        return user


class ReservationCRUD:
    @staticmethod
    async def create_reservation(session: AsyncSession, reservation_data: dict):
        """创建预约并保存到数据库。"""
        reservation = Reservation(**reservation_data)
        session.add(reservation)
        await session.commit()  # 提交事务
        await session.refresh(reservation)  # 刷新以获取数据库中的新数据
        return reservation

    @staticmethod
    async def get_all_reservations(session: AsyncSession):
        """获取所有待完成的预约任务"""
        result = await session.execute(select(Reservation).where(Reservation.status == 0))
        return result.scalars().all()

    @staticmethod
    async def get_reservation(session: AsyncSession, reservation_id: int):
        """根据预约 ID 获取预约信息。"""
        result = await session.execute(select(Reservation).where(Reservation.id == reservation_id))
        return result.scalar_one_or_none()  # 获取单个预约或 None

    @staticmethod
    async def get_reservation_qq(session: AsyncSession, qq: int):
        """根据QQ获取预约信息。"""
        result = await session.execute(select(Reservation).where(Reservation.user_id == qq))
        return result.scalars().all()  # 获取单个预约或 None

    @staticmethod
    async def get_reservation_qq_id(session: AsyncSession, qq: int, activity_id: int):
        """根据QQ与活动ID获取预约信息"""
        result = await session.execute(
            select(Reservation).where((Reservation.user_id == qq) & (Reservation.activity_id == activity_id)))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_reservation(session: AsyncSession, reservation_id: int, update_data: dict):
        """更新预约信息。"""
        reservation = await ReservationCRUD.get_reservation(session, reservation_id)
        if reservation:
            for key, value in update_data.items():
                setattr(reservation, key, value)  # 更新预约属性
            await session.commit()  # 提交事务
            await session.refresh(reservation)  # 刷新以获取数据库中的新数据
        return reservation

    @staticmethod
    async def delete_reservation(session: AsyncSession, reservation_id: int):
        """删除预约。"""
        reservation = await ReservationCRUD.get_reservation(session, reservation_id)
        if reservation:
            await session.delete(reservation)  # 删除预约
            await session.commit()  # 提交事务
        return reservation


class ActivityCRUD:
    @staticmethod
    async def create_activity(session: AsyncSession, activity_data: dict):
        """创建活动并保存到数据库。"""
        activity = Activity(**activity_data)
        session.add(activity)
        await session.commit()  # 提交事务
        await session.refresh(activity)  # 刷新以获取数据库中的新数据
        return activity

    @staticmethod
    async def get_activities(session: AsyncSession):
        """获取数据库中所有的活动"""
        result = await session.execute(select(Activity))
        return result.scalars().all()

    @staticmethod
    async def get_activity(session: AsyncSession, activity_id: int):
        """根据活动 ID 获取活动信息。"""
        result = await session.execute(select(Activity).where(Activity.activity_id == activity_id))
        return result.scalar_one_or_none()  # 获取单个活动或 None

    @staticmethod
    async def update_activity(session: AsyncSession, activity_id: int, update_data: dict):
        """更新活动信息。"""
        activity = await ActivityCRUD.get_activity(session, activity_id)
        if activity:
            for key, value in update_data.items():
                setattr(activity, key, value)  # 更新活动属性
            await session.commit()  # 提交事务
            await session.refresh(activity)  # 刷新以获取数据库中的新数据
        return activity

    @staticmethod
    async def delete_activity(session: AsyncSession, activity_id: int):
        """删除活动。"""
        activity = await ActivityCRUD.get_activity(session, activity_id)
        if activity:
            await session.delete(activity)  # 删除活动
            await session.commit()  # 提交事务
        return activity


class GroupCRUD:

    @staticmethod
    async def create_group(session: AsyncSession, group_data: dict):
        """创建活动并保存到数据库。"""
        group = Group(**group_data)
        session.add(group)
        await session.commit()  # 提交事务
        await session.refresh(group)  # 刷新以获取数据库中的新数据
        return group

    @staticmethod
    async def get_groups_id(session: AsyncSession, group_id: int):
        """根据群号获取信息"""
        result = await session.execute(select(Group).where(Group.group_id == group_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_group(session: AsyncSession, group_id: int, update_data: dict):
        """更新群信息。"""
        group = await GroupCRUD.get_groups_id(session, group_id)
        if group:
            for key, value in update_data.items():
                setattr(group, key, value)  # 更新活动属性
            await session.commit()  # 提交事务
            await session.refresh(group)  # 刷新以获取数据库中的新数据
        return group

    @staticmethod
    async def get_push(session: AsyncSession):
        """获取推送群号"""
        result = await session.execute(select(Group).where(Group.push == 1))
        return result.scalars().all()

    @staticmethod
    async def get_push_sid(session: AsyncSession, sid: int):
        """获取某一学校的推送群号"""
        result = await session.execute(select(Group).where((Group.push == 1) & (Group.sid == sid)))
        return result.scalars().all()

    @staticmethod
    async def get_push_sids(session: AsyncSession):
        """获取推送的sid"""
        result = await session.execute(select(Group.sid).where(Group.push == 1))
        return result.scalars().all()
