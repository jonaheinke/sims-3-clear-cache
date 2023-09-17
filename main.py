# ------------------------------------------------------ IMPORTS ----------------------------------------------------- #

#standard library imports
import argparse, glob, json, os, random, shutil, subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, InitVar

#third party imports
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

#changing the working directory, so that the program can be run from any path
os.chdir(os.path.dirname(os.path.realpath(__file__)))

#local imports
from tooltip import CreateToolTip



# -------------------------------------------- READ COMMAND LINE ARGUMENTS ------------------------------------------- #

parser = argparse.ArgumentParser(description = "The Sims 3 Management Program")
parser.add_argument("-l", "--light", action = "store_true", help = "switch to light mode")
parser.add_argument("-d", "--debug", action = "store_true", help = "enable debug mode (not recommended)")
parser.add_argument("--settings", type = str, default = "settings.json", help = "name of the settings file")
args = parser.parse_args()



# ----------------------------------------------- WINDOW INITIALIZATION ---------------------------------------------- #

#window init
window = tk.Tk()
window.title("The Sims 3 Management Program")
window.resizable(False, False)

#keyboard bindings
def focus_next_widget(event):
	event.widget.tk_focusNext().focus()
	return("break")
def focus_prev_widget(event):
	event.widget.tk_focusPrev().focus()
	return("break")
window.bind("<Tab>", focus_next_widget)
window.bind("<Shift-Tab>", focus_prev_widget)
window.bind("<Escape>", lambda _: window.destroy())

#theme
window.tk.call("source", os.path.join("theme", "forest-light.tcl" if args.light else "forest-dark.tcl"))
ttk.Style().theme_use("forest-light" if args.light else "forest-dark")



# ----------------------------------------------------- VARIABLES ---------------------------------------------------- #

#LOAD SAVED SETTINGS
try:
	with open(args.settings, "r") as f:
		settings: dict[str, str | dict[str, bool]] = json.load(f)
except json.JSONDecodeError:
	settings = {}
except FileNotFoundError:
	settings = {}
except:
	settings = {}

#DEFAULT DOCUMENT PATH
document_path_value = settings.get("document_path", "")
if not document_path_value or not os.path.isdir(document_path_value):
	document_path_value = next(glob.iglob(os.path.join(os.path.expanduser("~"), "Documents", "Electronic Arts", "* Sims 3")), "")

#DEFAULT GAME PATH
game_path_value = settings.get("game_path", "")
if not game_path_value or not os.path.isdir(game_path_value):
	possible_locations = [
		"C:\Program Files (x86)\Steam\steamapps\common\The Sims 3",
		"C:\Program Files (x86)\Origin Games\The Sims 3",
		"C:\Program Files\Origin Games\The Sims 3",
		"C:\Programs\Origin Games\The Sims 3",
		"C:\Program Files (x86)\Electronic Arts\The Sims 3",
		"C:\Program Files\Electronic Arts\The Sims 3",
		"C:\Programs\Electronic Arts\The Sims 3",
	]
	for location in possible_locations:
		if os.path.isdir(location):
			game_path_value = location
			break
	else:
		game_path_value = ""
		print("Game install location not found.")

#CREATE VARIABLES
game_path     = tk.StringVar(value = game_path_value)
document_path = tk.StringVar(value = document_path_value)
save_settings = tk.BooleanVar(value = True)



# ---------------------------------------------------- DATACLASSES --------------------------------------------------- #

@dataclass
class CheckButtonClass(ABC):
	name: str = ""
	filename: str = ""
	settings: InitVar[dict[str, str | dict[str, bool]]] = {}
	default: InitVar[bool] = True
	var: tk.BooleanVar | None = field(default = None, init = False, hash = False)
	checkbutton: ttk.Checkbutton = field(default = None, init = False, repr = False, hash = False, compare = False)

	def __hash__(self) -> int:
		return hash(self.name + self.filename)

	@abstractmethod
	def check_if_exists(self) -> bool:
		pass

	def set_disabled_state(self, value: bool | str):
		if not self.checkbutton:
			return
		if isinstance(value, bool):
			value = "normal" if value else "disabled"
		self.checkbutton.config(state = value)

	def get_checkbutton(self, frame: tk.Tk | tk.Toplevel | tk.Frame) -> ttk.Checkbutton:
		if not self.checkbutton:
			self.checkbutton = ttk.Checkbutton(frame, cursor = "hand2", text = self.name, variable = self.var)
		return self.checkbutton



