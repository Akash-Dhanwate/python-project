from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
win = Tk()
win.state('zoomed')
win.config(bg='black')
#~~~~~~~~~~~~~~~~~~~~~~BUTTON FUNCTION~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def pd():
    if e1.get()=="" or e2.get()=="":
        messagebox.showerror("Error","All fields are required")
    else:
        con = mysql.connector.connect(host="localhost", username="root", password="root", database="mydata_1")
        my_cursor = con.cursor()
        my_cursor.execute("insert into hospital values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
            nameoftablets.get(),
            ref.get(),
            dose.get(),
            nooftablets.get(),
            issuedate.get(),
            expdate.get(),
            dailydose.get(),
            sideeffect.get(),
            nameofpatient.get(),
            dob.get(),
            patientaddress.get()
        ))
        con.commit()
        fetch_data()
        con.close()
        messagebox.showinfo("Success","Record has been inserted")
def fetch_data():
    con = mysql.connector.connect(host="localhost", username="root",password="root",database="mydata_1")
    my_cursor = con.cursor()
    my_cursor.execute('select * from hospital')
    rows = my_cursor.fetchall()
    if len(rows)!=0:
        table.delete(* table.get_children())
        for items in rows:
            table.insert('',END,values=items)
        con.commit()
    con.close()
def get_data(event=''):
    cursor_row = table.focus()
    data = table.item(cursor_row)
    row = data['values']
    nameoftablets.set(row[0])
    ref.set(row[1])
    dose.set(row[2])
    nooftablets.set(row[3])
    issuedate.set(row[4])
    expdate.set(row[5])
    dailydose.set(row[6])
    sideeffect.set(row[7])
    nameofpatient.set(row[8])
    dob.set(row[9])
    patientaddress.set(row[10])
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Prescription Data ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def pre():
    txt_frme.insert(END,'Name of Tablets:\t\t\t'+nameoftablets.get()+'\n')
    txt_frme.insert(END,'Reference No.:\t\t\t'+ref.get()+'\n')
    txt_frme.insert(END,'Dose:\t\t\t'+dose.get()+'\n')
    txt_frme.insert(END,'No.of Tablets:\t\t\t'+nooftablets.get()+'\n')
    txt_frme.insert(END,'issue date:\t\t\t'+issuedate.get()+'\n')
    txt_frme.insert(END,'exp date:\t\t\t'+expdate.get()+'\n')
    txt_frme.insert(END,'Daily dose:\t\t\t'+dailydose.get()+'\n')
    txt_frme.insert(END,'sideeffect:\t\t\t'+sideeffect.get()+'\n')
    txt_frme.insert(END,'Blood pressure:\t\t\t'+bloodpressure.get()+'\n')
    txt_frme.insert(END,'Storage Device:\t\t\t'+storage.get()+'\n')
    txt_frme.insert(END,'Medication:\t\t\t'+medication.get()+'\n')
    txt_frme.insert(END,'Patient Id:\t\t\t'+patientid.get()+'\n')
    txt_frme.insert(END,'Nam of patient:\t\t\t'+nameofpatient.get()+'\n')
    txt_frme.insert(END,'DOB:\t\t\t'+dob.get()+'\n')
    txt_frme.insert(END,'Patient Address:\t\t\t'+patientaddress.get()+'\n')
#~~~~~~~~~~~~~~~~~~~~~DElete~~~~~~~~~~~~~~
def delete():
    con = mysql.connector.connect(host="localhost", username="root", password="root", database="mydata_1")
    my_cursor = con.cursor()
    querry = ('delete from hospital where Refrence = %s')
    value = (ref.get(),)
    my_cursor.execute(querry,value)
    con.commit()
    con.close()
    fetch_data()
    messagebox.showinfo('Deleted','Patient data has been deleted')
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Clear Button ~~~~~~~~~~~~~~~~~~~~~~~~
def clear():
    nameoftablets.set('')
    ref.set('')
    dose.set('')
    nooftablets.set('')
    issuedate.set('')
    expdate.set('')
    dailydose.set('')
    sideeffect.set('')
    bloodpressure.set('')
    storage,set('')
    medication.set('')
    patientid.set('')
    nameofpatient.set('')
    dob.set('')
    patientaddress.set('')
    txt_frme.delete(1.0,END)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Exit Button~~~~~~~~~~~~~~~~~~~~~~~~~
