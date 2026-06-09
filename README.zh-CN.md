# Draw.io SVG Docx

[English](README.md) | [简体中文](README.zh-CN.md)

这是一个独立的 Python 工具，也可以作为可选的 agent skill 使用。它用于后处理 draw.io 导出的 SVG 文件，让这些 SVG 插入到 Word、WPS 或 `.docx` 文档后表现更稳定。

它主要处理这些常见问题：

- 移除 `Text is not SVG - cannot display`;
- 默认移除 `foreignObject` HTML fallback;
- 从 draw.io 的 HTML 文本块中恢复多行文本;
- 将多行 fallback 文本转换为多个独立的 SVG `<text>` 节点，以提高 Word/WPS 兼容性;
- 处理后检查 SVG XML 是否有效。

## 仓库结构

```text
drawio-svg-docx/
├── README.md
├── README.zh-CN.md
├── LICENSE
├── skills/
│   └── drawio-svg-docx/
│       ├── SKILL.md
│       └── scripts/
│           └── fix_drawio_svg.py
└── tests/
    └── test_fix_drawio_svg.py
```

## 使用方法

对单个 SVG 文件或包含 SVG 文件的目录运行后处理脚本：

```bash
python3 skills/drawio-svg-docx/scripts/fix_drawio_svg.py path/to/svg-or-directory
```

只检查、不修改文件：

```bash
python3 skills/drawio-svg-docx/scripts/fix_drawio_svg.py --check path/to/svg-or-directory
```

如果你从 draw.io 重新导出了 SVG，需要再次运行后处理脚本，因为 draw.io 会重新生成原始 SVG 内容。

## 可选：安装为 Skill

如果你的 AI 编码工具支持本地 skills，可以把 skill 目录复制到对应的 skills 目录中。以 Codex 为例，通常可以这样安装：

```bash
mkdir -p ~/.codex/skills
cp -a skills/drawio-svg-docx ~/.codex/skills/
```

根据你的环境，也可能支持 `.agents/skills/` 这类工作区本地 skill 目录。

## 环境要求

- Python 3.10 或更高版本。
- 可选：如果还需要从 `.drawio` 或 `.io` 文件导出 SVG，需要安装 draw.io CLI。

SVG 清理脚本只使用 Python 标准库。

## 测试

```bash
python3 tests/test_fix_drawio_svg.py
```

## 注意事项

已有的 `.docx` 文件不会自动刷新已嵌入的图片。你需要删除文档中的旧图并重新插入处理后的 SVG，或者直接替换 `.docx` 内部的媒体文件。
