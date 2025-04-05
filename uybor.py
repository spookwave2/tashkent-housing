from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from webdriver_manager.chrome import ChromeDriverManager
from art import tprint
import pandas as pd
import os
import sys
import time

tprint("START", font="tarty1")

link_filename = "uybor_links_house.txt"
temp_csv_filename = "uybor_house_temp.csv"
final_csv_filename = "uybor_house.csv"
status_filename = "ub_status.txt"

# Initialize Options
chrome_options = Options()

# preferences
prefs = {
    "profile.managed_default_content_settings.images": 2,          # Block images
    "profile.managed_default_content_settings.media_stream": 2,   # Block microphone and camera (often used for video/audio input)
    "profile.managed_default_content_settings.plugins": 2,        # Block plugins (can include Flash, which some older ads/videos might use)
    "profile.managed_default_content_settings.autoplay": 2,       # Block autoplay of media
    "profile.managed_default_content_settings.stylesheets": 2    # Block CSS
}
chrome_options.add_experimental_option("prefs", prefs)

# Initialize driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# this is pretty much useless too
dash_count = 70

# kinda pointless but meh
def printm(value=""):
    print("|", value)

# deadly concoction :skull:
def print_lists(data):

    # Find the maximum length of each column
    max_lengths = [0, 0, 0]
    for row in data:
        for i, item in enumerate(row):
            max_lengths[i] = max(max_lengths[i], len(item))

    # Print the aligned data
    for row in data:
        aligned_row = ""
        for i, item in enumerate(row):
            padding = " " * (max_lengths[i] - len(item))
            aligned_row += f"{item}{padding}    "

        print(f"| {aligned_row}")


# Link gathering section
def gather_links(starting_point=1):
    url = "https://uybor.uz/listings?operationType__eq=sale&category__eq=8"
    driver.get(url)
    time.sleep(5) # give the web some time to load

    page_count = 1
    card_links = []

    if starting_point != 1:
        print("Starting point is not zero!")
        print(f"Skipping to page {starting_point}.")
        driver.get(f"{url}&page={starting_point}")
        page_count = starting_point
        with open(link_filename, "r") as linksfile:
            card_links = [l.strip("\n") for l in linksfile.readlines()]

    while True:
        # pretty print stuff again
        print("+", "-"*50, end="+\n", sep="")

        # Dynamic css moving can be weird so there's a webwait
        button_next = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH, "//a[@aria-label='Go to next page']")))
        printm(f"Page {page_count}")
        printm("Next Button found.")

        # gather elements and convert them into links
        for _ in range(20):
            WebDriverWait(driver, 20).until(expected_conditions.presence_of_all_elements_located((By.XPATH, "//a[@class='MuiBox-root mui-style-1vssrzj']")))
            card_elements = driver.find_elements(By.XPATH, "//a[@class='MuiBox-root mui-style-1vssrzj']")
            try:
                card_links.extend([element.get_attribute("href") for element in card_elements])
                break
            except:
                continue

        printm(f"{len(card_elements)} elements have been found and converted.")
        printm(f"{len(card_links)} links saved.")

        # break the program if there aren't any more pages
        if button_next.get_attribute("tabindex") == "-1":
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


# code debloaters
def get_text(xpath, alt):
    try:
        return driver.find_element(By.XPATH, xpath).text
    except:
        return alt
    
def get_element(xpath):
    try:
        if driver.find_element(By.XPATH, xpath):
            return 1
    except:
        return 0


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
titles = [] 
prices = []
rooms = []
sqms = []
lands = []          
floors = []         
conditions = []     
materials = []      
addresses = []       
lifts = []
securities = []
internets = []
playgrounds = []
saunas = []
sewerages = []
fridges = []
telephone_lines = []
separate_bathrooms = []
surveillances = []
pools = []
water_supply = []
microwaves = []
parkings = []
acs = []
tvs = []
washing_machines = []
cables = []
furnitures = []
gas_supply = []

link_count = 1

