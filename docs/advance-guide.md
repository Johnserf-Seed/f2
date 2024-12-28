---
outline: deep
---

# 进阶用法

::: tip :bulb: 什么是进阶用法？
进阶用法是指在 CLI 命令的基础上，通过开发者接口的方法，提高工具的使用效率，或者解决一些特殊问题。
:::

## Douyin

### 批量采集直播流 <Badge text="Beta" type="warning"/>

![batch-lives](/douyin/batch-lives.png)

<<< @/snippets/douyin/batch-lives.py

> [!IMPORTANT] 重要 ❗❗❗
> 1. 抖音限制同一个账号无法进入同一个直播间，所以采集的时候不能观看直播。
> 2. 使用游客账号即可绕过第一条限制，游客账号可以参考生成 `mstoken` 与 `ttwid` 代码片段。
> 3. 请确保你的网络环境稳定，否则可能会导致采集中断。
> 4. 请确保你的设备性能足够，否则大量采集可能会导致设备卡顿，同时需要增大 `max_connections` 与 `max_tasks` 的值。