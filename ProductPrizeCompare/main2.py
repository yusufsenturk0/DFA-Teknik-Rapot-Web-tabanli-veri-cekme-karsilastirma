import tkinter as tk
from tkinter import ttk
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import csv,os

sellers_data=[]
root=None
chosen_site = None
product_name = None
product_name_in_site=None

def search():
    
    choice = chosen_site.get()

    match choice:
        case "Trendyol":
            trendyol_search("D:\Downloards\chromedriver-win64\chromedriver-win64\chromedriver.exe")
        case "Hepsiburada":
            hepsiburada_search("D:\Downloards\chromedriver-win64\chromedriver-win64\chromedriver.exe")
        case "N11":
            n11_search("D:\Downloards\chromedriver-win64\chromedriver-win64\chromedriver.exe")


    # Buraya gerçek satıcı verilerini sen koyacaksın, ben örnek verdim
    sellers_data = []
    with open("datas.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row not in sellers_data:
                sellers_data.append(row)
    
    show_results_window(product_name_in_site,sellers_data)
    

def show_results_window(product, sellers_data):
    import tkinter.font as tkfont

    def update_table(data):
        for i in tree.get_children():
            tree.delete(i)
        for seller in data:
            tree.insert("", "end", values=(
                seller["seller"], seller["seller_rating"], seller["product_rating"], seller["price"]
            ))

    def convert_price(val):
        try:
            val_clean = ''.join(c for c in val if c.isdigit() or c in ",.")
            val_clean = val_clean.replace('.', '').replace(',', '.')
            return float(val_clean)
        except:
            return float('inf')

    def show_cheapest():
        sorted_data = sorted(sellers_data, key=lambda x: convert_price(x["price"]))[:5]
        update_table(sorted_data)

    def show_most_expensive():
        sorted_data = sorted(sellers_data, key=lambda x: convert_price(x["price"]), reverse=True)[:5]
        update_table(sorted_data)

    def show_all():
        update_table(sellers_data)

    # --- GUI ---
    result_win = tk.Toplevel()
    result_win.title("Search Results")
    result_win.geometry("700x500")
    result_win.configure(bg="#f2f2f2")

    title_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
    btn_font = tkfont.Font(family="Helvetica", size=10)

    tk.Label(
        result_win, 
        text=f"Product: {product}", 
        font=title_font, 
        bg="#f2f2f2", 
        fg="#333", 
        wraplength=650,   # max genişlik (pencereye göre)
        justify="center"
    ).pack(pady=15, padx=10)
    # Butonlar
    btn_frame = tk.Frame(result_win, bg="#f2f2f2")
    btn_frame.pack(pady=5)

    tk.Button(btn_frame, text="Top 5 Cheapest", command=show_cheapest, font=btn_font, bg="#d1e7dd", relief="groove").pack(side="left", padx=10)
    tk.Button(btn_frame, text="Top 5 Most Expensive", command=show_most_expensive, font=btn_font, bg="#f8d7da", relief="groove").pack(side="left", padx=10)
    tk.Button(btn_frame, text="Show All", command=show_all, font=btn_font, bg="#cfe2ff", relief="groove").pack(side="left", padx=10)

    # Treeview (Tablo)
    columns = ("seller", "seller_rating", "product_rating", "price")
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
    style.configure("Treeview", font=("Helvetica", 9), rowheight=25, fieldbackground="#ffffff")

    tree = ttk.Treeview(result_win, columns=columns, show="headings")
    tree.pack(expand=True, fill="both", pady=10, padx=10)

    tree.heading("seller", text="Seller", command=lambda: sort_column(tree, "seller", False))
    tree.heading("seller_rating", text="Seller Rating", command=lambda: sort_column(tree, "seller_rating", False))
    tree.heading("product_rating", text="Product Rating", command=lambda: sort_column(tree, "product_rating", False))
    tree.heading("price", text="Price", command=lambda: sort_column(tree, "price", False))

    for col in columns:
        tree.column(col, anchor=tk.CENTER, width=150)

    update_table(sellers_data)


def sort_column(tree, col, reverse):
    def convert_val(val):
        if not val or val == "N/A":
            return -1
        try:
            # Sadece sayısal karakterleri, nokta ve virgülü bırak
            val_clean = ''.join(c for c in val if (c.isdigit() or c in ",."))
            val_clean = val_clean.replace('.', '').replace(',', '.')  # Türkçe formatı düzelt
            return float(val_clean)
        except:
            return -1

    l = [(tree.set(k, col), k) for k in tree.get_children("")]

    if col in ["price", "seller_rating", "product_rating"]:
        l.sort(key=lambda t: convert_val(t[0]), reverse=reverse)
    else:
        l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)

    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

