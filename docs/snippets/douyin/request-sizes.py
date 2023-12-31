from f2.apps.douyin.utils import get_request_sizes

if __name__ == "__main__":
    print(get_request_sizes(10, 108))
    # [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 8]
    print(get_request_sizes(4, 75))
    # [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3]
