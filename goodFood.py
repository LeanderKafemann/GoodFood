import bueroUtils
bü = bueroUtils.bueroUtils(packageName="GoodFood")

import os, datetime, naturalsize, sqlite3, shutil
from tkinter import *
from tkinter.filedialog import askopenfilename

py = bü.importPyautoguiCatched()
dLg = bü.dLg

BPATH = "./programdata/buero/"
HPATH = "./programdata/goodFood/"

dLg.entry("Daten initialisiert")

with open(BPATH+"username.txt", "r", encoding="utf-8") as f:
    USER = f.read()
with open(BPATH+"devid.txt", "r", encoding="utf-8") as f:
    DEVID = f.read()
dLg.entrys("USER und DEVID ausgelesen", USER, DEVID)
    
try:
    with open("./premiumpass.txt", "r", encoding="utf-8") as f:
        premiumContent = f.read()
    PREMIUM = bü.checkPREMIUM(premiumContent)
except:
    PREMIUM = False

BETA = str(bü.checkBETA(USER))
dLg.entrys(PREMIUM, BETA)

if not PREMIUM:
    py.alert("Sie benötigen PREMIUM.", "PREMIUM")
    dLg.finalsave_log()
    quit(code="NoPREMIUM")

root = Tk()
root.title("GoodFood")
    
c = Canvas(root, width=600, height=800)
c.configure(bg="light blue")
c.pack()

c.benachrichtigung = c.create_text(300, 720, text="GoodFood gestartet", font=("Verdana", "17"))

a = "food.db" in os.listdir(HPATH)

con = sqlite3.connect(HPATH+"food.db")
cur = con.cursor()

if not a:
    cur.execute("CREATE TABLE Defaultroom (name VARCHAR PRIMARY KEY, dates VARCHAR);")
    cur.execute("INSERT INTO Defaultroom (name, dates) VALUES ('Default', '1.1.2000');")
    with open(HPATH+"räume.txt", "x", encoding="utf-8") as f:
        f.write("defaultroom")
    räume = ["Defaultroom"]
    lebensmittel = [[("Default", "1.1.2000")]]
else:
    räume = [i.capitalize() for i in open(HPATH+"/räume.txt", "r", encoding="utf-8").read().split("#*#")]

    lebensmittel = []
    for i in räume:
        cur.execute("SELECT * FROM "+i+";")
        lebensmittel.append(cur.fetchall())

mengen = []; mhds = []
for i in lebensmittel:
    #print(i)
    i.remove(("Default", "1.1.2000"))
    a = []; c_ = []
    for j in range(len(i)):
        a.append(str(len(i[j][1].split("|"))))
        c_.append(i[j][1])
        i[j] = i[j][0]
    mengen.append(a)
    mhds.append(c_)

#print(lebensmittel, mengen, mhds)

def aktDat():
    d = datetime.datetime.today()
    return f"{str(d.day)}.{d.month}.{d.year}"

def getDays(test: list):
    return int(test[2])*372+int(test[1])*31-(31-int(test[0]))

def getDays_(test: str):
    return getDays(test.split("."))

def dayDiff(akt: str, test: str):
    akt_ = akt.split("."); test_ = test.split(".")
    return getDays(test_)-getDays(akt_)

def quit_():
    dLg.finalsave_log()
    saveAll()
    con.commit()
    con.close()
    quit()

