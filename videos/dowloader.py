import pytube
link = "https://www.youtube.com/watch?v=0yZcDeVsj_Y" 
yt = pytube.YouTube(link)
stream = yt.streams.get_highest_resolution()
stream.download()
