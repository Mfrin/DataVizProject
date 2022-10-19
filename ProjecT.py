from tkinter import CENTER, Y
from turtle import title
import streamlit as st
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import altair as alt

####################################################
#IMPORTANT
# During the wholeproject, i continued using a dataset called Osaka while it is in fact talking about kyoto.
# I had some plans talking about Osaka at the start but then i changed my mind but the dataset was already called like that.
# I apologize about that
####################################################

st.set_page_config(layout="wide")
st.markdown("---")
st.title('My holidays in Japan :sunglasses:')


filepath = "C:/Users/marti/Documents/L4M1/Data_Visualization/2019_APRIL.json"

# here is the function that allows me to store the data from the json file to a standard pandas dataframe
def maps(filepath):
    place_visits = []
    activity_segments = []
    float_coordinates = 10000000

    with open(filepath, "r", encoding='UTF-8') as file:
        data = json.load(file)
        for instance in data['timelineObjects']:
            if 'placeVisit' in instance:
                single_visit = instance['placeVisit']
                try:# a try ... except is required because some field are missing a 'name' making the programm stop whenever it encounters one. 
                    # Without a name, these datas would be less meaningfull so i prefer getting rid of some rather than continue without any name
                    place_visit = { 
                        "latitude": single_visit['location']['latitudeE7']/float_coordinates,
                        "longitude": single_visit['location']['longitudeE7']/float_coordinates,
                        "iD": single_visit['location']['placeId'],
                        "location_confidence": single_visit['location']['locationConfidence'],
                        "name": single_visit['location']['name'],
                        "time_start": single_visit['duration']['startTimestamp'],
                        "time_end": single_visit['duration']['endTimestamp']
                    }
                    place_visits.append(place_visit)
                except KeyError:
                    print("error")
            else:# we also check for the activyties because they are really interesting to combine with the visits.
                single_visit = instance['activitySegment']

                activity_segment = {
                    "start_latitude": single_visit['startLocation']['latitudeE7']/float_coordinates,
                    "start_longitude": single_visit['startLocation']['longitudeE7']/float_coordinates,
                    "end_latitude": single_visit['endLocation']['latitudeE7']/float_coordinates,
                    "end_longitude": single_visit['endLocation']['longitudeE7']/float_coordinates,
                    "time_start": single_visit['duration']['startTimestamp'],
                    "time_end": single_visit['duration']['endTimestamp'],
                    "distance": single_visit['distance'],
                    "mean": single_visit['activityType']
                    }   
                activity_segments.append(activity_segment)

    return pd.DataFrame(place_visits), pd.DataFrame(activity_segments)# finnaly we return two dataframes, one for the visits and one for the activities


visits, activity = maps(filepath)

# here we create some functions that will help us transforming dates to easier to use columns.
def get_day(dt):
    return(dt.day)
def get_weekday(dt):
    return(dt.weekday())
def get_hours(dt):
    return(dt.hour)

#Now we correct the datframe for the visits
def correct_datasets(visits, activity):
    
    df_japon = visits[visits['longitude'] >= 100]# this line allows me to get only the datas from japan and not before or after
    # here we will convert the different time columns to better formats
    df_japon["time_end"] = pd.to_datetime(df_japon["time_end"])
    df_japon["time_start"] = pd.to_datetime(df_japon["time_start"])



    df_japon["day_start"] = df_japon["time_start"].map(get_day)
    df_japon["weekday_start"] = df_japon["time_start"].map(get_weekday)
    df_japon["hour_start"] = df_japon["time_start"].map(get_hours)

    df_japon["day_end"] = df_japon["time_end"].map(get_day)
    df_japon["weekday_end"] = df_japon["time_end"].map(get_weekday)
    df_japon["hour_end"] = df_japon["time_end"].map(get_hours)


    df_japon['total_time'] = (df_japon['time_end'] - df_japon['time_start'])/pd.Timedelta(hours=1)
    df_japon['name'] = df_japon['name'].astype('string')
    print(df_japon.info())

    df_Osaka = df_japon[df_japon['longitude'] <= 136]
    df_Osaka = df_Osaka[df_Osaka['latitude'] >= 35]
    df_Tokyo = df_japon[df_japon['longitude'] >= 137]

    #Now ce create our dataframes for the activities
    df_japon2 = activity[activity['start_longitude'] >= 100]
    df_japon2["time_end"] = pd.to_datetime(df_japon["time_end"])
    df_japon2["time_start"] = pd.to_datetime(df_japon["time_start"])


    df_japon2["day_start"] = df_japon2["time_start"].map(get_day)
    df_japon2["weekday_start"] = df_japon2["time_start"].map(get_weekday)
    df_japon2["hour_start"] = df_japon2["time_start"].map(get_hours)

    df_japon2["day_end"] = df_japon2["time_end"].map(get_day)
    df_japon2["weekday_end"] = df_japon2["time_end"].map(get_weekday)
    df_japon2["hour_end"] = df_japon2["time_end"].map(get_hours)

    df_japon2['total_time'] = (df_japon2['time_end'] - df_japon2['time_start'])/pd.Timedelta(hours=1)

    df_Osaka2 = df_japon2[df_japon2['start_longitude'] <= 136]#these filter represents Kyoto
    df_Osaka2 = df_Osaka2[df_Osaka2['start_latitude'] >= 35]
    df_Tokyo2 = df_japon2[df_japon2['start_longitude'] >= 137]
    df_Tokyo2 = df_Tokyo2.iloc[0:-1]
    
    df_Tokyo2['cumulative_sum'] = df_Tokyo2['distance'].cumsum()
    df_Tokyo2['cumulative_sum'] = df_Tokyo2['cumulative_sum']/1000
    return(df_japon,df_japon2,df_Osaka,df_Osaka2,df_Tokyo,df_Tokyo2)

