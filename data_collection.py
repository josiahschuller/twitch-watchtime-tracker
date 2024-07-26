#from twitchio.ext import commands
from urllib import request
import requests, json, time, csv, datetime

#Headers for API requests
CLIENT_ID = "REDACTED"
SECRET = "REDACTED"
authFile = open("auth.txt", "r")
AUTH = authFile.read()
HEADERS = {
    'Client-ID':CLIENT_ID,
    'Authorization':AUTH
}

def get_new_access_token():
    #This function generates a new app access token,
    #saves it to AUTH.txt and updates HEADERS
    global HEADERS, AUTH
    url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={SECRET}&grant_type=client_credentials"
    response = requests.post(url)
    output = json.dumps(response.json())
    AUTH = 'Bearer ' + json.loads(output)["access_token"]

    #Write AUTH to auth.txt
    authFile = open("auth.txt", "w")
    authFile.write(AUTH)
    
    HEADERS = {
        'Client-ID':CLIENT_ID,
        'Authorization':AUTH
    }
    print(f"{datetime.datetime.now()}    New app access token generated")
    

def get_channel_id(channel):
    #This function finds the id of a given channel
    url = f'https://api.twitch.tv/helix/users?login={channel}'
    response = json.loads(json.dumps(requests.get(url, headers=HEADERS).json()))
    #Check if app access token (AUTH) is outdated
    if "error" in response:
        #Get a new app access token
        get_new_access_token()
        
        channel_id = get_channel_id(channel)
    else:
        channel_id = response['data'][0]['id']
        print(f"{datetime.datetime.now()}    Query Twitch API for channel ID")
    return channel_id

def is_live(channel_id):
    #Determine if channel is live
    url = f'https://api.twitch.tv/helix/streams?user_id={channel_id}'
    response = requests.get(url, headers=HEADERS)
    output = json.loads(json.dumps(response.json()))['data']
    return False if len(output) == 0 else True

def viewer_list(channel):
    #Get list of viewers
    url = f"http://tmi.twitch.tv/group/user/{channel}/chatters"
    #print(f"{datetime.datetime.now()} start")
    data = json.loads(request.urlopen(url).read().decode("UTF-8"))["chatters"]
    #print(f"{datetime.datetime.now()} middle")
    viewers = data["viewers"]
    mods = data["moderators"]
    vips = data["vips"]
    #print(f"{datetime.datetime.now()} end")

    viewers_mods = sort_sorted_lists(viewers, mods, "add")
    viewers_total = sort_sorted_lists(viewers_mods, vips, "add")

    #Remove bots from list
    bots = ['anotherttvviewer', 'commanderroot', 'fossabot', 'moobot', 'nightbot',
            'randomtwitchstats', 'rewardtts', 'simonsaysbot',
            'squarkbot', 'streamelements', 'streamlabs', 'supibot',
            'thehungrypumpkin', 'thepositivebot', 'twitchprimereminder']

    viewers_total = sort_sorted_lists(viewers_total, bots, "remove")
    
    return viewers_total

def sort_sorted_lists(bigList,smallList,task):
    #This function is used in the viewer_list function
    index = 0
    for sIndex in range(len(smallList)):
        if index < len(bigList):
            for bIndex in range(index, len(bigList)):
                if task == "add":
                    if smallList[sIndex] < bigList[bIndex]:
                        bigList.insert(bIndex, smallList[sIndex])
                        index = bIndex
                        break
                    elif bIndex == len(bigList) - 1:
                        bigList.append(smallList[sIndex])
                elif task == "remove":
                    if smallList[sIndex] == bigList[bIndex]:
                        bigList.pop(bIndex)
                        index = bIndex
                        break
    return bigList