def addLM():
    try:
        antwort2 = c.raumAktText
        assert antwort2 != "Noch keine Lebensmittel hier"
        idx = räume.index(antwort2)
        while True:
            if len(lebensmittel[idx]) < 5:
                antwort3 = bü.buttonLog("Welches Lebensmittel wollen Sie hinzufügen?", antwort2, buttons=lebensmittel[idx]+["Neues Lebensmittel", "Zurück"])
            else:
                antwort3 = py.prompt("Welches Lebensmittel wollen Sie hinzufügen?", antwort2, lebensmittel[idx][1])
                if antwort3 == None:
                    antwort3 = "Zurück"
            if antwort3 != "Zurück":
                if antwort3 == "Neues Lebensmittel":
                    antwort3 = py.prompt("Neues Lebensmittel eingeben:", "neues Lebensmittel")
                antwort4 = py.prompt("Mindesthaltbarkeitsdatum des Lebensmittels eingeben:\n\nAchtung: 31 Tage je Monat:", antwort2, "1.1.2000"); addA4 = "x"
                while addA4 != "":
                    if addA4 != "x":
                        antwort4 += "|"+addA4
                    addA4 = py.prompt("Mindesthaltbarkeitsdatum eines weiteren Exemplars eingeben (sonst nichts):", antwort2, "1.1.2001")
                if not antwort3 in lebensmittel[idx]:
                    lebensmittel[idx].append(antwort3)
                    mengen[idx].append(str(len(antwort4.split("|"))))
                    mhds[idx].append(antwort4)
                else:
                    mhds[idx][lebensmittel[idx].index(antwort3)] = mhds[idx][lebensmittel[idx].index(antwort3)] + "|" + antwort4
                    mengen[idx][lebensmittel[idx].index(antwort3)] = str(int(mengen[idx][lebensmittel[idx].index(antwort3)])+len(antwort4.split("|")))
                updateLM()
            else:
                raise KeyError()
    except ValueError:
        notification("Fehlerhafter Raum")
    except KeyError:
        notification("Abgebrochen")

def findLM():
    try:
        while True:
            llist = ["Zurück"]
            for j in range(len(lebensmittel)):
                for i in lebensmittel[j]:
                    if i not in llist:
                        llist.insert(0, i)
            if len(llist) < 7:
                antwort2 = bü.buttonLog("Welches Lebensmittel wollen Sie finden?", "Lebensmittel finden", buttons=llist)
            else:
                antwort2 = py.prompt("Welches Lebensmittel wollen Sie finden?", "Lebensmittel finden", llist[1])
                if antwort2 == None:
                    antwort2 = "Zurück"
            if antwort2 != "Zurück":
                isNamed = False; z = False
                for i in range(len(lebensmittel)):
                    if antwort2 in lebensmittel[i]:
                        if bü.buttonLog("Von dem Lebensmittel {} befinden sich {} Stück im Raum {}.\nDie Ablaufdaten sind {}.".format(antwort2, mengen[i][lebensmittel[i].index(antwort2)], räume[i], mhds[i][lebensmittel[i].index(antwort2)]),\
                                      "Lebensmittel gefunden", ("Zurück", "Lebensmittel entfernen")) == "Lebensmittel entfernen":
                            mng = mengen[i][lebensmittel[i].index(antwort2)]
                            isNamed = True
                            mngEntf = py.prompt("Wie viel des Lebensmittels soll entfernt werden?", "Lebensmittel entfernen", mng)
                            if mngEntf == mng:
                                mengen[i].pop(lebensmittel[i].index(antwort2))
                                lebensmittel[i].remove(antwort2)
                            else:
                                for _ in range(int(mngEntf)):
                                    mhdEntf = py.prompt("Das Lebensmittel mit welchem MHD wollen Sie entfernen?", "Lebensmittel entfernen", mhds[i][lebensmittel[i].index(antwort2)].split("|")[0])
                                    idx__ = mhds[i][lebensmittel[i].index(antwort2)].index(mhdEntf)
                                    mhds[i][lebensmittel[i].index(antwort2)] = naturalsize.replStrPassage(idx__, idx__+len(mhdEntf)-1, mhds[i][lebensmittel[i].index(antwort2)], "").lstrip("|").rstrip("|").replace("||", "|")
                                mengen[i][lebensmittel[i].index(antwort2)] = str(int(mng)-int(mngEntf))
                            updateLM()
                        else:
                            z = True
                if not isNamed and not z:
                    py.alert("Keine Exemplare des gewünschten Lebensmittels gefunden.", "Nicht vorhanden")
                updateLM()
            else:
                raise ValueError()
    except ValueError:
        notification("Abgebrochen")

