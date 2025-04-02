import os
import platform
import shutil
import sys


def get_cache_paths():
    system = platform.system()
    cache_paths = []

    if system == "Windows":
        possible_paths = [
            os.path.join(os.getenv("APPDATA"), "Cursor", "Cache"),
            os.path.join(os.getenv("LOCALAPPDATA"), "Cursor", "Cache"),
        ]
        cache_paths.extend(possible_paths)
    elif system == "Darwin":  # macOS
        mac_path = os.path.expanduser("~/Library/Caches/Cursor")
        cache_paths.append(mac_path)
    elif system == "Linux":
        linux_path = os.path.expanduser("~/.cache/Cursor")
        cache_paths.append(linux_path)
    else:
        print(f"Unsupported system: {system}")
        sys.exit(1)

    return [path for path in cache_paths if os.path.exists(path)]


def clear_cache(cache_path):
    try:
        # 删除目录中的所有内容但保留父目录
        for root, dirs, files in os.walk(cache_path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                os.remove(file_path)
                print(f"Removed file: {file_path}")
            for name in dirs:
                dir_path = os.path.join(root, name)
                os.rmdir(dir_path)
                print(f"Removed directory: {dir_path}")
        print(f"\nSuccessfully cleaned Cursor cache at: {cache_path}")
        return True
    except Exception as e:
        print(f"\nError cleaning cache: {str(e)}")
        return False


def main():
    print("Starting Cursor cache cleanup...\n")

    cache_locations = get_cache_paths()

    if not cache_locations:
        print("No Cursor cache directories found.")
        return

    print("Found cache locations:")
    for i, path in enumerate(cache_locations, 1):
        print(f"{i}. {path}")

    print("\nWARNING: This will permanently delete all cache files!")
    confirmation = input("Are you sure you want to continue? (y/N): ").strip().lower()

    if confirmation != "y":
        print("Operation cancelled.")
        return

    success_count = 0
    for path in cache_locations:
        print(f"\nCleaning: {path}")
        if clear_cache(path):
            success_count += 1

    print(
        f"\nCleaning complete. Successfully cleaned {success_count}/{len(cache_locations)} cache locations."
    )


if __name__ == "__main__":
    main()
