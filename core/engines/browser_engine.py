import asyncio
import time
import json
import random
from typing import Optional, Dict, Any, List
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from django.conf import settings
import logging

from core.engines.screenshot_manager import ScreenshotMixin
from core.engines.element_locator import ElementLocatorMixin
from core.engines.action_executor import ActionExecutorMixin

logger = logging.getLogger(__name__)


class PlaywrightEngine(ScreenshotMixin, ElementLocatorMixin, ActionExecutorMixin):
    def __init__(
        self,
        headless: bool = None,
        timeout: int = None,
        slow_mo: int = None,
        screenshots_dir: Path = None,
        global_config: Dict[str, Any] = None,
    ):
        self.headless = headless if headless is not None else settings.PLAYWRIGHT_HEADLESS
        self.timeout = timeout if timeout is not None else settings.PLAYWRIGHT_TIMEOUT
        self.slow_mo = slow_mo if slow_mo is not None else settings.PLAYWRIGHT_SLOW_MO
        self.screenshots_dir = screenshots_dir or settings.SCREENSHOTS_DIR
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.global_config = global_config or {}

        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None

    async def start(self, browser_type: str = 'chromium', **context_options):
        self.playwright = await async_playwright().start()

        browser_launcher = getattr(self.playwright, browser_type)
        self.browser = await browser_launcher.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
        )

        viewport_width = self.global_config.get('viewport_width', 1920) if self.global_config else 1920
        viewport_height = self.global_config.get('viewport_height', 1080) if self.global_config else 1080
        default_context_options = {
            'viewport': {'width': viewport_width, 'height': viewport_height},
            'locale': 'zh-CN',
            'timezone_id': 'Asia/Shanghai',
        }
        default_context_options.update(context_options)

        self.context = await self.browser.new_context(**default_context_options)
        self.context.set_default_timeout(self.timeout)

        self.page = await self.context.new_page()

        logger.info(f"Playwright engine started with {browser_type}")
        return self.page

    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

        logger.info("Playwright engine closed")


class PlaywrightSync:
    @staticmethod
    def run_async(coro):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(coro)
