# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 22:43:23 2023

@author: gadbi
"""

#Kalm

import ClientH as MFC
from tkinter import*
from tkinter.colorchooser import askcolor
from tkinter import messagebox as boxedmessage


HOST, PORT = "localhost", "31425"
NICKNAME = "nick"
BASECOLOR = "#ca7511"

class Buttons :
    def __init__(self, menu):
        self.menu = menu
        self.dico_list=[{"name":"matteo","score":0},{"name":"killian","score":6},{"name":"adrien","score":2},{"name":"lucas","score":4}]
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
        self.f_adversaire=Frame(self.menu.Window)
        self.f_liste=Frame(self.menu.Window)
        
    def text(self):
        self.Labeltitle1=Label(self.frame,text='Menu du jeu saucisse',font=("arial",30),bg='#41B77F',fg='white')
        self.Labeltitle2=Label(self.frame,text='Preparez vous à jouer, regarder les règles et choississez votre couleur',font=("arial",10),bg='#41B77F',fg='white')
        self.L_pseudo=Label(self.frame,text='choisi ton pseudo',font=("arial",19),bg='#41B77F',fg='white')
        self.L_host=Label(self.frame,text='host',font=("arial",19),bg='#41B77F',fg='white')
        self.L_port = Label(self.frame,text='port',font=("arial",19),bg='#41B77F',fg='white')
        self.L_adversaire=Label(self.f_adversaire,text='choisi ton adversaire',font=("arial",19),bg='#41B77F',fg='white')
        self.trier_liste_score(self.dico_list) 
        self.classe_liste(self.dico_list,self.Liste_score_joueur)
        self.afficher_liste_joueur(self.dico_list)

    def buttons(self):
        self.B_quitter=Button(self.menu.Window,text='quitter',command=self.menu.Window.destroy,bg='#ed1111')
        self.B_couleur=Button(self.frame,text='Selectionner une couleur',command=self.menu.change_color,bg='#4065A4')
        self.B_jouer = Button(self.menu.Window,text='Connecter au server',command= self.menu.open_window,bg='#4065A4')

    def entries(self):
        self.e_pseudo=Entry(self.f_pseudo,font=("arial",20),bg='#41B77F',fg='white')
        self.e_host = Entry(self.f_host,font=("arial",20),bg='#41B77F',fg='white')
        self.e_port = Entry(self.f_port,font=("arial",20),bg='#41B77F',fg='white')
        self.e_adversaire = Entry(self.f_adversaire,font=("arial",20),bg='#41B77F',fg='white')
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
        self.L_adversaire.pack()
        self.e_adversaire.pack()
        self.f_adversaire.pack()
        self.B_jouer.pack(side=BOTTOM)
        self.f_liste.pack(side=RIGHT)


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
    
 
    def afficher_liste_joueur(self,dico_list):
        for i in range(len(self.Liste_joueur)-2,-1,-2):
            self.L_joueur=Label(self.f_liste,text=self.Liste_joueur[i]+" "+ str(self.Liste_joueur[i+1]),font=("arial",8),fg='red')
            self.L_joueur.pack(pady=i) 
            
    def trier_liste_score(self,dico_list):
        self.Liste_score_joueur=[]
        for i in range(0,len(self.dico_list)):
            a=self.dico_list[i]["score"]
            self.Liste_score_joueur.append(a)
        self.Liste_score_joueur.sort()
        print (self.Liste_score_joueur)
     
    def classe_liste(self,dico_list,Liste_score_joueur):
        self.Liste_joueur=[]
        for i in Liste_score_joueur:
            for j in range(0,len(self.dico_list)):
                if i==self.dico_list[j]["score"] and self.dico_list[j]["name"] not in self.Liste_joueur:
                    a=self.dico_list[j]["name"]
                    self.Liste_joueur.append(a)
                    b=self.dico_list[j]["score"]
                    self.Liste_joueur.append(b)
        print(self.Liste_joueur)
    
        
      
        
        
        

menu = Menu()
