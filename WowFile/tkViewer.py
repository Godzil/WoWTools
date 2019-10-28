#!`/usr/bin/whereis python3`
# -*- coding: iso-8859-9 -*-

import os
import WowFile as wow
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import sys
from . import __version__


class WOWFileViewer:

    _Types = ("Thickness", "Speed up", "Exposure level", "Speed down", "Exposure time", "Up movement distance")

    def __init__(self, master, wowfile):
        self.currentLayer = 0
        self.master = master
        self.wowfile = wowfile
        master.title("WOW file viewer - {ver}".format(ver=__version__))

        self.layer_count = wowfile.get_layercount()

        self.layer = wowfile.get_layer(self.currentLayer)

        # Configure columns and row
        self.master.columnconfigure(1, weight=1)
        self.master.columnconfigure(4, weight=1)
        self.master.rowconfigure(2, weight=1)

        # Row 1
        self.label = tk.Label(master, text="Layer: {num} / {tot}".format(num=self.layer.number, tot=self.layer_count))
        self.label.grid(row=1, columnspan=6)

        self.layern_var = tk.StringVar()
        self.layern_var.set(str(self.layer.number))
        self.layern_ent = tk.Entry(master, textvariable=self.layern_var, width=6)
        self.layern_ent.grid(row=1, column=7, sticky=tk.E+tk.W)
        self.layern_btn = tk.Button(master, text=" Change ", command=self.layerManualSet)
        self.layern_btn.grid(row=1, column=8, sticky=tk.E+tk.W+tk.N+tk.S)

        # Row 2
        self.img = ImageTk.PhotoImage(self.layer.image)
        self.layer_img = tk.Label(master, image=self.img)
        self.layer_img.grid(row=2, column=1, columnspan=7)

        tickinterval = self.layer_count/10
        self.layer_select = tk.Scale(master, from_=1, to=self.layer_count,
                                     command=self.sliderUpdate, orient=tk.VERTICAL,
                                     resolution=-1, length=400, tickinterval=tickinterval,
                                     takefocus=1)
        self.layer_select.grid(row=2, column=8, sticky=tk.E+tk.W+tk.N+tk.S)

        # Row 3
        self.thick_var = tk.StringVar()
        self.thick_var.set(str(self.layer.thickness * 1000))
        self.thick_lbl = tk.Label(master, text="Layer thickness (µm): ")
        self.thick_lbl.grid(row=3, column=1, sticky=tk.E)
        self.thick_ent = tk.Entry(master, textvariable=self.thick_var, width=10)
        self.thick_ent.grid(row=3, column=2, sticky=tk.E + tk.W)
        self.thick_btn = tk.Button(master, text="A",
                                   command=lambda: self.applyValueToAllLayer(1, self.thick_var.get()))
        self.thick_btn.grid(row=3, column=3, sticky=tk.E + tk.W + tk.N + tk.S)

        self.spdu_var = tk.StringVar()
        self.spdu_var.set(str(self.layer.speed_up))
        self.spdu_lbl = tk.Label(master, text="Speed up (mm/min): ")
        self.spdu_lbl.grid(row=3, column=4, sticky=tk.E)
        self.spdu_ent = tk.Entry(master, textvariable=self.spdu_var, width=10)
        self.spdu_ent.grid(row=3, column=5, sticky=tk.E + tk.W)
        self.spdu_btn = tk.Button(master, text="A",
                                  command=lambda: self.applyValueToAllLayer(2, self.spdu_var.get()))
        self.spdu_btn.grid(row=3, column=6, sticky=tk.E + tk.W + tk.N + tk.S)

        # Row 4
        self.exp_var = tk.StringVar()
        self.exp_var.set(str(self.layer.exposition))
        self.exp_lbl = tk.Label(master, text="Layer exposure level (0-255): ")
        self.exp_lbl.grid(row=4, column=1, sticky=tk.E)
        self.exp_ent = tk.Entry(master, textvariable=self.exp_var, width=10)
        self.exp_ent.grid(row=4, column=2, sticky=tk.E+tk.W)
        self.exp_btn = tk.Button(master, text="A",
                                  command=lambda: self.applyValueToAllLayer(3, self.exp_var.get()))
        self.exp_btn.grid(row=4, column=3, sticky=tk.E + tk.W + tk.N + tk.S)

        self.spdd_var = tk.StringVar()
        self.spdd_var.set(str(self.layer.speed_down))
        self.spdd_lbl = tk.Label(master, text="Speed down (mm/min): ")
        self.spdd_lbl.grid(row=4, column=4, sticky=tk.E)
        self.spdd_ent = tk.Entry(master, textvariable=self.spdd_var, width=10)
        self.spdd_ent.grid(row=4, column=5, sticky=tk.E+tk.W)
        self.spdd_btn = tk.Button(master, text="A",
                                  command=lambda: self.applyValueToAllLayer(4, self.spdd_var.get()))
        self.spdd_btn.grid(row=4, column=6, sticky=tk.E + tk.W + tk.N + tk.S)

        # Row 5
        self.expt_var = tk.StringVar()
        self.expt_var.set(str(self.layer.exposition_time))
        self.expt_lbl = tk.Label(master, text="Layer exposure time (in sec): ")
        self.expt_lbl.grid(row=5, column=1, sticky=tk.E)
        self.expt_ent = tk.Entry(master, textvariable=self.expt_var, width=10)
        self.expt_ent.grid(row=5, column=2, sticky=tk.E+tk.W)
        self.expt_btn = tk.Button(master, text="A",
                                  command=lambda: self.applyValueToAllLayer(5, self.expt_var.get()))
        self.expt_btn.grid(row=5, column=3, sticky=tk.E + tk.W + tk.N + tk.S)

        self.updist_var = tk.StringVar()
        self.updist_var.set(str(self.layer.up_distance))
        self.updist_lbl = tk.Label(master, text="Up mvmt distance (mm): ")
        self.updist_lbl.grid(row=5, column=4, sticky=tk.E)
        self.updist_ent = tk.Entry(master, textvariable=self.updist_var, width=10)
        self.updist_ent.grid(row=5, column=5, sticky=tk.E + tk.W)
        self.updist_btn = tk.Button(master, text="A",
                                  command=lambda: self.applyValueToAllLayer(6, self.updist_var.get()))
        self.updist_btn.grid(row=5, column=6, sticky=tk.E + tk.W + tk.N + tk.S)

        # Row 6
        self.printtime_var = tk.StringVar()
        self.printtime_var.set(str(wowfile.get_printtime(human_readable=True)))
        self.printtime_lbl = tk.Label(master, text="Estimated print time: ")
        self.printtime_lbl.grid(row=6, column=1, sticky=tk.E)
        self.printtime_ent = tk.Label(master, textvariable=self.printtime_var)
        self.printtime_ent.grid(row=6, column=2, sticky=tk.W)

        self.estvol_var = tk.StringVar()
        self.estvol_var.set(str(wowfile.get_volume(human_readable=True)))
        self.estvol_lbl = tk.Label(master, text="Estimated Volume: ")
        self.estvol_lbl.grid(row=6, column=4, sticky=tk.E)
        self.estvol_ent = tk.Label(master, textvariable=self.estvol_var)
        self.estvol_ent.grid(row=6, column=5, sticky=tk.W)

        # Row 7
        self.zheight_var = tk.StringVar()
        self.zheight_var.set(str(wowfile.get_zheight()))
        self.zheight_lbl = tk.Label(master, text="Printed height (mm): ")
        self.zheight_lbl.grid(row=7, column=1, sticky=tk.E)
        self.zheight_ent = tk.Label(master, textvariable=self.zheight_var)
        self.zheight_ent.grid(row=7, column=2, sticky=tk.W)

        self.apply_btn = tk.Button(master, text=" Apply Changes ", command=self.applyLayerChange)
        self.apply_btn.grid(row=7, column=5, sticky=tk.E+tk.W+tk.N+tk.S)

        self.saveas_btn = tk.Button(master, text=" Save As ", command=self.saveAsNewFile)
        self.saveas_btn.grid(row=7, column=6, columnspan=2, sticky=tk.E+tk.W+tk.N+tk.S)

        self.close_btn = tk.Button(master, text=" Exit ", command=master.quit)
        self.close_btn.grid(row=7, column=8, sticky=tk.E+tk.W+tk.N+tk.S)

        self.layer_select.focus_force()

    def applyLayerChange(self):
        try:
            self.layer.thickness = round(float(self.thick_var.get()) / 1000, 10)
            self.layer.exposition = float(self.exp_var.get())
            self.layer.exposition_time = float(self.expt_var.get())
            self.layer.speed_up = float(self.spdu_var.get())
            self.layer.speed_down = float(self.spdd_var.get())
            self.layer.up_distance = float(self.updist_var.get())
            self.layer.update_movetime()

            self.zheight_var.set(str(self.wowfile.get_zheight()))
            self.estvol_var.set(str(self.wowfile.get_volume(human_readable=True)))
            self.printtime_var.set(str(self.wowfile.get_printtime(human_readable=True)))
            self.layerChange(self.layer.number)
        except ValueError:
            tk.messagebox.showerror("WoW File Viewer", "Value error:\nOne of the layer field is invalid, please check")

    def applyValueToAllLayer(self, type, value):
        strtype = self._Types[type-1]
        answer = tk.messagebox.askyesno("WoW File Viewer", "Are you sure you want to apply the value '{value}'\n"
                                                           "to all layer for '{type}'?".format(value=value,
                                                                                               type=strtype))
        if answer == tk.YES:
            # The fun begins!
            try:
                for l in self.wowfile.layers:
                    if type == 1: # Thickness
                        l.thickness = round(float(value) / 1000, 10)
                    elif type == 2: # Speed up
                        l.speed_up = round(float(value), 5)
                    elif type == 3:  # Exposure
                        l.exposition = round(float(value), 5)
                    elif type == 4:  # Speed down
                        l.speed_down = round(float(value), 5)
                    elif type == 5:  # Exposure time
                        l.exposition_time = round(float(value), 5)
                    elif type == 6:  # Up movement distance
                        l.up_distance = round(float(value), 5)

                    l.update_movetime()

                self.zheight_var.set(str(self.wowfile.get_zheight()))
                self.printtime_var.set(str(self.wowfile.get_printtime(human_readable=True)))
                self.estvol_var.set(str(self.wowfile.get_volume(human_readable=True)))
                self.layerChange(self.layer.number)
            except ValueError:
                tk.messagebox.showerror("WoW File Viewer",
                                        "Value error:\n"
                                        "The value {value} is not valid, please check".format(value=value))

    def saveAsNewFile(self):
        newfile = tk.filedialog.asksaveasfilename(defaultextension=".wow",
                                                  filetypes=(("WOW print file", "*.wow"),("All files", "*.*")))
        self.wowfile.write_wow(newfile)

    def sliderUpdate(self, pos):
        self.layerChange(int(pos))

    def layerManualSet(self):
        self.layer_select.set(int(self.layern_var.get()))
        return True

    def layerChange(self, layer):
        self.layer = self.wowfile.get_layer(layer - 1)
        self.img = ImageTk.PhotoImage(self.layer.image)
        self.layer_img.configure(image=self.img)
        self.label.configure(text="Layer: {num} / {tot}".format(num=self.layer.number, tot=self.layer_count))
        self.layern_var.set(str(self.layer.number))
        self.thick_var.set(str(self.layer.thickness * 1000))
        self.exp_var.set(str(self.layer.exposition))
        self.expt_var.set(str(self.layer.exposition_time))
        self.spdu_var.set(str(self.layer.speed_up))
        self.spdd_var.set(str(self.layer.speed_down))
        self.updist_var.set(str(self.layer.up_distance))

def main():
    print("WOW File viewer {ver}".format(ver=__version__))
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
    root.focus_force()
    root.mainloop()


if __name__ == "__main__":
    main()