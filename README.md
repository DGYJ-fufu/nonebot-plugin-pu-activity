# PU口袋校园插件

这是一个基于NoneBot的PU口袋校园插件，旨在为用户提供校园活动的信息和管理功能。

## 功能

### 已开发功能
- **账号登录**: 用户可以通过账号进行登录。
- **获取全部活动**: 获取当前所有可用的活动信息。
- **获取学院活动**: 根据学院获取相关活动列表。
- **获取可参加活动**: 筛选出用户可以参加的活动。
- **查询活动详细信息**: 提供活动的详细信息。
- **活动报名**: 用户可以报名参加活动。
- **新活动推送订阅**: 用户可以订阅新活动的推送通知。
- **预约活动自动报名**: 实现活动的自动报名功能。

### 开发中功能
- **查询学分**: 查询用户的学分情况。
- **查询已报名活动**: 查看用户已报名的活动列表。

## 数据库结构

### 用户表 (`user`)
```sql
CREATE TABLE user (
    qq       BIGINT NOT NULL PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    sid      BIGINT NOT NULL,
    cid      BIGINT NULL,
    token    TEXT NULL,
    push     TINYINT(1) DEFAULT 0 NOT NULL
);
```

### 活动表 (activity)
```sql
CREATE TABLE activity (
    id             BIGINT NOT NULL PRIMARY KEY,
    name           TEXT NOT NULL,
    credit         FLOAT NOT NULL,
    allowCollege   BIGINT NULL,
    categoryId     BIGINT NOT NULL,
    categoryName   TEXT NOT NULL,
    allowUserCount INT NOT NULL,
    joinUserCount  INT NOT NULL,
    joinStartTime  DATETIME NOT NULL,
    joinEndTime    DATETIME NOT NULL,
    startTime      DATETIME NOT NULL,
    endTime        DATETIME NOT NULL,
    address        TEXT NULL,
    description    TEXT NULL,
    statusName     TEXT NOT NULL
) COLLATE = utf8mb4_unicode_ci;
```

### 预约表 (reservation)
```sql
create table reservation
(
    id               bigint auto_increment
        primary key,
    user_id          bigint                                                              not null,
    activity_id      bigint                                                              not null,
    reservation_time datetime                                                            not null,
    status           enum ('pending', 'completed', 'failed') default 'pending'           not null,
    created_at       timestamp                               default current_timestamp() not null,
    updated_at       timestamp                               default current_timestamp() not null on update current_timestamp(),
    constraint activity
        foreign key (activity_id) references activity (id),
    constraint user_qq
        foreign key (user_id) references user (qq)
);
```

## 阿巴阿巴
本人代码水平有限，面向结果编程，能跑就行

PU口袋校园接口:<https://dgyj-fufu.apifox.cn/api-219463037>
