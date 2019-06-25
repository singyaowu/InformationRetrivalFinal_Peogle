import tkinter as tk
from docList import DocList
from profile import Profile
import time

from model.find_relations import find_relations
from model.score_calculator import personal_score

base_x = 540
base_y = 450
profile_offset = [(400,0), (250,-350), (-250,-350), (-400,0), (-250,350), (250,350)]
line_offset = [(100,0,330,0), (90,-110,195,-270), (-90,-110,-195,-270), (-100,0,-330,0), (-90,110,-195,270), (90,110,195,270)]
docList_offset = [(250,70), (290,-200), (-80,-300), (-250,-70), (-290,200), (80,300)]
#related_docs = [{'article_title': '[新聞] 把2025非核當神主牌？ 馬英九：蔡政府非', 'url': 'https://1'}, {'article_title': '2', 'url': 'https://2'}, {'article_title': '3', 'url': 'https://3'}]

def createGraph(name, canvas):
    canvas.delete('all')
    #time.sleep(1)
    results = find_relations(name)
    

    profile = Profile(canvas, name=name, score=int(personal_score(name)), size=150)#韓國瑜 
    canvas_profile = canvas.create_window(base_x, base_y, window=profile)
    for i in range(len(results)):
        result = results[i]

        x, y = profile_offset[i]
        profile = Profile(canvas, name=result['name'], score=int(personal_score(result['name'])))#
        canvas.create_window(base_x + x, base_y + y, window=profile)

        x_0, y_0, x_1, y_1 = line_offset[i]
        canvas.create_line(base_x + x_0, base_y + y_0, base_x + x_1, base_y + y_1, fill="#476042", width=3)
    
        x, y = docList_offset[i]
        docList = DocList(canvas, related_docs=result['related_docs'])
        canvas_docList1 = canvas.create_window(base_x + x, base_y + y, window=docList)





if __name__ == '__main__':

    window = tk.Tk()
    window.title('Politician Retrieval')
    window.geometry('1100x950')

    query = tk.Frame(window)
    query.pack(side='top')
    graph = tk.Canvas(window, height=900, width=1100)
    #graph.configure(background='white')
    graph.pack(side='bottom')

    nameVar = tk.StringVar()
    tk.Label(query, text='Name:').pack(padx=5, pady=10, side='left')
    tk.Entry(query, textvariable=nameVar, width=5).pack(padx=5, pady=10, side='left')
    tk.Button(query, text='Start Retrieval', command=lambda : createGraph(nameVar.get(), graph)).pack(padx=5, pady=10, side='left')
    

    window.mainloop()