def exit():
    confirm = messagebox.askyesno('confirmation','Are You Sure you Want To Exit')
    if confirm>0:
        win.destroy()
        return
#Heading
Label(win,text='Hospital Management System',font='impack 31 bold',bg='blue',fg='white').pack(fill=X)
#frame1
frame1 = Frame(win,bd=15,relief=RIDGE)
frame1.place(x=0,y=54,wid=1580,height=310)
#Label Frame for Patient Info.
Lf1 = LabelFrame(frame1,text='Patient Information',font='ariel 15 bold',bd=10,bg='pink')
Lf1.place(x=10,y=0,width=750,height=280)
#Labels For Patient Information
Label(Lf1,text='Name of Tablets',bg='pink').place(x=5,y=10)
Label(Lf1,text='Reference No.',bg='pink').place(x=5,y=40)
Label(Lf1,text='Dose',bg='pink').place(x=5,y=70)
Label(Lf1,text='No.of Tablets',bg='pink').place(x=5,y=100)
Label(Lf1,text='Issue Date',bg='pink').place(x=5,y=130)
Label(Lf1,text='Exp. Date',bg='pink').place(x=5,y=160)
Label(Lf1,text='Daily Dose',bg='pink').place(x=5,y=190)
Label(Lf1,text='Side Effect',bg='pink').place(x=5,y=220)
Label(Lf1,text='Blood Pressure',bg='pink').place(x=370,y=10)
Label(Lf1,text='Storage Device',bg='pink').place(x=370,y=40)
Label(Lf1,text='Medication',bg='pink').place(x=370,y=70)
Label(Lf1,text='Patient id',bg='pink').place(x=370,y=100)
Label(Lf1,text='Name of Patient',bg='pink').place(x=370,y=130)
Label(Lf1,text='DOB',bg='pink').place(x=370,y=160)
Label(Lf1,text='Patient Address',bg='pink').place(x=370,y=190)
#Textvariable for Every Entry Field
nameoftablets = StringVar()
ref = StringVar()
dose = StringVar()
nooftablets = StringVar()
issuedate = StringVar()
expdate = StringVar()
dailydose = StringVar()
sideeffect = StringVar()
bloodpressure = StringVar()
storage = StringVar()
medication = StringVar()
patientid = StringVar()
nameofpatient = StringVar()
dob = StringVar()
patientaddress = StringVar()
#Entry Field for all Lables
e1 = Entry(Lf1,bd=4,textvariable=nameoftablets)
e1.place(x=130,y=10,width=200)
e2 = Entry(Lf1,bd=4,textvariable=ref)
e2.place(x=130,y=40,width=200)
e3 = Entry(Lf1,bd=4,textvariable=dose)
e3.place(x=130,y=70,width=200)
e4 = Entry(Lf1,bd=4,textvariable=nooftablets)
e4.place(x=130,y=100,width=200)
e5 = Entry(Lf1,bd=4,textvariable=issuedate)
e5.place(x=130,y=130,width=200)
e6 = Entry(Lf1,bd=4,textvariable=expdate)
e6.place(x=130,y=160,width=200)
e7 = Entry(Lf1,bd=4,textvariable=dailydose)
e7.place(x=130,y=190,width=200)
e8 = Entry(Lf1,bd=4,textvariable=sideeffect)
e8.place(x=130,y=220,width=200)
e9 = Entry(Lf1,bd=4,textvariable=bloodpressure)
e9.place(x=500,y=10,width=200)
e10 = Entry(Lf1,bd=4,textvariable=storage)
e10.place(x=500,y=40,width=200)
e11 = Entry(Lf1,bd=4,textvariable=medication)
e11.place(x=500,y=70,width=200)
e12 = Entry(Lf1,bd=4,textvariable=patientid)
e12.place(x=500,y=100,width=200)
e13 = Entry(Lf1,bd=4,textvariable=nameofpatient)
e13.place(x=500,y=130,width=200)
e14= Entry(Lf1,bd=4,textvariable=dob)
e14.place(x=500,y=160,width=200)
e15 = Entry(Lf1,bd=4,textvariable=patientaddress)
e15.place(x=500,y=190,width=200)
#Label Frame For Prescription 
Lf2 = LabelFrame(frame1,text='Prescription',font='ariel 15 bold',bd=10)
Lf2.place(x=770,y=0,width=750,height=280)
#Textbox for Prescription
txt_frme = Text(Lf2,font='impact 10 bold',width=60,height=30,bg='yellow')
txt_frme.pack(fill=BOTH)
#frame2
frame2 = Frame(win,bd=15,relief=RIDGE)
frame2.place(x=0,y=360,wid=1580,height=450)
#Button
#Delete Button
d_btn = Button(win,text='Delete',font='ariel 15 bold',bg='brown',fg='white',bd=6,cursor='hand2',command=delete)
d_btn.place(x=10,y=600,wid=300)
#prescription Button
p_btn= Button(win,text='prescription',font='ariel 15 bold',bg='purple',fg='white',bd=6,cursor='hand2',command=pre)
p_btn.place(x=270,y=600,wid=450)
#Save Prescription Data
d_btn = Button(win,text='Save Prescription Data',font='ariel 15 bold',bg='green',fg='white',bd=6,cursor='hand2',command=pd)
d_btn.place(x=700,y=600,wid=370)
#Clear Button
c_btn = Button(win,text='Clear',font='ariel 15 bold',bg='blue',fg='white',bd=6,cursor='hand2',command=clear)
c_btn.place(x=1050,y=600,wid=300)
#Exit Button
e_btn = Button(win,text='Exit',font='ariel 15 bold',bg='red',fg='white',bd=6,cursor='hand2',command=exit)
e_btn.place(x=1350,y=600,wid=170)
#Scroll Bar for prescription data
scroll_x = ttk.Scrollbar(frame2,orient=HORIZONTAL)
scroll_x.pack(side='bottom',fill='x')
scroll_y = ttk.Scrollbar(frame2,orient=VERTICAL)
scroll_y.pack(side='right',fill='y')
table = ttk.Treeview(frame2,columns=('not','ref','dose','nots','issd','expd','dd','sd','pn','dob','pa'),xscrollcommand=scroll_y.set,yscrollcommand=scroll_x.set)
scroll_x = ttk.Scrollbar(command=table.xview)
scroll_y = ttk.Scrollbar(command=table.yview)
table.heading
#Heading for Prescription Data
table.heading('not',text='Name of Tablets')
table.heading('ref',text='Reference No.')
table.heading('dose',text='Dose')
table.heading('nots',text='Name of Tablets') 
table.heading('issd',text='Issue Date')
table.heading('expd',text='Exp.date')
table.heading('dd',text='Daily Dose')
table.heading('sd',text='Side Effect')
table.heading('pn',text='Patient Name')
table.heading('dob',text='DOB')
table.heading('pa',text='Patient Address')
table['show'] = 'headings' 
table.pack(fill=BOTH,expand=1)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
table.column('not',width=100)
table.column('ref',width=100)
table.column('dose',width=100)
table.column('nots',width=100)
table.column('issd',width=100)
table.column('expd',width=100)
table.column('dd',width=100)
table.column('pn',width=100)
table.column('dob',width=100)
table.column('pa',width=100)
table.bind('<ButtonRelease-1>',get_data)
fetch_data()
mainloop() 


