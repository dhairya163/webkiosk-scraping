# import requests
# Importing libraries
import pandas as pd
import streamlit as st
from pathlib import Path
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
import os

# os.system("apt-get install -y chromium-browser")
# os.system("apt-get install libnss3")


def show_page():
  st.title("Check cgpa using default password 12345")
  st.text_input("Starting Roll Number", key="startingroll")
  st.text_input("Ending Roll Number", key="endingroll")
  post = st.button("Check cgpa")

  if post:
    st.write("Please wait...Script takes 2-3 min to get data.")
    print('new')
    import time
    from selenium import webdriver

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"
    header = {"authorization": "MzM2Mjc3OTM0NTcyNTY4NTc4.X3EwXw.OF4fUdtM0PZM5uImuAqd5JVYAy8"}

    options = webdriver.ChromeOptions()
    # options.headless = True
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path = os.environ.get("CHROMEDRIVER_PATH"),options=options)
    starting_rollnumber = st.session_state.startingroll
    ending_rollnumber = st.session_state.endingroll
    rollnumbers = range(int(starting_rollnumber),int(ending_rollnumber)+1)

    for rollnumber in rollnumbers:
      driver.get("https://webkiosk.thapar.edu/")
      username = driver.find_element_by_name("MemberCode")
      password = driver.find_element_by_name("Password")
      username.send_keys(str(rollnumber))
      password.send_keys("12345")
      form = driver.find_element_by_id('BTNSubmit')
      form.click()

      if "Invalid Password" in driver.page_source:
        print("Login for {} failed.. Trying next roll number".format(rollnumber))
        st.write("Login failed for " + str(rollnumber))
        continue
      
      else:
        driver.get("https://webkiosk.thapar.edu/StudentFiles/Exam/StudCGPAReport.jsp")

        rows = driver.find_elements_by_tag_name("tr")

        semname = []
        coursecredit = []
        creditearned = []
        pointssecure = []
        sgpa = []
        cgpa = []

        if(len(rows) < 5):
          print("{} left the college.. So no details available..".format(rollnumber))
          st.write("College left by " + str(rollnumber))
        else:
          x = len(rows) - 1
          for i in range(3,x):
            rowdata = rows[i].find_elements_by_tag_name("td")
            semname.append(rowdata[0].text)
            coursecredit.append(rowdata[1].text)
            creditearned.append(rowdata[2].text)
            pointssecure.append(rowdata[3].text)
            sgpa.append(rowdata[4].text)
            cgpa.append(rowdata[5].text)

          
          df = pd.DataFrame(list(zip(semname,coursecredit,creditearned,pointssecure,sgpa,cgpa)) , columns = ["ExamCode" , "Course Credit" , "Earned Credit","Points Secured", "SGPA" , "CGPA"]	)

          df.to_csv(str(rollnumber) +"-"+ str(rows[1].find_elements_by_tag_name("td")[0].text.split(":")[1].split()[0]) + "-" +(str(rows[1].find_elements_by_tag_name("td")[0].text.split(":")[1].split()[1])) + ".csv")
          print("Saved CGPA Details for {}...".format(rollnumber))
          st.write("Saved CGPA Details for " + str(rollnumber) + "-" + str(rows[1].find_elements_by_tag_name("td")[0].text.split(":")[1].split()[0]))
          st.dataframe(df)          
    st.header("Done")
    for file in os.listdir(os.getcwd()):
      if file.endswith('.csv'):
        tempdf = pd.read_csv(file)
        st.write(str(file))
        tempdf2 = tempdf.iloc[:,1:]
        st.dataframe(tempdf2)
        os.remove(file)
show_page()
