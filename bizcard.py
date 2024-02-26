import psycopg2
import streamlit as st 
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd 
import numpy as np 
import re
import io

## connection to Database

mydb = psycopg2.connect(host = "localhost",
                        user = "postgres",
                        port = 5432,
                        database = "bizcard",
                        password = "Jerrold@123")
cursor = mydb.cursor()


# SETTING PAGE CONFIGRATIONS

icon = Image.open("/Users/jerroldl/Downloads/bizcard_bg.webp")
st.set_page_config(page_title = "BizCardX: Extracting Business Card Data with OCR | By JERROLD",
                   page_icon = icon,
                   layout="wide",
                   initial_sidebar_state = "expanded")
                  
st.markdown("<h1 style = 'text_align: center; color: Green;'>BizCardx: Extracting Business card Data With OCR</h1>",
            unsafe_allow_html=True)

#SETTING-UP BAGROUND IMAGE

def setting_bg():
    st.markdown(f""" <style>.setApp {{
                    background:url("https://wallpapers.com/images/featured/plain-zoom-background-d3zz0xne0jlqiepg.jpg");
                    background-size: cover }}
                    </style>""", unsafe_allow_html=True)
setting_bg()

#CREATING OPTION MENU
selected = option_menu(None, ["Home", "Uplode & Modify", "Delete"],
                       icons= ["house", "cloud-uplode", "pencil-square"],
                       default_index=0,
                       orientation="horizontal",
                       styles= {"nav-link": {"font-size": "35px", "text-align": "center", "margni": "-3px", "--hover-color": "#545454"},
                                "icon": {"font-size": "35px"},
                                "container": {"max-width": "6000px"},
                                "nav-link-selected": {"background-color": "ff5757"}})

#HOME MENU

if selected == "Home":
    col1, col2 = st.columns(2)
    with col1:
        st.image(Image.open("/Users/jerroldl/Downloads/bizcard_bg.webp"),width = 500)
        st.markdown("## : green[**Technologies used :**] python,easy OCR, streamlit, SQL, pandas")
    with col2:
        st.write(
            "## :green[**About :**] Bizcard is a python application designed to ectract informayton from business card,")
        st.write(
            """The main purpose of Bizcard is to automate the process of extracting key details from nusiness card images, such as the name,
            designation, company, contact information, and other relevant data. By leveraging the power of OCR
            (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the image.""")

#DELETE MENU
        
if selected == "Delete":
    col1,col2 = st.columns([4, 4])
    name_selected = None
    designation_selected = None
    with col1:
        cursor.execute("SELECT NAME FROM BUSSINESS_CARD")
        Y = cursor.fetchall()
        names = ["Select"]
        for i in Y:
            names.append(i[0])
            name_selected = st.selectbox("Select the name to delete", options = names)
    with col2:
        cursor.execute(f"SELECT DESIGNATION FROM BUSSINESS_CARD WHERE NAME = '{name_selected}'")
        Z = cursor.fetchall()
        designation = ["Select"]
        for j in Z:
            designation.append(j[0])
            designation_selected = st.selectbox("Select the designation of the chosen name", options = designation)

    st.markdown(" ")
    col_a, col_b, col_c = st.columns([5, 3, 3])
    with col_b:
        remove = st.button("Clik here to delete")

    if name_selected and designation_selected and remove:
        cursor.execute(f"DELETE FROM BUSSINESS_CARD WHERE NAME = '{name_selected}' AND DESIGNATION = '{designation_selected}'")
        mydb.commit()
        if remove:
            st.warning('DELETE',icon = '⚠️')

#extract the data
            
def extracted_text(picture):
    ext_dic = {'Name': [], 'Designation': [], 'Company name': [], 'Contact': [], 'Email': [], 'Website': [], 'Address': [], 'Pincode': []}
    ext_dic['Name'].append(result[0])
    ext_dic['Designation'].append(result[1])

    for m in range(2, len(result)):
        if result[m].startswith('+') or (result[m].replace('-','').isdigit() and '-' in result[m]):
            ext_dic['Contact'].append(result[m])
        elif '@' in result[m] and '.com' in result[m]:
            small = result[m].lower()
            ext_dic['Email'].append(small)

        elif 'www' in result[m] or 'WWW' in result[m] or 'wwW' in result[m]:
            small = result[m].lower()
            ext_dic['Website'].append(small)
        elif 'TamilNadu' in result[m] or 'Tamil Nadu' in result[m] or result[m].isdigit():
            ext_dic['Pincode'].append(result[m])
        elif re.match(r'^[A-Za-z]', result[m]):
            ext_dic['Company name'].append(result[m])
        
        else:
            removed_colon = re.sub(r'[,;]','', result[m])
            ext_dic['Address'].append(removed_colon)

    for key, value in ext_dic.items():
        if len(value)>0:
            concatenated_string = ' '.join(value)
            ext_dic[key] = [concatenated_string]
        
        else:
            value = "NA"
            ext_dic[key] = [value]
    
    return ext_dic

