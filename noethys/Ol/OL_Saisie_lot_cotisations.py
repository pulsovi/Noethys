#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import GestionDB
import datetime
from Utils import UTILS_Titulaires
from Utils import UTILS_Questionnaires
from Data import DATA_Civilites as Civilites
from Utils import UTILS_Infos_individus
from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


DICT_INFOS_INDIVIDUS = {}


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def GetDictInfosIndividus():
    global DICT_INFOS_INDIVIDUS
    dictInfos = {}
    db = GestionDB.DB()
    req = """SELECT IDindividu, nom, prenom, rue_resid, cp_resid, ville_resid FROM individus;"""
    db.ExecuterReq(req)
    listeDonnees = db.ResultatReq()
    db.Close()
    for IDindividu, nom, prenom, rue_resid, cp_resid, ville_resid in listeDonnees :
        dictInfos[IDindividu] = { "nom" : nom, "prenom" : prenom, "rue_resid" : rue_resid, "cp_resid" : cp_resid, "ville_resid" : ville_resid}
    DICT_INFOS_INDIVIDUS = dictInfos


def FormateStr(valeur=u""):
    try :
        if valeur == None : return u""
        elif type(valeur) == int : return str(valeur)
        elif type(valeur) == float : return str(valeur)
        else : return valeur
    except : 
        return u""


def FormateDate(dateStr):
    if dateStr == "" or dateStr == None : return ""
    date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
    text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
    return text





#-----------INDIVIDUS-----------

class TrackIndividu(object):
    def __init__(self, listview, donnees, infosIndividus):
        self.listview = listview

        self.infosIndividus = infosIndividus
        self.IDindividu = donnees["rattachements.IDindividu"]
        self.ID = self.IDindividu
        self.IDfamille = donnees["rattachements.IDfamille"]
        self.nomTitulaires = donnees["nomTitulaires"]
        self.IDcompte_payeur = donnees["IDcompte_payeur"]
        self.IDcivilite = donnees["IDcivilite"]
        self.nom = donnees["nom"]
        self.prenom = donnees["prenom"]
        self.IDnationalite = donnees["IDnationalite"]
        self.date_naiss = donnees["date_naiss"]
        self.age = donnees["age"]
        self.IDpays_naiss = donnees["IDpays_naiss"]
        self.cp_naiss = donnees["cp_naiss"]
        self.ville_naiss = donnees["ville_naiss"]
        self.adresse_auto = donnees["adresse_auto"]
        
        # Adresse auto ou manuelle
        if self.adresse_auto != None and DICT_INFOS_INDIVIDUS.has_key(self.adresse_auto) :
            self.rue_resid = DICT_INFOS_INDIVIDUS[self.adresse_auto]["rue_resid"]
            self.cp_resid = DICT_INFOS_INDIVIDUS[self.adresse_auto]["cp_resid"]
            self.ville_resid = DICT_INFOS_INDIVIDUS[self.adresse_auto]["ville_resid"]
        else:
            self.rue_resid = donnees["rue_resid"]
            self.cp_resid = donnees["cp_resid"]
            self.ville_resid = donnees["ville_resid"]
        
        self.genre = donnees["genre"]
        self.categorieCivilite = donnees["categorieCivilite"]
        self.civiliteLong = donnees["civiliteLong"]
        self.civiliteAbrege = donnees["civiliteAbrege"]

        self.numero = None
        if self.listview.dictNumeros["individu"].has_key(self.IDindividu) :
            self.numero = self.listview.dictNumeros["individu"][self.IDindividu]

        # R�cup�ration des r�ponses des questionnaires
        for dictQuestion in self.listview.LISTE_QUESTIONS :
            exec(u"self.question_%d = self.listview.GetReponse(%d, %s)" % (dictQuestion["IDquestion"], dictQuestion["IDquestion"], self.IDindividu))
            


