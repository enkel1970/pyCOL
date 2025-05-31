import cv2, platform
from cv2_enumerate_cameras import enumerate_cameras

def find_camera_index_by_name_substring():
    """
    Find index of camera ocal2: ocal2.
    """
    platform_name = platform.system().lower()
    target_name = "ocal2: ocal2"

    if platform_name == 'linux':
        print('Using V4L2 backend for Linux cameras.')
        for camera_info in enumerate_cameras(cv2.CAP_V4L2):
            print(f'{camera_info.index}: {camera_info.name}')
            if camera_info.name == target_name:
                print(f'Found camera with name "ocal2" at index {camera_info.index}')
                return camera_info.index
    elif platform_name == 'windows':
        print('Using DirectShow backend for Windows cameras.')
        for camera_info in enumerate_cameras(cv2.CAP_DSHOW):
            print(f'{camera_info.index}: {camera_info.name}')
            if camera_info.name == target_name:
                print(f'Found camera with name "ocal2" at index {camera_info.index}')
                return camera_info.index
    elif platform_name == 'darwin':
        print('Using AVFoundation backend for macOS cameras.')
        for camera_info in enumerate_cameras(cv2.CAP_AVFOUNDATION):
            print(f'{camera_info.index}: {camera_info.name}')
            if camera_info.name == target_name:
                print(f'Found camera with name "ocal2" at index {camera_info.index}')
                return camera_info.index
    else:
        raise RuntimeError(f'Unsupported platform: {platform_name}. Supported platforms are Linux, Windows, and macOS.')    

    return None