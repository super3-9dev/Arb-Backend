#!/usr/bin/env python3
"""
Simple script to verify Playwright installation and browser availability
"""
import os
import sys
from playwright.sync_api import sync_playwright


def main():
    print("=== Playwright Verification Script ===")

    # Check environment
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")

    # Check Playwright installation
    try:
        from playwright import __version__

        print(f"Playwright version: {__version__}")
    except ImportError as e:
        print(f"ERROR: Playwright not installed: {e}")
        return False

    # Check browser availability
    try:
        with sync_playwright() as p:
            print("✓ Playwright context created successfully")

            # Try to launch browser
            browser = p.chromium.launch(headless=True)
            print("✓ Chromium browser launched successfully")

            # Create a page
            page = browser.new_page()
            print("✓ Page created successfully")

            # Navigate to a simple page
            page.goto("data:text/html,<h1>Hello World</h1>")
            title = page.title()
            print(f"✓ Page loaded successfully, title: {title}")

            # Close browser
            browser.close()
            print("✓ Browser closed successfully")

            return True

    except Exception as e:
        print(f"ERROR: Failed to launch browser: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ All Playwright checks passed!")
        sys.exit(0)
    else:
        print("\n❌ Playwright verification failed!")
        sys.exit(1)
