import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import decimal
from decimal import Decimal

class FileClassification:
    def __init__(self, filename, classification, probabilitySpam):
        self.filename = filename
        self.classification = classification
        self.probabilitySpam = probabilitySpam

#program global variables
bgcolor1 = "#C9E4DE"

alnumstring = "012356789abcdefghiljklmnopqrstuvwxyz"

k = 0
threshold = Decimal(0.50)

spamfolderpath = ""
hamfolderpath = ""
classifyfolderpath = ""

spamDict = {}
spamSize = 0
spamNumWords = 0
spamCount = 0

hamDict = {}
hamSize = 0
hamNumWords = 0
hamCount = 0

mergedCount = 0

classificationArray = []

#functions
def disableResize(event):
    if spamTable.identify_region(event.x, event.y) == "separator" or hamTable.identify_region(event.x, event.y) == "separator" or outputTable.identify_region(event.x, event.y) == "separator":
        return "break"

def openSpamFolder():
    global spamSize, spamfolderpath, spamDict, spamNumWords, spamCount, mergedCount
    bag = {}
    words = []
    spamfolderpath = filedialog.askdirectory()
    if spamfolderpath:
        #reset variables
        spamDict = {}
        spamSize = 0
        spamNumWords = 0
        spamCount = 0
        for filename in os.listdir(spamfolderpath):
            if filename:
                spamCount += 1
                file_path = os.path.join(spamfolderpath, filename)
                f = open(file_path, 'r', encoding='latin-1')
                lines = f.read()
                #tokenize
                words = lines.replace("\n", " ").split(" ")

                # print(words)
                f.close()
                
                for word in words:
                    #clean
                    cleanword = "".join(c.lower() for c in word if c.isalpha() or c.isnumeric())
                    #count
                    if cleanword != "":
                        if bag.get(cleanword) == None:
                            bag[cleanword] = 1
                        else:
                            bag[cleanword] = bag[cleanword] + 1

                #dictionary size
                spamSize = len(bag)
                #total number of words
                tnum = 0 
                for w in bag.keys():
                    tnum = tnum + bag[w]
                    
                spamNumWords = tnum

                #sort dictionary
                spamDict = dict(sorted(bag.items()))

                merged_dict = {**spamDict, **hamDict}
                mergedCount = len(merged_dict)
        #update UI
        spamTable.delete(*spamTable.get_children())
        for word, freq in spamDict.items():
            spamTable.insert("", "end", values=(word, freq))
        spamTableLabel.config(text="Total words in Spam: {}".format(spamNumWords))
        dictionarySizeLabel.config(text="Dictionary Size: {}".format(mergedCount))
        totalWordsLabel.config(text="Total words: {}".format(spamNumWords+hamNumWords))
        
        printValues()
                                
def openHamFolder():
    global hamSize, hamfolderpath, hamDict, hamNumWords, hamCount, mergedCount
    bag = {}
    words = []
    hamfolderpath = filedialog.askdirectory()
    if hamfolderpath:
        #reset variables
        hamDict = {}
        hamSize = 0
        hamNumWords = 0
        hamCount = 0
        for filename in os.listdir(hamfolderpath):
            if filename:
                hamCount += 1
                file_path = os.path.join(hamfolderpath, filename)
                f = open(file_path, 'r', encoding='latin-1')
                lines = f.read()
                #tokenize
                words = lines.replace("\n", " ").split(" ")

                # print(words)
                f.close()
                
                for word in words:
                    #clean
                    cleanword = "".join(c.lower() for c in word if c.isalpha() or c.isnumeric())
                    #count
                    if cleanword != "":
                        if bag.get(cleanword) == None:
                            bag[cleanword] = 1
                        else:
                            bag[cleanword] = bag[cleanword] + 1

                #dictionary size
                hamSize = len(bag)
                #total number of words
                tnum = 0 
                for w in bag.keys():
                    tnum = tnum + bag[w]
                    
                hamNumWords = tnum

                #sort dictionary
                hamDict = dict(sorted(bag.items()))

                merged_dict = {**spamDict, **hamDict}
                mergedCount = len(merged_dict)
        #update UI
        hamTable.delete(*hamTable.get_children())
        for word, freq in hamDict.items():
            hamTable.insert("", "end", values=(word, freq))
        hamTableLabel.config(text="Total words in Ham: {}".format(hamNumWords))
        dictionarySizeLabel.config(text="Dictionary Size: {}".format(mergedCount))
        totalWordsLabel.config(text="Total words: {}".format(spamNumWords+hamNumWords))
        
        printValues()

