import asyncio
import time
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ScreenshotMixin:
    async def take_screenshot(self, name: str, full_page: bool = False) -> str:
        if not self.page:
            raise RuntimeError("Page not initialized. Call start() first.")

        timestamp = int(time.time() * 1000)
        filename = f"{name}_{timestamp}.png"
        filepath = self.screenshots_dir / filename

        await self.page.screenshot(path=str(filepath), full_page=full_page)

        logger.info(f"Screenshot saved: {filepath}")
        return str(filepath)

    async def take_element_screenshot(self, element, name: str) -> str:
        if not self.page:
            raise RuntimeError("Page not initialized. Call start() first.")

        timestamp = int(time.time() * 1000)
        filename = f"{name}_{timestamp}.png"
        filepath = self.screenshots_dir / filename

        await element.screenshot(path=str(filepath))

        logger.info(f"Element screenshot saved: {filepath}")
        return str(filepath)
