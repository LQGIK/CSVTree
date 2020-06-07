""" IMPORTS """
import csv
from tkinter import *
from tkinter import ttk
from tkinter import filedialog


# Global Declarations
global folder_img


class Folder:
    """
    Array of Subfolders
    Array of Info
    """

    def __init__(self, name, sub, data):
        """ Create new folder """
        self.name = name
        self.sub = sub
        self.data = data

def tokenize(path):
    """
    Simply breaks path into each directory
    """
    cleanup = path.split("\\")
    tokens = [i for i in cleanup if i]

    # Make repeats unique
    for token in tokens:
        # Check for repeats
        repeats = getIndexPositions(tokens, token)
        if len(repeats) > 1:

            # Make each repeat value different
            for repeat in repeats[1:]:
                tokens[repeat] += ("?" * repeat)
    
    return tokens

def getIndexPositions(listOfElements, element):
    ''' Returns the indexes of all occurrences of give element in
    the list- listOfElements '''
    indexPosList = []
    indexPos = 0
    while True:
        try:
            # Search for item in list from indexPos to the end of list
            indexPos = listOfElements.index(element, indexPos)
            # Add the index position in list
            indexPosList.append(indexPos)
            indexPos += 1
        except ValueError as e:
            break
    return indexPosList

def explore(ntfs, tokens, depth, data):
    """
    Recursive function that iterates through NTFS Filesystem and creates a map in memory using the Folder Object
    """


    # If we've matched the name of the target folder
    if tokens[-1] == ntfs.name:

        # Omit these accounts
        if data != "NT AUTHORITY\SYSTEM" and data != "BUILTIN\Administrators":

            # Update subfolders and add account names to subfolder
            ntfs.data.append(data)

        return ntfs

    # Get the next directory to follow. If it doesn't exist, create it
    direct_subdir = tokens[tokens.index(ntfs.name) + 1]
    sub_names = [x.name for x in ntfs.sub]
    if direct_subdir in sub_names:
        i = sub_names.index(direct_subdir)
        explore(ntfs.sub[i], tokens, depth + 1, data)
        
    else:
        ntfs.sub.append(Folder(direct_subdir, [], []))
        explore(ntfs.sub[-1], tokens, depth + 1, data)

    return ntfs    

def load(csv_name):
    """
    Loads a given csv with file or path names and returns a ntfs structure with labels on data per folder
    """

    with open(csv_name, newline='') as csvfile:

        # Read file
        csv_reader = list(csv.reader(csvfile))
        root = tokenize(csv_reader[1][0])[0]

        ntfs = Folder(root, [], [])

        labels = csv_reader[0]
        for row in csv_reader[1:]:

            # Declare necessary vars
            path = tokenize(row[0])
            data = row[1]    

            ntfs = explore(ntfs, path, 0, data)

    return ntfs, labels

def tree_load(origin, ntfs, label):
    """
    Recursively inserts branches of file structure 'dir', into tree variable 'origin'
    """

    # Insert data tag
    data = tree.insert(origin, "end", text=label, tag="data")
    # Populate data tag
    for item in ntfs.data:
        #insert item
        tree.insert(data, "end", text=item, tag="data")
        

    # Populate subfolder tag
    for subfolder in ntfs.sub:
        # Insert subfolder
        subfolder_tree = tree.insert(origin, "end", text=subfolder.name.replace("?", ""))

        # Load the subfolder
        tree_load(subfolder_tree, subfolder, label)

def make():

    root.filename = filedialog.askopenfilename(initialdir="/", title="Select A File", filetypes=[("CSV Files", "*.csv")])
    source, labels = load(root.filename)

    # Write formatted data to new file
    file_name = "CSVTreeData.txt"
    with open(file_name, "w") as f:

        # Neatly print out directories with following groups
        f.write(source.name + "\n")
        write(f, source, 1, labels[1])

def write(f, ZimFolder, d, label):
    """
    Writes out to file given the folder struct
    """
    indent = "   " * d

    # Write data
    f.write(indent + label +":\n")
    for item in ZimFolder.data:
        f.write(indent + "  |-> " + item + "\n")

    for subfolder in ZimFolder.sub:
        f.write(indent + subfolder.name + "\n")
        write(f, subfolder, d + 1, label)

# Click Function
def click():

    # Upload a csv
    root.filename = filedialog.askopenfilename(initialdir="/", title="Select A File", filetypes=[("CSV Files", "*.csv")])

    if tree:
        tree.delete(*tree.get_children())

    # Init directory
    source, labels = load(root.filename)

    # Insert aggregated structure into tree
    origin = tree.insert("", "end", "dir", text=source.name, image=folder_img)
    tree_load(origin, source, labels[1])

    # Packing
    tree.pack(fill=BOTH, expand=1)
    




# Initialize Tk()
root = Tk()
root.geometry("450x400")
root.title("CSV Tree")
root.iconbitmap("Icons/gui.ico")


# Image
folder_img = PhotoImage(file="icons/folder.png")


# Styles
style = ttk.Style()
style.configure("mystyle.Treeview", highlightthickness=0, background="#c9c3b9", bd=0, font=('Calibri', 11)) # Modify the font of the body
style.configure("mystyle.Treeview.Heading", font=('Calibri', 13,'bold')) # Modify the font of the headings
style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})]) # Remove the borders



# Tree initialization
tree = ttk.Treeview(root, style="mystyle.Treeview")
tree.tag_configure("data", background="#B1ACA4")

# Label Directions
prompt = Label(text="Upload CSV", font=('Calibri', 11))
directions1 = Label(text="Must consist of a list of folder paths", font=('Calibri', 8))
directions2 = Label(text="and/or single column data on that folder", font=('Calibri', 8))

# Upload button
upload_img = PhotoImage(file="icons/upload.png")
upload_btn = Button(
    root, 
    borderwidth=0,
    image=upload_img,
    command=click,
    pady=20
)

# Save button
save_img = PhotoImage(file="icons/save.png")
save_btn = Button(
    root, 
    borderwidth=0,
    image=save_img,
    command=make,
    pady=20
)

padding = Label(text="        ")

# Packaging
padding.pack()
prompt.pack()
upload_btn.pack()
save_btn.pack(padx=15, pady=15)
directions1.pack()
directions2.pack()




root.mainloop()