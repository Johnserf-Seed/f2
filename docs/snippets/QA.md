// #region response-is-null-snippet
只要是出现第 n 次响应内容为空均是`cookie`设置的问题。

你需要排查的是：
1. 检查对应app配置文件中的`cookie`值是否正确配置，未出现换行，空格，缺失，错误等。
2. 如抖音，完整的网页端抖音`cookie`有超过60多个键，tiktok为不到30个。如果你获取的`cookie`长度过短，那明显是无法正常使用的。
3. 使用`--auto-cookie`命令时，确保选择的浏览器中已登录正常账号，游客账号的`cookie`非常不稳定。
4. 如果你使用的是该app扫码登录的功能，可能会因为未知的设备环境风控造成网页端与app端账号下线。如果出现扫码登录的`cookie`失效，请使用`--auto-cookie`命令。
5. `0.0.1.2`之前的版本如果将`cookie`保存在自定义配置文件中，会有无法被正确识别的情况。
// #endregion response-is-null-snippet


// #region api-rate-limit-snippet
如果出现`API Rate Limit Error`时只需等待一会后重试即可。
继续频繁出现该错误需在网页端中重新登录并获取`cookie`。
仍无效后请切换网络环境和账号。

https://zh.wikipedia.org/wiki/HTTP%E7%8A%B6%E6%80%81%E7%A0%81
https://datatracker.ietf.org/doc/html/rfc6585#section-7.2
// #endregion api-rate-limit-snippet


// #region urlopen-errno-11001
该问题为本地网络连接问题，请检查你的网络连接是否正常。需要排查代理是否可以正常访问。
// #endregion urlopen-errno-11001


// #region f2-command-not-found
在非Windows系统中，如果出现`f2: command not found`错误，说明你的系统环境变量中没有添加`f2`命令的路径。

运行`which f2`命令查看`f2`命令的路径，然后将该路径添加到环境变量中。

添加环境变量的方法：
1. 编辑`~/.bashrc`文件，添加`export PATH="$PATH:/home/YOUR_NAME/.local/bin"`。
2. 运行`source ~/.bashrc`命令使环境变量生效。
// #endregion f2-command-not-found


// #region no-matching-videos-found
如果出现`WARNING  没有找到符合条件的作品`，请检查你是否配置了`interval`参数，该参数是用来设置作品发布时间的筛选条件。

解决办法：
1. 检查你的配置文件中是否有`interval`参数。如果没有，请添加为`interval: all`。
2. 如果你的配置文件中有`interval`参数，请检查你的`interval`参数是否设置正确。
3. `cli`命令中的`-i`参数也是用来设置作品发布时间的筛选条件 你可以设置为`-i all`。
4. 如果你使用了`-i`参数，请检查你的`-i`参数是否设置正确。

可参考的issue：
https://github.com/Johnserf-Seed/f2/issues/42
https://github.com/Johnserf-Seed/TikTokDownload/issues/660
// #endregion no-matching-videos-found
