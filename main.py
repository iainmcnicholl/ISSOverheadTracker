import requests
import geocoder
import datetime as dt
import smtplib
import time
import schedule

#global variables
current_lat = 0
current_lng = 0
sunset_time = 0
sunrise_time = 0
my_email = ""
password = "" #password to be added with email. Adjust email server based on sender
receiving_email = ""


#retrieve current location and save lat lng coords
def get_current_location():
    global current_lat, current_lng
    current_location = geocoder.ip(location="me")
    current_lat = int(current_location.latlng[0])
    current_lng = int(current_location.latlng[1])

#request for sunrise / set data, stored as sunset data json, set sunset / rise hour as int for comparison
def get_sundown_time():
    global sunrise_time, sunset_time
    sun_set_response = requests.get(url=f"https://api.sunrise-sunset.org/json? lat={current_lat}&lng={current_lng}&formatted=0")
    sun_set_response.raise_for_status()
    sunset_data = sun_set_response.json()
    sunrise_time = int(sunset_data['results']['sunrise'][11:13])
    sunset_time = int(sunset_data['results']['sunset'][11:13])


#get current time and set current hour as int for comparison
def get_current_hour():
    now = dt.datetime.now()
    current_time = now.time()
    current_hour = int(str(current_time)[0:2])
    return current_hour

#function if ISS is overhead, and sundown, send email to notify
def iss_overhead ():
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()

    data = response.json()

    latitude = int(float(data["iss_position"]["latitude"]))
    longitude = int(float(data["iss_position"]["longitude"]))
    if sunset_time < get_current_hour() <= 23 and sunrise_time > get_current_hour() >= 0:
        if latitude == current_lat and longitude == current_lng:
            with smtplib.SMTP("smtp.mail.yahoo.com") as connection: #update smtp based on sender email
                connection.starttls()
                connection.login(user=my_email, password=password)
                connection.sendmail(
                    from_addr=my_email,
                    to_addrs=receiving_email,
                    msg=f"Subject: ISS Is Overhead!! \n\nQuick, look up!"
                )
    else:
        print(f"The ISS lat lng is {(latitude,longitude)}\n Your location is {current_lat,current_lng}")

while True:
    get_current_location()
    get_sundown_time()
    get_current_hour()
    iss_overhead()
    time.sleep(60)


