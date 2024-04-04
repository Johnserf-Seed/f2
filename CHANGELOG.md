# Changelog

本项目的所有变更都将记录在此文件中。
格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)、
本项目遵循 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)。

## [Unreleased]

- `0.0.1.6`版本中添加对`weibo`，`x`的支持

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