@dataclass
class CacheFile(CheckButtonClass):
	description: str = ""

	def __post_init__(self, settings, default):
		value = default
		if settings and "caches" in settings and self.name in settings["caches"]:
			value = settings["caches"][self.name]
		self.var = tk.BooleanVar(value = value)
	
	def check_if_exists(self) -> bool:
		exists = next(glob.iglob(self.filename, root_dir = document_path.get()), None) is not None
		if args.debug:
			print(f"Cache file {self.name}, exists: {exists}")
			print(glob.glob(self.filename, root_dir = document_path.get())[:3], "etc.")
			print()
		self.set_disabled_state(exists)
		return exists

	def remove(self):
		files = glob.iglob(self.filename, root_dir = document_path.get())
		if args.debug:
			print(f"To be removed as {self.name}:")
			print(list(files))
			return
		for file in files:
			try:
				os.remove(os.path.join(document_path.get(), file))
			except PermissionError:
				print("Permission denied.")
			except:
				print("File is still in use.")



@dataclass
class DLC(CheckButtonClass):
	id: str = "EPXX"

	def __post_init__(self, settings, default):
		value = default
		if settings and "dlcs" in settings and self.id in settings["dlcs"]:
			value = settings["dlcs"][self.id]
		self.var = tk.BooleanVar(value = value)

	def check_if_exists(self) -> bool:
		if not game_path.get():
			self.set_disabled_state(True)
			return True
		is_installed = os.path.isdir(os.path.join(game_path.get(), self.id))
		if not is_installed:
			self.var.set(False)
		self.set_disabled_state(is_installed)
		return is_installed

	def choose_this(self):
		path_to_mod = os.path.join(document_path.get(), "Mods", "Packages", "randomized-loading-screen-theme.package")
		if not isinstance(self.filename, str):
			print("Error selecting DLC: filename is not a string")
		if self.filename:
			shutil.copy(os.path.join("dlcs", self.filename), path_to_mod)
		else:
			try:
				os.remove(path_to_mod)
			except:
				pass



# -------------------------------------------------- OTHER VARIABLES ------------------------------------------------- #

caches: list[CacheFile] = [
	CacheFile("CASPartCache",       "CASPartCache.package",            settings, True , "CAS parts that appear in Create-A-Sim"),
	CacheFile("compositorCache",    "compositorCache.package",         settings, True , "New objects that would appear in Buy/Build mode"),
	CacheFile("scriptCache",        "scriptCache.package",             settings, True , "Mod Cache"),
	CacheFile("simCompositorCache", "simCompositorCache.package",      settings, True , "New Sims, default skins"),
	CacheFile("socialCache",        "socialCache.package",             settings, True , "Information about the social aspects (Introduced with Patch 1.31)"),
	CacheFile("WorldCaches",        "WorldCaches/*.package",           settings, True , "FOR WINDOWS ONLY! Caches for Save Worlds and Travel Worlds, WILL BREAK MAP HOVER TAGS ON MACOS!"),
	CacheFile("DCCache",            "DCCache/*",                       settings, False, "EXPERIMENTAL: DOES NOT WORK CORRECTLY! DO NOT CHECK! Check if launcher or game continues to crash, corrupted files will be regenerated"),
	CacheFile("IGACache",           "IGACache/*",                      settings, False, "Check if launcher or game continues to crash, corrupted files will be regenerated"),
	CacheFile("SigsCache",          "SigsCache/*.bin",                 settings, False, "Check if launcher or game continues to crash, corrupted files will be regenerated"),
	CacheFile("FeaturedItems",      "FeaturedItems/*.png",             settings, False, "Check if you deinstalled third party items, might slow down the game for first two minutes"),
	CacheFile("Thumbnails",         "Thumbnails/*.package",            settings, False, "Check if you deinstalled third party items, might slow down the game for first two minutes"),
	CacheFile("Sims3Logs",          "Sims3Logs.xml",                   settings, True , "Allows the launcher to correctly close upon shutdown, non-existing update processes will be skipped, typical issue with Steam version of the game"),
	CacheFile("ScriptErrorLogs",    "ScriptError_*.xml",               settings, False, "Error Log Files generated by NRaas ErrorTrap"),
	CacheFile("ExportDB",           "Saves/*.sims3/*ExportDB.package", settings, False, "EXPERIMENTAL: DO NOT CHECK UNLESS ABSOLUTELY NECESSARY!"),
]
eps: list[DLC] = [
	DLC("Base Game",        "base.package", settings, True , id = "Game"),
	DLC("World Adventures", "ep1.package",  settings, True , id = "EP1" ),
	DLC("Ambitions",        "ep2.package",  settings, True , id = "EP2" ),
	DLC("Late Night",       "ep3.package",  settings, True , id = "EP3" ),
	DLC("Generations",      "ep4.package",  settings, True , id = "EP4" ),
	DLC("Pets",             "ep5.package",  settings, True , id = "EP5" ),
	DLC("Showtime",         "ep6.package",  settings, True , id = "EP6" ),
	DLC("Supernatural",     "ep7.package",  settings, True , id = "EP7" ),
	DLC("Seasons",          "ep8.package",  settings, True , id = "EP8" ),
	DLC("University Life",  "ep9.package",  settings, True , id = "EP9" ),
	DLC("Island Paradise",  "ep10.package", settings, True , id = "EP10"),
	DLC("Into the Future",  "",             settings, True , id = "EP11"),
]
sps: list[DLC] = [
	DLC("High-End Loft Stuff",       "sp1.package", settings, True , id = "SP1"),
	DLC("Fast Lane Stuff",           "sp2.package", settings, True , id = "SP2"),
	DLC("Outdoor Living Stuff",      "sp3.package", settings, True , id = "SP3"),
	DLC("Town Life Stuff",           "sp4.package", settings, True , id = "SP4"),
	DLC("Master Suite Stuff",        "sp5.package", settings, True , id = "SP5"),
	DLC("Katy Perry's Sweet Treats", "sp6.package", settings, True , id = "SP6"),
	DLC("Diesel Stuff",              "sp7.package", settings, True , id = "SP7"),
	DLC("70s, 80s, & 90s Stuff",     "sp8.package", settings, True , id = "SP8"),
	DLC("Movie Stuff",               "sp9.package", settings, True , id = "SP9"),
]