def openClassifyFolder():
    global classifyfolderpath
    classifyfolderpath = filedialog.askdirectory()
    if classifyfolderpath:
        openedClassifyFolderLabel.config(text="Folder to Classify: {}".format(classifyfolderpath))

def filterbuttonClick():
    global k, spamfolderpath, hamfolderpath, classifyfolderpath, classificationArray

    tempk = kEntry.get()
    #validate
    if not is_integer(tempk):
        popupDialog("Error", "Not an Integer!")
        return -1
    if int(tempk) < 0:
        popupDialog("Error", "k cannot be a negative number")
        return -1
    if not spamfolderpath:
        popupDialog("Error", "No choosen Spam Folder")
        return -1
    if not hamfolderpath:
        popupDialog("Error", "No choosen Ham Folder")
        return -1
    if not classifyfolderpath:
        popupDialog("Error", "No choosen Classify Folder")
        return -1

    k = int(tempk)
    classificationArray.clear()
    #Laplace Smoothing
    #Step 1
    p_spam = Decimal((spamCount + k) / ((spamCount+hamCount) + (2*k)))  #P(Spam)
    p_ham = Decimal(1 - p_spam)                                        #P(Ham)
    print("{} {}".format(p_spam,p_ham)) 

    #per message
    for filename in os.listdir(classifyfolderpath):
        if filename:
            file_path = os.path.join(classifyfolderpath, filename)
            f = open(file_path, 'r', encoding='latin-1')
            lines = f.read()
            #tokenize
            words = lines.replace("\n", " ").split(" ")

            message = []
            newwords = []

            for word in words:
                #clean
                cleanword = "".join(c.lower() for c in word if c.isalpha() or c.isnumeric())
                if cleanword != "":
                    message.append(cleanword)
                    if spamDict.get(word) == None and hamDict == None and cleanword not in newwords:
                        newwords.append(cleanword)
            
            
            #Step 2
            p_message_spam = Decimal(1.0)
            for word in message:
                p_message_spam *= Decimal((spamDict.get(word,0) + k) / (spamNumWords + k * (len(newwords) + mergedCount)))

            print(p_message_spam)

            p_message_ham = Decimal(1.0)
            for word in message:
                p_message_ham *= Decimal((hamDict.get(word,0) + k) / (hamNumWords + k * (len(newwords) + mergedCount)))
                
            print(p_message_ham)

            #Step 3
            p_message = Decimal((p_message_spam*p_spam) + (p_message_ham*p_ham))

            print(p_message)

            p_spam_message = Decimal((p_message_spam*p_spam)/(p_message))

            print(p_spam_message)

            #classify
            if p_spam_message > threshold: #SPAM
                newFile = FileClassification(filename, "SPAM", p_spam_message)
                classificationArray.append(newFile)
            else: #HAM
                newFile = FileClassification(filename, "HAM", p_spam_message)
                classificationArray.append(newFile)

    #classify.out
    outputFile = open("classify.out", "w", encoding="latin-1")
    for x in classificationArray:
        outputFile.write("{} {} {} \n".format(x.filename, x.classification, x.probabilitySpam))
        #update UI
        outputTable.insert("", "end", values=(x.filename, x.classification, x.probabilitySpam))

    outputFile.write("\nHAM\n")
    outputFile.write("Dictionary Size: {}\n".format(hamSize))
    outputFile.write("Total Number of Words: {}\n".format(hamNumWords))

    outputFile.write("\nSPAM\n")
    outputFile.write("Dictionary Size: {}\n".format(spamSize))
    outputFile.write("Total Number of Words: {}\n".format(spamNumWords))


    outputFile.close()
    # printValues()

