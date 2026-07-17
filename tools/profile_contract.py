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
