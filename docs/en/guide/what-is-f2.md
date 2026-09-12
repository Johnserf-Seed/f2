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

::: tip :bulb: Tip
`F2` redacts its logs automatically: `cookie`, `key`, `token` and password values from the configuration, as well as credentials inside proxy URLs, are masked (only a short prefix and the length remain) before a record reaches the console, log files or your own logging handlers. When using `F2` as a library and printing configuration yourself, run it through `from f2.log.redact import redact_config` first.
:::

## Log Output to Console

When `F2` is imported as a library, logs are only written to the console by default: no `logs` directory is created in the current directory and no old log files are cleaned up. To also write log files, call `log_setup` with a `log_path` (defaults to `./logs`; pass `None` to disable file logging). The `CLI` performs this setup automatically on startup.

<<< @/snippets/set-debug.py#log-2-console-snippet{6}

![log-2-console](/douyin/log-2-console.png)

::: tip :bulb: Tip
If you want more detailed logs in the console, you can use the `DEBUG` level. `log_setup` only takes effect once per process; later calls simply return the already configured `logger`. Exception tracebacks go to the separate `f2-trace` logger; as a library user you can enable its file output with `log_setup(log_to_console=False, log_name="f2-trace", lazy_file_creation=True)`.
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
> The `verify` under the `wss` section configures the certificate of the local danmaku forwarding service; the current version does not support enabling it, so keep it `false`. It is unrelated to the top-level `verify` in `conf.yaml`, which controls certificate verification for `HTTP` requests (enabled by default).
> The default timeout for both local and remote connections is `10` seconds.
> If the local connection does not connect to `WSS` within the timeout, `F2` will automatically disconnect to save resources.
