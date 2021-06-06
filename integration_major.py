import streamlit as st
from PIL import Image
import cv2
import pickle
import numpy as np
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from google_trans_new import google_translator  
from bs4 import BeautifulSoup as bs
import requests
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/ 90.0.4430.212 Safari/537.36"
# US english
LANGUAGE = "en-US,en;q=0.5"

def print_weather(data):
    try:
        st.write("Weather for:", data["region"])
        st.write("Now:", data["dayhour"])
        st.write(f"Temperature now: {data['temp_now']}°C")
        st.write("Description:", data['weather_now'])
        st.write("Precipitation:", data["precipitation"])
        st.write("Humidity:", data["humidity"])
        st.write("Wind:", data["wind"])
    except:
        st.write(None)
    
def get_weather_data(region):
    url = "https://www.google.com/search?lr=lang_en&ie=UTF-8&q=weather "
    url+= region
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    html = session.get(url)
    # create a new soup
    soup = bs(html.text, "html.parser")
    #store all results on this dictionary
    result = {}
    # extract region
    try:
        result['region'] = soup.find("div", attrs={"id": "wob_loc"}).text
        # extract temperature now
        result['temp_now'] = soup.find("span", attrs={"id": "wob_tm"}).text
        # get the day and hour now
        result['dayhour'] = soup.find("div", attrs={"id": "wob_dts"}).text
        # get the actual weather
        result['weather_now'] = soup.find("span", attrs={"id": "wob_dc"}).text
        # get the precipitation
        result['precipitation'] = soup.find("span", attrs={"id": "wob_pp"}).text
        # get the % of humidity
        result['humidity'] = soup.find("span", attrs={"id": "wob_hm"}).text
        # extract the wind
        result['wind'] = soup.find("span", attrs={"id": "wob_ws"}).text
        return result
    except:
        return None
   

    
translator =google_translator()

loc_button = Button(label="Get Location")
loc_button.js_on_event("button_click", CustomJS(code="""
    navigator.geolocation.getCurrentPosition(
        (loc) => {
            document.dispatchEvent(new CustomEvent("GET_LOCATION", {detail: {lat: loc.coords.latitude, lon: loc.coords.longitude}}))
        }
    )
    """))
result = streamlit_bokeh_events(
    loc_button,
    events="GET_LOCATION",
    key="get_location",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)
if result:
    if "GET_LOCATION" in result:
        st.write(result.get("GET_LOCATION"))
        
def yieldpred(m,features):
    features = np.array(features).astype(np.float64).reshape(1,-1)
    
    predict = m.predict(features)
    

    return predict

def predrainfall(state):
    region=(np.array([state]).reshape(1, 1))
    rain_model = pickle.load(open("rainfall.pkl", "rb"))
    annual=rain_model.predict(region)
    return annual
     
    
    
    
        
