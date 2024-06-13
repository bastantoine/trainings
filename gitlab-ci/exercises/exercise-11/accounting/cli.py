import platform
import sys

if __name__ == "__main__":
    plateform = platform.platform()
    major = sys.version_info.major
    minor = sys.version_info.minor
    micro = sys.version_info.micro
    print(f"cli running on {plateform} with Python {major}.{minor}.{micro}")
