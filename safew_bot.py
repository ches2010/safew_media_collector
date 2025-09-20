import requests
import json
from typing import Optional, List, Dict, Any, Union

class SafeWBotAPI:
    """
    SafeW Bot API Python 客户端库。
    用于与 SafeW Bot API 进行交互。
    """

    def __init__(self, token: str):
        """
        初始化 SafeWBotAPI 实例。

        :param token: 你的 bot token。
        """
        self.token = token
        self.base_url = f"https://api.safew.org/bot{self.token}"

    def _make_request(self, method: str, data: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        向 SafeW Bot API 发送请求。

        :param method: API 方法名 (e.g., 'getMe', 'sendMessage').
        :param data: 要发送的数据 (键值对).
        :param files: 要上传的文件 (用于 sendPhoto, sendDocument 等).
        :return: API 响应的 JSON 对象。
        :raises Exception: 如果请求失败或 API 返回错误。
        """
        url = f"{self.base_url}/{method}"
        try:
            if files:
                # 对于文件上传，使用 POST 和 multipart/form-data
                response = requests.post(url, data=data, files=files)
            else:
                # 尝试使用 POST，如果失败则使用 GET (如 getMe)
                # 根据文档，推荐使用 POST 或 JSON，这里优先使用 JSON payload 的 POST
                response = requests.post(url, json=data)
                # 如果是 GET-only 方法（如 getMe, getUpdates），服务器可能不接受 JSON body
                # 在这种情况下，可以将参数放在 URL query string 中并使用 GET
                if response.status_code == 400 or response.status_code == 405:
                     # 回退到 GET 请求，参数放在 URL 查询字符串中
                     response = requests.get(url, params=data)
        except requests.RequestException as e:
            raise Exception(f"网络请求错误: {e}")

        try:
            result = response.json()
        except json.JSONDecodeError:
            raise Exception(f"无法解析 API 响应为 JSON: {response.text}")

        if not result.get('ok'):
            raise Exception(f"API 调用失败: {result.get('description', '未知错误')}, 错误码: {result.get('error_code')}")

        return result

    def get_me(self) -> Dict[str, Any]:
        """
        获取 bot 的基本信息。

        :return: 包含 bot 信息的字典。
        """
        return self._make_request('getMe')

    def get_updates(self, offset: Optional[int] = None, limit: Optional[int] = None,
                    allowed_updates: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        获取 bot 收到的更新（消息等）。

        :param offset: 要获取的第一个更新的标识符。
        :param limit: 要获取的更新数量限制 (1-100)。
        :param allowed_updates: 指定要接收的更新类型列表。
        :return: 更新对象列表。
        """
        data = {}
        if offset is not None:
            data['offset'] = offset
        if limit is not None:
            data['limit'] = limit
        if allowed_updates is not None:
            data['allowed_updates'] = json.dumps(allowed_updates)
        response = self._make_request('getUpdates', data)
        return response.get('result', [])

    def send_message(self, chat_id: Union[int, str], text: str,
                     parse_mode: Optional[str] = None, disable_notification: Optional[bool] = None,
                     protect_content: Optional[bool] = None, reply_parameters: Optional[Dict[str, Any]] = None,
                     reply_markup: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        发送文本消息。

        :param chat_id: 目标聊天的唯一标识符或频道用户名。
        :param text: 消息文本。
        :param parse_mode: 实体解析模式 ('Markdown', 'MarkdownV2', 'HTML')。
        :param disable_notification: 是否静默发送。
        :param protect_content: 是否保护内容不被转发和保存。
        :param reply_parameters: 回复消息的参数。
        :param reply_markup: 附加接口选项（如内联键盘）。
        :return: 已发送消息对象。
        """
        data = {'chat_id': chat_id, 'text': text}
        if parse_mode is not None:
            data['parse_mode'] = parse_mode
        if disable_notification is not None:
            data['disable_notification'] = disable_notification
        if protect_content is not None:
            data['protect_content'] = protect_content
        if reply_parameters is not None:
            data['reply_parameters'] = json.dumps(reply_parameters)
        if reply_markup is not None:
            data['reply_markup'] = json.dumps(reply_markup)
        response = self._make_request('sendMessage', data)
        return response.get('result')

    def send_photo(self, chat_id: Union[int, str], photo: str, # 这里简化处理，photo 传 file_id 或 URL
                   caption: Optional[str] = None, parse_mode: Optional[str] = None,
                   disable_notification: Optional[bool] = None, protect_content: Optional[bool] = None,
                   reply_parameters: Optional[Dict[str, Any]] = None, reply_markup: Optional[Dict[str, Any]] = None):
        """
        发送图片。

        :param chat_id: 目标聊天的唯一标识符或频道用户名。
        :param photo: 图片的 file_id、URL 或文件路径。
        :param caption: 图片说明。
        :param parse_mode: 说明文字解析模式。
        :param disable_notification: 是否静默发送。
        :param protect_content: 是否保护内容不被转发和保存。
        :param reply_parameters: 回复消息的参数。
        :param reply_markup: 附加接口选项。
        :return: 已发送消息对象。
        """
        data = {'chat_id': chat_id, 'photo': photo}
        if caption is not None:
            data['caption'] = caption
        if parse_mode is not None:
            data['parse_mode'] = parse_mode
        if disable_notification is not None:
            data['disable_notification'] = disable_notification
        if protect_content is not None:
            data['protect_content'] = protect_content
        if reply_parameters is not None:
            data['reply_parameters'] = json.dumps(reply_parameters)
        if reply_markup is not None:
            data['reply_markup'] = json.dumps(reply_markup)
        # 注意：如果 photo 是文件路径，需要使用 multipart/form-data 上传
        # 此简化版本假设 photo 是 file_id 或 URL
        response = self._make_request('sendPhoto', data)
        return response.get('result')

    def send_document(self, chat_id: Union[int, str], document: str, # 这里简化处理，document 传 file_id 或 URL
                      caption: Optional[str] = None, parse_mode: Optional[str] = None,
                      disable_notification: Optional[bool] = None, protect_content: Optional[bool] = None,
                      reply_parameters: Optional[Dict[str, Any]] = None, reply_markup: Optional[Dict[str, Any]] = None):
        """
        发送文档。

        :param chat_id: 目标聊天的唯一标识符或频道用户名。
        :param document: 文档的 file_id、URL 或文件路径。
        :param caption: 文档说明。
        :param parse_mode: 说明文字解析模式。
        :param disable_notification: 是否静默发送。
        :param protect_content: 是否保护内容不被转发和保存。
        :param reply_parameters: 回复消息的参数。
        :param reply_markup: 附加接口选项。
        :return: 已发送消息对象。
        """
        data = {'chat_id': chat_id, 'document': document}
        if caption is not None:
            data['caption'] = caption
        if parse_mode is not None:
            data['parse_mode'] = parse_mode
        if disable_notification is not None:
            data['disable_notification'] = disable_notification
        if protect_content is not None:
            data['protect_content'] = protect_content
        if reply_parameters is not None:
            data['reply_parameters'] = json.dumps(reply_parameters)
        if reply_markup is not None:
            data['reply_markup'] = json.dumps(reply_markup)
        # 注意：如果 document 是文件路径，需要使用 multipart/form-data 上传
        # 此简化版本假设 document 是 file_id 或 URL
        response = self._make_request('sendDocument', data)
        return response.get('result')

    def forward_message(self, chat_id: Union[int, str], from_chat_id: Union[int, str],
                        message_id: int, disable_notification: Optional[bool] = None,
                        protect_content: Optional[bool] = None) -> Dict[str, Any]:
        """
        转发消息。

        :param chat_id: 目标聊天的唯一标识符或频道用户名。
        :param from_chat_id: 源聊天的唯一标识符或频道用户名。
        :param message_id: 要转发的消息 ID。
        :param disable_notification: 是否静默转发。
        :param protect_content: 是否保护内容不被转发和保存。
        :return: 已转发消息对象。
        """
        data = {
            'chat_id': chat_id,
            'from_chat_id': from_chat_id,
            'message_id': message_id
        }
        if disable_notification is not None:
            data['disable_notification'] = disable_notification
        if protect_content is not None:
            data['protect_content'] = protect_content
        response = self._make_request('forwardMessage', data)
        return response.get('result')

    def edit_message_text(self, text: str,
                          chat_id: Optional[Union[int, str]] = None, message_id: Optional[int] = None,
                          inline_message_id: Optional[str] = None, parse_mode: Optional[str] = None,
                          reply_markup: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], bool]:
        """
        编辑文本消息。

        :param text: 新的文本。
        :param chat_id: 目标聊天的唯一标识符或频道用户名 (如果不是 inline_message)。
        :param message_id: 要编辑的消息 ID (如果不是 inline_message)。
        :param inline_message_id: 要编辑的内联消息 ID。
        :param parse_mode: 实体解析模式。
        :param reply_markup: 新的内联键盘。
        :return: 编辑后的消息对象或 True (对于内联消息)。
        """
        data = {'text': text}
        if chat_id is not None:
            data['chat_id'] = chat_id
        if message_id is not None:
            data['message_id'] = message_id
        if inline_message_id is not None:
            data['inline_message_id'] = inline_message_id
        if parse_mode is not None:
            data['parse_mode'] = parse_mode
        if reply_markup is not None:
            data['reply_markup'] = json.dumps(reply_markup)

        response = self._make_request('editMessageText', data)
        # 根据文档，如果是内联消息，返回 True；否则返回编辑后的消息对象
        return response.get('result')

    def delete_message(self, chat_id: Union[int, str], message_id: int) -> bool:
        """
        删除一条消息。

        :param chat_id: 目标聊天的唯一标识符或频道用户名。
        :param message_id: 要删除的消息 ID。
        :return: 成功时返回 True。
        """
        data = {'chat_id': chat_id, 'message_id': message_id}
        response = self._make_request('deleteMessage', data)
        return response.get('result', False)

    def get_chat(self, chat_id: Union[int, str]) -> Dict[str, Any]:
        """
        获取聊天信息。

        :param chat_id: 聊天的唯一标识符或用户名。
        :return: 聊天信息对象。
        """
        data = {'chat_id': chat_id}
        response = self._make_request('getChat', data)
        return response.get('result')

    def leave_chat(self, chat_id: Union[int, str]) -> bool:
        """
        让 bot 离开一个群组、超级群组或频道。

        :param chat_id: 聊天的唯一标识符或用户名。
        :return: 成功时返回 True。
        """
        data = {'chat_id': chat_id}
        response = self._make_request('leaveChat', data)
        return response.get('result', False)

    def get_chat_member_count(self, chat_id: Union[int, str]) -> int:
        """
        获取聊天成员数量。

        :param chat_id: 聊天的唯一标识符或用户名。
        :return: 成员数量。
        """
        data = {'chat_id': chat_id}
        response = self._make_request('getChatMemberCount', data)
        return response.get('result')

    def ban_chat_member(self, chat_id: Union[int, str], user_id: int,
                        until_date: Optional[int] = None, revoke_messages: Optional[bool] = None) -> bool:
        """
        在群组、超级群组或频道中封禁用户。

        :param chat_id: 聊天的唯一标识符或用户名。
        :param user_id: 要封禁的用户 ID。
        :param until_date: 封禁解除的 Unix 时间戳。
        :param revoke_messages: 是否删除该用户的所有消息。
        :return: 成功时返回 True。
        """
        data = {'chat_id': chat_id, 'user_id': user_id}
        if until_date is not None:
            data['until_date'] = until_date
        if revoke_messages is not None:
            data['revoke_messages'] = revoke_messages
        response = self._make_request('banChatMember', data)
        return response.get('result', False)

    def set_webhook(self, url: str, certificate: Optional[str] = None,
                    ip_address: Optional[str] = None, max_connections: Optional[int] = None,
                    allowed_updates: Optional[List[str]] = None, drop_pending_updates: Optional[bool] = None,
                    secret_token: Optional[str] = None) -> bool:
        """
        设置 webhook。

        :param url: 接收更新的 HTTPS URL。
        :param certificate: 公钥证书文件路径 (如果使用自签名证书)。
        :param ip_address: 固定 IP 地址。
        :param max_connections: 最大连接数 (1-100)。
        :param allowed_updates: 允许的更新类型列表。
        :param drop_pending_updates: 是否丢弃待处理的更新。
        :param secret_token: Secret token。
        :return: 成功时返回 True。
        """
        data = {'url': url}
        files = None
        if certificate is not None:
            # 如果 certificate 是文件路径，则需要上传文件
            files = {'certificate': open(certificate, 'rb')}
        if ip_address is not None:
            data['ip_address'] = ip_address
        if max_connections is not None:
            data['max_connections'] = max_connections
        if allowed_updates is not None:
            data['allowed_updates'] = json.dumps(allowed_updates)
        if drop_pending_updates is not None:
            data['drop_pending_updates'] = drop_pending_updates
        if secret_token is not None:
            data['secret_token'] = secret_token

        response = self._make_request('setWebhook', data, files)
        # 关闭文件
        if files:
            files['certificate'].close()
        return response.get('result', False)

    def delete_webhook(self, drop_pending_updates: Optional[bool] = None) -> bool:
        """
        删除 webhook。

        :param drop_pending_updates: 是否丢弃待处理的更新。
        :return: 成功时返回 True。
        """
        data = {}
        if drop_pending_updates is not None:
            data['drop_pending_updates'] = drop_pending_updates
        response = self._make_request('deleteWebhook', data)
        return response.get('result', False)

    def get_webhook_info(self) -> Dict[str, Any]:
        """
        获取 webhook 信息。

        :return: WebhookInfo 对象。
        """
        response = self._make_request('getWebhookInfo')
        return response.get('result')

# --- 使用示例 ---
if __name__ == '__main__':
    # 请替换为你的实际 bot token
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    bot = SafeWBotAPI(BOT_TOKEN)

    try:
        # 示例 1: 获取 bot 信息
        print("1. 获取 bot 信息:")
        me = bot.get_me()
        print(json.dumps(me, indent=2))

        # 示例 2: 获取更新
        print("\n2. 获取更新:")
        updates = bot.get_updates(limit=5)
        print(f"收到 {len(updates)} 条更新")
        for update in updates:
             print(json.dumps(update, indent=2))

        # 示例 3: 发送消息 (需要一个有效的 chat_id)
        # CHAT_ID = "@your_channel_username_or_chat_id"
        # print("\n3. 发送消息:")
        # sent_message = bot.send_message(chat_id=CHAT_ID, text="Hello from SafeW Bot API Python library!")
        # print(f"消息已发送，ID: {sent_message['message_id']}")

    except Exception as e:
        print(f"发生错误: {e}")




