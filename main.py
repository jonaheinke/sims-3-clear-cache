# ------------------------------------------------------ IMPORTS ----------------------------------------------------- #

#standard library imports
import os, random, shutil, json
from dataclasses import dataclass, InitVar, field

#third party imports
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

#changing the working directory, so that the program can be run from any path
os.chdir(os.path.dirname(os.path.realpath(__file__)))



# ---------------------------------------------------- DATACLASSES --------------------------------------------------- #

@dataclass
class CacheFile:
	name: str = ""
	filename: str | list[str] = ""
	settings: InitVar[dict[str, str | dict[str, bool]]] = {}
	default: InitVar[bool] = True
	var: tk.BooleanVar | None = None

	def __post_init__(self, settings, default):
		value = default
		if settings and "caches" in settings and self.name in settings["caches"]:
			value = settings["caches"][self.name]
		self.var = tk.BooleanVar(value = value)
	
	def __hash__(self) -> int:
		return hash(self.name + self.filename)

	def remove(self):
		if isinstance(self.filename, str):
			os.remove(os.path.join(document_path.get(), self.filename))
		else:
			for file in self.filename:
				os.remove(os.path.join(document_path.get(), file))

@dataclass
class DLC:
	id: str = "EPXX"
	name: str = ""
	filename: str = ""
	settings: InitVar[dict[str, str | dict[str, bool]]] = {}
	default: InitVar[bool] = True
	var: tk.BooleanVar | None = None

	def __post_init__(self, settings, default):
		value = default
		if settings and "dlcs" in settings and self.id in settings["dlcs"]:
			value = settings["dlcs"][self.id]
		self.var = tk.BooleanVar(value = value)

	def __hash__(self) -> int:
		return hash(self.id + self.name)

	def choose_this(self):
		path_to_mod = os.path.join(document_path.get(), "Mods", "Packages", "randomized-loading-screen-theme.package")
		if self.filename:
			shutil.copy(os.path.join("dlcs", self.filename), path_to_mod)
		else:
			try:
				os.remove(path_to_mod)
			except:
				pass



# ------------------------------------------------- HELPER FUNCTIONS ------------------------------------------------- #

def tkinter_center(win: tk.Tk | tk.Toplevel):
	"""Centers a tkinter window on the screen.
	Copied from https://stackoverflow.com/a/10018670"""
	win.update_idletasks()
	width = win.winfo_width()
	frm_width = win.winfo_rootx() - win.winfo_x()
	win_width = width + 2 * frm_width
	height = win.winfo_height()
	titlebar_height = win.winfo_rooty() - win.winfo_y()
	win_height = height + titlebar_height + frm_width
	x = win.winfo_screenwidth() // 2 - win_width // 2
	y = win.winfo_screenheight() // 2 - win_height // 2
	win.geometry(f"{width}x{height}+{x}+{y}")
	win.deiconify()



# ----------------------------------------------- WINDOW INITIALIZATION ---------------------------------------------- #

#window init
window = tk.Tk()
window.title("The Sims 3 Management Program")
window.resizable(False, False)

#keyboard bindings
window.bind("<Escape>", lambda _: window.destroy())

#theme
window.tk.call("source", os.path.join("theme", "forest-light.tcl"))
ttk.Style().theme_use("forest-light")
#window.tk.call("source", os.path.join("theme", "forest-dark.tcl"))
#ttk.Style().theme_use("forest-dark")



# ----------------------------------------------------- VARIABLES ---------------------------------------------------- #

#LOAD SAVED SETTINGS
with open("settings.json", "r") as f:
	settings: dict[str, str | dict[str, bool]] = json.load(f)
