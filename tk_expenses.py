from datetime import datetime as dt
from datetime import timedelta as td
import tkinter
from tkinter import messagebox

from rrg import models
from app import session
import api
import lib


class AppletCreateExpense(object):  # pylint: disable=too-many-instance-attributes
    """"""

    def __init__(self, parent, exp_cats):
        """"""

        self.parent = parent
        self.exp_cats = exp_cats
        self.expense = None
        self.root = tkinter.Toplevel()
        self.root.title('Add Expense')
        self.root.iconify()
        self.root.geometry('500x%s' % 600)
        self.vendor_obj = None
        self.msgvar = tkinter.StringVar(self.root)
        msg = tkinter.Label(self.root, textvariable=self.msgvar)
        msg.grid(row=0, column=0)
        cat_label = tkinter.Label(self.root, text='Category')
        cat_label.grid(row=1, column=0)
        self.cat = tkinter.StringVar(self.root, value='')
        exp_cats = self.exp_cats
        popup_menu = tkinter.OptionMenu(self.root, self.cat, *exp_cats.keys())
        popup_menu.grid(row=1, column=1)
        desc_label = tkinter.Label(self.root, text='Description')
        desc_label.grid(row=2, column=0)
        self.desc = tkinter.StringVar(self.root, value='')
        self.desc_entry = tkinter.Entry(self.root, textvariable=self.desc, width=80)
        self.desc_entry.grid(row=2, column=1)
        amt_label = tkinter.Label(self.root, text='Amount')
        amt_label.grid(row=3, column=0)
        self.amt = tkinter.StringVar(self.root, value='')
        self.amt_entry = tkinter.Entry(self.root, textvariable=self.amt)
        self.amt_entry.grid(row=3, column=1)
        date_label = tkinter.Label(self.root, text='Date')
        date_label.grid(row=4, column=0)
        self.date = tkinter.StringVar(self.root, value='')
        self.date_entry = tkinter.Entry(self.root, textvariable=self.date)
        self.date_entry.grid(row=4, column=1)
        self.notes_entry = tkinter.Text(self.root, height=5, width=80)
        tkinter.Label(
            self.root,
            text='Notes').grid(row=5, column=0)
        tkinter.Entry(
            self.root,
            textvariable=self.notes_entry
        ).grid(row=5, column=1)
        button_frame = tkinter.Frame(self.root)
        button_frame.grid(row=6, column=1)
        cancel_button = tkinter.Button(button_frame,
                                       text="Cancel",
                                       name="cancel-expense-button",
                                       command=self.cancel_btn,
                                       padx=7, pady=2)
        cancel_button.pack(side="left")
        save_button = tkinter.Button(
            button_frame,
            text="Save",
            name="save-expense-button",
            command=self.save_btn,
            padx=7, pady=2
        )
        save_button.pack(side="left")

    def cancel_btn(self):
        """"""

        self.root.iconify()
        self.parent.root.deiconify()

    def form_to_obj(self):
        """"""

        self.expense_obj.amount = self.amt.get()
        self.expense_obj.description = self.desc.get()
        self.expense_obj.date = self.date.get()
        self.expense_obj.category = self.cat.get()
        self.expense_obj.notes = self.notes_entry.get('1.0', tkinter.END)

    def initialize(self):
        """"""

        self.expense_obj = api.Expense(created_date=dt.now(), modified_date=dt.now())
        self.msgvar.set('Add new expense')
        self.date.set(dt.now().strftime(api.DATE_INPUT_FORMAT))
        self.desc.set('')
        self.amt.set('')
        self.cat.set('')
        # fixme: this does not clear the text entry
        self.notes_entry.delete('1.0', tkinter.END)

    def save_btn(self):
        """Save new expense"""

        self.form_to_obj()
        result = api.ExpenseSchema().load(self.expense_obj.to_dict())
        if result.errors:
            print(result.errors)
        else:
            lib.save_expense(self.expense_obj.to_dict())
            self.root.iconify()
            self.parent.root.deiconify()
            self.parent.load()