# --------------------------------------------------- GUI FUNCTIONS -------------------------------------------------- #

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

def set_all(a: list[DLC] | list[CacheFile], set_to: bool):
	for i in a:
		i.var.set(set_to)

def update_all_checkbutton_states():
	for checkbutton in caches + eps + sps:
		checkbutton.check_if_exists()
	window.update_idletasks()

def set_game_path():
	game_path.set(filedialog.askdirectory(title = "Select Sims 3 folder"))
	update_all_checkbutton_states()

def set_document_path():
	document_path.set(filedialog.askdirectory(title = "Select Sims 3 in Documents folder"))
	update_all_checkbutton_states()

def execute():
	#VALIDATE PATH
	if not document_path.get() or not os.path.exists(document_path.get()):
		messagebox.showerror("Directory Error", "Document folder does not exist. Please choose a valid directory.")
		return
	
	#SAVE SETTINGS
	if save_settings.get():
		dump = {
			"game_path":     game_path.get(),
			"document_path": document_path.get(),
			"caches": {cache.name: cache.var.get() for cache in caches},
			"dlcs":   {dlc.id:     dlc.var.get()   for dlc in eps + sps},
		}
		with open(args.settings, "w") as f:
			json.dump(dump, f, indent = "\t")
	
	#DELETE ALL SELECTED CACHE FILES
	for cache in caches:
		if cache.var.get():
			cache.remove()

	#CHOOSE RANDOM DLC
	allowed_dlcs = [dlc for dlc in eps + sps if dlc.var.get()]
	if not allowed_dlcs:
		messagebox.showerror("Selection Error", "No DLCs selected.")
		return
	chosen_dlc = random.choice(allowed_dlcs)
	#print(f"Chosen DLC: {chosen_dlc.name}")
	chosen_dlc.choose_this()

	#END PROGRAM
	window.destroy()

def confirm():
	execute()

def confirm_and_start_launcher():
	execute()
	try:
		subprocess.Popen(os.path.join(game_path.get(), "Game", "Bin", "Sims3LauncherW.exe"))
	except OSError:
		messagebox.showerror("File Error", "Sims3LauncherW.exe not found. Launcher could not be started.")

def confirm_and_start_game():
	execute()
	try:
		subprocess.Popen(os.path.join(game_path.get(), "Game", "Bin", "TS3W.exe"))
	except OSError:
		messagebox.showerror("File Error", "TS3W.exe not found. Game could not be started.")



# ------------------------------------------------------ LAYOUT ------------------------------------------------------ #

#PATH SELECTOR
frame_path = ttk.LabelFrame(window, text = "Select Path", padding = 10)
#GAME PATH
ttk.Label(frame_path, text = "Path to The Sims 3 installation folder: (optional)").pack()
frame_path_select = tk.Frame(frame_path)
ttk.Entry(frame_path_select, state = "readonly", cursor = "arrow", textvariable = game_path).pack(fill = tk.BOTH, expand = True, side = tk.LEFT, padx = (0, 10))
ttk.Button(frame_path_select, text = "Browse directory...", cursor = "hand2", command = set_game_path, style = "Accent.TButton").pack()
frame_path_select.pack(fill = tk.BOTH, expand = True, pady = (0, 10))

