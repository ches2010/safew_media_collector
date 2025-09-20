# SafeW Media Collector

一个用于监听 Discord 频道、收集图片和视频，并通过 Web 界面查看的工具。此项目旨在与 SafeW Bot 配合使用，但也可以适配其他 Bot。

## 功能

*   监听指定 Discord 频道的消息。
*   自动下载消息中的图片和视频附件。
*   将文件元数据（文件名、访问 URL、时间戳、关联消息）存储在 SQLite 数据库中。
*   提供一个简单的 Web 前端，用于浏览和查看已收集的媒体文件。
*   支持通过 systemd 部署为 Ubuntu 服务器上的长期运行服务，并设置开机自启。

## 技术栈

*   **后端:** Python 3, Flask, discord.py
*   **前端:** HTML5, CSS3, JavaScript (Vanilla JS)
*   **数据库:** SQLite
*   **部署:** systemd (Linux)

## 部署 (Ubuntu)

### 先决条件

*   一个拥有读取消息和附件权限的 Discord Bot。
*   Bot 已加入包含目标频道的服务器。
*   一台运行 Ubuntu 的服务器 (推荐 18.04 LTS 或更高版本)。

### 一键部署

1.  **克隆或下载此仓库:**
    ```bash
    git clone https://github.com/ches2010/safew_media_collector.git
    cd safew_media_collector
    ```

2.  **配置环境变量:**
    *   复制 `.env.example` 文件:
        ```bash
        cp .env.example .env
        ```
    *   编辑 `.env` 文件，填入你的 Discord Bot Token 和要监听的频道 ID:
        ```bash
        nano .env
        ```
        内容示例:
        ```env
        DISCORD_BOT_TOKEN=YOUR_ACTUAL_BOT_TOKEN_HERE
        DISCORD_CHANNEL_ID=YOUR_ACTUAL_CHANNEL_ID_HERE
        ```

3.  **赋予部署脚本执行权限并运行:**
    ```bash
    chmod +x deploy.sh
    sudo ./deploy.sh
    ```

4.  **访问前端:**
    *   部署完成后，脚本会输出服务器的 IP 地址。
    *   在浏览器中访问 `http://<你的服务器IP>:9890` 即可查看收集到的媒体。

### 手动部署 (备选)

如果你不想使用一键脚本，可以参考 `deploy.sh` 的步骤手动操作：

1.  安装 Python 3, pip, venv: `sudo apt install python3 python3-pip python3-venv`
2.  创建并激活虚拟环境: `cd backend && python3 -m venv venv && source venv/bin/activate`
3.  安装依赖: `pip install -r requirements.txt`
4.  确保 `.env` 文件已配置。
5.  初始化数据库: `python database.py`
6.  启动应用: `python app.py` (这将在前台运行)
7.  配置 `safew_media_collector.service` 文件并使用 `systemctl` 管理服务。

## 项目结构

  ```bash
    safew_media_collector/
    ├── backend/                 # 后端服务代码
    │   ├── app.py              # 主应用 (Flask + Discord Bot)
    │   ├── requirements.txt    # Python 依赖
    │   ├── config.py           # 配置加载 (从 .env)
    │   ├── database.py         # 数据库初始化
    │   └── media/              # 下载的媒体文件存储目录 (运行时生成)
    ├── frontend/               # 前端静态文件
    │   └── index.html          # 媒体查看页面
    ├── safew_media_collector.service.template # systemd 服务模板
    ├── deploy.sh               # 一键部署脚本
    ├── .env.example            # 环境变量示例
    ├── .gitignore              # Git 忽略文件列表
    └── README.md               # 本文件
   ```

## 配置

所有配置项均通过 `.env` 文件进行管理。请确保 `.env` 文件存在于项目根目录。

*   `DISCORD_BOT_TOKEN`: 你的 Discord Bot 的 Token。
*   `DISCORD_CHANNEL_ID`: 你希望监听的频道的数字 ID。

## 维护与日志

*   **服务管理:**
*   查看状态: `sudo systemctl status safew_media_collector`
*   启动服务: `sudo systemctl start safew_media_collector`
*   停止服务: `sudo systemctl stop safew_media_collector`
*   重启服务: `sudo systemctl restart safew_media_collector`
*   **查看日志:**
*   实时日志: `sudo journalctl -u safew_media_collector -f`
*   最近日志: `sudo journalctl -u safew_media_collector --since "1 hour ago"`

## 安全注意事项

*   **保护 `.env` 文件:** `.env` 文件包含敏感的 Bot Token。确保它不会被意外提交到 Git 仓库 (`.gitignore` 已配置) 并且文件权限设置正确 (部署脚本会处理)。
*   **防火墙:** 考虑配置防火墙 (如 UFW) 仅允许必要的端口 (如 22 SSH, 5000 应用)。
*   **更新:** 定期更新系统和 Python 依赖包以修复安全漏洞。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进此项目。

## 许可证

  ```
    MIT License

    Copyright (c) [2025] [ches2010]

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
  ```
