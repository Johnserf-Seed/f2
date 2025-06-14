# Common Issues and Solutions

## Empty Response on the nth Request

An empty response on the nth request is related to `cookie` settings.

::: details :link: Solution
1. Check the `cookie` value in the `app` configuration file for incorrect characters (e.g., newlines, spaces, non-ASCII characters).
2. The Douyin web `cookie` has over `60` keys, while TikTok's web `cookie` has fewer than `30`. A short `cookie` will likely cause issues.
3. When using `--auto-cookie`, ensure the browser is logged in with a normal account, as guest account cookies are unstable.
4. If you used QR code login in the app, the cookie might expire due to device environment risk control. Re-generate the `cookie` with `--auto-cookie`.
5. In versions before `0.0.1.2`, custom config file `cookies` may not be recognized correctly.

`Cookie` retrieval method: See the image below.
![Console Cookie](https://github.com/user-attachments/assets/4523e8c7-f74e-4d5f-9da6-6bb3658f8b24)
:::

## API Rate Limit Error

If you encounter `API Rate Limit Error`, simply wait and retry. This error is caused by too frequent requests being throttled by the server.

If it continues, log in again on the web and retrieve a new `cookie`. If still ineffective, switch networks or accounts.

**Reference Links:**
- https://zh.wikipedia.org/wiki/HTTP%E7%8A%B6%E6%80%81%E7%A0%81
- https://datatracker.ietf.org/doc/html/rfc6585#section-7.2

## <urlopen error [Errno 11001] getaddrinfo failed>

This issue is related to local network connection problems. Check if your network and `DNS` are functioning correctly. Ensure your proxy is properly configured.

## f2: command not found

On `non-Windows` systems, if you encounter `f2: command not found`, it means the `f2` command is not in your system’s PATH.

::: details :link: Solution
Run `which f2` to find the path of `f2` and add it to your environment variable.
1. Edit the `~/.bashrc` file to add `export PATH="$PATH:/home/YOUR_NAME/.local/bin"`.
2. Run `source ~/.bashrc` to apply the changes.
3. Reopen the terminal and use the `f2` command.
:::

## WARNING: No matching works were found

If you see `WARNING: No matching works were found`, check if you have configured the `interval` parameter correctly.

::: details :link: Solution
1. Ensure `interval: all` is set if the `interval` parameter is missing.
2. If `interval` is present, verify its value.
3. The `-i` flag also sets the content filter. Set it to `-i all`.
4. If you use `-i`, ensure it's configured correctly.
:::
**Reference Links:**
- https://github.com/Johnserf-Seed/f2/issues/42
- https://github.com/Johnserf-Seed/TikTokDownload/issues/660

## EOF occurred in violation of protocol (_ssl.c:992)

This indicates an SSL handshake failure.

Non-project issue, multiple possible causes need investigation.

::: details :link: Solution
1. Check if your proxy settings are correct and not blocking the `SSL/TLS` handshake.
2. Ensure a stable proxy connection.
3. Use more professional proxy tools.
4. Switch networks.
5. Try changing `DNS` servers.
6. If the issue is related to the `httpx` library version, try downgrading `httpx`.
7. If using tools like `Postman` or `curl` can access the API but the project times out, see item `6`.
:::

## _ssl.c:975 The handshake operation timed out

This indicates an `SSL` handshake timeout, often caused by unstable network connections or high latency.

Non-project issue, requires investigation.

::: details :link: Solution
1. Ensure stable network connection and low latency.
2. Check server status for responsiveness.
3. Verify firewall and proxy settings.
4. Adjust timeout settings.
:::

## tiktok 403 Forbidden

A `403 Forbidden` error when downloading TikTok videos occurs due to the `device_Id`being banned.

Device IDs are tied to `cookies`, and a banned device ID results in invalid cookies.

::: details :link: Solution
1. Regenerate the `device_Id`.
2. Replace the old `device_Id` in the config file with the new one.
3. Incrementally update the `cookie` values in the config file, rather than overwriting them.
4. Retry the download command.
:::
**Reference Links:**
- https://f2.wiki/guide/apps/tiktok/overview#%E7%94%9F%E6%88%90deviceid-%F0%9F%9F%A2
- https://github.com/Johnserf-Seed/f2/issues/79
- https://github.com/Johnserf-Seed/f2/issues/154

## TypeError: object of type 'NoneType' has no len()

You may see errors like this in the terminal:

```shell
Due to API updates, some fields failed:
Field weibo_read_count: object of type 'NoneType' has no len()
Field weibo_topic_title: object of type 'NoneType' has no len()
```

This occurs when the API field has changed and no longer exists or is different.

::: details :link: Please report the issue in the Issue tracker with the following information:
1. Debug logs (`f2 -d DEBUG [app_name]`):
    - Complete error message and context.
2. A description of the problematic fields:
    - Clearly indicate which fields are problematic and may need updating.
3. Simplified response data structure (optional):
    - Provide the approximate location of the fields in the API response.

Once feedback is received, the issue will be addressed in the next version, or you can submit a PR.
:::

## twitter 403 Forbidden

A `403 Forbidden` error when downloading Twitter posts is caused by an expired `cookie` or `X-Csrf-Token`.

::: details :link: Solution
1. Regenerate the `cookie` and `X-Csrf-Token`.
2. Update the `cookie` and `X-Csrf-Token` in the config files.
3. Retry the download command.

The `X-Csrf-Token` is in the `F2 config file (conf.yaml)`, while the cookie is in the app's main or custom config files.
:::

## Installing build dependencies error

When installing dependencies, you may encounter an error like this:
```shell
  × pip subprocess to install build dependencies did not run successfully.
  │ exit code: 1
      Looking in indexes: https://xxxx
      ERROR: Could not find a version that satisfies the requirement hatchling (from versions: none)
      ERROR: No matching distribution found for hatchling
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
```

This error occurs because `pip` cannot find the build dependencies.

::: details :link: Solution
1. Switch to the official PyPI source:

```shell
pip config unset global.index-url
```
2. Reinstall the project:

```shell
pip install f2
```
or

```shell
pip install -e .
```
:::

## Proxy Connection Failed

When using a proxy and encountering connection failures, check the following issues:

::: details :link: Solution
1. **Correct proxy type**: Ensure you have selected the correct proxy type (http/https/socks4/socks5)
2. **Proxy address and port**: Verify that the proxy server address and port are correct
3. **Authentication credentials**: If the proxy requires authentication, ensure the username and password are correct
4. **Network connectivity**: Test whether the proxy server can be accessed normally
5. **Firewall settings**: Check if the firewall is blocking the proxy connection

**Test proxy connection:**
```bash
# Test SOCKS5 proxy with curl
curl --socks5 127.0.0.1:1080 https://httpbin.org/ip

# Test HTTP proxy with curl
curl --proxy http://127.0.0.1:8080 https://httpbin.org/ip
```

**Troubleshooting steps:**
1. Verify proxy server is running and accessible
2. Check if proxy requires authentication
3. Test proxy with other tools (curl, browser)
4. Ensure no firewall blocking the connection
5. Try different proxy servers or types
6. Check proxy logs for error messages
:::
