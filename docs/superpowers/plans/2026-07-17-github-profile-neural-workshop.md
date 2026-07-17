# GitHub 个人首页 Neural Workshop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `zhilideng/zhilideng` 的 GitHub Profile README 改造成中文优先、仓库自托管资产、面向技术同行与开源开发者的 Neural Workshop 风格首页。

**Architecture:** 使用一张 `1280 × 420` 的自托管 PNG 作为唯一重视觉资产，正文继续使用 GitHub 原生 Markdown 与安全 HTML。实现分为可重复构建的横幅合成工具、可执行的资料页契约检查、README 内容和真实 GitHub 渲染验收四部分；最终通过非强制快进推送发布到 `main`。

**Tech Stack:** GitHub Profile README、Markdown、GitHub 安全 HTML、PNG、Python 3、Pillow 12.2.0、`unittest`、Codex 内置 Image Generation、Codex in-app Browser。

## Global Constraints

- 主要受众固定为技术同行和开源开发者。
- 正文固定为中文优先；英文只用于技术名词和短视觉标签。
- 首屏固定文字为 `ZhiLi Deng / 邓智立`、`把 AI 想法，做成真正运行的系统`、`AI SYSTEMS / AGENTS / EVALUATION`。
- 首屏最终画布固定为 `1280 × 420` PNG。
- 代表项目固定为 `arch-fastapi`、`agentscope-chat-service`、`medical-ai-safety-evaluation`、`awesome-skills`。
- 不展示 `claude-sdk`，不修改任何代表项目仓库。
- 不使用 GitHub Stats、连续提交、语言占比、访问量或第三方动态统计卡。
- 不公开邮箱、微信、手机号等额外个人联系方式。
- 所有核心视觉资产由 `zhilideng/zhilideng` 仓库自身托管。
- `README.md` 不使用 JavaScript、内联 CSS、外部字体或运行时渲染组件。
- 发布只能使用非强制快进推送；若 `origin/main` 前进，必须先合并远端新提交并重新执行全部验证。

---

## 文件职责

| 文件 | 职责 |
| --- | --- |
| `README.md` | GitHub 个人首页的唯一内容入口 |
| `assets/neural-workshop/hero-source.png` | Image Generation 生成的无文字、无人物视觉底图 |
| `assets/neural-workshop/hero.png` | 叠加真实头像和准确文字后的最终横幅 |
| `tools/compose_neural_workshop_hero.py` | 将底图、头像和固定文案确定性合成为横幅 |
| `tools/profile_contract.py` | 离线验证 README 内容、外部依赖和 PNG 尺寸 |
| `tests/test_compose_neural_workshop_hero.py` | 验证横幅合成尺寸、模式和输出稳定性 |
| `tests/test_profile_contract.py` | 验证资料页契约检查器能够识别有效与无效输入 |

运行图片相关脚本时固定使用 Codex bundled Python：

```bash
PYTHON=/Users/zhili.deng/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
```

---

### Task 1: 建立资料页离线契约检查

**Files:**
- Create: `tools/profile_contract.py`
- Create: `tests/test_profile_contract.py`

**Interfaces:**
- Produces: `read_png_size(path: Path) -> tuple[int, int]`
- Produces: `validate_profile(root: Path) -> list[str]`
- Consumes: 仓库根目录中的 `README.md`、`assets/neural-workshop/hero.png` 和 `assets/neural-workshop/hero-source.png`

- [ ] **Step 1: 编写失败测试**

创建 `tests/test_profile_contract.py`：

