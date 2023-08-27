import datetime
from datetime import date
from kivymd.app import MDApp
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.metrics import dp
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty, NumericProperty
from kivy.core.window import Window
from kivymd.toast import toast
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.card import MDCard

# Window.size = (350, 600)

class MyCard(MDCard):
    
    sect = StringProperty()
    val = StringProperty()

class ActivityCard(MDCard):
    date = StringProperty()
    dep = NumericProperty()
    gains = NumericProperty()

class DetailScreen(MDFloatLayout):
    nom = StringProperty()
    date_creation = StringProperty()
    capital = NumericProperty()


class ToCard(FakeRectangularElevationBehavior, MDFloatLayout):
    name = StringProperty()
    date = StringProperty()
    rt_previous = NumericProperty()
    depenses = NumericProperty()
    production = NumericProperty()
    diff = NumericProperty()


class Table(MDApp):
    dialog = None
    project_count = NumericProperty()
    somme_dep = StringProperty()
    somme_gain = StringProperty()
    act_len = NumericProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_tables = None

        global contacts
        global contacts_name
        contacts = []
        contacts_name = []
        self.detail_data = None

    def on_start(self):
        self.add_datatable()
        self.initialise_all_act()
        self.projet_dep_gains_count()
        today = date.today()
        wd = date.weekday(today)
        days =["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        year = str(datetime.datetime.now().year)
        month = str(datetime.datetime.now().strftime("%b"))
        day = str(datetime.datetime.now().strftime("%d"))
        sc.get_screen("accueil").ids.current_date.text = f"{days[wd]}, {day} {month} {year} "
        # sc.get_screen("accueil").ids.current_date.text = f"{days[wd]}, {day} {month} {year}"


    def build(self):
        global sc
        sc = ScreenManager()
        
        sc.add_widget(Builder.load_file("accueil.kv"))
        sc.add_widget(Builder.load_file("main.kv"))
        sc.add_widget(Builder.load_file("update.kv"))
        sc.add_widget(Builder.load_file("add_act.kv"))
        sc.add_widget(Builder.load_file("add.kv"))
        
        sc.add_widget(Builder.load_file("detail.kv"))

        return sc

# première fonction...
    def add_datatable(self):
        import sqlite3
        vt = sqlite3.connect('database.db')
        im = vt.cursor()
        im.execute("SELECT * from projets")
        data = im.fetchall()
        self.data_tables = MDDataTable(
            size_hint=(.96, .7),
            
            use_pagination=True,
            check=True,
            column_data=[
                ("id", dp(20)),
                ("Nom", dp(50)),
                ("Date de création", dp(50)),
                ("Capital (F GNF)", dp(50)),
            ],
            row_data=[
                (
                    i[:][0],
                    i[:][1],
                    i[:][2],
                    i[:][3],
                )
                for i in data
            ],
        )

        self.data_tables.bind(on_check_press=self.on_check_press)
        sc.get_screen("page").ids.datatable.add_widget(self.data_tables)
    

    def on_check_press(self, instance_table, current_row):
        
        if current_row[0] not in contacts and current_row[1] not in contacts:
            contacts.append(current_row[0])
            contacts.append(current_row[1])
        else:
            contacts.remove(current_row[0])
            contacts.remove(current_row[1])
        
        

# second fonction
    def delete(self):
        # alert message
        if contacts:
            self.dialog=MDDialog(
                text="Êtes-vous de vouloir continuer",
                buttons=[
                    MDFlatButton(text="[color=3338FF]Non[/color]", on_release=self.close),
                    MDRectangleFlatButton(text="[color=096C7F]Oui[/color]", on_release=self.open)
                ],
            )
            self.dialog.open()
    
    def close(self, obj):
        self.dialog.dismiss()

    def open(self, obj):

        for i in contacts:
            if i:
                import sqlite3
                vt = sqlite3.connect("database.db")
                im = vt.cursor()
                im.execute(f"delete from projets where projet_id=?", (i[0]))
                im.execute(f"delete from activite where projet_id=?", (i[0]))
                vt.commit()
                sc.get_screen("page").ids.datatable.clear_widgets()
                self.add_datatable()
        
        self.dialog.dismiss()
        contacts.clear()


    def detail_screen(self):
        
        for i in contacts:
            if i:

                import sqlite3
                vt = sqlite3.connect('database.db')
                im = vt.cursor()
                                
                im.execute(f"SELECT * from projets where projet_id=?",(i[0]))
                
                data = im.fetchall()
                for j in data:
                    
                    sc.get_screen("detail").ids.detail_page.nom = j[1]
                    sc.get_screen("detail").ids.detail_page.date_creation = j[2]
                    sc.get_screen("detail").ids.detail_page.capital = j[3]

                # import sqlite3
                vt = sqlite3.connect('database.db')
                act = vt.cursor()               
                act.execute("SELECT * from activite where projet_id=?", (i[0]))
                data_act = act.fetchall()
                
                
                for e in data_act:
                    # benef = e[5] - e[4]
                    self.detail_data = ToCard(date=e[3], rt_previous=e[4], depenses=e[5], production=e[6], diff=e[7])
                    sc.get_screen("detail").ids.todo_list.add_widget(self.detail_data)
                
                sc.transition.direction = "left"
                sc.current = "detail"
            else:
                sc.current = "page"
                sc.get_screen("detail").ids.todo_list.remove_widget(self.detail_data)
                
        
        
        
    # open update.kv 1

    # def updatenewpage(self):
    #     sc.current = "upd"
    
    # open update.kv remanier
    def updatenewpage(self):
        for i in contacts:
            if i:

                import sqlite3
                vt = sqlite3.connect('database.db')
                im = vt.cursor()
                im.execute(f"SELECT * from projets where projet_id=?",(i[0]))
                data = im.fetchall()
                for j in data:
                    sc.get_screen("update").ids.nom.text = j[1]
                    sc.get_screen("update").ids.date_creation.text = j[2]
                    sc.get_screen("update").ids.capital.text = str(j[3])

                sc.transition.direction = "left"
                sc.current = "update"
        

    # open add.kv
    def addnewpage(self):
        sc.transition.direction = "left"
        sc.current = "add_projet"

    def add_act_newpage(self):
        sc.transition.direction = "left"
        sc.current = "add_activity"

    # open main.kv
    def back(self):
        
        sc.get_screen("detail").ids.todo_list.clear_widgets()
        sc.transition.direction = "right"
        sc.current = "page"
        

    def back2(self):
        
        sc.transition.direction = "right"
        sc.current = "detail"
        


    def update(self, nom, date_creation, capital):
        for i in contacts:
            if i:
                import sqlite3
                vt = sqlite3.connect('database.db')
                im = vt.cursor()
                im.execute("update projets set nom=?, date_creation=?, capital=? where projet_id=?", (nom, date_creation, capital, i[0]))
                vt.commit()
                sc.get_screen("page").ids.datatable.remove_widget(self.data_tables)
                self.add_datatable()
        
        contacts.clear()
        sc.transition.direction = "right"
        sc.current="page"

    def add(self, name, date_creation, capital):

        if name != "" and date_creation != "" and capital != "":
            import sqlite3
            vt = sqlite3.connect('database.db')
            im = vt.cursor()
            im.execute("insert into projets(nom, date_creation, capital) VALUES(?, ?, ?)", (name, date_creation, capital))
            vt.commit()
            sc.get_screen("page").ids.datatable.remove_widget(self.data_tables)
            self.add_datatable()

            contacts.clear()
            sc.transition.direction = "right"
            sc.current="page"

    def add_act(self, date, rt_previous, depenses, production):
        
        if date != "" and rt_previous != "" and depenses != "" and production != "":
            projet_id = contacts[0]
            diff = int(production) - int(depenses)
            
            import sqlite3
            vt = sqlite3.connect('database.db')
            im = vt.cursor()
            im.execute("insert into activite(projet_id, date, rt_previous, depenses, production, diff) VALUES(?, ?, ?, ?, ?, ?)", (projet_id, date, rt_previous, depenses, production, diff))
            vt.commit()
            toast(f"activitée du {date} enrégistré...")
            sc.get_screen("detail").ids.todo_list.clear_widgets()
            self.detail_screen()
            sc.transition.direction = "right"
            sc.current="detail"
    
    def date_dialog(self):
        date_dialog = MDDatePicker(min_date=datetime.date.today())
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    def on_save(self, instance, value, date_range):
        sc.get_screen("add_projet").ids.date_creation.text = str(value)
    
    def on_cancel(self, instance, value):
        pass

    def date_dialog2(self):
        date_dialog = MDDatePicker(min_date=datetime.date.today())
        date_dialog.bind(on_save=self.on_save2, on_cancel=self.on_cancel2)
        date_dialog.open()

    def on_save2(self, instance, value, date_range):
        sc.get_screen("add_activity").ids.date.text = str(value)
    
    def on_cancel2(self, instance, value):
        pass
    
    ############################################################################
    ####### ALL ACTIVITYS
    ##############################################################################

    def initialise_all_act(self):
        import sqlite3
        vt = sqlite3.connect('database.db')
        im = vt.cursor()
        im.execute("SELECT * from activite")
        data = im.fetchall()
        
        self.act_len = len(data)
        for i in data:
            all_act = ActivityCard()
            all_act.date = i[3]
            all_act.dep = i[5]
            all_act.gains = i[7]
            sc.get_screen("accueil").ids.act_list.add_widget(all_act)

    ############################################################################
    ####### Count and new page
    ############################################################################

    def projet_dep_gains_count(self):
        import sqlite3
        vt = sqlite3.connect('database.db')
        im = vt.cursor()
        im.execute("SELECT * from projets")
        data = im.fetchall()
        self.project_count = len(data)

        g = vt.cursor()
        g.execute("SELECT diff from activite")
        gain = g.fetchall()
        liste_gain = ()
        for ga in gain:
            liste_gain += ga
        self.somme_gain = str(sum(liste_gain))
        

        d = vt.cursor()
        d.execute("SELECT depenses from activite")
        dep = d.fetchall()
        liste_dep = ()
        for de in dep:
            liste_dep += de
        self.somme_dep = str(sum(liste_dep))

    def all_projectnew_page(self):
        sc.transition.direction = "left"
        sc.current = "page"

    def back_accueil(self):
        sc.get_screen("accueil").ids.act_list.clear_widgets()
        self.initialise_all_act()
        self.projet_dep_gains_count()
        sc.transition.direction = "right"
        sc.current = "accueil"

if __name__ == '__main__':
    Table().run()