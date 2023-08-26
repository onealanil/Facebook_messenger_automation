import tkinter as tk
from tkinter import Label, Entry, Button, StringVar
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chatterbot import ChatBot
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from chatterbot.trainers import ChatterBotCorpusTrainer
import os
import time
import threading
import sys


def update_progress_bar(description, iteration_counter, total_items, progress_bar_length):
    percent = iteration_counter / total_items
    hashes = '#' * int(round(percent * progress_bar_length))
    spaces = ' ' * (progress_bar_length - len(hashes))
    
    def update_text_widget():
        gui_text.delete('1.0', tk.END)
        gui_text.insert(tk.END, f"{description}: [{hashes + spaces}] {int(round(percent * 100))}% completed")
    
    gui_text.after(0, update_text_widget)
    
    if total_items == iteration_counter:
        gui_text.after(0, lambda: gui_text.insert(tk.END, '\nTraining completed!'))

        
def redirect_stdout(widget):
    class StdoutRedirect:
        def __init__(self, widget):
            self.widget = widget

        def write(self, text):
            self.widget.insert(tk.END, text)
            self.widget.see(tk.END)  # Scroll to the end of the widget

        def flush(self):
            pass

    sys.stdout = StdoutRedirect(widget)

def start_selenium_chatbot():
    # Initialize the chatbot and trainer within this thread
    chatbot = ChatBot('Anil')
    trainer = ChatterBotCorpusTrainer(chatbot)
    current_directory = "./data/"
    for idx, filename in enumerate(os.listdir(current_directory)):
        if filename.endswith('.yml'):
            file_path = os.path.join(current_directory, filename)
            trainer.train(file_path)
            # Update the progress bar
            update_progress_bar("Training", idx + 1, len(os.listdir(current_directory)), 50)

    option = Options()

    option.add_argument("--disable-notifications")
    option.add_experimental_option('detach', True)
    driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()), options= option)
    driver.get("https://facebook.com/messages/t")
    driver.maximize_window()
    driver.find_element("id", "email").send_keys(email.get())
    driver.find_element("id", "pass").send_keys(password.get())
    driver.find_element(By.NAME, "login").click()
    
    redirect_stdout(gui_text)
    
    print("Sucessfully LoggedIn...(40 sec)")
    time.sleep(40)
    
    input_box = driver.find_element(
      By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[2]/div/div/div/div/div/label/input')

    input_box.send_keys(friendName.get())
    
    print("Searching Friend "+ friendName.get())
    time.sleep(15)

    selected_account = driver.find_element(
     By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[2]/div/div/div[1]/div[1]/div/div[1]/ul/li[1]/ul/div[2]/li/div/a/div/div[2]/div/div/span/span/span')
    selected_account.click()
 
    print("Selecting and Writing First Message: Hello")
    time.sleep(40)

    def chatBotResponse(question):
        print("Bot is checking for reply .....")
        bot_response = chatbot.get_response(question)
        return bot_response
    
    
    msg_box = driver.find_element(
     By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div/div[4]/div[2]/div/div/div[1]/p')
    msg_box.send_keys("hello!!")
    msg_box.send_keys(Keys.RETURN)

    time.sleep(4)
    
    wait = WebDriverWait(driver, 30)  # Maximum wait time of 10 seconds
    element = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//div[contains(@class, "x6prxxf x1fc57z9 x1yc453h x126k92a xzsf02u")]')))
    elements = driver.find_elements(
        By.XPATH, '//div[contains(@class, "x6prxxf x1fc57z9 x1yc453h x126k92a xzsf02u")]')
    
    counter = len(elements) 
    
    print("Waiting 40 sec to, receive message .... ")
    time.sleep(40)
    
    
    
    def send_message(message):
        try:
            msg_box = driver.find_element(
                By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div/div[4]/div[2]/div/div/div[1]/p')
            msg_box.send_keys(str(message))
            msg_box.send_keys(Keys.RETURN)
    
        except StaleElementReferenceException:
            # Handle StaleElementReferenceException by re-finding the element
            print("Stale element reference encountered. Re-finding the element and retrying...")
            send_message(message)
            
    
    def check_reply(prev_counter, prev_message):
        if counter > prev_counter:
            elements = driver.find_elements(
                By.XPATH, '//div[contains(@class, "x6prxxf x1fc57z9 x1yc453h x126k92a xzsf02u")]')
            message_after_chat = elements[-1].text
            print("This is the last message:", message_after_chat)
            
            if message_after_chat != prev_message:
                ans = chatBotResponse(message_after_chat)
                print("ChatBot has sent the response:", ans)
                time.sleep(3)
                send_message(ans)
    
            return message_after_chat
    
        return prev_message
    
    prev_message = ""
    
    while True:
        prev_counter = counter 
        counter += 1  
        prev_message = check_reply(prev_counter, prev_message)  
        time.sleep(20)  
    
    driver.close()
    
def chatFunctionAsync():
    thread = threading.Thread(target=start_selenium_chatbot, args=())
    thread.start()
    
def LoginPage():
    global email, password, friendName, gui_text
    login_screen=tk.Tk()
    login_screen.title("Login")
    login_screen.geometry("400x500")
    
    
    Label(login_screen, text="Fill the details").pack()
    
    
    Label(login_screen, text="").pack()
    Label(login_screen, text="Email or Phone number").pack()
    email = StringVar()
    username_login_entry = Entry(login_screen, textvariable=email , show="-")
    username_login_entry.pack()
    
    
    Label(login_screen, text="").pack()
    Label(login_screen, text="Password").pack()
    password = StringVar()
    password__login_entry = Entry(login_screen, textvariable=password, show= '*')
    password__login_entry.pack()
    
    Label(login_screen, text="").pack()
    Label(login_screen, text="Friend facebook name").pack()
    friendName = StringVar()
    friendName__login_entry = Entry(login_screen, textvariable=friendName)
    friendName__login_entry.pack()
    
    Label(login_screen, text="").pack()
    Button(login_screen, text="Go", width=10, bg="green", height=1, command=chatFunctionAsync).pack()
    
    gui_text = tk.Text(login_screen, wrap=tk.WORD, width=40, height=10)
    gui_text.place(y=300, x=40)
    login_screen.mainloop()
    
    
    
# if __name__ == "__main__":
    # First, train the chatbot using the training module
#     train_chatbot()

    # Then start the GUI
LoginPage()
