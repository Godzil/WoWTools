#!`/usr/bin/whereis python3`
# -*- coding: iso-8859-9 -*-

import os
import wow
import tkinter as tk
import tkinter.filedialog
import sys


try:
    import BUILD_CONSTANTS
    version = BUILD_CONSTANTS.BUILD_VERSION
except ImportError:
    try:
        import git
        r = git.repo.Repo('./')
        version = r.git.describe("--tags", "--dirty")
    except ImportError:
        version = "?version unknown?"

from PIL import ImageTk

class WOWFileViewer:

    def __init__(self, master, wowfile):
        self.currentLayer = 0
        self.master = master
        self.wowfile = wowfile
        master.title("WOW file viewer - {ver}".format(ver=version))

        self.layer_count = wowfile.get_layercount()

        self.layer = wowfile.get_layer(self.currentLayer)

        self.label = tk.Label(master, text="Layer: {num} / {tot}".format(num=self.layer.number, tot=self.layer_count))
        self.label.grid(row=1, columnspan=4)

        self.img = ImageTk.PhotoImage(self.layer.image)
        self.layer_img = tk.Label(master, image=self.img)
        self.layer_img.grid(row=2, column=1, columnspan=3)

        tickinterval = self.layer_count/10
        self.layer_select = tk.Scale(master, from_=1, to=self.layer_count,
                                     command=self.sliderUpdate, orient=tk.VERTICAL,
                                     resolution=1, length=400, tickinterval=tickinterval)
        self.layer_select.grid(row=2, column=4)

        self.thick_var = tk.StringVar()
        self.thick_var.set(str(self.layer.thickness * 1000))
        self.thick_lbl = tk.Label(master, text="Layer thickness (µm): ")
        self.thick_lbl.grid(row=3, column=1, sticky=tk.E)
        self.thick_ent = tk.Entry(master, textvariable=self.thick_var)
        self.thick_ent.grid(row=3, column=2, sticky=tk.W)

        self.exp_var = tk.StringVar()
        self.exp_var.set(str(self.layer.exposition))
        self.exp_lbl = tk.Label(master, text="Layer exposure level (0-255): ")
        self.exp_lbl.grid(row=4, column=1, sticky=tk.E)
        self.exp_ent = tk.Entry(master, textvariable=self.exp_var)
        self.exp_ent.grid(row=4, column=2, sticky=tk.W)

        self.spdu_var = tk.StringVar()
        self.spdu_var.set(str(self.layer.speed_up))
        self.spdu_lbl = tk.Label(master, text="Speed up (mm/min): ")
        self.spdu_lbl.grid(row=3, column=3, sticky=tk.E)
        self.spdu_ent = tk.Entry(master, textvariable=self.spdu_var)
        self.spdu_ent.grid(row=3, column=4, sticky=tk.W)

        self.spdd_var = tk.StringVar()
        self.spdd_var.set(str(self.layer.speed_down))
        self.spdd_lbl = tk.Label(master, text="Speed down (mm/min): ")
        self.spdd_lbl.grid(row=4, column=3, sticky=tk.E)
        self.spdd_ent = tk.Entry(master, textvariable=self.spdd_var)
        self.spdd_ent.grid(row=4, column=4, sticky=tk.W)

        self.expt_var = tk.StringVar()
        self.expt_var.set(str(self.layer.exposition_time))
        self.expt_lbl = tk.Label(master, text="Layer exposure time (in sec): ")
        self.expt_lbl.grid(row=5, column=1, sticky=tk.E)
        self.expt_ent = tk.Entry(master, textvariable=self.expt_var)
        self.expt_ent.grid(row=5, column=2, sticky=tk.W)

        self.printtime_var = tk.StringVar()
        self.printtime_var.set(str(wowfile.get_printtime(human_readable=True)))
        self.printtime_lbl = tk.Label(master, text="Estimated print time: ")
        self.printtime_lbl.grid(row=6, column=1, sticky=tk.E)
        self.printtime_ent = tk.Label(master, textvariable=self.printtime_var)
        self.printtime_ent.grid(row=6, column=2, sticky=tk.W)

        self.close_button2 = tk.Button(master, text=" Exit ", command=master.quit)
        self.close_button2.grid(row=6, column=4)

    def sliderUpdate(self, pos):
        self.layerChange(int(pos))

    def layerUp(self):
        if self.currentLayer < self.wowfile.get_layercount():
            self.currentLayer += 1
            self.layerChange(self.currentLayer)

    def layerDown(self):
        if self.currentLayer > 0:
            self.currentLayer -= 1
            self.layerChange(self.currentLayer)

    def layerChange(self, layer):
        self.layer = self.wowfile.get_layer(layer - 1)
        self.img = ImageTk.PhotoImage(self.layer.image)
        self.layer_img.configure(image=self.img)
        self.label.configure(text="Layer: {num} / {tot}".format(num=self.layer.number, tot=self.layer_count))
        self.thick_var.set(str(self.layer.thickness * 1000))
        self.exp_var.set(str(self.layer.exposition))
        self.expt_var.set(str(self.layer.exposition_time))
        self.spdu_var.set(str(self.layer.speed_up))
        self.spdd_var.set(str(self.layer.speed_down))

def main():
    print("WOW File viewer {ver}".format(ver=version))
    root = tk.Tk()
    root.title("WOW file viewer")
    lbl = tk.Label(root, text="Please Wait...")
    lbl.grid(row=1, column=1)
    filename = tkinter.filedialog.askopenfilename(filetypes=(("WOW print file", "*.wow"),("All files", "*.*")))
    if filename is "":
        sys.exit(0)

    lbl.configure(text="")
    wowfile = wow.WowFile(filename)
    lbl = None
    my_gui = WOWFileViewer(root, wowfile)
    root.mainloop()


if __name__ == "__main__":
    main()