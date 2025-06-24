# Camera index finder for ocal2 camera
import cv2, platform
from cv2_enumerate_cameras import enumerate_cameras


def find_camera_index_by_name_substring():
    """
    Find index of camera ocal2: ocal2.
    """
    platform_name = platform.system().lower()
    target_name_linux = "ocal2: ocal2"
    target_name_windows = "ocal2"
    target_name_darwin = "ocal2"

    if platform_name == "linux":
        print("Using V4L2 backend for Linux cameras.")
        for camera_info in enumerate_cameras(cv2.CAP_V4L2):
            print(f"{camera_info.index}: {camera_info.name}")
            if target_name_linux in camera_info.name:
                print(f'Found camera with name "ocal2" at index {camera_info.index}')
                return camera_info.index - 1  # Adjusting index for V4L2 backend
    elif platform_name == "windows":
        print("Using MSMF backend for Windows cameras.")
        for camera_info in enumerate_cameras(cv2.CAP_MSMF):
            print(f"{camera_info.index}: {camera_info.name}")
            if target_name_windows in camera_info.name:
                print(f'Found camera with name "ocal2" at index {camera_info.index}')
                return camera_info.index
    elif platform_name == "darwin":
        print("Using AVFoundation backend for macOS cameras.")
        for camera_info in enumerate_cameras(cv2.CAP_AVFOUNDATION):
            print(f"{camera_info.index}: {camera_info.name}")
            if target_name_darwin in camera_info.name:
                print(camera_info.name)
                print(f'Found camera with name "ocal2" at index {camera_info.index}')
            return camera_info.index
    else:
        raise RuntimeError(
            f"Unsupported platform: {platform_name}. Supported platforms are Linux, Windows, and partial Darwin."
        )

    return None
