""" tk_ToolTip_class101.py
gives a Tkinter widget a tooltip as the mouse is above the widget
tested with Python27 and Python34  by  vegaseat  09sep2014
www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter

Modified to include a delay time by Victor Zaccardo, 25mar16

Modified to only allow Python 3, use dataclasses, annotate types by Jona Heinke
"""

#standard library imports
from dataclasses import dataclass, field, InitVar

#third party imports
import tkinter as tk



@dataclass
class CreateToolTip:
	"""
	create a tooltip for a given widget
	"""
	widget: tk.Widget
	text: str
	wraplength: int = 250 #pixels
	waittime: int   = 500 #miliseconds
	id: str = field(default = None, init = False)
	tw: tk.Toplevel = field(default = None, init = False)

	def __post_init__(self):
		self.widget.bind("<Enter>", self.enter)
		self.widget.bind("<Leave>", self.leave)
		#self.widget.bind("<ButtonPress>", self.leave)

	def enter(self, event = None):
		self.schedule()

	def leave(self, event = None):
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

	def showtip(self, event = None):
		x = y = 0
		x, y, _, _ = self.widget.bbox("insert")
		x += self.widget.winfo_rootx() + self.widget.winfo_width()
		y += self.widget.winfo_rooty() + 4
		#creates a toplevel window
		self.tw = tk.Toplevel(self.widget)
		#leaves only the label and removes the app window
		self.tw.wm_overrideredirect(True)
		self.tw.wm_geometry("+%d+%d" % (x, y))
		label = tk.Label(self.tw, text = self.text, justify = "left",
						background = "#000000", relief = "solid", borderwidth = 1,
						wraplength = self.wraplength)
		label.pack(ipadx = 1)

	def hidetip(self):
		tw = self.tw
		self.tw = None
		if tw:
			tw.destroy()