def data_collection(channel, channel_id):
    #List of every viewer who has watched the stream
    data_viewers = []
    #List of the watchtime of every viewer in data_viewers
    data_watchtime = []
    #Time between each collection of data
    sleep_time = 60

    start_time = round(time.time())

    #Open csv file
    file_name = f"Data/{datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')} {channel}.csv"

    #Open the total csv file (or create a new one if necessary)
    try:
        with open(f'Data/{channel}_total.csv', 'r+', newline='') as total_csv:
            total_data = list(csv.reader(total_csv,delimiter=','))
            total_viewers = total_data[0]
            total_watchtime = [float(i) for i in total_data[1]]
        new_total = False
    except:
        new_total = True
    
    while True:
        time_iteration_start = time.time()
        print(f"{datetime.datetime.now()}    Query Twitch API whether stream is live")
        
        #If the stream ends
        if is_live(channel_id) == False:
            print(f"{datetime.datetime.now()}    Stream has ended")
            print(f"{datetime.datetime.now()}    Check if the stream is being restarted")
            #Check another couple times in case the stream is being restarted
            restart = False
            for _ in range(0,3):
                print(f"{datetime.datetime.now()}    Query Twitch API whether stream is live")
                if is_live(channel_id) == True:
                    restart = True
                    print(f"{datetime.datetime.now()}    Stream has been restarted")
                    break
                else:
                    print(f"{datetime.datetime.now()}    Stream is not live")
                    print()
                    time.sleep(60)

            if not restart:
                end_time = round(time.time())
                print()
                print(f"{datetime.datetime.now()}    Stream has ended")
                stream_length = end_time - start_time
                average_watchtime = sum(data_watchtime)/len(data_watchtime)
                percentage = round(60*100*average_watchtime/stream_length)
                print(f"On average, each viewer watched {percentage}% of the stream.")
                break
        
        #Get viewer list
        print(f"{datetime.datetime.now()}    Import viewer list")
        conc_viewers = viewer_list(channel)
        print(f"{datetime.datetime.now()}    Data of {len(conc_viewers)} concurrent viewers recorded")
        
        #Add new viewers to data list and calculate watchtime
        if len(data_viewers) == 0:
            data_viewers = conc_viewers
            data_watchtime = [sleep_time/60]*len(conc_viewers)
        else:
            index = 0
            for i in conc_viewers:
                if i > data_viewers[-1]:
                    data_viewers.append(i)
                    data_watchtime.append(sleep_time/60)
                    continue
                for j in range(index,len(data_viewers)):
                    if i == data_viewers[j]:
                        data_watchtime[j] += sleep_time/60
                        index = j
                        break
                    elif i < data_viewers[j]:
                        data_viewers.insert(j,i)
                        data_watchtime.insert(j,sleep_time/60)
                        index = j
                        break
        
        print(f"{datetime.datetime.now()}    Stream data updated ({len(data_viewers)} viewers this stream)")
        
        #Update the total list of viewers and watchtime
        if new_total:
            total_viewers = data_viewers.copy()
            total_watchtime = data_watchtime.copy()
        else:
            index = 0
            for i in conc_viewers:
                if i > total_viewers[-1]:
                    total_viewers.append(i)
                    total_watchtime.append(sleep_time/60)
                    continue
                for j in range(index,len(total_viewers)):
                    if i == total_viewers[j]:
                        total_watchtime[j] += sleep_time/60
                        index = j
                        break
                    elif i < total_viewers[j]:
                        total_viewers.insert(j,i)
                        total_watchtime.insert(j,sleep_time/60)
                        index = j
                        break
        
        print(f"{datetime.datetime.now()}    Total data updated ({len(total_viewers)} total viewers)")

        #Export data to a csv file
        with open(file_name, 'w', newline='') as data_file:
            writer_file = csv.writer(data_file)
            data_file.truncate()
            writer_file.writerows([data_viewers,data_watchtime])
            print(f'{datetime.datetime.now()}    Data written to "{file_name}"')
        
        #Update the total data csv file for the specified channel
        with open(f'Data/{channel}_total.csv', 'w', newline='') as total_file:
            writer_total = csv.writer(total_file)
            total_file.truncate()
            writer_total.writerows([total_viewers,total_watchtime])
            print(f'{datetime.datetime.now()}    Data written to "Data/{channel}_total.csv"')

        #Pause the program for the value of sleep_time
        time_iteration_end = time.time()
        time_of_iteration = time_iteration_end - time_iteration_start
        print(f'{time_of_iteration} seconds to run algorithm')
        print()
        time.sleep(sleep_time - time_of_iteration)

def main(channel):
    channel_id = get_channel_id(channel)
    while True:
        print()
        #If channel is live, then start collecting data
        if is_live(channel_id):
            data_collection(channel, channel_id)
            break
        else:
            print(f"{datetime.datetime.now()}    Channel is not live")
        time.sleep(60)

if __name__ == '__main__':
    channel = input("Enter a channel name: ")
    main(channel)
