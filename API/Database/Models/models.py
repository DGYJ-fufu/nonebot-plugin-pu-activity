from sqlalchemy import Column, BigInteger, Integer, Text, ForeignKey, DateTime, TIMESTAMP, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship
from enum import Enum as PyEnum


# 定义基础类，继承AsyncAttrs和DeclarativeBase，用于支持异步操作
class Base(AsyncAttrs, DeclarativeBase):
    pass


class ReservationStatus(PyEnum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'


class User(Base):
    __tablename__ = 'user'  # 数据库中的表名

    # 用户 QQ 号，主键
    qq = Column(BigInteger, primary_key=True, nullable=False)
    # 用户名，非空
    username = Column(Text, nullable=False)
    # 密码，非空
    password = Column(Text, nullable=False)
    # SID，非空
    sid = Column(BigInteger, nullable=False)
    # CID，可为空
    cid = Column(BigInteger)
    # 认证令牌，可为空
    token = Column(Text)
    # 是否推送通知，默认值为 0（不推送）
    push = Column(Integer, default=0, nullable=False)
    # 年级
    yid = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<{self.__class__.__name__}(qq={self.qq}, username={self.username},username={self.password}, sid={self.sid}, cid={self.cid}, token={self.token}, push={self.push}, yid={self.yid})>"

    def to_dict(self):
        return {
            'qq': self.qq,
            'username': self.username,
            'password': self.password,
            'sid': self.sid,
            'cid': self.cid,
            'token': self.token,
            'push': self.push,
            'yid': self.yid
        }


class Reservation(Base):
    __tablename__ = 'reservation'  # 数据库中的表名

    # 预约 ID，主键，自增
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 用户 QQ 号，外键，非空
    user_id = Column(BigInteger, ForeignKey('user.qq'), nullable=False)
    # 活动 ID，外键，非空
    activity_id = Column(BigInteger, ForeignKey('activity.activity_id'), nullable=False)
    # 预约时间，非空
    reservation_time = Column(DateTime, nullable=False)
    # 预约状态，使用枚举类型
    status = Column(Integer, default=0, nullable=False)
    # 创建时间，默认值为当前时间
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # 定义与 User 模型的关系
    user = relationship('User', back_populates='reservations')

    def __repr__(self):
        return (f"<{self.__class__.__name__}(id={self.id}, user_id={self.user_id}, activity_id={self.activity_id}, "
                f"reservation_time={self.reservation_time}, status={self.status}, created_at={self.created_at})>")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_id': self.activity_id,
            'reservation_time': self.reservation_time,
            'status': self.status,
            'created_at': self.created_at,
        }


class Activity(Base):
    __tablename__ = 'activity'  # 数据库中的表名

    # 活动 ID，主键
    activity_id = Column(Integer, primary_key=True, autoincrement=True)

    def __repr__(self):
        return f'{self.activity_id}'

    def to_dict(self):
        return {
            'activity_id': self.activity_id
        }


# 关系定义：一个用户可以有多个预约
User.reservations = relationship('Reservation', order_by=Reservation.id, back_populates='user')


class Group(Base):
    __tablename__ = 'group'  # 数据库中表名

    # 群号，主键
    group_id = Column(Integer, primary_key=True)
    # 是否推送通知，默认值为 0（不推送）
    push = Column(Integer, default=0, nullable=False)
    # SID，非空
    sid = Column(BigInteger, nullable=False)

    def __repr__(self):
        return f"<{self.__class__.__name__}(group_id={self.group_id}, push={self.push}, sid={self.sid})>"

    def to_dict(self):
        return {
            'group_id': self.group_id,
            'push': self.push,
            'sid': self.sid
        }
