import asyncio
from f2.apps.douyin.handler import handle_sso_login

if __name__ == '__main__':
    asyncio.run(handle_sso_login())