def main():
    st.title('AGRICULTURAL PREDICTION')
    s=['ANDAMAN AND NICOBAR ISLANDS', 'ANDHRA PRADESH', 'ARUNACHAL PRADESH', 'ASSAM', 'BIHAR', 'CHANDIGARH', 'CHHATTISGARH', 'DADRA AND NAGAR HAVELI', 'GUJARAT', 'HARYANA', 'HIMACHAL PRADESH', 'JAMMU AND KASHMIR', 'JHARKHAND', 'KARNATAKA', 'KERALA', 'MADHYA PRADESH', 'MAHARASHTRA', 'MANIPUR', 'MEGHALAYA', 'MIZORAM', 'NAGALAND', 'ODISHA', 'PUDUCHERRY', 'PUNJAB', 'RAJASTHAN', 'TAMIL NADU', 'TELANGANA ', 'TRIPURA', 'UTTAR PRADESH', 'UTTARAKHAND']
    rain={'ANDAMAN AND NICOBAR ISLANDS':0,'ANDHRA PRADESH':1,'ARUNACHAL PRADESH':2,'BIHAR':3,'CHHATTISGARH':4,'GUJARAT':5,
 'HIMACHAL PRADESH':6,'JAMMU AND KASHMIR':7,'JHARKHAND':8,'KARNATAKA':9,'KERALA':10,'MADHYA PRADESH':11,'MAHARASHTRA':12,
 'ODISHA':13,'PUNJAB':14,'RAJASTHAN':15,'TAMIL NADU':16,'TELANGANA':17,'UTTAR PRADESH':18,'UTTARAKHAND':19}
    d="Mumbai"
   
    try:
        AREA = int(st.sidebar.text_input("ENTER AREA OF FARM (HECTARES)")) 
    except:
        st.sidebar.write('Area needs to be numerical!')
        
    
    STATE= st.sidebar.selectbox('SELECT YOUR STATE',(s))
   
    if STATE==s[0]:
        an={'NICOBARS':0,  'NORTH AND MIDDLE ANDAMAN':1,  'SOUTH ANDAMANS':2}
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(an.keys()))
        r=rain.get(s[0])
        DISTRICT=an.get(d)
        season={'Autumn     ': 0, 'Kharif     ': 1, 'Rabi       ': 2, 'Whole Year ': 3}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON  ',list(season.keys())))
        crop={'Arecanut': 0, 'Arhar/Tur': 1, 'Banana': 2, 'Black pepper': 3, 'Cashewnut': 4, 'Coconut ': 5, 'Dry chillies': 6, 'Dry ginger': 7, 'Groundnut': 8, 'Maize': 9, 'Moong(Green Gram)': 10, 'Other Kharif pulses': 11, 'Rice': 12, 'Sugarcane': 13, 'Sunflower': 14, 'Sweet potato': 15, 'Tapioca': 16, 'Turmeric': 17, 'Urad': 18, 'other oilseeds': 19}
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='hi')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open("Andaman and Nicobar Islands.pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
                
    elif STATE==s[1]:
        ap={'ANANTAPUR':0, 'CHITTOOR':1,  'EAST GODAVARI':2, 'GUNTUR':3, 'KADAPA':4,  'KRISHNA':5,  'KURNOOL':6, 'PRAKASAM':7, 'SPSR NELLORE':8,  'SRIKAKULAM':9, 'VISAKHAPATANAM':10, 'VIZIANAGARAM':11, 'WEST GODAVARI':12}
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(ap.keys()))
        DISTRICT=ap.get(d)
        r=rain.get(s[1])
        season={'Kharif     ':0,  'Rabi       ':1,  'Whole Year ':2}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        crop={'Arecanut': 0, 'Arhar/Tur': 1, 'Bajra': 2, 'Banana': 3, 'Beans & Mutter(Vegetable)': 4, 'Bhindi': 5, 'Bottle Gourd': 6, 'Brinjal': 7, 'Cabbage': 8, 'Cashewnut': 9, 'Castor seed': 10, 'Citrus Fruit': 11, 'Coconut ': 12, 'Coriander': 13, 'Cotton(lint)': 14, 'Cowpea(Lobia)': 15, 'Cucumber': 16, 'Dry chillies': 17, 'Dry ginger': 18, 'Garlic': 19, 'Ginger': 20, 'Gram': 21, 'Grapes': 22, 'Groundnut': 23, 'Horse-gram': 24, 'Jowar': 25, 'Korra': 26, 'Lemon': 27, 'Linseed': 28, 'Maize': 29, 'Mango': 30, 'Masoor': 31, 'Mesta': 32, 'Moong(Green Gram)': 33, 'Niger seed': 34, 'Onion': 35, 'Orange': 36, 'Other  Rabi pulses': 37, 'Other Fresh Fruits': 38, 'Other Kharif pulses': 39, 'Other Vegetables': 40, 'Papaya': 41, 'Peas  (vegetable)': 42, 'Pome Fruit': 43, 'Pome Granet': 44, 'Potato': 45, 'Ragi': 46, 'Rapeseed &Mustard': 47, 'Rice': 48, 'Safflower': 49, 'Samai': 50, 'Sapota': 51, 'Sesamum': 52, 'Small millets': 53, 'Soyabean': 54, 'Sugarcane': 55, 'Sunflower': 56, 'Sweet potato': 57, 'Tapioca': 58, 'Tobacco': 59, 'Tomato': 60, 'Turmeric': 61, 'Urad': 62, 'Varagu': 63, 'Wheat': 64, 'other fibres': 65, 'other misc. pulses': 66, 'other oilseeds': 67}
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='te')  
        st.write(translate_text)
        #weather(d)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[1]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
            st.sidebar.write('Soil nutrients:')
            st.sidebar.write('Boron:0.468,Manganese:0.745,Copper:0.639, \n Iron:0.043,Zinc:0.511,Sulphur:0.34,Minor Nutrients:0.427,Degree of Nutrition:Low')
       
                
        
        
    elif STATE==s[2]:
        arp={ 'ANJAW':0,  'CHANGLANG':1, 'DIBANG VALLEY':2, 'EAST KAMENG':3,  'EAST SIANG':4, 'KURUNG KUMEY':5,  'LOHIT':6, 'LONGDING':7,  'LOWER DIBANG VALLEY':8,  'LOWER SUBANSIRI':9,  'NAMSAI':10,  'PAPUM PARE':11,  'TAWANG':12,  'TIRAP':13, 'UPPER SIANG':14, 'UPPER SUBANSIRI':15,  'WEST KAMENG':16,  'WEST SIANG':17}
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(arp.keys()))
        DISTRICT=arp.get(d)
        r=rain.get(s[2])
        season={'Kharif     ':0,  'Rabi       ':1,  'Whole Year ':2}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        crop={'Dry chillies': 0, 'Dry ginger': 1, 'Groundnut': 2, 'Maize': 3, 'Oilseeds total': 4, 'Potato': 5, 'Pulses total': 6, 'Rapeseed &Mustard': 7, 'Rice': 8, 'Sesamum': 9, 'Small millets': 10, 'Soyabean': 11, 'Sugarcane': 12, 'Sunflower': 13, 'Turmeric': 14, 'Wheat': 15}
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        st.write('Weclome to our state '+STATE) 
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[2]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
            st.sidebar.write('Soil nutrients:')
            st.sidebar.write('Boron:0.1,Manganese:0.6,Copper:0.5, \n Iron:0.75,Zinc:0.55,Sulphur:0.275,Minor Nutrients:0.496,Degree of Nutrition:Medium')
      
       
   
    elif STATE==s[3]:
        ass={'BAKSA':0,  'BARPETA':1, 'BONGAIGAON':2,  'CACHAR':3, 'CHIRANG':4, 'DARRANG':5,  'DHEMAJI':6, 'DHUBRI':7,  'DIBRUGARH':8,  'DIMA HASAO':9,  'GOALPARA':10, 'GOLAGHAT':11, 'HAILAKANDI':12,  'JORHAT':13,  'KAMRUP':14, 'KAMRUP METRO':15,  'KARBI ANGLONG':16, 'KARIMGANJ':17,  'KOKRAJHAR':18,  'LAKHIMPUR':19,  'MARIGAON':20,  'NAGAON':21,  'NALBARI':22,  'SIVASAGAR':23,  'SONITPUR':24,  'TINSUKIA':25,  'UDALGURI':26}
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(ass.keys()))
        DISTRICT=ass.get(d)
        season={'Autumn     ': 0, 'Kharif     ': 1, 'Rabi       ': 2, 'Summer     ': 3, 'Whole Year ': 4, 'Winter     ': 5}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        crop={'Arecanut': 0, 'Arhar/Tur': 1, 'Banana': 2, 'Black pepper': 3, 'Blackgram': 4, 'Castor seed': 5, 'Coconut ': 6, 'Cotton(lint)': 7, 'Dry chillies': 8, 'Dry ginger': 9, 'Ginger': 10, 'Gram': 11, 'Jute': 12, 'Linseed': 13, 'Maize': 14, 'Masoor': 15, 'Mesta': 16, 'Moong(Green Gram)': 17, 'Niger seed': 18, 'Onion': 19, 'Orange': 20, 'Other  Rabi pulses': 21, 'Paddy': 22, 'Papaya': 23, 'Peas & beans (Pulses)': 24, 'Pineapple': 25, 'Potato': 26, 'Rapeseed &Mustard': 27, 'Rice': 28, 'Sesamum': 29, 'Small millets': 30, 'Sugarcane': 31, 'Sweet potato': 32, 'Tapioca': 33, 'Tobacco': 34, 'Turmeric': 35, 'Urad': 36, 'Wheat': 37, 'other misc. pulses': 38}
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='hi')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[3]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            st.sidebar.write('Soil nutrients:')
            st.sidebar.write('Boron:0.029,Manganese:0.705,Copper:0.794, \n Iron:0.794,Zinc:0.794,Sulphur:0.397,Minor Nutrients:0.569,Degree of Nutrition:Medium')
            
       

    elif STATE==s[4]:
        b={'ARARIA':0,  'ARWAL':1, 'AURANGABAD':2, 'BANKA':3,  'BEGUSARAI':4, 'BHAGALPUR':5,  'BHOJPUR':6,  'BUXAR':7,  'DARBHANGA':8,  'GAYA':9,  'GOPALGANJ':10,  'JAMUI':11, 'JEHANABAD':12, 'KAIMUR (BHABUA)':13, 'KATIHAR':14, 'KHAGARIA':15, 'KISHANGANJ':16,  'LAKHISARAI':17,  'MADHEPURA':18,  'MADHUBANI':19, 'MUNGER':20,  'MUZAFFARPUR':21,  'NALANDA':22,  'NAWADA':23,  'PASHCHIM CHAMPARAN':24,  'PATNA':25,  'PURBI CHAMPARAN':26,  'PURNIA':27,  'ROHTAS':28,  'SAHARSA':29,  'SAMASTIPUR':30,  'SARAN':31, 'SHEIKHPURA':32,  'SHEOHAR':33,'SITAMARHI':34,  'SIWAN':35,  'SUPAUL':36, 'VAISHALI':37}
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(b.keys()))
        DISTRICT=b.get(d)
        r=rain.get(s[4])
        season={'Autumn     ': 0, 'Kharif     ': 1, 'Rabi       ': 2, 'Summer     ': 3, 'Whole Year ': 4, 'Winter     ': 5}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        crop={'Arhar/Tur': 0, 'Bajra': 1, 'Banana': 2, 'Barley': 3, 'Blackgram': 4, 'Castor seed': 5, 'Coriander': 6, 'Cotton(lint)': 7, 'Dry chillies': 8, 'Dry ginger': 9, 'Garlic': 10, 'Gram': 11, 'Groundnut': 12, 'Horse-gram': 13, 'Jowar': 14, 'Jute': 15, 'Khesari': 16, 'Linseed': 17, 'Maize': 18, 'Masoor': 19, 'Mesta': 20, 'Moong(Green Gram)': 21, 'Niger seed': 22, 'Onion': 23, 'Other  Rabi pulses': 24, 'Other Kharif pulses': 25, 'Peas & beans (Pulses)': 26, 'Potato': 27, 'Ragi': 28, 'Rapeseed &Mustard': 29, 'Rice': 30, 'Safflower': 31, 'Sannhamp': 32, 'Sesamum': 33, 'Small millets': 34, 'Sugarcane': 35, 'Sunflower': 36, 'Sweet potato': 37, 'Tobacco': 38, 'Turmeric': 39, 'Urad': 40, 'Wheat': 41}
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='hi')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[4]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
            st.sidebar.write('Soil nutrients:')
            st.sidebar.write('Boron:0.189,Manganese:0.189,Copper:0.162, \n Iron:0.757,Zinc:0.243,Sulphur:0.054,Minor Nutrients:0.253,Degree of Nutrition:Low')
            
       

    elif STATE==s[5]:
        c={'CHANDIGARH':0}
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(c.keys()))
        DISTRICT=c.get(d)
        season={'Kharif     ':0,  'Rabi       ':1,  'Whole Year ':2}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        crop={'Arhar/Tur': 0, 'Gram': 1, 'Maize': 2, 'Masoor': 3, 'Moong(Green Gram)': 4, 'Onion': 5, 'Potato': 6, 'Rapeseed &Mustard': 7, 'Rice': 8, 'Sunflower': 9, 'Urad': 10, 'Wheat': 11}
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='pa')  
        st.write(translate_text)
        
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[5]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
       
    elif STATE==s[6]:
        ch={'BALOD':0,  'BALODA BAZAR':1, 'BALRAMPUR':2,  'BASTAR':3,  'BEMETARA':4,  'BIJAPUR':5, 'BILASPUR':6,  'DANTEWADA':7,  'DHAMTARI':8,  'DURG':9,  'GARIYABAND':10, 'JANJGIR-CHAMPA':11, 'JASHPUR':12,  'KABIRDHAM':13,  'KANKER':14,  'KONDAGAON':15,  'KORBA':16,  'KOREA':17,  'MAHASAMUND':18,  'MUNGELI':19,  'NARAYANPUR':20,'RAIGARH':21, 'RAIPUR':22,  'RAJNANDGAON':23, 'SUKMA':24,  'SURAJPUR':25,  'SURGUJA':26}
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(ch.keys()))
        DISTRICT=ch.get(d)
        r=rain.get(s[6])
        season={'Kharif     ': 0, 'Rabi       ': 1, 'Summer     ': 2, 'Whole Year ': 3}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        crop={'Arhar/Tur': 0, 'Bajra': 1, 'Banana': 2, 'Barley': 3, 'Castor seed': 4, 'Coriander': 5, 'Cotton(lint)': 6, 'Dry chillies': 7, 'Dry ginger': 8, 'Garlic': 9, 'Gram': 10, 'Groundnut': 11, 'Guar seed': 12, 'Horse-gram': 13, 'Jowar': 14, 'Khesari': 15, 'Linseed': 16, 'Maize': 17, 'Masoor': 18, 'Mesta': 19, 'Moong(Green Gram)': 20, 'Niger seed': 21, 'Onion': 22, 'Other  Rabi pulses': 23, 'Other Kharif pulses': 24, 'Papaya': 25, 'Peas & beans (Pulses)': 26, 'Potato': 27, 'Ragi': 28, 'Rapeseed &Mustard': 29, 'Rice': 30, 'Safflower': 31, 'Sannhamp': 32, 'Sesamum': 33, 'Small millets': 34, 'Soyabean': 35, 'Sugarcane': 36, 'Sunflower': 37, 'Sweet potato': 38, 'Tobacco': 39, 'Turmeric': 40, 'Urad': 41, 'Wheat': 42, 'other misc. pulses': 43}
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='hi')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[6]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
            st.sidebar.write('Soil nutrients:')
            st.sidebar.write('Boron:0.857,Manganese:0.679,Copper:0.714, \n Iron:0.964,Zinc:0.957,Sulphur:0.411,Minor Nutrients:0.668,Degree of Nutrition:High')
            
      
    
    elif STATE==s[7]:
        dn={ 'DADRA AND NAGAR HAVELI':0}
        DISTRICT=dn.get(st.sidebar.selectbox('SELECT YOUR DISTRICT  ',list(dn.keys())))
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(dn.keys()))
        DISTRICT=dn.get(d)
        season={'Kharif     ': 0, 'Rabi       ': 1, 'Winter     ': 2}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        crop={'Arhar/Tur': 0, 'Banana': 1, 'Coconut ': 2, 'Coriander': 3, 'Gram': 4, 'Groundnut': 5, 'Jowar': 6, 'Maize': 7, 'Niger seed': 8, 'Other  Rabi pulses': 9, 'Other Kharif pulses': 10, 'Ragi': 11, 'Rapeseed &Mustard': 12, 'Rice': 13, 'Sannhamp': 14, 'Sesamum': 15, 'Small millets': 16, 'Sugarcane': 17, 'Sunflower': 18, 'Urad': 19, 'Wheat': 20}
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='gu')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[7]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
       

    elif STATE==s[8]:
        gujarat={'AHMADABAD':0, 'AMRELI':1, 'ANAND':2, 'BANAS KANTHA':3, 'BHARUCH':4, 'BHAVNAGAR':5, 'DANG':6,  'DOHAD':7, 'GANDHINAGAR':8,  'JAMNAGAR':9, 'JUNAGADH':10, 'KACHCHH':11,  'KHEDA':12, 'MAHESANA':13, 'NARMADA':14, 'NAVSARI':15,  'PANCH MAHALS':16, 'PATAN':17, 'PORBANDAR':18,  'RAJKOT':19, 'SABAR KANTHA':20, 'SURAT':21, 'SURENDRANAGAR':22,  'TAPI':23, 'VADODARA':24,  'VALSAD':25}
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(gujarat.keys()))
        DISTRICT=gujarat.get(d)
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='gu')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        r=rain.get(s[8])
        season={'Kharif     ': 0, 'Rabi       ': 1, 'Summer     ': 2, 'Whole Year ': 3}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        crop={'Arhar/Tur': 0, 'Bajra': 1, 'Banana': 2, 'Castor seed': 3, 'Cotton(lint)': 4, 'Dry chillies': 5, 'Garlic': 6, 'Gram': 7, 'Groundnut': 8, 'Guar seed': 9, 'Jowar': 10, 'Maize': 11, 'Moong(Green Gram)': 12, 'Moth': 13, 'Oilseeds total': 14, 'Onion': 15, 'Other  Rabi pulses': 16, 'Other Cereals & Millets': 17, 'Other Kharif pulses': 18, 'Potato': 19, 'Pulses total': 20, 'Ragi': 21, 'Rapeseed &Mustard': 22, 'Rice': 23, 'Sesamum': 24, 'Small millets': 25, 'Soyabean': 26, 'Sugarcane': 27, 'Tobacco': 28, 'Urad': 29, 'Wheat': 30, 'other oilseeds': 31}
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        model = pickle.load(open(s[8]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
            st.sidebar.write('Soil nutrients:')
            st.sidebar.write('Boron:0.971,Manganese:0.794,Copper:0.794, \n Iron:0.912,Zinc:1,Sulphur:0.471,Minor Nutrients:0.75,Degree of Nutrition:High')
            
    elif STATE==s[9]:
        haryana={'AMBALA':0, 'BHIWANI':1, 'FARIDABAD':2, 'FATEHABAD':3, 'GURGAON':4, 'HISAR':5, 'JHAJJAR':6, 'JIND':7, 'KAITHAL':8, 'KARNAL':9, 'KURUKSHETRA':10,'MAHENDRAGARH':11, 'MEWAT':12, 'PALWAL':13, 'PANCHKULA':14,'PANIPAT':15, 'REWARI':16, 'ROHTAK':17, 'SIRSA':18,  'SONIPAT':19, 'YAMUNANAGAR':20}
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(haryana.keys()))
        DISTRICT=haryana.get(d)
        season={'Kharif     ': 0, 'Rabi       ': 1, 'Whole Year ': 2}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        crop={'Arhar/Tur': 0, 'Bajra': 1, 'Banana': 2, 'Barley': 3, 'Castor seed': 4, 'Coriander': 5, 'Cotton(lint)': 6, 'Dry chillies': 7, 'Dry ginger': 8, 'Garlic': 9, 'Gram': 10, 'Grapes': 11, 'Groundnut': 12, 'Guar seed': 13, 'Horse-gram': 14, 'Jowar': 15, 'Maize': 16, 'Mango': 17, 'Masoor': 18, 'Moong(Green Gram)': 19, 'Moth': 20, 'Onion': 21, 'Other  Rabi pulses': 22, 'Other Fresh Fruits': 23, 'Other Kharif pulses': 24, 'Other Vegetables': 25, 'Peas & beans (Pulses)': 26, 'Potato': 27, 'Rapeseed &Mustard': 28, 'Rice': 29, 'Sannhamp': 30, 'Sesamum': 31, 'Sugarcane': 32, 'Sunflower': 33, 'Sweet potato': 34, 'Turmeric': 35, 'Urad': 36, 'Wheat': 37}
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='hi')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[9]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            st.sidebar.write('Soil nutrients:')
            st.sidebar.write('Boron: 0.773,Manganese:0.955,Copper:0.955, \n Iron:0.864,Zinc:0.955,Sulphur:0.477,Minor Nutrients:0.713,Degree of Nutrition:High')
           

    elif STATE==s[10]:
        hp={'BILASPUR':0, 'CHAMBA':1, 'HAMIRPUR':2, 'KANGRA':3, 'KINNAUR':4, 'KULLU':5,  'LAHUL AND SPITI':6,  'MANDI':7, 'SHIMLA':8,  'SIRMAUR':9, 'SOLAN':10, 'UNA':11}
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(hp.keys()))
        DISTRICT=hp.get(d)
        r=rain.get(s[10])
        season={'Kharif     ': 0, 'Rabi       ': 1, 'Whole Year ': 2}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        crop={'Arhar/Tur': 0, 'Bajra': 1, 'Barley': 2, 'Coriander': 3, 'Cotton(lint)': 4, 'Dry chillies': 5, 'Dry ginger': 6, 'Garlic': 7, 'Ginger': 8, 'Gram': 9, 'Groundnut': 10, 'Horse-gram': 11, 'Jowar': 12, 'Linseed': 13, 'Maize': 14, 'Masoor': 15, 'Moong(Green Gram)': 16, 'Moth': 17, 'Onion': 18, 'Other  Rabi pulses': 19, 'Other Kharif pulses': 20, 'Peas & beans (Pulses)': 21, 'Potato': 22, 'Ragi': 23, 'Rapeseed &Mustard': 24, 'Rice': 25, 'Sannhamp': 26, 'Sesamum': 27, 'Small millets': 28, 'Soyabean': 29, 'Sugarcane': 30, 'Tobacco': 31, 'Turmeric': 32, 'Urad': 33, 'Wheat': 34}
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
      
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='hi')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[10]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
       

    elif STATE==s[11]:
        jk={'ANANTNAG':0,  'BADGAM':1,  'BANDIPORA':2,  'BARAMULLA':3,  'DODA':4,  'GANDERBAL':5,  'JAMMU':6,  'KARGIL':7,  'KATHUA':8,  'KISHTWAR':9,  'KULGAM':10,  'KUPWARA':11,  'LEH LADAKH':12,  'POONCH':13,'PULWAMA':14,  'RAJAURI':15,  'RAMBAN':16, 'REASI':17,  'SAMBA':18,  'SHOPIAN':19,  'SRINAGAR':20,  'UDHAMPUR':21}
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(jk.keys()))
        DISTRICT=jk.get(d)
        r=rain.get(s[11])
        season={'Kharif     ': 0, 'Rabi       ': 1, 'Whole Year ': 2}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        crop={'Arhar/Tur': 0, 'Bajra': 1, 'Barley': 2, 'Beans & Mutter(Vegetable)': 3, 'Carrot': 4, 'Cond-spcs other': 5, 'Coriander': 6, 'Cotton(lint)': 7, 'Dry chillies': 8, 'Dry ginger': 9, 'Garlic': 10, 'Ginger': 11, 'Gram': 12, 'Groundnut': 13, 'Horse-gram': 14, 'Jowar': 15, 'Linseed': 16, 'Maize': 17, 'Masoor': 18, 'Moong(Green Gram)': 19, 'Moth': 20, 'Onion': 21, 'Other  Rabi pulses': 22, 'Other Cereals & Millets': 23, 'Other Fresh Fruits': 24, 'Other Kharif pulses': 25, 'Other Vegetables': 26, 'Peas & beans (Pulses)': 27, 'Potato': 28, 'Rapeseed &Mustard': 29, 'Redish': 30, 'Rice': 31, 'Sannhamp': 32, 'Sesamum': 33, 'Small millets': 34, 'Sugarcane': 35, 'Tobacco': 36, 'Turmeric': 37, 'Turnip': 38, 'Urad': 39, 'Wheat': 40, 'other oilseeds': 41}
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='hi')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[11]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
       
    
    elif STATE==s[12]:
        jhk={'BOKARO':0,  'CHATRA':1,  'DEOGHAR':2,  'DHANBAD':3,  'DUMKA':4, 'EAST SINGHBUM':5, 'GARHWA':6,  'GIRIDIH':7, 'GODDA':8,  'GUMLA':9,  'HAZARIBAGH':10,  'JAMTARA':11,  'KHUNTI':12,  'KODERMA':13,  'LATEHAR':14,  'LOHARDAGA':15,  'PAKUR':16,  'PALAMU':17,  'RAMGARH':18,  'RANCHI':19, 'SAHEBGANJ':20,  'SARAIKELA KHARSAWAN':21,  'SIMDEGA':22,  'WEST SINGHBHUM':23}
        r=rain.get(s[12])
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(jhk.keys()))
        DISTRICT=jhk.get(d)
        season={'Autumn     ': 0, 'Kharif     ': 1, 'Rabi       ': 2, 'Whole Year ': 3, 'Winter     ': 4}
        crop={'Arhar/Tur': 0, 'Barley': 1, 'Gram': 2, 'Maize': 3, 'Masoor': 4, 'Onion': 5, 'Potato': 6, 'Ragi': 7, 'Rapeseed &Mustard': 8, 'Rice': 9, 'Sugarcane': 10, 'Wheat': 11}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='hi')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[12]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
       

    elif STATE==s[13]:
        k={'BAGALKOT':0,  'BANGALORE RURAL':1,  'BELGAUM':2,  'BELLARY':3, 'BENGALURU URBAN':4,  'BIDAR':5,  'BIJAPUR':6,  'CHAMARAJANAGAR':7,  'CHIKBALLAPUR':8,  'CHIKMAGALUR':9,  'CHITRADURGA':10,  'DAKSHIN KANNAD':11,  'DAVANGERE':12,  'DHARWAD':13,  'GADAG':14,  'GULBARGA':15,  'HASSAN':16,  'HAVERI':17,  'KODAGU':18,  'KOLAR':19,  'KOPPAL':20, 'MANDYA':21, 'MYSORE':22,  'RAICHUR':23,  'RAMANAGARA':24,  'SHIMOGA':25,  'TUMKUR':26,  'UDUPI':27,  'UTTAR KANNAD':28,  'YADGIR':29}
       
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(k.keys()))
        r=rain.get(s[13])
        DISTRICT=k.get(d)
        season={'Kharif     ': 0, 'Rabi       ': 1, 'Summer     ': 2, 'Whole Year ': 3}
        crop={'Arcanut (Processed)': 0, 'Arecanut': 1, 'Arhar/Tur': 2, 'Atcanut (Raw)': 3, 'Bajra': 4, 'Banana': 5, 'Beans & Mutter(Vegetable)': 6, 'Black pepper': 7, 'Brinjal': 8, 'Cardamom': 9, 'Cashewnut': 10, 'Cashewnut Processed': 11, 'Cashewnut Raw': 12, 'Castor seed': 13, 'Citrus Fruit': 14, 'Coconut ': 15, 'Coriander': 16, 'Cotton(lint)': 17, 'Cowpea(Lobia)': 18, 'Dry chillies': 19, 'Dry ginger': 20, 'Garlic': 21, 'Gram': 22, 'Grapes': 23, 'Groundnut': 24, 'Horse-gram': 25, 'Jowar': 26, 'Linseed': 27, 'Maize': 28, 'Mango': 29, 'Mesta': 30, 'Moong(Green Gram)': 31, 'Niger seed': 32, 'Onion': 33, 'Other  Rabi pulses': 34, 'Other Fresh Fruits': 35, 'Other Kharif pulses': 36, 'Paddy': 37, 'Papaya': 38, 'Peas & beans (Pulses)': 39, 'Pome Fruit': 40, 'Potato': 41, 'Ragi': 42, 'Rapeseed &Mustard': 43, 'Rice': 44, 'Safflower': 45, 'Sannhamp': 46, 'Sesamum': 47, 'Small millets': 48, 'Soyabean': 49, 'Sugarcane': 50, 'Sunflower': 51, 'Sweet potato': 52, 'Tapioca': 53, 'Tobacco': 54, 'Tomato': 55, 'Turmeric': 56, 'Urad': 57, 'Wheat': 58}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='kn')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[13]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
       

    elif STATE==s[14]:
        ker={'ALAPPUZHA':0,  'ERNAKULAM':1,  'IDUKKI':2,  'KANNUR':3,  'KASARAGOD':4,  'KOLLAM':5,  'KOTTAYAM':6,  'KOZHIKODE':7,  'MALAPPURAM':8,  'PALAKKAD':9, 'PATHANAMTHITTA':10,  'THIRUVANANTHAPURAM':11, 'THRISSUR':12,  'WAYANAD':13}
        r=rain.get(s[14])
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(ker.keys()))
        DISTRICT=ker.get(d)
        season={'Autumn     ': 0, 'Kharif     ': 1, 'Summer     ': 2, 'Whole Year ': 3, 'Winter     ': 4}
        crop={'Arecanut': 0, 'Arhar/Tur': 1, 'Banana': 2, 'Bhindi': 3, 'Bitter Gourd': 4, 'Black pepper': 5, 'Brinjal': 6, 'Cardamom': 7, 'Cashewnut': 8, 'Cashewnut Raw': 9, 'Coconut ': 10, 'Coffee': 11, 'Cotton(lint)': 12, 'Drum Stick': 13, 'Dry chillies': 14, 'Dry ginger': 15, 'Garlic': 16, 'Groundnut': 17, 'Jack Fruit': 18, 'Jowar': 19, 'Maize': 20, 'Mango': 21, 'Other Cereals & Millets': 22, 'Other Fresh Fruits': 23, 'Other Vegetables': 24, 'Papaya': 25, 'Pineapple': 26, 'Potato': 27, 'Ragi': 28, 'Rice': 29, 'Rubber': 30, 'Sesamum': 31, 'Small millets': 32, 'Snak Guard': 33, 'Soyabean': 34, 'Sugarcane': 35, 'Sweet potato': 36, 'Tapioca': 37, 'Tea': 38, 'Tobacco': 39, 'Turmeric': 40, 'Wheat': 41, 'other oilseeds': 42}                   
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='ml')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[14]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
       
    
    elif STATE==s[15]:
        mp={ 'AGAR MALWA':0,  'ALIRAJPUR':1,  'ANUPPUR':2,  'ASHOKNAGAR':3,  'BALAGHAT':4,  'BARWANI':5,  'BETUL':6,'BHIND': 7 , 'BHOPAL':8 , 'BURHANPUR':9 ,  'CHHATARPUR':10,  'CHHINDWARA':11,  'DAMOH':12,  'DATIA':13,  'DEWAS':14, 'DHAR':15,  'DINDORI':16,  'GUNA':17,  'GWALIOR':18,  'HARDA':19, 'HOSHANGABAD':20,  'INDORE':21, 'JABALPUR':22,  'JHABUA':23, 'KATNI':24,  'KHANDWA':25,  'KHARGONE':26,  'MANDLA':27,  'MANDSAUR':28,  'MORENA':29,  'NARSINGHPUR':30,  'NEEMUCH':31,  'PANNA':32,  'RAISEN':33,  'RAJGARH':34,  'RATLAM':35,  'REWA':36,  'SAGAR':37,  'SATNA':38,  'SEHORE':39,  'SEONI':40,  'SHAHDOL':41,  'SHAJAPUR':42,  'SHEOPUR':43,  'SHIVPURI':44,  'SIDHI':45,  'SINGRAULI':46,  'TIKAMGARH':47,  'UJJAIN':48,  'UMARIA':49,  'VIDISHA':50}
        r=rain.get(s[15])
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(mp.keys()))
        DISTRICT=mp.get(d)
        season={'Kharif     ': 0, 'Rabi       ': 1, 'Whole Year ': 2}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        crop={'Arhar/Tur': 0, 'Bajra': 1, 'Banana': 2, 'Barley': 3, 'Beans & Mutter(Vegetable)': 4, 'Bhindi': 5, 'Brinjal': 6, 'Cabbage': 7, 'Cashewnut': 8, 'Castor seed': 9, 'Cauliflower': 10, 'Citrus Fruit': 11, 'Coriander': 12, 'Cotton(lint)': 13, 'Cowpea(Lobia)': 14, 'Dry chillies': 15, 'Dry ginger': 16, 'Garlic': 17, 'Gram': 18, 'Grapes': 19, 'Groundnut': 20, 'Horse-gram': 21, 'Jowar': 22, 'Jute': 23, 'Khesari': 24, 'Linseed': 25, 'Maize': 26, 'Mango': 27, 'Masoor': 28, 'Mesta': 29, 'Moong(Green Gram)': 30, 'Niger seed': 31, 'Onion': 32, 'Orange': 33, 'Other  Rabi pulses': 34, 'Other Citrus Fruit': 35, 'Other Fresh Fruits': 36, 'Other Kharif pulses': 37, 'Other Vegetables': 38, 'Paddy': 39, 'Papaya': 40, 'Peas & beans (Pulses)': 41, 'Pome Fruit': 42, 'Potato': 43, 'Ragi': 44, 'Rapeseed &Mustard': 45, 'Rice': 46, 'Safflower': 47, 'Sannhamp': 48, 'Sesamum': 49, 'Small millets': 50, 'Soyabean': 51, 'Sugarcane': 52, 'Sunflower': 53, 'Sweet potato': 54, 'Tobacco': 55, 'Tomato': 56, 'Turmeric': 57, 'Urad': 58, 'Water Melon': 59, 'Wheat': 60, 'other misc. pulses': 61}
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='hi')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[15]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
       
    
    elif STATE==s[16]:
        mah={ 'AHMEDNAGAR':0,  'AKOLA':1,  'AMRAVATI':2,  'AURANGABAD':3,  'BEED':4,  'BHANDARA':5,  'BULDHANA':6,  'CHANDRAPUR':7,  'DHULE':8,  'GADCHIROLI':9,  'GONDIA':10, 'HINGOLI':11,  'JALGAON':12, 'JALNA':13,  'KOLHAPUR':14,  'LATUR':15,  'MUMBAI':16,  'NAGPUR':17,  'NANDED':18,  'NANDURBAR':19,  'NASHIK':20, 'OSMANABAD':21, 'PALGHAR':22, 'PARBHANI':23,  'PUNE':24, 'RAIGAD':25, 'RATNAGIRI':26,  'SANGLI':27,  'SATARA':28,  'SINDHUDURG':29, 'SOLAPUR':30, 'THANE':31, 'WARDHA':32,  'WASHIM':33, 'YAVATMAL':34}
        r=rain.get(s[16])
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(mah.keys()))
        DISTRICT=mah.get(d)
        season={'Autumn     ': 0, 'Kharif     ': 1, 'Rabi       ': 2, 'Summer     ': 3, 'Whole Year ': 4}
        crop={'Arhar/Tur': 0, 'Bajra': 1, 'Banana': 2, 'Castor seed': 3, 'Cotton(lint)': 4, 'Gram': 5, 'Grapes': 6, 'Groundnut': 7, 'Jowar': 8, 'Linseed': 9, 'Maize': 10, 'Mango': 11, 'Moong(Green Gram)': 12, 'Niger seed': 13, 'Onion': 14, 'Other  Rabi pulses': 15, 'Other Cereals & Millets': 16, 'Other Kharif pulses': 17, 'Pulses total': 18, 'Ragi': 19, 'Rapeseed &Mustard': 20, 'Rice': 21, 'Safflower': 22, 'Sesamum': 23, 'Small millets': 24, 'Soyabean': 25, 'Sugarcane': 26, 'Sunflower': 27, 'Tobacco': 28, 'Tomato': 29, 'Total foodgrain': 30, 'Urad': 31, 'Wheat': 32, 'other oilseeds': 33}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome in '+STATE,lang_tgt='mr')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[16]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
            st.sidebar.write('Soil nutrients:')
            st.sidebar.write('Boron:0.914,Manganese:0.914,Copper:0.914, \n Iron:0.286,Zinc:0.571,Sulphur:0.4,Minor Nutrients:0.595,Degree of Nutrition:Medium')
           
    
    elif STATE==s[17]:
        mani={'BISHNUPUR':0,  'CHANDEL':1,  'CHURACHANDPUR':2,  'IMPHAL EAST':3,  'IMPHAL WEST':4,  'SENAPATI':5,  'TAMENGLONG':6,                   'THOUBAL':7,  'UKHRUL':8}
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(mani.keys()))
        DISTRICT=mani.get(d)
        season={'Autumn     ': 0, 'Kharif     ': 1, 'Rabi       ': 2, 'Summer     ': 3, 'Whole Year ': 4, 'Winter     ': 5}
        crop={'Arhar/Tur': 0, 'Banana': 1, 'Beans & Mutter(Vegetable)': 2, 'Bhindi': 3, 'Bitter Gourd': 4, 'Bottle Gourd': 5, 'Brinjal': 6, 'Cabbage': 7, 'Carrot': 8, 'Cashewnut': 9, 'Cauliflower': 10, 'Citrus Fruit': 11, 'Cotton(lint)': 12, 'Dry chillies': 13, 'Dry ginger': 14, 'Jack Fruit': 15, 'Jute': 16, 'Kapas': 17, 'Maize': 18, 'Mango': 19, 'Onion': 20, 'Orange': 21, 'Other Fresh Fruits': 22, 'Other Kharif pulses': 23, 'Other Vegetables': 24, 'Papaya': 25, 'Peas & beans (Pulses)': 26, 'Pineapple': 27, 'Pome Fruit': 28, 'Potato': 29, 'Rapeseed &Mustard': 30, 'Redish': 31, 'Rice': 32, 'Rubber': 33, 'Sesamum': 34, 'Soyabean': 35, 'Sugarcane': 36, 'Sweet potato': 37, 'Tapioca': 38, 'Tomato': 39, 'Turmeric': 40}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        st.write('Welcome to our state '+STATE) 
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[17]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
       
    
    elif STATE==s[18]:
        meg={'EAST GARO HILLS':0,  'EAST JAINTIA HILLS':1,  'EAST KHASI HILLS':2,  'NORTH GARO HILLS':3,  'RI BHOI':4,  'SOUTH GARO HILLS':5,  'SOUTH WEST GARO HILLS':6,  'SOUTH WEST KHASI HILLS':7,  'WEST GARO HILLS':8,  'WEST JAINTIA HILLS':9,  'WEST KHASI HILLS':10}
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(meg.keys()))
        DISTRICT=meg.get(d)
        season={'Autumn     ': 0, 'Kharif     ': 1, 'Rabi       ': 2, 'Summer     ': 3, 'Whole Year ': 4, 'Winter     ': 5}
        crop={'Arecanut': 0, 'Arhar/Tur': 1, 'Banana': 2, 'Black pepper': 3, 'Cashewnut': 4, 'Castor seed': 5, 'Citrus Fruit': 6, 'Coriander': 7, 'Cotton(lint)': 8, 'Cowpea(Lobia)': 9, 'Dry chillies': 10, 'Dry ginger': 11, 'Garlic': 12, 'Gram': 13, 'Jute': 14, 'Kapas': 15, 'Linseed': 16, 'Maize': 17, 'Masoor': 18, 'Mesta': 19, 'Oilseeds total': 20, 'Other  Rabi pulses': 21, 'Papaya': 22, 'Peas & beans (Pulses)': 23, 'Pineapple': 24, 'Potato': 25, 'Pulses total': 26, 'Rapeseed &Mustard': 27, 'Rice': 28, 'Sesamum': 29, 'Small millets': 30, 'Soyabean': 31, 'Sugarcane': 32, 'Sweet potato': 33, 'Tapioca': 34, 'Tobacco': 35, 'Total foodgrain': 36, 'Turmeric': 37, 'Wheat': 38}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        st.write('Welcome to our state '+STATE)  
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[18]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
       

    elif STATE==s[19]:
        miz={'AIZAWL':0,  'CHAMPHAI':1,  'KOLASIB':2, 'LAWNGTLAI':3,  'LUNGLEI':4,  'MAMIT':5,  'SAIHA':6,  'SERCHHIP':7}
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(miz.keys()))
        DISTRICT=miz.get(d)
        season={'Kharif     ': 0, 'Rabi       ': 1, 'Whole Year ': 2}
        crop={'Arhar/Tur': 0, 'Coconut ': 1, 'Cotton(lint)': 2, 'Gram': 3, 'Groundnut': 4, 'Kapas': 5, 'Maize': 6, 'Masoor': 7, 'Moong(Green Gram)': 8, 'Other  Rabi pulses': 9, 'Other Kharif pulses': 10, 'Peas & beans (Pulses)': 11, 'Potato': 12, 'Rapeseed &Mustard': 13, 'Rice': 14, 'Sesamum': 15, 'Soyabean': 16, 'Sugarcane': 17, 'Sunflower': 18, 'Tapioca': 19, 'Tobacco': 20, 'Urad': 21, 'Wheat': 22, 'other oilseeds': 23}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        st.write('Welcome to our state '+STATE)  
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[19]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
       
    
    elif STATE==s[20]:
        n={ 'DIMAPUR':0,  'KIPHIRE':1,  'KOHIMA':2,  'LONGLENG':3, 'MOKOKCHUNG':4,  'MON':5,  'PEREN':6,  'PHEK':7,  'TUENSANG':8,  'WOKHA':9, 'ZUNHEBOTO':10}
        
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(n.keys()))
        DISTRICT=n.get(d)
        season={'Kharif     ': 0, 'Rabi       ': 1, 'Whole Year ': 2}
        crop={'Arhar/Tur': 0, 'Bajra': 1, 'Barley': 2, 'Bean': 3, 'Blackgram': 4, 'Cardamom': 5, 'Castor seed': 6, 'Colocosia': 7, 'Cotton(lint)': 8, 'Cowpea(Lobia)': 9, 'Dry chillies': 10, 'Dry ginger': 11, 'Ginger': 12, 'Gram': 13, 'Groundnut': 14, 'Horse-gram': 15, 'Jobster': 16, 'Jowar': 17, 'Jute': 18, 'Lentil': 19, 'Linseed': 20, 'Maize': 21, 'Masoor': 22, 'Mesta': 23, 'Moong(Green Gram)': 24, 'Niger seed': 25, 'Oilseeds total': 26, 'Other  Rabi pulses': 27, 'Other Kharif pulses': 28, 'Peas & beans (Pulses)': 29, 'Perilla': 30, 'Potato': 31, 'Ragi': 32, 'Rajmash Kholar': 33, 'Rapeseed &Mustard': 34, 'Rice': 35, 'Ricebean (nagadal)': 36, 'Sesamum': 37, 'Small millets': 38, 'Soyabean': 39, 'Sugarcane': 40, 'Sunflower': 41, 'Sweet potato': 42, 'Tapioca': 43, 'Tea': 44, 'Turmeric': 45, 'Urad': 46, 'Wheat': 47}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        st.write('Welcome to our state '+STATE)  
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[20]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
       
    
    elif STATE==s[21]:
        o={'ANUGUL':0,  'BALANGIR':1,  'BALESHWAR':2, 'BARGARH':3,  'BHADRAK':4, 'BOUDH':5,  'CUTTACK':6,  'DEOGARH':7,  'DHENKANAL':8,  'GAJAPATI':9,  'GANJAM':10,  'JAGATSINGHAPUR':11,  'JAJAPUR':12,  'JHARSUGUDA':13,  'KALAHANDI':14,  'KANDHAMAL':15,  'KENDRAPARA':16,  'KENDUJHAR':17,  'KHORDHA':18,  'KORAPUT':19,  'MALKANGIRI':20,  'MAYURBHANJ':21,  'NABARANGPUR':22,  'NAYAGARH':23,  'NUAPADA':24,  'PURI':25,  'RAYAGADA':26,  'SAMBALPUR':27,  'SONEPUR':28,  'SUNDARGARH':29}
       
        r=rain.get(s[21])
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(o.keys()))
        DISTRICT=o.get(d)
        season={'Autumn     ': 0, 'Kharif     ': 1, 'Rabi       ': 2, 'Summer     ': 3, 'Whole Year ': 4, 'Winter     ': 5}
        crop={'Arhar/Tur': 0, 'Bajra': 1, 'Castor seed': 2, 'Coriander': 3, 'Cotton(lint)': 4, 'Dry chillies': 5, 'Dry ginger': 6, 'Garlic': 7, 'Gram': 8, 'Groundnut': 9, 'Horse-gram': 10, 'Jowar': 11, 'Jute': 12, 'Linseed': 13, 'Maize': 14, 'Masoor': 15, 'Mesta': 16, 'Moong(Green Gram)': 17, 'Niger seed': 18, 'Onion': 19, 'Other  Rabi pulses': 20, 'Other Kharif pulses': 21, 'Paddy': 22, 'Potato': 23, 'Ragi': 24, 'Rapeseed &Mustard': 25, 'Rice': 26, 'Safflower': 27, 'Sannhamp': 28, 'Sesamum': 29, 'Small millets': 30, 'Soyabean': 31, 'Sugarcane': 32, 'Sunflower': 33, 'Sweet potato': 34, 'Tobacco': 35, 'Turmeric': 36, 'Urad': 37, 'Wheat': 38}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        st.write('Welcome to our state '+STATE)  
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[21]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} mm'.format(rainfall))
       
    elif STATE==s[22]:
        p= {'KARAIKAL':0, 'MAHE':1,  'PONDICHERRY':2,  'YANAM':3}
        
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(p.keys()))
        DISTRICT=p.get(d)
        season={'Autumn     ': 0, 'Kharif     ': 1, 'Rabi       ': 2, 'Summer     ': 3, 'Whole Year ': 4, 'Winter     ': 5}
        crop={'Arecanut': 0, 'Bajra': 1, 'Banana': 2, 'Black pepper': 3, 'Brinjal': 4, 'Cashewnut': 5, 'Coconut ': 6, 'Coriander': 7, 'Cotton(lint)': 8, 'Dry chillies': 9, 'Dry ginger': 10, 'Groundnut': 11, 'Jowar': 12, 'Mango': 13, 'Moong(Green Gram)': 14, 'Onion': 15, 'Other  Rabi pulses': 16, 'Other Cereals & Millets': 17, 'Other Kharif pulses': 18, 'Paddy': 19, 'Ragi': 20, 'Rapeseed &Mustard': 21, 'Rice': 22, 'Sesamum': 23, 'Small millets': 24, 'Sugarcane': 25, 'Sunflower': 26, 'Sweet potato': 27, 'Tapioca': 28, 'Turmeric': 29, 'Urad': 30}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='ta')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[22]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
       
    
    elif STATE==s[23]:
        pa={ 'AMRITSAR':0,  'BARNALA':1,  'BATHINDA':2,  'FARIDKOT':3,  'FATEHGARH SAHIB':4,  'FAZILKA':5,  'FIROZEPUR':6,  'GURDASPUR':7,  'HOSHIARPUR':8,  'JALANDHAR':9,  'KAPURTHALA':10,  'LUDHIANA':11,  'MANSA':12,  'MOGA':13,  'MUKTSAR':14,  'NAWANSHAHR':15,  'PATHANKOT':16,  'PATIALA':17,  'RUPNAGAR':18,  'S.A.S NAGAR':19,  'SANGRUR':20,  'TARN TARAN':21}
        r=rain.get(s[23])
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(pa.keys()))
        DISTRICT=pa.get(d)
        season={'Kharif     ': 0, 'Rabi       ': 1, 'Whole Year ': 2}
        crop={'Arhar/Tur': 0, 'Bajra': 1, 'Barley': 2, 'Cotton(lint)': 3, 'Gram': 4, 'Groundnut': 5, 'Guar seed': 6, 'Jowar': 7, 'Linseed': 8, 'Maize': 9, 'Masoor': 10, 'Moong(Green Gram)': 11, 'Moth': 12, 'Other  Rabi pulses': 13, 'Peas & beans (Pulses)': 14, 'Rapeseed &Mustard': 15, 'Rice': 16, 'Sesamum': 17, 'Sugarcane': 18, 'Sunflower': 19, 'Urad': 20, 'Wheat': 21}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='pa')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[23]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
       
    
    elif STATE==s[24]:
        r={ 'AJMER':0,  'ALWAR':1,  'BANSWARA':2,  'BARAN':3,  'BARMER':4,  'BHARATPUR':5,  'BHILWARA':6,  'BIKANER':7, 'BUNDI':8,  'CHITTORGARH':9,  'CHURU':10,  'DAUSA':11,  'DHOLPUR':12, 'DUNGARPUR':13,  'GANGANAGAR':14,  'HANUMANGARH':15,  'JAIPUR':16,  'JAISALMER':17,  'JALORE':18,  'JHALAWAR':19,  'JHUNJHUNU':20,  'JODHPUR':21,  'KARAULI':22,  'KOTA':23,  'NAGAUR':24,  'PALI':25,  'PRATAPGARH':26,  'RAJSAMAND':27,  'SAWAI MADHOPUR':28, 'SIKAR':29,  'SIROHI':30,  'TONK':31,  'UDAIPUR':32}
        r=rain.get(s[24])
        DISTRICT=r.get(st.sidebar.selectbox('SELECT YOUR DISTRICT ',list(r.keys())))
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(r.keys()))
        DISTRICT=r.get(d)
        season={'Kharif     ': 0, 'Rabi       ': 1, 'Whole Year ': 2}
        crop={'Arhar/Tur': 0, 'Bajra': 1, 'Banana': 2, 'Barley': 3, 'Castor seed': 4, 'Citrus Fruit': 5, 'Coriander': 6, 'Cotton(lint)': 7, 'Dry chillies': 8, 'Dry ginger': 9, 'Garlic': 10, 'Gram': 11, 'Grapes': 12, 'Groundnut': 13, 'Guar seed': 14, 'Jowar': 15, 'Linseed': 16, 'Maize': 17, 'Mango': 18, 'Masoor': 19, 'Mesta': 20, 'Moong(Green Gram)': 21, 'Moth': 22, 'Oilseeds total': 23, 'Onion': 24, 'Orange': 25, 'Other  Rabi pulses': 26, 'Other Fresh Fruits': 27, 'Other Kharif pulses': 28, 'Other Vegetables': 29, 'Papaya': 30, 'Peas & beans (Pulses)': 31, 'Pome Fruit': 32, 'Potato': 33, 'Rapeseed &Mustard': 34, 'Rice': 35, 'Sannhamp': 36, 'Sesamum': 37, 'Small millets': 38, 'Soyabean': 39, 'Sugarcane': 40, 'Sunflower': 41, 'Sweet potato': 42, 'Tapioca': 43, 'Tobacco': 44, 'Turmeric': 45, 'Urad': 46, 'Water Melon': 47, 'Wheat': 48, 'other fibres': 49, 'other oilseeds': 50}

        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='hi')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[24]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} mm'.format(rainfall))
       
    
    elif STATE==s[25]:
        tn={'ARIYALUR': 0, 'COIMBATORE': 1, 'CUDDALORE': 2, 'DHARMAPURI': 3, 'DINDIGUL': 4, 'ERODE': 5, 'KANCHIPURAM': 6, 'KANNIYAKUMARI': 7, 'KARUR': 8, 'KRISHNAGIRI': 9, 'MADURAI': 10, 'NAGAPATTINAM': 11, 'NAMAKKAL': 12, 'PERAMBALUR': 13, 'PUDUKKOTTAI': 14, 'RAMANATHAPURAM': 15, 'SALEM': 16, 'SIVAGANGA': 17, 'THANJAVUR': 18, 'THE NILGIRIS': 19, 'THENI': 20, 'THIRUVALLUR': 21, 'THIRUVARUR': 22, 'TIRUCHIRAPPALLI': 23, 'TIRUNELVELI': 24, 'TIRUPPUR': 25, 'TIRUVANNAMALAI': 26, 'TUTICORIN': 27, 'VELLORE': 28, 'VILLUPURAM': 29, 'VIRUDHUNAGAR': 30}
        r=rain.get(s[25])
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(tn.keys()))
        DISTRICT=tn.get(d)
        season={'Kharif     ': 0, 'Rabi       ': 1, 'Whole Year ': 2}
        crop={'Apple': 0, 'Arecanut': 1, 'Arhar/Tur': 2, 'Ash Gourd': 3, 'Bajra': 4, 'Banana': 5, 'Beans & Mutter(Vegetable)': 6, 'Beet Root': 7, 'Ber': 8, 'Bhindi': 9, 'Bitter Gourd': 10, 'Black pepper': 11, 'Bottle Gourd': 12, 'Brinjal': 13, 'Cabbage': 14, 'Cardamom': 15, 'Carrot': 16, 'Cashewnut': 17, 'Castor seed': 18, 'Cauliflower': 19, 'Citrus Fruit': 20, 'Coconut ': 21, 'Coriander': 22, 'Cotton(lint)': 23, 'Cucumber': 24, 'Drum Stick': 25, 'Dry chillies': 26, 'Dry ginger': 27, 'Garlic': 28, 'Gram': 29, 'Grapes': 30, 'Groundnut': 31, 'Guar seed': 32, 'Horse-gram': 33, 'Jack Fruit': 34, 'Jowar': 35, 'Korra': 36, 'Lab-Lab': 37, 'Litchi': 38, 'Maize': 39, 'Mango': 40, 'Mesta': 41, 'Moong(Green Gram)': 42, 'Onion': 43, 'Orange': 44, 'Other Cereals & Millets': 45, 'Other Citrus Fruit': 46, 'Other Fresh Fruits': 47, 'Other Kharif pulses': 48, 'Other Vegetables': 49, 'Papaya': 50, 'Peach': 51, 'Pear': 52, 'Pineapple': 53, 'Plums': 54, 'Pome Fruit': 55, 'Pome Granet': 56, 'Potato': 57, 'Pulses total': 58, 'Pump Kin': 59, 'Ragi': 60, 'Rapeseed &Mustard': 61, 'Redish': 62, 'Ribed Guard': 63, 'Rice': 64, 'Samai': 65, 'Sannhamp': 66, 'Sesamum': 67, 'Small millets': 68, 'Snak Guard': 69, 'Sugarcane': 70, 'Sunflower': 71, 'Sweet potato': 72, 'Tapioca': 73, 'Tobacco': 74, 'Tomato': 75, 'Total foodgrain': 76, 'Turmeric': 77, 'Turnip': 78, 'Urad': 79, 'Varagu': 80, 'Water Melon': 81, 'Wheat': 82, 'Yam': 83}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='ta')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[25]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
       
    
    elif STATE==s[26]:
        tel={ 'ADILABAD':0, 'HYDERABAD':1,  'KARIMNAGAR':2,  'KHAMMAM':3,  'MAHBUBNAGAR':4,  'MEDAK':5,  'NALGONDA':6,  'NIZAMABAD':7,  'RANGAREDDI':8, 'WARANGAL':9}
        r=rain.get(s[26])
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(tel.keys()))
        DISTRICT=tel.get(d)
        season={'Kharif     ': 0, 'Rabi       ': 1, 'Whole Year ': 2}
        crop={'Arhar/Tur': 0, 'Bajra': 1, 'Banana': 2, 'Beans & Mutter(Vegetable)': 3, 'Bhindi': 4, 'Bottle Gourd': 5, 'Brinjal': 6, 'Cabbage': 7, 'Cashewnut': 8, 'Castor seed': 9, 'Citrus Fruit': 10, 'Coconut ': 11, 'Coriander': 12, 'Cotton(lint)': 13, 'Cowpea(Lobia)': 14, 'Cucumber': 15, 'Dry chillies': 16, 'Dry ginger': 17, 'Garlic': 18, 'Ginger': 19, 'Gram': 20, 'Grapes': 21, 'Groundnut': 22, 'Horse-gram': 23, 'Jowar': 24, 'Korra': 25, 'Linseed': 26, 'Maize': 27, 'Mango': 28, 'Masoor': 29, 'Mesta': 30, 'Moong(Green Gram)': 31, 'Niger seed': 32, 'Onion': 33, 'Orange': 34, 'Other  Rabi pulses': 35, 'Other Dry Fruit': 36, 'Other Fresh Fruits': 37, 'Other Kharif pulses': 38, 'Other Vegetables': 39, 'Papaya': 40, 'Peas  (vegetable)': 41, 'Pome Fruit': 42, 'Potato': 43, 'Ragi': 44, 'Rapeseed &Mustard': 45, 'Rice': 46, 'Safflower': 47, 'Samai': 48, 'Sesamum': 49, 'Small millets': 50, 'Soyabean': 51, 'Sugarcane': 52, 'Sunflower': 53, 'Sweet potato': 54, 'Tapioca': 55, 'Tobacco': 56, 'Tomato': 57, 'Turmeric': 58, 'Urad': 59, 'Varagu': 60, 'Wheat': 61, 'other fibres': 62, 'other misc. pulses': 63, 'other oilseeds': 64}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='te')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[26]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
       
     
    elif STATE==s[27]:
        tri={'DHALAI':0,  'GOMATI':1,  'KHOWAI':2,  'NORTH TRIPURA':3,  'SEPAHIJALA':4,  'SOUTH TRIPURA':5,  'UNAKOTI':6,  'WEST TRIPURA':7}
       
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(tri.keys()))
        DISTRICT=tri.get(d)
        season={'Kharif     ': 0, 'Rabi       ': 1, 'Whole Year ': 2}
        crop={'Arhar/Tur': 0, 'Cotton(lint)': 1, 'Gram': 2, 'Groundnut': 3, 'Jute': 4, 'Jute & mesta': 5, 'Maize': 6, 'Masoor': 7, 'Mesta': 8, 'Moong(Green Gram)': 9, 'Oilseeds total': 10, 'Other  Rabi pulses': 11, 'Other Kharif pulses': 12, 'Peas & beans (Pulses)': 13, 'Potato': 14, 'Rapeseed &Mustard': 15, 'Rice': 16, 'Sesamum': 17, 'Sugarcane': 18, 'Urad': 19, 'Wheat': 20, 'other oilseeds': 21}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='bn')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[27]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
       
    
    elif STATE==s[28]:
        up={'AGRA': 0,'ALIGARH': 1,'ALLAHABAD': 2,'AMBEDKAR NAGAR': 3,'AMETHI': 4,'AMROHA': 5,'AURAIYA': 6,'AZAMGARH': 7,'BAGHPAT': 8,
 'BAHRAICH': 9,'BALLIA': 10,'BALRAMPUR': 11,'BANDA': 12,'BARABANKI': 13,'BAREILLY': 14,'BASTI': 15,'BIJNOR': 16,'BUDAUN': 17,
 'BULANDSHAHR': 18,'CHANDAULI': 19,'CHITRAKOOT': 20,'DEORIA': 21,'ETAH': 22,'ETAWAH': 23,'FAIZABAD': 24,'FARRUKHABAD': 25,
 'FATEHPUR': 26,'FIROZABAD': 27,'GAUTAM BUDDHA NAGAR': 28,'GHAZIABAD': 29,'GHAZIPUR': 30,'GONDA': 31,'GORAKHPUR': 32,'HAMIRPUR': 33,
 'HAPUR': 34,'HARDOI': 35,'HATHRAS': 36,'JALAUN': 37,'JAUNPUR': 38,'JHANSI': 39,'KANNAUJ': 40,'KANPUR DEHAT': 41,'KANPUR NAGAR': 42,
 'KASGANJ': 43,'KAUSHAMBI': 44,'KHERI': 45,'KUSHI NAGAR': 46,'LALITPUR': 47,'LUCKNOW': 48,'MAHARAJGANJ': 49,'MAHOBA': 50,'MAINPURI': 51,
 'MATHURA': 52,'MAU': 53,'MEERUT': 54,'MIRZAPUR': 55,'MORADABAD': 56,'MUZAFFARNAGAR': 57,'PILIBHIT': 58,'PRATAPGARH': 59,'RAE BARELI': 60,
 'RAMPUR': 61,'SAHARANPUR': 62,'SAMBHAL': 63,'SANT KABEER NAGAR': 64,'SANT RAVIDAS NAGAR': 65,'SHAHJAHANPUR': 66,'SHAMLI': 67,
 'SHRAVASTI': 68,'SIDDHARTH NAGAR': 69,'SITAPUR': 70,'SONBHADRA': 71,'SULTANPUR': 72,'UNNAO': 73,'VARANASI': 74}
        r=rain.get(s[28])
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(up.keys()))
        DISTRICT=up.get(d)
        season={'Kharif     ': 0, 'Rabi       ': 1, 'Summer     ': 2, 'Whole Year ': 3}
        crop={'Arhar/Tur': 0, 'Bajra': 1, 'Banana': 2, 'Barley': 3, 'Castor seed': 4, 'Coriander': 5, 'Cotton(lint)': 6, 'Dry chillies': 7, 'Dry ginger': 8, 'Garlic': 9, 'Ginger': 10, 'Gram': 11, 'Groundnut': 12, 'Guar seed': 13, 'Jowar': 14, 'Jute': 15, 'Linseed': 16, 'Maize': 17, 'Masoor': 18, 'Moong(Green Gram)': 19, 'Moth': 20, 'Oilseeds total': 21, 'Onion': 22, 'Other  Rabi pulses': 23, 'Other Kharif pulses': 24, 'Peas & beans (Pulses)': 25, 'Potato': 26, 'Ragi': 27, 'Rapeseed &Mustard': 28, 'Rice': 29, 'Sannhamp': 30, 'Sesamum': 31, 'Small millets': 32, 'Soyabean': 33, 'Sugarcane': 34, 'Sunflower': 35, 'Sweet potato': 36, 'Tobacco': 37, 'Total foodgrain': 38, 'Turmeric': 39, 'Urad': 40, 'Wheat': 41}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='hi')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[28]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
       
    
    elif STATE==s[29]:
        uk={'ALMORA': 0, 'BAGESHWAR': 1, 'CHAMOLI': 2, 'CHAMPAWAT': 3, 'DEHRADUN': 4, 'HARIDWAR': 5, 'NAINITAL': 6, 'PAURI GARHWAL': 7, 'PITHORAGARH': 8, 'RUDRA PRAYAG': 9, 'TEHRI GARHWAL': 10, 'UDAM SINGH NAGAR': 11, 'UTTAR KASHI': 12}
        r=rain.get(s[29])
        d=st.sidebar.selectbox('SELECT YOUR DISTRICT :  ',list(uk.keys()))
        DISTRICT=uk.get(d)
        season={'Kharif     ': 0, 'Rabi       ': 1, 'Summer     ': 2, 'Whole Year ': 3}
        crop={'Arhar/Tur': 0, 'Bajra': 1, 'Barley': 2, 'Dry chillies': 3, 'Dry ginger': 4, 'Garlic': 5, 'Ginger': 6, 'Gram': 7, 'Groundnut': 8, 'Horse-gram': 9, 'Jowar': 10, 'Lentil': 11, 'Linseed': 12, 'Maize': 13, 'Masoor': 14, 'Moong(Green Gram)': 15, 'Moth': 16, 'Onion': 17, 'Other  Rabi pulses': 18, 'Other Cereals & Millets': 19, 'Other Kharif pulses': 20, 'Peas & beans (Pulses)': 21, 'Potato': 22, 'Pulses total': 23, 'Ragi': 24, 'Rapeseed &Mustard': 25, 'Rice': 26, 'Sannhamp': 27, 'Sesamum': 28, 'Small millets': 29, 'Soyabean': 30, 'Sugarcane': 31, 'Sunflower': 32, 'Tobacco': 33, 'Total foodgrain': 34, 'Turmeric': 35, 'Urad': 36, 'Wheat': 37, 'other oilseeds': 38}
        SEASON=season.get(st.sidebar.selectbox('SELECT THE SEASON ',list(season.keys())))
        CROP=crop.get(st.sidebar.selectbox('SELECT THE CROP  ',list(crop.keys())))
        translate_text = translator.translate('Welcome to our state '+STATE,lang_tgt='hi')  
        st.write(translate_text)
        data=get_weather_data(d)
        print_weather(data)
        model = pickle.load(open(s[29]+".pkl", "rb"))
        if st.sidebar.button("Predict"):
            features =[AREA,DISTRICT,SEASON,CROP]
            predict= yieldpred(model,features)
            production=round(float(predict),2)
            y=round(production/float(AREA),2)
            st.sidebar.write('Production : {} tonnes \n\n Yield : {} tonnes/hectares'.format(production,y))
            rainfall=predrainfall(r)
            st.sidebar.write('Annual rainfall is {} cm'.format(rainfall))
       
     
   

    imagee = cv2.imread(r'C:\Users\AASTHA\Desktop\agri.png')
    cv2.imshow('Image', imagee)
    st.image(imagee,width=800)


if __name__ == '__main__':
 
   
    main()
     

     

     
     

    
    
   
    
    

  
  
    
    




    
    
        
        
        
      
    
    
    
    
    
    
  

    
    

    

