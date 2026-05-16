from pathlib import Path


async def capture_public_page_screenshot(url: str, output_path: Path) -> Path:
    """Capture a screenshot of a legally accessible public page with Playwright.

    This helper intentionally accepts only caller-provided public URLs and performs no authentication,
    bypass, or stealth behavior.
    """
    from playwright.async_api import async_playwright

    output_path.parent.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 1200})
        await page.goto(url, wait_until="networkidle", timeout=30_000)
        await page.screenshot(path=str(output_path), full_page=True)
        await browser.close()
    return output_path
