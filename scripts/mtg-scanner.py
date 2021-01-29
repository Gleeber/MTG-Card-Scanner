from PIL import ImageTk
import cv2 as cv
import os
import tkinter as tk

import json

import img_manip as im
from scrape_img_hashes import scrape_data

root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
data_dir = os.path.join(root_dir,'data')
img_hashes_file = os.path.join(data_dir,"img_hashes.json")

def find_match(img_hash):
    '''
    Given an image hash, find the closest hash among stored hashes
    '''
    f = open(img_hashes_file, 'r')
    hash_data = json.load(f)

    all_matches = {}
    
    closest_match = ("Card Name",64)
    for each_card in hash_data:
        each_hash = hash_data[each_card]
        similarity = im.hash_compare(img_hash,each_hash)

        all_matches[each_card] = similarity

        if similarity < closest_match[1]:
            closest_match = (each_card,similarity)

    # {print(k,v) for k, v in sorted(all_matches.items(), key=lambda item: item[1], reverse=True)[-2:]}
    # print("---------------------------------------------------------------------------------------")

    return closest_match

class TkClass:
    '''
    This class is used for handling Tkinter values, like the main window, labels, and frames
    '''

    def __init__(self):
        self.window = tk.Tk()

        self.window.geometry('1024x768')
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        self.cap = cv.VideoCapture(0)
        zoom_out = 2
        w,h = 1280/zoom_out, 720/zoom_out
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, w)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, h)
        
        self.tk_frame = tk.Label(self.window)
        self.tk_frame.grid(row=0,column=0,columnspan=2)

        self.card_frame = tk.Label(self.window, width=200, height=400)

        self.scan_card_button = tk.Button(self.window,text="Scan Card",command=self.scan_card)

        self.result = tk.Text(self.window, height=1)
        self.result.insert(tk.INSERT,"Matched Card: ")
        self.result.grid(row=1,column=1)
        
        self.window.bind('<Escape>', lambda e: self.window.quit())

        self.run_scan_bool = False

        self.matched_card = ""
        self.match_threshold = 5

        self.main_event_loop()

    def put_img_in_label(self,label,img):
        img_tk = ImageTk.PhotoImage(img)
        label.img_tk = img_tk
        label.configure(image = img_tk)

    def main_event_loop(self):
        ret,cam_frame = self.cap.read()

        img = im.cv_to_pil(cam_frame)
        self.put_img_in_label(self.tk_frame,img)
        
        if self.run_scan_bool:
            rect = im.find_card_border(cam_frame)

            draw_border = im.cv_to_pil(im.draw_box(cam_frame,rect)) 
            self.put_img_in_label(self.tk_frame,draw_border)

            width,height = rect[1][0],rect[1][1]
            error = abs(width/height - 63/88)
            err_thresh = 0.1
            if error < err_thresh:
                cropped_card = im.crop_to_card(cam_frame,rect)
                cropped_card_art = im.crop_art(cropped_card)

                card_pil = im.cv_to_pil(cropped_card)
                self.put_img_in_label(self.card_frame,card_pil)

                self.card_frame.grid(row=0,column=2)

                card = find_match(im.get_hash(cropped_card_art))

                try:
                    self.card_matches[card[0]] += 1
                except:
                    self.card_matches[card[0]] = 0

                if self.card_matches[card[0]] > self.match_threshold:
                    self.matched_card = card[0]
                    self.run_scan_bool = False   

        if self.matched_card:
            self.card_frame.grid_forget()
            
            print(self.matched_card)
            self.result.insert(tk.INSERT,self.matched_card)
            self.matched_card = ""

        
        self.scan_card_button.grid(row=1,column=0)

        self.tk_frame.after(10, self.main_event_loop)

    def scan_card(self):
        self.result.delete("1.14",tk.END)

        self.card_matches = {}
        
        self.run_scan_bool = True


if __name__ == "__main__":
    try:
        f = open(img_hashes_file, 'x')
        scrape_data()
    except:
        pass

    main_program = TkClass()
    main_program.window.mainloop()
