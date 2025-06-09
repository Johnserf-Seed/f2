# Changelog

本项目的所有变更都将记录在此文件中。
格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)、
本项目遵循 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)。

## [Unreleased]

- 新增文档，介绍如何扩展默认数据模型并在接口中使用自定义 `Filter`。
- 将在 `0.0.1.8` 版本中添加 `BiliBili` & `NetEaseMusic` 支持。
- 将在 `0.0.1.8` 版本中维护更多的 `API` 与 `CLI` 功能。
- 添加 `Socket` 代理支持。
- 添加 `Cookie` 池，`Proxy` 池，`User-Agent` 池等支持。

## [0.0.1.7] - 2024-12-31

### Added

- 添加 `douyin` 动图作品接口维护输出 #218
- 添加无法查看网页端 `weibo` 的异常处理 #223
- 添加 `douyin` 批量采集直播的代码片段
- 添加 `Babel` 依赖
- 添加支援电子邮件地址 -> `support@f2.wiki`
- 添加文档域名 -> `f2.wiki`
- 添加所有应用 `Bark` 推送服务
- 添加启用应用 `Bark` 加密推送配置
- 添加生成 `pot` 文件批处理
- 添加 `Bark` 加密推送模式
- 添加生成随机字节数字方法
- 添加 `bark` 通过设备 `token` 推送接口端点
- 添加 `RSA` 加密工具类
- 添加 `AES` 加密工具类
- 添加使用 `bark` 端点文件生成接口
- 添加替换配置文件中空值为空字符串
- 添加 `douyin` 作品状态统计方法
- 添加 `douyin` 作品状态统计接口
- 添加 `cli_commands` 覆盖率测试
- 添加 `x` 书签（收藏）推文模式
- 添加 `x` 喜欢推文模式
- 添加提取 `x` 标题方法
- 添加 `weibo` 工具类测试用例
- 为 `FAQ` 添加 `'NoneType' has no len()` 解决方案
- 添加 `interval` 参数通用的方法处理
- 统一使用 `Live` 管理进度条任务
- 新增 `weibo` 文案提取方法
- 添加通用过滤器转列表的方法
- 允许中断来跳过版本检查
- 添加 `tiktok proto` 元数据
- 主配置添加 `Bark token` 配置
- 添加 `Bark volume` 配置
- 添加 `tiktok wss` 客户端配置管理方法
- 添加 `tiktok` 作品区间 `interval` 参数支持
- 添加 `Bark` 警告通知级别 https://github.com/Finb/Bark/issues/152
- 添加 `tiktok` 直播间信息与弹幕信息回调方法
- 添加 `tiktok` 直播弹幕接口模型
- 添加 `tiktok` 直播间接口模型
- 添加 `tiktok` 基础直播间接口模型
- 为 `douyin` 弹幕爬虫添加代理参数
- 添加弹幕输出开关
- 添加了通知推送 `Bark` 应用
- 添加了代理验证功能
- 添加 `douyin` 直播间消息显示参数
- 添加 `bark` 通知配置
- 添加 `douyin`本地 `wss` 客户端配置
- 添加 `tiktok` 弹幕接口
- 添加 `douyin` 作品翻页时间码显示
- 新增实况图集下载 #75
- 新增 `douyin` 本地弹幕 `wss` 转发服务
- 新增大量 `douyin` 直播间弹幕回调接口
- 添加抖音 `live` 作品解析
- 添加支持 `proxy` 的 `websockets` 依赖
- 添加 `py` 版本检查
- 添加筛选作品 `filter_by_date_interval` 方法
- 添加 `interval_2_timestamp` 方法
- 添加 `str_2_timestamp` 方法
- 在异步线程池中检测 `F2` 版本

### Changed

