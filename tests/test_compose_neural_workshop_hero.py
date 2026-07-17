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