df_japon,df_japon2,df_Osaka,df_Osaka2,df_Tokyo,df_Tokyo2 = correct_datasets(visits,activity)
#Now we begin the app for real

#we will start by making scatter maps of all japan, kyoto and tokyo. We will also insert some pictures next to it to make it better.
col1, col2 = st.columns([2,1])

with col1:
    option = st.selectbox(
        'Maps of our visits',
        ['All','Kyoto','Tokyo'])

    if (option == 'All'):
        df_map = df_japon[['latitude','longitude']]
        st.map(df_map) 
    elif (option == 'Kyoto'):
        df_map = df_Osaka[['latitude','longitude']]
        st.map(df_map) 
    else:
        df_map = df_Tokyo[['latitude','longitude']]
        st.map(df_map) 

#Here i have an unsovable problem. Either these pictures appear on the streamlit but make VS bugs 
#                                   either i take the absolute path but they stop working on streamlit

with col2:
    if (option == 'All'):
        st.image("images/fuji.jpg")
    elif (option == 'Kyoto'):
        st.image("images/tori.webp")
    else:
        st.image("images/tower.webp")
        
st.markdown("***")
st.title('Discovering Kyoto ⛩️')
# here we set a bar chart that will compare the amount of travel and the different means by day and by hour
option2 = st.selectbox(
        'Select the timestamp ',
        ['By day','By hour'])
if (option2 == 'By day'):
    bar_chart = alt.Chart(df_Osaka2).mark_bar(size=60).encode(# here is the code for the /day
            x="day_start",
            y="distance",
            color="mean"
        ).properties(
        width=800,
        height=300)
    st.altair_chart(bar_chart, use_container_width=True) 
else :
    bar_chart = alt.Chart(df_Osaka2).mark_bar(size=4).encode(#and here is the code for the /hour
                x="time_start",
                y="distance",
                color="mean"
            ).properties(
            width=800,
            height=300)
    st.altair_chart(bar_chart, use_container_width=True) 
    
# now we are creating a dataset that will calculate the top total_times in our Osaka dataset to take the 
df_Osaka_6 = df_Osaka.sort_values('total_time').tail(14)
df_Osaka_6 = df_Osaka_6.iloc[0:-3]# we toss the 3 first because they represent the hotel and so they are not interesting compared to the rest
 
slideropt = st.select_slider(# the client chooses the number of places to show
     'Select the number of places on the chart',
     options = [1,2,3,4,5,6,7,8,9,10])


bar_chart = alt.Chart(df_Osaka_6.iloc[-slideropt-1:-1]).mark_bar(size=12).encode(
                alt.X("total_time:Q"),
                alt.Y("name", sort= '-x'),
                color = alt.Color('total_time:N', sort = '-x', legend = None)# we show all the graph and sort them from top to bottom while keeping the same color for each place
            ).properties(
            width=1210,
            height=300)

st.altair_chart(bar_chart, use_container_width=False)
     
st.markdown("***")
st.title("Let's go to Tokyo ! 🗼")# Let's goooo !


col1b, col2b= st.columns([2,1])# we start by creating the grid for our next observation

