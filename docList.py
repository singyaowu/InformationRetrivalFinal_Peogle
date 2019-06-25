import tkinter as tk
import webbrowser

class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

class DocList(tk.Frame):
    def __init__(self, root, related_docs):
        tk.Frame.__init__(self, root)

        length = len(related_docs)
        
        text1 = related_docs[0]['article_title']
        if len(text1) > 18:
            text1 = text1[:15] + '...'
        label1 = tk.Label(self, text=text1)
        label1.bind("<Button-1>", lambda e: webbrowser.open_new(related_docs[0]['url']))
        label1.grid()
        label1_tip = CreateToolTip(label1, related_docs[0]['article_title'])

        if length >= 2:
            
            text2 = related_docs[1]['article_title']
            if len(text2) > 18:
                text2 = text2[:15] + '...'
            label2 = tk.Label(self, text=text2)
            label2.bind("<Button-1>", lambda e: webbrowser.open_new(related_docs[1]['url']))
            label2.grid()
            label2_tip = CreateToolTip(label2, related_docs[1]['article_title'])

        if length >= 3:

            text3 = related_docs[2]['article_title']
            if len(text3) > 18:
                text3 = text3[:15] + '...'
            label3 = tk.Label(self, text=text3)
            label3.bind("<Button-1>", lambda e: webbrowser.open_new(related_docs[2]['url']))
            label3.grid()
            label3_tip = CreateToolTip(label3, related_docs[2]['article_title'])
        
            



if __name__ == '__main__':

    related_docs = [{'article_title': '1', 'url': 'https://1'}, {'article_title': '2', 'url': 'https://2'}, {'article_title': '3', 'url': 'https://3'}]

    root = tk.Tk()
    docList = DocList(root, related_docs)
    docList.pack(side="top", fill="both", expand="true")


    root.mainloop()
    """
    btn1 = tk.Label(root, text='testing')
    btn1.pack(padx=10, pady=5)
    button1_ttp = CreateToolTip(btn1, \
   'Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, '
   'consectetur, adipisci velit. Neque porro quisquam est qui dolorem ipsum '
   'quia dolor sit amet, consectetur, adipisci velit. Neque porro quisquam '
   'est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit.')

    btn2 = tk.Button(root, text="button 2")
    btn2.pack(padx=10, pady=5)
    button2_ttp = CreateToolTip(btn2, \
    "First thing's first, I'm the realest. Drop this and let the whole world "
    "feel it. And I'm still in the Murda Bizness. I could hold you down, like "
    "I'm givin' lessons in  physics. You should want a bad Vic like this.")
    root.mainloop()
    """