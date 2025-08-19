# FIT-GPX 转换器

这是一个用于将FIT格式运动数据文件转换为GPX格式的工具，具有直观的图形用户界面。

## 功能特点

- 将文件夹中的所有FIT文件批量转换为GPX格式
- 支持自定义输出文件目录，实现输入输出分离
- 提供直观的图形用户界面，使用ttkbootstrap美化
- 显示转换进度和详细日志
- 支持中文显示
- 提供文件验证功能，避免转换无效文件
- 错误处理和重试机制
- 程序图标支持

## 安装依赖

该工具需要Python环境以及以下Python库：

- fitparse：用于解析FIT文件
- gpxpy：用于处理GPX文件
- ttkbootstrap：用于美化GUI界面
- pillow：ttkbootstrap的依赖库

可以使用以下命令安装依赖：

```bash
pip install fitparse gpxpy ttkbootstrap pillow
```

## 使用方法

1. 运行主程序文件 `fit2gpx_converter.py`
2. 点击"浏览"按钮选择包含FIT文件的输入文件夹
3. 点击"浏览"按钮选择保存转换后GPX文件的输出文件夹（默认与输入文件夹相同）
4. 点击"开始转换"按钮开始操作
5. 观察转换进度和日志输出
6. 如有需要，点击"帮助"按钮查看使用说明

## 注意事项

- 文件太小（小于1KB）的FIT文件可能无法正常转换
- 转换后的GPX文件会保存在用户指定的输出文件夹中
- 如果转换过程中遇到问题，请查看日志区域的详细信息
- 程序需要安装所有依赖库才能运行

## 系统要求

- Windows操作系统
- Python 3.6或更高版本
- 足够的磁盘空间来存储转换后的文件

## 项目结构

```
fit2gpx/
├── fit2gpx_converter.py  # 主程序文件
├── README.md             # 项目说明
├── b.ico                 # 程序图标
└── venv/                 # Python虚拟环境
```

## 打包成可执行文件

如果需要将程序打包成Windows可执行文件，可以使用PyInstaller：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=b.ico fit2gpx_converter.py
```

打包后的可执行文件将位于`dist`目录下。

## 贡献

欢迎提交Issue和Pull Request来改进这个工具。

## 许可证

[MIT License](https://opensource.org/licenses/MIT)

## 作者

- Wyl-k
- QQ群：521292550
- B站主页：https://space.bilibili.com/3546591426251062
