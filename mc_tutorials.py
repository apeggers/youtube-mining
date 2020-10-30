import os

import socket
import json
import datetime as dt
import isodate
import statistics as stat
import matplotlib.pyplot as plt 

import googleapiclient.discovery
import googleapiclient.errors

from dotenv import load_dotenv
load_dotenv()

socket.setdefaulttimeout(10)

def main():
    api_service_name = "youtube"
    api_version = "v3"
    API_KEY = os.getenv("API_KEY")
    
    # Initialize API connection
    print("Connecting to Google API...")
    try:
        youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=API_KEY)
    except socket.timeout:
        print("Connection to Google API timed out.\nEXITING")
        return
    else:
        print("SUCCESS")

    page = None
    video_durations = []

    # Loop through each year to maximize results
    for year in range(2016, 2021, 2):

        # API gives 50-item pages so must loop through each one
        while(True):
            # Get page of search results
            request = youtube.search().list(
                part="snippet",
                q="minecraft tutorial",
                maxResults=50,
                publishedAfter=str(year)+"-1-1T00:00:00Z",
                publishedBefore=str(year+1)+"-1-1T00:00:00Z",
                type="video",
                pageToken=page
            )
            search_results = request.execute()
        
            # Extract video id's from search results
            video_ids = []
            for search_result in search_results["items"]:
                video_ids.append(search_result["id"]["videoId"])
        
            # Get video durations based on video id's
            request = youtube.videos().list(
                part="contentDetails",
                id=",".join(video_ids)
            )
            videos = request.execute()

            for video in videos["items"]:
                duration = video["contentDetails"]["duration"]
                video_durations.append(isodate.parse_duration(duration).seconds)
            
            if "nextPageToken" in search_results:
                page = search_results["nextPageToken"]
            else:
                page = None
                break
    
    # Remove 0-duration videos
    list(filter((0).__ne__, video_durations))

    # Print basic stats
    n = len(video_durations)
    print("n:      %s" % str(n))
    print("Min:    %s" % str(dt.timedelta(seconds=min(video_durations))))
    print("Max:    %s" % str(dt.timedelta(seconds=max(video_durations))))
    print("Mean:   %s" % str(dt.timedelta(seconds=stat.mean(video_durations))))
    print("Median: %s" % str(dt.timedelta(seconds=stat.median(video_durations))))

    # Plot histogram
    dur_range = max(video_durations)-min(video_durations)
    bin_size = 60 #seconds
    
    sns.distplot(video_durations, hist=True, kde=True,
                 bins = int(dur_range/bin_size), color = 'darkblue',
                 hist_kws={'edgecolor':'black'}, kde_kws={'linewidth': 4})

    plt.title('Duration of Videos')
    plt.xlabel('Seconds')
    plt.ylabel('Density')
    
    plt.show()

def split_list(l, n):
    return [ l[i*n:(i+1)*n] for i in range((len(l)+n-1) // n )]

if __name__ == "__main__":
    main()