if os.path.exists(temp_csv_filename):
    print("Previous dataset already exists.")
    print("Continuing from previous dataset.")

    # Tweak 2
    df = pd.read_csv(temp_csv_filename)
    titles = df["Title"].tolist()
    prices = df["Price"].tolist()
    rooms = df["Rooms"].tolist()
    sqms = df["Area"].tolist()
    lands = df["Land Area"].tolist()
    floors = df["Floors"].tolist()
    conditions = df["Condition"].tolist()
    materials = df["Material"].tolist()
    addresses = df["Address"].tolist()
    lifts = df["Lift"].tolist()
    securities = df["Security"].tolist()
    internets = df["Internet"].tolist()
    playgrounds = df["Playground"].tolist()
    saunas = df["Sauna"].tolist()
    sewerages = df["Sewerage"].tolist()
    fridges = df["Fridge"].tolist()
    telephone_lines = df["Telephone Line"].tolist()
    separate_bathrooms = df["Separate Bathrooms"].tolist()
    surveillances = df["Surveillance"].tolist()
    pools = df["Pool"].tolist()
    water_supply = df["Water"].tolist()
    microwaves = df["Microwave"].tolist()
    parkings = df["Parking"].tolist()
    acs = df["AC"].tolist()
    tvs = df["TV"].tolist()
    washing_machines = df["Washing Machine"].tolist()
    cables = df["Cable TV"].tolist()
    furnitures = df["Furniture"].tolist()
    gas_supply = df["Gas"].tolist()

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
        # funky Dynamic css stuff makes me use webwait again
        title = WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.XPATH, "//h1[@class='MuiTypography-root MuiTypography-h2 mui-style-1tyknu']"))).text
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

    price = get_text("//div[@class='MuiTypography-root MuiTypography-h2 mui-style-86wpc3']", alt="None")
    printm(f"Price: \t\t{price}")
    prices.append(price)

    sqm = get_text("//div[@class='MuiTypography-root MuiTypography-overline mui-style-1xqesu' and text()='Площадь']/following-sibling::div", alt="None")
    printm(f"sqm: \t\t\t{sqm}")
    sqms.append(sqm)    

    land = get_text("//div[@class='MuiTypography-root MuiTypography-overline mui-style-1xqesu' and contains(text(), 'Площадь земли')]/following-sibling::div", alt="None")
    printm(f"Land Area: \t\t{land}")
    lands.append(land)    

    room_amount = get_text("//div[@class='MuiTypography-root MuiTypography-overline mui-style-1xqesu' and text()='Комнат']/following-sibling::div", alt="None")
    printm(f"Rooms: \t\t{room_amount}")
    rooms.append(room_amount)

    floor = get_text("//div[@class='MuiTypography-root MuiTypography-overline mui-style-1xqesu' and contains(text(), 'Этаж')]/following-sibling::div", alt="None")
    printm(f"Floors: \t\t{floor}")
    floors.append(floor)
    
    material = get_text("//div[@class='MuiTypography-root MuiTypography-overline mui-style-1xqesu' and contains(text(), 'Материал')]/following-sibling::div", alt="None")
    printm(f"Building Material: \t{material}")
    materials.append(material)

    condition = get_text("//div[@class='MuiTypography-root MuiTypography-overline mui-style-1xqesu' and contains(text(), 'Ремонт')]/following-sibling::div", alt="None")
    printm(f"Condition: \t\t{condition}")
    conditions.append(condition)

    address = get_text("//div[@class='MuiTypography-root MuiTypography-body2 mui-style-31fjox']", alt="None")
    printm(f"Address: \t\t{address}")
    addresses.append(address)

    printm("Facilities:")
    facilities_list = []
    
    lift = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Лифт')]")
    if lift == 1: facilities_list.append("Lift")
    lifts.append(lift)

    security = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Охрана')]")
    if security == 1: facilities_list.append("Security")
    securities.append(security)

    internet = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Интернет')]")
    if internet == 1: facilities_list.append("Internet")
    internets.append(internet)

    playground = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Детская площадка')]")
    if playground == 1: facilities_list.append("Playground")
    playgrounds.append(playground)

    sauna = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Сауна')]")
    if sauna == 1: facilities_list.append("Sauna")
    saunas.append(sauna)

    sewerage = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Канализация')]")
    if sewerage == 1: facilities_list.append("Sewerage")
    sewerages.append(sewerage)

    fridge = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Холодильник')]")
    if fridge == 1: facilities_list.append("Fridge")
    fridges.append(fridge)

    telephone_line = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Телефонная линия')]")
    if telephone_line == 1: facilities_list.append("Telephone line")
    telephone_lines.append(telephone_line)

    separate_bathroom = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Санузел раздельный')]")
    if separate_bathroom == 1: facilities_list.append("Separate bathrooms")
    separate_bathrooms.append(separate_bathroom)

    surveillance = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Видеонаблюдение')]")
    if surveillance == 1: facilities_list.append("Surveillance")
    surveillances.append(surveillance)

    pool = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Бассейн')]")
    if pool == 1: facilities_list.append("Pool")
    pools.append(pool)

    water = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Водоснабжение')]")
    if water == 1: facilities_list.append("Water")
    water_supply.append(water)

    microwave = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Микроволновая печь')]")
    if microwave == 1: facilities_list.append("Oven")
    microwaves.append(microwave)

    parking = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Парковочное место')]")
    if parking == 1: facilities_list.append("Parking")
    parkings.append(parking)

    ac = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Кондиционер')]")
    if ac == 1: facilities_list.append("AC")
    acs.append(ac)

    tv = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Телевизор')]")
    if tv == 1: facilities_list.append("TV")
    tvs.append(tv)

    washing_machine = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Стиральная машина')]")
    if washing_machine == 1: facilities_list.append("Washing machine")
    washing_machines.append(washing_machine)

    cable = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Спутниковое/кабельное ТВ')]")
    if cable == 1: facilities_list.append("Cable")
    cables.append(cable)

    furniture = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Мебель')]")
    if furniture == 1: facilities_list.append("Furniture")
    furnitures.append(furniture)

    gas = get_element("//div[@class='MuiTypography-root MuiTypography-body3 mui-style-xckitu' and contains(text(), 'Газоснабжение')]")
    if gas == 1: facilities_list.append("Gas")
    gas_supply.append(gas)

    # Using list comprehension and slicing
    result_lists = [facilities_list[i:i+3] for i in range(0, len(facilities_list), 3)]
    print_lists(result_lists)

    # save progress every 50 links
    if link_count % 50 == 0:
        df = pd.DataFrame(
            {
            "Title": titles,
            "Price": prices,
            "Rooms": rooms,
            "Land Area": lands,
            "Area": sqms,
            "Floors": floors,
            "Condition": conditions,
            "Material": materials,
            "Address": addresses,
            "Lift": lifts,
            "Security": securities,
            "Internet": internets,
            "Playground": playgrounds,
            "Sauna": saunas,
            "Sewerage": sewerages,
            "Fridge": fridges,
            "Telephone Line": telephone_lines,
            "Separate Bathrooms": separate_bathrooms,
            "Surveillance": surveillances,
            "Pool": pools,
            "Water": water_supply,
            "Microwave": microwaves,
            "Parking": parkings,
            "AC": acs,
            "TV": tvs,
            "Washing Machine": washing_machines,
            "Cable TV": cables,
            "Furniture": furnitures,
            "Gas": gas_supply
            }
        )
        df.to_csv(temp_csv_filename)

    link_count += 1

print("+", "-"*dash_count, end="+\n", sep="")

# save after finishing
df = pd.DataFrame(
    {
        "Title": titles,
        "Price": prices,
        "Rooms": rooms,
        "Land Area": lands,
        "Area": sqms,
        "Floors": floors,
        "Condition": conditions,
        "Material": materials,
        "Address": addresses,
        "Lift": lifts,
        "Security": securities,
        "Internet": internets,
        "Playground": playgrounds,
        "Sauna": saunas,
        "Sewerage": sewerages,
        "Fridge": fridges,
        "Telephone Line": telephone_lines,
        "Separate Bathrooms": separate_bathrooms,
        "Surveillance": surveillances,
        "Pool": pools,
        "Water": water_supply,
        "Microwave": microwaves,
        "Parking": parkings,
        "AC": acs,
        "TV": tvs,
        "Washing Machine": washing_machines,
        "Cable TV": cables,
        "Furniture": furnitures,
        "Gas": gas_supply
    }
)

df.to_csv(final_csv_filename)

tprint("DONE!", font="tarty1")