def newRoum():
    antwort2 = py.prompt("Neuen Raum hinzufügen:", "neuer Raum")
    räume.append(antwort2)
    lebensmittel.append([])
    mengen.append([])
    mhds.append([])
    with open(HPATH+"räume.txt", "a", encoding="utf-8") as f:
        f.write("#*#"+antwort2.lower())
    cur.execute("CREATE TABLE "+antwort2+ "(name VARCHAR PRIMARY KEY, dates VARCHAR);")
    saveAll()
    notification("Neuen Raum hinzugefügt")

def saveAll():
    for i in räume:
        cur.execute("DROP TABLE "+i+";")
        cur.execute("CREATE TABLE "+i+" (name VARCHAR PRIMARY KEY, dates VARCHAR);")
        cur.execute("INSERT INTO "+i+" (name, dates) VALUES ('Default', '1.1.2000');")
        for j in lebensmittel[räume.index(i)]:
            cur.execute("INSERT INTO "+i+" (name, dates) VALUES ('"+j+"', '"+mhds[räume.index(i)][lebensmittel[räume.index(i)].index(j)]+"');")
    notification("Alle Daten gespeichert")

def notification(n: str):
    c.itemconfig(c.benachrichtigung, text=n)

def showRooms():
    py.alert("Räume:\n"+str(räume).rstrip("]").lstrip("[").replace(", ", "\n").replace("'", ""), "Räume")

def alterRoom():
    newRoom = ""
    count = False
    while newRoom not in räume:
        if count:
            notification("Invalide Eingabe!")
        newRoom = py.prompt("Neuen Raum wählen:", "Raum", c.raumAktText)
        count = True
    c.raumAktText = newRoom
    c.itemconfig(c.raumAkt, text=c.raumAktText)
    updateLM()
    notification("Raum geändert")

def updateLM():
    addVar = 10 if len(lebensmittel[räume.index(c.raumAktText)]) - c.scrollVar > 10 else len(lebensmittel[räume.index(c.raumAktText)]) - c.scrollVar
    if addVar < 0:
        addVar = 0
    idx = räume.index(c.raumAktText)
    showText = str([mengen[idx][c.scrollVar:c.scrollVar+addVar][i] + "*" + lebensmittel[idx][c.scrollVar:c.scrollVar+addVar][i] + " (" +\
                    mhds[idx][c.scrollVar:c.scrollVar+addVar][i].split("|")[[getDays_(l) for l in mhds[idx][c.scrollVar:c.scrollVar+addVar][i].split("|")].index(min([getDays_(k) for k in mhds[idx][c.scrollVar:c.scrollVar+addVar][i].split("|")]))] +\
                    ")" for i in range(addVar)]).lstrip("[").rstrip("]").replace(", ", "\n").replace("'", "") or "Noch keine Lebensmittel hier"
    c.itemconfig(c.lmText, text=showText)

def down():
    if c.scrollVar < (len(lebensmittel[räume.index(c.raumAktText)])-10 if c.raumAktText != "Noch kein Raum" else 0):
        c.scrollVar += 1
        updateLM()
        notification("Runtergescrollt")
    else:
        notification("Schon ganz unten")

def up():
    if c.scrollVar > 0:
        c.scrollVar -= 1
        updateLM()
        notification("Hochgescrollt")
    else:
        notification("Schon ganz oben")

def abgelaufen():
    akt = aktDat()
    for i in range(len(lebensmittel)):
        for j in range(len(lebensmittel[i])):
            c__ = []
            for k in mhds[i][j].split("|"):
                if dayDiff(akt, k) < 0:
                    c__.append(k)
            if len(c__) > 0:
                py.alert(f"Vom Lebensmittel {str(lebensmittel[i][j])} im Raum {räume[i]} sind {str(len(c__))} Exemplare abgelaufen!\n\nMHDs: {str(c__)}.", "Abgelaufen!")
    notification("Abgelaufenes geprüft")