def create_interface():
    global chosen_site, product_name,root

    root = tk.Tk()
    root.title("Product Search")
    root.geometry("400x200")

    chosen_site = tk.StringVar(value="Trendyol")

    tk.Label(root, text="Select site:").pack(anchor="w", padx=10, pady=5)

    sites = ["Trendyol", "Hepsiburada", "N11"]
    for site in sites:
        tk.Radiobutton(root, text=site, variable=chosen_site, value=site).pack(anchor="w", padx=20)

    frame = tk.Frame(root, width=380, height=40)
    frame.pack(pady=20)
    frame.pack_propagate(False)

    tk.Label(frame, text="Product name:").pack(side="left", padx=5)
    product_name = tk.Entry(frame, width=20)  
    product_name.pack(side="left", padx=5)

    tk.Button(frame, text="Search", command=search).pack(side="left", padx=5)

    root.mainloop()


def trendyol_search(driver_path):
    global product_name_in_site
    global sellers_data
    sellers_data = []  # önce boşaltabilirsin

    options = webdriver.ChromeOptions()
    service = Service(driver_path)
    options.add_argument("--disable-notifications") 
    options.add_argument("--incognito")
    driver = webdriver.Chrome(service=service, options=options)
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.geolocation": 2
    })


    driver.get("https://www.trendyol.com")
    time.sleep(2)


    arama_kutusu = driver.find_element(By.CLASS_NAME, "V8wbcUhU")
    arama_kutusu.send_keys(product_name.get())
    arama_kutusu.send_keys(Keys.ENTER)
    time.sleep(2)
    # -----------------------------------------
    wait = WebDriverWait(driver, 5)

    

    # -----------------------------------------------------------
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    # Tüm ürün linklerini içeren <a> taglarını seçelim
    # Örnek: <a> etiketi içinde "class" varsa veya CSS selector ile seçilebilir
    product_links_0 = soup.find_all("a", class_="p-card-chldrn-cntnr card-border") 
    product_link=None
    a=0
    for a_tag in product_links_0:
        if(a==1):
            break
        href = a_tag.get("href")
        # Eğer link tam URL değilse site adresini ekle
        if href and not href.startswith("http"):
            href = "https://www.trendyol.com" + href
        product_link=href
        a=a+1

    driver.get(product_link)
    time.sleep(2)  
    
     

    with open("datas.csv","w",newline='',encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["seller", "seller_rating", "product_rating", "price"])
        writer.writeheader()
    
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        c=0

        try:
            
            show_all_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "show-all"))
        )
            
            show_all_button.click()
            print("Show all button clicked.")
            c=1
            time.sleep(1)
            # --- Ana Satıcının Bilgileri ---
            try:
                product_name_in_site = driver.find_element(By.CLASS_NAME, "pr-new-br").text.strip()
            except:
                product_name_in_site = "N/A"
            try:
                seller_name_main = driver.find_element(By.CLASS_NAME, "seller-name-text").text.strip()
            except:
                seller_name_main = "N/A"

            try:
                seller_rating_main = driver.find_element(By.CLASS_NAME, "sl-pn").text.strip()
            except:
                seller_rating_main = "N/A"

            try:
                price_main = driver.find_element(By.CLASS_NAME, "prc-dsc").text.strip()
            except:
                price_main = "N/A"
            
            try:
                price_rating_main = driver.find_element(By.CLASS_NAME, "value").text.strip()
            except:
                price_rating_main = "N/A"

            writer.writerow({"seller": seller_name_main, "seller_rating": seller_rating_main,"product_rating": price_rating_main, "price": price_main})
            
            time.sleep(0.5)
            element = driver.find_element(By.CSS_SELECTOR, ".omc-mr-btn.gnr-cnt-br")
            element.click()
            time.sleep(0.5)

            seller_boxes = driver.find_elements(By.CSS_SELECTOR, ".omc-cntr .pr-mc-w.gnr-cnt-br")
            

            for box in seller_boxes:
                try:
                    seller_name = box.find_element(By.CLASS_NAME, "seller-name-text").text.strip()
                except:
                    seller_name = "N/A"

                try:
                    seller_rating = box.find_element(By.CLASS_NAME, "sl-pn").text.strip()
                except:
                    seller_rating = "N/A"

                try:
                    price = box.find_element(By.CLASS_NAME, "prc-dsc").text.strip()
                except:
                    price = "N/A"

                


                writer.writerow({"seller": seller_name, "seller_rating": seller_rating,"product_rating":price_rating_main, "price": price})
                

        
        except:
            try:
                product_name_in_site = driver.find_element(By.CLASS_NAME, "pr-new-br").text.strip()
            except:
                product_name_in_site = "N/A"
            
            if(c==0):
                time.sleep(1)
                # --- Ana Satıcının Bilgileri ---
                try:
                    seller_name_main = driver.find_element(By.CLASS_NAME, "seller-name-text").text.strip()
                except:
                    seller_name_main = "N/A"

                try:
                    seller_rating_main = driver.find_element(By.CLASS_NAME, "sl-pn").text.strip()
                except:
                    seller_rating_main = "N/A"

                try:
                    price_main = driver.find_element(By.CLASS_NAME, "prc-dsc").text.strip()
                except:
                    price_main = "N/A"
                
                try:
                    price_rating_main = driver.find_element(By.CLASS_NAME, "value").text.strip()
                except:
                    price_rating_main = "N/A"

                writer.writerow({"seller": seller_name_main, "seller_rating": seller_rating_main,"product_rating": price_rating_main, "price": price_main})
                
                print("!!!There is no other seller")
                time.sleep(0.5)
            elif(c==1):
                time.sleep(1)
                # --- Ana Satıcının Bilgileri ---
                try:
                    seller_name_main = driver.find_element(By.CLASS_NAME, "seller-name-text").text.strip()
                except:
                    seller_name_main = "N/A"

                try:
                    seller_rating_main = driver.find_element(By.CLASS_NAME, "sl-pn").text.strip()
                except:
                    seller_rating_main = "N/A"

                try:
                    price_main = driver.find_element(By.CLASS_NAME, "prc-dsc").text.strip()
                except:
                    price_main = "N/A"
                
                try:
                    price_rating_main = driver.find_element(By.CLASS_NAME, "value").text.strip()
                except:
                    price_rating_main = "N/A"


                writer.writerow({"seller": seller_name_main, "seller_rating": seller_rating_main,"product_rating": price_rating_main, "price": price_main})
                #--diğer satıcı bilgileri-------------

                seller_boxes = driver.find_elements(By.CSS_SELECTOR, ".omc-cntr .pr-mc-w.gnr-cnt-br")

                for box in seller_boxes:
                    try:
                        seller_name = box.find_element(By.CLASS_NAME, "seller-name-text").text.strip()
                    except:
                        seller_name = "N/A"

                    try:
                        seller_rating = box.find_element(By.CLASS_NAME, "sl-pn").text.strip()
                    except:
                        seller_rating = "N/A"

                    try:
                        price = box.find_element(By.CLASS_NAME, "prc-dsc").text.strip()
                    except:
                        price = "N/A"


                    

                    writer.writerow({"seller": seller_name, "seller_rating": seller_rating,"product_rating": price_rating_main, "price": price})



