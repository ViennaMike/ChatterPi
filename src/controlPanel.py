import tkinter as tk
import configparser
import sys
import os
import shutil
import maxVol

class ConfigManager(tk.Toplevel): 
    def __init__(self, parent, configpath='config.ini', 
              oldpath='oldconfig.ini', title='ChatterPi'):
        self.parent = parent
        self.configpath = configpath
        self.oldpath = oldpath
        self.window_title = title
       
        self.parser = configparser.ConfigParser()
        self.load(self.configpath)
        self.build(self.parser_dict)
        shutil.copy2(configpath, oldpath)
         
    def as_dict(self, config) -> dict:
        """
        Converts a ConfigParser object into a dictionary.
        The resulting dictionary has sections as keys which point to a dict of the
        sections options as key : value pairs.
        https://stackoverflow.com/a/23944270
        """
        the_dict = {}
        for section in config.sections():
            the_dict[section] = {}
            for key, val in config.items(section):
                the_dict[section][key] = val
        return the_dict

    def load(self, path):
        if not os.path.exists(self.configpath):
            print('config.ini file is either missing or not in ChatterPi directory')
            sys.exit()
        self.parser.read(path)
        self.parser_dict = self.as_dict(self.parser)
        
    def build(self, parser_dict: dict) -> None:
        """Dynamically populates GUI from the contents of parser_dict"""
        self.parser_dict = parser_dict
        self.fields = []  # list of the input widgets from every section
        self.sections = parser_dict.keys()  # list of all the sections
        self.section_keys = []  # list of keys from every section
        for section in self.sections:
            self.section_keys.extend(self.parser_dict[section].keys())
    
        # make a LabelFrame for each section in the ConfigParser
        for idx, section in enumerate(self.parser_dict.keys()):
            frm = tk.LabelFrame(master=window, relief=tk.RIDGE, borderwidth=5, 
                                text=section.title(), font=('bold'))
            if section.title() in ('Servo', 'Controller'):
                frm['bg'] = 'wheat1'
            frm.grid(row=idx//3 , column=idx%3)
    
            # make a label and Entry/Text widget for each key in the section
            for idx, section_key in enumerate(self.parser_dict[section].keys()):
                self.section_keys.append(section_key)
                frm.grid_rowconfigure(idx, weight=1)
                if section.title() in ('Servo', 'Controller'):
                    tk.Label(frm, text=section_key.title(), bg='wheat1').grid(row=idx, column=0, 
                                            padx=2, pady=2, sticky='e')
                else:
                    tk.Label(frm, text=section_key.title(),).grid(row=idx, column=0, 
                                            padx=2, pady=2, sticky='e')
                ent =  tk.Entry(frm, width=10)
                ent.grid(row=idx, column=1, sticky='W')
                ent.insert(0, self.parser_dict[section][section_key])
                # after deciding which to make, add to a list for convenience
                self.fields.append(ent)
         
        # Revert back to values in old config file
        reset_txt = tk.Label(text="Reset values back values when first opened", justify='left')
        reset_txt.grid(row=3, column=0)
        reset_button = tk.Button(text='RESET', font=('bold'), bg='blue', fg='white', 
                                 width=15, height=2, borderwidth=5, command=lambda: [self.load(self.oldpath), 
                                 self.build(self.parser_dict)])
        reset_button.grid(row=2, column=0)
        
        # Write changes back to config file
        save_txt = tk.Label(text="""Note: only new values for the Servo and Controller parameters will take
        effect while ChatterPi is running (at start of next vocal). ChatterPi must be 
        restarted for changes to the other parameters to take effect.""", justify='left')
        save_txt.grid(row=3, column=1)
        save_button = tk.Button(text='SAVE', font=('bold'), bg='green', fg='white', 
                                width=15, height=2, borderwidth=5, command=lambda: self.save_config())
        save_button.grid(row=2, column=1)
        
        # Add box for the maximize volume buttons
        vol_frm = tk.LabelFrame(master=window, relief=tk.RIDGE, borderwidth=5, 
                                text='Maximize Audio Volume', font=('bold'))
        vol_frm.grid(row=1, column=2)
              
        # maximize volume of all audio files in vocals folder
        voice_button = tk.Button(master=vol_frm, text='Vocals', 
                                 font=('bold'), bg='deep pink', fg='white', 
                                width=10, height=1, borderwidth=5,
                                command=lambda: maxVol.multimax('vocals'))
        voice_button.pack(padx=10, pady=5)
        
        
        # maximize volume of all audio files in ambient folder
        ambient_button = tk.Button(master=vol_frm, text='Ambient', font=('bold'), bg='hot pink', fg='white', 
                                width=10, height=1, borderwidth=5, 
                                command=lambda: maxVol.multimax('ambient'))
        ambient_button.pack(padx=10, pady=5)        

    def save_config(self):
        """Saves the contents of the form to configpath if one was passed."""
        # collect all the inputs
        all_inputs = []
        for child in self.fields:  # filter getting by widget class
            if isinstance(child, tk.Entry):
                all_inputs.append(child.get())
    
        new_parser_dict = {}
        for section in self.sections:
            new_parser_dict[section] = {}
            for section_key, input in zip(self.section_keys, all_inputs):
                if section_key in self.parser_dict[section]:
                    # configparser uses ordereddicts by default
                    # this should maintain their order
                    new_parser_dict[section][section_key] = input
    
        parser = configparser.ConfigParser()
        parser.read_dict(new_parser_dict)
    
        with open(self.configpath, 'w') as configfile:
            parser.write(configfile)
    
        # reset the form to reflect the changes
        self.build(new_parser_dict)

if __name__ == '__main__':
    path = 'ChatterPi/config.ini'
    window = tk.Tk()
    configuration = ConfigManager(window)
    window.title("ChatterPi Control Panel")
    window.columnconfigure(1, pad=10)
    window.columnconfigure(0, pad=10)
    window.columnconfigure(2, pad=10)
    window.rowconfigure(0, pad=10)
    window.rowconfigure(1, pad=10)
    window.rowconfigure(2, pad=10)
    
    window.mainloop()