def ablaufend():
    akt = aktDat()
    for i in range(len(lebensmittel)):
        for j in range(len(lebensmittel[i])):
            c___ = []
            for k in mhds[i][j].split("|"):
                if dayDiff(akt, k) < 31 and dayDiff(akt, k) > -1:
                    c___.append(k)
            if len(c___) > 0:
                py.alert(f"Vom Lebensmittel {str(lebensmittel[i][j])} im Raum {räume[i]} laufen {str(len(c___))} Exemplare ab!\n\nMHDs: {str(c___)}.", "Ablaufend!")
    notification("Ablaufendes geprüft")

def importNQuit():
    if bü.buttonLog("Wirklich bestehende Daten überschreiben?", "Importieren") == "Fortfahren":
        db = askopenfilename(filetypes=[("Database", "*.db")], title="Datenbank wählen")
        rooms = askopenfilename(filetypes=[("TXT-Raumdatei", "*txt")], title="Raumdatei wählen")
        os.remove(HPATH+"food.db")
        os.remove(HPATH+"räume.txt")
        shutil.move(db, HPATH+"food.db")
        shutil.move(rooms, HPATH+"räume.txt")
        notification("Erfolgreich importiert")
        py.alert("Ein Neustart ist erforderlich.")
        quit()
    else:
        notification("Abgebrochen")

c.create_text(300, 30, text="GoodFood", font=("Verdana", "30", "bold"))
c.create_text(300, 790, text="Copyright Leander Kafemann 2025  -  Version 1.0.0", font=("Verdana", "5"))

c.create_window(300, 650, window=Button(master=root, command=quit_, text="Beenden", background="light blue", relief="ridge", height=2, width=30))

c.raumAktText = "Defaultroom"
c.create_text(300, 120, text="Raum:", font=("Verdana", "10"))
c.raumAkt = c.create_text(300, 150, text=c.raumAktText, font=("Verdana", "24"), width=400)
c.lmText = c.create_text(300, 200, font=("Verdana", "15"), width=400, text="Noch keine Lebensmittel", anchor="n")
c.scrollVar = 0
c.create_window(50, 150, anchor="w", window=Button(master=root, command=showRooms, text="🛈", background="light blue", activebackground="blue", relief="ridge"), width=33)
c.create_window(550, 150, anchor="e", window=Button(master=root, command=alterRoom, text="⛭", background="light blue", activebackground="blue", relief="ridge"), width=33)

c.create_window(550, 300, window=Button(master=root, command=saveAll, text="💾", background="light blue", activebackground="green", relief="ridge"), width=33, anchor="e")
c.create_window(550, 340, window=Button(master=root, command=newRoum, text="➕", background="light blue", activebackground="blue", relief="ridge"), width=33, anchor="e")
c.create_window(50, 300, window=Button(master=root, command=findLM, text="🔍", background="light blue", activebackground="red", relief="ridge"), width=33, anchor="w")
c.create_window(50, 340, window=Button(master=root, command=addLM, text="🛒", background="light blue", activebackground="light green", relief="ridge"), width=33, anchor="w")
c.create_window(50, 380, window=Button(master=root, command=ablaufend, text="❗", background="orange", activebackground="red", relief="ridge"), width=33, anchor="w")
c.create_window(550, 380, window=Button(master=root, command=abgelaufen, text="💀", background="red", activebackground="orange", relief="ridge"), width=33, anchor="e")

c.create_window(265, 550, window=Button(master=root, command=down, text="⇓", background="light blue", activebackground="blue", relief="ridge"), width=33)
c.create_window(335, 550, window=Button(master=root, command=up, text="⇑", background="light blue", activebackground="blue", relief="ridge"), width=33)
c.create_window(300, 550, window=Button(master=root, command=importNQuit, text="🡇", background="light blue", activebackground="blue", relief="ridge"), width=33)

root.mainloop()