- 优化 `tiktok` 播放列表相关方法
- 优化 `douyin` 动态作品错误的处理
- 优化注册信号类
- 调整进度条的完成百分比为 `2` 位小数
- 优化直播流 `504` 状态码的处理
- 优化应用任务通知结构
- 为 `weibo` 详情过滤器添加 `nickname_raw` 字段
- 优化选择 `Bark` 加密通知判断逻辑
- 分离 `douyin` 房间号提取方法
- 改进 `x` 短链的解析与错误捕获
- 改进错误捕获与代码规范
- 增加 `tiktok SecUserIdFetcher` 类的稳定性
- `tiktok` 提取 `secUid` 方法支持视频链接
- 优化下载 `douyin` 直播流超时处理捕获层级
- 更新 `bark` 模式列表与其他调整
- 更新 `x` 工具类方法注释与方法名
- 添加贡献者 #213
- 更新 `x` 获取用户唯一 `ID` 类名
- 修改 `x` 爬虫初始化可接受 `x_csrf_token` 参数
- 将 `weibo` 用户 `id` 变量名改回 `uid`
- 更新 `tiktok odin_tt` 生成方法
- 改进直播流下载时受服务器返回的 `HTTP` 不规范的错误
- 更新 `docs` 工作流为 `pnpm` 包管理器
- 更新 `bark` 加密推送，改用随机 `iv`
- 取消 `AES` 算法 `CBC` 模式一起返回 `Iv` 的情况
- 为 `Bark` 接口爬虫 `GET` 方法添加 `URL` 转义
- 为 `bark` 基础模型添加默认值
- 修复 `bark token` 校验函数
- 更新 `douyin` 好友作品接口模型缺失值
- 调整 `douyin` 通过 `app` 分享的直播短链问题情况
- 调整堆积的丢失信息影响下载任务显示
- 调整 `douyin` 视频默认清晰度地址，最高可下 `4K` 作品  #209
- 更新 `douyin` 代码片段 #197
- 优化 `x` 一些边界情况处理
- 分离获取 `weibo` 用户数据的 `2` 种方法
- 计算 `x` 推文数量时过滤空值
- 调整 `x` 应用细节
- 更新 `x` 喜欢模式
- 更新爬取 `x` 主页推文方法
- 更新 `x` 用户推文数据过滤器
- 优化 `x` 下载器
- 更新 `x` 接口模型
- 手动刷新 `live` 管理器防止闪屏
- 完善 `douyin` 测试用例
- 调整 `base_crawler` 异常捕获
- 改进 `weibo` 方法为异步生成器并添加翻页
- 调整 `weibo` 提取文案的方法
- 更改默认异步事件循环作用域，确保兼容性
- 更新 `x` 发布时间字段
- 更新项目 `python` 最低要求版本 >= `3.10.0`
- 优化了过滤器性能并提取为通用方法
- 更新 `weibo` 下载器
- 更新 `timestamp_2_str` 方法，新增列表转换与递归
- 更新关闭信号注册入口
- 更新 `ua` 版本 `126` -> `130`
- 支持自定义 `ua` 生成 `abogus`
- 更新代码片段
- 使用异步任务处理 `douyin` 直播弹幕信息
- 更新 `douyin proto` 元数据
- 优化 `base_crawler`，添加更多边界处理
- 为文本正则解析方法添加空值处理
- 极大提升 `jsonpath` 解析性能
- 捕获 `yaml` 格式错误导致无法解析
- 修改终端输出格式
- 捕获 `tk设备id` 注册时因网络问题导致的出错
- 更新 `douyin` 直播消息 `callback` 方法
- 优化 `douyin` 本地 `WebSocket` 服务性能
- 更新 `douyin` 直播 `BattleTeamTaskMessage` 消息 `proto` 结构体
- 调整 `douyin` 图集文件回 `webp` 格式
- 添加毫秒级时间戳字符串转换
- 优化时间戳转字符串函数
- 重写 `json_filter` 逻辑
- 完善 `douyin` 直播 `protobuf`
- 优化抖音 `interval` 参数的作品解析
- 完善静态类型检查
- 调整进度条显示 #105
- 更新 `douyin` 处理下载任务
- 更新 `douyin` 筛选日期区间作品方法
- 更新日志文件名
- 调整 `i18n` 方法防止重复导入错误
- 更新 `douyin` `abogus` 代码片段
- 更新 `vitepress` 工作流
- 更新 `tiktok` 的 `webmssdk` 版本号
- 更新 `douyin` 直播 `signature` 参数
- 更新 `douyin` 弹幕 `sdk` 版本 `1.0.12` -> `1.0.14-beta.0`

