from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os
import sys
import time

link_filename = "uyjoy_house_links.txt"
temp_csv_filename = "uyjoy_house_temp.csv"
final_csv_filename = "uyjoy_house.csv"
status_filename = "uyjoy_house_status.txt"

# Initialize Options
chrome_options = Options()

# preferences
prefs = {
    "profile.managed_default_content_settings.images": 2, # Block images
    "profile.managed_default_content_settings.media_stream": 2,  # Block microphone and camera (often used for video/audio input)
    "profile.managed_default_content_settings.plugins": 2,   # Block plugins (can include Flash, which some older ads/videos might use)
    "profile.managed_default_content_settings.autoplay": 2  # Block autoplay of media
}
chrome_options.add_experimental_option("prefs", prefs)

# Initialize driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# this is pretty much useless too
dash_count = 70

# kinda pointless but meh
def printm(value=""):
    print("|", value)

# Link gathering section
def gather_links(starting_point=1):
    url = "https://uy-joy.uz"
    driver.get(url)
    time.sleep(10) # give the web some time to load

    hbutton = driver.find_element(By.XPATH, "//div[@id='tab-ResidentialIndividual_Sell']")
    hbutton.click()
    time.sleep(1)

    search_button = driver.find_element(By.XPATH, "//div[@class='mt-3 flex items-center justify-center']/button[@class='el-button el-button--primary']")
    search_button.click()

    page_count = 1
    card_links = []

    if starting_point != 1:
        print("Starting point is not zero!")
        print(f"Skipping to page {starting_point}.")
        while page_count < starting_point:
            print(f"Page {page_count}.")
            button_next = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH, "//button[@class='btn-next']")))
            button_next.click()
            page_count += 1

    while True:
        # pretty print stuff again
        print("+", "-"*50, end="+\n", sep="")

        # Ajax css moving can be weird so there's a webwait
        button_next = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH, "//button[@class='btn-next']")))
        printm(f"Page {page_count}")
        printm("Next Button found.")

        # gather elements and convert them into links
        card_elements = driver.find_elements(By.XPATH, "//div[@class='el-card__body']/a")
        printm(f"{len(card_elements)} elements have been found and converted.")

        card_links = card_links + [element.get_attribute("href") for element in card_elements]
        printm(f"{len(card_links)} links saved.")

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
        # save progress
        except Exception as e:
            printm(f"{e} Error.")
            printm("Saving..")
            # open 2 files. One to save links, and one to save the status of the link collecting
            with open(link_filename, "w") as file, open(status_filename, "w") as sfile:
                file.writelines("\n".join(card_links)) # Join each link with a newline
                sfile.writelines("\n".join(["Unfinished", f"{page_count}"])) # Signal that you're not done collecting links
            printm(f"Links saved to {link_filename}")
            print("+", "-"*50, end="+\n", sep="")
            sys.exit(f"Exited at page {page_count}.")

        page_count += 1
    # save links to a text file just incase
    with open(link_filename, "w") as file, open(status_filename, "w") as sfile:
        file.writelines("\n".join(card_links))
        sfile.writelines("\n".join(["Finished", f"{page_count}"])) # Signal that you're done


# code debloater
def get_text(xpath, alt):
    try:
        return driver.find_element(By.XPATH, xpath).text
    except:
        return alt


"""MAIN"""
# uhhh
if os.path.exists(link_filename):
    with open(status_filename, "r") as sfile:
        # Check if link collecting isn't done
        lines = sfile.readlines()
        if lines[0].strip("\n") == "Unfinished":
            gather_links(int(lines[1]))
else:
    gather_links()

print("Links were already collected.")
print("Moving on to information gathering.")

# get link from file
with open(link_filename, "r") as file:
    links = file.readlines()
print(f"{len(links)} links found.")

