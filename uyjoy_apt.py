from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os
import sys
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# this is pretty much useless too
dash_count = 70

# kinda pointless but meh
def printm(value=""):
    print("|", value)


def gather_links(s_point=1):
    url = "https://uy-joy.uz"
    driver.get(url)
    time.sleep(10) # give the web some time to load

    button = driver.find_element(By.XPATH, "//div[@class='mt-3 flex items-center justify-center']/button[@class='el-button el-button--primary']")
    button.click()

    page_count = 1
    flat_links = []

    while True:
        if s_point != 1:
            print("Starting point is not zero!")
            print(f"Skipping to page {s_point}.")
            while page_count < s_point:
                print(f"Page {page_count}.")
                button_next = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH, "//button[@class='btn-next']")))
                button_next.click()
                page_count += 1

        # pretty print stuff again
        print("+", "-"*45, end="+\n", sep="")
        printm(f"Page {page_count}")
        
        # Ajax css moving can be weird so there's a webwait
        button_next = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH, "//button[@class='btn-next']")))
        printm("Next Button found.")

        # gather elements and convert them into links
        flat_elements = driver.find_elements(By.XPATH, "//div[@class='el-card__body']/a")
        printm(f"{len(flat_elements)} Flat elements have been found and converted.")

        flat_links = flat_links + [element.get_attribute("href") for element in flat_elements]
        printm(f"{len(flat_links)} links saved.")

        # break the program if there aren't any more pages
        if not button_next.is_enabled():
            printm("Button is disabled.")
            printm("Breaking loop...")
            break

        printm("Button is enabled.")
        printm("Clicking button..")

        # if the next page gives an error, save progress.
        try:
            button_next.click()
        except Exception as e:
            printm(f"{e} Error.")
            printm("Saving..")
            with open("links.txt", "w") as file, open("done.txt", "w") as dfile:
                file.writelines("\n".join(flat_links)) # Join each link with a newline
                dfile.write("0") # Signal that you're not done collecting links
            printm("Links saved to links.txt")
            print("+", "-"*45, end="+\n", sep="")
            sys.exit(f"Exited at page {page_count}.")

        page_count += 1
    # save links to a links.txt just incase
    with open("links.txt", "w") as file, open("done.txt", "w") as dfile:
        file.writelines("\n".join(flat_links))
        dfile.write("1") # Signal that you're done


# code debloater
def get_text(xpath, alt):
    try:
        return driver.find_element(By.XPATH, xpath).text
    except:
        return alt


"""MAIN"""
# uhhh
if not os.path.exists("links.txt"):
    with open("links.txt", "r") as lfile, open("done.txt", "r") as dfile:
        lf_length = len(lfile)
        if dfile.readline() == "0":
            gather_links(lf_length)
    

# get link from file
with open("links.txt", "r") as file:
    flat_links = file.readlines()

# -----------------------------------------------------------
# THIS CAME LATER

# got an error so had to whip this up to continue from where it left off
# you may delete this
df = pd.read_csv("uyjoy_temp.csv")

# if you didn't get an error, lucky you, just turn these into empty lists
titles = df["Title"].tolist()
prices = df["Price"].tolist()
rooms = df["Rooms"].tolist()
sqms = df["Area"].tolist()
floors = df["Floor"].tolist()
b_floors = df["Building floors"].tolist()
conditions = df["Condition"].tolist()
styles = df["Style"].tolist()
provinces = df["Province"].tolist()
districts = df["District"].tolist()
neighborhoods = df["Neighborhood"].tolist()

# you can turn this into 1
apt_count = len(df) + 1

# you can delete this too
flat_links = flat_links[apt_count:]
# -----------------------------------------------------------

# actual info collecting let's gooo
for link in flat_links:
    # Pretty print stuff
    print("+", "-"*dash_count, end="+\n", sep="")
    
    # get rid of \n in links so it doesn't interfere with driver
    link = link.strip("\n")
    driver.get(link)
    
    # funky ajax stuff makes me use webwait again
    title = WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@class='product-details font-medium text-xl']/span"))).text

    # mostly debugging stuff
    printm(f"Apartment {apt_count}")
    printm(link)

    # actualt data collecting
    printm(f"Title: {title}")
    titles.append(title)

    price = get_text("//div[@class='product-price text-xl']", alt="None")
    printm(f"Price: \t\t{price}")
    prices.append(price)

    sqm = get_text("//div[@class='specification-type' and contains(text(), 'Умумий майдон (м²)')]/following-sibling::div", alt="None")
    printm(f"sqm: \t\t\t{sqm}")
    sqms.append(sqm)

    room_amount = get_text("//div[@class='specification-type' and contains(text(), 'Хоналар сони')]/following-sibling::div", alt="None")
    printm(f"Rooms: \t\t{room_amount}")
    rooms.append(room_amount)

    floor = get_text("//div[@class='specification-type' and contains(text(), 'Қавати')]/following-sibling::div", alt="None")
    printm(f"Floor: \t\t{floor}")
    floors.append(floor)

    b_floor = get_text("//div[@class='specification-type' and contains(text(), 'Уй қаватлилиги')]/following-sibling::div", alt="None")
    printm(f"Building floors: \t{b_floor}")
    b_floors.append(b_floor)

    style = get_text("//div[@class='specification-type' and contains(text(), 'Архитектуравий услуб')]/following-sibling::div", alt="None")
    printm(f"Architectural Style: \t{style}")
    styles.append(style)

    condition = get_text("//div[@class='specification-type' and contains(text(), 'Таъмир холати')]/following-sibling::div", alt="None")
    printm(f"Condition: \t\t{condition}")
    conditions.append(condition)

    province = get_text("//div[@class='specification-type' and contains(text(), 'Вилоят')]/following-sibling::div", alt="None")
    printm(f"Province: \t\t{province}")
    provinces.append(province)

    district = get_text("//div[@class='specification-type' and contains(text(), 'Туман')]/following-sibling::div", alt="None")
    printm(f"District: \t\t{district}")
    districts.append(district)

    neighborhood = get_text("//div[@class='specification-type' and contains(text(), 'МФЙ')]/following-sibling::div", alt="None")
    printm(f"Neigborhood: \t\t{neighborhood}")
    neighborhoods.append(neighborhood)

    # save progress every 100 links
    if apt_count % 100 == 0:
        df = pd.DataFrame(
            {
            "Title": titles,
            "Price": prices,
            "Rooms": rooms,
            "Area": sqms,
            "Floor": floors,
            "Building floors": b_floors,
            "Condition": conditions,
            "Style": styles,
            "Province": provinces,
            "District": districts,
            "Neighborhood": neighborhoods
            }
        )
        df.to_csv("uyjoy_temp2.csv")

    apt_count += 1

# save after finishing
df = pd.DataFrame(
    {
        "Title": titles,
        "Price": prices,
        "Rooms": rooms,
        "Area": sqms,
        "Floor": floors,
        "Building floors": b_floors,
        "Condition": conditions,
        "Style": styles,
        "Province": provinces,
        "District": districts,
        "Neighborhood": neighborhoods
    }
)

df.to_csv("uyjoy.csv")