def GetListeIndividus(listview=None, infosIndividus=None):
    # R�cup�ration des individus
    listeChamps = (
        "rattachements.IDindividu", "IDcivilite", "nom", "prenom", "num_secu", "IDnationalite",
        "date_naiss", "IDpays_naiss", "cp_naiss", "ville_naiss",
        "adresse_auto", "rue_resid", "cp_resid", "ville_resid",
        "rattachements.IDfamille", "IDcompte_payeur",
        )
    DB = GestionDB.DB()
    req = """SELECT %s
    FROM rattachements
    LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
    LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = rattachements.IDfamille
    WHERE IDcategorie IN (1, 2)
    ;""" % ",".join(listeChamps)
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close() 

    # R�cup�ration des civilit�s
    dictCivilites = Civilites.GetDictCivilites()
    
    # R�cup�ration des adresses auto
    GetDictInfosIndividus()
        
    listeListeView = []
    titulaires = UTILS_Titulaires.GetTitulaires()
    for valeurs in listeDonnees :
        dictTemp = {}
        dictTemp["IDindividu"] = valeurs[0]
        # Infos de la table Individus
        for index in range(0, len(listeChamps)) :
            nomChamp = listeChamps[index]
            dictTemp[nomChamp] = valeurs[index]
        # Infos sur la civilit�
        if dictTemp["IDcivilite"] == None or dictTemp["IDcivilite"] == "" :
            IDcivilite = 1
        else :
            IDcivilite = dictTemp["IDcivilite"]
        dictTemp["genre"] = dictCivilites[IDcivilite]["sexe"]
        dictTemp["categorieCivilite"] = dictCivilites[IDcivilite]["categorie"]
        dictTemp["civiliteLong"]  = dictCivilites[IDcivilite]["civiliteLong"]
        dictTemp["civiliteAbrege"] = dictCivilites[IDcivilite]["civiliteAbrege"] 
        dictTemp["nomImage"] = dictCivilites[IDcivilite]["nomImage"] 
        
        if dictTemp["date_naiss"] == None :
            dictTemp["age"] = None
        else:
            datenaissDD = datetime.date(year=int(dictTemp["date_naiss"][:4]), month=int(dictTemp["date_naiss"][5:7]), day=int(dictTemp["date_naiss"][8:10]))
            datedujour = datetime.date.today()
            age = (datedujour.year - datenaissDD.year) - int((datedujour.month, datedujour.day) < (datenaissDD.month, datenaissDD.day))
            dictTemp["age"] = age

        IDfamille = dictTemp["rattachements.IDfamille"]
        if IDfamille != None and titulaires.has_key(IDfamille):
            nomTitulaires = titulaires[IDfamille]["titulairesSansCivilite"]
        else:
            nomTitulaires = _(u"Aucun titulaire")
        dictTemp["nomTitulaires"] = nomTitulaires

        # Formatage sous forme de TRACK
        track = TrackIndividu(listview, dictTemp, infosIndividus)
        listeListeView.append(track)
        
    return listeListeView


#-----------FAMILLES-----------

class TrackFamille(object):
    def __init__(self, listview, donnees, infosIndividus):
        self.listview = listview

        self.infosIndividus = infosIndividus
        self.IDfamille = donnees["IDfamille"]
        self.ID = self.IDfamille
        self.IDcompte_payeur = donnees["IDcompte_payeur"]
        self.nomTitulaires = donnees["titulaires"]
        self.IDindividu = None
        self.rue = donnees["rue"]
        self.cp = donnees["cp"]
        self.ville = donnees["ville"]
        self.regime = donnees["nomRegime"]
        self.caisse = donnees["nomCaisse"]
        self.numAlloc = donnees["numAlloc"]
        
        # Ajout des adresses Emails des titulaires
        self.listeMails = donnees["listeMails"]
        if len(self.listeMails) > 0 :
            self.mail = self.listeMails[0]
        else :
            self.mail = None

        # Num�ro
        self.numero = None
        if self.listview.dictNumeros["famille"].has_key(self.IDfamille) :
            self.numero = self.listview.dictNumeros["famille"][self.IDfamille]

        # R�cup�ration des r�ponses des questionnaires
        for dictQuestion in self.listview.LISTE_QUESTIONS :
            exec(u"self.question_%d = self.listview.GetReponse(%d, %s)" % (dictQuestion["IDquestion"], dictQuestion["IDquestion"], self.IDfamille))


def GetListeFamilles(listview=None, infosIndividus=None):
    """ R�cup�ration des infos familles """
    # R�cup�ration des r�gimes et num d'alloc pour chaque famille
    DB = GestionDB.DB()
    req = """
    SELECT 
    familles.IDfamille, regimes.nom, caisses.nom, num_allocataire, comptes_payeurs.IDcompte_payeur
    FROM familles 
    LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = familles.IDfamille
    LEFT JOIN caisses ON caisses.IDcaisse = familles.IDcaisse
    LEFT JOIN regimes ON regimes.IDregime = caisses.IDregime
    ;"""

    DB.ExecuterReq(req)
    listeFamilles = DB.ResultatReq()
    DB.Close() 
    
    # Formatage des donn�es
    listeListeView = []
    titulaires = UTILS_Titulaires.GetTitulaires() 
    for IDfamille, nomRegime, nomCaisse, numAlloc, IDcompte_payeur in listeFamilles :
        dictTemp = {}
        if IDfamille != None and titulaires.has_key(IDfamille) :
            nomTitulaires = titulaires[IDfamille]["titulairesSansCivilite"]
            rue = titulaires[IDfamille]["adresse"]["rue"]
            cp = titulaires[IDfamille]["adresse"]["cp"]
            ville = titulaires[IDfamille]["adresse"]["ville"]
            listeMails = titulaires[IDfamille]["listeMails"]
        else :
            nomTitulaires = _(u"Aucun titulaire")
            rue = u""
            cp = u""
            ville = u""
            listeMails = []
        dictTemp = {
            "IDfamille" : IDfamille, "titulaires" : nomTitulaires, "nomRegime" : nomRegime, 
            "nomCaisse" : nomCaisse, "numAlloc" : numAlloc,
            "rue" : rue, "cp" : cp, "ville" : ville, "listeMails" : listeMails,
            "IDcompte_payeur" : IDcompte_payeur,
            }
    
        # Formatage sous forme de TRACK
        track = TrackFamille(listview, dictTemp, infosIndividus)
        listeListeView.append(track)
        
    return listeListeView


