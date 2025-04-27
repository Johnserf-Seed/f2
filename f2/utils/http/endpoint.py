# path: f2/utils/http/endpoint.py


class BaseEndpointManager:
    @classmethod
    def model_2_endpoint(cls, base_endpoint: str, params: dict) -> str:
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        separator = "&" if "?" in base_endpoint else "?"
        return f"{base_endpoint}{separator}{param_str}"
