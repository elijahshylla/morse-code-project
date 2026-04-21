from pathlib import Path
from tkinter import Tk
from tkinter import ttk
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from tkinter import messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog as fd
from tkinter import *
import sys, argparse
import pygame
import time

pygame.mixer.init()

__author__ = "Elijah Shylla"
__version__ = "1.0"

# -------------------------------
# THEME
# -------------------------------
BG = "#0b1a24"
PANEL = "#102733"
ACCENT = "#00c2a8"
TEXT = "#d8f3ff"
SUBTLE = "#6aa9b8"
BUTTON = "#163847"
BUTTON_ACTIVE = "#1f4e61"

FONT_TITLE = ("Consolas", 20, "bold")
FONT_MAIN = ("Consolas", 13)
FONT_SMALL = ("Consolas", 11)

code = {'a':'.-', 'b':'-...', 'c':'-.-.', 'd':'-..', 'e':'.', 'f':'..-.',
        'g':'--.', 'h':'....', 'i':'..', 'j':'.---', 'k':'-.-', 'l':'.-..',
        'm':'--', 'n':'-.', 'o':'---', 'p':'.--.', 'q':'--.-', 'r':'.-.',
        's':'...', 't':'-', 'u':'..-', 'v': '...-', 'w':'.--', 'x':'-..-',
        'y':'-.--', 'z':'--..', '1':'.----','2':'..---','3':'...--','4':'....-',
        '5':'.....','6':'-....','7':'--...','8':'---..','9':'----.','0':'-----',
        '.': '.-.-.-',',': '--..--','?': '..--..','!': '-.-.--'}

def encode(string):
    string = string.lower()
    output = ''
    for c in string:
        if c in code:
            output += code[c]+' '
        elif c==' ':
            output += '/ '
        else:
            output += c+' / '
    return output

def decode(string):
    letters = string.split()
    output =''
    dcode = {v:k for k,v in code.items()}
    for l in letters:
        if l in dcode:
            output += dcode[l]
        elif l =='/':
            output +=' '
        else:
            output += l
    return output

