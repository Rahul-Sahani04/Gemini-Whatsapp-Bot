from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from undetected_chromedriver import Chrome
from undetected_chromedriver import ChromeOptions


import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

import time
import pickle as pkl
import pyautogui
import re
# import keyboard 

from selenium.webdriver.common.keys import Keys

from PIL import Image
# import requests
import logging

import json

import pyperclip


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)


# Configure the Gemini API
api_key = config['api_key']
genai.configure(api_key=api_key)
# print(HarmCategory)


safety_settings={
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    # HarmCategory.HARM_CATEGORY_VIOLENCE: HarmBlockThreshold.BLOCK_NONE,
    # HarmCategory.HARM_CATEGORY_ILLEGAL: HarmBlockThreshold.BLOCK_NONE,
    # HarmCategory.HARM_CATEGORY_MEDICAL: HarmBlockThreshold.BLOCK_NONE,
    # HarmCategory.HARM_CATEGORY_PERSONAL_ATTACK: HarmBlockThreshold.BLOCK_NONE,
    # HarmCategory.HARM_CATEGORY_PRIVACY_VIOLATION: HarmBlockThreshold.BLOCK_NONE,
    # HarmCategory.HARM_CATEGORY_CHILD_ENDANGERMENT: HarmBlockThreshold.BLOCK_NONE,
    # HarmCategory.HARM_CATEGORY_FALSE_INFORMATION: HarmBlockThreshold.BLOCK_NONE,
    # HarmCategory.HARM_CATEGORY_HOAX: HarmBlockThreshold.BLOCK_NONE,
    # HarmCategory.HARM_CATEGORY_OTHER: HarmBlockThreshold.BLOCK_NONE,
    # HarmCategory.HARM_CATEGORY_TERROR: HarmBlockThreshold.BLOCK_NONE,
}


model = genai.GenerativeModel("gemini-1.5-flash", safety_settings=safety_settings)
person = pkl.load(open("Persons/person.pkl", "rb"))
model = model.start_chat(history=person)

context_messages = []

# Set up ChromeOptions for headless browsing
chrome_options = ChromeOptions()
chrome_options.headless = False

# Add user data directory to keep the session
user_data_dir = "/Users/rsahani/Library/Application Support/Google/Chrome/chrome_whatsapp_profile"
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--allow-running-insecure-content")



# Function to get the last message from WhatsApp Web using Selenium
def get_last_whatsapp_message(driver):
    global context_messages
    last_message = ""
    try:
        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-tab="3"]')))

        time.sleep(5)  # Give some time for messages to load
        print(len(driver.find_elements(By.CSS_SELECTOR, 'div.message-in span.selectable-text')))
        
        # Finding the main div that contains all the messages 
        main_div = driver.find_element(By.CSS_SELECTOR, 'div#main')
        
        # Finding the last message row and then the last message text element within it and if it is not found then it will return False
        # finding elements with role = row and then finding the last element of the list
        
            
        all_messages = main_div.find_elements(By.CSS_SELECTOR, 'div[role="row"]') #[-1].find_elements(By.CSS_SELECTOR, 'span.selectable-text')[-1]
        
        context_messages = ["Context:"]
        # print('All messages: ', len(all_messages))
            
        
        if "message-out" in all_messages[-1].get_attribute("innerHTML"):
            return False
        
        
        last_message_parent = all_messages[-1].find_element(By.CSS_SELECTOR, 'div.message-in')
        
        try:
            last_message = last_message_parent.find_element(By.CSS_SELECTOR, 'span.selectable-text')
            logging.info("Message is a text")
            
            # Get all the incoming messages from the chat
            all_message_in = main_div.find_elements(By.CSS_SELECTOR, 'div.focusable-list-item')
            
            # keep only the last 5 messages
            all_message_in = all_message_in[-5:]
            # print('All messages in: ', len(all_message_in))
            
            
            # extract previous 5 messages to get the context of the message 
            for i in range(1, len(all_message_in)+1):
                try:
                    # context_last_message = all_message_in[i]
                    if all_message_in and i < len(all_message_in):
                        context_last_message = all_message_in[i]
                    else:
                        logging.error("all_message_in is empty or index is out of range")

                    
                    # Extract the name from the message
                    try:
                        # Extract the name from the message
                        name_data = context_last_message.find_element(By.CSS_SELECTOR, 'div.copyable-text').get_attribute("data-pre-plain-text")
                        date_from_name = re.search(r"\[(.*?)\]", name_data)
                        
                        # remove the date from the name
                        name_match = name_data.replace(date_from_name.group(0), "")
                        
                        name = "Rahul  Sahani"
                        if name_match:
                            if name in name_match:
                                name = "Me: "
                            else:
                                name = name_match
                    except Exception as e:
                        name = ""
                        logging.error(f"No element with selector 'div.copyable-text' in message {i}", str(e)    )
                        continue
                    
                    # convert the name to a string and print it
                    # print("Name match: ", name_match)
                            
                        # print("Name:", name)
                        
                    context_messages.append(name + context_last_message.find_element(By.CSS_SELECTOR, 'span.selectable-text').text)

                except Exception as e:
                    logging.error("No more messages becasue of error: ", str(e))
                    break
        except:
            logging.info(" Message is an image")
            last_message = last_message.find_elements(By.CSS_SELECTOR, 'img')[-1]
            # save the image to a file 
            last_message.screenshot("last_message.png")
            img = Image.open("last_message.png")
            return img, True
        return last_message.text, False
    
    except Exception as e:
        logging.error(f"Error fetching last message: {str(e)}")
        return False