def popupDialog(title,text):
    # Create a Toplevel window as the dialog
    dialog = tk.Toplevel(root)
    dialog.title(title)

    dialog.resizable(0, 0)

    # Add content to the dialog
    label = tk.Label(dialog, text=text)
    label.pack(padx=10, pady=10)

    # Add a button to close the dialog
    close_button = tk.Button(dialog, text="Close", command=dialog.destroy)
    close_button.pack(pady=10)

def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def printValues():
    print("k: {}".format(k))
    print("Spam Dictionary Size: {}, Spam Total Number of words: {}, Spam File Count: {}".format(spamSize, spamNumWords, spamCount))
    # print("Spam Dictionary: {} ".format(spamDict))
    print("Ham Dictionary Size: {}, Ham Total Number of words: {}, Ham File Count: {} ".format(hamSize, hamNumWords, hamCount))
    # print("Ham Dictionary: {} ".format(hamDict))

#create window
root = tk.Tk()
root.title("Spam Filtering")
root.geometry('1300x700')
root.minsize(1000,500)

spamFrame = tk.Frame(root, width=100, height=300, bg=bgcolor1)
hamFrame = tk.Frame(root, width=100, height=300, bg=bgcolor1)
classifyFrame = tk.Frame(root, width=200, height=300, bg=bgcolor1)

spamFrame.pack(side="left", fill="both", expand=True)
hamFrame.pack(side="left", fill="both", expand=True)
classifyFrame.pack(side="left", fill="both", expand=True)

#Spam Frame
openSpamfolderbutton = tk.Button(spamFrame, text="Select Spam Folder", command=openSpamFolder)
openSpamfolderbutton.pack(side=tk.TOP, pady=5)

spamTableFrame = tk.Frame(spamFrame,bg=bgcolor1)

spamTable = ttk.Treeview(spamTableFrame, columns=("word", "frequency"), show='headings')
spamTable.heading("word", text="Word")
spamTable.heading("frequency", text="Frequency")
spamTable.column("word", width=150, anchor="center") 
spamTable.column("frequency", width=30, anchor="center") 

spamvsb = ttk.Scrollbar(spamTableFrame, orient="vertical", command=spamTable.yview)
spamTable.configure(yscrollcommand=spamvsb.set)
spamvsb.pack(side="right", fill="y")

spamTable.pack(side="top", fill=tk.BOTH, expand=True)
spamTableFrame.pack(side=tk.TOP, padx=10, pady=5,fill=tk.BOTH, expand=True)

spamTableLabel = tk.Label(
        spamFrame, 
        text="Total words in Spam: ",
        fg="BLACK", bg=bgcolor1,
        font=('Arial',10,'bold')
        )
spamTableLabel.pack(side="top")

#Ham Frame
openHamfolderbutton = tk.Button(hamFrame, text="Select Ham Folder", command=openHamFolder)
openHamfolderbutton.pack(side=tk.TOP, pady=5)

hamTableFrame = tk.Frame(hamFrame,bg=bgcolor1)

hamTable = ttk.Treeview(hamTableFrame, columns=("word", "frequency"), show='headings')
hamTable.heading("word", text="Word")
hamTable.heading("frequency", text="Frequency")
hamTable.column("word", width=150, anchor="center") 
hamTable.column("frequency", width=30, anchor="center") 

