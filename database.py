import os
import mysql.connector
# from api import login, get_activity_info, get_activity_list
from .api import login, get_activity_info, get_activity_list, join_activity
from .tools import *


class DataBase:
    def __init__(self):
        self.sql_connect = mysql.connector.connect(
            host=os.getenv('DB_HOST'),  # 从环境变量中读取数据库主机
            user=os.getenv('DB_USER'),  # 从环境变量中读取数据库用户名
            password=os.getenv('DB_PASS'),  # 从环境变量中读取数据库密码
            port=int(os.getenv('DB_PORT')),
            database=os.getenv('DB_NAME')  # 从环境变量中读取数据库名
        )
        self.sql = self.sql_connect.cursor()

    # 查询QQ是否在库
    def find_qq(self, qq):
        self.sql.execute("SELECT qq FROM user WHERE qq = %s", (qq,))
        return self.sql.fetchall()[0]

    # 添加用户数据
    def user_add(self, qq, username, sid, password):
        self.sql.execute("INSERT INTO user (qq,username, sid, password) VALUES (%s, %s, %s, %s)",
                         (qq, username, sid, password))
        self.sql_connect.commit()

    # 更新用户数据
    def user_update(self, qq, username, sid, password):
        self.sql.execute("UPDATE user SET username=%s,password=%s,sid=%s WHERE qq = %s",
                         (username, password, sid, qq,))
        self.sql_connect.commit()

    # 获取用户token和sid
    def get_user_token(self, qq):
        self.sql.execute("SELECT token,sid FROM user WHERE qq = %s", (qq,))
        return self.sql.fetchall()[0]

    # 更新用户token和cid
    def update_user_token(self, qq):
        self.sql.execute("SELECT username,password,sid FROM user WHERE qq = %s", (qq,))
        user = self.sql.fetchone()
        response = login(user[0], user[1], user[2])
        if response != "-1":
            self.sql.execute("UPDATE user SET token = %s,cid=%s WHERE qq = %s",
                             (str(response["token"]), int(response["cid"]), qq,))
            self.sql_connect.commit()

    # 获取cid
    def get_user_cid(self, qq):
        self.sql.execute("SELECT cid FROM user WHERE qq = %s", (qq,))
        return self.sql.fetchall()[0]

    # 获取订阅QQ
    def get_auto_push(self):
        self.sql.execute("SELECT qq FROM user WHERE push = 1")
        return self.sql.fetchall()

    # 账号订阅开关
    def set_auto_push(self, qq, status):
        self.sql.execute("UPDATE user SET push = %s WHERE qq = %s", (status, qq,))
        self.sql_connect.commit()

    # 自动推送
    def auto_push(self, user_info_list):
        # 获取活动列表
        response = get_activity_list(user_info_list[0]["token"], user_info_list[0]["sid"])["data"]["list"]

        # SQL 命令
        sql_add_cmd = """
                INSERT INTO activity (id, name, credit, allowCollege, categoryId, categoryName,
                allowUserCount, joinUserCount, joinStartTime, joinEndTime, startTime, endTime,
                address, description, statusName)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

        sql_up_cmd = """
                UPDATE activity
                SET allowUserCount = %s, joinUserCount = %s, joinStartTime = %s,
                joinEndTime = %s, startTime = %s, endTime = %s, address = %s,
                description = %s, statusName = %s
                WHERE id = %s
            """

        # 用于存储待插入和更新的值
        sql_add_val = []
        sql_up_val = []

        for item in response:
            self.sql.execute("SELECT id FROM activity WHERE id = %s", (item["id"],))
            item_info = get_activity_info(user_info_list[0]["token"], user_info_list[0]["sid"], item["id"])["data"][
                "baseInfo"]

            # 检查活动是否存在
            if self.sql.fetchone() is None:
                allow_college = item_info["allowCollege"][0]["id"] if item_info["allowCollege"] else None
                cache = (
                    item["id"],
                    item["name"],
                    item["credit"],
                    allow_college,
                    item_info["categoryId"],
                    item_info["categoryName"],
                    item_info["allowUserCount"],
                    item_info["joinUserCount"],
                    item_info["joinStartTime"],
                    item_info["joinEndTime"],
                    item_info["startTime"],
                    item_info["endTime"],
                    item_info["address"],
                    item_info["description"],
                    item_info["statusName"]
                )
                sql_add_val.append(cache)
            else:
                cache = (
                    item_info["allowUserCount"],
                    item_info["joinUserCount"],
                    item_info["joinStartTime"],
                    item_info["joinEndTime"],
                    item_info["startTime"],
                    item_info["endTime"],
                    item_info["address"],
                    item_info["description"],
                    item_info["statusName"],
                    item["id"]
                )
                sql_up_val.append(cache)

        # 执行插入和更新操作
        if sql_add_val:
            self.sql.executemany(sql_add_cmd, sql_add_val)
        if sql_up_val:
            self.sql.executemany(sql_up_cmd, sql_up_val)

        # 提交事务
        self.sql_connect.commit()

        msg = []

        for item in sql_add_val:
            activity = {
                "id": item[0],
                "name": item[1],
                "credit": item[2],
                "allow_colleg": item[3],
                "categoryId": item[4],
                "categoryName": item[5],
                "allowUserCount": item[6],
                "joinUserCount": item[7],
                "joinStartTime": item[8],
                "joinEndTime": item[9],
                "startTime": item[10],
                "endTime": item[11],
                "address": item[12],
                "description": item[13],
                "statusName": item[14]
            }
            msg.append(activity)

        return msg

    # 添加预约任务
    def reservation(self, qq, activity_id, token, sid):
        self.sql.execute("SELECT activity_id FROM reservation WHERE activity_id = %s AND user_id = %s",
                         (activity_id, qq,))
        if len(self.sql.fetchall()) == 0:
            time = get_datetime()
            res = get_activity_info(token=token, sid=sid, id=activity_id)
            if res == "-1":
                return "-1"
            elif res == "-2":
                return "-2"
            else:
                reservation_time = res["data"]["baseInfo"][
                    "joinStartTime"]
                self.sql.execute(
                    "INSERT INTO reservation (user_id, activity_id, reservation_time,created_at,updated_at) VALUES (%s, %s, %s, %s, %s)",
                    (qq, activity_id, reservation_time, time, time))
                self.sql_connect.commit()
                return 0
        else:
            return 1

    # 自动报名
    def auto_join(self):
        self.sql.execute("SELECT id FROM reservation WHERE status = 'pending'")
        reservations = self.sql.fetchall()
        try:
            if len(reservations) > 0:
                users = []
                for reservation in reservations:
                    self.sql.execute("UPDATE reservation SET updated_at = %s WHERE id = %s",
                                     (get_datetime(), reservation[0],))
                    self.sql_connect.commit()
                    self.sql.execute("SELECT user_id,activity_id,reservation_time FROM reservation WHERE id = %s",
                                     (reservation[0],))
                    reservation_info = self.sql.fetchall()
                    self.sql.execute("SELECT token,sid FROM user WHERE qq = %s", (reservation_info[0][0],))
                    user_info = self.sql.fetchall()
                    users.append(
                        {
                            "id": reservation[0],
                            "qq": reservation_info[0][0],
                            "activity_id": reservation_info[0][1],
                            "reservation_time": reservation_info[0][2].strftime('%Y-%m-%d %H:%M:%S'),
                            "token": user_info[0][0],
                            "sid": user_info[0][1]
                        }
                    )
                ok_users = []
                for user in users:
                    if datetime.now() > datetime.strptime(user['reservation_time'], "%Y-%m-%d %H:%M:%S"):
                        res = join_activity(token=user['token'], sid=user['sid'], id=user['activity_id'])
                        if res == "-1":
                            self.sql.execute("UPDATE reservation SET status=%s WHERE id = %s",
                                             ("completed", user["id"],))
                            self.sql_connect.commit()
                            ok_user = user
                            ok_user["code"] = "-1"
                            ok_users.append(ok_user)
                        elif res == "-2":
                            self.update_user_token(user["qq"])
                            ok_user = user
                            ok_user["code"] = "-2"
                            ok_users.append(ok_user)
                        else:
                            if res["code"] == 9405 or res["code"] == 0:
                                self.sql.execute("UPDATE reservation SET status=%s WHERE id = %s",
                                                 ("completed", user["id"],))
                                self.sql_connect.commit()
                                ok_user = user
                                ok_user["code"] = res["code"]
                                ok_user["message"] = res["message"]
                                ok_users.append(ok_user)
                return ok_users
            return 0
        except Exception as e:
            if len(reservations) > 0:
                for id in reservations:
                    self.sql.execute("UPDATE reservation SET status=%s WHERE id = %s",
                                     ("failed", id[0],))
                    self.sql_connect.commit()
            return "-1"

    # 查询预约信息
    def find_reservation(self, qq):
        self.sql.execute("SELECT id,activity_id,reservation_time,status FROM reservation WHERE user_id = %s",
                         (qq,))
        reservations_info = self.sql.fetchall()
        if len(reservations_info) > 0:
            res = []
            for reservation_info in reservations_info:
                res.append({
                    "id": reservation_info[0],
                    "activity_id": reservation_info[1],
                    "reservation_time": reservation_info[2].strftime('%Y-%m-%d %H:%M:%S'),
                    "status": reservation_info[3],
                })
            return res
        else:
            return 0