def hepsiburada_search(driver_path):
    global sellers_data
    global product_name_in_site
    sellers_data = []  # önce boşaltabilirsin

    options = webdriver.ChromeOptions()
    service = Service(driver_path)
    options.add_argument("--disable-notifications") 
    options.add_argument("--incognito")
    driver = webdriver.Chrome(service=service, options=options)
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.geolocation": 2
    })


    driver.get(f"https://www.hepsiburada.com/ara?q={product_name.get()}")
    time.sleep(2)

  
    

    # -----------------------------------------------------------
    with open("datas.csv","w",newline='',encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["seller", "seller_rating", "product_rating", "price"])
        writer.writeheader()
    
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Tüm ürün linklerini içeren <a> taglarını seçelim
        # Örnek: <a> etiketi içinde "class" varsa veya CSS selector ile seçilebilir
        product_links_0 = soup.find_all("a", class_="productCardLink-module_productCardLink__GZ3eU") 
        product_link=None
        a=0
        for a_tag in product_links_0:
            if(a==1):
                break
            href = a_tag.get("href")
            # Eğer link tam URL değilse site adresini ekle
            if href and not href.startswith("http"):
                href = "https://www.hepsiburada.com" + href
            product_link=href
            a=a+1

        driver.get(product_link)
        time.sleep(2)  

        #-------Getting seller informations-----------------

        try:
            product_rating=driver.find_element(By.CLASS_NAME,"JYHIcZ8Z_Gz7VXzxFB96").text.strip()
        except:
            product_rating="N/A" 

        try:
            product_name_in_site=driver.find_element(By.CSS_SELECTOR, '[data-test-id="title"]').text.strip()
        except:
            product_name_in_site="N/A" 
        
        time.sleep(2) 
        try:
            
            # "Tüm satıcıları gör" butonunu kontrol et
            element = driver.find_element(By.CLASS_NAME, "M6iJLUpgHKlEPzGcOggE")
            element.click()
            time.sleep(2) 
            "ciEqaMdv5xbgmqxYG3vq"
            seller_boxes = driver.find_elements(By.CLASS_NAME, "VwUAvtsSpdiwukfc0VGp")
            print(len(seller_boxes))
            
            for box in seller_boxes:
                
                try:
                    seller_name = box.find_element(By.CSS_SELECTOR, '[data-test-id="merchant-name"]').text
                    
                except:
                    seller_name = "N/A"
                if(seller_name=="Hepsiburada"):
                    seller_rating="10"
                else:
                    try:
                        seller_rating = box.find_element(By.CSS_SELECTOR,'[data-test-id="merchant-rating"]').text.strip()
                    except:
                        seller_rating = "N/A"

                try:
                    price = box.find_element(By.CSS_SELECTOR, '[data-test-id="price-current-price"]').text.strip()
                except:
                    price = "N/A"

                a=0
                if(seller_name=="N/A" or seller_name==""):
                    a+=1
                if(seller_rating=="N/A" or seller_rating==""):
                    a+=1
                if(product_rating=="N/A" or product_rating==""):
                    a+=1
                if(price=="N/A" or price==""):
                    a+=1
                
                
                
                new_data={"seller": seller_name, "seller_rating": seller_rating,"product_rating": product_rating, "price": price}
                
                writer.writerow(new_data)



        except :
            print("a")
            time.sleep(1) 
            print("Buton bulunamadı, tek satıcı olabilir.")

            try:
                seller_name=driver.find_element(By.CLASS_NAME,"rzVCX6O5Vz9bkKB61N2W").text.strip()
            except:
                seller_name="N/A"
            
            if(seller_name=="Hepsiburada"):
                seller_rating="10"
            else:
                try:
                    seller_rating=driver.find_element(By.CSS_SELECTOR, '[data-test-id="merchant-rating"]').text.strip()
                except:
                    seller_rating="N/A"

            try:
                price=driver.find_element(By.CLASS_NAME,"z7kokklsVwh0K5zFWjIO").text.strip()
            except:
                price="N/A"
        
            writer.writerow({"seller": seller_name, "seller_rating": seller_rating,"product_rating": product_rating, "price": price})