# -----------------------------------------------------------
# got an error so had to whip this up so it continues from where it left off
titles = []         # df["Title"].tolist()
prices = []         # df["Price"].tolist()
lands = []          # df["Area"].tolist()
footprints = []     # df["Area"].tolist()
sqms = []           # df["Area"].tolist()
floors = []         # df["Floor"].tolist()
conditions = []     # df["Condition"].tolist()
styles = []         # df["Style"].tolist()
provinces = []      # df["Province"].tolist()
districts = []      # df["District"].tolist()
neighborhoods = []  # df["Neighborhood"].tolist()

link_count = 1

if os.path.exists(temp_csv_filename):
    print("Previous dataset already exists.")
    print("Continuing from previous dataset.")

    # Tweak 2
    df = pd.read_csv(temp_csv_filename)
    titles = df["Title"].tolist()
    prices = df["Price"].tolist()
    lands = df["Land Area"].tolist()
    footprints = df["Footprint"].tolist()
    sqms = df["Area"].tolist()
    floors = df["Floors"].tolist()
    conditions = df["Condition"].tolist()
    styles = df["Style"].tolist()
    provinces = df["Province"].tolist()
    districts = df["District"].tolist()
    neighborhoods = df["Neighborhood"].tolist()

    link_count = len(df) + 1

    links = links[link_count:]
    print(f"{len(links)} links left.")

# -----------------------------------------------------------

fetch_fails_limit = 3

# actual info collecting.
for link in links:
    # Pretty print stuff
    print("+", "-"*dash_count, end="+\n", sep="")
    
    # get rid of \n in links so it doesn't interfere with driver
    link = link.strip("\n")
    driver.get(link)
    
    try:
        # funky ajax stuff makes me use webwait again
        title = WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@class='product-details font-medium text-xl']/span"))).text
    except Exception as e:
        fetch_fails_limit -= 1
        if fetch_fails_limit < 0:
            raise Exception("Exceeded fetch fails limit. There is probably a server error.")
        print(f"Couldn't fetch {link}")
        print(f"Fetch fails limit = {fetch_fails_limit}")
        continue

    # mostly debugging stuff
    printm(f"Link {link_count}")
    printm(link)

    # Tweak 3
    # actualt data collecting
    printm(f"Title: {title}")
    titles.append(title)

    price = get_text("//div[@class='product-price text-xl']", alt="None")
    printm(f"Price: \t\t{price}")
    prices.append(price)

    land = get_text("//div[@class='specification-type' and contains(text(), 'Умумий ер майдон (м²)')]/following-sibling::div", alt="None")
    printm(f"Land area: \t\t{land}")
    lands.append(land)

    footprint = get_text("//div[@class='specification-type' and contains(text(), 'Умумий қурилиш ости майдони(м²)')]/following-sibling::div", alt="None")
    printm(f"Footprint: \t\t{footprint}")
    footprints.append(footprint)

    sqm = get_text("//div[@class='specification-type' and contains(text(), 'Фойдали майдони')]/following-sibling::div", alt="None")
    printm(f"sqm: \t\t\t{sqm}")
    sqms.append(sqm)    

    floor = get_text("//div[@class='specification-type' and contains(text(), 'Қаватлилиги')]/following-sibling::div", alt="None")
    printm(f"Floors: \t\t{floor}")
    floors.append(floor)

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
    if link_count % 50 == 0:
        # Tweak 4
        df = pd.DataFrame(
            {
            "Title": titles,
            "Price": prices,
            "Land Area": lands,
            "Footprint": footprints,
            "Area": sqms,
            "Floors": floors,
            "Condition": conditions,
            "Style": styles,
            "Province": provinces,
            "District": districts,
            "Neighborhood": neighborhoods
            }
        )
        df.to_csv(temp_csv_filename)

    link_count += 1

# Tweak 5
# save after finishing
df = pd.DataFrame(
    {
        "Title": titles,
        "Price": prices,
        "Land Area": lands,
        "Footprint": footprints,
        "Area": sqms,
        "Floors": floors,
        "Condition": conditions,
        "Style": styles,
        "Province": provinces,
        "District": districts,
        "Neighborhood": neighborhoods
    }
)

df.to_csv(final_csv_filename)