class AppletEditExpense(object):  # pylint: disable=too-many-instance-attributes
    """"""

    def __init__(self, parent, exp_cats):
        """"""

        self.parent = parent
        self.exp_cats = exp_cats
        self.expense = None
        self.root = tkinter.Toplevel()
        self.root.title('Add Expense')
        self.root.iconify()
        self.root.geometry('500x%s' % 600)
        self.vendor_obj = None
        self.msgvar = tkinter.StringVar(self.root)
        msg = tkinter.Label(self.root, textvariable=self.msgvar)
        msg.grid(row=0, column=0)
        cat_label = tkinter.Label(self.root, text='Category')
        cat_label.grid(row=1, column=0)
        self.cat = tkinter.StringVar(self.root, value='')
        exp_cats = self.exp_cats
        popup_menu = tkinter.OptionMenu(self.root, self.cat, *exp_cats.keys())
        popup_menu.grid(row=1, column=1)
        desc_label = tkinter.Label(self.root, text='Description')
        desc_label.grid(row=2, column=0)
        self.desc = tkinter.StringVar(self.root, value='')
        self.desc_entry = tkinter.Entry(self.root, textvariable=self.desc, width=80)
        self.desc_entry.grid(row=2, column=1)
        amt_label = tkinter.Label(self.root, text='Amount')
        amt_label.grid(row=3, column=0)
        self.amt = tkinter.StringVar(self.root, value='')
        self.amt_entry = tkinter.Entry(self.root, textvariable=self.amt)
        self.amt_entry.grid(row=3, column=1)
        date_label = tkinter.Label(self.root, text='Date')
        date_label.grid(row=4, column=0)
        self.date = tkinter.StringVar(self.root, value='')
        self.date_entry = tkinter.Entry(self.root, textvariable=self.date)
        self.date_entry.grid(row=4, column=1)
        self.notes_entry = tkinter.Text(self.root, height=5, width=80)
        tkinter.Label(
            self.root,
            text='Notes').grid(row=5, column=0)
        tkinter.Entry(
            self.root,
            textvariable=self.notes_entry
        ).grid(row=5, column=1)
        button_frame = tkinter.Frame(self.root)
        button_frame.grid(row=6, column=1)
        cancel_button = tkinter.Button(button_frame,
                                       text="Cancel",
                                       name="cancel-expense-button",
                                       command=self.cancel_btn,
                                       padx=7, pady=2)
        cancel_button.pack(side="left")
        save_button = tkinter.Button(
            button_frame,
            text="Save",
            name="save-expense-button",
            command=self.save_btn,
            padx=7, pady=2
        )
        save_button.pack(side="left")

    def cancel_btn(self):
        """"""

        self.root.iconify()
        self.parent.root.deiconify()

    def form_to_obj(self):
        """"""

        self.expense_obj.amount = self.amt.get()
        self.expense_obj.description = self.desc.get()
        self.expense_obj.date = self.date.get()
        self.expense_obj.category = self.cat.get()
        self.expense_obj.notes = self.notes_entry.get('1.0', 'end-1c')

    def set_edit_form(self, expense_dict):
        """"""

        self.expense_obj = api.Expense(**expense_dict)
        self.msgvar.set('%s: %s' % (self.expense_obj.id, self.expense_obj.amount))
        self.amt.set(self.expense_obj.amount)
        self.date.set(self.expense_obj.date.strftime(api.DATE_INPUT_FORMAT))
        self.cat.set(self.expense_obj.category)
        self.desc.set(self.expense_obj.description)
        self.notes_entry.delete('1.0', tkinter.END)
        self.notes_entry.insert(tkinter.END, self.expense_obj.notes if self.expense_obj.notes else '')

    def save_btn(self):
        """Save Edited Expense"""

        self.form_to_obj()
        result = api.ExpenseSchema().load(self.expense_obj.to_dict())
        if result.errors:
            print(result.errors)
        else:
            lib.save_expense(self.expense_obj.to_dict())
            self.root.iconify()
            self.parent.root.deiconify()
            self.parent.load()


class ApplicationGenerateMileage(object):
    """Runs the Mileage Generating Routine"""

    def __init__(self, parent, title='Generate Mileage'):
        """"""
        self.parent = parent
        self.root = tkinter.Tk()
        self.root.title(title)
        self.root.iconify()

    def generate(self):
        """"""
        description = 'IDC-Google 53 miles x 2 @ $.54/mile (2017)'
        contract = session.query(models.Contract).get(1664)
        employee = session.query(models.Employee).get(1479)
        mileage_cat = session.query(models.ExpenseCategory).get(2)
        startdate = dt(year=contract.startdate.year, month=contract.startdate.month,
                                day=contract.startdate.day)
        delta = dt.now() - startdate
        for i in range(delta.days + 1):
            day = startdate + td(days=i)
            if day.weekday() in range(0, 5):
                exp_count = session.query(models.Expense).filter(models.Expense.category == mileage_cat,
                                                                 models.Expense.description == description,
                                                                 models.Expense.date == day).count()
                if exp_count == 0:
                    exp = models.Expense(category=mileage_cat, description=description, amount=53 * 2 * .54, date=day,
                                         employee=employee)
                    session.add(exp)
                    session.commit()
        self.root.iconify()


