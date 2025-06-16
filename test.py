# 显卡测试是否可用
import torch
import platform
import psutil
import sys


def check_gpu_and_cpu_details():
    print("=== Python / PyTorch 基本信息 ===")
    print(f"Python 版本: {platform.python_version()}")
    print(f"PyTorch 版本: {torch.__version__}")
    print(f"CUDA 编译版本: {torch.version.cuda}")
    print(f"是否支持 CUDA: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        gpu_count = torch.cuda.device_count()
        print(f"可用 GPU 数量: {gpu_count}")

        for i in range(gpu_count):
            print(f"\n=== GPU {i} 信息 ===")
            try:
                gpu_name = torch.cuda.get_device_name(i)
                capability = torch.cuda.get_device_capability(i)
                props = torch.cuda.get_device_properties(i)
                total_memory = props.total_memory
                allocated_memory = torch.cuda.memory_allocated(i)
                reserved_memory = torch.cuda.memory_reserved(i)
                free_memory = total_memory - allocated_memory

                print(f"GPU 名称: {gpu_name}")
                print(f"CUDA 版本: {torch.version.cuda}")
                print(f"计算能力: {capability[0]}.{capability[1]}")
                print(f"总显存: {total_memory / 1024 ** 2:.2f} MB")
                print(f"已分配显存: {allocated_memory / 1024 ** 2:.2f} MB")
                print(f"保留显存: {reserved_memory / 1024 ** 2:.2f} MB")
                print(f"空闲显存(估算): {free_memory / 1024 ** 2:.2f} MB")
            except Exception as e:
                print(f"获取 GPU {i} 信息时出错: {e}")
    else:
        print("未检测到可用的 CUDA 设备（可能使用的是 CPU-only PyTorch）")

    print("\n=== CPU 信息 ===")
    cpu_info = platform.processor()
    print(f"CPU 型号: {cpu_info or '未知'}")

    physical_cores = psutil.cpu_count(logical=False)
    logical_cores = psutil.cpu_count(logical=True)
    print(f"物理核心数: {physical_cores}")
    print(f"逻辑核心数: {logical_cores}")

    cpu_freq = psutil.cpu_freq()
    if cpu_freq:
        print(f"当前频率: {cpu_freq.current:.2f} MHz")
        print(f"最大频率: {cpu_freq.max:.2f} MHz")
    else:
        print("无法获取 CPU 频率信息")

    cpu_usage = psutil.cpu_percent(interval=1)
    print(f"CPU 使用率: {cpu_usage:.1f}%")


if __name__ == "__main__":
    check_gpu_and_cpu_details()