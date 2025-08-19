import os
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import fitparse
import gpxpy
from datetime import datetime, timezone, timedelta
import time
import threading

class FitGpxConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("FIT-GPX 转换器")
        # 增大窗口尺寸，确保完全显示
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置中文字体支持
        self.font_config = ('SimHei', 10)
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=BOTH, expand=YES)
        
        # 创建标题
        title_label = ttk.Label(self.main_frame, text="FIT/GPX 文件转换器", font=('SimHei', 16, 'bold'))
        title_label.pack(pady=10)
        
        # 创建输入文件夹选择部分
        input_frame = ttk.LabelFrame(self.main_frame, text="输入文件夹", padding="10")
        input_frame.pack(fill=X, pady=5)
        
        self.folder_path_var = tk.StringVar()
        folder_entry = ttk.Entry(input_frame, textvariable=self.folder_path_var, width=50, font=self.font_config)
        folder_entry.pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        
        browse_button = ttk.Button(input_frame, text="浏览", command=self.browse_folder)
        browse_button.pack(side=RIGHT)
        
        # 创建输出文件夹选择部分
        output_frame = ttk.LabelFrame(self.main_frame, text="输出文件夹", padding="10")
        output_frame.pack(fill=X, pady=5)
        
        self.output_folder_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_folder_var, width=50, font=self.font_config)
        output_entry.pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        
        output_browse_button = ttk.Button(output_frame, text="浏览", command=self.browse_output_folder)
        output_browse_button.pack(side=RIGHT)
        
        # 创建进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.main_frame, variable=self.progress_var, length=100)
        self.progress_bar.pack(fill=X, pady=10)
        
        # 创建状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(self.main_frame, textvariable=self.status_var, font=self.font_config)
        status_label.pack(pady=5)
        
        # 创建转换按钮和帮助按钮框架
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=X, pady=10)
        
        # 创建转换按钮（左对齐）
        self.convert_button = ttk.Button(button_frame, text="开始转换", command=self.start_conversion, bootstyle="primary")
        self.convert_button.pack(side=LEFT, padx=(0, 10))
        
        # 创建帮助按钮（右对齐）
        self.help_button = ttk.Button(button_frame, text="帮助", command=self.show_help, bootstyle="info")
        self.help_button.pack(side=RIGHT, padx=(10, 0))
        
        # 创建日志区域
        log_frame = ttk.LabelFrame(self.main_frame, text="转换日志", padding="10")
        log_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        self.log_text = tk.Text(log_frame, height=8, wrap=WORD, font=self.font_config)
        self.log_text.pack(side=LEFT, fill=BOTH, expand=YES)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.log_text.config(yscrollcommand=scrollbar.set)
        
    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path_var.set(folder_selected)
            # 默认将输出文件夹设置为与输入文件夹相同
            if not self.output_folder_var.get():
                self.output_folder_var.set(folder_selected)
            self.log_message(f"已选择输入文件夹: {folder_selected}")
    
    def browse_output_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_folder_var.set(folder_selected)
            self.log_message(f"已选择输出文件夹: {folder_selected}")
            
    def show_help(self):
        """显示帮助信息"""
        # 创建帮助窗口，使用ttkbootstrap的对话框风格
        help_window = ttk.Toplevel(self.root)
        help_window.title("帮助")
        help_window.geometry("400x300")
        help_window.resizable(False, False)
        help_window.transient(self.root)  # 设置为主窗口的子窗口
        help_window.grab_set()  # 模态窗口
        
        # 创建帮助信息文本区域
        help_text = tk.Text(help_window, wrap=WORD, font=self.font_config, height=12, width=40)
        help_text.pack(padx=20, pady=20, fill=BOTH, expand=YES)
        help_text.config(state=DISABLED)  # 设置为只读
        
        # 配置标签样式用于格式化文本
        help_text.tag_configure("title", font=('SimHei', 12, 'bold'), justify=CENTER)
        help_text.tag_configure("content", font=('SimHei', 10), lmargin1=20, lmargin2=20)
        help_text.tag_configure("warning", font=('SimHei', 10, 'bold'), foreground="red")
        help_text.tag_configure("footer", font=('SimHei', 10, 'italic'), justify=RIGHT)
        
        # 插入帮助信息
        help_text.config(state=NORMAL)  # 临时允许编辑
        help_text.insert(END, "FIT/GPX 文件转换器帮助\n\n", "title")
        help_text.insert(END, "使用说明:\n", "content")
        help_text.insert(END, "1. 选择输入文件夹：包含FIT文件的文件夹\n", "content")
        help_text.insert(END, "2. 选择输出文件夹：GPX文件将保存在此文件夹\n", "content")
        help_text.insert(END, "3. 点击'开始转换'按钮开始转换过程\n\n", "content")
        help_text.insert(END, "注意：文件太小的可能无法正常转换\n\n", "warning")
        help_text.insert(END, "by：Wyl-k", "footer")
        help_text.config(state=DISABLED)  # 重新设置为只读
        
        # 创建关闭按钮
        close_button = ttk.Button(help_window, text="关闭", command=help_window.destroy, bootstyle="primary")
        close_button.pack(pady=10)
    
    def start_conversion(self):
        folder_path = self.folder_path_var.get()
        output_folder_path = self.output_folder_var.get()
        
        if not folder_path or not os.path.isdir(folder_path):
            messagebox.showerror("错误", "请先选择有效的输入文件夹")
            return
        
        if not output_folder_path or not os.path.isdir(output_folder_path):
            messagebox.showerror("错误", "请先选择有效的输出文件夹")
            return
        
        # 禁用转换按钮，防止重复点击
        self.convert_button.config(state=tk.DISABLED)
        self.status_var.set("转换中...")
        self.progress_var.set(0)
        
        # 在新线程中执行转换，避免UI卡顿
        conversion_thread = threading.Thread(target=self.perform_conversion, args=(folder_path,))
        conversion_thread.daemon = True
        conversion_thread.start()
    
    def perform_conversion(self, folder_path):
        try:
            # 只保留FIT转GPX功能
            self.convert_fit_to_gpx(folder_path)
            self.root.after(0, lambda: self.status_var.set("转换完成"))
            self.root.after(0, lambda: messagebox.showinfo("完成", "文件转换已完成"))
        except Exception as e:
            # 使用lambda参数捕获错误信息，确保在异步执行时仍可访问
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self.status_var.set(f"操作出错: {msg}"))
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("错误", f"操作过程中发生错误: {msg}"))
        finally:
            self.root.after(0, lambda: self.convert_button.config(state=tk.NORMAL))
    
    def validate_fit_file(self, file_path):
        """验证FIT文件是否完整且可读"""
        try:
            # 检查文件是否存在且不为空
            if not os.path.exists(file_path):
                return False, "文件不存在"
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return False, "文件为空"
            
            # 检查文件大小是否合理（至少应该大于1KB）
            if file_size < 1024:
                return False, f"文件过小（{file_size} 字节），可能不完整"
            
            # 尝试打开文件并读取更多内容来验证
            try:
                with open(file_path, 'rb') as f:
                    # 读取文件头
                    header = f.read(12)
                    if len(header) < 12:
                        return False, "无法读取完整文件头，文件可能已损坏"
                    
                    # 尝试读取更多内容来验证文件完整性
                    # 这有助于检测"Tried to read X bytes from .FIT file but got 0"类型的错误
                    try:
                        # 尝试读取文件的多个部分
                        f.seek(0)
                        # 读取前10%的内容或最多100KB，以较小者为准
                        read_size = min(int(file_size * 0.1), 102400)
                        partial_content = f.read(read_size)
                        if len(partial_content) < read_size:
                            return False, "文件读取不完整，可能已损坏或被截断"
                    except Exception as read_e:
                        return False, f"文件读取验证失败: {str(read_e)}"
            except Exception as f_e:
                return False, f"文件访问错误: {str(f_e)}"
            
            # 尝试使用fitparse预解析文件，这是最严格的验证
            try:
                temp_fit = fitparse.FitFile(file_path)
                # 尝试读取第一个记录，检查文件结构是否有效
                # 不使用max_messages参数，而是手动限制读取的消息数量
                message_count = 0
                for message in temp_fit.get_messages('file_id'):
                    message_count += 1
                    # 只读取一个消息即可验证文件结构
                    if message_count >= 1:
                        break
            except Exception as parse_e:
                return False, f"FIT文件格式验证失败: {str(parse_e)}"
            
            return True, "文件验证通过"
        except Exception as e:
            return False, f"文件验证失败: {str(e)}"
    
    def convert_fit_to_gpx(self, folder_path):
        # 获取输出文件夹路径
        output_folder_path = self.output_folder_var.get()
        
        # 获取文件夹中的所有FIT文件
        fit_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.fit')]
        total_files = len(fit_files)
        
        if total_files == 0:
            self.log_message("未找到FIT文件")
            return
        
        self.log_message(f"找到 {total_files} 个FIT文件，开始转换...")
        self.log_message(f"输出目录: {output_folder_path}")
        
        # 用于跟踪需要重试的文件
        failed_files = []
        
        for i, fit_file in enumerate(fit_files):
            try:
                fit_file_path = os.path.join(folder_path, fit_file)
                gpx_file_path = os.path.join(output_folder_path, os.path.splitext(fit_file)[0] + '.gpx')
                
                # 转换文件
                self.fit_to_gpx(fit_file_path, gpx_file_path)
                
                # 更新进度
                progress = (i + 1) / total_files * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                self.log_message(f"已转换: {fit_file} -> {os.path.basename(gpx_file_path)}")
            except Exception as e:
                error_msg = str(e)
                self.log_message(f"转换失败 {fit_file}: {error_msg}")
                failed_files.append((fit_file, fit_file_path, gpx_file_path, error_msg))
        
        # 如果有转换失败的文件，提供重试选项
        if failed_files:
            self.log_message(f"有 {len(failed_files)} 个文件转换失败")
            # 在主线程中显示重试对话框，使用参数捕获避免闭包陷阱
            self.root.after(0, lambda ff=failed_files, ofp=output_folder_path: self._show_retry_dialog(ff, ofp))
    
    def _show_retry_dialog(self, failed_files, output_folder_path):
        """显示重试对话框"""
        # 创建一个新窗口作为重试对话框，使用ttkbootstrap风格
        retry_window = ttk.Toplevel(self.root)
        retry_window.title("文件转换重试")
        retry_window.geometry("400x300")
        retry_window.transient(self.root)  # 设置为主窗口的子窗口
        retry_window.grab_set()  # 模态窗口
        
        # 创建标签和列表框显示失败的文件
        ttk.Label(retry_window, text="以下文件转换失败，是否重试？", font=self.font_config).pack(pady=10)
        
        list_frame = ttk.Frame(retry_window)
        list_frame.pack(fill=BOTH, expand=YES, padx=10, pady=5)
        
        # 创建列表框显示失败的文件
        listbox = tk.Listbox(list_frame, font=self.font_config, width=50, height=10)
        listbox.pack(side=LEFT, fill=BOTH, expand=YES)
        
        scrollbar = ttk.Scrollbar(list_frame, command=listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        listbox.config(yscrollcommand=scrollbar.set)
        
        # 填充列表
        for idx, (fit_file, _, _, error_msg) in enumerate(failed_files):
            listbox.insert(END, f"{fit_file}: {error_msg[:30]}...")
        
        # 创建按钮
        button_frame = ttk.Frame(retry_window)
        button_frame.pack(fill=X, pady=10)
        
        ttk.Button(button_frame, text="全选", command=lambda: listbox.selection_set(0, END), bootstyle="secondary").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="取消选择", command=lambda: listbox.selection_clear(0, END), bootstyle="secondary").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="重试所选", command=lambda: self._retry_selected_files(listbox.curselection(), failed_files, retry_window), bootstyle="primary").pack(side=RIGHT, padx=5)
        ttk.Button(button_frame, text="关闭", command=retry_window.destroy, bootstyle="danger").pack(side=RIGHT, padx=5)
    
    def _retry_selected_files(self, selected_indices, failed_files, retry_window):
        """重试选择的文件"""
        if not selected_indices:
            messagebox.showinfo("提示", "请先选择要重试的文件")
            return
        
        # 关闭重试窗口
        retry_window.destroy()
        
        # 在新线程中执行重试
        retry_thread = threading.Thread(target=self._perform_retry, args=(selected_indices, failed_files))
        retry_thread.daemon = True
        retry_thread.start()
    
    def _perform_retry(self, selected_indices, failed_files):
        """执行文件转换重试"""
        # 更新状态
        self.root.after(0, lambda: self.status_var.set("重试转换中..."))
        
        # 重试选择的文件
        total_to_retry = len(selected_indices)
        success_count = 0
        
        for i, idx in enumerate(selected_indices):
            fit_file, fit_file_path, gpx_file_path, _ = failed_files[idx]
            try:
                # 先验证文件
                is_valid, validation_msg = self.validate_fit_file(fit_file_path)
                if not is_valid:
                    self.log_message(f"文件验证失败 {fit_file}: {validation_msg}，跳过重试")
                    continue
                
                # 重试转换
                self.fit_to_gpx(fit_file_path, gpx_file_path)
                
                # 更新进度
                progress = (i + 1) / total_to_retry * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                self.log_message(f"重试成功: {fit_file} -> {os.path.basename(gpx_file_path)}")
                success_count += 1
            except Exception as e:
                self.log_message(f"重试失败 {fit_file}: {str(e)}")
        
        # 显示结果
        self.root.after(0, lambda: self.status_var.set("重试完成"))
        # 使用参数捕获避免闭包陷阱
        self.root.after(0, lambda ttr=total_to_retry, sc=success_count: messagebox.showinfo("重试结果", f"共重试 {ttr} 个文件，成功 {sc} 个"))
    
    def fit_to_gpx(self, fit_file_path, gpx_file_path):
        # 首先验证文件
        is_valid, validation_msg = self.validate_fit_file(fit_file_path)
        if not is_valid:
            raise Exception(f"文件验证失败: {validation_msg}")
        
        # 解析FIT文件
        try:
            # 尝试使用兼容当前fitparse库版本的参数
            try:
                # 首先尝试使用基本参数，不使用可能不兼容的选项
                fitfile = fitparse.FitFile(fit_file_path)
            except Exception as basic_e:
                # 如果基本参数失败，尝试添加check_crc=False参数
                try:
                    fitfile = fitparse.FitFile(fit_file_path, check_crc=False)
                except Exception as crc_e:
                    # 如果添加check_crc参数也失败，则忽略这些参数
                    # 这种情况可能发生在不同版本的fitparse库中
                    raise Exception(f"无法解析FIT文件: 兼容不同版本的fitparse库失败。基本错误: {str(basic_e)}, CRC错误: {str(crc_e)}")
        except Exception as e:
            error_msg = str(e)
            # 提供更具体的错误信息
            if "Tried to read" in error_msg and "but got 0" in error_msg:
                raise Exception(f"无法解析FIT文件: 文件可能已损坏或格式不兼容。错误: {error_msg}")
            else:
                raise Exception(f"无法解析FIT文件: {error_msg}")
        
        # 创建GPX对象
        gpx = gpxpy.gpx.GPX()
        
        # 创建一个GPX track
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)
        
        # 创建一个GPX segment
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        
        # 遍历FIT文件中的所有记录
        points_added = 0
        record_count = 0
        max_retries = 3  # 设置最大重试次数
        retry_count = 0
        
        try:
            while retry_count < max_retries:
                try:
                    # 尝试获取记录
                    for record in fitfile.get_messages('record'):
                        record_count += 1
                        # 每处理100条记录休息一下，避免解析器过载
                        if record_count % 100 == 0:
                            time.sleep(0.01)
                        
                        # 尝试获取经纬度、时间和其他数据
                        latitude = None
                        longitude = None
                        timestamp = None
                        
                        for data in record:
                            try:
                                if data.name == 'position_lat' and data.value is not None:
                                    latitude = data.value / ((2**32) / 360.0)
                                elif data.name == 'position_long' and data.value is not None:
                                    longitude = data.value / ((2**32) / 360.0)
                                elif data.name == 'timestamp' and data.value is not None:
                                    # 修复时间戳处理问题
                                    # 检查timestamp是否为int类型
                                    if isinstance(data.value, int):
                                        # 如果是整数，尝试转换为datetime
                                        try:
                                            # 假设整数是从1989-12-31开始的秒数（FIT文件的时间戳格式）
                                            base_time = datetime(1989, 12, 31, tzinfo=timezone.utc)
                                            timestamp = base_time + timedelta(seconds=data.value)
                                        except Exception:
                                            # 如果转换失败，使用当前时间或跳过
                                            timestamp = None
                                    else:
                                        timestamp = data.value
                            except Exception as data_e:
                                # 单个数据项解析失败，继续处理下一个
                                continue
                        
                        # 只有当有有效的经纬度时才添加点
                        if latitude is not None and longitude is not None and latitude != 0 and longitude != 0:
                            try:
                                # 创建GPX点，处理时间戳可能为None的情况
                                gpx_point = gpxpy.gpx.GPXTrackPoint(
                                    latitude=latitude,
                                    longitude=longitude,
                                    time=timestamp if timestamp is not None else None
                                )
                                
                                # 添加其他可选数据
                                for data in record:
                                    try:
                                        if data.name == 'altitude' and data.value is not None:
                                            gpx_point.elevation = data.value
                                        elif data.name == 'heart_rate' and data.value is not None:
                                            # 添加心率数据作为扩展
                                            pass  # 这里可以根据需要添加扩展数据
                                    except Exception:
                                        # 忽略单个数据项的错误
                                        continue
                                
                                gpx_segment.points.append(gpx_point)
                                points_added += 1
                            except Exception as point_e:
                                # 添加点失败，继续处理下一个记录
                                continue
                    
                    # 如果成功处理完所有记录，跳出循环
                    break
                except Exception as e:
                    error_msg = str(e)
                    retry_count += 1
                    
                    # 针对特定的读取错误提供更详细的信息
                    if "Tried to read" in error_msg and "but got 0" in error_msg:
                        if retry_count >= max_retries:
                            # 最后一次重试失败，提供详细的错误信息
                            raise Exception(f"解析FIT文件记录时出错: 文件可能已损坏或不完整。错误: {error_msg}\n已成功解析 {points_added} 个点")
                        else:
                            # 继续重试
                            time.sleep(0.5)  # 短暂暂停后重试
                            continue
                    else:
                        # 其他错误直接抛出
                        raise Exception(f"解析FIT文件记录时出错: {error_msg}")
        except Exception as e:
            # 捕获解析过程中的异常
            raise Exception(f"解析FIT文件记录时出错: {str(e)}")
        
        # 只有当添加了点时才保存GPX文件
        if points_added > 0:
            with open(gpx_file_path, 'w', encoding='utf-8') as f:
                f.write(gpx.to_xml())
        else:
            raise Exception("未找到有效的轨迹点，无法生成GPX文件")
    
    def log_message(self, message):
        # 在UI线程中更新日志
        timestamp = datetime.now().strftime("%H:%M:%S")
        # 使用参数捕获避免闭包陷阱
        formatted_message = f"[{timestamp}] {message}\n"
        self.root.after(0, lambda msg=formatted_message: self._update_log(msg))
    
    def _update_log(self, message):
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)

if __name__ == "__main__":
    # 创建ttkbootstrap窗口，使用指定主题
    root = ttk.Window(themename="solar")
    app = FitGpxConverter(root)
    root.mainloop()