```python
import struct
import tempfile
import unittest
from pathlib import Path

from tools.profile_contract import validate_profile


PROJECT_URLS = (
    "https://github.com/zhilideng/arch-fastapi",
    "https://github.com/zhilideng/agentscope-chat-service",
    "https://github.com/zhilideng/medical-ai-safety-evaluation",
    "https://github.com/zhilideng/awesome-skills",
)


def write_png_header(path: Path, width: int, height: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x06\x00\x00\x00"
    )


def valid_readme() -> str:
    project_links = "\n".join(f"- {url}" for url in PROJECT_URLS)
    return f"""![Neural Workshop](./assets/neural-workshop/hero.png)

把 AI 想法，做成真正运行的系统

## 01 / 当前专注
## 02 / 代表系统
{project_links}
## 03 / 技术版图
## 04 / 开源即实践
"""


class ProfileContractTests(unittest.TestCase):
    def test_valid_profile_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(valid_readme(), encoding="utf-8")
            write_png_header(root / "assets/neural-workshop/hero.png", 1280, 420)
            write_png_header(root / "assets/neural-workshop/hero-source.png", 1280, 420)

            self.assertEqual(validate_profile(root), [])

    def test_reports_dynamic_cards_missing_projects_and_wrong_size(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad = valid_readme().replace(PROJECT_URLS[-1], "")
            bad += "\nhttps://github-readme-stats.vercel.app/api?username=zhilideng\n"
            (root / "README.md").write_text(bad, encoding="utf-8")
            write_png_header(root / "assets/neural-workshop/hero.png", 1200, 400)
            write_png_header(root / "assets/neural-workshop/hero-source.png", 1280, 420)

            errors = validate_profile(root)

            self.assertTrue(any("awesome-skills" in error for error in errors))
            self.assertTrue(any("动态统计" in error for error in errors))
            self.assertTrue(any("1280x420" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试并确认按预期失败**

Run:

```bash
$PYTHON -m unittest tests/test_profile_contract.py -v
```

Expected: `ModuleNotFoundError: No module named 'tools.profile_contract'`。

- [ ] **Step 3: 实现最小契约检查器**

创建 `tools/profile_contract.py`：

```python
from __future__ import annotations

import struct
import sys
from pathlib import Path


REQUIRED_FRAGMENTS = (
    "把 AI 想法，做成真正运行的系统",
    "## 01 / 当前专注",
    "## 02 / 代表系统",
    "## 03 / 技术版图",
    "## 04 / 开源即实践",
    "https://github.com/zhilideng/arch-fastapi",
    "https://github.com/zhilideng/agentscope-chat-service",
    "https://github.com/zhilideng/medical-ai-safety-evaluation",
    "https://github.com/zhilideng/awesome-skills",
    "./assets/neural-workshop/hero.png",
)

FORBIDDEN_DYNAMIC_SERVICES = (
    "github-readme-stats",
    "streak-stats",
    "github-profile-trophy",
    "komarev.com/ghpvc",
    "shields.io",
)

EXPECTED_SIZE = (1280, 420)


def read_png_size(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"不是有效 PNG: {path}")
    return struct.unpack(">II", header[16:24])