class ApplicationExpense(object):  # pylint: disable=too-many-instance-attributes
    """"""

    def __init__(self, parent, exp_cats):
        """"""

        self.parent = parent
        self.edit_app = None
        self.create_app = None
        self.dicts = None
        self.exp_cats = exp_cats
        self.select_msg = "Error", "Please select an expense."
        self.root = tkinter.Tk()
        self.root.title('Expenses')
        self.generate_mileage_app = None
        self.messagebox = messagebox
        search_frame = tkinter.Frame(self.root)
        search_frame.pack(side='top')
        self.querystring = tkinter.StringVar(search_frame)
        querystring_entry = tkinter.Entry(
            search_frame,
            textvariable=self.querystring,
            width=120
        )
        querystring_entry.pack(side='left')
        button_frame = tkinter.Frame(self.root)
        button_frame.pack(side='top')
        add_button = tkinter.Button(
            button_frame,
            text="Add",
            name="add-button",
            command=self.add_btn,
            padx=7, pady=2
        )
        add_button.pack(side='left')
        add_button = tkinter.Button(
            button_frame,
            text="Generate Mileage",
            name="generate-mileage",
            command=self.generate_mileage,
            padx=7, pady=2
        )
        add_button.pack(side='left')
        delete_button = tkinter.Button(
            button_frame,
            text="Delete",
            name="delete-button",
            command=self.delete_btn,
            padx=7, pady=2
        )
        delete_button.pack(side='left')
        edit_button = tkinter.Button(
            button_frame,
            text="Edit",
            name="edit-button",
            command=self.edit_btn,
            padx=7, pady=2
        )
        edit_button.pack(side='left')
        home_button = tkinter.Button(
            button_frame,
            text="Home",
            name="home-button",
            command=self.home_btn,
            padx=7, pady=2
        )
        home_button.pack(side='left')
        reload_button = tkinter.Button(
            button_frame,
            text="Reload",
            name="reload-button",
            command=self.load,
            padx=7, pady=2
        )
        reload_button.pack(side='left')
        search_button = tkinter.Button(
            button_frame,
            text="Search",
            name="search-button",
            command=self.search_btn,
            padx=7, pady=2
        )
        search_button.pack(side='left')
        quit_button = tkinter.Button(
            button_frame,
            text="Quit",
            name="quit-button",
            command=quit,
            padx=7, pady=2
        )
        quit_button.pack(side='left')
        scrollbar = tkinter.Scrollbar(self.root)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.listbox = tkinter.Listbox(
            self.root,
            height=50,
            width=400,
            selectmode=tkinter.SINGLE,
            yscrollcommand=scrollbar.set
        )
        self.listbox.pack()
        scrollbar.config(command=self.listbox.yview)

    def add_btn(self):
        """"""

        if self.create_app is None:
            self.create_app = AppletCreateExpense(self, self.exp_cats)
        self.create_app.initialize()
        self.root.iconify()
        self.create_app.root.deiconify()

    def delete_btn(self):
        """Delete expense selected from listbox"""

        if self.listbox.curselection() != ():
            result = messagebox.askquestion("Delete", "Are You Sure?", icon='warning')
            if result == 'yes':
                print('deleting %s' % self.dicts[self.listbox.curselection()[0]]['id'])
                lib.delete_expense(self.dicts[self.listbox.curselection()[0]]['id'])
                if self.querystring.get():
                    self.search()
                else:
                    self.load()
            else:
                print("Delete canceled.")
        else:
            self.messagebox.showinfo(
                "Warning",
                "Please select somthing.",
                icon='warning'
            )

    def home_btn(self):
        """"""

        self.parent.root.deiconify()
        self.root.iconify()

    def edit_btn(self):
        """"""

        if self.listbox.curselection() != ():
            if self.edit_app is None:
                self.edit_app = AppletEditExpense(self, self.exp_cats)
            self.edit_app.set_edit_form(self.dicts[self.listbox.curselection()[0]])
            self.edit_app.root.deiconify()
            self.root.iconify()
        else:
            self.messagebox.showinfo(
                "Warning",
                "Please select an expense.",
                icon='warning'
            )

    def generate_mileage(self):
        """"""

        if self.generate_mileage_app is None:
            self.generate_mileage_app = ApplicationGenerateMileage(self, self.exp_cats)
        self.generate_mileage_app.generate()

    def load(self):
        """"""

        self.dicts = []
        self.listbox.delete(0, tkinter.END)
        for diction in lib.list_page_expenses():
            self.dicts.append(diction)
            self.listbox.insert(tkinter.END, api.formatted_list_expense_line(diction))

    def search(self):
        """"""

        if self.querystring.get():
            self.dicts = []
            self.listbox.delete(0, tkinter.END)
            for diction in lib.search_expenses(self.querystring.get()):
                self.dicts.append(diction)
                self.listbox.insert(tkinter.END, api.formatted_list_expense_line(diction))
        else:
            self.listbox.delete(0, tkinter.END)

    def search_btn(self):
        """"""

        self.search()


