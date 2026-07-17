import struct
import tempfile
import unittest
from pathlib import Path

from tools.profile_contract import validate_profile


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
    return f"""![Neural Workshop](./assets/neural-workshop/hero.png)

把 AI 想法，做成真正运行的系统

我关注的不是让模型“看起来聪明”，而是让 AI 系统真正可运行、可维护、可评估。

从生产级应用架构、Agent 状态与会话，到高风险场景下的安全评测。
"""


class ProfileContractTests(unittest.TestCase):
    def test_valid_profile_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(valid_readme(), encoding="utf-8")
            write_png_header(root / "assets/neural-workshop/hero.png", 1280, 420)
            write_png_header(root / "assets/neural-workshop/hero-source.png", 1280, 420)

            self.assertEqual(validate_profile(root), [])

    def test_reports_dynamic_cards_missing_intro_copy_and_wrong_size(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad = valid_readme().replace(
                "从生产级应用架构、Agent 状态与会话，到高风险场景下的安全评测。",
                "",
            )
            bad += "\nhttps://github-readme-stats.vercel.app/api?username=zhilideng\n"
            (root / "README.md").write_text(bad, encoding="utf-8")
            write_png_header(root / "assets/neural-workshop/hero.png", 1200, 400)
            write_png_header(root / "assets/neural-workshop/hero-source.png", 1280, 420)

            errors = validate_profile(root)

            self.assertTrue(any("从生产级应用架构" in error for error in errors))
            self.assertTrue(any("动态统计" in error for error in errors))
            self.assertTrue(any("1280x420" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
