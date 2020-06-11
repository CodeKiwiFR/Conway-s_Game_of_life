"""
Python - Game of life with tkinter
06/06/2020
Madipoupou
"""

import tkinter as tk
import tkinter.font as font
from tkinter import filedialog
from tkinter import ttk
from .GridCanvas import GridCanvas
from .CellGrid import CellGrid

class ToolBox(object):
    """
    Just a class to put some tools in order to debug or test things
    -> Not supposed to be a part of the final version
    """
    @classmethod
    def print_key(self, key):
        print(key)

class App(tk.Tk):
    """ Class which manages all the application """
    def __init__(self):
        """ Class constructor """
        tk.Tk.__init__(self)
        self.icon = tk.PhotoImage(file='./images/ck.png')
        self.my_font = font.Font(family='system', size=15, weight='bold')
        self.iconphoto(False, self.icon)
        self.geometry('1200x700')
        self.geometry('+0+0')
        self.configure(bg='dark slate gray')
        self.resizable(False, False)
        self.title('Conway\'s GAME OF LIFE')
        self.option_add('*Background', 'dark slate gray')
        self.anim_speed = 100
        self.is_animated = False
        self.create_mode = False

        # Preparing file browser (hide hidden files from it)
        self.init_file_browser()
        
        # Initialize grid
        self.grid = CellGrid([])

        # Buttons binding
        self.bind('<Escape>', lambda event: self.quit())

        self.welcome_menu()
        self.mainloop()
    
    def init_file_browser(self):
        """
        Call a dummy dialog with an impossible option to initialize the file
        dialog without really getting a dialog window; this will throw a
        TclError, so we need a try...except :
        """
        try:
            try:
                self.tk.call('tk_getOpenFile', '-foobarbaz')
            except tk.TclError:
                pass
            # now set the magic variables accordingly
            self.tk.call('set', '::tk::dialog::file::showHiddenBtn', '1')
            self.tk.call('set', '::tk::dialog::file::showHiddenVar', '0')
        except:
            pass

    def main_win(self):
        """ Just a window to test my canvas and the functionalities """

        # Frame which contains all the window -> full window container
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Canvas part
        self.can = GridCanvas(boss=self.container)
        self.can.grid(row=0, column=0, padx=5, pady=5)

        # Right panel
        self.right_frame = tk.Frame(
            self.container, bg='slate gray',
            width=175, height=600,
        )
        self.right_frame.grid(row=0, column=1, padx=5, pady=5)
        self.right_frame.grid_propagate(0)
        self.right_frame.columnconfigure(0, weight=1)
        self.start_button = tk.Button(
            self.right_frame,
            fg='white', highlightthickness=0,
            font=self.my_font, width=60, height=2,
            text='START', command=self.start_anim
        )
        self.start_button.grid(row=0, padx=5, pady=10)

        # Adding create button
        self.create_button = tk.Button(
            self.right_frame,
            fg='white', highlightthickness=0,
            font=self.my_font, width=60, height=2,
            text='CREATE: OFF', command=self.create
        )
        self.create_button.grid(row=1, padx=5, pady=10)

        # Adding save/reload buttons
        tk.Button(
            self.right_frame,
            fg='white', highlightthickness=0,
            font=self.my_font, width=60, height=2,
            text='SAVE', command=self.grid.save_cells
        ).grid(row=2, padx=5, pady=10)
        tk.Button(
            self.right_frame,
            fg='white', highlightthickness=0,
            font=self.my_font, width=60, height=2,
            text='LOAD',
            command=lambda: self.grid.load_cells(self.can) or self.cycle_label.configure(text=f'CYCLE: {self.grid.cycle_num}')
        ).grid(row=3, padx=5, pady=10)

        # Adding speed frame and buttons
        self.speed_frame = tk.Frame(
            self.right_frame, bg='dark slate gray',
            width=170, height=80,
        )
        self.speed_frame.grid(row=4, padx=5, pady=10)
        self.speed_frame.grid_propagate(0)
        self.speed_frame.columnconfigure(0, weight=1)
        tk.Label(
            self.speed_frame, text='SPEED',
            fg='white', font=self.my_font
        ).grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        tk.Button(
            self.speed_frame,
            fg='white', bg='slate gray', highlightthickness=0,
            font=self.my_font,
            text='-', command=lambda: self.change_speed(10)
        ).grid(row=1, column=0, padx=5, pady=5, sticky='W')
        tk.Button(
            self.speed_frame,
            fg='white', bg='slate gray', highlightthickness=0,
            font=self.my_font,
            text='+', command=lambda: self.change_speed(-10)
        ).grid(row=1, column=1, padx=5, pady=5)

        # Speed and cycle info
        self.speed_label = tk.Label(
            self.right_frame, text='SPEED: 100%',
            bg='slate gray', fg='midnight blue', font=self.my_font
        )
        self.speed_label.grid(row=5, padx=5, pady=(60, 5))
        self.cycle_label = tk.Label(
            self.right_frame, text='CYCLE: 0',
            bg='slate gray', fg='midnight blue', font=self.my_font
        )
        self.cycle_label.grid(row=6, padx=5, pady=5)

        # Bottom panel
        self.bottom_frame = tk.Frame(self.container)
        self.bottom_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        #self.bottom_frame.grid_propagate(0)
        tk.Button(
            self.bottom_frame,
            fg='white', bg='slate gray', highlightthickness=0,
            font=self.my_font, width=15, height=2,
            text='CLEAR CANVAS', command=self.reset
        ).grid(row=0, column=0, padx=5, pady=15)
        tk.Button(
            self.bottom_frame,
            fg='white', bg='slate gray', highlightthickness=0,
            font=self.my_font, width=15, height=2,
            text='HELP', command=lambda: self.change_speed(-10)
        ).grid(row=0, column=1, padx=5, pady=15)
        tk.Button(
            self.bottom_frame,
            fg='white', bg='slate gray', highlightthickness=0,
            font=self.my_font, width=15, height=2,
            text='EXPORT GRID', command=self.export_to_file
        ).grid(row=0, column=2, padx=5, pady=15)
        tk.Button(
            self.bottom_frame,
            fg='white', bg='slate gray', highlightthickness=0,
            font=self.my_font, width=15, height=2,
            text='IMPORT A GRID', command=self.import_from_file
        ).grid(row=0, column=3, padx=5, pady=15)
        tk.Button(
            self.bottom_frame,
            fg='white', bg='gray23', highlightthickness=0,
            font=self.my_font, width=15, height=2,
            text='EXIT', command=self.destroy
        ).grid(row=0, column=4, padx=5, pady=15)

    def reset(self):
        """ Reset all the canvas, cleans all existing cells """
        self.grid.reset(self.can)
        self.cycle_label.configure(text=f'CYCLE: {self.grid.cycle_num}')
        self.anim_speed = 100
        speed = int(1/self.anim_speed * 10000)
        self.speed_label.configure(text=f'SPEED: {speed}%')

    def start_anim(self):
        """ Starts the animation """
        if (not self.is_animated and not self.create_mode):
            self.is_animated = True
            self.animate_game()
            self.start_button.configure(
                text='STOP',
                command=self.stop_anim,
                bg='slate gray'
            )

    def stop_anim(self):
        """ Stops the animation """
        self.is_animated = False
        self.start_button.configure(
            text='START',
            command=self.start_anim,
            bg='dark slate gray'
        )

    def animate_game(self):
        """ Manages the game animation: clean can, launch cycle, render """
        for rect in self.grid.rectangle_ref:
            self.can.delete(rect)
        self.grid.activate_cycle()
        self.grid.render_cells(self.can)
        self.cycle_label.configure(text=f'CYCLE: {self.grid.cycle_num}')
        if (self.is_animated and not self.create_mode):
            self.after(self.anim_speed, self.animate_game)
        
    def change_speed(self, coeff):
        """ Change animation speed """
        if (coeff < 0):
            self.anim_speed = max(self.anim_speed + coeff, 10)
        else:
            self.anim_speed = min(self.anim_speed + coeff, 1000)
        speed = int(1/self.anim_speed * 10000)
        self.speed_label.configure(text=f'SPEED: {speed}%')

    def create(self):
        """ Manage create mode """
        if (self.create_mode):
            self.create_mode = False
            self.can.unbind('<Button-1>')
            self.create_button.configure(text='CREATE: OFF', bg='dark slate gray')
        else:
            self.stop_anim()
            self.create_mode = True
            self.can.bind('<Button-1>', lambda event: self.grid.add_remove_cell(self.can.get_cell_click(event), self.can))
            self.create_button.configure(text='CREATE: ON', bg='red')

    def welcome_menu(self):
        """ Displays the first menu of the application """

        # Inner function which closes the welcome overlay
        def close_welcome(mode):
            self.shape_mode = mode
            self.destroy_overlay(w_list)
            if (self.shape_mode == 1):
                self.wip()
            else:
                self.main_win()
        
        # Creating the welcome interface
        self.w_frame = tk.Frame(
            self, bg='slate gray',
            highlightbackground="black", highlightthickness=2
        )
        self.w_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.w_but_mode1 = tk.Button(
            self.w_frame,
            text='PREDEFINED SHAPES',
            highlightthickness=0,
            fg='white',
            width=50, height=2,
            font=self.my_font,
            command=lambda: close_welcome(1)
        )
        self.w_but_mode1.pack(padx=15, pady=10)
        self.w_but_mode2 = tk.Button(
            self.w_frame,
            text='CREATE SHAPES',
            highlightthickness=0,
            fg='white',
            width=50, height=2,
            font=self.my_font,
            command=lambda: close_welcome(2)
        )
        self.w_but_mode2.pack(padx=15, pady=10)
        w_list = [self.w_frame, self.w_but_mode1, self.w_but_mode2]
    
    def wip(self):
        """ Just temporary function to display work in progress message """
        self.wip_frame = tk.Frame(
            self, bg='slate gray',
            highlightbackground="black", highlightthickness=2
        )
        self.wip_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.wip_label = tk.Label(
            self.wip_frame, text="Work in progress...",
            font=self.my_font, fg='white', bg='slate gray'
        )
        self.wip_label.pack(padx=55, pady=20)

    def destroy_overlay(self, ref_list):
        """ Destroys ref but can be added to welcome_menu method """
        for ref in ref_list:
            ref.destroy()

    def top_error(self, my_str="ERROR"):
        """ A toplevel pops to annouce that an error occured """
        error_win = tk.Toplevel(self)
        error_win.grab_set()
        error_win.geometry('500x400')
        error_win.iconphoto(False, self.icon)
        error_win.geometry('+100+100')
        error_win.resizable(False, False)
        error_win.title('ERROR')
        error_win.bind('<Escape>', lambda event: error_win.destroy())

    def export_to_file(self):
        """ Exports the grid to a file by opening OS explorer """
        if (not self.grid.alive_cells):
            self.top_error('ERROR - The grid is empty')
            return
        filename = filedialog.asksaveasfile(
            parent=self, mode='w', title='Export a pattern'
        )
        if (not filename):
            self.top_error('ERROR - The pattern has not been saved')
            return
        try:
            for cell in self.grid.alive_cells:
                cell_str = f'{cell[0]},{cell[1]}-'
                filename.write(cell_str)
        except:
            self.top_error('ERROR - Writing into the file was not possible')
        finally:
            filename.close()

    def import_from_file(self):
        """ Import a saved grid from a file, opening the explorer """
        filename = filedialog.askopenfilename(title = "Select A File")
        if (not filename):
            return
        try:
            fd = open(filename, 'r')
        except:
            self.top_error('ERROR - Impossible to open the file')
            return
        file_content = fd.read()
        cell_list = file_content.split('-')
        final_cell_list = []
        for cell in cell_list:
            temp = cell.split(',')
            try:
                x = int(temp[0])
                y = int(temp[1])
            except:
                continue
            final_cell_list.append((x, y))
        fd.close()
        if (final_cell_list == []):
            self.top_error('ERROR - The file is not well formatted')
            return
        self.reset()
        self.grid.replace_current_cells(final_cell_list, self.can)
