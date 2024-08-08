# WhatsApp Reply Bot README

## Overview

This WhatsApp Reply Bot is a Python-based automation script that uses Selenium to interact with WhatsApp Web and Google Gemini API to generate automated replies to incoming messages. The bot is designed to run continuously, monitoring for new messages and replying in real-time.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Bot](#running-the-bot)
5. [Code Explanation](#code-explanation)
6. [Libraries Used](#libraries-used)
7. [Common Issues](#common-issues)
8. [References](#references)

## Prerequisites

Before running the bot, ensure you have the following installed on your system:

1. Python 3.x
2. Google Chrome browser
3. ChromeDriver compatible with your Chrome version
4. A Google Gemini API key

## Installation

1. Clone the repository or download the script file.

2. Install the required Python libraries using `pip`:

    ```bash
    pip install selenium undetected-chromedriver google-generativeai pyautogui pyperclip logging Pillow
    ```

## Configuration

### Google Gemini API

1. **API Key**: Obtain your API key from Google Gemini and replace the placeholder in the script.

### Chrome Profile

1. **User Data Directory**: Modify the `user_data_dir` path in the `setup_chrome_options` function to point to your Chrome user data directory. This allows the bot to use your existing WhatsApp Web session.

## Running the Bot

1. Ensure all configurations are set correctly.
2. Run the script:

    ```bash
    python whatsapp_reply_bot.py
    ```

## Code Explanation

### Libraries and Imports

- **Selenium**: Used for browser automation.
- **Undetected ChromeDriver**: To avoid detection as a bot.
- **Google Generative AI**: For generating replies.
- **PyAutoGUI**: For UI automation.
- **Pyperclip**: For clipboard management.
- **Logging**: For logging events.

### Functions

#### `configure_genai(api_key)`

Configures the Google Gemini API with the provided API key and safety settings.

#### `setup_chrome_options()`

Sets up Chrome options for the WebDriver, including headless browsing and user data directory configuration.

#### `get_last_whatsapp_message(driver)`

Fetches the last received message from WhatsApp Web.

#### `get_gemini_reply(model, message, safety_settings)`

Generates a reply using the Google Gemini API based on the last received message.

#### `send_whatsapp_message_through_input(driver, message)`

Sends a reply message through the WhatsApp Web interface using Selenium.

#### `main(api_key)`

The main function that combines all functionalities. It initializes configurations, launches the browser, and enters a loop to check for new messages and send replies.

### Example Run

```python
if __name__ == "__main__":
    banner()
    api_key = "your_gemini_api_key_here"
    main(api_key)
```

## Libraries Used

1. **Selenium**: For browser automation.
   - `By`, `WebDriverWait`, `expected_conditions` from `selenium.webdriver.common` and `selenium.webdriver.support`.
2. **Undetected ChromeDriver**: To avoid detection.
   - `Chrome`, `ChromeOptions` from `undetected_chromedriver`.
3. **Google Generative AI**: For generating AI-based replies.
   - `google.generativeai` and related types.
4. **PyAutoGUI**: For automating GUI interactions.
5. **Pyperclip**: For clipboard operations.
6. **Logging**: For detailed logging and debugging.

## Common Issues

1. **ChromeDriver Version Mismatch**: Ensure ChromeDriver version matches your Chrome browser version.
2. **WhatsApp Web Login**: Make sure you are logged into WhatsApp Web on the user profile specified.
3. **API Key Errors**: Verify your Google Gemini API key and permissions.

## References

- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Undetected ChromeDriver GitHub](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
- [Google Generative AI Documentation](https://developers.google.com/generative-ai)
- [PyAutoGUI Documentation](https://pyautogui.readthedocs.io/)
- [Pyperclip Documentation](https://pyperclip.readthedocs.io/)

---

This README should guide you through the setup, configuration, and execution of the WhatsApp Reply Bot. Make sure to follow each step carefully to ensure smooth operation.