### Deprecated

- 弃用 `douyin` 扫码登录方法警告
- 弃用 `WebcastSignatureManager.model_2_endpoint` 方法
- 弃用 `_get_first_item_from_list` 方法
- 弃用 `num_to_base36` 方法

### Removed

- 删除 `bark` 无用的代码
- 删除 `x` 重复 `utils` 方法
- 删除 `weibo` 工具类重复代码
- 删除 `npm` 锁定文件
- 删除 `douyin wss` 重复回调方法
- 删除 `tiktok` 基础接口模型默认 `设备id`
- 删除 `x` 错误的接口
- 删除 `x` 转推模式
- 删除测试无效的 `JSONPath` 测试

### Fixed

- 修复 `x` 无法下载图文的错误
- 修复 `tiktok` 作品没有视频链接的错误
- 修复 `douyin` 收藏夹类型错误
- 修复 `Bark` 没有设置密钥时加密推送失败的情况
- 修复 `vitepress sidebar` 配置
- 修复下载器并发限制不起作用的问题
- 修复 `weibo` 遗漏 `uid` 变量名修改
- 修复 `douyin` 封面下载错误 #213
- 修复 `douyin` 关注用户排序类型翻页的问题 #210
- 修复防止变量未完成初始化
- 修复 `weibo` 过滤器字段 #149
- 修复文档线上不显示 `icon` 的问题
- 修复 `douyin` 错误的弹幕消息类型日志
- 修复 `tiktok` 错误的本地化代码
- 修复事件循环风险 #159
- 修复 `tiktok` 接口过滤器处理空值的错误
- 修复 `tiktok` 直播流文件名解析错误
- 修复 `x` 默认配置名 #145
- 修复 Incomplete URL substring sanitization #139
- 修复 `douyin` 的 `webmssdk` 库创建缓冲区的安全性问题
- 修复 `tiktok` 读取 `BaseRequestModel` 配置的错误 #79
- 修复 `F2` 版本检测逻辑
- 修复文档编译 `dead link` 的情况

### Security

- 更新 `pytest-asyncio` 版本到 `0.25.0`
- 更新 `browser_cookie3` 版本到 `0.20.1`
- 更新 `vitepress` 版本到 `1.5.0`
- 更新 `pydantic` 的新方法 `ConfigDict` 代替 `Config` 类
- 更新 `protobuf` 版本到 `5.28.3`
- 更新 `aiofiles` 版本到 `24.1.0`
- 更新 `importlib-resources` 版本到 `6.4.5`
- 更新 `pytest` 版本到 `8.3.4`
- 更新 `jsonpath-ng` 版本到 `1.6.1`

## [0.0.1.6] - 2024-05-04

### Added

