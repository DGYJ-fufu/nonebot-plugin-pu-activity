import os
import mysql.connector
# from api import login, get_activity_info, get_activity_list
from .api import login, get_activity_info, get_activity_list


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
