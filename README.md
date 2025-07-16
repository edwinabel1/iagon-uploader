# IAGON Uploader

IAGON Uploader 是一个用于递归上传本地目录结构到 IAGON 分布式存储平台的 Python CLI 工具。  
支持多层目录自动映射、权限控制（public/private）、上传进度显示、私有文件访问密码等功能。

## 功能特点

- 递归上传本地目录及其所有子目录中的文件
- 自动在 IAGON 远程端创建对应目录结构
- 支持 public / private 权限控制
- 支持为私有文件设置访问密码
- 实时上传进度显示
- 仅依赖 Python 标准库与 requests，部署简单

## 安装依赖

```bash
pip install requests
````

## 设置认证信息

你需要在 IAGON 控制台生成 Personal Access Token，并设置为环境变量：

PowerShell（仅当前窗口有效）：

```powershell
$env:IAGON_API_TOKEN = "your_token_here"
```

Linux / macOS（仅当前窗口有效）：

```bash
export IAGON_API_TOKEN="your_token_here"
```

## 使用方法

公共上传（无需密码）：

```bash
python iagon_uploader.py --dir "./your_folder" --visibility public
```

私有上传（需要密码）：

```bash
python iagon_uploader.py --dir "./your_folder" --visibility private --password yourpassword
```

## 参数说明

| 参数                | 类型   | 说明                            |
| ----------------- | ---- | ----------------------------- |
| --dir             | 必填   | 要上传的本地目录路径                    |
| --visibility      | 可选   | public 或 private，默认 private   |
| --password        | 私有必填 | 当 --visibility private 时，必须提供 |
| IAGON\_API\_TOKEN | 环境变量 | 必须设置为你的 Personal Access Token |

## 示例

上传本地 images 目录为公开：

```bash
python iagon_uploader.py --dir "./images" --visibility public
```

上传本地 backup 目录为私有（密码设为 mypass）：

```bash
python iagon_uploader.py --dir "./backup" --visibility private --password mypass
```

## 注意事项

* 本工具仅做上传，不处理文件/目录公开 URL 的生成，请到 IAGON 控制台查看。
* 建议使用 `/` 或 `\\` 分隔目录，避免 Windows 下单斜杠转义冲突。
* 运行前请确保设置好 IAGON\_API\_TOKEN 环境变量。

## License

MIT

欢迎反馈建议、提 Issue 或 PR！
