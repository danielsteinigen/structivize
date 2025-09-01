import asyncio
import os
from pathlib import Path

from playwright.async_api import async_playwright


async def export_markmap(path: str, width: int, height: int):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={"width": width, "height": height})
        page = await context.new_page()
        # await page.goto(Path(f"{path}.html").resolve())
        path_abs = os.path.abspath(path)
        await page.goto(f"file://{path_abs}.html")
        await page.add_style_tag(
            content="""
@import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');
svg * {
    font-family: 'Roboto', sans-serif !important;
}
"""
        )

        # Wait for the SVG to load
        await page.wait_for_selector("svg")
        await page.wait_for_timeout(500)

        # Export SVG
        svg_content = await page.eval_on_selector("svg", "el => el.outerHTML")

        svg_content = svg_content.replace("<svg", f'<svg width="{width}" height="{height}"', 1).replace(
            "<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1
        )

        with open(f"{path_abs}_2.svg", "w", encoding="utf-8") as f:
            f.write(svg_content)

        # Export PNG
        element = await page.query_selector("svg")
        box = await element.bounding_box()
        await page.screenshot(path=f"{path_abs}.png", clip=box)

        await browser.close()