# Function to get a reply from Gemini API
def get_gemini_reply(message):
    try:
        # print("\n".join(context_messages) + "\n.The Message to reply to:" + message)
        response = model.send_message("\n".join(context_messages) + "\n.The Message to reply to:" + message, safety_settings=safety_settings)
        # implement a prompt to get the user input to train the model to reply to the messages 
        if 'What should I say?' in response.text or 'GivMeData' in response.text:
            # open a prompt to get the user input from the user 
            response = model.send_message(input("What should I say?"), safety_settings=safety_settings)
            
        return response.text
    except Exception as e:
        return f"Sorry, I couldn't understand that. Error: {str(e)}"
    
# Function to get a reply from Gemini API
def get_image_gemini_reply(message):
    try:
        # print("\n".join(context_messages))
        response = model.send_message([f"{"\n".join(context_messages)}\n- The Message to reply to is the image.", message], safety_settings=safety_settings)
        response.resolve()
        return response.text
    except Exception as e:
        return f"Sorry, I couldn't understand that. Error: {str(e)}"

# Function to send a message using WhatsApp Web
def send_whatsapp_message():
    # pyautogui.write(message)
    # pyperclip.paste()
    
    pyautogui.hotkey('command', 'v', interval=0.1)
    pyautogui.press("enter")
    
def send_whatsapp_message_through_input(driver, message):
    main_div = driver.find_element(By.CSS_SELECTOR, 'div#main')
    input_box = main_div.find_element(By.CSS_SELECTOR, 'div[role="textbox"]')
    input_box.click()
    
    # remove the emojis from the message 
    # message = ''.join([i if ord(i) < 128 else ' ' for i in message])
    logging.info(f"Message to send: {message}")
    
    # send keys to the input box without the emojis 
    input_box.send_keys(Keys.COMMAND + "v")

    send_button = main_div.find_element(By.CSS_SELECTOR, 'button span[data-icon="send"]')
    send_button.click()
    
    


# Main function to combine all functionalities
def main():
    last_message = ""
    last_replied_message = ""  # Track the last message replied to
    
    # Wait for 5 seconds before starting
    # for i in range(5):
    #     print(f"Starting in {5 - i} seconds...")
    #     time.sleep(1)  

    driver = Chrome(options=chrome_options)
    driver.get('https://web.whatsapp.com')
    
    while True:

        # Get the last message from WhatsApp Web
        result = get_last_whatsapp_message(driver)
        if isinstance(result, tuple):
            current_message, isImage = result
        else:
            current_message = result
            isImage = False
        
        logging.info(f"Last message from WhatsApp Web: {current_message}")

        # Check if the current message is the same as the last replied message
        if current_message != last_replied_message and current_message :
            # Get a reply from Gemini API based on the last message
            if isImage:
                gemini_reply = get_image_gemini_reply(current_message)
            else:
                gemini_reply = get_gemini_reply(current_message)
                
            logging.info(f"Reply from Gemini: {gemini_reply}")
            pyperclip.copy(gemini_reply)
            
            with open("person.pkl", "wb") as f:
                person = model.history
                pkl.dump(person, f)

            # Optionally, send a reply back to WhatsApp
            # send_whatsapp_message(gemini_reply)
            send_whatsapp_message_through_input(driver, gemini_reply)

            # Update the last replied message
            last_replied_message = current_message

        time.sleep(2)  # Check for new messages every 5 seconds
    
    driver.quit()
 
 
