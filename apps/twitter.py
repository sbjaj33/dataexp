#Credentials for twitter API
consumer_key = 'KQIxS8N8eXag4sV4qb69gGDUn'
consumer_secret = 'Iz4kKCnd5XCFwLLJsEXxVyQzySOsQLSPu9H54oQ7GppMMvCw75'
access_token = '1359060451036831746-bw0UGcIajrInIEWhbL5AvmEEZNrV7B'
access_token_secret = 'JOJ9K88ybrjNHuNnyPi5bGfZJ1kOG4zFhwzjZ0WLfDVp2'
#libraries import
import tweepy
import streamlit as st
import numpy as np
import pandas as pd
from textblob import TextBlob
import plotly as py
import plotly.graph_objs as go
import plotly.express as px
import re
import base64
import matplotlib.pyplot as plt
import pycountry
import pydeck as pdk
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim

def app():
    def filedownload(df, filename):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download={filename}>Download {filename} File</a>'
        return href
    st.image('twitter.png',width=280)
    st.title('Twitter Ananlysis App')
    auth=tweepy.OAuthHandler(consumer_key,consumer_secret)
    auth.set_access_token(access_token,access_token_secret)
    api=tweepy.API(auth)
    data = st.sidebar.text_input("Keyword Input")
    location = st.sidebar.text_input("Location Input","Global")
    count1 = st.sidebar.slider("Tweet Count",0,1000,300,50)

    df=pd.DataFrame(columns=['Tweets', 'User', 'User_statuses_count', 'user_followers', 'User_location', 'User_verified','fav_count', 'rt_count', 'tweet_date'])
    def FillupData(data,count1):
        i=0
        st.info("Tweets are being extracted to DataFrame ")
        for tweet in tweepy.Cursor(api.search,q=data,count=count1,lang='en').items():
            df.loc[i, 'Tweets'] = tweet.text
            df.loc[i, 'User'] = tweet.user.name
            df.loc[i, 'User_statuses_count'] = tweet.user.statuses_count
            df.loc[i, 'user_followers'] = tweet.user.followers_count
            df.loc[i, 'User_location'] = tweet.user.location
            df.loc[i, 'User_verified'] = tweet.user.verified
            df.loc[i, 'fav_count'] = tweet.favorite_count
            df.loc[i, 'rt_count'] = tweet.retweet_count
            df.loc[i, 'tweet_date'] = tweet.created_at
            i+=1
            if i==count1:
                break
            else:
                pass
    if len(data)!=0:

        FillupData(data,count1)
        st.markdown('**Raw Tweets Dataset**')
        st.write(df)
        st.markdown(filedownload(df,'Rawtweets.csv'), unsafe_allow_html=True)
        def clean_tweet(tweet):
            return ' '.join(re.sub('(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)', ' ', tweet).split())
        #Analyzing Sentiment with TextBlob (polarity one)
        def analyze_sentiment(tweet):
            analysis = TextBlob(tweet)
            if analysis.sentiment.polarity > 0:
                return 'Positive'
            elif analysis.sentiment.polarity ==0:
                return 'Neutral'
            else:
                return 'Negative'

        #cleaning tweets
        st.info("Cleaning tweets data from dataset")
        df['clean_tweet'] = df['Tweets'].apply(lambda x: clean_tweet(x))
        st.markdown('**Cleaned Tweets Dataset**')
        st.write(df)
        st.markdown(filedownload(df,'Cleantweets.csv'), unsafe_allow_html=True)
        st.markdown('**Tweets cleaning example **')
        st.write("Raw tweet")
        st.write(df['Tweets'][0]);
        st.write("cleaned tweet")
        st.write(df['clean_tweet'][0]);

        st.markdown('**Sentiment Analysis Report**')
        df['Sentiment'] = df['clean_tweet'].apply(lambda x: analyze_sentiment(x))
        if location!='Global':
            temp=location+"n"
            df[temp]=np.zeros(len(df['User_location']))
            for i in range(len(df['User_location'])):
                if df['User_location'][i].find(location)!=-1:
                    df[temp][i]=1

            df=df[df[temp]==1]
        st.write(df[['User','clean_tweet','Sentiment']])
        f = px.histogram(df, x="Sentiment", nbins=20, title="Overall Sentiments Distribution ({}),{}".format(data,location),color="Sentiment")
        f.update_xaxes(title="Sentiment")
        f.update_yaxes(title="Sentiment Count")
        f1 = px.histogram(df, x="Sentiment", nbins=20, title="Overall Sentiments Distribution ({}),{}".format(data,location),color="User_verified")
        f1.update_xaxes(title="Sentiment")
        f1.update_yaxes(title="Sentiment Count")
        st.plotly_chart(f)
        st.plotly_chart(f1)
        postweet=len(df[df['Sentiment']=='Positive'])
        negtweet=len(df[df['Sentiment']=='Negative'])
        total=len(df['Sentiment'])
        posper=postweet*100/total
        negper=negtweet*100/total
        neuper=100*(total-(postweet+negtweet))/total
        label = ['Positive','Negative','Neutral']
        data1 = [posper,negper,neuper]
        df1=pd.DataFrame(label,columns=['name'])
        df1['value']=data1
        # Creating plot
        st.markdown('**Pie chart representation of overall sentiment percentage**')
        fg = px.pie(df1, values='value', names='name')
        st.plotly_chart(fg)
        if location=='Global':
            longitude = []
            latitude = []
            def findGeocode(city):

                # try and catch is used to overcome
                # the exception thrown by geolocator
                # using geocodertimedout
                try:

                    # Specify the user_agent as your
                    # app name it should not be none
                    geolocator = Nominatim(user_agent="Data_Exp",timeout=10)
                    return geolocator.geocode(city)

                except GeocoderTimedOut:
                    return findGeocode(city)


            df['locn']=np.zeros(len(df['User_location']))
            for i in range(len(df['User_location'])):
                df['locn'][i]=df['User_location'][i].split(',')[-1]
            for i in (df['locn']):

                if findGeocode(i) != None:

                    loc = findGeocode(i)

                    # coordinates returned from
                    # function is stored into
                    # two separate list
                    latitude.append((loc.latitude))
                    longitude.append((loc.longitude))

                # if coordinate for a city not
                # found, insert "NaN" indicating
                # missing value
                else:
                    latitude.append(np.nan)
                    longitude.append(np.nan)
            df["lon"] = longitude
            df["lat"] = latitude
            st.markdown(' ')
            st.markdown('**Dataset with longitude and latitude values**')
            st.markdown(' ')
            st.write(df)
        # midpoint = (np.average(df['lat']), np.average(df['lon']))

        # st.pydeck_chart(
        #         viewport={
        #             'latitude': midpoint[0],
        #             'longitude':  midpoint[1],
        #             'zoom': 4
        #         },
        #         layers=[{
        #             'type': 'ScatterplotLayer',
        #             'data': df,
        #             'radiusScale': 250,
        #             'radiusMinPixels': 5,
        #             'getFillColor': [248, 24, 148],
        #         }]
        #     )
        # datageo=df[['lat','lon']]
        # st.write(datageo)
        # r=(pdk.Deck(
        # map_style='mapbox://styles/mapbox/light-v9',
        #  initial_view_state=pdk.ViewState(
        #      latitude=20.5937,
        #      longitude=78.9629,
        #      zoom=4,
        #      pitch=50,
        #  ),
        #  layers=[
        #      pdk.Layer(
        #          'ScatterplotLayer',
        #          data=datageo,
        #          get_position='[lon, lat]',
        #          get_color='[200, 30, 0, 160]',
        #          get_radius=200,
        #          ),
        #          ],
        #     ))
        # st.pydeck_chart(r)
        # geolocator = Nominatim(user_agent="my_request")
        #
        # #applying the rate limiter wrapper
        # geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

        #Applying the method to pandas DataFrame

        # df['location'] = df['User_location'].apply(geocode)
        # df['lat'] = df['location'].apply(lambda x: x.latitude if x else 0)
        # df['lon'] = df['location'].apply(lambda x: x.longitude if x else 0)
        # s.write(df[['lat','lon']])
        # midpoint = (np.average(df["lat"]), np.average(df["lon"]))
        #
        # st.write(pdk.Deck(
        #     initial_view_state ={
        #         "latitude": midpoint[0],
        #         "longitude": midpoint[1],
        #         "zoom": 11,
        #         "pitch": 50,
        #     },
        #     layers =[
        #         pdk.Layer(
        #         "HexagonLayer",
        #         data = df[['User_location', 'lat', 'lon']],
        #         get_position =["lon", "lat"],
        #         auto_highlight = True,
        #         radius = 100,
        #         extruded = True,
        #         pickable = True,
        #         elevation_scale = 4,
        #         elevation_range =[0, 1000],
        #         ),
        #     ],
        # ))

            st.markdown(' ')
            st.markdown('**Geoplot visualization of tweets source country**')
            st.markdown(' ')
            st.map(df[["lat", "lon"]].dropna(how ="any"))
    else:
        st.info('''Awaiting for keyword to be entered''')
    # layer = pdk.Layer(
    # 'HexagonLayer',  # `type` positional argument is here
    # datageo,
    # get_position=['lon', 'lat'],
    # auto_highlight=True,
    # elevation_scale=50,
    # pickable=True,
    # elevation_range=[0, 3000],
    # extruded=True,
    # coverage=1)


    # layer = pdk.Layer(
    # 'ScatterplotLayer',     # Change the `type` positional argument here
    # datageo,
    # get_position=['lon', 'lat'],
    # auto_highlight=True,
    # get_radius=1000,          # Radius is given in meters
    # get_fill_color=[180, 0, 200, 140],  # Set an RGBA value for fill
    # pickable=True)
    # # Set the viewport location
    # view_state = pdk.ViewState(
    # longitude=-1.415,
    # latitude=52.2323,
    # zoom=2,
    # min_zoom=5,
    # max_zoom=15,
    # pitch=40.5,
    # bearing=-27.36)
    #
    #     # Combined all of it and render a viewport
    # r = pdk.Deck(layers=[layer], initial_view_state=view_state)
    # st.pydeck_chart(r)


    # layer = pdk.Layer(
    # "HexagonLayer",
    # datageo,
    # get_position="[lon, lat]",
    # auto_highlight=True,
    # elevation_scale=50,
    # pickable=True,
    # elevation_range=[0, 3000],
    # extruded=True,
    # coverage=1,
    # )
    #
    # # Set the viewport location
    # view_state = pdk.ViewState(
    #     longitude=-1.415, latitude=52.2323, zoom=6, min_zoom=5, max_zoom=15, pitch=40.5, bearing=-27.36
    # )
    #
    # # Combined all of it and render a viewport
    # r = pdk.Deck(
    #     map_style="mapbox://styles/mapbox/light-v9",
    #     layers=[layer],
    #     initial_view_state=view_state,
    #     tooltip={"html": "<b>Elevation Value:</b> {elevationValue}", "style": {"color": "white"}},
    # )
    # #r.to_html("test.html", open_browser=True, notebook_display=False)
    # st.pydeck_chart(r)

    # layer = pdk.Layer(
    #     "ScatterplotLayer",
    #     datageo,
    #     pickable=True,
    #     opacity=0.8,
    #     stroked=True,
    #     filled=True,
    #     radius_scale=6,
    #     radius_min_pixels=1,
    #     radius_max_pixels=100,
    #     line_width_min_pixels=1,
    #     get_position="[lon,lat]",
    #     get_fill_color=[255, 140, 0],
    #     get_line_color=[0, 0, 0],
    # )
    #
    # # Set the viewport location
    # view_state = pdk.ViewState(latitude=37.7749295, longitude=-122.4194155, zoom=10, bearing=0, pitch=0)
    #
    # # Render
    # r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{name}\n{address}"})
    # st.pydeck_chart(r)
