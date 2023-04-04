# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 22:43:23 2023

@author: gadbi
"""

#Kalm

import MyFirstClient as MFC
from tkinter import*
from tkinter.colorchooser import askcolor
from tkinter import messagebox as boxedmessage


HOST, PORT = "localhost", "31425"
NICKNAME = "nick"
BASECOLOR = "#ca7511"

class Buttons :
    def __init__(self, menu):
        self.menu = menu
        self.frame()
        self.text()
        self.buttons()
        self.entries()
        self.packall()
        
    def frame(self):
        self.frame=Frame(self.menu.Window,bg='#41B77F')
        self.f_pseudo= Frame(self.frame,bg='#41B77F')
        self.f_host = Frame(self.frame,bg='#41B77F')
        self.f_port = Frame(self.frame,bg='#41B77F')
        self.f_liste=Frame(self.window)
        self.f_liste.pack(side=RIGHT)
        
    def text(self):
        self.Labeltitle1=Label(self.frame,text='Menu du jeu saucisse',font=("arial",30),bg='#41B77F',fg='white')
        self.Labeltitle2=Label(self.frame,text='Preparez vous à jouer, regarder les règles et choississez votre couleur',font=("arial",10),bg='#41B77F',fg='white')
        self.L_pseudo=Label(self.frame,text='choisi ton pseudo',font=("arial",19),bg='#41B77F',fg='white')
        self.L_host=Label(self.frame,text='host',font=("arial",19),bg='#41B77F',fg='white')
        self.L_port = Label(self.frame,text='port',font=("arial",19),bg='#41B77F',fg='white')
        self.enregistrer_liste_joueur(self.dico_list) 
        self.afficher_liste_joueur(self.dico_list)

    def buttons(self):
        self.B_quitter=Button(self.menu.Window,text='quitter',command=self.menu.Window.destroy,bg='#ed1111')
        self.B_couleur=Button(self.frame,text='Selectionner une couleur',command=self.menu.change_color,bg='#4065A4')
        self.B_jouer = Button(self.menu.Window,text='Connecter au server',command= self.menu.open_window,bg='#4065A4')

    def entries(self):
        self.e_pseudo=Entry(self.f_pseudo,font=("arial",20),bg='#41B77F',fg='white')
        self.e_host = Entry(self.f_host,font=("arial",20),bg='#41B77F',fg='white')
        self.e_port = Entry(self.f_port,font=("arial",20),bg='#41B77F',fg='white')
        self.e_pseudo.insert(0,NICKNAME)
        self.e_host.insert(0,HOST)
        self.e_port.insert(0,PORT)

    def packall (self):
        self.frame.pack(expand=YES)
        self.Labeltitle1.pack()
        self.B_quitter.pack(side=LEFT)
        self.Labeltitle2.pack()
        self.B_couleur.pack()
        self.L_pseudo.pack()
        self.e_pseudo.pack()
        self.f_pseudo.pack()
        self.L_host.pack()
        self.f_host.pack()
        self.e_host.pack()
        self.L_port.pack()
        self.e_port.pack()
        self.f_port.pack()
        self.B_jouer.pack(side=BOTTOM)


class Menu :
    def __init__(self):
        self.Window=Tk()
        self.Window.geometry("520x500")
        self.Window.title("menu principal du jeu")
        self.Window.config(background='#41B77F')
        self.buttons = Buttons(self)
        self.color = BASECOLOR
        self.Window.mainloop()
        
    def open_window(self):
        self.enregistrer_pseudo()
        self.enregistrer_port()
        self.enregistrer_host()
        if self.nickname != NICKNAME :
            self.client_window = MFC.ClientWindow(self.host, self.port, self.color, self.nickname)
            self.client_window.myMainLoop()
        else :
            boxedmessage.showinfo(title=None, message="please change your nickname")

    def change_color(self):
        colors=askcolor(title="Tkinter Color Chooser")
        self.Window.configure(bg=colors[1])
        self.color = colors[1]

    #enregistrer pseudo dans une variable
    def enregistrer_pseudo(self):
        self.nickname=self.buttons.e_pseudo.get()

    def enregistrer_host(self):
        self.host=self.buttons.e_host.get()
        
    def enregistrer_port(self):
        self.port=self.buttons.e_port.get()
        
    def enregistrer_liste_joueur(self,dico_list):
        self.Liste_joueur=[]
        c=0
        d=0
        for i in range(0,len(self.dico_list)):
            a=self.dico_list[i]["name"]
            b=self.dico_list[i]["score"]
            if b>c:
                self.Liste_joueur.append(a)
                self.Liste_joueur.append(b)
            elif b<=0:
                self.Liste_joueur.insert(0,a)
                self.Liste_joueur.insert(1,b)
            else:
                self.Liste_joueur.insert(d,a)
                self.Liste_joueur.insert(d+1,b)
            d=c
            c=b
        print (self.Liste_joueur)  
 
   
    def afficher_liste_joueur(self,dico_list):
        for i in range(len(self.Liste_joueur)-2,-1,-2):
            self.L_joueur=Label(self.f_liste,text=self.Liste_joueur[i]+" "+ str(self.Liste_joueur[i+1]),font=("arial",8),fg='red')
            self.L_joueur.pack(pady=i) 
    
        
      
        
        
        

menu = Menu()
