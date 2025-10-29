import requests
from config import SAFEW_API_URL, BOT_TOKEN
from utils.logger import get_logger

logger = get_logger(__name__)

class SafewApiClient:
    def __init__(self):
        self.base_url = f"{SAFEW_API_URL}/bot{BOT_TOKEN}"

    def get_chat_info(self, chat_id):
        """获取频道信息"""
        params = {"chat_id": chat_id}
        return self._request("getChat", params)

    def get_channel_messages(self, offset=0, limit=100, allowed_updates=None):
        """获取频道消息（分页）"""
        params = {            
            "offset": offset,
            "limit": limit            
        }
        # 处理可选的更新类型过滤
        if allowed_updates:
            params["allowed_updates"] = allowed_updates        

        return self._request("getUpdates", params)

    def get_file_info(self, file_id):
        """获取文件信息（包含下载链接）"""
        params = {"file_id": file_id}
        return self._request("getFile", params)

    def get_file_download_url(self, file_path):
        """生成文件下载URL"""
        return f"{SAFEW_API_URL}/file/bot{BOT_TOKEN}/{file_path}"

    def _request(self, method, params=None):
        """通用请求方法"""
        try:
            url = f"{self.base_url}/{method}"
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get("ok"):
                return result["result"]
            logger.error(f"API错误 [{method}]: {result.get('description')}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败 [{method}]: {str(e)}")
            return None
def get_file(self, file_id):
    """获取文件下载链接"""
    params = {"file_id": file_id}
    response = requests.get(f"{self.base_url}/getFile", params=params)
    response.raise_for_status()
    result = response.json()
    if result["ok"]:
        return result["result"]
    raise Exception(f"API Error: {result['description']}")