game_path     = tk.StringVar(value = settings.get("game_path",     ""))
document_path = tk.StringVar(value = settings.get("document_path", ""))
caches: list[CacheFile] = [
	CacheFile("CASPartCache",       "CASPartCache.package",       settings, False),
	CacheFile("compositorCache",    "compositorCache.package",    settings, False),
	CacheFile("scriptCache",        "scriptCache.package",        settings, False),
	CacheFile("simCompositorCache", "simCompositorCache.package", settings, False),
	CacheFile("socialCache",        "socialCache.package",        settings, False),
	CacheFile("WorldCaches",        "WorldCaches.package",        settings, False),
	CacheFile("IGACache",           "IGACache.package",           settings, False),
	CacheFile("SigsCache",          "SigsCache.package",          settings, False),
	CacheFile("DCCache",            "DCCache.package",            settings, False),
	CacheFile("ScriptErrorLogs",    "Scripterror_*.xml",          settings, False),
	CacheFile("FeaturedItems",      "Scripterror_*.xml",          settings, False),
	CacheFile("ExportDB",           "Scripterror_*.xml",          settings, False),
]
eps: list[DLC] = [
	DLC("Game", "Base Game",        "base.package", settings, True ),
	DLC("EP1",  "World Adventures", "ep1.package",  settings, True ),
	DLC("EP2",  "Ambitions",        "ep2.package",  settings, True ),
	DLC("EP3",  "Late Night",       "ep3.package",  settings, True ),
	DLC("EP4",  "Generations",      "ep4.package",  settings, True ),
	DLC("EP5",  "Pets",             "ep5.package",  settings, True ),
	DLC("EP6",  "Showtime",         "ep6.package",  settings, True ),
	DLC("EP7",  "Supernatural",     "ep7.package",  settings, True ),
	DLC("EP8",  "Seasons",          "ep8.package",  settings, True ),
	DLC("EP9",  "University Life",  "ep9.package",  settings, True ),
	DLC("EP10", "Island Paradise",  "ep10.package", settings, True ),
	DLC("EP11", "Into the Future",  "",             settings, True ),
]
sps: list[DLC] = [
	DLC("SP1", "High-End Loft Stuff",       "sp1.package", settings, True ),
	DLC("SP2", "Fast Lane Stuff",           "sp2.package", settings, True ),
	DLC("SP3", "Outdoor Living Stuff",      "sp3.package", settings, True ),
	DLC("SP4", "Town Life Stuff",           "sp4.package", settings, True ),
	DLC("SP5", "Master Suite Stuff",        "sp5.package", settings, True ),
	DLC("SP6", "Katy Perry's Sweet Treats", "sp6.package", settings, False),
	DLC("SP7", "Diesel Stuff",              "sp7.package", settings, True ),
	DLC("SP8", "70s, 80s, & 90s Stuff",     "sp8.package", settings, True ),
	DLC("SP9", "Movie Stuff",               "sp9.package", settings, True ),
]



# --------------------------------------------------- GUI FUNCTIONS -------------------------------------------------- #

def set_all(a: list[DLC] | list[CacheFile], set_to: bool):
	for i in a:
		i.var.set(set_to)

def execute():
	#VALIDATE PATH
	if not document_path.get() or not os.path.exists(document_path.get()):
		messagebox.showerror("Directory Error", "Document folder does not exist. Please choose a valid directory.")
		return
	
	#SAVE SETTINGS
	with open("settings.json", "w") as f:
		dump = {
			"game_path":     game_path.get(),
			"document_path": document_path.get(),
			"caches": {cache.name: cache.var.get() for cache in caches},
			"dlcs":    {dlc.id:    dlc.var.get()   for dlc in eps + sps},
		}
		json.dump(dump, f, indent = "\t") #, default = lambda x: x.__dict__()
	print("Saved settings successfully.")
	
	#DELETE ALL SELECTED CACHE FILES
	for cache in caches:
		if cache.var.get():
			cache.remove()
	print("Removed all selected cache files successfully.")

	#CHOOSE RANDOM DLC
	allowed_dlcs = [dlc for dlc in eps + sps if dlc.var.get()]
	if not allowed_dlcs:
		messagebox.showerror("Selection Error", "No DLCs selected.")
		return
	chosen_dlc = random.choice(allowed_dlcs)
	print(f"Chosen DLC: {chosen_dlc.name}")
	chosen_dlc.choose_this()

	#END PROGRAM
	window.destroy()



# ------------------------------------------------------ LAYOUT ------------------------------------------------------ #

#PATH SELECTOR
frame_path = ttk.LabelFrame(window, text = "Path Selector", padding = 10)
#GAME PATH
ttk.Label(frame_path, text = "Path to The Sims 3 folder: (optional)").pack()
frame_path_select = tk.Frame(frame_path)
ttk.Entry(frame_path_select, state = "readonly", cursor = "arrow", textvariable = game_path).pack(fill = tk.BOTH, expand = True, side = tk.LEFT, padx = (0, 10))
ttk.Button(frame_path_select, text = "Browse directory...", cursor = "hand2", command = lambda: game_path.set(filedialog.askdirectory(title = "Select Sims 3 folder")), style = "Accent.TButton").pack()
frame_path_select.pack(fill = tk.BOTH, expand = True, pady = (0, 10))
#DOCUMENT PATH
ttk.Label(frame_path, text = "Path to The Sims 3 in Documents folder:").pack()
frame_path_select = tk.Frame(frame_path)
ttk.Entry(frame_path_select, state = "readonly", cursor = "arrow", textvariable = document_path).pack(fill = tk.BOTH, expand = True, side = tk.LEFT, padx = (0, 10))
ttk.Button(frame_path_select, text = "Browse directory...", cursor = "hand2", command = lambda: document_path.set(filedialog.askdirectory(title = "Select Sims 3 in Documents folder")), style = "Accent.TButton").pack()
frame_path_select.pack(fill = tk.BOTH, expand = True)
frame_path.pack(fill = "both", expand = "yes", padx = 20, pady = 10)