def n11_search(driver_path):
    global product_name_in_site
    global sellers_data
    sellers_data = []  # önce boşaltabilirsin

    options = webdriver.ChromeOptions()
    service = Service(driver_path)
    options.add_argument("--force-device-scale-factor=1") 
    options.add_argument("--disable-notifications") 
    options.add_argument("--incognito")
    driver = webdriver.Chrome(service=service, options=options)
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.geolocation": 2
    })


    driver.get("https://www.n11.com/")
    time.sleep(2)

    


    arama_kutusu = driver.find_element(By.ID, "searchData")
    arama_kutusu.send_keys(product_name.get())
    arama_kutusu.send_keys(Keys.ENTER)
    time.sleep(2)
    # -----------------------------------------


    

    with open("datas.csv","w",newline='',encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["seller", "seller_rating", "product_rating", "price"])
        writer.writeheader()

        # -----------------------------------------------------------
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Tüm ürün linklerini içeren <a> taglarını seçelim
        # Örnek: <a> etiketi içinde "class" varsa veya CSS selector ile seçilebilir
        product_links_0 = soup.find_all("a", class_="plink") 
        product_link=None
        a=0
        for a_tag in product_links_0:
            if(a==1):
                break
            href = a_tag.get("href")
            # Eğer link tam URL değilse site adresini ekle
            if href and not href.startswith("http"):
                href = "https://www.n11.com" + href
            product_link=href
            a=a+1

        driver.get(product_link)
        time.sleep(2)  
         # -----------------------------------------------------------
        

 # -----------------------------------------------------------

        try:
            seller_name=driver.find_element(By.CLASS_NAME,"unf-p-seller-name").text.strip()
        except:
            seller_name="N/A" 
        
        try:
            seller_rating=driver.find_element(By.CLASS_NAME,"shopPoint").text.strip()
        except:
            seller_rating="N/A"
        
        try:
            product_rating=driver.find_element(By.CLASS_NAME,"ratingScore").text.strip()
        except:
            product_rating="N/A"
        
        try:
            price=driver.find_element(By.CLASS_NAME,"newPrice").text.strip()
        except:
            price="N/A"

        try:
            product_name_in_site=driver.find_element(By.CLASS_NAME, "proName").text.strip()
        except:
            product_name_in_site="N/A" 

        

        new_data={"seller": seller_name, "seller_rating": seller_rating,"product_rating": product_rating, "price": price}
        writer.writerow(new_data)

        time.sleep(2)
        try:
            # "Tüm satıcıları gör" butonunu kontrol et
            element = driver.find_element(By.XPATH, "//span[contains(text(),'Tümü')]")
            element.click()
            time.sleep(2) 
            

            while True:
                driver.execute_script("window.scrollBy(0, 1000);")
            
                time.sleep(2)  # Sayfanın yüklenmesini bekle

                # Satıcıları çek (örnek class ismine göre)
                seller_box=driver.find_elements(By.CSS_SELECTOR,".unf-cmp .unf-cmp-body")
                for seller in seller_box:
                    # Burada seller_name, price gibi bilgileri çekersin
                    try:
                        seller_name = seller.find_element(By.CLASS_NAME, "b-n-title").text.strip()
                    except:
                        seller_name="N/A"
                    
                    try:
                        seller_rating=seller.find_element(By.CLASS_NAME,"shopPoint").text.strip()
                    except:
                        seller_rating="N/A"
                    
                    try:
                        price = seller.find_element(By.CLASS_NAME, "b-p-new").text.strip()
                    except:
                        price="N/A"
                    
                    print(f"Seller: {seller_name}|| Seller Rating: {seller_rating} || Price: {price} || Product Rating: {product_rating} ")

                    new_data={"seller": seller_name, "seller_rating": seller_rating,"product_rating": product_rating, "price": price}
                    writer.writerow(new_data)

                # "Sonraki" butonunu bulmaya çalış
                time.sleep(1)
                try:
                    print("aaaaaaaaaaaaaaaaaaaaaaaaaaa")
                    next_button = driver.find_element(By.CSS_SELECTOR, ".unf-cmp .pagination .next.navigation") # Güncel class ismini kullan
                    next_button.click()
                    print("bbbbbbbbbbbbbbbbbbbbbbbbb")
                    
                    
                    time.sleep(2)
                except:
                    print("ccccccccccccccccccccccccccc")
                    break  # Buton yoksa çık


            
        except:
            print("Diğer satıcılar bulunmamakta")
            time.sleep(2) 
            pass
        







if __name__ == '__main__':

    create_interface()