def validate_profile(root: Path) -> list[str]:
    errors: list[str] = []
    readme = root / "README.md"
    if not readme.exists():
        return ["缺少 README.md"]

    content = readme.read_text(encoding="utf-8")
    for fragment in REQUIRED_FRAGMENTS:
        if fragment not in content:
            errors.append(f"README 缺少必要内容: {fragment}")

    lowered = content.lower()
    for service in FORBIDDEN_DYNAMIC_SERVICES:
        if service in lowered:
            errors.append(f"README 引入了禁止的动态统计服务: {service}")

    for name in ("hero.png", "hero-source.png"):
        path = root / "assets" / "neural-workshop" / name
        if not path.exists():
            errors.append(f"缺少图片资产: {path.relative_to(root)}")
            continue
        try:
            size = read_png_size(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if size != EXPECTED_SIZE:
            errors.append(
                f"{path.relative_to(root)} 尺寸必须为 1280x420，实际为 {size[0]}x{size[1]}"
            )

    return errors


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    errors = validate_profile(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Profile contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: 运行测试并确认通过**

Run:

```bash
$PYTHON -m unittest tests/test_profile_contract.py -v
```

Expected: `Ran 2 tests` 和 `OK`。

- [ ] **Step 5: 提交契约检查器**

```bash
git add tools/profile_contract.py tests/test_profile_contract.py
git commit -m "test: add GitHub profile contract checks"
```

---

### Task 2: 生成并确定性合成 Neural Workshop 横幅

**Files:**
- Create: `tools/compose_neural_workshop_hero.py`
- Create: `tests/test_compose_neural_workshop_hero.py`
- Create: `assets/neural-workshop/hero-source.png`
- Create: `assets/neural-workshop/hero.png`

**Interfaces:**
- Produces: `build_hero(background_path: Path, avatar_path: Path, output_path: Path) -> None`
- Consumes: `1280 × 420` 或更大的 RGB/RGBA 背景图、可读取的头像图片
- Produces: `1280 × 420` RGB PNG，固定包含头像和三段已批准文案

- [ ] **Step 1: 编写横幅合成失败测试**

创建 `tests/test_compose_neural_workshop_hero.py`：

```python
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from tools.compose_neural_workshop_hero import build_hero


class ComposeHeroTests(unittest.TestCase):
    def test_build_hero_outputs_expected_png(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            background = root / "background.png"
            avatar = root / "avatar.png"
            output = root / "hero.png"
            Image.new("RGB", (1600, 900), "#0B1526").save(background)
            Image.new("RGB", (460, 460), "#E8F7FF").save(avatar)

            build_hero(background, avatar, output)

            with Image.open(output) as image:
                self.assertEqual(image.size, (1280, 420))
                self.assertEqual(image.mode, "RGB")
                self.assertEqual(image.format, "PNG")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试并确认按预期失败**

Run:

```bash
$PYTHON -m unittest tests/test_compose_neural_workshop_hero.py -v
```

Expected: `ModuleNotFoundError: No module named 'tools.compose_neural_workshop_hero'`。

- [ ] **Step 3: 实现横幅合成器**

创建 `tools/compose_neural_workshop_hero.py`：

```python
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


WIDTH = 1280
HEIGHT = 420
FONT_CJK = Path("/System/Library/Fonts/Hiragino Sans GB.ttc")
FONT_MONO = Path("/System/Library/Fonts/Menlo.ttc")


def font(path: Path, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size, index=index)


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(image.convert("RGB"), size, method=Image.Resampling.LANCZOS)


def circular_avatar(image: Image.Image, size: int) -> Image.Image:
    avatar = ImageOps.fit(image.convert("RGB"), (size, size), method=Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    output.paste(avatar, (0, 0), mask)
    return output


def build_hero(background_path: Path, avatar_path: Path, output_path: Path) -> None:
    with Image.open(background_path) as source:
        canvas = cover(source, (WIDTH, HEIGHT)).convert("RGBA")

    shade = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    for x in range(820):
        alpha = max(20, int(210 * (1 - x / 820)))
        shade_draw.line((x, 0, x, HEIGHT), fill=(3, 9, 18, alpha))
    canvas = Image.alpha_composite(canvas, shade)

    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((936, 48, 1224, 336), fill=(103, 232, 249, 95))
    glow = glow.filter(ImageFilter.GaussianBlur(34))
    canvas = Image.alpha_composite(canvas, glow)

    with Image.open(avatar_path) as avatar_source:
        avatar = circular_avatar(avatar_source, 226)
    ring = Image.new("RGBA", (242, 242), (0, 0, 0, 0))
    ring_draw = ImageDraw.Draw(ring)
    ring_draw.ellipse((2, 2, 239, 239), fill=(8, 18, 31, 235), outline=(103, 232, 249, 255), width=4)
    canvas.alpha_composite(ring, (958, 88))
    canvas.alpha_composite(avatar, (966, 96))

    draw = ImageDraw.Draw(canvas)
    draw.text((72, 62), "OPEN SOURCE AI ENGINEER", font=font(FONT_MONO, 20), fill="#67E8F9", spacing=4)
    draw.text((72, 104), "ZhiLi Deng / 邓智立", font=font(FONT_CJK, 47), fill="#E8F7FF")
    draw.text((72, 182), "把 AI 想法，做成真正运行的系统", font=font(FONT_CJK, 38), fill="#FFFFFF")
    draw.rounded_rectangle((72, 257, 686, 318), radius=12, fill=(4, 12, 23, 205), outline=(103, 232, 249, 75), width=2)
    draw.text((94, 274), "AI SYSTEMS / AGENTS / EVALUATION", font=font(FONT_MONO, 20), fill="#A5B4FC")
    draw.text((72, 353), "github.com/zhilideng", font=font(FONT_MONO, 16), fill="#91A4BA")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path, format="PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--background", type=Path, required=True)
    parser.add_argument("--avatar", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    build_hero(args.background, args.avatar, args.out)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 运行合成器单元测试**

Run:

```bash
$PYTHON -m unittest tests/test_compose_neural_workshop_hero.py -v
```

Expected: `Ran 1 test` 和 `OK`。

- [ ] **Step 5: 生成无文字、无人物的横幅底图**

使用 Codex 内置 Image Generation，参考已批准的 Neural Workshop 选稿，输入以下完整提示词：

```text
Use case: stylized-concept
Asset type: GitHub profile README hero background
Primary request: Create a premium futuristic AI engineering workshop background for a Chinese open-source developer profile.
Scene/backdrop: deep navy technical laboratory atmosphere with a restrained perspective grid, sparse glowing cyan nodes, subtle violet energy haze, and a few elegant connection lines suggesting models, agents, and evaluation pipelines.
Style/medium: polished high-resolution digital environment art, minimal, precise, sophisticated, credible engineering mood.
Composition/framing: exact 1280 x 420 wide banner; keep the left 70% calm and dark with generous negative space for typography; place the strongest cyan-violet glow and visual detail on the right 30% behind an avatar area.
Lighting/mood: dark, controlled, futuristic, confident, not aggressive.
Color palette: #06111B, #0B1526, #67E8F9, #A5B4FC, #7C3AED.
Constraints: no people, no faces, no avatars, no logos, no readable text, no letters, no numbers, no code snippets, no UI panels, no watermark; no busy circuit-board cliché; preserve clean negative space.
Avoid: cyberpunk city, gaming poster, neon overload, stock HUD, random glyphs, lens flare across the text area.
```

将内置工具返回的实际生成文件复制为 `assets/neural-workshop/hero-source.png`，然后统一归一到准确尺寸：

```bash
$PYTHON -c 'from pathlib import Path; from PIL import Image,ImageOps; p=Path("assets/neural-workshop/hero-source.png"); image=Image.open(p).convert("RGB"); ImageOps.fit(image,(1280,420),method=Image.Resampling.LANCZOS).save(p,"PNG",optimize=True)'
```

Expected: `hero-source.png` 为 `1280 × 420` RGB PNG，只发生居中裁切和等比缩放，不拉伸画面。

- [ ] **Step 6: 下载当前公开头像到临时路径并合成最终横幅**

Run:

```bash
$PYTHON -c 'from pathlib import Path; from urllib.request import urlopen; Path("/tmp/zhilideng-avatar.png").write_bytes(urlopen("https://avatars.githubusercontent.com/u/44140641?v=4").read())'
$PYTHON tools/compose_neural_workshop_hero.py \
  --background assets/neural-workshop/hero-source.png \
  --avatar /tmp/zhilideng-avatar.png \
  --out assets/neural-workshop/hero.png
```

Expected: 生成 `assets/neural-workshop/hero.png`，尺寸 `1280 × 420`。

- [ ] **Step 7: 打开并人工核对横幅**

用图片查看工具检查：

- 姓名完整显示为 `ZhiLi Deng / 邓智立`。
- 主标题完整显示为 `把 AI 想法，做成真正运行的系统`。
- 英文标签完整显示为 `AI SYSTEMS / AGENTS / EVALUATION`。
- 头像没有变形，脸部没有被裁切。
- 左侧文字与背景对比清晰，右侧发光不覆盖头像。
- 所有内容距离画布边缘至少 `48px`。

- [ ] **Step 8: 提交横幅工具和资产**

```bash
git add tools/compose_neural_workshop_hero.py tests/test_compose_neural_workshop_hero.py assets/neural-workshop/hero-source.png assets/neural-workshop/hero.png
git commit -m "feat: add Neural Workshop profile hero"
```

---

### Task 3: 用真实项目内容重写 Profile README

**Files:**
- Modify: `README.md`
- Test: `tools/profile_contract.py`
- Test: `tests/test_profile_contract.py`

**Interfaces:**
- Consumes: `./assets/neural-workshop/hero.png`
- Produces: GitHub Profile 首页结构与四个稳定项目入口

- [ ] **Step 1: 在修改前运行契约检查并确认失败**

Run:

```bash
$PYTHON tools/profile_contract.py .
```

Expected: 非零退出码，并报告缺少横幅引用、必要章节和代表项目链接。

- [ ] **Step 2: 将 `README.md` 替换为已批准内容**

使用以下完整内容：

````markdown
<div align="center">
  <img src="./assets/neural-workshop/hero.png" alt="ZhiLi Deng 的 Neural Workshop：把 AI 想法，做成真正运行的系统" width="100%" />
</div>

<br />

<div align="center">
  <strong>我关注的不是让模型“看起来聪明”，而是让 AI 系统真正可运行、可维护、可评估。</strong>
  <br />
  <sub>从生产级应用架构、Agent 状态与会话，到高风险场景下的安全评测。</sub>
</div>

## 01 / 当前专注

```text
$ current_focus

● 生产级 AI 应用架构
● Agent 会话、状态与持久化
● 大模型与智能体安全评测
● 可复用 Skill 与开发工具
```

## 02 / 代表系统

<table>
  <tr>
    <td width="50%" valign="top">
      <h3><a href="https://github.com/zhilideng/arch-fastapi">arch-fastapi</a></h3>
      <p>面向 AI Agent 应用的生产化 FastAPI 后端脚手架。</p>
      <p><code>Python</code> <code>FastAPI</code> <code>LLM Gateway</code> <code>Milvus</code></p>
    </td>
    <td width="50%" valign="top">
      <h3><a href="https://github.com/zhilideng/agentscope-chat-service">agentscope-chat-service</a></h3>
      <p>支持流式对话、状态恢复和会话隔离的通用会话 Agent MVP。</p>
      <p><code>Java</code> <code>Spring Boot</code> <code>AgentScope</code> <code>PostgreSQL</code></p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3><a href="https://github.com/zhilideng/medical-ai-safety-evaluation">medical-ai-safety-evaluation</a></h3>
      <p>医疗大模型与智能体全生命周期安全评测基线。</p>
      <p><code>Medical AI</code> <code>Agent Safety</code> <code>Evaluation</code></p>
    </td>
    <td width="50%" valign="top">
      <h3><a href="https://github.com/zhilideng/awesome-skills">awesome-skills</a></h3>
      <p>个人原创与开源 Skill 的 Plugin Marketplace。</p>
      <p><code>Agent Skills</code> <code>Plugins</code> <code>Open Source</code></p>
    </td>
  </tr>
</table>

## 03 / 技术版图

`Python` · `Java` · `FastAPI` · `Spring Boot` · `AgentScope` · `LLM` · `RAG` · `Milvus` · `PostgreSQL`

## 04 / 开源即实践

我希望把真实项目中反复出现的问题，沉淀成可以复用、验证和继续演进的工程资产。

如果某个项目与你正在解决的问题有关，欢迎进入对应仓库，通过 Issue 交流具体场景与想法。
````

- [ ] **Step 3: 运行全部离线验证**

Run:

```bash
$PYTHON -m unittest discover -s tests -v
$PYTHON tools/profile_contract.py .
git diff --check
```

Expected:

- `Ran 3 tests` 和 `OK`。
- `Profile contract: PASS`。
- `git diff --check` 无输出，退出码为 `0`。

- [ ] **Step 4: 人工核对 README 文案与链接**

逐项确认：

- `claude-sdk` 没有出现在 README。
- 四个项目的描述与各自公开 README 一致。
- 不存在 Stars、访问量、连续提交或语言占比。
- 不存在邮箱、微信或手机号。
- 不存在 `TBD`、`TODO`、空链接或无效锚点。

- [ ] **Step 5: 提交 README**

```bash
git add README.md
git commit -m "feat: redesign GitHub profile as Neural Workshop"
```

---

### Task 4: 在真实 GitHub 渲染中完成视觉验收

**Files:**
- Modify if needed: `README.md`
- Modify if needed: `assets/neural-workshop/hero.png`

**Interfaces:**
- Consumes: Task 2 的横幅和 Task 3 的 README
- Produces: 已在 GitHub 分支页面验证的桌面与移动端视觉结果

- [ ] **Step 1: 重新执行完整验证并确认工作树干净**

Run:

```bash
$PYTHON -m unittest discover -s tests -v
$PYTHON tools/profile_contract.py .
git diff --check
git status --short
```

Expected: 测试与契约检查通过；`git status --short` 无输出。

- [ ] **Step 2: 推送实现分支用于 GitHub 原生渲染预览**

```bash
git push -u origin codex/neural-workshop-profile
```

Expected: 远端分支创建成功。此操作不改变线上个人首页，因为默认分支仍为 `main`。

- [ ] **Step 3: 捕获桌面端 GitHub 分支页面**

使用 Codex in-app Browser 打开：

```text
https://github.com/zhilideng/zhilideng/tree/codex/neural-workshop-profile
```

使用约 `1280px` 宽视口捕获完整 README 区域。检查：

- 横幅按主内容区宽度缩放，没有横向滚动。
- 头像、中文姓名和主标题清晰。
- 两列项目表格边界、内边距和换行自然。
- 段落长度没有形成难读的宽行。

将截图保存为 `/tmp/neural-workshop-github-desktop.png`，供 Step 6 进行同屏比较。

- [ ] **Step 4: 捕获移动端 GitHub 分支页面**

将同一页面视口改为约 `390 × 844` 后重新截图。检查：

- 横幅缩放后仍能辨认主标题和头像。
- 项目区域没有被截断或超出视口。
- 行内技术标签允许自然换行。
- 没有小于可辨认程度的正文。

将截图保存为 `/tmp/neural-workshop-github-mobile.png`。

- [ ] **Step 5: 检查深色与浅色背景兼容性**

在视觉伴侣中建立一个双背景检查页，页面片段固定为：

```html
<h2>Neural Workshop 深浅色背景检查</h2>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px">
  <figure style="margin:0;padding:24px;background:#ffffff">
    <img src="/files/hero.png" alt="浅色背景横幅检查" style="display:block;width:100%" />
  </figure>
  <figure style="margin:0;padding:24px;background:#0d1117">
    <img src="/files/hero.png" alt="深色背景横幅检查" style="display:block;width:100%" />
  </figure>
</div>
```

将 `assets/neural-workshop/hero.png` 作为视觉伴侣文件资产提供给 `/files/hero.png`。确认横幅自身深色边界在两种背景上都完整，浅色主题不出现透明边缘，深色主题不丢失外轮廓。

- [ ] **Step 6: 将选稿与实现截图并排比较**

使用 bundled Python 和 Pillow 将已批准的 `visual-style-preview-v2.png` 与桌面端实现截图横向拼接为临时比较图：

```bash
$PYTHON -c 'from PIL import Image,ImageOps; from pathlib import Path; a=Image.open("../visual-style-preview-v2.png").convert("RGB"); b=Image.open("/tmp/neural-workshop-github-desktop.png").convert("RGB"); h=max(a.height,b.height); a=ImageOps.pad(a,(a.width,h),color="white"); b=ImageOps.pad(b,(b.width,h),color="white"); out=Image.new("RGB",(a.width+b.width,h),"white"); out.paste(a,(0,0)); out.paste(b,(a.width,0)); out.save("/tmp/neural-workshop-comparison.png")'
```

打开比较图，确认实现保留了选稿的深蓝、青色、紫色、系统感和项目优先级，同时没有把整页伪装成不能落地的自定义网页。

- [ ] **Step 7: 修正可见问题并重复验收**

只针对截图中实际出现的问题修改 `README.md` 或重新合成 `hero.png`。每次修改后重新执行：

```bash
$PYTHON -m unittest discover -s tests -v
$PYTHON tools/profile_contract.py .
git diff --check
```

若发生修改，提交：

```bash
git add README.md assets/neural-workshop/hero.png
git commit -m "fix: polish Neural Workshop profile rendering"
git push
```

若没有修改，不创建空提交。

---

### Task 5: 非强制发布到 GitHub 默认分支并验证线上首页

**Files:**
- Publish: `README.md`
- Publish: `assets/neural-workshop/hero-source.png`
- Publish: `assets/neural-workshop/hero.png`
- Publish: `tools/compose_neural_workshop_hero.py`
- Publish: `tools/profile_contract.py`
- Publish: `tests/test_compose_neural_workshop_hero.py`
- Publish: `tests/test_profile_contract.py`
- Publish: `docs/superpowers/specs/2026-07-17-github-profile-neural-workshop-design.md`
- Publish: `docs/superpowers/plans/2026-07-17-github-profile-neural-workshop.md`

**Interfaces:**
- Consumes: 通过 Task 4 真实 GitHub 渲染验收的分支
- Produces: `https://github.com/zhilideng` 上立即生效的 Neural Workshop 首页

- [ ] **Step 1: 获取远端最新状态并阻止并发覆盖**

Run:

```bash
git fetch origin main
git merge-base --is-ancestor origin/main HEAD
```

在 `git fetch` 后记录回退点：

```bash
mkdir -p .superpowers/sdd
git rev-parse origin/main > .superpowers/sdd/previous-main
PREVIOUS_MAIN=$(cat .superpowers/sdd/previous-main)
```

Expected: `git merge-base` 退出码为 `0`。若退出码为 `1`，执行：

```bash
git merge --no-edit origin/main
$PYTHON -m unittest discover -s tests -v
$PYTHON tools/profile_contract.py .
git diff --check
git push origin codex/neural-workshop-profile
```

禁止对实现分支或 `main` 使用任何 force 选项。合并后必须重新完成 Task 4 的桌面端截图检查，再继续发布。

- [ ] **Step 2: 确认最后提交和工作树状态**

Run:

```bash
git status --short --branch
git log --oneline --decorate -5
```

Expected: 工作树无未提交文件；HEAD 位于 `codex/neural-workshop-profile`，最新提交已经推送到同名远端分支。

- [ ] **Step 3: 使用非强制快进推送发布到 `main`**

Run:

```bash
git push origin HEAD:main
```

Expected: `main` 快进到已验证提交。若远端拒绝推送，停止，不使用 force；回到 Step 1 获取并处理新的远端提交。

- [ ] **Step 4: 验证线上 README 与本地提交一致**

Run:

```bash
git fetch origin main
git rev-parse HEAD
git rev-parse origin/main
git hash-object README.md
```

Expected: 前两个提交 SHA 完全一致。通过 GitHub 读取 `zhilideng/zhilideng` 默认分支 `README.md` 的 blob SHA，并确认与 `git hash-object README.md` 输出一致。

记录发布提交：

```bash
git rev-parse origin/main > .superpowers/sdd/published-main
PUBLISHED_MAIN=$(cat .superpowers/sdd/published-main)
```

- [ ] **Step 5: 捕获并检查真实个人首页**

使用 Codex in-app Browser 打开：

```text
https://github.com/zhilideng
```

捕获桌面端完整页面，确认：

- Neural Workshop 横幅出现在 Profile README 首屏。
- 四个项目链接和内容区全部可见。
- 页面没有加载失败图标、断链或第三方统计错误。
- GitHub 热门仓库区域仍正常显示，没有被 README 布局影响。

- [ ] **Step 6: 记录发布结果与回退点**

在交付说明中记录：

- 发布前 `main` 提交：读取 `.superpowers/sdd/previous-main` 中的实际完整 SHA。
- 发布后 `main` 提交：读取 `.superpowers/sdd/published-main` 中的实际完整 SHA。
- 回退方式：先执行 `PREVIOUS_MAIN=$(cat .superpowers/sdd/previous-main)`，再执行 `git revert --no-commit "$PREVIOUS_MAIN"..origin/main`，检查差异后执行 `git commit -m "revert: restore previous GitHub profile"` 与 `git push origin HEAD:main`；禁止 `git reset --hard` 和对 `main` 强制推送。

最终回复必须提供线上首页链接、验证摘要和实际发布提交 SHA。