frame_settings = tk.Frame(window)
frame_settings.grid_columnconfigure(0, weight = 1)
frame_settings.grid_columnconfigure(1, weight = 1)

#CACHE FILE SELECTOR
frame_settings_cache = ttk.LabelFrame(frame_settings, text = "Cache Cleaner", padding = 10)
ttk.Button(frame_settings_cache, cursor = "hand2", text = "Select all",   command = lambda: set_all(caches, True ), width = 10, style = "Accent.TButton").pack(pady = (0, 5))
ttk.Button(frame_settings_cache, cursor = "hand2", text = "Deselect all", command = lambda: set_all(caches, False), width = 10, style = "Accent.TButton").pack(pady = (0, 5))
temporary_disable = False
for cachefile in caches:
	if cachefile.name == "WorldCaches":
		temporary_disable = True
	if temporary_disable:
		ttk.Checkbutton(frame_settings_cache, cursor = "hand2", text = cachefile.name, variable = cachefile.var, state = tk.DISABLED).pack(anchor = "w", pady = 2)
		continue
	ttk.Checkbutton(frame_settings_cache, cursor = "hand2", text = cachefile.name, variable = cachefile.var).pack(anchor = "w", pady = 2)
frame_settings_cache.grid(row = 0, column = 0, sticky = "NESW", padx = (20, 10), pady = 10)

#TITLE SCREEN SELECTOR
frame_settings_title = ttk.LabelFrame(frame_settings, text = "Title Screen Selector", padding = 10)
frame_settings_title_ep = tk.Frame(frame_settings_title)
ttk.Button(frame_settings_title_ep, cursor = "hand2", text = "Select all",   command = lambda: set_all(eps, True ), width = 10, style = "Accent.TButton").pack(pady = (0, 5))
ttk.Button(frame_settings_title_ep, cursor = "hand2", text = "Deselect all", command = lambda: set_all(eps, False), width = 10, style = "Accent.TButton").pack(pady = (0, 5))
for ep in eps:
	ttk.Checkbutton(frame_settings_title_ep, cursor = "hand2", text = ep.name, variable = ep.var).pack(anchor = "w", pady = 2)
frame_settings_title_ep.pack(side = tk.LEFT, padx = (0, 10))
frame_settings_title_sp = tk.Frame(frame_settings_title)
ttk.Button(frame_settings_title_sp, cursor = "hand2", text = "Select all",   command = lambda: set_all(sps, True ), width = 10, style = "Accent.TButton").pack(pady = (0, 5))
ttk.Button(frame_settings_title_sp, cursor = "hand2", text = "Deselect all", command = lambda: set_all(sps, False), width = 10, style = "Accent.TButton").pack(pady = (0, 5))
for sp in sps:
	ttk.Checkbutton(frame_settings_title_sp, cursor = "hand2", text = sp.name, variable = sp.var).pack(anchor = "w", pady = 2)
frame_settings_title_sp.pack()
frame_settings_title.grid(row = 0, column = 1, sticky = "NESW", padx = (10, 20), pady = 10)
frame_settings.pack(fill = "both", expand = "yes")

#BUTTONS
#ttk.Label(window,  cursor = "hand2", text = "License").pack(anchor = "w")
ttk.Button(window, cursor = "hand2", text = "Confirm", width = 10, style = "Accent.TButton", command = execute).pack(pady = (10, 20))

#CENTER WINDOW
tkinter_center(window)



# ----------------------------------------------------- MAINLOOP ----------------------------------------------------- #

window.mainloop()

"""
try:
	for files in os.scandir("WorldCaches"):
		os.remove(files.path)
	
	end()
	#check following deletion instructions for correctness
	for files in os.scandir("IGACache"):
		os.remove(files.path)
	for files in os.scandir("SigsCache"):
		if files.name.endswith(".bin"):
			os.remove(files.path)
	os.remove(os.path.join("DCCache", "missingdeps.idx"))
	os.remove(os.path.join("DCCache", "dcc.ent"))
except FileNotFoundError:
	print("File not found.")
except PermissionError:
	print("Permission denied.")
except:
	print("File is still in use.")
"""