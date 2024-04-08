import subprocess
import time
import psutil

def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return True
    return False

def run_aspera_transfer():
    command = [
        r"C:\Program Files\IBM\Aspera Connect\bin\ascp.exe",   # 替换成你的Aspera的安装位置的ascp.exe
        "-i", r"D:\data\aspera.openssh", # 替换成从NCBI下载得出传输密钥的位置
        "-QT", "-l500m", "-k1", "-d", # 设置一下限速
        r"D:\data\single-celldata\\", # 替换成你要上传的文件夹，填到文件夹就行，会自动上传文件夹里所有文件
        "subasp@upload.ncbi.nlm.nih.gov:uploads/mail_adress_code/file_you_add_at_root_catalog"  # 用从NCBI处获取的上传路径替换这里，记得在主路径新建文件夹
    ]
    subprocess.run(command)

while True:
    if not is_process_running("ascp.exe"):
        print("Aspera transfer interrupted. Restarting...")
        run_aspera_transfer()
    time.sleep(60)  # 每60秒检查一次