- 添加`weibo`应用
- 添加`abogus(limit ua)`加密
- 添加`douyin`加密算法切换配置
- 添加基础接口模型转url类
- 添加`WebSocket`爬虫客户端
- 添加`douyin`直播wss签名管理器
- 添加`douyin`直播wss签名生成类
- 添加`douyin`工具JS库`webmssdk.es5-1.0.0.53`
- 添加`douyin`直播间弹幕wss接口
- 添加`F2`版本检测
- 添加`tiktok`直播间开播状态
- 添加`PyExecJS==1.5.1`依赖
- 添加`protobuf==4.23.0`依赖
- 添加`websockets>=11.0`依赖
- 添加`tiktok`的`device_id注册`与`cookie`管理类
- 添加`douyin`生成`webid`配置
- 添加`douyin`关注用户直播
- 添加`douyin`，`tiktok`模型配置
- 添加`conf.yaml`配置版本号
- 添加`tiktok`集成测试
- 添加`traceback`输出
- 添加`douyin`短剧作品
- 添加同步客户端的同步`transport`
- 添加同步客户端
- 添加`douyin`直播弹幕初始化
- 添加`douyin`合集`mix_id`获取方法
- 添加`douyin`查询用户
- 添加时间戳转换的默认时区设置（`UTC/GMT+08:00`）
- 添加`ClientConfManager`为每个应用提供方便的配置读取
- 添加`uniqueId`查询`tiktok`的`user_db`
- 添加获取`segments`的`duration`列表方法
- 添加应用运行模式的输出
- 新增`tiktok`作品搜索
- 新增`tiktok`用户直播
- 添加反转义`JSON`方法
- 新增`douyin`相关推荐
- 新增`douyin`好友作品

### Changed

