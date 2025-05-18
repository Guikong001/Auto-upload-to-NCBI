import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import time
import psutil
import threading
import os
import json

class AsperaUploadGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NCBI Aspera上传监控工具（作者：wslll.cn）")
        self.root.geometry("900x800")  # 增加窗口大小以适应说明文字
        
        # 创建配置文件路径
        self.config_file = "aspera_config.json"
        
        # 创建样式
        style = ttk.Style()
        style.configure("TLabel", padding=5)
        style.configure("TButton", padding=5)
        style.configure("TEntry", padding=5)
        style.configure("Info.TLabel", font=('SimSun', 9), foreground='gray')  # 说明文字样式
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        current_row = 0
        
        # Aspera路径设置
        ttk.Label(main_frame, text="Aspera路径 (ascp.exe):").grid(row=current_row, column=0, sticky=tk.W)
        self.aspera_path = tk.StringVar()
        aspera_entry = ttk.Entry(main_frame, textvariable=self.aspera_path, width=50)
        aspera_entry.grid(row=current_row, column=1, sticky=tk.W)
        ttk.Button(main_frame, text="浏览", command=lambda: self.browse_file(self.aspera_path)).grid(row=current_row, column=2)
        current_row += 1
        ttk.Label(main_frame, text="通常位于 C:\\Program Files\\IBM\\Aspera Connect\\bin\\ascp.exe", 
                 style="Info.TLabel").grid(row=current_row, column=1, sticky=tk.W)
        current_row += 1
        
        # 密钥路径设置
        ttk.Label(main_frame, text="密钥路径 (openssh):").grid(row=current_row, column=0, sticky=tk.W)
        self.key_path = tk.StringVar()
        key_entry = ttk.Entry(main_frame, textvariable=self.key_path, width=50)
        key_entry.grid(row=current_row, column=1, sticky=tk.W)
        ttk.Button(main_frame, text="浏览", command=lambda: self.browse_file(self.key_path)).grid(row=current_row, column=2)
        current_row += 1
        ttk.Label(main_frame, text="从NCBI下载的你本次上传所需要的的openssh密钥文件路径，用于验证上传权限", 
                 style="Info.TLabel").grid(row=current_row, column=1, sticky=tk.W)
        current_row += 1
        
        # 上传目录设置
        ttk.Label(main_frame, text="上传目录:").grid(row=current_row, column=0, sticky=tk.W)
        self.upload_dir = tk.StringVar()
        upload_dir_entry = ttk.Entry(main_frame, textvariable=self.upload_dir, width=50)
        upload_dir_entry.grid(row=current_row, column=1, sticky=tk.W)
        ttk.Button(main_frame, text="浏览", command=lambda: self.browse_directory(self.upload_dir)).grid(row=current_row, column=2)
        current_row += 1
        ttk.Label(main_frame, text="选择要上传的文件夹，程序会上传该文件夹内所有符合格式要求的文件", 
                 style="Info.TLabel").grid(row=current_row, column=1, sticky=tk.W)
        current_row += 1
        
        # 文件格式设置
        ttk.Label(main_frame, text="文件格式 (用逗号分隔):").grid(row=current_row, column=0, sticky=tk.W)
        self.file_formats = tk.StringVar(value="*.*")
        ttk.Entry(main_frame, textvariable=self.file_formats, width=50).grid(row=current_row, column=1, sticky=tk.W)
        current_row += 1
        ttk.Label(main_frame, text="例如: *.fastq,*.gz,*.txt 只上传指定格式的文件，使用*.*表示上传所有文件", 
                 style="Info.TLabel").grid(row=current_row, column=1, sticky=tk.W)
        current_row += 1
        
        # 限速设置
        ttk.Label(main_frame, text="上传速度限制 (Mbps):").grid(row=current_row, column=0, sticky=tk.W)
        self.speed_limit = tk.StringVar(value="500")
        ttk.Entry(main_frame, textvariable=self.speed_limit, width=50).grid(row=current_row, column=1, sticky=tk.W)
        current_row += 1
        ttk.Label(main_frame, text="设置上传速度限制，单位为Mbps，默认500Mbps，除以8为上传速度MB/s，根据网络情况调整", 
                 style="Info.TLabel").grid(row=current_row, column=1, sticky=tk.W)
        current_row += 1
        
        # NCBI上传信息设置
        ttk.Label(main_frame, text="NCBI邮箱代码:").grid(row=current_row, column=0, sticky=tk.W)
        self.mail_code = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.mail_code, width=50).grid(row=current_row, column=1, sticky=tk.W)
        current_row += 1
        ttk.Label(main_frame, text="从NCBI获取的邮箱代码，通常为一串字母数字组合，直接复制NCBI页面上的邮箱代码，@会被改为下划线_", 
                 style="Info.TLabel").grid(row=current_row, column=1, sticky=tk.W)
        current_row += 1
        
        ttk.Label(main_frame, text="目标文件夹名:").grid(row=current_row, column=0, sticky=tk.W)
        self.target_folder = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.target_folder, width=50).grid(row=current_row, column=1, sticky=tk.W)
        current_row += 1
        ttk.Label(main_frame, text="在NCBI服务器上创建的文件夹名称，用于存放上传的文件。尽量不要上传到主路径，建议在主路径下创建一个文件夹", 
                 style="Info.TLabel").grid(row=current_row, column=1, sticky=tk.W)
        current_row += 1
        
        # 检查间隔设置
        ttk.Label(main_frame, text="检查间隔 (秒):").grid(row=current_row, column=0, sticky=tk.W)
        self.check_interval = tk.StringVar(value="60")
        ttk.Entry(main_frame, textvariable=self.check_interval, width=50).grid(row=current_row, column=1, sticky=tk.W)
        current_row += 1
        ttk.Label(main_frame, text="程序检查上传状态的时间间隔，单位为秒，默认60秒", 
                 style="Info.TLabel").grid(row=current_row, column=1, sticky=tk.W)
        current_row += 1
        
        # 状态显示
        ttk.Label(main_frame, text="运行状态:").grid(row=current_row, column=0, sticky=tk.W)
        self.status_text = tk.Text(main_frame, height=10, width=60)
        self.status_text.grid(row=current_row, column=1, columnspan=2, sticky=tk.W)
        current_row += 1
        ttk.Label(main_frame, text="显示程序运行状态、错误信息和上传进度", 
                 style="Info.TLabel").grid(row=current_row, column=1, sticky=tk.W)
        current_row += 1
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=current_row, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="保存配置", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="加载配置", command=self.load_config).pack(side=tk.LEFT, padx=5)
        self.start_button = ttk.Button(button_frame, text="开始监控", command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(button_frame, text="停止监控", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 监控线程
        self.monitoring = False
        self.monitor_thread = None
        
        # 加载配置
        self.load_config()
    
    def browse_file(self, string_var):
        filename = filedialog.askopenfilename()
        if filename:
            string_var.set(filename)
    
    def browse_directory(self, string_var):
        directory = filedialog.askdirectory()
        if directory:
            string_var.set(directory)
    
    def save_config(self):
        config = {
            'aspera_path': self.aspera_path.get(),
            'key_path': self.key_path.get(),
            'upload_dir': self.upload_dir.get(),
            'file_formats': self.file_formats.get(),
            'speed_limit': self.speed_limit.get(),
            'mail_code': self.mail_code.get(),
            'target_folder': self.target_folder.get(),
            'check_interval': self.check_interval.get()
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo("成功", "配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")
    
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                self.aspera_path.set(config.get('aspera_path', ''))
                self.key_path.set(config.get('key_path', ''))
                self.upload_dir.set(config.get('upload_dir', ''))
                self.file_formats.set(config.get('file_formats', '*.*'))
                self.speed_limit.set(config.get('speed_limit', '500'))
                self.mail_code.set(config.get('mail_code', ''))
                self.target_folder.set(config.get('target_folder', ''))
                self.check_interval.set(config.get('check_interval', '60'))
        except Exception as e:
            messagebox.showerror("错误", f"加载配置失败: {str(e)}")
    
    def is_process_running(self, process_name):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == process_name:
                return True
        return False
    
    def run_aspera_transfer(self):
        ncbi_path = f"subasp@upload.ncbi.nlm.nih.gov:uploads/{self.mail_code.get()}/{self.target_folder.get()}"
        command = [
            self.aspera_path.get(),
            "-i", self.key_path.get(),
            "-QT", f"-l{self.speed_limit.get()}m", "-k1", "-d",
            self.upload_dir.get(),
            ncbi_path
        ]
        try:
            subprocess.run(command)
        except Exception as e:
            self.update_status(f"错误: {str(e)}")
    
    def update_status(self, message):
        self.status_text.insert(tk.END, f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        self.status_text.see(tk.END)
    
    def monitor_loop(self):
        while self.monitoring:
            if not self.is_process_running("ascp.exe"):
                self.update_status("Aspera传输中断，正在重新启动...")
                self.run_aspera_transfer()
            time.sleep(int(self.check_interval.get()))
    
    def start_monitoring(self):
        if not all([self.aspera_path.get(), self.key_path.get(), self.upload_dir.get(),
                   self.mail_code.get(), self.target_folder.get()]):
            messagebox.showerror("错误", "请填写所有必要信息")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.update_status("开始监控...")
    
    def stop_monitoring(self):
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.update_status("停止监控")

if __name__ == "__main__":
    root = tk.Tk()
    app = AsperaUploadGUI(root)
    root.mainloop()
