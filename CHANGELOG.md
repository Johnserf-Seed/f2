# Changelog

本项目的所有变更都将记录在此文件中。
格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)、
本项目遵循 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)。

## [Unreleased]

- 修复 TikTok 用游客 cookie 或空 cookie 时主页、喜欢、收藏、合集模式无法开始下载：用户信息接口对它们只返回空内容，建立用户目录时重试 5 次后失败。现在使用打开主页时取得的用户信息，公开内容不需要登录 cookie 也能下载（复测 #384、#366）。
- 修复 TikTok 喜欢列表没有公开时无限请求：接口一直返回带新游标的空页面，命令行的喜欢模式不会结束。现在主页、喜欢、收藏、合集连续 3 页没有作品时停止并说明原因。
- 修复按 Ctrl+C 中断后以退出码 `0` 结束：现在以 `130` 退出（收到 `SIGTERM` 时为 `143`），脚本可以判断运行被中断；在启动阶段（读取配置、`--auto-cookie` 读取浏览器）或运行结束时按 Ctrl+C 也不再输出 `RuntimeError: no running event loop` 的堆栈。
- 修复数据库版本查询依赖 SQLite 把双引号当作字符串：按官方推荐关闭 DQS 编译的 SQLite 会报 `no such column: version`，连接数据库时失败。
- 修复直播录制时片段中途超时或出错后，重新下载该片段会把残缺数据重复写入录像：现在片段完整下载后才写入文件。
- 修复各应用下载完成后的 Bark 通知没有按配置加密：配置了加密密钥时，此前这些通知仍以明文发送；加密开关写成 `no` 时也会被当成开启。
- 修复设置了 `--max-counts` 时结束前还要白等 `timeout` 秒：抖音、TikTok、推特的翻页在达到最大数量后仍先等待再退出循环，现在直接结束。
- `-l` 只对本次运行生效：此前会把语言写回安装目录里的 `conf.yaml`，之后不加 `-l` 也沿用上次的语言，回写还会改动文件格式。需要英文界面时，请在每次运行时加上 `-l en_US`。
- 修复配置向导的几个问题：`f2 config-wizard -o` 与 `-a` 只被打印出来，向导仍然询问保存路径并让用户选择平台；推特命名模板 `{user_name}_{create}` 中的字段不存在，按它生成的配置下载时报错；输入结束（例如在管道中运行）时各输入循环无限重试。同时补上最大下载数量这一项与 `related`、`search` 模式的说明，`D:/Downloads` 只在 Windows 上提供；向导此前没有翻译，英文界面下仍是中文，现已补齐。
- 下载路径支持以 `~` 开头的用户目录：此前配置 `path: ~/Downloads` 会保存到当前目录下名为 `~` 的目录中。
- 修复运行结束时 httpx 客户端没有关闭：获取 ID、token 与访客 cookie 的类方法每次调用都新建客户端，handler 的下载器也没有关闭，连接要等事件循环关闭后才被回收，Windows 上退出时会报 `Event loop is closed`。现在用完即关闭，各应用的 `main` 结束时（包括出错）关闭下载器。
- 修复获取用户、作品等 ID 的请求不使用应用配置与 `--proxies` 中的代理：抖音、TikTok、推特从链接获取 sec_user_id、sec_uid、作品 ID、合集 ID、直播间号、用户名与推文 ID 时只用客户端配置中的代理（默认为空），只在 F2 中配置了代理、没有系统代理时这些请求直连，TikTok 的主页、喜欢等模式在获取 sec_uid 时就失败。相关类方法增加可选参数 `proxies`，没有配置代理时仍使用客户端配置中的代理。
- 日志脱敏补充整个 cookie 串与各平台的登录字段：此前 cookie 串里推特的 `auth_token`、`ct0`，微博的 `SUB`、`SUBP`，抖音与 TikTok 的 `sid_tt`、`sid_guard`、`tt_chain_token` 等字段原样输出，请求头字典与 JSON 中带引号的写法也不会匹配。现在整串打码，并补充各平台的登录字段。
- 修复代理的用户名或密码含有 `@`、`:`、`/` 等字符时代理无法使用：此前直接拼进代理地址，httpx 与 python-socks 报端口无效，接口、下载与代理检查都会失败。现在按 URL 编码，此前已经自己编码填写的值仍然有效。直播弹幕连接按已安装的 websockets 版本处理：17.2 起它才解码代理地址中的用户名与密码。
- 修复命令行 `--proxies` 的几处问题：`f2 x` 指定 `socks5`、`https` 代理时代理被忽略（返回的配置键名写成了 `http`、`https`）；`f2 bk` 无法解析文档中带用户名密码的 `username:password@host:port`，提示端口必须是数字；密码中有 `@` 时无法识别。现在五个应用共用同一个解析函数，返回与配置文件相同格式的代理配置（`--update-config` 写入配置文件的也是这个格式），命令行指定的代理不再检查两次。
- 不再支持 Python 3.10，最低版本改为 3.11：Python 3.10 于 2026-10 结束官方支持，websockets 17 等依赖的新版本也已不再支持它。CI 在 3.11–3.14 上运行测试，mypy 另按 3.11 检查一次。
- 直播弹幕改用 websockets 新版 asyncio 接口，支持 websockets 15–17（此前限制在 13 以下）：websockets 14 起顶层的 `connect`、`serve` 换成新版实现，F2 传入的 `extra_headers` 会直接报错。15 起原生支持 HTTP 与 SOCKS 代理，去掉依赖旧版实现的 `websockets_proxy`；配置了代理时使用它（新格式 `type`、`host`、`port` 的代理配置此前在弹幕连接中被忽略），否则使用环境变量与系统设置中的代理。服务器持续拒绝握手时不再无限重试，最多尝试 3 次。真实抖音直播间实测弹幕接收与本地转发正常。
- protobuf 放宽到 7.x：直播消息的生成代码由 protoc 5.29.3 生成，6.x、7.x 运行时都能直接使用，无需重新生成；新增用录制的直播间消息检查解析结果的测试，CI 另用 websockets、protobuf 的最低版本运行一次离线测试。
- 推特从网页脚本获取的 queryId 缓存到本地，直到下次更新：内置 queryId 失效后，此前每次运行都要先请求一次失效的地址，再下载约 1.6 MB 的网页脚本。现在获取到的值写入 `~/.f2/cache/twitter_graphql.json` 并记录它替换的内置值，内置值不变时之后的运行直接使用；X 再次更换时重新获取；F2 更新内置值后旧记录不再使用，仍然内置优先。内置 queryId 集中到 `f2.apps.twitter.api.QUERY_IDS`，接口地址由它生成。
- 修复环境变量或系统设置中的代理覆盖了 F2 中配置的代理：httpx 默认读取环境与系统代理并挂在 `http://`、`https://` 上，比 F2 挂在 `all://` 上的配置更具体，接口与下载请求都改走环境或系统代理，配置的 HTTP 与 SOCKS 代理不生效。现在配置了代理时不再读取环境与系统代理。
- 修复只开系统代理时 TikTok 接口请求不走代理：TikTok 接口由 curl_cffi 发送，libcurl 不读取 macOS、Windows 系统设置中的代理，没有在 F2 中配置代理时这部分请求直连。现在与 httpx 一样使用环境变量与系统设置中的代理。
- 修复推特 `desc.txt` 的文案与推文错位：主页、喜欢与收藏的 `tweet_desc_raw` 跳过了没有文案的条目，推荐关注等模块之后的推文都拿到了下一条推文的文案。`desc.txt` 现在保存完整文案：超过 280 字的长推文取 `note_tweet`，转推取原推文并保留 `RT @用户名:` 前缀，短链接换成原始链接，不再只保存第一个链接之前的文字；文件名中的 `{desc}` 不变。
- TikTok 视频 CDN（Akamai）返回 403 Access Denied 时提示更换代理节点：实测与 cookie、请求头、TLS 指纹都无关，取决于网络出口所在地区；FAQ 已说明。
- 推特喜欢模式请求别人的喜欢时，说明 X 的喜欢列表只对本人可见（此前提示“该用户没有公开喜欢的推文”）。
- 推特适配 X 新版接口：queryId 与 features 更新为 2026-10 网页端使用的值。新的 queryId 返回新版结构：用户对象不再有 `legacy`（名称等字段移到 `core`、`profile_bio` 等处），主页与喜欢列表的 `timeline_v2` 改名为 `timeline`，只换 queryId 会取不到昵称与推文；过滤器现在先把响应整理成原来的结构再读取（`f2.apps.twitter.filter.normalize_graphql_response`），新旧 queryId 返回的数据都能解析。时间线中包在 `TweetWithVisibilityResults` 里的受限推文此前没有作者信息，被当成广告跳过；推文详情中作者的粉丝数、所在地等字段少了 `legacy` 一级，此前始终为空。
- 推特接口的 queryId 失效时自动从 X 网页脚本中获取新的值：内置值返回 404（`Query not found`）时，用 cookie 打开 x.com，从页面加载的 `main.js`（收藏等查询在按需加载的脚本里，按名称查找）读取新的 queryId 并重试，同一进程内之后的请求都使用新值，不需要等 F2 发布新版；新查询需要的 features 开关缺失时补上 `false`。内置值仍然优先使用：它对应的响应结构经过测试，实测 2023 年的旧 queryId 至今仍可用，只在失效时才切换。新增 `TwitterCrawler.fetch_graphql_operation` 与 `f2.apps.twitter.utils.parse_graphql_operations`，FAQ 新增“twitter 404 / Query not found”。
- 修复推特主页模式漏下载置顶推文与串推：置顶推文在 `TimelinePinEntry` 指令里，串推（自己回复自己）在 `profile-conversation` 模块里，此前都不会下载，实测 NASA 主页第一页 18 条推文只下载了 9 条。串推在相邻两页重复出现时也不再重复计数。
- 修复推特喜欢、收藏的推文是回复时取成了根推文的 ID：此前取 `conversation_id_str`，文件名中的 `{tweet_id}` 是别人的推文，同一会话的多条回复同名，后面的被当成已下载跳过。
- 修复推特图文混合、多个视频的推文下载不全：下载器此前只按第一个媒体的类型处理，图片在前时视频只得到缩略图，推文详情中有多个视频时一个都不下载。现在逐个下载，图片仍为 `_image_序号`，只有一个视频时仍为 `_video`，多个视频时为 `_video_1`、`_video_2`；过滤器新增 `tweet_media`。
- 修复推特设置日期区间后一条推文都不下载（移植自 #461）：下载器按推文数据中不存在的 `createTime` 字段筛选。现在按发布时间戳筛选，与其他平台一样按北京时间计算区间；新增 `-i/--interval` 选项（移植自 #461）。`post` 模式翻到区间开始之前的推文即停止翻页，不再翻完整个主页；`like` 与 `bookmark` 按点赞、收藏的时间排列，仍然翻完全部页面。
- 修复推特各模式的 `--max-counts` 不按整页截取：接口不按 `count` 返回，一页的推文数可能超过剩余数量，此前整页都会下载。设置日期区间时按区间内的推文计数。
- 修复只靠系统代理上网时获取文件大小失败，媒体被当成 0 字节跳过（移植自 #462）：获取文件大小的 HEAD 请求此前总是指定传输层，httpx 因此不再读取环境变量与系统代理；没有在 F2 中配置代理、只靠系统代理（如 Clash 的系统代理模式）上网时，接口请求正常，下载却全部跳过。下载器现在把自己的传输层传给 `get_content_length`，代理设置与下载请求完全一致，新格式的 SOCKS 代理此前在这一步也被忽略。
- 支持 Python 3.14：CI 测试矩阵加入 3.14，Lint 改用 3.14 并按最低支持的 3.10 再运行一次 mypy（依赖库的类型标注会按 Python 版本区分，此前 3.12 及以下的 mypy 报 `impersonate.py` 缺少类型标注）；Python 3.14 上要求 `pydantic>=2.12`。工作流中的 Action 升级到支持 Node 24 的版本；离线测试不再访问真实网络（抖音弹幕的用例此前会请求 `ttwid.bytedance.com`），没有 `network` 标记的用例解析外部主机时直接报错。
- 修复配置文件里写成 `no` 的开关反而被打开：`ruamel.yaml` 按 YAML 1.2 解析，`yes`/`no`/`on`/`off` 会被读成字符串，而字符串 `"no"` 为真，配置 `folderize: no`、`cover: no` 时功能照样开启（登录态实测封面、文案、音乐都下载了），`enable_bark: no` 会打开 Bark 通知，`check_update`、`verify` 同理。现在这些开关接受 `true`/`false`、`yes`/`no`、`on`/`off`、`1`/`0`，应用的开关写成其他内容时报错退出；新增 `f2.utils.config.merge.parse_bool` 与 `coerce_bool_options`，配置文档补充了开关的写法。
- 修复 TikTok 合集模式只列出前几个合集、只有一个合集时选择出错：合集列表此前只取第一页（`--page-counts` 默认 5），现在翻完全部页面；只有一个合集时合集 ID 被当成字符串，选择列表会把 ID 的每个字符当成一个合集。没有合集时直接结束，不再创建用户目录；选择提示中误写的“收藏夹ID”改为“合集ID”。
- 修复抖音直播间排行榜只有一位观众时 `_to_list` 报“由于接口更新，部分字段处理失败”，以及缺少签名等字段时后面观众的值错位；抖音作品的 `caption`（命名模板 `{caption}`）同样会错位，只有一个作品时只取到第一个字；TikTok 作品详情的话题在只有一个时是字符串。这些带 `[*]` 的字段现在都按列表读取。
- 抖音主页作品与首页推荐在接口没有返回翻页信息时，提示游客 `cookie` 只能获取主页第一页（#435）：实测游客 `cookie` 请求第一页之后的任何游标，接口都只返回状态码，没有作品也没有 `has_more`，此前会提示“所有作品采集完毕”，像是已经下完；登录状态下每页都带有 `has_more`，到底时为 `0`。设置 `--interval` 时第一次请求就从区间的结束时间开始，游客 `cookie` 一个作品也拿不到；文档与 FAQ 已说明这两种情况需要登录后的 `cookie`。
- 修复抖音与 TikTok 翻页时可能不间断地重复请求同一页：抖音主页、喜欢、首页推荐遇到空页面时立即重新请求，不等待也不检查游标，有作品的页面之后不看 `has_more`，最后一页之后还会多请求一次；音乐收藏、收藏、收藏夹作品、合集在接口返回同一个游标时会一直重复；TikTok 搜索接口出错且游标为空时同样会立即重复请求。现在每页处理完后 `has_more` 为假即结束，游标为空或没有变化时提示并停止，继续翻页前都会等待。
- 修复抖音喜欢、收藏等模式与 TikTok 各列表模式的 `--max-counts` 不生效（#443）：这些接口不按请求的数量返回，或请求时传的就是 `--page-counts`，整页作品都会下载（复测中 `max_counts` 为 2 时抖音喜欢模式处理了 18 个作品）。抖音的主页、喜欢、音乐收藏、收藏、收藏夹、合集、feed、相关推荐、好友作品，以及 TikTok 的主页、喜欢、收藏、合集、搜索，在交给下载前都截到剩余数量；新增 `f2.utils.json.filter.limit_page_items`。文档补充说明了两个参数的区别：`--max-counts` 是本次总共下载多少，`--page-counts` 只决定每次向接口请求多少；TikTok 的 `--page-counts` 默认值在文档中更正为 `5`。
- 修复抖音收藏夹模式只列出第一页收藏夹（#443）：此前把作品数上限 `--max-counts` 也用来限制收藏夹数量，第一页就达到上限时只会列出这一页（复测中共 12 个收藏夹只列出 5 个）。现在先取出全部收藏夹再选择一次（此前分多页时每页各弹一次选择），`--max-counts` 按每个收藏夹分别计算；没有收藏夹时提示后结束，不再弹出只有“全部下载”的选择。
- 修复抖音 `fetch_user_live_videos_by_room_id` 使用登录 cookie 时报 `object of type 'NoneType' has no len()`（#367）：`fetch_live_room_id` 只清空了客户端默认请求头里的 Cookie，每次请求仍会带上登录 cookie，接口返回状态码 101 与空数据。现在这个接口用空 cookie 请求；没有返回直播间数据时抛出带状态码的 `APIResponseError`。
- 修复抖音点赞模式在对方没有公开点赞列表或 cookie 没有登录时只提示“重试次数达到上限”：现在说明可能的原因。
- 修复抖音好友作品模式丢掉最后一页：此前在交出作品之前就判断没有下一页而结束；本页没有作品时也不会再用同一个游标不停地重复请求。
- 修复抖音 `fetch_query_user` 在查询成功时误报“请提供正确的ttwid”：接口成功时现在返回状态码 `0`，此前只把没有状态码当作成功。
- 直播弹幕连接关闭后，正在处理的消息发送 ack 失败不再以错误级别打印完整堆栈（抖音与 TikTok）。
- 抖音直播弹幕的 `signature` 改为纯 Python 计算，不再通过 `PyExecJS` 调用 `Node.js`：`DouyinWebcastSignature` 实现了网页端 SDK（webmssdk 1.0.0.53）的 `frontierSign`，在相同随机数下与原来的 JavaScript 结果逐字节一致，并在真实直播间验证可以正常接收弹幕。移除 `PyExecJS` 依赖与 350 KB 的 `webcast_signature.js`，获取直播弹幕不再需要安装 `Node.js`。`DouyinWebcastSignature` 不再接受 `user_agent` 参数：原实现只是把 UA 写进 JavaScript 运行环境，换用不同的 UA 签名结果完全相同，现在直接调用 `DouyinWebcastSignature().get_signature(room_id, user_unique_id)`；新增 `frontier_sign` 方法，可用关键字参数 `rng` 指定随机数来源。
- TikTok 的 `TokenManager.gen_ttwid` 改为读取打开首页时服务器下发的 `ttwid`：`ttwid/check` 接口现在只做校验、不再下发 `ttwid`，此前总是报“ttwid 检查没有通过”；配置文件中 TikTok 的 `ttwid` 配置不再使用。`gen_odin_tt` 请求时跟随跳转，拿不到时明确提示 TikTok 已不再向未登录用户下发 `odin_tt`（只有登录后的 cookie 中才有），文档中标为将会弃用。这两个方法只供作为库调用，F2 自身的下载流程不受影响。
- 修复 Twitter 用户链接解析出的用户名为 `i` 的问题：`UniqueIdFetcher` 此前总是请求链接后再从最终地址提取用户名，x.com 在未登录时会把 `https://x.com/用户名/followers` 等页面跳转到登录页 `/i/flow/login`，于是得到保留路径 `i`。现在链接里带着用户名时直接取出、不发请求；t.co 短链等仍需请求时跳过 x.com 的保留路径，并从登录页的 `redirect_after_login` 参数取回原地址。
- 润色英文翻译：逐条审阅全部 935 条英文文案，改写其中 650 条。统一术语（作品 post、主页 profile、直播 livestream、直播间 live room、弹幕 danmaku、接口地址 API endpoint、配置文件 configuration file；抖音与 TikTok 按平台接口的命名，点赞（喜欢）为 favorites、收藏为 collection、收藏夹为 collection folder、合集为 mix，Twitter 仍用 likes 与 bookmarks），消息改为普通句式、不再逐词首字母大写，同一句中文只保留一种译法。修正误译：“配置文件的路径，最低优先”曾译为 highest priority，“配置文件路径无写权限”曾译为“配置文件不存在”，FAQ 提示的两句英文粘在一起，Bark 密钥长度把“位”（字符）译成了 bits；下载进度的状态与文件类型标签统一为 Done、Skipped、Video、Caption 等。收藏夹列表的提示不再用方括号，避免被 rich 当作样式标签。横幅的英文简介改为 “An asynchronous, multi-platform downloader”；英文文档中抖音、TikTok 的模式说明与 CLI 帮助统一叫法，TikTok 播放列表接口的 `secUid` 说明由“合集ID”更正为“用户ID”。
- 补齐英文翻译：此前有 217 条文案在英文界面下仍显示中文，其中 102 条从未翻译，115 条因原文修改被标记为待确认（编译时会被跳过），涉及代理设置、下载进度、断点续传、m3u8 直播流、数据库与抖音弹幕、评论等提示；现在全部有英文译文，原有 718 条译文不变。
- TikTok 的 `https://www.tiktok.com/user/<sec_uid>` 链接直接从地址中取出 `sec_uid`，不再发请求（#366）：这类页面里没有用户数据，此前会报“未在响应中找到 __UNIVERSAL_DATA_FOR_REHYDRATION__”或“接口状态码异常”。直播模式需要用户名，请使用 `@用户名` 形式的主页链接。
- 直播弹幕因本地 WebSocket 服务器没有客户端连接而停止时，不再提示“直播间已结束直播”：抖音与 TikTok 的本地转发服务在超时时间内没有客户端连接时会断开与弹幕服务器的连接，此前与直播结束一样返回 `closed`，现在返回 `no_client`，并提示“本地 WebSocket 服务器没有客户端连接，已停止接收直播间的弹幕，直播可能仍在进行”；因其他原因关闭时提示“弹幕连接已关闭，可能已结束直播”，不再断言直播已经结束。`WebSocketCrawler.close_websocket` 新增 `reason` 参数，爬虫主动关闭连接时 `receive_messages` 返回该原因。
- 修复本地弹幕转发服务的端口被占用时抛出 `UnboundLocalError` 的问题：启动失败后 `finally` 仍会关闭尚未创建的服务器，这个异常要等弹幕接收结束才抛出并打断调用；现在只记录启动失败的原因，弹幕照常接收。
- 修复 TikTok 检查开播状态（`fetch_check_live_alive`）与直播弹幕初始化（`fetch_live_im`）一调用就报错“msToken 内容不符合要求”的问题：这两个请求模型不再联网生成 `msToken`，与 `www.tiktok.com` 的接口一样在签名时从 cookie 读取。实测 `webcast.tiktok.com` 的 `im/fetch` 现在只接受新版签名加浏览器指纹（只用 X-Bogus，或只换成 curl_cffi，都返回空内容），两个直播接口因此改用 `XGnarlyManager` 签名并由 curl_cffi 发送；检查开播、初始化与 WebSocket 接收弹幕的完整流程已实测可用。CLI 的直播下载模式（`-M live`）不经过这两个接口，此前不受影响。
- `TokenManager.gen_real_msToken` 只检查 mssdk 是否下发了 `msToken`，不再要求 152 位：接口下发的 `msToken` 现在是 168 位，此前会误报“msToken 内容不符合要求”；没有下发时也不会再把字符串 `None` 当成 `msToken`。
- 修复 TikTok 网页接口返回 200 空内容的问题（#384）：`www.tiktok.com` 的接口改用网页 SDK 的新版签名，在业务参数之后依次追加 `X-Dynosaur`、`msToken`、`X-Bogus`（固定为 `1`）与 `X-Gnarly`，签名前按 RFC 3986 编码参数值，与浏览器抓包一致；`msToken` 只从 cookie 读取，没有时留空，不再联网生成或伪造，`www.tiktok.com` 的请求模型不再携带 `msToken`。这些接口还会校验 TLS 与 HTTP/2 指纹，`httpx` 发出的请求即使签名正确也只会得到空内容，`TiktokCrawler` 现在通过新增的运行时依赖 `curl_cffi`（`>=0.16.3,<0.17`，MIT 协议）模拟 Chrome 发送 `www.tiktok.com` 的请求，`webcast.tiktok.com` 与文件下载仍使用 `httpx`；缺少 `curl_cffi` 时（例如使用 `--no-deps` 安装）回退 `httpx` 并在日志中提示。用户信息等接口需要登录后的 cookie，用户发布作品用游客 cookie 也能获取。新增纯 Python 实现的 `f2.utils.crypto.bytedance.xgnarly`、`XGnarlyManager` 与 `f2.utils.http.impersonate`，FAQ 新增对应条目。
- TikTok 获取 `secUid`（`SecUserIdFetcher`）与设备 ID（`DeviceIdManager`）时不再生成 `msToken`：旧的 `msToken` 生成接口已失效，此前会在发出请求前就报错“msToken 内容不符合要求”；主页与首页的 HTML 不需要 `msToken`。
- `getXBogus` 计算签名时纳入请求体：此前固定按空请求体计算，传入的 `body` 被忽略。F2 自身目前只给 GET 请求签名，签名不变；作为库给 POST 请求签名时才会受影响。
- 微博 `--page-counts` 的帮助与文档如实说明对微博不生效：微博主页接口不支持指定每页数量，每页固定返回约 20 条，需要限制数量时请使用 `--max-counts`。
- 修复 twitter 主页推文与书签在一页只有一个条目时崩溃的问题：`jsonpath_ng` 对超出列表长度的负数下标（如只有 1 项时取 `[-2]`）会抛出 `IndexError`，`min_cursor` 因此报错，连带 `_to_list`、`_to_dict` 失败。`JSONModel` 的查询现在把这种情况视为字段缺失，所有平台的过滤器都受益。
- 抖音按分辨率与码率选择最高清晰度（#214）：此前固定取清晰度列表的第一项，而接口按码率排序，2K、4K 只有 H.265 版本时码率可能低于 1080p 的 H.264，会下载到 1080p。现在先比较分辨率、再比较码率，清晰度列表为空时改用 `video.play_addr`；普通作品下载的文件不变。新增 `select_best_bit_rate`、`get_video_play_urls`。最高清晰度可能只有 H.265 编码，FAQ 已说明。
- 抖音作品被删除或设为私密时，报错给出接口返回的原因（如“因作品权限或已被删除，无法观看”），不再提示“动图作品接口正在维护中”。
- `--auto-cookie` 读取 Chrome、Edge 失败时给出原因与解决办法（#193、#205）：Windows 上的新版 Chrome、Edge 改用了应用绑定加密，`browser_cookie3`（0.20.1，目前的最新版）还不能解密。报错 `Unable to get key for cookie decryption` 时现在会提示改用 `--auto-cookie firefox` 或手动复制 cookie，并附上 FAQ 链接；cookie 数据库被占用时提示关闭浏览器后重试。FAQ 新增对应条目，各应用的 `--auto-cookie` 说明链接到它。新增 `f2.utils.http.browser.explain_browser_error`。
- 修复 `--auto-cookie` 获取失败时退出码仍为 `0` 的问题：`finally` 中的 `ctx.exit(0)` 会覆盖失败时的 `abort`。现在读取浏览器失败、没有取到 cookie 或权限不足时输出原因并以退出码 `1` 结束，确认更新配置时被取消（如输入已结束）同样以 `1` 结束；获取成功或选择不更新配置时仍为 `0`。
- 没有提供 cookie 时抛出 `ConfError`，只报一行错误：此前抖音、TikTok、twitter、微博的下载器抛出 `ValueError`（`kwargs` 里没有 `cookie` 时是 `KeyError`），会打印完整堆栈。只检查是否提供了 cookie，空字符串仍然允许，因为抖音直播等请求不需要用户的 cookie；通过 CLI 运行时，配置里空的 cookie 是空字符串，所以主要影响作为库使用的场景。微博的提示文字与其他应用统一。
- 修复作者改名后另建文件夹、重新下载全部作品的问题：此前 `create_or_rename_user_folder` 先按新名称建目录，再把新目录「重命名」为它自己，旧目录从不搬动。现在名称变化时，把各下载模式下旧名称的目录一起重命名为新名称，已下载的作品随目录保留；某个模式下新名称的目录已存在时，该模式的两个目录都保持不变，不覆盖也不合并，并在日志中提示；重命名失败（例如目录中的文件正被占用）时当前模式本次继续使用旧目录。各模式的旧目录都改名后，数据库中的名称更新为新名称（此前从不更新），作者以后再改名也能继续跟随；还有冲突或改名失败的旧目录时保留旧名称，下次运行继续处理。抖音、推特、微博按昵称，TikTok 按用户名（`uniqueId`）；TikTok 单个作品与直播模式按新用户名查不到本地记录时改按 `secUid` 查找。#248 调整文件名规则后很多作者的文件夹名会变化，升级后旧文件夹会在下次下载时自动改为新名称，不再另建文件夹（文件名变化的作品仍会按新名称重新下载一次）。新增 `f2.utils.file.path.get_user_folder_path`、`migrate_user_folder`、`migrate_user_folders` 与 `is_user_folder_migrated`；微博 `AsyncUserDB` 新增拼写正确的 `update_user_info`（`updat_user_info` 仍可使用）。
- 抖音、TikTok、twitter 的日期区间格式错误或结束日期早于开始日期时，在发起请求前以一行错误退出（退出码 `1`）。此前只记一条日志：主页等模式会翻完全部页面，却因筛选失败一个作品都不下载，并且每页重复报错。校验在创建下载器时进行，作为库使用时同样生效；主页作品的翻页游标改用 `parse_interval` 计算，结果不变。
- 配置错误中的配置项名称不再被日志脱敏打码：`ConfError` 的标签由 `Key` 改为 `Setting`（此前 `Key: interval` 会被当成密钥显示为 `Key: ***`）；`cookie`、`key`、`token` 等敏感配置项的值在异常文本中直接打码，此前被打码的只是键名，`Value` 中的值反而原样输出。`InvalidConfError`、`InvalidEncodingError` 的配置项与值改由 `ConfError` 统一追加。
- 配置文件出错时只输出一行错误：`-c` 指定的配置文件无法解析时不再抛出 `RuntimeError` 并打印完整堆栈，而是给出出错的行号、列号与文件路径；文件不是 UTF-8 编码、顶层不是键值映射（此前抛出 `AttributeError`）或没有该应用的配置（此前抛出 `ValueError`）时同样只报一行，并以退出码 `1` 结束，缺少应用配置时提示可以用 `--init-config` 补充。用户级 `conf.yaml` 与 `--init-config` 遇到的解析错误也改为同样的一行格式。新增 `ConfigManager.get_app_config`。
- `-c` 指定的配置文件不存在时，报错中显示用户给出的路径，不再显示包目录下的路径。
- 修复一个文件无法保存就中止整批下载的问题（#179）：目录无法创建、文件无法打开或改名、`desc.txt` 等文本文件写入失败时，只把这个文件记为下载失败并继续下载其它文件，结束时列出失败的文件并以退出码 `1` 结束；这类本地文件错误不再换链接重复请求。`Path.exists` 遇到文件名过长时抛出的异常也不会再中止下载。
- 文件名连同后缀超过 `255` 字节时截断中间部分（#179）：`ext4` 与多数 `NAS` 按字节限制文件名长度，中文文件名此前容易超出而无法保存。默认命名模板的文件名不会触及上限，不受影响；拼接了昵称、多段文案等字段的自定义模板生成的超长文件名会被截断，在 `Windows`、`macOS` 上已按原名下载的这类文件会按新名称重新下载一次。新增 `f2.utils.file.name.fit_filename`。
- `Windows` 下路径超过 `260` 个字符时自动改用扩展长度路径（`\\?\`），不需要开启系统的长路径支持（#179）；新增 `f2.utils.file.path.long_path`。
- 微博主页模式支持 `--interval` 日期区间（#222）：微博主页接口不支持按日期查询，改为从最新的微博开始翻页，只下载区间内发布的微博（首尾两天都包含，按北京时间计算），翻到区间开始之前的微博时停止；置顶微博在区间内时同样下载，不影响翻页。日期格式错误或结束日期早于开始日期时直接报错退出，不会发起请求。`fetch_user_weibo` 新增 `interval` 参数；新增 `f2.utils.time.timestamp.parse_interval`。
- 修复微博主页模式的 `--max-counts` 不生效：此前没有传给翻页函数，总是下载全部微博；接口每页固定返回约 20 条，超出上限的部分会被截掉。
- 修复 `--no-log-file` 时出错会把完整堆栈打印到控制台的问题：没有日志文件时错误堆栈直接丢弃，控制台只输出一行错误原因。
- 语言切换测试改为写入配置副本，运行测试不再改动包内的 `conf.yaml`。
- 文件名规则变化，升级后会按新文件名重新下载一次（#248）：文案与昵称不再把标点、空格、日文假名、emoji 等字符替换为下划线，只把系统不允许的 `\ / : * ? " < > |` 换成外观相近的全角字符，换行等控制字符换成空格或去掉，并去掉首尾空格与结尾的点。多数作品的文件名和部分作者的文件夹名会因此变化：作者文件夹会在下次下载时自动改为新名称，同步主页时文件名变化的作品会按新名称重新下载，旧文件仍留在文件夹中，可按需清理。各应用的命名模板文档已同步说明。
- TikTok 生成设备 ID 时同样逐个读取 `Set-Cookie` 头，`tt_chain_token` 等值里带逗号时不再被截断；新增 `f2.utils.http.cookie.join_set_cookie_headers`，微博游客 cookie 也改用它。
- 微博生成游客 cookie 时逐个读取 `Set-Cookie` 头，不再把多个头拼成一行后按逗号切分，值里带逗号时不会被截断（移植自 #434）。
- 支持用户级 `conf.yaml` 覆盖默认配置（#377）：按优先级从低到高读取 `~/.f2/conf.yaml`、当前目录的 `conf.yaml` 与环境变量 `F2_CONFIG` 指定的文件，叠加在 `site-packages` 中的 `conf.yaml` 之上，只需写出要修改的部分；用户配置不会写回默认配置文件，界面语言仍由 `-l` 设置。
- `--init-config` 不再覆盖已有的配置文件：文件里没有该应用时追加默认配置，已有时只补充缺少的配置项，已有的值、其他应用的配置和注释都会保留，修改前把原文件备份为同名 `.bak` 文件；配置文件无法解析或顶层不是键值映射时报错且不做修改。同一个文件可以依次为多个应用初始化。
- CLI 新增全局选项 `--no-log-file`（#293）：写在应用名之前时只在控制台输出日志，不创建 `logs` 目录，也不清理旧日志，适合没有写文件权限的环境；作为库使用时本来就不会写日志文件。
- 修复抖音直播弹幕无法获取的问题（#412）：弹幕初始化接口新增了对 cookie 字段 `x-web-secsdk-uid` 的强校验，缺少时返回空内容。`fetch_live_im` 现在会在 cookie 缺少该字段时自动补上随机值；新增 `TokenManager.gen_secsdk_uid` 与 `TokenManager.ensure_secsdk_uid`，文档示例的 cookie 同步更新（`__live_version__` 更新为 `1.1.4.7838`）。
- 修复 Twitter 单条推文下载失败（#436、#404）：接口在 `instructions` 前面插入了 `TimelineClearCache` 指令，推文详情改为按指令内容与 `entryId` 定位目标推文；评论或回复的链接不再下载到上层推文（#234）；受限推文（`TweetWithVisibilityResults`）也能读取。
- 修复 Twitter 推文文案为空时报 `'NoneType' object has no attribute 'strip'` 的问题（#436、#404）。
- Twitter 视频只取 MP4 并按码率选择最高清晰度，不再依赖接口返回的变体顺序（#436、#368）；新增 `sort_mp4_urls`、`best_mp4_url`。
- Twitter 自动把 `cookie` 中的 `ct0` 作为 `X-Csrf-Token`，并优先于配置文件里的值，避免两者不一致导致 403（#426，移植自 #442）。
- Twitter 主页、点赞、书签推文的命名模板支持 `{uid}`（移植自 #442）。
- 修复抖音 `51`、`53`、`66` 等新作品类型不下载的问题（#402）：下载器不再使用写死的作品类型名单，图集作品或带有图片的作品下载图集，其他作品只要有视频链接就下载视频；新增 `DouyinDownloader.download_media`。
- 抖音作品没有可下载的视频或图片、或可见状态不支持下载时输出警告并注明原因，此前会静默跳过。
- 修复查询串不超过 32 个字符时生成 X-Bogus 抛出越界异常或得到错误签名的问题（#389）：原始字符串一律按原文计算 md5，只对 md5 摘要做十六进制解码；过短的自定义 `User-Agent` 同样受影响，已一并修复。正常长度查询串的签名不变。
- 修复抖音合集下载失效（#423）：合集短链现在会跳转到短剧分享页 `share/playlet/detail/`，而 `MixIdFetcher` 只识别 `collection/`。现在支持合集页、合集分享页 `share/mix/detail/` 与短剧分享页，地址里已经带有合集 ID 时不再发起请求；短剧按合集下载。
- 抖音合集模式不再吞掉解析错误：只有链接不是合集页时才改用作品链接解析，并在警告里给出原因；作品不属于任何合集或合集为空时以明确的错误结束（此前合集为空会报变量未绑定）。
- 翻译源文件 `.po` 纳入版本控制：由现有 `.mo` 重建 `en_US.po` 与 `zh_CN.po`，放在各自 `.mo` 所在目录且不打包进 wheel；`make_pot` 脚本改为只用 `pybabel` 从 `f2` 与 `tests` 抽取文案、更新这两个 `.po` 并编译 `.mo`，位置引用只保留文件名；新增测试检查 `.mo` 与 `.po` 的译文一致。重建时移除了 74 条代码中已不存在的旧译文，现行文案的译文不变；`Babel` 开发依赖下限提高到 2.14.0。
- 修复 GitHub 安全页的文档依赖告警：文档站 `vitepress` 升级到 1.6.4，并通过 `pnpm.overrides` 使用 `vite` 6.4.3，同时刷新锁文件中的 `esbuild`、`rollup`、`postcss`、`nanoid`、`preact` 与 `mdast-util-to-hast`；这些依赖只用于构建文档，不影响 PyPI 包。
- 开发依赖升级：`black` 26.5.1（修复缓存文件任意写入漏洞，`pre-commit` 同步到同一版本，并按新版风格重新格式化）、`pytest` 9.1.1（修复临时目录处理漏洞）与 `pytest-asyncio` 1.4.0（旧版不支持 `pytest` 9）。
- `bark` 推送加密使用 `ECB` 模式时输出安全警告；保留该模式只为兼容 Bark App 的同名选项，推荐使用 `CBC`。
- `bark` 推送加密的随机 `iv` 改为由字母和数字组成，不再只用数字（此前 `GCM` 的 12 位 `iv` 只有约 40 比特随机性，同一密钥推送量大时可能重复）；新增 `generate_alphanumeric_bytes`。
- Issue 模板改为表单：关键信息设为必填，新增「平台接口失效」与「文档问题」模板，关闭空白 issue，并把一般提问与功能想法引导到讨论区、安全问题引导到私密报告；新增按表单中所选平台自动添加标签的工作流。
- 修复微博、TikTok、twitter 在第一页就结束或没有作品时报 `nickname_raw` 未绑定的问题（#401，此前只修复了抖音）。
- 修复微博视频的类型为整数 `11` 时被判定为无法下载的问题（#249、#359）。
- 修复 TikTok 主页作品翻页：接口返回字符串游标时第二页崩溃、最后一页之后从头重新抓取、空页面返回错误码时反复请求（#270）；点赞、收藏、合集每页作品数被重复计数，导致只下载到一半就结束。
- 文档：快速上手与配置文件页中的 `f2 apps` 改为 `f2 dy` 等具体命令，列出各应用简称（#439）。
- 贡献规范：`PR` 需提交到当前开发分支（目前为 `v0.0.1.8-pw3`），不要提交到 `main`；新增 `PR` 模板与目标分支检查工作流，`dependabot` 改为向开发分支提交更新，`README` 的开发分支徽章更新为 `v0.0.1.8-pw3`。
- 异常在构造时不再输出日志：`CLI` 中止时只输出一行错误原因和 FAQ 链接，不再重复打印四五行错误；读取配置等准备阶段抛出的 `F2Error` 也按同样方式报告，不再打印完整堆栈。作为库使用时由调用方决定是否记录。
- 修复 `FileError` 没有文件路径时异常信息为空的问题（移植自 #433）。
- 修复出错时 `CLI` 退出码仍为 `0` 的问题：接口请求失败（HTTP 状态码错误、重试耗尽、网络错误、返回内容不是 JSON）不再被吞成空数据，而是抛出 `F2Error` 子类，`CLI` 以退出码 `1` 结束；有文件在所有链接都尝试后仍下载失败时，同样以退出码 `1` 结束并列出失败的文件。
- 作为库使用时，`crawler` 与 `handler` 的方法在接口请求失败时抛出异常，不再返回空数据；接口异常的 `status_code` 为真实的 HTTP 状态码（此前为 `None`）。
- 修复 `bark` 通知发送失败时仍提示发送成功的问题；`f2 bark` 发送失败时以退出码 `1` 结束，作为下载通知时失败仍只记录日志。
- 修复抖音主页作品、单个作品、点赞、收藏等接口返回 `403`（`Blocked by ArgusSecurityPlugin`）的问题：请求自动附加网关要求的 `x-tt-argus` 请求头，并从 cookie 读取 `UIFID`/`UIFID_TEMP` 作为 `uifid` 请求头，游客 cookie 同样适用 #443（移植并扩展自 #446）。
- `conf.yaml` 中 `douyin.headers` 的全部请求头都会生效，不再只取 `User-Agent` 与 `Referer`，便于手动覆盖网关请求头。
- 新增 `f2.utils.http.cookie.parse_cookie_str`，把 Cookie 字符串解析为字典。
- 测试配置支持通过环境变量 `F2_TEST_<APP>_<KEY>` 与 `conf/test.local.yaml` 覆盖，个人 cookie 无需写入仓库。
- `wheel` 不再打包 `f2/apps/*/test` 测试目录与 `conf/test.yaml` 测试配置。
- 新增 `security` 工作流：`gitleaks` 泄露扫描与 `wheel` 内容检查。
- TLS 证书校验可配置：`conf.yaml` 新增 `verify`（默认开启），应用命令行新增 `--insecure`，作为库使用时可通过 `kwargs["verify"]` 传入。
- 版本检查改用 `packaging` 比较版本号，并开启证书校验。
- 修复分块下载重试时重复写入已下载字节的问题；服务器忽略 `Range` 返回整个文件时会重新下载而不是追加。
- 修复 m3u8 分片下载修改共享客户端默认请求头，导致同一下载器上其它请求丢失 `Referer`/`Cookie` 的问题。
- 导入 `f2` 模块不再产生副作用：请求模型的 `msToken` 改为首次实例化时获取并在进程内缓存（`TokenManager.cached_msToken`）；日志目录与日志文件仅在 CLI 启动或调用 `log_setup` 时创建；导入 `f2.utils.string.generator` 不再重置全局随机种子。
- `log_setup` 新增 `log_path` 参数，可自定义日志目录或传 `None` 关闭文件日志。
- 修复启动时清理旧日志会把当前进程刚创建的空日志文件一并删除、导致 macOS/Linux 下 CLI 日志文件丢失的问题。
- 新增 `ci` 工作流：`ruff`/`black`/`isort`/`mypy` 检查、Python 3.10–3.13 测试矩阵（`pytest -m "not network"`）、构建与 `wheel` 冒烟测试，并接管 Codecov 上传。
- 新增 `release` 工作流：发布 GitHub Release 后校验标签与版本号一致，并通过 PyPI Trusted Publishing 发布（草稿不触发，pre-release 只构建不发布）。
- 删除 `pytest.ini`，pytest 配置统一到 `pyproject.toml`（此前 `pytest.ini` 优先生效，`testpaths` 与 `network` 标记的注册都未起作用）；`isort` 跳过被 git 忽略的目录。
- 新增根异常 `f2.exceptions.F2Error`，接口/配置/数据库/文件四类异常都继承它；`CLI` 遇到 `F2Error` 时只输出一行错误并以退出码 `1` 结束（堆栈写入 `f2-trace` 日志），各应用 `handler.main` 对未知模式改为抛出异常。
- 随包发布 `py.typed`，类型检查器可以使用 `f2` 的类型标注（分类器早已声明 `Typing :: Typed`）。
- 富文本帮助（`-h`）补充 `--insecure` 选项，`-r` 显示为实际的 `--max_retries`；新增测试保证富文本帮助包含命令行定义的全部长选项。
- 补充本分支新增文案的英文翻译（证书校验、断点续传重试、版本比较）。
- 修复同一进程导入多个应用时模式表互相覆盖的问题：`mode_handler` 改为按应用注册，各应用 `handler.main` 通过 `get_mode_handlers(__name__)` 查找自己的模式；全局 `mode_function_map` 移除。
- 运行时依赖改为版本范围（下限为已验证或已修复漏洞的版本，上限为已验证最新版的下一个大版本），`babel`、`mypy-protobuf` 移至开发依赖，移除 `importlib_resources`（改用标准库）；`click`、`protobuf`、`cryptography` 的下限提升到已修复已知漏洞的版本。
- `security` 工作流新增 `pip-audit` 依赖漏洞扫描，并每周定时运行。
- 日志脱敏：`f2` 记录器在输出与向上传播前自动打码 cookie、token、密钥、密码与代理地址中的凭据；各应用调试日志打印配置时经 `redact_config` 处理，`bark` 不再以明文记录 API 密钥与设备密钥，代理探测不再记录带密码的地址。
- 修复全新安装后 `import f2` 报 `No module named 'sniffio'` 的问题：`httpx-socks` 升级到 0.11.0（0.10.x 使用 `sniffio` 但未声明依赖，新版 `anyio` 不再附带它）。
- 平台接口用例统一标记为 `network`，`pytest` 默认收集 `tests` 与 `f2/apps`；新增 `ruff` 配置并修复未使用导入/变量与裸 `except`；`twitter` 的 `UniqueIdFetcher`/`TweetIdFetcher` 改为使用配置代理。
- 更新文档：证书校验配置、`--insecure` 选项、测试凭据注入方式、直播分片请求头、msToken 获取方式、日志配置与 CI/发布流程说明。
- 改进配置文件与快速上手文档的表述，提升可读性。
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
