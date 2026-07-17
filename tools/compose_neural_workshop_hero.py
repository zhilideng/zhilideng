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