- 更新`__aexit__`方法
- 更新`douyin`加密算法代码片段
- 更新`weibo`测试用例
- 优化命令不存在的输出
- 取消接口数据过滤器对`bool`的预处理
- 调整停止异步任务信号
- 更新`douyin`的`xbogus`调用
- 为装饰器文件重命名
- 更新获取`Content-Length`的方法
- 防止`douyin`直播结束时下载崩溃
- 更新`BaseCrawler`类处理`httpx`即将弃用`proxies`参数
- 更新`tiktok`的`msToken`配置
- 修复`ClientConfManager`参数
- 更新了所有应用配置
- 重构了所有工具类方法
- 更新`base_downloader`的区块下载参数
- 修改`douyin`生成的`ttwid`将绑定`ua`
- 修改`tiktok`用户直播下载流地址
- 修改`douyin`，`tiktok`获取用户信息方法名
- 完善时间戳转换类型，支持30位
- 修改应用的代理配置名（`http: https: -> http://: https://:`）
- 更新`xb`算法示例部分
- 更新`base_crawler`异常捕获与输出
- 更新应用初始化配置文件后退出 (#70)
- 更新应用使用`--auto-cookie`命令后退出
- 更新`douyin`过滤器，将`video_play_addr`返回完整视频列表便于下载失败轮替
- 更改`douyin`图集文件名（`jpg -> webp`）
- 更改应用直播下载文件名（`mp4 -> flv`）
- 更新应用工具类网络错误捕获

### Deprecated

- 弃用`douyin`SSO扫码登录
- 类`BaseModel`中的`dict`方法已弃用(`pydantic>=2.6.4`)
- 类`datetime`中的`utcnow`方法已弃用
- 弃用`douyin`，`tiktok`获取用户名方法

### Removed

- 删除`tiktok`基础请求模型的无用参数
- 删除`f2\utils\utils.py`无效导入

### Fixed

- 修复`douyin`接口更新导致的错误 #104
- 修复`_dl`日志输出
- 修复`douyin`下载合集时合集链接无法识别的情况
- 修复`tiktok`下载播放列表（合集）的错误
- 修复`m3u8`流下载时会重复下载`ts`片段的问题
- 修复`m3u8`流获取`content_length`时没有提供代理参数造成的访问失败
- 修复`douyin`，`tiktok`因提前引发异常导致无法生成虚假的msToken

### Security

- 更新`pytest`版本到`8.2.1`
- 更新`pydantic`版本到`2.6.4`
- 更新`httpx`版本到`0.27.0`
- 更新`aiosqlite`版本到`0.20.0`


## [0.0.1.5] - 2024-04-04

### Added

- 添加安全政策汇报
- 添加`run_app`时输出版本号
- 添加`douyin`用户收藏夹下载
- 添加`douyin`的`filter`对非法收藏夹名字符的处理
- 添加`douyin`用户音乐收藏下载
- 添加`douyin`音乐歌词json转lrc方法
- 添加`douyin`用户收藏音乐下载任务
- 添加`douyin`配置`--lyric`
- 添加`f2 utils`的`get_cookie_from_browser`方法
- 添加`f2 utils`的`check_invalid_naming`方法
- 添加`f2 utils`的`merge_config`方法
- 添加`douyin`粉丝用户接口方法
- 添加`douyin`关注用户接口方法
- 添加`douyin`，`tiktok`数据过滤器的原始字段
- 添加对30位时间戳进行格式化
- 添加测试抖音原声歌词转换
- 添加获取抖音用户粉丝代码片段
- 添加获取抖音用户关注代码片段
- 添加`fetch`方法的`timeout`参数，避免请求过于频繁
- 添加`douyin`用户收藏夹代码片段
- 添加对丢失链接的重试逻辑
- 添加`自定义UA`生成`XBogus`参数
- 添加`douyin`，`tiktok`对`UserProfile`请求内容为空的报错

### Changed

- 修改`douyin`主页收藏模式为`collection`
- 更正`douyin`文档`user-mix`方法
- 修改`F2`版本号输出
- 修改`douyin`，`tiktok`帮助信息
- 优化`douyin`，`tiktok`的`utils`中`msToken`，`ttwid`，`sec_user_id`，`aweme_id`，`webcast_id`，具体请求错误的输出
- 明确`douyin`，`tiktok`所有`fetch`函数返回为过滤器类型
- 更新了F2版本号的导入
- 优化`tiktok`的`handler`处理播放列表的逻辑
- 优化`douyin`，`tiktok`中对具体请求错误的输出
- 更正`douyin`，`tiktok`受`collects_id`类型导致的多次转换
- 更正`tiktok`的`handler`多种获取用户信息方法的参数
- 添加`base_downloader`对重命名文件时的异常处理
- 更新`_dl`的`head`请求`Content-Length`失效时调用`get`方法
- 更新`douyin`，`tiktok`接口文档代码片段
- 更新`douyin`，`tiktok`在`cli`中的`handler_auto_cookie`方法
- 更新`douyin`，`tiktok`在`cli`中的`handler_naming`方法
- 更新`douyin`，`tiktok`的`--mode`统一`choice`管理
- 更新`F2`帮助说明格式
- 统一了`douyin`关注粉丝用户的`total`字段
- 修改下载逻辑以提高性能
- 更新`douyin`，`tiktok`数据库字段(需要删除旧数据库或迁移)
- 优化`douyin`，`tiktok`的`handler`模块注释表达与方法参数格式
- 重构了所有`handle`方法的调用
- 重构了所有`fetch`方法的返回类型
- 调整`douyin` `mix`作品在没有更多数据时提前`break`
- 调整`tiktok`获取用户数据去除地区参数
- 优化在适当的位置`yield`作品数据
- 修改日志输出级别
- 重构数据库异常类
- 重构文件异常类
- 重构接口异常类
- 完善`i18n`消息

### Deprecated

- 弃用`douyin` `UserLiveFilter`的无用方法
- 弃用`douyin` `PostDetailFilter`的无用方法

### Removed

- 删除文档旧版本`-d`指令
- 移除`tiktok`的`post\detail`接口示例
- 删除无用的`__init__.py`文件
- 删除`douyin`，`tiktok`：`cli`下的`get_cookie_from_browser`方法
- 删除`example`示例
- 删除无用导入
- 删除`apps`中db模块的`aiosqlite`导入与错误处理

### Fixed

- 修复本地化服务
- 修复`douyin`关注用户数据过滤器`_to_list`方法的排除字段
- 修复`douyin`数据过滤器时间戳类型

### Security

- 更新`rich`版本到`13.7.1`
- 更新`douyin`接口版本到`19.5.0`


## [0.0.1.4] - 2024-02-16

### Added

- 添加`black`格式化白名单
- 添加`douyin`，`tiktok`命令行对`--proxies`命令的支持
- 添加`tiktok`数据库忽略字段
- 添加文档QA页面
- 添加`douyin`对`msToken`值验证
- 添加写入配置文件时处理文件权限问题
- 添加提取有效URL的错误类型
- 添加`split_filename`方法处理不同系统下文件名长度
- 添加`douyin`，`tiktok`：`cli`模块的`merge_config`方法
- 添加了低频配置文件默认路径
- 添加`split_filename`函数单元测试
- 添加`base_downloader`模块日志堆栈错误输出
- 添加`tiktok`的`get_secuid`方法对不支持地区的错误消息
- 添加`douyin`，`tiktok`：`utils`模块对空urls列表的错误处理
- 添加`douyin`，`tiktok`：`utils`模块对AwemeIdFetcher的连接失败处理
- 添加`douyin`图集`aweme_id`测试链接
- 添加文档`algolia`配置参数
- 添加`douyin`，`tiktok`：`{aweme_id}`与`{uid}`的文件名模板

### Changed

- 重写`douyin`，`tiktok` handler对`crawler`与`dl`的配置，提升性能
- 将`dict`类型的`--proxies`添加默认值`None`
- 将配置文件中`url`设置为空，防止因为缺省出错
- 对高低频配置合并时只合并非空值
- 更新翻译模板
- 调整`timestamp_2_str`方法的默认时间字符串格式
- 将低频参数配置移入`F2`的`conf.yaml`
- 修改`tiktok`对`msToken`值验证
- 修改`douyin`，`tiktok`的`TokenManager`里固定配置的读取方式
- 改进 `douyin`，`tiktok` handler类的结构和清晰度
- 更新方法签名，使用 `self` 替代 `cls`
- 在适当的情况下，用异步实例方法替代类方法
- 更新`douyin`，`tiktok` `handler`类下的`fetch`用法
- 修改`main`入口函数，实例化每个app的`handler`并传递给相应的方法
- 更新`douyin`，`tiktok`的`get_or_add_user_data`方法，以处理`Filter`类型的数据
- 更新`F2 -d`参数，现在需要指定`debug`模式
- 更新`conf_manager`模块，添加了日志输出
- 更新`douyin`接口文档`format-file-name`代码片段
- 更新`douyin`，`tiktok`的`crawler`模块重新添加异步上下文管理器
- 更新`douyin`，`tiktok`的`utils`模块捕获错误时显示具体类名
- 更新了配置文件加载逻辑
- 更新了日志输出
- 更新`split_filename`方法适配双语种环境
- 更新`douyin`，`tiktok`的`crawler`模块获取`response`的多种http请求方法
- 修改`file_exceptions`模块，使输出更简洁
- 修改`db_exceptions`模块，使输出更简洁
- 修改`api_exceptions`模块，使输出更简洁
- 更改`base_crawler`模块里的方法名称
- 完善所有`APIConnectionError`的错误处理
- 更新在无代理时配置默认值
- 改进`douyin`的cli模块的`handler_sso_login`方法
- 更新`douyin`，`tiktok`单元测试用例
- 更新接口文档开发者代码片段
- 修改`cli_console`进度条默认宽度

### Deprecated

- 弃用`douyin`：`extract_desc_from_share_desc`方法
- 弃用`douyin`：`get_request_sizes`方法

### Removed

- 移除文档`reference`页面
- 删除`douyin`：`VerifyFpManager`注释代码
- 删除`douyin`： `cli`模块的英文注释
- 移除`split_filename`方法的`desc_length_limit`参数
- 删除`conf.yaml`中的代理值
- 删除`base_crawler`模块选择随机代理的注释代码
- 删除`base_downloader`模块中`_download_chunks`方法的`finally`
- 删除`F2 conf.yaml`中的代理值与无效值
- 删除弃用接口测试

### Fixed

- 修复部分自定义配置失效的问题
- 修复接口缺失时间戳值导致的问题
- 修复`get_or_add_user_data`中的`AttributeError`问题
- 修复了非windows系统下创建长中文名文件出错的问题
- 修复了`tiktok`文件名出错的问题
- 修复了在更新配置时缺少自定义配置文件路径的问题
- 修复`douyin`直播嵌套ts文件无法获取字节大小的问题
- 修复`base_downloader`下载文件区块时未能正确捕获超时错误
- 修复`cli`退出时`base_downloader`出现`UnboundLocalError`错误的问题
- 修复`douyin`收藏作品下载错误的问题
- 修复`douyin`，`tiktok`：`cli`的默认参数影响kwargs合并
- 修正`douyin`的`utils`模块对`aweme_id`的处理

### Security

- 依赖更新`pyyaml6.0 -> pyyaml6.0.1`


## [0.0.1.3] - 2024-01-07

### Added

- 添加`douyin`，`tiktok`对`--interval`命令的支持

### Changed

- 取消`bool`参数的默认值，防止配置文件与`cli`命令冲突
- 调整日志控制台输出与级别
- 修改默认与自定义配置读取与合并
- 恢复`tiktok`接口模型的`msToken`值
- 修改自定义文件名模板中作品创建时间的键名
- 更新主配置文件格式


## [0.0.1.2] - 2024-01-05

### Added

- 添加依赖缺失时输出错误到日志
- 使用`black`统一代码风格
- 添加`douyin`单个作品(one)与`--sso-login`命令帮助

### Changed

- `--auto-cookie`命令去掉`none`参数
- 所有app的`--interval`命令参数改为`all`
- 完善`douyin`的`cli`帮助说明
- 更新`F2`帮助说明
- 完善`tiktok`的`cli`帮助说明
- 修改代码片段高亮
- 更新项目文档
- 更新翻译文件

### Fixed

- 修复`--init-config`命令初始化的问题
- 修复`douyin`文档`user-live`代码片段错误方法名
- 修复`douyin`文档`user-mix`代码片段`aweme_id`不明的问题
- 修复`douyin`，`tiktok`未提供参数也自动获取ck
- 修复显示语言中`en_US`缺失
- 修复接口文档的代码片段格式与错误
- 使用缺省`none`来避免触发`callback`干预程序运行


## [0.0.1.1] - 2024-01-01

### Added

- 添加依赖缺失时输出错误到日志

### Fixed

- 修复pyproject.toml依赖部分遗漏造成的`Error: No such command`


## [0.0.1-pw.1] - 2024-01-01

### Added

- 创建文档
- 添加`douyin`，`tiktok`应用
- 添加`douyin`，`tiktok`测试
- 添加代码示例
- 添加`i18n`翻译模板文件
- 添加`show_qrcode`方法，用于显示二维码
- 添加`s_v_web_id`方法
- `douyin`：添加`room_id`查询直播间信息接口
- `douyin`：添加`--sso-login`命令，使用扫码获取cookie
- `douyin`：添加`sso登录`测试
- 添加`douyin`，`tiktok`开发接口文档
- 添加`douyin`，`tiktok`接口地址生成XB的方法
- 添加`douyin`，`tiktok`接口文档代码片段
- 创建目录时支持绝对与相对路径
- 添加`douyin`，`tiktok`获取列表`secuid`，`unique_id`，`aweme_id`的方法

### Changed

- 细化`Basecrwaler`的`response`处理方法
- 自定义将日志输出到控制台
- 将guide文档调整为统一文件夹下
- 修改文档代码片段高亮行号
- 重命名接口模型生成XB的方法
- 修改`douyin`提取列表用户id返回值变量名
- 修改`douyin`提取列表用户直播rid返回值变量名
- 完善配置文件site-config部分
- 修改默认配置参数置空

### Fixed

- 修复`douyin`用户数据库名称
- 修复`douyin`直播结束后无法下载
- 修复`douyin`在`handler_user_mix`方法中`AsyncUserDB`只初始化一次
- 修复`user-nickname`代码片段导入
- 修复`douyin`文档`user-get-add`代码片段导入
- 修复`tiktok`文档`user-mix`代码导入与缩进
- 修复`tiktok`文档`one-video`代码缩进
