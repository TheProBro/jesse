import re
song_title = re.search(r'Jhooth Bol Raha Hai Tumse', """[{'url': 'https://www.youtube.com/watch?v=bR83FKvearM', 'content': 'Jhoot bola gya hai tumse, Areeb bewafa nahi tha... #mujhepyaarhuatha #haniaamir. 9.3K views · 1 year ago ...more. ARY Digital HD. 57.6M.'}]""").group()
print(song_title)