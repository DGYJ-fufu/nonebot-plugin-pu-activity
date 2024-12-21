<div align="center">
  <img src="https://s2.loli.net/2022/06/16/opBDE8Swad5rU3n.png" width="180" height="180" alt="NoneBotPluginLogo">
  <br>
  <p><img src="https://s2.loli.net/2022/06/16/xsVUGRrkbn1ljTD.png" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-pu-activity

_✨PU口袋校园插件✨_

插件主要实现群聊/私聊的PU口袋校园功能

<img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="python">

</div>



## 介绍

这是一个基于NoneBot的PU口袋校园插件，旨在为用户提供校园活动的信息和管理功能。

#### 已开发功能

- **账号登录**: 用户可以通过账号进行登录。
- **获取活动**: 获取当前所有可用的活动信息。
- **获取可参加活动**: 筛选出用户可以参加的活动。
- **查询活动详细信息**: 提供活动的详细信息。
- **活动报名**: 用户可以报名参加活动。
- **新活动推送订阅**: 用户可以订阅新活动的推送通知。
- **预约活动自动报名**: 实现活动的自动报名功能。
- **查询已报名活动**: 查看用户已报名的活动列表。
- **查询学分**: 查询用户的学分情况。
- **新活动群推送**:QQ群可以订阅新活动的推送通知。(需要订阅的学校已经存在用户)

## 安装

- 克隆仓库

将本仓库克隆到nonebot项目的插件目录下

```
git clone https://github.com/DGYJ-fufu/nonebot-plugin-pu-activity.git
```

- 使用发布的版本

将文件下载解压后放入nonebot项目的插件目录下


## 使用

使用前需要为Python安装如下软件包:
```
httpx
orjson
SQLAlchemy
pydantic
aiosqlite
```
在使用前请先安装 nonebot-plugin-apscheduler 插件至项目环境中，可在项目目录下执行以下命令： ```nb plugin install nonebot-plugin-apscheduler```


### 触发方式：
#### 以下命令需要加命令前缀 (默认为/)，可自行设置为空，详细配置方法可参考nonebot官方文档。
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


#### 示例:

<div align="left">
    <img src="https://s2.loli.net/2024/12/22/rXNWKHijmPdOIUh.jpg" width="400" />
  
</div>

<div align="left">
    <img src="https://s2.loli.net/2024/12/22/GcTpP5ZKIMCXWqJ.jpg" width="400" />
</div>

## ⚠️注意:
- 预约任务只适用于报名时间还没到的活动，如果已经到达的报名的开始时间，请不要使用预约活动功能，预约了不会有效果滴。如果已经预约了删除预约即可，当然不删其实也没什么关系。

- 如果是第一次使用活动推送功能的用户，在下一个活动更新周期可能会收到较多的活动通知，因为首次使用数据库没有历史活动数据，一般一次过后就没这个问题了，不必理会即可。

- 预约活动本质还是定时发送报名请求，所以本机时间与PU口袋的服务器时间越接近，抢活动越快，建议使用较高精度的时间校准来同步本机时间。

## PU口袋校园接口: 
### [Apifox](https://dgyj-fufu.apifox.cn/api-219463037)

## 🎉支持

- 大家喜欢的话可以给这个项目点个star
- 有bug、意见和建议都欢迎提交 [Issues](https://github.com/DGYJ-fufu/nonebot-plugin-pu-activity/issues) 
- 或者联系个人邮箱：dgyj-fufu@foxmail.com
