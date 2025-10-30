# SafeW 机器人 API 文档

## 简介

从核心功能来说，你可以将 SafeW 机器人 API 视为一种能对你的查询提供 JSON 编码响应的软件。

而机器人本质上是一种程序、软件或脚本，它通过 HTTPS 请求调用 API 并等待响应。你可以发起多种类型的请求，也可以使用和接收多种不同的对象作为响应。

由于你的你的浏览器浏览器**能够发送 HTTPS 请求，因此你可以用它快速试用该 API。获取令牌后，尝试将以下字符串粘贴到浏览器中：

```
https://api.safew.org/bot<你的机器人令牌>/getMe
```

理论上，你可以通过浏览器或 curl 等其他定制工具，通过类似这样的**基本请求**与 API 交互。虽然对于像上述示例这样的简单请求，这种方式可能可行，但对于大型应用来说并不实用，而且扩展性不佳。

**获取你的机器人令牌**  
在此语境中，**令牌**是一串用于在机器人 API 上验证你的机器人（而非你的账户）的字符串。每个机器人都有唯一的令牌，该令牌可随时通过 @BotFather 撤销。

获取令牌的操作很简单，只需联系 @BotFather，发送[<mark style="color:red;">`/newbot`</mark>](#user-content-fn-1)[^1]命令，然后按照步骤操作，直至获得新令牌。你可以在此处查看详细的步骤指南。

你的令牌看起来会类似这样：

```
4839574812:AAFD39kkdpWt3ywyRZergyOLMaJhac60qc
```

## getMe

机器人 API 是一个基于 HTTP 的接口，专为热衷于为 SafeW 开发机器人的开发者打造。要了解如何创建和设置机器人，请参考我们的《机器人简介》和《机器人常见问题》。

### getMe

#### 机器人授权

每个机器人在创建时都会获得一个唯一的认证令牌。令牌看起来类似<mark style="color:red;">`123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`</mark>，但在本文档中我们简称为**\<token>**。你可以在本文档中了解获取令牌和生成新令牌的方法。

#### 发起请求

所有对 SafeW 机器人 API 的查询都必须通过 HTTPS 进行，且格式如下：`https://api.safew.org/bot<token>/方法名称`。例如：

{% hint style="info" %}
<https://api.safew.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/getMe>
{% endhint %}

我们支持**GET**和**POST**两种 HTTP 方法。在机器人 API 请求中，我们支持四种传递参数的方式：

* URL 查询字符串
* application/x-www-form-urlencoded
* application/json（文件上传除外）
* multipart/form-data（用于文件上传）

响应包含一个 JSON 对象，该对象始终有一个布尔字段“ok”，可能还有一个可选的字符串字段“description”，用于对结果进行人工可读的描述。如果“ok”为*True*，则请求成功，查询结果可在“result”字段中找到。如果请求失败，“ok”为 false，错误信息会在“description”中说明。响应中还会返回一个整数类型的“error_code”字段，但该字段的内容未来可能会有所变化。某些错误可能还有一个可选的“parameters”字段，其类型为 ResponseParameters，有助于自动处理错误。

* 机器人 API 中的所有方法均不区分大小写。
* 所有查询都必须使用 UTF-8 编码。

## getUpdates

使用此方法通过长轮询（wiki）接收 incoming 更新。返回 Update 对象的数组。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| offset | Integer | 可选 | 要返回的第一个更新的标识符。该标识符必须比之前接收的所有更新的标识符中的最大值大 1。默认情况下，将返回从最早未确认的更新开始的更新。一旦调用 getUpdates 时使用的 offset 高于某个更新的 update_id，该更新即被视为已确认。可以指定负的 offset 来从更新队列的末尾开始获取 -offset 个更新。所有之前的更新都将被遗忘。 |
| limit | Integer | 可选 | 限制要获取的更新数量。接受 1-100 之间的值。默认值为 100。 |
| allowed_updates | Array of String | 可选 | 一个 JSON 序列化的列表，包含你希望机器人接收的更新类型。例如，指定 ["message", "edited_channel_post", "callback_query"] 仅接收这些类型的更新。查看 Update 可获取所有可用更新类型的完整列表。指定空列表将接收除 chat_member、message_reaction 和 message_reaction_count 之外的所有更新类型（默认值）。如果未指定，将使用之前的设置。请注意，此参数不会影响在调用 getUpdates 之前创建的更新，因此在短时间内可能会收到不需要的更新。 |

{% hint style="success" %}
注意事项

1. 如果已设置 outgoing webhook，此方法将无法使用。
2. 为避免收到重复更新，每次服务器响应后都要重新计算 offset。
{% endhint %}

## sendMessage

使用此方法发送文本消息。成功时，返回发送的 Message。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| business_connection_id | String | 可选 | 代表其发送消息的业务连接的唯一标识符 |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为 @channelusername） |
| message_thread_id | Integer | 可选 | 论坛的目标消息线程（主题）的唯一标识符；仅适用于论坛超级群组 |
| text | String | 是 | 要发送的消息文本，解析实体后为 1-4096 个字符 |
| parse_mode | String | 可选 | 消息文本中实体的解析模式。详情请查看格式选项。 |
| entities | Array of MessageEntity | 可选 | 消息文本中出现的特殊实体的 JSON 序列化列表，可指定此参数代替 parse_mode |
| link_preview_options | LinkPreviewOptions | 可选 | 消息的链接预览生成选项 |
| disable_notification | Boolean | 可选 | 静默发送消息。用户将收到无声音的通知。 |
| protect_content | Boolean | 可选 | 保护发送消息的内容不被转发和保存 |
| allow_paid_broadcast | Boolean | 可选 | 传递 True 以允许每秒最多 1000 条消息，忽略广播限制，每条消息收费 0.1 Telegram Stars。相关 Stars 将从机器人的余额中扣除 |
| message_effect_id | String | 可选 | 要添加到消息的消息效果的唯一标识符；仅适用于私人聊天 |
| reply_parameters | ReplyParameters | 可选 | 要回复的消息的描述 |
| reply_markup | InlineKeyboardMarkup 或 ReplyKeyboardMarkup 或 ReplyKeyboardRemove 或 ForceReply | 可选 | 附加界面选项。用于内联键盘、自定义回复键盘、移除回复键盘的指令或强制用户回复的 JSON 序列化对象 |

## sendPhoto

使用此方法发送照片。成功时，返回发送的 Message。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| business_connection_id | String | 可选 | 代表其发送消息的业务连接的唯一标识符 |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为<mark style="color:red;">@channelusername</mark>） |
| message_thread_id | Integer | 可选 | 论坛的目标消息线程（主题）的唯一标识符；仅适用于论坛超级群组 |
| photo | InputFile 或 String | 是 | 要发送的照片。传递 file_id 字符串以发送 Telegram 服务器上已存在的照片（推荐），传递 HTTP URL 字符串让 Telegram 从互联网获取照片，或使用 multipart/form-data 上传新照片。照片大小不得超过 10 MB。照片的宽度和高度总和不得超过 10000。宽高比不得超过 20。 |
| caption | String | 可选 | 照片说明（通过 file_id 重发照片时也可使用），解析实体后为 0-1024 个字符 |
| parse_mode | String | 可选 | 照片说明中实体的解析模式。详情请查看格式选项。 |
| caption_entities | Array of MessageEntity | 可选 | 说明中出现的特殊实体的 JSON 序列化列表，可指定此参数代替 parse_mode |
| show_caption_above_media | Boolean | 可选 | 传递 True，如果说明必须显示在消息媒体上方 |
| has_spoiler | Boolean | 可选 | 如果照片需要用 spoiler 动画覆盖，传递 True |
| disable_notification | Boolean | 可选 | 静默发送消息。用户将收到无声音的通知。 |
| protect_content | String | 可选 | 保护发送消息的内容不被转发和保存 |
| allow_paid_broadcast | Boolean | 可选 | 传递 True 以允许每秒最多 1000 条消息，忽略广播限制，每条消息收费 0.1 Telegram Stars。相关 Stars 将从机器人的余额中扣除 |
| message_effect_id | String | 可选 | 要添加到消息的消息效果的唯一标识符；仅适用于私人聊天 |
| reply_parameters | ReplyParameters | 可选 | 要回复的消息的描述 |
| reply_markup | InlineKeyboardMarkup 或 ReplyKeyboardMarkup 或 ReplyKeyboardRemove 或 ForceReply | 可选 | 附加界面选项。用于内联键盘、自定义回复键盘、移除回复键盘的指令或强制用户回复的 JSON 序列化对象 |

## sendVideo

使用此方法发送视频文件，SafeW 客户端支持 MPEG4 视频（其他格式可能作为 Document 发送）。成功时，返回发送的 Message。机器人目前可以发送最大 50 MB 的视频文件，此限制未来可能会更改。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| business_connection_id | String | 可选 | 代表其发送消息的业务连接的唯一标识符 |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为<mark style="color:red;">@channelusername</mark>） |
| message_thread_id | Integer | 可选 | 论坛的目标消息线程（主题）的唯一标识符；仅适用于论坛超级群组 |
| video | InputFile 或 String | 是 | 要发送的视频。传递 file_id 字符串以发送 Telegram 服务器上已存在的视频（推荐），传递 HTTP URL 字符串让 Telegram 从互联网获取视频，或使用 multipart/form-data 上传新视频。 |
| duration | String | 可选 | 发送的视频的时长（秒） |
| width | Integer | 可选 | 视频宽度 |
| height | Integer | 可选 | 视频高度 |
| thumbnail | InputFile 或 String | 可选 | 发送文件的缩略图；如果服务器端支持文件的缩略图生成，则可忽略。缩略图应为 JPEG 格式，大小小于 200 kB。缩略图的宽度和高度不应超过 320。如果文件不是使用 multipart/form-data 上传的，则忽略此参数。缩略图不能重复使用，只能作为新文件上传，因此如果缩略图是使用 multipart/form-data 在<file_attach_name>下上传的，你可以传递“attach://<file_attach_name>”。 |
| caption | String | 可选 | 视频说明（通过 file_id 重发视频时也可使用），解析实体后为 0-1024 个字符 |
| parse_mode | Boolean | 可选 | 视频说明中实体的解析模式。详情请查看格式选项。 |
| caption_entities | Array of MessageEntity | 可选 | 说明中出现的特殊实体的 JSON 序列化列表，可指定此参数代替 parse_mode |
| show_caption_above_media | Boolean | 可选 | 传递 True，如果说明必须显示在消息媒体上方 |
| has_spoiler | Boolean | 可选 | 如果视频需要用 spoiler 动画覆盖，传递 True |
| supports_streaming | Boolean | 可选 | 如果上传的视频适合流式传输，传递 True |
| disable_notification | Boolean | 可选 | 静默发送消息。用户将收到无声音的通知。 |
| protect_content | Boolean | 可选 | 保护发送消息的内容不被转发和保存 |
| allow_paid_broadcast | Boolean | 可选 | 传递 True 以允许每秒最多 1000 条消息，忽略广播限制，每条消息收费 0.1 Telegram Stars。相关 Stars 将从机器人的余额中扣除 |
| message_effect_id | String | 可选 | 要添加到消息的消息效果的唯一标识符；仅适用于私人聊天 |
| reply_parameters | ReplyParameters | 可选 | 要回复的消息的描述 |
| reply_markup | InlineKeyboardMarkup 或 ReplyKeyboardMarkup 或 ReplyKeyboardRemove 或 ForceReply | 可选 | 附加界面选项。用于内联键盘、自定义回复键盘、移除回复键盘的指令或强制用户回复的 JSON 序列化对象 |

## sendDocument

使用此方法发送通用文件。成功时，返回发送的 Message。机器人目前可以发送任何类型的最大 50 MB 的文件，此限制未来可能会更改。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| business_connection_id | String | 可选 | 代表其发送消息的业务连接的唯一标识符 |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为<mark style="color:red;">@channelusername</mark>） |
| message_thread_id | Integer | 可选 | 论坛的目标消息线程（主题）的唯一标识符；仅适用于论坛超级群组 |
| document | InputFile 或 String | 是 | 要发送的文件。传递 file_id 字符串以发送 Telegram 服务器上已存在的文件（推荐），传递 HTTP URL 字符串让 Telegram 从互联网获取文件，或使用 multipart/form-data 上传新文件。 |
| thumbnail | InputFile 或 String | 可选 | 发送文件的缩略图；如果服务器端支持文件的缩略图生成，则可忽略。缩略图应为 JPEG 格式，大小小于 200 kB。缩略图的宽度和高度不应超过 320。如果文件不是使用 multipart/form-data 上传的，则忽略此参数。缩略图不能重复使用，只能作为新文件上传，因此如果缩略图是使用 multipart/form-data 在<file_attach_name>下上传的，你可以传递“attach://<file_attach_name>”。 |
| caption | String | 可选 | 文档说明（通过 file_id 重发文档时也可使用），解析实体后为 0-1024 个字符 |
| parse_mode | String | 可选 | 文档说明中实体的解析模式。详情请查看格式选项。 |
| caption_entities | Array of MessageEntity | 可选 | 说明中出现的特殊实体的 JSON 序列化列表，可指定此参数代替 parse_mode |
| disable_content_type_detection | Boolean | 可选 | 禁用对使用 multipart/form-data 上传的文件的服务器端自动内容类型检测 |
| disable_notification | Boolean | 可选 | 静默发送消息。用户将收到无声音的通知。 |
| protect_content | Array of MessageEntity | 可选 | 保护发送消息的内容不被转发和保存 |
| allow_paid_broadcast | Boolean | 可选 | 传递 True 以允许每秒最多 1000 条消息，忽略广播限制，每条消息收费 0.1 Telegram Stars。相关 Stars 将从机器人的余额中扣除 |
| message_effect_id | Boolean | 可选 | 要添加到消息的消息效果的唯一标识符；仅适用于私人聊天 |
| reply_parameters | ReplyParameters | 可选 | 要回复的消息的描述 |
| reply_markup | InlineKeyboardMarkup 或 ReplyKeyboardMarkup 或 ReplyKeyboardRemove 或 ForceReply | 可选 | 附加界面选项。用于内联键盘、自定义回复键盘、移除回复键盘的指令或强制用户回复的 JSON 序列化对象 |

## forwardMessage

使用此方法转发任何类型的消息。服务消息和具有受保护内容的消息不能被转发。成功时，返回发送的 Message。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为<mark style="color:red;">@channelusername</mark>） |
| message_thread_id | Integer | 可选 | 论坛的目标消息线程（主题）的唯一标识符；仅适用于论坛超级群组 |
| from_chat_id | Integer 或 String | 是 | 原始消息发送所在聊天的唯一标识符（或格式为<mark style="color:red;">@channelusername</mark>的频道用户名） |
| disable_notification | Boolean | 可选 | 静默发送消息。用户将收到无声音的通知。 |
| protect_content | Boolean | 可选 | 保护转发消息的内容不被转发和保存 |
| message_id | Integer | 是 | from_chat_id 所指定聊天中的消息标识符 |

## editMessageText

使用此方法编辑文本和游戏消息。成功时，如果被编辑的消息不是内联消息，则返回被编辑的 Message，否则返回 True。请注意，不是由机器人发送且不包含内联键盘的业务消息只能在发送后 48 小时内编辑。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| business_connection_id | String | 可选 | 代表其发送要编辑的消息的业务连接的唯一标识符 |
| chat_id | Integer 或 String | 可选 | 如果未指定 inline_message_id，则为必需参数。目标聊天的唯一标识符或目标频道的用户名（格式为<mark style="color:red;">@channelusername</mark>） |
| message_id | Integer | 可选 | 如果未指定 inline_message_id，则为必需参数。要编辑的消息的标识符 |
| inline_message_id | String | 可选 | 如果未指定 chat_id 和 message_id，则为必需参数。内联消息的标识符 |
| text | String | 是 | 消息的新文本，解析实体后为 1-4096 个字符 |
| parse_mode | String | 可选 | 消息文本中实体的解析模式。详情请查看格式选项。 |
| entities | Array of MessageEntity | 可选 | 消息文本中出现的特殊实体的 JSON 序列化列表，可指定此参数代替 parse_mode |
| link_preview_options | LinkPreviewOptions | 可选 | 消息的链接预览生成选项 |
| reply_markup | InlineKeyboardMarkup | 可选 | 用于内联键盘的 JSON 序列化对象。 |

## deleteMessage

使用此方法删除消息，包括服务消息，但有以下限制：

- 消息只能在发送后不到 48 小时内删除。
- 关于超级群组、频道或论坛主题创建的服务消息不能删除。
- 私人聊天中的骰子消息只能在发送超过 24 小时后删除。
- 机器人可以删除私人聊天、群组和超级群组中的 outgoing 消息。
- 机器人可以删除私人聊天中的 incoming 消息。
- 被授予 can_post_messages 权限的机器人可以删除频道中的 outgoing 消息。
- 如果机器人是群组的管理员，它可以删除该群组中的任何消息。
- 如果机器人在超级群组或频道中具有 can_delete_messages 权限，它可以删除该群组或频道中的任何消息。

成功时返回 True。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为<mark style="color:red;">@channelusername</mark>） |
| message_id | Integer | 是 | 要删除的消息的标识符 |

## getChat

使用此方法获取有关聊天的最新信息。成功时返回 ChatFullInfo 对象。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标超级群组或频道的用户名（格式为<mark style="color:red;">@channelusername</mark>） |

## leaveChat

使用此方法让你的机器人离开群组、超级群组或频道。成功时返回 True。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标超级群组或频道的用户名（格式为<mark style="color:red;">@channelusername</mark>） |

## getChatMemberCount

使用此方法获取聊天中的成员数量。成功时返回 Int。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标超级群组或频道的用户名（格式为<mark style="color:red;">@channelusername</mark>） |

## banChatMember

使用此方法在群组、超级群组或频道中封禁用户。对于超级群组和频道，除非先解封，否则用户将无法通过邀请链接等方式自行返回聊天。机器人必须是聊天中的管理员才能执行此操作，并且必须具有适当的管理员权限。成功时返回 True。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标群组的唯一标识符或目标超级群组或频道的用户名（格式为<mark style="color:red;">@channelusername</mark>） |
| user_id | Integer | 是 | 目标用户的唯一标识符 |
| until_date | Integer | 可选 | 用户将被解封的日期；Unix 时间。如果用户被封禁超过 366 天或少于当前时间 30 秒，则视为永久封禁。仅适用于超级群组和频道。 |
| revoke_messages | Boolean | 可选 | 传递 True 以删除被移除用户在聊天中的所有消息。如果为 False，用户将能够看到在其被移除之前发送到群组的消息。对于超级群组和频道，此参数始终为 True。 |

## sendVoice

使用此方法发送音频文件，如果你希望 Telegram 客户端将该文件显示为可播放的语音消息。为此，你的音频必须是 .OGG 格式（采用 OPUS 编码）、.MP3 格式或 .M4A 格式（其他格式可能作为 Audio 或 Document 发送）。成功时，返回发送的 Message。机器人目前可以发送最大 50 MB 的语音消息，此限制未来可能会更改。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| business_connection_id | String | 可选 | 代表其发送消息的业务连接的唯一标识符 |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为<mark style="color:red;"><code>@channelusername</code></mark>） |
| message_thread_id | Integer | 可选 | 论坛的目标消息线程（主题）的唯一标识符；仅适用于论坛超级群组 |
| voice | InputFile 或 String | 是 | 要发送的音频文件。传递 file_id 字符串以发送 Telegram 服务器上已存在的文件（推荐），传递 HTTP URL 字符串让 Telegram 从互联网获取文件，或使用 multipart/form-data 上传新文件。 |
| caption | String | 可选 | 语音消息说明，解析实体后为 0-1024 个字符 |
| parse_mode | String | 可选 | 语音消息说明中实体的解析模式。详情请查看格式选项。 |
| caption_entities | Array of MessageEntity | 可选 | 说明中出现的特殊实体的 JSON 序列化列表，可指定此参数代替 parse_mode |
| duration | Integer | 可选 | 语音消息的时长（秒） |
| disable_notification | Boolean | 可选 | 静默发送消息。用户将收到无声音的通知。 |
| protect_content | Boolean | 可选 | 保护发送消息的内容不被转发和保存 |
| allow_paid_broadcast | Boolean | 可选 | 传递 True 以允许每秒最多 1000 条消息，忽略广播限制，每条消息收费 0.1 Telegram Stars。相关 Stars 将从机器人的余额中扣除 |
| message_effect_id | String | 可选 | 要添加到消息的消息效果的唯一标识符；仅适用于私人聊天 |
| reply_parameters | ReplyParameters | 可选 | 要回复的消息的描述 |
| reply_markup | InlineKeyboardMarkup 或 ReplyKeyboardMarkup 或 ReplyKeyboardRemove 或 ForceReply | 可选 | 附加界面选项。用于内联键盘、自定义回复键盘、移除回复键盘的指令或强制用户回复的 JSON 序列化对象 |

## sendMediaGroup

使用此方法发送一组照片、视频、文档或音频作为相册。文档和音频文件只能与相同类型的消息组成相册。成功时，返回已发送的 Messages 数组。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| business_connection_id | String | 可选 | 代表其发送消息的业务连接的唯一标识符 |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为<mark style="color:red;"><code>@channelusername</code></mark>） |
| message_thread_id | Integer | 可选 | 论坛的目标消息线程（主题）的唯一标识符；仅适用于论坛超级群组 |
| media | Array of InputMediaAudio, InputMediaDocument, InputMediaPhoto and InputMediaVideo | 是 | 描述要发送的消息的 JSON 序列化数组，必须包含 2-10 个项目 |
| disable_notification | Boolean | 可选 | 静默发送消息。用户将收到无声音的通知。 |
| protect_content | Boolean | 可选 | 保护发送消息的内容不被转发和保存 |
| allow_paid_broadcast | Boolean | 可选 | 传递 True 以允许每秒最多 1000 条消息，忽略广播限制，每条消息收费 0.1 Telegram Stars。相关 Stars 将从机器人的余额中扣除 |
| message_effect_id | String | 可选 | 要添加到消息的消息效果的唯一标识符；仅适用于私人聊天 |
| reply_parameters | ReplyParameters | 可选 | 要回复的消息的描述 |

## sendAudio

使用此方法发送音频文件，如果你希望 Telegram 客户端将它们显示在音乐播放器中。你的音频必须是 .MP3 或 .M4A 格式。成功时，返回发送的 Message。机器人目前可以发送最大 50 MB 的音频文件，此限制未来可能会更改。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| business_connection_id | String | 可选 | 代表其发送消息的业务连接的唯一标识符 |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为<code>@channelusername</code>） |
| message_thread_id | Integer | 可选 | 论坛的目标消息线程（主题）的唯一标识符；仅适用于论坛超级群组 |
| audio | <a href="https://core.telegram.org/bots/api#inputfile">InputFile</a> 或 String | 是 | 要发送的音频文件。传递 file_id 字符串以发送 Telegram 服务器上已存在的音频文件（推荐），传递 HTTP URL 字符串让 Telegram 从互联网获取音频文件，或使用 multipart/form-data 上传新文件。 |
| caption | String | 可选 | 音频说明，解析实体后为 0-1024 个字符 |
| parse_mode | String | 可选 | 音频说明中实体的解析模式。详情请查看格式选项。 |
| caption_entities | Array of MessageEntity | 可选 | 说明中出现的特殊实体的 JSON 序列化列表，可指定此参数代替 parse_mode |
| duration | Integer | 可选 | 音频的时长（秒） |
| performer | String | 可选 | 表演者 |
| title | String | 可选 | 曲目名称 |
| thumbnail | InputFile 或 String | 可选 | 发送文件的缩略图；如果服务器端支持文件的缩略图生成，则可忽略。缩略图应为 JPEG 格式，大小小于 200 kB。缩略图的宽度和高度不应超过 320。如果文件不是使用 multipart/form-data 上传的，则忽略此参数。缩略图不能重复使用，只能作为新文件上传，因此如果缩略图是使用 multipart/form-data 在<file_attach_name>下上传的，你可以传递“attach://<file_attach_name>”。 |
| disable_notification | Boolean | 可选 | 静默发送消息。用户将收到无声音的通知。 |
| protect_content | Boolean | 可选 | 保护发送消息的内容不被转发和保存 |
| allow_paid_broadcast | Boolean | 可选 | 传递 True 以允许每秒最多 1000 条消息，忽略广播限制，每条消息收费 0.1 Telegram Stars。相关 Stars 将从机器人的余额中扣除 |
| message_effect_id | String | 可选 | 要添加到消息的消息效果的唯一标识符；仅适用于私人聊天 |
| reply_parameters | ReplyParameters | 可选 | 要回复的消息的描述 |
| reply_markup | InlineKeyboardMarkup 或 ReplyKeyboardMarkup 或 ReplyKeyboardRemove 或 ForceReply | 可选 | 附加界面选项。用于内联键盘、自定义回复键盘、移除回复键盘的指令或强制用户回复的 JSON 序列化对象 |


## setWebhook（设置网络钩子）

使用此方法可以指定一个URL，并通过外向网络钩子接收传入的更新。每当机器人有更新时，系统会向指定URL发送一个包含JSON序列化的Update对象的HTTPS POST请求。如果请求失败（响应的HTTP状态码不是`2XY`），系统会重复请求，并在经过一定次数的尝试后放弃。成功时返回*True*。

如果希望确保网络钩子是由你设置的，可以在*secret_token*参数中指定秘密数据。如果指定了该参数，请求将包含一个头部信息“X-Telegram-Bot-Api-Secret-Token”，其内容为该秘密令牌。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| url | String | 是 | 用于接收更新的HTTPS URL。使用空字符串可移除网络钩子集成 |
| certificate | InputFile | 可选 | 上传你的公钥证书，以便检查所使用的根证书。详情请参见自签名指南。 |
| ip_address | String | 可选 | 用于发送网络钩子请求的固定IP地址，替代通过DNS解析的IP地址 |
| max_connections | Integer | 可选 | 用于更新传递的网络钩子的最大并发HTTPS连接数，范围1-100。默认值为*40*。使用较低值可限制机器人服务器的负载，较高值可提高机器人的吞吐量。 |
| allowed_updates | Array of String | 可选 | 一个JSON序列化的列表，包含你希望机器人接收的更新类型。例如，指定`["message", "edited_channel_post", "callback_query"]`仅接收这些类型的更新。查看Update可获取所有可用更新类型的完整列表。指定空列表将接收除*chat_member*、*message_reaction*和*message_reaction_count*之外的所有更新类型（默认值）。如果未指定，将使用之前的设置。<br>请注意，此参数不影响调用setWebhook之前创建的更新，因此短期内可能会收到不需要的更新。 |
| drop_pending_updates | Boolean | 可选 | 传递*True*以丢弃所有待处理的更新 |
| secret_token | String | 可选 | 一个秘密令牌，将在每个网络钩子请求的头部“X-Telegram-Bot-Api-Secret-Token”中发送，长度1-256个字符。仅允许使用字符`A-Z`、`a-z`、`0-9`、`_`和`-`。该头部有助于确保请求来自你设置的网络钩子。 |

> **注意**
> 1. 只要设置了外向网络钩子，就无法使用getUpdates接收更新。
> 2. 要使用自签名证书，需要通过*certificate*参数上传你的公钥证书。请以InputFile形式上传，发送字符串将无效。
> 3. 目前网络钩子支持的端口：**443、80、88、8443**。
>
> 如果在设置网络钩子时遇到任何问题，请查看这份出色的网络钩子指南。


## deleteWebhook（删除网络钩子）

使用此方法可以移除网络钩子集成，如果你决定切换回getUpdates。成功时返回*True*。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| drop_pending_updates | Boolean | 可选 | 传递*True*以丢弃所有待处理的更新 |


## getWebhookInfo（获取网络钩子信息）

使用此方法可以获取当前网络钩子的状态。无需参数。成功时返回一个WebhookInfo对象。如果机器人正在使用getUpdates，将返回一个*url*字段为空的对象。

**WebhookInfo（网络钩子信息）**

描述网络钩子的当前状态。

| 参数 | 类型 | 描述 |
| ---- | ---- | ---- |
| url | String | 网络钩子URL，如果未设置网络钩子则可能为空 |
| has_custom_certificate | Boolean | 如果为网络钩子证书检查提供了自定义证书，则为*True* |
| pending_update_count | Integer | 等待传递的更新数量 |
| ip_address | String | 可选。当前使用的网络钩子IP地址 |
| last_error_date | Integer | 可选。最近一次尝试通过网络钩子传递更新时发生错误的Unix时间 |
| last_error_message | String | 可选。最近一次尝试通过网络钩子传递更新时发生错误的人类可读格式的错误消息 |
| last_synchronization_error_date | Integer | 可选。最近一次尝试与Telegram数据中心同步可用更新时发生错误的Unix时间 |
| max_connections | Integer | 可选。用于更新传递的网络钩子的最大并发HTTPS连接数 |
| allowed_updates | Array of String | 可选。机器人订阅的更新类型列表。默认值为除*chat_member*之外的所有更新类型 |


## deleteMessages（批量删除消息）

使用此方法可以同时删除多条消息。如果某些指定的消息无法找到，将被跳过。成功时返回*True*。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为`@channelusername`） |
| message_ids | Array of Integer | 是 | 一个JSON序列化的列表，包含1-100个要删除的消息的标识符。参见deleteMessage了解关于哪些消息可以被删除的限制 |


## editMessageReplyMarkup（编辑消息的回复标记）

使用此方法仅编辑消息的回复标记。成功时，如果被编辑的消息不是内联消息，则返回被编辑的Message，否则返回*True*。请注意，不是由机器人发送且不包含内联键盘的业务消息只能在发送后**48小时**内编辑。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| business_connection_id | String | 可选 | 代表其发送要编辑的消息的业务连接的唯一标识符 |
| chat_id | Integer 或 String | 可选 | 如果未指定*inline_message_id*，则为必需参数。目标聊天的唯一标识符或目标频道的用户名（格式为`@channelusername`） |
| message_id | Integer | 可选 | 如果未指定*inline_message_id*，则为必需参数。要编辑的消息的标识符 |
| inline_message_id | String | 可选 | 如果未指定*chat_id*和*message_id*，则为必需参数。内联消息的标识符 |
| reply_markup | InlineKeyboardMarkup | 可选 | 用于内联键盘的JSON序列化对象。 |


## copyMessage（复制消息）

使用此方法可以复制任何类型的消息。服务消息、付费媒体消息、赠品消息、赠品获奖者消息和发票消息不能被复制。测验投票只有在机器人知道*correct_option_id*字段的值时才能被复制。此方法类似于forwardMessage方法，但复制的消息没有指向原始消息的链接。成功时返回发送消息的MessageId。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为`@channelusername`） |
| message_thread_id | Integer | 可选 | 论坛的目标消息线程（主题）的唯一标识符；仅适用于论坛超级群组 |
| from_chat_id | Integer 或 String | 是 | 原始消息发送所在聊天的唯一标识符（或格式为`@channelusername`的频道用户名） |
| message_id | Integer | 是 | 在*from_chat_id*指定的聊天中的消息标识符 |
| video_start_timestamp | Integer | 可选 | 消息中复制的视频的新开始时间戳 |
| caption | String | 可选 | 媒体的新说明，解析实体后为0-1024个字符。如果未指定，将保留原始说明 |
| parse_mode | String | 可选 | 新说明中实体的解析模式。详情请查看格式选项。 |
| caption_entities | Array of MessageEntity | 可选 | 新说明中出现的特殊实体的JSON序列化列表，可指定此参数代替*parse_mode* |
| show_caption_above_media | Boolean | 可选 | 传递*True*，如果说明必须显示在消息媒体上方。如果未指定新说明，则忽略此参数。 |
| disable_notification | Boolean | 可选 | 静默发送消息。用户将收到无声音的通知。 |
| protect_content | Boolean | 可选 | 保护发送消息的内容不被转发和保存 |
| allow_paid_broadcast | Boolean | 可选 | 传递*True*以允许每秒最多1000条消息，忽略广播限制，每条消息收费0.1 Telegram Stars。相关Stars将从机器人的余额中扣除 |
| reply_parameters | ReplyParameters | 可选 | 要回复的消息的描述 |
| reply_markup | InlineKeyboardMarkup 或 ReplyKeyboardMarkup 或 ReplyKeyboardRemove 或 ForceReply | 可选 | 附加界面选项。用于内联键盘、自定义回复键盘、移除回复键盘的指令或强制用户回复的JSON序列化对象 |


## promoteChatMember（提升/降级聊天成员）

使用此方法可以在超级群组或频道中提升或降级用户。机器人必须是该聊天的管理员才能执行此操作，并且必须具有适当的管理员权限。将所有布尔参数传递为*False*可降级用户。成功时返回*True*。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为`@channelusername`） |
| user_id | Integer | 是 | 目标用户的唯一标识符 |
| is_anonymous | Boolean | 可选 | 如果管理员在聊天中的存在是隐藏的，传递*True* |
| can_manage_chat | Boolean | 可选 | 如果管理员可以访问聊天事件日志、获取boost列表、查看隐藏的超级群组和频道成员、举报垃圾消息并忽略慢速模式，传递*True*。此权限由任何其他管理员特权隐含。 |
| can_delete_messages | Boolean | 可选 | 如果管理员可以删除其他用户的消息，传递*True* |
| can_manage_video_chats | Boolean | 可选 | 如果管理员可以管理视频聊天，传递*True* |
| can_restrict_members | Boolean | 可选 | 如果管理员可以限制、封禁或解封聊天成员，或访问超级群组统计信息，传递*True* |
| can_promote_members | Boolean | 可选 | 如果管理员可以添加具有其自身权限子集的新管理员，或降级其直接或间接提升的管理员（由其任命的管理员所提升的管理员），传递*True* |
| can_change_info | Boolean | 可选 | 如果管理员可以更改聊天标题、照片和其他设置，传递*True* |
| can_invite_users | Boolean | 可选 | 如果管理员可以邀请新用户加入聊天，传递*True* |
| can_post_stories | Boolean | 可选 | 如果管理员可以向聊天发布故事，传递*True* |
| can_edit_stories | Boolean | 可选 | 如果管理员可以编辑其他用户发布的故事、向聊天页面发布故事、固定聊天故事并访问聊天的故事档案，传递*True* |
| can_delete_stories | Boolean | 可选 | 如果管理员可以删除其他用户发布的故事，传递*True* |
| can_post_messages | Boolean | 可选 | 如果管理员可以在频道中发布消息，或访问频道统计信息，传递*True*；仅适用于频道 |
| can_edit_messages | Boolean | 可选 | 如果管理员可以编辑其他用户的消息并可以固定消息，传递*True*；仅适用于频道 |
| can_pin_messages | Boolean | 可选 | 如果管理员可以固定消息，传递*True*；仅适用于超级群组 |
| can_manage_topics | Boolean | 可选 | 如果用户被允许创建、重命名、关闭和重新打开论坛主题，传递*True*；仅适用于超级群组 |


## setChatPermissions（设置聊天权限）

使用此方法可以为所有成员设置默认的聊天权限。机器人必须是群组或超级群组的管理员才能执行此操作，并且必须具有*can_restrict_members*管理员权限。成功时返回*True*。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标超级群组的用户名（格式为`@supergroupusername`） |
| permissions | ChatPermissions | 是 | 新的默认聊天权限的JSON序列化对象 |
| use_independent_chat_permissions | Boolean | 可选 | 传递*True*如果聊天权限是独立设置的。否则，*can_send_other_messages*和*can_add_web_page_previews*权限将隐含*can_send_messages*、*can_send_audios*、*can_send_documents*、*can_send_photos*、*can_send_videos*、*can_send_video_notes*和*can_send_voice_notes*权限；*can_send_polls*权限将隐含*can_send_messages*权限。 |


## restrictChatMember（限制聊天成员）

使用此方法可以在超级群组中限制用户。机器人必须是该超级群组的管理员才能执行此操作，并且必须具有适当的管理员权限。将所有权限传递为*True*可解除对用户的限制。成功时返回*True*。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标超级群组的用户名（格式为`@supergroupusername`） |
| user_id | Integer | 是 | 目标用户的唯一标识符 |
| permissions | ChatPermissions | 是 | 新的用户权限的JSON序列化对象 |
| use_independent_chat_permissions | Boolean | 可选 | 传递*True*如果聊天权限是独立设置的。否则，*can_send_other_messages*和*can_add_web_page_previews*权限将隐含*can_send_messages*、*can_send_audios*、*can_send_documents*、*can_send_photos*、*can_send_videos*、*can_send_video_notes*和*can_send_voice_notes*权限；*can_send_polls*权限将隐含*can_send_messages*权限。 |
| until_date | Integer | 可选 | 对用户的限制将被解除的日期；Unix时间。如果用户被限制超过366天或少于当前时间30秒，则视为被永久限制 |


## setMyDefaultAdministratorRights（设置我的默认管理员权限）

使用此方法可以更改机器人被添加为群组或频道的管理员时请求的默认管理员权限。这些权限将向用户建议，但用户可以在添加机器人之前修改列表。成功时返回*True*。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| rights | ChatAdministratorRights | 可选 | 描述新的默认管理员权限的JSON序列化对象。如果未指定，默认管理员权限将被清除。 |
| for_channels | Boolean | 可选 | 传递*True*以更改机器人在频道中的默认管理员权限。否则，将更改机器人在群组和超级群组中的默认管理员权限。 |


## setChatAdministratorCustomTitle（设置聊天管理员自定义头衔）

使用此方法可以为机器人在超级群组中提升的管理员设置自定义头衔。成功时返回*True*。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标超级群组的用户名（格式为`@supergroupusername`） |
| user_id | Integer | 是 | 目标用户的唯一标识符 |
| custom_title | String | 是 | 管理员的新自定义头衔；0-16个字符，不允许使用表情符号 |


## getChatMember（获取聊天成员信息）

使用此方法可以获取聊天成员的信息。仅当机器人是聊天的管理员时，才能保证此方法对其他用户有效。成功时返回一个ChatMember对象。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标超级群组或频道的用户名（格式为`@channelusername`） |
| user_id | Integer | 是 | 目标用户的唯一标识符 |


## setChatTitle（设置聊天标题）

使用此方法可以更改聊天的标题。私人聊天的标题不能更改。机器人必须是该聊天的管理员才能执行此操作，并且必须具有适当的管理员权限。成功时返回*True*。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为`@channelusername`） |
| title | String | 是 | 新的聊天标题，1-128个字符 |


## getChatAdministrators（获取聊天管理员列表）

使用此方法可以获取聊天中不是机器人的管理员列表。返回一个ChatMember对象数组。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标超级群组或频道的用户名（格式为`@channelusername`） |


## getMyCommands（获取我的命令）

使用此方法可以获取机器人在给定范围和用户语言下的当前命令列表。返回一个BotCommand对象数组。如果未设置命令，将返回空列表。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| scope | BotCommandScope | 可选 | 一个JSON序列化的对象，描述用户范围。默认为BotCommandScopeDefault。 |
| language_code | String | 可选 | 两个字母的ISO 639-1语言代码或空字符串 |


## setMyCommands（设置我的命令）

使用此方法可以更改机器人的命令列表。有关机器人命令的更多详细信息，请参见本手册。成功时返回*True*。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| commands | Array of BotCommand | 是 | 一个JSON序列化的机器人命令列表，将被设置为机器人的命令列表。最多可指定100个命令。 |
| scope | BotCommandScope | 可选 | 一个JSON序列化的对象，描述命令相关的用户范围。默认为BotCommandScopeDefault。 |
| language_code | String | 可选 | 两个字母的ISO 639-1语言代码。如果为空，命令将应用于来自给定范围的所有用户，对于这些用户的语言没有专门的命令 |


## createChatInviteLink（创建聊天邀请链接）

使用此方法可以为聊天创建一个额外的邀请链接。机器人必须是该聊天的管理员才能执行此操作，并且必须具有适当的管理员权限。可以使用revokeChatInviteLink方法撤销该链接。成功时返回新的邀请链接作为ChatInviteLink对象。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为`@channelusername`） |
| name | String | 可选 | 邀请链接名称；0-32个字符 |
| expire_date | Integer | 可选 | 链接将过期的时间点（Unix时间戳） |
| member_limit | Integer | 可选 | 通过此邀请链接加入聊天后，可同时成为聊天成员的最大用户数量；1-99999 |
| creates_join_request | Boolean | 可选 | 如果通过链接加入聊天的用户需要得到聊天管理员的批准，传递*True*。如果为*True*，则不能指定*member_limit* |


## editChatInviteLink（编辑聊天邀请链接）

使用此方法可以编辑机器人创建的非主要邀请链接。机器人必须是该聊天的管理员才能执行此操作，并且必须具有适当的管理员权限。成功时返回编辑后的邀请链接作为ChatInviteLink对象。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为`@channelusername`） |
| invite_link | String | 是 | 要编辑的邀请链接 |
| name | String | 可选 | 邀请链接名称；0-32个字符 |
| expire_date | Integer | 可选 | 链接将过期的时间点（Unix时间戳） |
| member_limit | Integer | 可选 | 通过此邀请链接加入聊天后，可同时成为聊天成员的最大用户数量；1-99999 |
| creates_join_request | Boolean | 可选 | 如果通过链接加入聊天的用户需要得到聊天管理员的批准，传递*True*。如果为*True*，则不能指定*member_limit* |


## revokeChatInviteLink（撤销聊天邀请链接）

使用此方法可以撤销机器人创建的邀请链接。如果主要链接被撤销，将自动生成一个新链接。机器人必须是该聊天的管理员才能执行此操作，并且必须具有适当的管理员权限。成功时返回被撤销的邀请链接作为ChatInviteLink对象。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为`@channelusername`） |
| invite_link | String | 是 | 要撤销的邀请链接 |


## approveChatJoinRequest（批准聊天加入请求）

使用此方法可以批准聊天加入请求。机器人必须是该聊天的管理员才能执行此操作，并且必须具有*can_invite_users*管理员权限。成功时返回*True*。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为`@channelusername`） |
| user_id | Integer | 是 | 目标用户的唯一标识符 |


## declineChatJoinRequest（拒绝聊天加入请求）

使用此方法可以拒绝聊天加入请求。机器人必须是该聊天的管理员才能执行此操作，并且必须具有*can_invite_users*管理员权限。成功时返回*True*。

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| chat_id | Integer 或 String | 是 | 目标聊天的唯一标识符或目标频道的用户名（格式为`@channelusername`） |
| user_id | Integer | 是 | 目标用户的唯一标识符 |


## answerCallbackQuery（回复回调查询）

使用此方法可以回复从[内联键盘](https://core.telegram.org/bots/features#inline-keyboards)发送的回调查询。回复将以聊天屏幕顶部的通知或警报的形式显示给用户。成功时返回*True*。

{% hint style="info" %}
或者，可以将用户重定向到指定的游戏URL。要使此选项生效，你必须首先通过[@BotFather](https://t.me/botfather)为你的机器人创建一个游戏并接受条款。否则，你可以使用类似`t.me/your_bot?start=XXXX`的链接，这些链接会打开带有参数的你的机器人。
{% endhint %}

| 参数 | 类型 | 是否必需 | 描述 |
| ---- | ---- | ---- | ---- |
| callback_query_id | String | 是 | 要回复的查询的唯一标识符 |
| text | String | 可选 | 通知文本。如果未指定，将不会向用户显示任何内容，0-200个字符 |
| show_alert | Boolean | 可选 | 如果为*True*，客户端将显示一个警报，而不是聊天屏幕顶部的通知。默认为*false*。 |
| url | String | 可选 | 用户客户端将打开的URL。如果你已创建一个游戏并通过@BotFather接受了条件，请指定打开你的游戏的URL - 请注意，这仅在查询来自*callback_game*按钮时有效。<br>否则，你可以使用类似`t.me/your_bot?start=XXXX`的链接，这些链接会打开带有参数的你的机器人。 |
| cache_time | Integer | 可选 | 回调查询结果可在客户端缓存的最长时间（秒）。Telegram应用将从3.14版本开始支持缓存。默认为0。 |