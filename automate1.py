from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from tkinter import *
import pandas as pd
import datetime
import time
import threading
import random

# Function to login and check-in
def login_checkin(driver, username, password):
    driver.get("https://app.rajulaw.com/admin/login/?next=/admin/")
    try:
        # Updated locators for username and password fields
        username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        # Updated locator for the login button
        login_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.lf--submit[type='submit']")))

        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()

        # Assuming there's a check-in button to be clicked after logging in
        # Update the locator for the check-in button if necessary
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn-primary[type='button']"))).click()
    except Exception as e:
        print("An error occurred while trying to log in:", e)

        

# Function to read tasks from CSV
def read_tasks_from_csv(file_path):
    df = pd.read_csv(file_path)
    tasks = df[['Client name_task name', 'Task Type', 'Client Name']].to_dict('records')
    return tasks

# Define a mapping between task names and their corresponding option values
task_category_mapping = {
    'Other': '59',
    'Internal Communication': '60',
    'Form Fill-Up': '118',
    'Email': '119',
    'Drafting': '120',
    'Research': '121',
    'Review and Edit': '122',
    'Meeting': '123',
}

# Function to add task entry
def add_task_entry(driver, task_entry, max_retries=3):
    attempt = 0
    while attempt < max_retries:
        try:
            # Navigate directly to the 'Task Entry' page
            driver.get("https://app.rajulaw.com/admin/task/taskentry/")
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.addlink[href='/admin/task/taskentry/add/']"))).click()
            
            # Use the mapping to get the option value for the task category
            task_category_value = task_category_mapping.get(task_entry['Task Type'], "")
            if task_category_value == "":
                print(f"Task Type '{task_entry['Task Type']}' not found in the mapping.")
                return  # Skip this task entry or handle the error as needed

            Select(driver.find_element(By.ID, "id_task_category")).select_by_value(task_category_value)
            Select(driver.find_element(By.ID, "id_out_of_office")).select_by_value("false")
            Select(driver.find_element(By.ID, "id_is_break")).select_by_value("false")

            task_description = task_entry['Client name_task name']
            driver.find_element(By.ID, "id_description").send_keys(task_description)
            
            # Click the dropdown to open it
            client_dropdown = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "select2-id_client-container"))
            )
            client_dropdown.click()

            # Wait for the dropdown options to become visible
            dropdown_options = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".select2-results__option"))
            )

            client_name = task_entry['Client Name']
            # Iterate through the dropdown options and click the one that matches the client name
            for option in dropdown_options:
                if option.text == client_name:
                    option.click()
                    break

            # Use JavaScript to click the "Save" button
            save_button = driver.find_element(By.XPATH, "//input[@type='submit'][@name='_save']")
            driver.execute_script("arguments[0].click();", save_button)
            
            break  # If the task entry is successful, break out of the loop
        except WebDriverException as e:
            attempt += 1
            print(f"Attempt {attempt} failed with exception: {e}")
            time.sleep(2)  # Wait for 2 seconds before retrying
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break  # Break the loop if there is an unexpected error

    if attempt == max_retries:
        print("Max retries reached. Task entry failed.")

# Function to automate task entry
def automate_task_entry(driver, file_path):
    tasks = read_tasks_from_csv(file_path)
    try:
        while True:
            task_description = random.choice(tasks)
            add_task_entry(driver, task_description)
            time_to_wait = random.randint(28*60, 32*60)
            print(f"Waiting for {time_to_wait/60} minutes before the next task entry.")
            time.sleep(time_to_wait)
    except Exception as e:
        print("An error occurred during task automation:", e)

    
# Function to check out

def check_out(driver):
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "attendance"))).click()
    # The driver.quit() call is indented to be inside the function block

 # Function to start the automation process
def start_automation(username, password, file_path):
    # Setup the Selenium WebDriver
    driver = webdriver.Chrome()  # Make sure to have the chromedriver executable in your PATH or specify the path to chromedriver.

    # Call the login function
    login_checkin(driver, username, password)

    # Start the task entry automation
    automate_task_entry(driver, file_path)

    # You can also add a call to check_out here if needed
    # check_out(driver)       

# Function to create GUI
def create_gui():
    root = Tk()
    root.title("Automated Task Entry")

    Label(root, text="Username").grid(row=0)
    Label(root, text="Password").grid(row=1)
    Label(root, text="CSV File Path").grid(row=2)

    username_entry = Entry(root)
    password_entry = Entry(root, show="*")
    file_path_entry = Entry(root)

    username_entry.grid(row=0, column=1)
    password_entry.grid(row=1, column=1)
    file_path_entry.grid(row=2, column=1)

    
    Button(root, text="Start", command=lambda: threading.Thread(target=start_automation, args=(username_entry.get(), password_entry.get(), file_path_entry.get())).start()).grid(row=3, column=1, sticky=W, pady=4)

    root.mainloop()


# Main function
def main():
    create_gui()

# Run the main function
if __name__ == "__main__":
    main()
