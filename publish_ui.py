import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
import json
import os
from functools import partial
import asyncio
from video_publish_func import xhs,ks,blbl,dy,wb,sph,bjh
import threading
import tkinter.font as tkFont


DATA_FILE = "last_publish_data.json"

class ArticlePublisher(ttk.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        
        self.title("Video Publisher")
        self.geometry("800x600")

        # 使用支持中文的字体
        self.default_font = tkFont.nametofont("TkDefaultFont")
        self.default_font.configure(family="Microsoft YaHei", size=10)  # SimHei (黑体) 是一个常见的中文字体
        self.option_add("*Font", self.default_font)

        self.saved_data = self.load_data()

        # 配置 grid 的列宽度比例
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)


        # Left column
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Title
        self.title_label = ttk.Label(left_frame, text="Title")
        self.title_label.grid(row=0, column=0, pady=5, sticky="e")
        self.title_entry = ttk.Entry(left_frame, width=30)
        self.title_entry.grid(row=0, column=1, pady=5)


        # Description
        self.description_label = ttk.Label(left_frame, text="Description")
        self.description_label.grid(row=1, column=0, pady=5, sticky="e")
        self.description_entry = ttk.Entry(left_frame, width=30)
        self.description_entry.grid(row=1, column=1, pady=5)

        # Tags
        self.tags_label = ttk.Label(left_frame, text="Tags")
        self.tags_label.grid(row=2, column=0, pady=5, sticky="e")
        self.tags_entry = ttk.Entry(left_frame, width=30)
        self.tags_entry.grid(row=2, column=1, pady=5)

        # # Cover Images
        # self.cover_label = ttk.Label(left_frame, text="Cover Images")
        # self.cover_label.grid(row=3, column=0, pady=5, sticky="e")
        # self.cover_button = ttk.Button(left_frame, text="Upload Images", command=self.upload_images, bootstyle="primary")
        # self.cover_button.grid(row=3, column=1, pady=5)
        # self.cover_path = tk.StringVar()
        # self.cover_entry = ttk.Entry(left_frame, textvariable=self.cover_path, state='readonly', width=30)
        # self.cover_entry.grid(row=4, column=1, pady=5)

        # File URL
        self.file_label = ttk.Label(left_frame, text="Video Path")
        self.file_label.grid(row=5, column=0, pady=5, sticky="e")
        self.file_button = ttk.Button(left_frame, text="Upload Video", command=self.upload_file, bootstyle="primary")
        self.file_button.grid(row=5, column=1, pady=5)
        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(left_frame, textvariable=self.file_path, state='readonly', width=30)
        self.file_entry.grid(row=6, column=1, pady=5)

        # Author
        self.author_label = ttk.Label(left_frame, text="Author")
        self.author_label.grid(row=8, column=0, pady=5, sticky="e")
        self.author_entry = ttk.Entry(left_frame, width=30)
        self.author_entry.grid(row=8, column=1, pady=5)

        # Right column
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.platform_label = ttk.Label(right_frame, text="Publish Platforms",  bootstyle="info")
        self.platform_label.grid(row=0, column=0, pady=5, sticky="w")
        # Additional buttons for different platforms

        self.xhs_button = ttk.Button(right_frame, text="publish to xhs", command=self.publish_xhs, bootstyle="info")
        self.xhs_button.grid(row=1, column=0, pady=5, sticky="w")

        self.ks_button = ttk.Button(right_frame, text="publish to ks", command=self.publish_ks, bootstyle="info")
        self.ks_button.grid(row=2, column=0, pady=5, sticky="w")

        self.blbl_button = ttk.Button(right_frame, text="publish to blbl", command=self.publish_blbl, bootstyle="info")
        self.blbl_button.grid(row=3, column=0, pady=5, sticky="w")

        self.dy_button = ttk.Button(right_frame, text="publish to dy", command=self.publish_dy, bootstyle="info")
        self.dy_button.grid(row=4, column=0, pady=5, sticky="w")

        self.wb_button = ttk.Button(right_frame, text="publish to wb", command=self.publish_wb, bootstyle="info")
        self.wb_button.grid(row=5, column=0, pady=5, sticky="w")

        self.sph_button = ttk.Button(right_frame, text="publish to sph", command=self.publish_sph, bootstyle="info")
        self.sph_button.grid(row=6, column=0, pady=5, sticky="w")
        
        self.bjh_button = ttk.Button(right_frame, text="publish to bjh", command=self.publish_bjh, bootstyle="info")
        self.bjh_button.grid(row=7, column=0, pady=5, sticky="w")


        self.save_data_button = ttk.Button(right_frame, text="Save Data", command=self.save_data, bootstyle="info")
        self.save_data_button.grid(row=14, column=0, pady=5, sticky="w")

        # Load saved data
        self.load_saved_data()
        # 添加一个方法来保存数据
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.save_data()
        # 然后销毁窗口
        self.destroy()
    
    # def upload_images(self):
    #     file_path = filedialog.askopenfilename(title="Select Images",filetypes=[("Image", "*.*")])
    #     if file_path:
    #         self.cover_path.set(file_path)

    def upload_file(self):
        file_path = filedialog.askopenfilename(title="Select File", filetypes=[("Video", "*.*")])
        if file_path:
            self.file_path.set(file_path)
    
    def publish_bjh(self):
        # Gather data from the UI fields
        title = self.title_entry.get()
        description = self.description_entry.get()
        tags = self.tags_entry.get()
        file_path = self.file_path.get()
        author = self.author_entry.get()
        
        # Ensure all fields are filled
        if not title or not description or not tags  or not file_path :
            messagebox.showwarning("Warning", "All fields must be filled!")
            return
        
        # 调用bjh方法
        asyncio.run(bjh(title=title, author=author, description=description, tags=tags,  file_path=file_path))

    def publish_sph(self):
        # Gather data from the UI fields
        title = self.title_entry.get()
        description = self.description_entry.get()
        tags = self.tags_entry.get()
        file_path = self.file_path.get()
        author = self.author_entry.get()
        
        # Ensure all fields are filled
        if not title or not description or not tags  or not file_path :
            messagebox.showwarning("Warning", "All fields must be filled!")
            return
        
        # 调用sph方法
        asyncio.run(sph(title=title, author=author, description=description, tags=tags,  file_path=file_path))

    def publish_wb(self):
        # Gather data from the UI fields
        title = self.title_entry.get()
        description = self.description_entry.get()
        tags = self.tags_entry.get()
        file_path = self.file_path.get()
        author = self.author_entry.get()
        
        # Ensure all fields are filled
        if not title or not description or not tags  or not file_path :
            messagebox.showwarning("Warning", "All fields must be filled!")
            return
        
        # 调用dy方法
        asyncio.run(wb(title=title, author=author, description=description, tags=tags,  file_path=file_path))

    def publish_dy(self):
        # Gather data from the UI fields
        title = self.title_entry.get()
        description = self.description_entry.get()
        tags = self.tags_entry.get()
        file_path = self.file_path.get()
        author = self.author_entry.get()
        
        # Ensure all fields are filled
        if not title or not description or not tags  or not file_path :
            messagebox.showwarning("Warning", "All fields must be filled!")
            return
        
        # 调用dy方法
        asyncio.run(dy(title=title, author=author, description=description, tags=tags,  file_path=file_path))


    def publish_blbl(self):
        # Gather data from the UI fields
        title = self.title_entry.get()
        description = self.description_entry.get()
        tags = self.tags_entry.get()
        file_path = self.file_path.get()
        author = self.author_entry.get()
        
        # Ensure all fields are filled
        if not title or not description or not tags  or not file_path :
            messagebox.showwarning("Warning", "All fields must be filled!")
            return
        
        # 调用blbl方法
        asyncio.run(blbl(title=title, author=author, description=description, tags=tags,  file_path=file_path))

    def publish_ks(self):
        # Gather data from the UI fields
        title = self.title_entry.get()
        description = self.description_entry.get()
        tags = self.tags_entry.get()
        file_path = self.file_path.get()
        author = self.author_entry.get()
        
        # Ensure all fields are filled
        if not title or not description or not tags  or not file_path :
            messagebox.showwarning("Warning", "All fields must be filled!")
            return
        
        # 调用ks方法
        asyncio.run(ks(title=title, author=author, description=description, tags=tags,  file_path=file_path))

    def publish_xhs(self):
        # Gather data from the UI fields
        title = self.title_entry.get()
        description = self.description_entry.get()
        tags = self.tags_entry.get()
        file_path = self.file_path.get()
        author = self.author_entry.get()
        
        # Ensure all fields are filled
        if not title or not description or not tags  or not file_path :
            messagebox.showwarning("Warning", "All fields must be filled!")
            return
        
        asyncio.run(xhs(title=title, author=author, description=description, tags=tags,  file_path=file_path))

    def save_data(self):
                # Gather data from the UI fields
        title = self.title_entry.get()
        description = self.description_entry.get()
        tags = self.tags_entry.get()
        file_path = self.file_path.get()
        author = self.author_entry.get()
        data = {
            "title": title,
            "description": description,
            "tags": tags,
            "file_path": file_path,
            "author": author,
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {}

    def load_saved_data(self):
        self.title_entry.insert(0, self.saved_data.get("title", ""))
        self.description_entry.insert(0, self.saved_data.get("description", ""))
        self.tags_entry.insert(0, self.saved_data.get("tags", ""))
        self.file_path.set(self.saved_data.get("file_path", ""))
        self.author_entry.insert(0, self.saved_data.get("author", ""))


if __name__ == "__main__":
    # 异步事件循环
    app = ArticlePublisher()
    app.mainloop()