def banner():
    font = """
██╗    ██╗██╗  ██╗ █████╗ ████████╗███████╗ █████╗ ██████╗ ██████╗     
██║    ██║██║  ██║██╔══██╗╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██╔══██╗    
██║ █╗ ██║███████║███████║   ██║   ███████╗███████║██████╔╝██████╔╝    
██║███╗██║██╔══██║██╔══██║   ██║   ╚════██║██╔══██║██╔═══╝ ██╔═══╝     
╚███╔███╔╝██║  ██║██║  ██║   ██║   ███████║██║  ██║██║     ██║         
 ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝         
                                                                       
██████╗ ███████╗██████╗ ██╗  ██╗   ██╗    ██████╗  ██████╗ ████████╗   
██╔══██╗██╔════╝██╔══██╗██║  ╚██╗ ██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝   
██████╔╝█████╗  ██████╔╝██║   ╚████╔╝     ██████╔╝██║   ██║   ██║      
██╔══██╗██╔══╝  ██╔═══╝ ██║    ╚██╔╝      ██╔══██╗██║   ██║   ██║      
██║  ██║███████╗██║     ███████╗██║       ██████╔╝╚██████╔╝   ██║      
╚═╝  ╚═╝╚══════╝╚═╝     ╚══════╝╚═╝       ╚═════╝  ╚═════╝    ╚═╝      
                                                                       
"""
    print(font)
    
    
def defaultBanner():
    font = """
█████   ███   █████ █████                 █████              █████████                         
░░███   ░███  ░░███ ░░███                 ░░███              ███░░░░░███                        
 ░███   ░███   ░███  ░███████    ██████   ███████    █████  ░███    ░███  ████████  ████████    
 ░███   ░███   ░███  ░███░░███  ░░░░░███ ░░░███░    ███░░   ░███████████ ░░███░░███░░███░░███   
 ░░███  █████  ███   ░███ ░███   ███████   ░███    ░░█████  ░███░░░░░███  ░███ ░███ ░███ ░███   
  ░░░█████░█████░    ░███ ░███  ███░░███   ░███ ███ ░░░░███ ░███    ░███  ░███ ░███ ░███ ░███   
    ░░███ ░░███      ████ █████░░████████  ░░█████  ██████  █████   █████ ░███████  ░███████    
     ░░░   ░░░      ░░░░ ░░░░░  ░░░░░░░░    ░░░░░  ░░░░░░  ░░░░░   ░░░░░  ░███░░░   ░███░░░     
                                                                          ░███      ░███        
                                                                          █████     █████       
                                                                         ░░░░░     ░░░░░        
 ███████████                      ████                ███████████            █████              
░░███░░░░░███                    ░░███               ░░███░░░░░███          ░░███               
 ░███    ░███   ██████  ████████  ░███  █████ ████    ░███    ░███  ██████  ███████             
 ░██████████   ███░░███░░███░░███ ░███ ░░███ ░███     ░██████████  ███░░███░░░███░              
 ░███░░░░░███ ░███████  ░███ ░███ ░███  ░███ ░███     ░███░░░░░███░███ ░███  ░███               
 ░███    ░███ ░███░░░   ░███ ░███ ░███  ░███ ░███     ░███    ░███░███ ░███  ░███ ███           
 █████   █████░░██████  ░███████  █████ ░░███████     ███████████ ░░██████   ░░█████            
░░░░░   ░░░░░  ░░░░░░   ░███░░░  ░░░░░   ░░░░░███    ░░░░░░░░░░░   ░░░░░░     ░░░░░             
                        ░███             ███ ░███                                               
                        █████           ░░██████                                                
                       ░░░░░             ░░░░░░                                                 
    
    """
    print(font)   
       
if __name__ == "__main__":
    defaultBanner()
    main()