hamvsb = ttk.Scrollbar(hamTableFrame, orient="vertical", command=hamTable.yview)
hamTable.configure(yscrollcommand=hamvsb.set)
hamvsb.pack(side="right", fill="y")

hamTable.pack(side="top", fill=tk.BOTH, expand=True)
hamTableFrame.pack(side=tk.TOP, padx=10, pady=5,fill=tk.BOTH, expand=True)

hamTableLabel = tk.Label(
        hamFrame, 
        text="Total words in Ham: ",
        fg="BLACK", bg=bgcolor1,
        font=('Arial',10,'bold')
        )
hamTableLabel.pack(side="top")

#Classify Frame
wordCountFrame = tk.Frame(classifyFrame, height=100, bg=bgcolor1)
dictionarySizeLabel = tk.Label(
        wordCountFrame, 
        text="Dictionary Size: ",
        fg="BLACK", bg=bgcolor1,
        font=('Arial',10,'bold')
        )
dictionarySizeLabel.pack(side=tk.LEFT)

totalWordsLabel = tk.Label(
        wordCountFrame, 
        text="Total words: ",
        fg="BLACK", bg=bgcolor1,
        font=('Arial',10,'bold')
        )
totalWordsLabel.pack(side=tk.LEFT, padx=5, pady=15, fill=tk.X, expand=True)
wordCountFrame.pack(side=tk.TOP, padx=5, pady=5)

openClassifyfolderbutton = tk.Button(classifyFrame, text="Select Classify Folder", command=openClassifyFolder)
openClassifyfolderbutton.pack(side=tk.TOP, pady=5)
openedClassifyFolderLabel = tk.Label(
        classifyFrame, 
        text="Folder to Classify: None",
        fg="BLACK", bg=bgcolor1,
        font=('Arial',10,'bold'),
        wraplength=400
        )
openedClassifyFolderLabel.pack(side=tk.TOP, pady=5)


kfilterFrame = tk.Frame(classifyFrame, height=100, bg=bgcolor1)
kLabel = tk.Label(
        kfilterFrame, 
        text="k",
        fg="BLACK", bg=bgcolor1,
        font=('Arial',10,'bold')
        )
kLabel.pack(side=tk.LEFT, padx=5, pady=5)

kEntry = tk.Entry(kfilterFrame)
kEntry.pack(side=tk.LEFT, padx=5, pady=5)

filterButton = tk.Button(kfilterFrame, text="Filter", command=filterbuttonClick)
filterButton.pack(side=tk.LEFT, padx=5, pady=5)

kfilterFrame.pack(side=tk.TOP, padx=5, pady=5)

outputLabel = tk.Label(
        classifyFrame, 
        text="Output",
        fg="BLACK", bg=bgcolor1,
        font=('Arial',10,'bold')
        )
outputLabel.pack(side=tk.TOP, padx=5, pady=5)

outputTableFrame = tk.Frame(classifyFrame,bg=bgcolor1)

outputTable = ttk.Treeview(outputTableFrame, columns=("filename","class","probability"), show='headings')
outputTable.heading("filename", text="Filename")
outputTable.heading("class", text="Class")
outputTable.heading("probability", text="P(spam)")
outputTable.column("filename", width=100, anchor="center") 
outputTable.column("class", width=50, anchor="center") 
outputTable.column("probability", width=150, anchor="center") 

outputvsb = ttk.Scrollbar(outputTableFrame, orient="vertical", command=outputTable.yview)
outputTable.configure(yscrollcommand=outputvsb.set)
outputvsb.pack(side="right", fill="y")

outputTable.pack(side="top", fill=tk.BOTH, expand=True)
outputTableFrame.pack(side=tk.TOP, padx=10, pady=10,fill=tk.BOTH, expand=True)

#disable resize of tables
spamTable.bind('<Button-1>', disableResize)
hamTable.bind('<Button-1>', disableResize)
outputTable.bind('<Button-1>', disableResize)
root.mainloop()