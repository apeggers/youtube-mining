import json
import datetime as dt
import isodate
import statistics as stat
import matplotlib.pyplot as plt 

import googleapiclient.discovery
import googleapiclient.errors


def main():
    api_service_name = "youtube"
    api_version = "v3"
    api_key = "AIzaSyA01YcUhlrZKc72Adeh2hsBAg_GCM5ozZM"

    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)
    
    page = None
    video_durations = []
    while(true):
        # Get page of search results
        request = youtube.search().list(
            part="snippet",
            q="minecraft tutorial",
            maxResults=50,
            publishedAfter="2015-10-29T00:00:00Z",
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
            print(page)
        else:
            break

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
    plt.hist(video_durations, color = 'blue', edgecolor = 'black', bins = int(dur_range/bin_size))
    plt.title('Duration of Videos')
    plt.xlabel('Seconds')
    plt.ylabel('Videos')
    plt.show()

def split_list(l, n):
    return [ l[i*n:(i+1)*n] for i in range((len(l)+n-1) // n )]

if __name__ == "__main__":
    main()

