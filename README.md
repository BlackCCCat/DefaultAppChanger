
---

# 📂 Default Apps Changer for macOS

一个基于 **PyQt6** 的图形界面工具，用于在 macOS 上快速批量设置文件类型的默认打开方式（依赖 [duti](https://github.com/moretension/duti) 命令行工具）。

---

## ✨ 功能特点

* 自动扫描 `/Applications` 与 `/System/Applications` 中的支持文本/代码编辑类的 App（如 VSCode、TextEdit、Sublime Text 等）
* 支持按类别（如“基础文本格式”、“编程语言格式”）批量选择文件扩展名
* 每个类别下的子项以多列布局呈现，支持“全选/取消”、“反选”
* 更改完成后根据成功与否弹窗反馈详细信息
* 支持显示 App 图标，提高识别度

---

## 📦 依赖项

确保以下环境已经配置好：

* Python ≥ 3.7
* PyQt6
* [duti](https://github.com/moretension/duti)：用于设置 macOS 默认打开方式（可通过 Homebrew 安装）

```bash
brew install duti
pip install PyQt6
```

---

## 🚀 运行方式

```bash
python DefaultAppChanger.py
```

---

## 🖼️ 界面示意

* App 选择框支持显示图标
* 文件类型分为多个分类，每类下有子项，支持全选、反选
* 支持滚动区域展示所有内容
* “更改打开方式”按钮仅在勾选项非空时可用

---

## 📂 文件类型分类示例

* **基础文本格式**：`.txt`, `.csv`, `.json` 等
* **编程语言格式**：`.py`, `.cpp`, `.js`, `.html` 等
* **标记语言格式**：`.md`, `.rst`, `.tex`
* **其他**：`.gitignore`, `.makefile`, `.plist` 等

---

## ⚠️ 注意事项

* 请确保 `duti` 命令可用（通过终端输入 `duti -h` 验证）
* 修改默认打开方式后，部分类型可能需重启 Finder 或系统才能生效
* 仅限 macOS 使用

---

## 📄 License

MIT License

---