with col1b:#the first one is a simple line_chart with different time and the cumulative sum of the distance traveled by us
    st.line_chart(data = df_Tokyo2, x = 'time_start', y = 'cumulative_sum', height = 500, width=500)   
with col2b:# the second one is a pie chart where we will compare the efficiency of different travel means and the time we spend on them.
    option3 = st.selectbox(
        'Activity types',
        ['By distance','By time'])
    
    if (option3 == 'By distance'):
        st.write("Activity type repartition by distance", fontweight = "bold")
        
        sizes = df_Tokyo2.groupby('mean')['distance'].sum()
        labels= ['Bus','Subway','Train','Walking']
        
        fig1, ax1 = plt.subplots()
        
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1)
        
    elif (option3 == 'By time'):
        st.write("Activity type repartition by time", fontweight = "bold")
        
        sizes = df_Tokyo2.groupby('mean')['total_time'].sum()
        labels= ['Bus','Subway','Train','Walking']
        
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        
        st.pyplot(fig1)
#note, the code are similar but i couldn't figure a way to make dynamics column layout 
if st.button('Reset'):
    print("ok")
t1, t2, t3, t4, t5 = st.columns(5)# here we are creating the layout for our top 5 picks
   
def stlbar(df1,name):# first we start by creating the function that will show the scatter plots
    print("ok")
    bar_chart = alt.Chart(df1).mark_point().encode(
    alt.X("location_confidence:Q"),
    alt.Y('total_time',sort = '-x'),
    # The highlight will be set on the result of a conditional statement
    color=alt.condition(
        alt.datum.name == name,  # If the year is 1810 this test returns True,
        alt.value('orange'),     # which sets the bar orange.
        alt.value('steelblue')   # And if it's not true it sets the bar steelblue.
    )
    ).properties(width=1200, )
    
    st.altair_chart(bar_chart, use_container_width=True)
        
def get_df1(df_Tokyo):  # then we create a function to reorganize our datasets
    df = df_Tokyo[df_Tokyo['name'] == 'Takeshita Street']
    df1 = df_Tokyo.groupby('name').sum()
    
    print(df1,df1.iloc[:,2],df1.iloc[:,-1])

    df1 = pd.DataFrame({'name': df1.index, 'location_confidence': df1.iloc[:,2], 'total_time' : df1.iloc[:,-1]})
    df1 = df1[df1['name'] != 'Shiba Park']
    return(df1)

df1 = get_df1(df_Tokyo)
with t1: #finally we repeat 5 time the operation to get our layout working
    if st.button('Takeshita Street'):
        df = df_Tokyo[df_Tokyo['name'] == 'Takeshita Street']
        print("df : ",df)
        df_map = df[['latitude','longitude']]
        st.map(df_map)
        st.write("Link between time spend and accuracy")
        stlbar(df1,'Takeshita Street')
    else:
        st.image("images/take.webp")
        
with t2:
    if st.button('Tokyo Tower'):
        df = df_Tokyo[df_Tokyo['name'] == 'Tokyo Tower']
        print("df : ",df)
        df_map = df[['latitude','longitude']]
        st.map(df_map) 
        st.write("Link between time spend and accuracy")
        stlbar(df1,'Tokyo Tower')
    else:
        st.image("images/toktow.jpg")
        
with t3:
    if st.button('Don Quijote Roppongi'):
        df = df_Tokyo[df_Tokyo['name'] == 'Don Quijote Roppongi']
        print("df : ",df)
        df_map = df[['latitude','longitude']]
        st.map(df_map) 
        st.write("Link between time spend and accuracy")
        stlbar(df1,'Don Quijote Roppongi')
    else:
        st.image("images/don.jpg")
        
with t4:
    if st.button('Shinjuku Gyoen National Garden'):
        df = df_Tokyo[df_Tokyo['name'] == 'Shinjuku Gyoen National Garden']
        print("df : ",df)
        df_map = df[['latitude','longitude']]
        st.map(df_map) 
        st.write("Link between time spend and accuracy")
        stlbar(df1,'Shinjuku Gyoen National Garden')
    else:
        st.image("images/goyen.jpg")
        
with t5:
    if st.button('Shibuya Crossing'):
        df = df_Tokyo[df_Tokyo['name'] == 'Shibuya Crossing']
        print("df : ",df)
        df_map = df[['latitude','longitude']]
        st.map(df_map)
        st.write("Link between time spend and accuracy")
        stlbar(df1,'Shibuya Crossing') 
    else:
        st.image("images/shib.jpg")
        
        
st.markdown("---")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.title("I hope you enjoyed the trip ! 🎉🎉🎉")