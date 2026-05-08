import random
from playwright.sync_api import sync_playwright

TIMES = 5

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,   # shows the browser window
        slow_mo=500       # slows actions so you can see them
    )

    page = browser.new_page()
    page.goto("http://127.0.0.1:5000/")

    # getting in the first login page
    page.fill("input[name='email']", "a@m.com")
    page.fill("input[name='password']", "1")
    page.click("button[type='submit']")

    # getting into GRN form
    for i in range(TIMES):
        page.click("a[href='/grn']")
        page.fill("input[name='JobNumber']", str(random.randint(0, 100)))
        page.fill("input[name='SupplierCode']", str(random.randint(0, 100)))
        page.fill("input[name='BrokerCode']", str(random.randint(0, 100)))
        page.fill("textarea[name='Comments']", "JU 2764 ITTIFAQ GOODS")
        page.fill("input[name='Hardness']", "0")
        page.fill("input[name='JobNumber']", str(random.randint(0, 100)))
        page.fill("input[name='Weight']", str(random.randint(2000, 30000)))

        grades = ["SPCC", "HARD"]
        page.select_option("select[name='Grade']", random.choice(grades))

        page.fill("input[name='itemcode']", str(random.randint(0, 100)))
        page.fill("input[name='JobNumber']", str(random.randint(0, 100)))
        m = ["KG", "CM", "IN", "FT", "SWG"]
        page.fill("input[name='UOM']", random.choice(m))
        page.fill("input[name='BatchNo']", str(random.randint(0, 100)))
        page.fill("input[name='manufcode']", str(random.randint(0, 100)))
        page.fill("input[name='DC']", str(random.randint(0, 100)))

        coils = ["CRC", "HRC", "GI"]
        page.select_option("select[name='coil']", random.choice(coils))

        suppliers = ["AISHA STEEL LTD", "GUL DEEWAN", "CHINA"]
        page.select_option("select[name='supplier']", random.choice(suppliers))

        itemes = ["CRC", "HRC", "GI", "mi", "CRC COIL 1.20 MM X 1219 MM"]
        page.select_option("select[name='ItemDesc']", random.choice(itemes))

        page.click("button[type='submit']")

    page.wait_for_timeout(10000)  # keep browser open for 10 seconds

    browser.close()