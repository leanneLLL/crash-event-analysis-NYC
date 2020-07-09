import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px



DATA_URL = (
"/Users/binglin/Desktop/project/Motor_Vehicle_Collisions_-_Crashes.csv"
)

st.image("/Users/binglin/Desktop/project/images/title_imag.png",use_column_width = True)
# st.title("🗽 Motor Vehicle Collisions in New York City ")
st.markdown("> A Dashboard for analyzing motor vehicle collisions in New York city🗽💥🏎️")
st.write("In order to visualize the distributions of crash events in NYC"
        "I decided to create an application allowing for exploration of this data"
        "Moreover, I felt this was a nice opportunity to see how much various information"
        "can be extracted from this dataset."
        )
st.write("The data in this application is from Open Data NY - NY.gov."
        "Data last updated on July 8, 2020"
        "More information about this data can be found here: "
)
st.write("https://data.ny.gov/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95")


@st.cache(persist = True)
def load_data(nrows):   # load & display data
    data = pd.read_csv(DATA_URL, nrows = nrows, parse_dates = [['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset = ['LATITUDE','LONGITUDE'], inplace = True) # drop values in specific columns
    lowercase = lambda x: str(x).lower() # lowercase function
    data.rename(lowercase, axis = 'columns', inplace = True)
    data.rename(columns = {'crash_date_crash_time':'date/time'}, inplace = True) # using dictionary format
    return data

data = load_data(100000)
original_data = data
st.sidebar.title("Menu")
app_mode = st.sidebar.selectbox("Please select a page",["Homepage",
                                                        "Raw Data"])



# location based on # map visualization
st.header("📍Crash Event Locations ")
injured_people = st.slider("Number of injured pepple in accident:",0,19) #range for the slider, pre checked by the author
st.map(data.query("injured_persons >= @injured_people")[["latitude","longitude"]].dropna(how = "any")) # plot using map


# top dangerous street to travel /injured the most
st.header("⚠️Top 5 Dangerous Streets")
select = st.selectbox('Affected type of people',['Pedestrians','Cyclists','Motorists'])
if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name","injured_pedestrians"]].sort_values(by = ['injured_pedestrians'],ascending = False).dropna(how = 'any')[:5])
elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name","injured_cyclists"]].sort_values(by = ['injured_cyclists'],ascending = False).dropna(how = 'any')[:5])
else :
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name","injured_motorists"]].sort_values(by = ['injured_motorists'],ascending = False).dropna(how = 'any')[:5])


# collisions based on time
st.header("⏲️Number of Collisions in a specific time period ")
# hour  = st.sidebar.slider("Hour to look at",0,23)
hour  = st.slider("Hour to look at",0,23)
data = data[data['date/time'].dt.hour == hour]
st.markdown("Vehicle collisions between %i:00 and %i:00" %(hour, (hour+1) %24))

midpoint  = (np.average(data['latitude']), np.average(data['longitude']))       # initial coordinate for the initial view state

st.write(pdk.Deck(# Another initial view map
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {# initialize using dictionary formaty
        "latitude" : midpoint[0],
        "longitude" : midpoint[1],
        "zoom"  : 11,
        "pitch" : 50,
    }, #don't forget the comma here

    layers = [  # Add layer on top of the initial view map
        pdk.Layer(
        "HexagonLayer",
        data = data[['date/time','latitude','longitude']],
        get_position = ['longitude','latitude'],
        radius = 100,
        extruded = True, # to make the map 3D view
        pickable = True,
        elevation_scale = 4,
        elevation_range = [0,1000],
        ),
    ],
))

# graph distrubution breakdown
st.subheader("📊Breakdown by minute between %i:00 and %i:00" %(hour,(hour+1) %24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour+1))
]
hist = np.histogram(filtered['date/time'].dt.minute,bins = 60, range = (0,60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(chart_data, x = 'minute', y = 'crashes', hover_data = ['minute', 'crashes'], height = 400)
st.write(fig)











# diaplay data on application
if st.checkbox("Show Raw Data",False): # Hide raw data by defaut, use checkbox
    st.subheader('Raw Data')
    st.write(data)
