import os
import time
import argparse
import requests

BASE_URL = "https://gw.iagon.com/api/v2"

# 从环境变量读取 API Token
API_TOKEN = os.environ.get("IAGON_API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("❌ 环境变量 IAGON_API_TOKEN 未设置。请使用 export 或 set 设置它。")

HEADERS = {
    "x-api-key": API_TOKEN
}

# 缓存本地相对目录路径对应的远程目录 ID
remote_dir_map = {}

def create_remote_directory(local_path, visibility="private", parent_id=None):
    dir_name = os.path.basename(local_path.rstrip(os.sep))
    payload = {
        "directory_name": dir_name,
        "visibility": visibility,
        "index_listing": True
    }
    # ⚠️ 若官方支持，可启用 parent_directory_id
    if parent_id:
        payload["parent_directory_id"] = parent_id

    res = requests.post(f"{BASE_URL}/storage/directory", json=payload, headers=HEADERS)
    if res.ok:
        dir_id = res.json()['data']['_id']
        print(f"[📁] 创建远程目录: {dir_name} → ID: {dir_id}")
        return dir_id
    else:
        raise Exception(f"[❌] 创建目录失败 ({local_path}): {res.status_code} - {res.text}")

def upload_file(file_path, file_name, directory_id, visibility="private", password=None, file_index=None, total_files=None):
    url = f"{BASE_URL}/storage/upload"
    try:
        with open(file_path, 'rb') as f:
            files = {
                "file": (file_name, f, "application/octet-stream")
            }
            data = {
                "filename": file_name,
                "visibility": visibility,
                "index_listing": "true",
                "directoryId": directory_id
            }
            if visibility == "private":
                data["password"] = password or ""

            res = requests.post(url, headers=HEADERS, data=data, files=files)
            if res.ok:
                print(f"[{file_index}/{total_files}] ✅ 上传成功: {file_path}")
            else:
                print(f"[{file_index}/{total_files}] ⚠️ 上传失败: {file_path} - {res.status_code} - {res.text}")
    except Exception as e:
        print(f"[❌] 文件读取失败: {file_path} - {e}")

def collect_all_files(root_dir):
    """收集所有待上传文件及其相对路径"""
    file_list = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            full = os.path.join(root, file)
            rel = os.path.relpath(full, root_dir)
            file_list.append((full, rel))
    return file_list

def recursive_upload(local_root, visibility="private", password=None):
    start_time = time.time()

    # 获取所有文件列表
    all_files = collect_all_files(local_root)
    total_files = len(all_files)
    print(f"\n📦 发现 {total_files} 个文件，开始上传...\n")

    # 缓存本地相对路径到远程目录 ID 的映射
    for i, (file_path, rel_path) in enumerate(all_files, 1):
        rel_dir = os.path.dirname(rel_path)
        if rel_dir not in remote_dir_map:
            if rel_dir == ".":
                dir_id = None
            else:
                parent_dir = os.path.dirname(rel_dir)
                parent_id = remote_dir_map.get(parent_dir)
                dir_id = create_remote_directory(os.path.join(local_root, rel_dir), visibility, parent_id)
            remote_dir_map[rel_dir] = dir_id
        else:
            dir_id = remote_dir_map[rel_dir]

        upload_file(file_path, os.path.basename(file_path), dir_id,
                    visibility, password, i, total_files)
        time.sleep(0.3)  # 可根据情况调整上传节奏

    end_time = time.time()
    print(f"\n✅ 上传完成，用时 {end_time - start_time:.1f} 秒，共上传 {total_files} 个文件。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🧩 IAGON 递归上传器 v0.3")
    parser.add_argument("--dir", required=True, help="本地目录路径（将被递归上传）")
    parser.add_argument("--visibility", choices=["private", "public"], default="private", help="文件可见性")
    parser.add_argument("--password", help="若 visibility=private，必须提供密码")
    args = parser.parse_args()

    if args.visibility == "private" and not args.password:
        raise RuntimeError("❌ visibility=private 时必须使用 --password 显式提供访问密码。")

    if not os.path.isdir(args.dir):
        raise RuntimeError(f"❌ 指定路径无效或不是目录: {args.dir}")

    recursive_upload(args.dir, args.visibility, args.password)
