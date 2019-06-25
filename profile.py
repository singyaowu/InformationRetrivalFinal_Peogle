import tkinter as tk
from PIL import Image, ImageTk
import requests
import urllib.request
from bs4 import BeautifulSoup
import os

headers = {'User-Agent': 'Mozilla/5.0'}


def getImage(name, size):
    path = 'tmp/' + name + '.jpeg'
    if not os.path.isfile(path):
        url = 'https://www.google.com/search?q=' + name + ' 照片&source=lnms&tbm=isch'#政治人物 大頭照 個人照
        response = requests.get(url,headers = headers) #使用header避免訪問受到限制
        soup = BeautifulSoup(response.content, 'html.parser')
        item = soup.find('img')
        html = requests.get(item.get('src'))
        with open(path, 'wb') as f:
            f.write(html.content)
            f.flush()
        
    return Image.open(path).resize((size,size))


class Profile(tk.Frame):
    def __init__(self, root, name, score, size=100):
        tk.Frame.__init__(self, root)
        #self.configure(background='white')
        score = tk.Label(self, text=score)
        score.grid()
        #img = Image.open('index.jpeg').resize((size,size))
        img = getImage(name, size)
        img = ImageTk.PhotoImage(img)
        profile = tk.Label(self, image=img)
        profile.img = img
        profile.grid()
        name = tk.Label(self, text=name)
        name.grid()


if __name__ == '__main__':


    root = tk.Tk()
    #root.configure(background='white')
    profile = Profile(root, 'jacky', 50)
    profile.pack(side="top", fill="both", expand="true")


    root.mainloop()