#DOCUMENT PATH
ttk.Label(frame_path, text = "Path to The Sims 3 in your Documents folder:").pack()
frame_path_select = tk.Frame(frame_path)
ttk.Entry(frame_path_select, state = "readonly", cursor = "arrow", textvariable = document_path).pack(fill = tk.BOTH, expand = True, side = tk.LEFT, padx = (0, 10))
ttk.Button(frame_path_select, text = "Browse directory...", cursor = "hand2", command = set_document_path, style = "Accent.TButton").pack()
frame_path_select.pack(fill = tk.BOTH, expand = True)
frame_path.pack(fill = "both", expand = "yes", padx = 20, pady = (20, 10))

frame_settings = tk.Frame(window)
frame_settings.grid_columnconfigure(0, weight = 1)
frame_settings.grid_columnconfigure(1, weight = 1)

#CACHE FILE SELECTOR
frame_settings_cache = ttk.LabelFrame(frame_settings, text = "Cache Cleaner", padding = 10)
ttk.Button(frame_settings_cache, cursor = "hand2", text = "Select all",   command = lambda: set_all(caches, True ), width = 10, style = "Accent.TButton").pack(pady = (0, 5))
ttk.Button(frame_settings_cache, cursor = "hand2", text = "Deselect all", command = lambda: set_all(caches, False), width = 10, style = "Accent.TButton").pack(pady = (0, 5))
for cache in caches:
	checkbutton = cache.get_checkbutton(frame_settings_cache)
	checkbutton.pack(anchor = "w", pady = 2)
	CreateToolTip(checkbutton, cache.description)
frame_settings_cache.grid(row = 0, column = 0, sticky = "NESW", padx = (20, 10), pady = 10)

#TITLE SCREEN SELECTOR
frame_settings_title = ttk.LabelFrame(frame_settings, text = "Title Screen Selector", padding = 10)
frame_settings_title_ep = tk.Frame(frame_settings_title)
ttk.Button(frame_settings_title_ep, cursor = "hand2", text = "Select all",   command = lambda: set_all(eps, True ), width = 10, style = "Accent.TButton").pack(pady = (0, 5))
ttk.Button(frame_settings_title_ep, cursor = "hand2", text = "Deselect all", command = lambda: set_all(eps, False), width = 10, style = "Accent.TButton").pack(pady = (0, 5))
for ep in eps:
	ep.get_checkbutton(frame_settings_title_ep).pack(anchor = "w", pady = 2)
	#ttk.Checkbutton(frame_settings_title_ep, cursor = "hand2", text = ep.name, variable = ep.var)
frame_settings_title_ep.grid(row = 0, column = 0, sticky = "NESW", padx = (0, 10))
frame_settings_title_sp = tk.Frame(frame_settings_title)
ttk.Button(frame_settings_title_sp, cursor = "hand2", text = "Select all",   command = lambda: set_all(sps, True ), width = 10, style = "Accent.TButton").pack(pady = (0, 5))
ttk.Button(frame_settings_title_sp, cursor = "hand2", text = "Deselect all", command = lambda: set_all(sps, False), width = 10, style = "Accent.TButton").pack(pady = (0, 5))
for sp in sps:
	sp.get_checkbutton(frame_settings_title_sp).pack(anchor = "w", pady = 2)
	#ttk.Checkbutton(frame_settings_title_sp, cursor = "hand2", text = sp.name, variable = sp.var).pack(anchor = "w", pady = 2)
frame_settings_title_sp.grid(row = 0, column = 1, sticky = "NESW")
frame_settings_title.grid(row = 0, column = 1, sticky = "NESW", padx = (10, 20), pady = 10)
frame_settings.pack(fill = "both", expand = "yes")

#BUTTONS
#ttk.Label(window, cursor = "hand2", text = "License").pack(anchor = "w")
ttk.Checkbutton(window, cursor = "hand2", text = "Save Settings", variable = save_settings).pack(pady = 10)
ttk.Button(window, cursor = "hand2", text = "Confirm and Start Game",    width = 22, style = "Accent.TButton", command = confirm_and_start_game    ).pack(side = tk.RIGHT, padx = (10, 20), pady = (10, 20))
ttk.Button(window, cursor = "hand2", text = "Confirm and Open Launcher", width = 25, style = "Accent.TButton", command = confirm_and_start_launcher).pack(side = tk.RIGHT, padx = (10, 10), pady = (10, 20))
ttk.Button(window, cursor = "hand2", text = "Confirm",                   width = 10, style = "Accent.TButton", command = confirm                   ).pack(side = tk.RIGHT, padx = (20, 10), pady = (10, 20))



# ----------------------------------------------------- MAINLOOP ----------------------------------------------------- #

#UPDATE CHECKBUTTON DISABLED STATES
update_all_checkbutton_states()

#CENTER WINDOW
tkinter_center(window)

window.mainloop()