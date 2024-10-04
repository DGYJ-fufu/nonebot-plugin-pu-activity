from datetime import datetime


def get_datetime():
    # 获取当前日期和时间
    now = datetime.now()

    # 格式化输出
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_now


def compare_datetime(dt_str1, dt_str2):
    # 将字符串转换为datetime对象
    dt1 = datetime.strptime(dt_str1, "%Y-%m-%d %H:%M:%S")
    dt2 = datetime.strptime(dt_str2, "%Y-%m-%d %H:%M:%S")

    # 比较并返回结果
    if dt1 > dt2:
        return False
    else:
        return True