class Visualizer:
    x = 600
    y = 650
    index = 0
    stop = False
    sound_allowed = True

    def __init__(self):
        self.import_audio()
        self.root = Tk()
        self.root.geometry(f'{self.x}x{self.y}')
        self.root.title("Visualizer")
        self.root.configure(bg=BG)

        # Title
        Label(self.root, text="Morse Code Visualizer",
              font=FONT_TITLE, bg=BG, fg=ACCENT).pack(pady=10)

        # INPUT
        self.main_frame = Frame(self.root, bg=PANEL)
        self.main_frame.pack(padx=15, pady=10, fill="x")

        Label(self.main_frame, text="INPUT",
              font=FONT_SMALL, bg=PANEL, fg=SUBTLE).pack(anchor="w", padx=10)

        self.string_textbox = ScrolledText(self.main_frame, height=2, font=FONT_MAIN,
                                           bg="#08141c", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.string_textbox.pack(padx=10, pady=5)

        Button(self.main_frame, text="ENCODE", command=self.convert,
               font=FONT_SMALL, bg=BUTTON, fg=TEXT, relief="flat").pack(pady=5)

        # OUTPUT
        self.bottom_frame = Frame(self.root, bg=PANEL)
        self.bottom_frame.pack(padx=15, pady=10, fill="x")

        Label(self.bottom_frame, text="MORSE OUTPUT",
              font=FONT_SMALL, bg=PANEL, fg=SUBTLE).pack(anchor="w", padx=10)

        self.coded_textbox = ScrolledText(self.bottom_frame, height=2, font=FONT_MAIN,
                                          bg="#08141c", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.coded_textbox.pack(padx=10, pady=5)
        self.coded_textbox.bind('<Key>', self.morse_format)

        Button(self.bottom_frame, text="DECODE", command=self.reverse,
               font=FONT_SMALL, bg=BUTTON, fg=TEXT, relief="flat").pack(pady=5)

        # -------------------------------
        # SCI-FI WPM SELECTOR
        # -------------------------------
        self.wpm_frame = Frame(self.root, bg=BG)
        self.wpm_frame.pack(pady=10)

        Label(self.wpm_frame, text="Select WPM:",
              font=FONT_SMALL, bg=BG, fg=SUBTLE).pack(side="left")

        self.wpm_panel = Frame(self.wpm_frame, bg=PANEL)
        self.wpm_panel.pack(side="left", padx=10)

        self.wpm_value = StringVar(value="5")

        def select_wpm(val):
            self.wpm_value.set(str(val))
            update_buttons()
            self.set_focus(None)

        def update_buttons():
            for v, btn in self.wpm_buttons.items():
                if str(v) == self.wpm_value.get():
                    btn.config(bg=ACCENT, fg="#001a17")
                else:
                    btn.config(bg=BUTTON, fg=TEXT)

        self.wpm_buttons = {}

        for val in [5, 10, 20]:
            btn = Button(self.wpm_panel, text=str(val), width=4,
                         font=FONT_SMALL, bg=BUTTON, fg=TEXT,
                         relief="flat",
                         command=lambda v=val: select_wpm(v))
            btn.pack(side="left", padx=2, pady=2)
            self.wpm_buttons[val] = btn

        update_buttons()

        # LED with border
        self.led_frame = Frame(self.root, bg=BG, bd=1, highlightbackground=ACCENT, highlightthickness=1)
        self.led_frame.pack(pady=15)

        inner = Frame(self.led_frame, bg=BG)
        inner.pack(padx=10, pady=10)

        self.canvas = Canvas(inner, width=130, height=130, bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.glow = self.canvas.create_oval(5,5,125,125, fill="", outline="")
        self.led = self.canvas.create_oval(25,25,105,105, fill="#000d0c", outline="")
        self.highlight = self.canvas.create_oval(45,40,65,60, fill="#ccfff5", outline="")
        self.canvas.itemconfig(self.highlight, state="hidden")

        # Controls
        controls = Frame(self.root, bg=BG)
        controls.pack()

        Button(controls, text="PLAY", command=self.simulate,
               font=FONT_SMALL, bg=BUTTON, fg=TEXT).pack(side="left", padx=5)
        Button(controls, text="STOP", command=self.terminate,
               font=FONT_SMALL, bg=BUTTON, fg=TEXT).pack(side="left", padx=5)
        self.mute_button = Button(controls, text="MUTE", command=self.mute,
                                 font=FONT_SMALL, bg=BUTTON, fg=TEXT)
        self.mute_button.pack(side="left", padx=5)

        self.root.mainloop()

    # -------- LOGIC UNCHANGED BELOW --------

    def import_audio(self):
        self.dot_5 = Path(r"C:\Users\Elijah\Desktop\eli's\programs\env\morse_audio\dot_5.wav")
        self.dash_5 = Path(r"C:\Users\Elijah\Desktop\eli's\programs\env\morse_audio\dash_5.wav")
        self.dot_10 = Path(r"C:\Users\Elijah\Desktop\eli's\programs\env\morse_audio\dot_10.wav")
        self.dash_10 = Path(r"C:\Users\Elijah\Desktop\eli's\programs\env\morse_audio\dash_10.wav")
        self.dot_20 = Path(r"C:\Users\Elijah\Desktop\eli's\programs\env\morse_audio\dot_20.wav")
        self.dash_20 = Path(r"C:\Users\Elijah\Desktop\eli's\programs\env\morse_audio\dash_20.wav")

        self.dot_5_audio = pygame.mixer.Sound(self.dot_5)
        self.dot_10_audio = pygame.mixer.Sound(self.dot_10)
        self.dot_20_audio = pygame.mixer.Sound(self.dot_20)
        self.dash_5_audio = pygame.mixer.Sound(self.dash_5)
        self.dash_10_audio = pygame.mixer.Sound(self.dash_10)
        self.dash_20_audio = pygame.mixer.Sound(self.dash_20)

        self.audios = {"5d":self.dot_5_audio, "10d":self.dot_10_audio, "20d":self.dot_20_audio,
                       "5D":self.dash_5_audio, "10D":self.dash_10_audio, "20D":self.dash_20_audio}

    def set_focus(self, event):
        self.root.focus_set()

    def update_units(self, unit):
        self.DOT = 1 * unit
        self.DASH = 3 * unit
        self.SYMBOL_GAP = 1 * unit
        self.LETTER_GAP = 3 * unit
        self.WORD_GAP = 1 * unit

    def convert(self):
        self.text = self.string_textbox.get('1.0', END)
        self.encoded = encode(self.text.strip())
        self.coded_textbox.delete('1.0', END)
        self.coded_textbox.insert(END,self.encoded)

    def reverse(self):
        morse = self.coded_textbox.get("1.0", END)
        decoded = decode(morse.strip())
        self.string_textbox.delete('1.0',END)
        self.string_textbox.insert(END, decoded)

    def morse_format(self, event):
        allowed = ".-/ \b\n"
        if event.char not in allowed:
            return "break"

    def toggle(self, state, sound):
        if state:
            if self.sound_allowed and sound:
                self.audios[sound].play()
            self.canvas.itemconfig(self.led, fill="#00ffc8")
            self.canvas.itemconfig(self.glow, fill="#00c2a8")
            self.canvas.itemconfig(self.highlight, state="normal")
        else:
            self.canvas.itemconfig(self.led, fill="#000d0c")
            self.canvas.itemconfig(self.glow, fill="")
            self.canvas.itemconfig(self.highlight, state="hidden")

    def simulate(self):
        self.index = 0
        morse_code = self.coded_textbox.get('1.0',END).strip()
        wpm = self.wpm_value.get()
        units = {5:0.24, 10:0.12, 20:0.06}
        unit = units[int(wpm)]

        self.update_units(unit)
        self.timeline = []

        for symbol in morse_code:
            if symbol == '.':
                self.timeline.append((True, self.DOT, wpm+'d'))
                self.timeline.append((False, self.SYMBOL_GAP, None))
            elif symbol == '-':
                self.timeline.append((True, self.DASH, wpm+'D'))
                self.timeline.append((False, self.SYMBOL_GAP, None))
            elif symbol == ' ':
                self.timeline.append((False, self.LETTER_GAP, None))
            elif symbol == '/':
                self.timeline.append((False, self.WORD_GAP, None))

        self.play()

    def play(self):
        if self.index >= len(self.timeline):
            self.toggle(False, None)
            return
        if self.stop:
            self.stop = False
            return
        state, duration, sound = self.timeline[self.index]
        self.toggle(state, sound)
        self.index += 1
        self.root.after(round(duration*1000), self.play)

    def terminate(self):
        self.toggle(False, None)
        self.stop = True

    def mute(self):
        if self.sound_allowed:
            self.sound_allowed = False
            self.mute_button['text'] = "Unmute"
        else:
            self.sound_allowed = True
            self.mute_button['text'] = "Mute"

parser = argparse.ArgumentParser()

parser.add_argument('-a', '--author', action='store_true')
parser.add_argument('-v', '--version', action='store_true')
parser.add_argument('string', nargs='?', help='String to be encoded/decoded', default='')
parser.add_argument('-m', '--mode', choices = ["encode","decode"], default="encode")
parser.add_argument('-f', '--file', help='File to be encoded/decoded', default='')
parser.add_argument('-w', '--write', help='Output to specified file', type=str, default='')
parser.add_argument('-g', '--gtk', help='Opens the graphical text editor', action='store_true')
parser.add_argument('-V', '--visualizer', help='Opens the graphical visualizer', action='store_true')

args = parser.parse_args()
output_string = ""

if args.author:
    print(f'Author: {__author__}')
if args.version:
    print(f'Version: {__version__}')

if args.visualizer:
    v = Visualizer()

if args.string:
    if args.mode == 'encode':
        output_string = encode(args.string)
    else:
        output_string = decode(args.string)

if args.file:
    try:
        file=Path(args.file)
        with open(file, 'r') as fptr:
            if args.mode == 'encode':
                for line in fptr:
                    output_string+=encode(line.strip())+'\n'
            else:
                for line in fptr:
                    output_string+=decode(line.strip())+'\n'
    except Exception as E:
        print(E)

if args.write and output_string:
    try:
        output_file=Path(args.write)
        with open(output_file, 'a') as fptr:
            fptr.write(output_string+'\n')
    except Exception as E:
        print(E)
elif not args.write and output_string:
    print(output_string)