#-----------LISTVIEW-----------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
        self.categorie = kwds.pop("categorie", "individu")
        self.afficher_colonne_numero = False
        self.dictNumeros = {"famille" : {}, "individu" : {}}
        self.donnees = []
        # Infos organisme
        self.UtilsQuestionnaires = UTILS_Questionnaires.Questionnaires()
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

    def OnItemActivated(self, event):
        if self.afficher_colonne_numero == False :
            return

        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune ligne dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]

        # Demande le num�ro
        dlg = wx.TextEntryDialog(self, _(u"Veuillez saisir un num�ro pour la cotisation � cr�er :"), _(u"Num�ro de cotisation"))
        if track.numero != None :
            dlg.SetValue(track.numero)
        reponse = dlg.ShowModal()
        if reponse != wx.ID_OK:
            dlg.Destroy()
            return
        numero = dlg.GetValue()
        dlg.Destroy()

        # M�morise le num�ro
        self.dictNumeros[self.categorie][track.ID] = numero
        track.numero = numero
        self.RefreshObject(track)


    def InitModel(self):
        # R�cup�ration des questions
        self.LISTE_QUESTIONS = self.UtilsQuestionnaires.GetQuestions(type=self.categorie)
        
        # R�cup�ration des questionnaires
        self.DICT_QUESTIONNAIRES = self.UtilsQuestionnaires.GetReponses(type=self.categorie)

        # R�cup�ration des infos de base individus et familles
        self.infosIndividus = UTILS_Infos_individus.Informations() 
        
        # R�cup�ration des tracks
        if self.categorie == "individu" :
            self.donnees = GetListeIndividus(self, self.infosIndividus)
        else:
            self.donnees = GetListeFamilles(self, self.infosIndividus)

    def InitObjectListView(self):
        def FormateDate(dateStr):
            if dateStr == "" or dateStr == None : return ""
            date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text
        
        def FormateAge(age):
            if age == None : return ""
            return _(u"%d ans") % age
        
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                
        if self.categorie == "individu" :
            # INDIVIDUS
            liste_Colonnes = [
                ColumnDefn(u"ID", "left", 0, "IDindividu", typeDonnee="entier"),
                ColumnDefn(_(u"Nom"), 'left', 100, "nom", typeDonnee="texte"),
                ColumnDefn(_(u"Pr�nom"), "left", 100, "prenom", typeDonnee="texte"),
                ColumnDefn(_(u"Date naiss."), "left", 72, "date_naiss", typeDonnee="date", stringConverter=FormateDate),
                ColumnDefn(_(u"Age"), "left", 50, "age", typeDonnee="entier", stringConverter=FormateAge),
                ColumnDefn(_(u"Famille"), 'left', 200, "nomTitulaires", typeDonnee="texte"),
                ColumnDefn(_(u"Rue"), "left", 150, "rue_resid", typeDonnee="texte"),
                ColumnDefn(_(u"C.P."), "left", 50, "cp_resid", typeDonnee="texte"),
                ColumnDefn(_(u"Ville"), "left", 120, "ville_resid", typeDonnee="texte"),
                ]
        
        else:
            # FAMILLES
            liste_Colonnes = [
                ColumnDefn(_(u"ID"), "left", 0, "IDfamille", typeDonnee="entier"),
                ColumnDefn(_(u"Famille"), 'left', 200, "nomTitulaires", typeDonnee="texte"),
                ColumnDefn(_(u"Rue"), "left", 160, "rue", typeDonnee="texte"),
                ColumnDefn(_(u"C.P."), "left", 45, "cp", typeDonnee="texte"),
                ColumnDefn(_(u"Ville"), "left", 120, "ville", typeDonnee="texte"),
                ColumnDefn(_(u"Email"), "left", 100, "mail", typeDonnee="texte"),
                ColumnDefn(_(u"R�gime"), "left", 130, "regime", typeDonnee="texte"),
                ColumnDefn(_(u"Caisse"), "left", 130, "caisse", typeDonnee="texte"),
                ColumnDefn(_(u"Num�ro Alloc."), "left", 120, "numAlloc", typeDonnee="texte"),
                ]        

        if self.afficher_colonne_numero == True :
            liste_Colonnes.insert(1, ColumnDefn(_(u"Num�ro"), "left", 90, "numero", typeDonnee="texte"))

        # Ajout des questions des questionnaires
        for dictQuestion in self.LISTE_QUESTIONS :
            nomChamp = "question_%d" % dictQuestion["IDquestion"]
            #typeDonnee = UTILS_Infos_individus.GetTypeChamp(nomChamp)
            filtre = dictQuestion["filtre"]
            if filtre == "texte" : typeDonnee = "texte"
            elif filtre == "entier" : typeDonnee = "entier"
            elif filtre == "montant" : typeDonnee = "montant"
            elif filtre == "choix" : typeDonnee = "texte"
            elif filtre == "coche" : typeDonnee = "texte"
            elif filtre == "date" : typeDonnee = "date"
            else : typeDonnee = "texte"
            liste_Colonnes.append(ColumnDefn(dictQuestion["label"], "left", 150, "question_%d" % dictQuestion["IDquestion"], typeDonnee=typeDonnee))

        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        
        if self.categorie == "individu" :
            self.SetEmptyListMsg(_(u"Aucun individu"))
        else:
            self.SetEmptyListMsg(_(u"Aucune famille"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        if self.afficher_colonne_numero == True:
            self.SetSortColumn(self.columns[3])
        else :
            self.SetSortColumn(self.columns[2])
        self.SetObjects(self.donnees)
       
    def MAJ(self, categorie=None):
        if categorie != None :
            self.categorie = categorie
        self.InitModel()
        self.InitObjectListView()
        self.MAJlabel()

    def MAJlabel(self):
        # Affichage du label du staticbox
        label = u"%ss" % self.categorie.capitalize()
        nbreCoches = len(self.GetCheckedObjects())
        if nbreCoches == 1 :
            label += _(u" (1 s�lection)")
        elif nbreCoches > 1 :
            label += _(u" (%d s�lections)") % nbreCoches
        self.GetParent().SetLabelBox(label)

    def SetAfficherColonneNumero(self, etat=False):
        if self.afficher_colonne_numero != etat :
            self.afficher_colonne_numero = etat
            self.MAJ()

    def GetReponse(self, IDquestion=None, ID=None):
        if self.DICT_QUESTIONNAIRES.has_key(IDquestion) :
            if self.DICT_QUESTIONNAIRES[IDquestion].has_key(ID) :
                return self.DICT_QUESTIONNAIRES[IDquestion][ID]
        return u""

    def Selection(self):
        return self.GetSelectedObjects()
    
    def GetTracksCoches(self):
        return self.GetCheckedObjects()
    
    def GetInfosCoches(self):
        listeDonnees = []
        for track in self.GetTracksCoches() :
            dictTemp = track.GetDict()
            listeDonnees.append(dictTemp)
        return listeDonnees
    
    def SetIDcoches(self, listeID=[]):
        for track in self.donnees :
            if self.categorie == "individu" :
                ID = track.IDindividu
            else :
                ID = track.IDfamille
            if ID in listeID :
                self.Check(track)
                self.RefreshObject(track)

    def OnCheck(self, track):
        self.MAJlabel()
        try :
            self.GetParent().OnCheck(track)
        except :
            pass
        
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """            
        # Cr�ation du menu contextuel
        menuPop = UTILS_Adaptations.Menu()
        
        # Tout s�lectionner
        item = wx.MenuItem(menuPop, 20, _(u"Tout cocher"))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheListeTout, id=20)

        # Tout d�-s�lectionner
        item = wx.MenuItem(menuPop, 30, _(u"Tout d�cocher"))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheListeRien, id=30)
        
        menuPop.AppendSeparator()
        
        # Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aper�u avant impression"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Impression(self, mode="preview"):
        if self.donnees == None or len(self.donnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune donn�e � imprimer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des %ss") % self.categorie, intro="", total="", format="A", orientation=wx.LANDSCAPE)
        if mode == "preview" :
            prt.Preview()
        else:
            prt.Print()
        
    def Apercu(self, event):
        self.Impression("preview")

    def Imprimer(self, event):
        self.Impression("print")

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des %ss") % self.categorie)
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des %ss") % self.categorie)

    def Validation(self):
        if len(self.GetTracksCoches()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins une ligne dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        for track in self.GetTracksCoches() :
            if self.afficher_colonne_numero == True and track.numero in (None, ""):
                if self.categorie == "individu" :
                    label = u"%s, %s" % (track.nom, track.prenom)
                else :
                    label = track.nomTitulaires
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un num�ro de cotisation pour %s") % label, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        return True

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ(categorie="individu")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()