if selected == "Uplode & Modify":
    image = st.file_uploader(label="Upload the image", type=['png', 'jpg', 'jpeg'], label_visibility="hidden")

    @st.cache_data
    def load_image():
        reader = easyocr.Reader(['en'], model_storage_directory=".")
        return reader
    
    reader_1 = load_image()
    if image is not None:
        input_image = Image.open(image)
        st.image(input_image, width=350, caption='Upload Image')
        st.markdown(f'<style>.css-1aumxhk img {{max-width: 300px; }}</style>',unsafe_allow_html=True)
        result = reader_1.readtext(np.array(input_image), detail=0)

##Creating Database
        ext_text = extracted_text(result)
        df = pd.DataFrame(ext_text)
        st.dataframe(df)

        ##converting image into byte

        image_bytes = io.BytesIO()
        input_image.save(image_bytes, format='PNG')
        image_data = image_bytes.getvalue()
        #Creating Dictnory
        data = {"Image": [image_data]}
        df_1 = pd.DataFrame(data)
        concat_df = pd.concat([df, df_1], axis=1)
        #Database

        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            selected = option_menu(
                menu_title = None,
                options=["preview"],
                icons=['file-earmark'],
                default_index=0,
                orientation="horizongtal"
            )

            ext_text = extracted_text(result)
            df = pd.DataFrame(ext_text)
        if selected == "preview":
            col1, col2 = st.columns([4, 4])
            with col1:
                modified_n = st.text_input('Name', ext_text["Name"][0])
                modified_d = st.text_input('Designation', ext_text["Designation"][0])
                modified_c = st.text_input('Company name', ext_text["Company name"][0])
                modified_con = st.text_input('Mobile', ext_text["Contact"][0])
                concat_df["Name"], concat_df["Designation"], concat_df["Company name"],concat_df[
                    "Contact"] = modified_n, modified_d, modified_c, modified_con
                
            with col2:
                modified_m = st.text_input('Email', ext_text["Email"][0])
                modified_w = st.text_input('Website', ext_text["Website"][0])
                modified_a = st.text_input('Address', ext_text["Address"][0][1])
                modified_p = st.text_input('Pincode', ext_text["Pincode"][0])
                concat_df["Email"], concat_df["Website"], concat_df["Address"], concat_df[
                    "Pincode"] = modified_m, modified_w, modified_a, modified_p

            col3, col4 = st.columns([4, 4])
            with col3:
                preview = st.button("Preview modifiied text")
            with col4:
                Upload = st.button("Upload")
            if preview:
                filtered_df = concat_df[
                    ['Name', 'Designation', 'Company name', 'Contact', 'Email', 'Website', 'Address', 'Pincode']]
                st.dataframe(filtered_df)

            else:
                pass

            if Upload:
                with st.spinner("In Prograss"):
                    cursor.execute(
                        "CREATE TABLE IF NOT EXISTS BUSSINESS_CARD(NAME VARCHAR(50), DESIGNATION VARCHAR(100),"
                        "COMPANY_NAME VARCHAR(100), CONTACT VARCHAR(35), EMAIL VARCHAR(100), WEBSITE VARCHAR("
                        "100), ADDRESS TEXT, PINCODE VARCHAR(100))")
                    mydb.commit()

                    A = "INSERT INTO BUSSINESS_CARD(NAME, DESIGNATION, COMPANY_NAME, CONTACT, EMAIL, WEBSITE, ADDRESS, PINCODE)VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

                    for index, i in concat_df.iterrows():
                        result_table = (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7])
                        cursor.execute(A,result_table)
                        mydb.commit()
                        st.success('SUCCESSFULLY UPLODED', icon="✅")
    else:
        st.write("Upload an image")                
                        
                        
                




