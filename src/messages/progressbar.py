from __future__ import annotations
from discord.ext.commands import Context
from discord import Embed, Colour, File

import PIL.Image as PILImage
import PIL.ImageDraw as PILImageDraw
import PIL.ImageFont as PILImageFont
import io


class ProgressBar:
    def __init__(self, ctx: Context, title: str, total: int):
        self._ctx = ctx
        self._title = title
        self._progress = 0
        self._total = total

    async def progress(self):
        self._progress += 1
        await self._message.edit(attachments=[self._generate_attachment()])

    async def __aenter__(self) -> ProgressBar:
        self._message = await self._ctx.send(files=[self._generate_attachment()])
        return self

    async def __aexit__(self, *_):
        await self._message.delete(delay=2)

    def _generate_image(self) -> io.BytesIO:
        with PILImage.open("./assets/loadingbackground.jpg") as image:
            width, height = image.size

            draw = PILImageDraw.Draw(image)

            # Draw Progress Bar
            bar_height = 20
            bar_width = 180
            bar_pos = (3 * width / 5, 3 * height / 5)

            # Background Rectangle
            background_color = (21, 2, 30)
            start_pos = (bar_pos[0] + bar_height / 2, bar_pos[1])
            end_pos = (start_pos[0] + bar_width - bar_height, start_pos[1] + bar_height)
            draw.rectangle((start_pos, end_pos), fill=background_color)

            # Background Circle
            start_pos = (end_pos[0] - bar_height / 2, bar_pos[1])
            end_pos = (start_pos[0] + bar_height, start_pos[1] + bar_height)
            draw.ellipse((start_pos, end_pos), fill=background_color)

            # Progress Start Circle
            progress_ratio = self._progress / self._total
            progress_color = (117, 2, 71)
            start_pos = bar_pos
            end_pos = (start_pos[0] + bar_height, start_pos[1] + bar_height)
            draw.ellipse((start_pos, end_pos), fill=progress_color)

            # Progress Rectangle
            start_pos = (bar_pos[0] + bar_height / 2, bar_pos[1])
            end_pos = (start_pos[0] + (bar_width - bar_height)
                       * progress_ratio, start_pos[1] + bar_height)
            draw.rectangle((start_pos, end_pos), fill=progress_color)

            # Progress End Circle
            if self._progress == self._total:
                start_pos = (bar_pos[0] + bar_width - bar_height, bar_pos[1])
                end_pos = (start_pos[0] + bar_height, start_pos[1] + bar_height)
                draw.ellipse((start_pos, end_pos), fill=progress_color)

            # Draw Progress Text
            font_size = 45
            font = PILImageFont.truetype("./assets/norwester.otf", font_size)
            text = f"{self._progress} / {self._total}"
            pos = (bar_pos[0] + bar_width * 9 / 40,
                   bar_pos[1] - 6 * bar_height / 2)
            draw.text(pos, text, font=font, fill="white", align="center")

            image_bytes = io.BytesIO()
            image.save(image_bytes, format="PNG")

        image_bytes.seek(0)
        return image_bytes

    def _generate_attachment(self) -> File:
        return File(self._generate_image(), filename="progressbar.png")
