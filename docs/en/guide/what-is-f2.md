# For Developers

If you're a developer or contributor, please read this document before checking out the API.

## Specify Configuration File

Developers can directly define their own configuration files and specify the path to the configuration file during testing using the `-c` parameter. For example:

```bash
f2 dy -c conf/app.yaml
```
Alternatively, you can specify the configuration file path directly in the code, for example:

<<< @/snippets/set-debug.py#set-config-snippet{3}

## Set Debug Log Level

<<< @/snippets/set-debug.py#set-debug-snippet{6}

In addition to supporting the code `API` mode, you can also use the `-d` flag in `CLI` mode to specify the log level. The available options are `DEBUG`, `INFO`, `WARNING`, and `ERROR`.

```bash
$ f2 -d WARNING dy -M post
```

![set-debug](/douyin/set-debug.png)

## Log Output to Console

<<< @/snippets/set-debug.py#log-2-console-snippet{6}

![log-2-console](/douyin/log-2-console.png)

::: tip :bulb: Tip
If you want more detailed logs in the console, you can use the `DEBUG` level. You must then use the `logger` object to output logs, otherwise, they won't be shown in the console.
:::

## WSS Configuration <Badge type="warning" text="Experimental" />

If you want to use the live-streaming bullet chat forwarding feature for `douyin` or `tiktok`, you need to configure the WSS service address and port.

The `WSS` configuration should be added to the `conf.yaml` file, as shown below:

::: code-group
```yaml [douyin]
douyin:
......
    wss:
      domain: localhost
      port: 8765
      verify: false
......
```
```yaml [tiktok]
tiktok:
......
    wss:
      domain: localhost
      port: 8766
      verify: false
......
```
:::

::: details :link: Example: Start `WSS` Service and Connect.
![wss](/douyin/wss-connect.png)
:::

> [!IMPORTANT] Important ❗❗❗
> The current version does not support enabling `SSL` certificate verification, so the `verify` parameter must always be set to `false`.
> The default timeout for both local and remote connections is `10` seconds.
> If the local connection does not connect to `WSS` within the timeout, `F2` will automatically disconnect to save resources.
