# PU口袋校园插件

这是一个基于NoneBot的PU口袋校园插件，旨在为用户提供校园活动的信息和管理功能。

## 功能

### 已开发功能

- **账号登录**: 用户可以通过账号进行登录。
- **获取活动**: 获取当前所有可用的活动信息。
- **获取可参加活动**: 筛选出用户可以参加的活动。
- **查询活动详细信息**: 提供活动的详细信息。
- **活动报名**: 用户可以报名参加活动。
- **新活动推送订阅**: 用户可以订阅新活动的推送通知。
- **预约活动自动报名**: 实现活动的自动报名功能。
- **查询已报名活动**: 查看用户已报名的活动列表。
- **查询学分**: 查询用户的学分情况。


## 使用

- ✨添加用户
- ✨获取活动
- ✨获取可参加活动
- ✨活动推送开启/关闭
- ✨我的活动
- ✨活动🆔
- ✨报名🆔
- ✨预约🆔
- ✨查询预约
- ✨删除预约🆔
- ✨刷新token
- ✨查询分数
- ✨帮助
- ⚠️注:🆔为活动ID

## 数据库结构（SQLite）

### 用户表 (`user`)

```sql
create table user
(
    qq       bigint               not null
        primary key,
    username text                 not null,
    password text                 not null,
    sid      bigint               not null,
    cid      bigint,
    token    text,
    push     tinyint(1) default 0 not null,
    yid      integer              not null
);
```

### 活动表 (activity)

```sql
create table activity
(
    activity_id integer not null constraint activity_id
            primary key
);
```

### 预约表 (reservation)

```sql
create table reservation
(
    id               INTEGER       not null /*autoincrement needs PK*/
        constraint id
            unique,
    user_id          BIGINT        not null,
    activity_id      BIGINT        not null,
    reservation_time DATETIME      not null,
    status           INT default 0 not null,
    created_at       DATETIME      not null
);
```

## 阿巴阿巴

本人代码水平有限，面向结果编程，能跑就行

PU口袋校园接口:<https://dgyj-fufu.apifox.cn/api-219463037>
