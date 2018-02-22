#!`/usr/bin/whereis python3`

import wow
import tkinter as tk
from PIL import ImageTk

wowfile = wow.WowFile("CG_LCD_W.wow")

class WOWFileViewer:
    def __init__(self, master):
        self.currentLayer = 0
        self.master = master
        master.title("WOW file viewer")

        self.top_frame = tk.Frame(master)
        self.top_frame.pack(fill=tk.X)

        self.label = tk.Label(self.top_frame, text="Layer:".format(num=self.currentLayer))
        self.label.pack(fill=tk.X)

        self.mid_frame = tk.Frame(master)
        self.mid_frame.pack(fill=tk.X)

        self.img = ImageTk.PhotoImage(wowfile.layers[self.currentLayer].image)
        self.layer_img = tk.Label(self.mid_frame, image=self.img)
        self.layer_img.pack(side=tk.LEFT)
        self.layer_select = tk.Scale(self.mid_frame, from_=0, to=wowfile.get_layercount(), command=self.sliderUpdate, orient=tk.VERTICAL)
        self.layer_select.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.bottom_frame = tk.Frame(master)
        self.bottom_frame.pack(fill=tk.X)


        self.close_button2 = tk.Button(self.bottom_frame, text="Exit", command=master.quit)
        self.close_button2.pack()

    def sliderUpdate(self, pos):
        self.layerChange(int(pos))

    def layerUp(self):
        if self.currentLayer < wowfile.get_layercount():
            self.currentLayer += 1
            self.layerChange(self.currentLayer)

    def layerDown(self):
        if self.currentLayer > 0:
            self.currentLayer -= 1
            self.layerChange(self.currentLayer)


    def layerChange(self, layer):
        self.img = ImageTk.PhotoImage(wowfile.layers[layer].image)
        self.layer_img.configure(image=self.img)
        self.label.configure(text="Layer: {num}".format(num=layer))


root = tk.Tk()
my_gui = WOWFileViewer(root)
root.mainloop()


# if __name__ == "__main__":