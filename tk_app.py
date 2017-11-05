"""
tk application - clients, contracts, invoices ...
"""
# pylint: disable=too-many-lines
import os
from subprocess import call
from datetime import datetime as dt
from datetime import timedelta as td

import tkinter
from tkinter import messagebox

import api
import lib
import tk_applets
import tk_expenses
import tk_forms

# todo: fix unittests

REMINDERS_DAYS_BACK = 90


def format_timecard_period_string(timecard_dict):
    """returns period string of timecard dictionary for printing"""

    return 'From %s To %s' % (
        dt.strptime(timecard_dict['period_start'], api.DATE_ISO_FORMAT).strftime(
            tk_forms.DATE_OUTPUT_READABLE_FORMAT),
        dt.strptime(timecard_dict['period_end'], api.DATE_ISO_FORMAT).strftime(
            tk_forms.DATE_OUTPUT_READABLE_FORMAT))


def generate_pdf(timecard_dict):
    """Generate Invoice PDF for timecard posted to invoice"""

    with open('templates/latex/invoice.tex', 'r') as latex_tmpl:
        data = latex_tmpl.read(). \
            replace('James Smith', ''). \
            replace('Generic Corporation', timecard_dict['contract']['client']['name']). \
            replace('street1', timecard_dict['contract']['client']['street1']). \
            replace('street2',
                    timecard_dict['contract']['client']['street2']
                    if timecard_dict['contract']['client']['street2'] else ''). \
            replace('\\today', dt.strptime(timecard_dict['date'], api.DATE_ISO_FORMAT).strftime(
            # pylint: disable=bad-continuation
            tk_forms.DATE_OUTPUT_READABLE_FORMAT)). \
            replace('\\number', str(timecard_dict['id'])). \
            replace('\\billing-period', format_timecard_period_string(timecard_dict)). \
            replace('\\message', timecard_dict['message']). \
            replace('\\terms', '%s days' % timecard_dict['terms']). \
            replace('Consulting Services1', timecard_dict['contract']['title']). \
            replace('Consulting Services2', format_timecard_period_string(timecard_dict)). \
            replace('city, state zip', '%s, %s %s' % (
                timecard_dict['contract']['client']['city'],
                timecard_dict['contract']['client']['state'],
                timecard_dict['contract']['client']['zip']))
        if timecard_dict['notes'] is not None:
            nout = ''
            for line in timecard_dict['notes'].split('\n'):
                nout += '\\tab %s\n \\\\' % line
            data = data.replace('\\notes', nout)
        else:
            data = data.replace('\\notes', '')
        items_out = ''
        for i in timecard_dict['invoice_items']:
            items_out += '\\hourrow{%s}{%s}{%s}\n' % (i['description'], i['quantity'], i['amount'])
        data = data.replace('\\hourrow{October 4, 2012}{6.5}{12}\n', items_out)
        ltxo_fname = 'templates/latex/invoice_%s.tex' % timecard_dict['id']
        with open(ltxo_fname, 'w') as latex_out:
            latex_out.write(data)
        cpwd = os.getcwd()  # make invoice.cls local to pdf compile
        os.chdir('templates/latex')
        call(["pdflatex", 'invoice_%s.tex' % timecard_dict['id']])
        os.chdir(cpwd)


class AppletReceiveCheck(object):
    # pylint: disable=too-many-instance-attributes
    """Displays selected client's open invoices for applying to a received check written
    with child applet AppletWriteCheck"""

    def __init__(self, parent, client_dict):
        """"""

        self.parent = parent
        self.write_checkapp = None
        self.client = client_dict
        self.root = tkinter.Tk()
        self.root.iconify()
        self.root.title('Invoices For Payment')
        self.root.geometry('500x%s' % 600)
        button_frame = tkinter.Frame(self.root)
        button_frame.pack(side='top')
        tkinter.Button(
            button_frame,
            text="Calculate credit to apply to check",
            name="calculate-credit-button",
            command=self.select_invoice_button_callback,
            padx=7, pady=2
        ).pack(side='left')
        tkinter.Button(
            button_frame,
            text="Cancel",
            name="cancel-button",
            command=self.cancel_btn,
            padx=7, pady=2
        ).pack(side='left')
        scrollbar = tkinter.Scrollbar(self.root)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.listbox = tkinter.Listbox(
            self.root,
            width=400,
            selectmode=tkinter.EXTENDED,
            yscrollcommand=scrollbar.set
        )
        self.listbox.pack(side='top')
        scrollbar.config(command=self.listbox.yview)

    def cancel_btn(self):
        """Exit to Client App"""

        self.root.iconify()
        self.parent.root.deiconify()

    def fill_client_open_invoice_box(self):
        """"""

        self.listbox.delete(0, tkinter.END)
        for i in lib.open_client_invoices(self.client['id']):
            self.listbox.insert(tkinter.END, api.formatted_list_invoice_line(i))

    def select_invoice_button_callback(self):
        """"""

        if self.write_checkapp is None:
            self.write_checkapp = AppletWriteCheck(
                self, self.listbox.curselection(),
                self.fill_client_open_invoice_box, client_id=self.client['id'])
        self.write_checkapp.initialize(client_id=self.client['id'])
        self.root.iconify()
        self.write_checkapp.root.deiconify()

    def setclient(self, client):
        """"""
        self.client = client
        self.fill_client_open_invoice_box()


class AppletWriteCheck(object):
    # pylint: disable=too-many-instance-attributes
    """"""

    def __init__(self, parent, listbox_selection, fill_client_open_invoice_box, client_id):
        # pylint: disable=too-many-locals
        """"""

        self.parent = parent
        self.fill_client_open_invoice_box = fill_client_open_invoice_box
        self.fill_client_open_invoice_box()
        self.selected_invoice_dicts = []
        self.root = tkinter.Toplevel()
        self.root.iconify()
        self.root.title("Create Client Payment")
        self.check_obj = api.Check(client_id=client_id)
        self.check_date = tkinter.StringVar(
            self.root, value=dt.now().strftime(api.DATE_INPUT_FORMAT))
        self.notes_entry = tkinter.Text(self.root, height=5, width=80)
        self.check_number = tkinter.StringVar(self.root, value='')
        self.msgvar = tkinter.StringVar(
            self.root, value='Total - %.2f' % self.total(listbox_selection))
        tkinter.Label(self.root, textvariable=self.msgvar).grid(row=0, column=0)
        tkinter.Label(self.root, text='Check Number').grid(row=1, column=0)
        tkinter.Entry(self.root, textvariable=self.check_number).grid(row=1, column=1)
        tkinter.Label(self.root, text='Notes').grid(row=2, column=0)
        tkinter.Entry(self.root, textvariable=self.notes_entry).grid(row=2, column=1)
        tkinter.Label(self.root, text='Date').grid(row=3, column=0)
        tkinter.Entry(self.root, textvariable=self.check_date).grid(row=3, column=1)
        invoice_numbers = [None for _ in self.selected_invoice_dicts]
        invoice_amounts = [None for _ in self.selected_invoice_dicts]
        self.invoice_amount_entries = [None for _ in self.selected_invoice_dicts]
        tkinter.Label(self.root, text='Invoice Number').grid(row=4, column=0)
        tkinter.Label(self.root, text='Credit').grid(row=4, column=2)
        for indx, _ in enumerate(self.selected_invoice_dicts):
            invoice_numbers[indx] = tkinter.Label(
                self.root, text=self.selected_invoice_dicts[indx]['id'])
            invoice_numbers[indx].grid(row=indx + 5, column=0)
            invoice_amounts[indx] = tkinter.StringVar(
                self.root,
                value=self.selected_invoice_dicts[indx]['balance']
            )
            self.invoice_amount_entries[indx] = tkinter.Entry(
                self.root, textvariable=invoice_amounts[indx]
            )
            self.invoice_amount_entries[indx].grid(row=indx + 5, column=2)
        tkinter.Button(
            self.root,
            text="save",
            name="save-client-check-button",
            command=self.save_btn,
            padx=7, pady=2
        ).grid(row=5 + len(self.selected_invoice_dicts), column=0)
        tkinter.Button(
            self.root,
            text="recalculate",
            name="recalculate-client-check-button",
            command=self.recalculate_button_callback,
            padx=7, pady=2
        ).grid(row=5 + len(self.selected_invoice_dicts), column=1)
        tkinter.Button(
            self.root,
            text="cancel",
            name="cancel-client-check-button",
            command=self.cancel_btn,
            padx=7, pady=2
        ).grid(row=5 + len(self.selected_invoice_dicts), column=2)
        print('Total credit to apply %s' % self.total(listbox_selection))

    def cancel_btn(self):
        """"""

        self.root.iconify()
        self.parent.root.deiconify()

    def initialize(self, client_id):
        """Initialize AR Client check input form"""

        self.check_obj = api.Check(client_id=client_id)
        self.check_date.set(dt.now().strftime(api.DATE_INPUT_FORMAT))
        self.notes_entry.delete(1.0, tkinter.END)
        self.check_number.set('')

    def recalculate_button_callback(self):
        """"""

        total = 0.0
        for i in self.invoice_amount_entries:
            total += float(i.get())
        self.msgvar.set('Total - %.2f' % total)

    def save_btn(self):
        """"""

        total = 0.0
        for _, amount_entry in enumerate(self.invoice_amount_entries):
            total += float(amount_entry.get())
        payments = [{'invoice_id':
                         self.selected_invoice_dicts[index]['id'], 'amount': amount_entry.get()} for
                    index, amount_entry in enumerate(self.invoice_amount_entries)]
        payload = {
            'check': {
                'id': 0,
                'date': dt.strptime(
                    self.check_date.get(), api.DATE_INPUT_FORMAT).strftime(api.DATE_ISO_FORMAT),
                'notes': self.notes_entry.get('1.0', 'end-1c'),
                'number': self.check_number.get(),
                'client_id': self.check_obj.client_id,
            },
            'payments': payments,
        }
        lib.save_client_check(payload)
        self.fill_client_open_invoice_box()
        self.root.iconify()
        self.parent.parent.root.deiconify()

    def total(self, listbox_selection):
        """Calculate sum of selected invoices"""

        open_invoices = lib.open_client_invoices(self.check_obj.client_id)
        total = 0
        for sel in listbox_selection:
            self.selected_invoice_dicts.append(open_invoices[sel])
            total += open_invoices[sel]['balance']
        return total


class ApplicationClient(object):  # pylint: disable=too-many-instance-attributes
    """"""
    # pylint: disable=too-many-locals

    def __init__(self, parent, states):
        """"""

        self.parent = parent
        self.states = states
        self.edit_app = None
        self.create_app = None
        self.check_app = None
        self.dicts = []
        self.root = tkinter.Tk()
        self.root.iconify()
        self.root.geometry('535x%s' % 600)
        self.messagebox = messagebox
        search_frame = tkinter.Frame(self.root)
        search_frame.pack(side='top')
        search_label = tkinter.Label(search_frame, text='Search')
        search_label.pack(side='left')
        self.querystring = tkinter.StringVar(search_frame)
        querystring_entry = tkinter.Entry(
            search_frame,
            textvariable=self.querystring,
            width=120
        )
        querystring_entry.pack(side='left')
        self.edit_app = None
        self.create_app = None
        self.select_msg = "Error", "Please select a vendor."
        self.receive_check_app = None
        self.root.title('Clients')
        button_frame = tkinter.Frame(self.root)
        button_frame.pack(side='top')
        select_client_button = tkinter.Button(
            button_frame,
            text="Select Client Check is From",
            name="select-client-button",
            command=self.receive_check_btn,
            padx=7, pady=2
        )
        select_client_button.pack(side='left')
        add_button = tkinter.Button(
            button_frame,
            text="Add",
            name="add-button",
            command=self.add_btn,
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
            self.create_app = tk_applets.AppletCreateClient(self, self.states)
        self.create_app.initialize()
        self.root.iconify()
        self.create_app.root.deiconify()

    def delete_btn(self):
        """Delete client selected from list box"""

        if self.listbox.curselection() != ():
            result = messagebox.askquestion("Delete", "Are You Sure?", icon='warning')
            if result == 'yes':
                lib.delete_client(self.dicts[self.listbox.curselection()[0]]['id'])
                if self.querystring.get():
                    self.search()
                else:
                    self.load()
            else:
                print("Delete canceled.")
        else:
            self.messagebox.showinfo(
                "Warning",
                "Please select a client.",
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
                self.edit_app = tk_applets.AppletEditClient(self, self.states)
            self.edit_app.set_edit_form(self.dicts[self.listbox.curselection()[0]])
            self.edit_app.root.deiconify()
            self.root.iconify()
        else:
            self.messagebox.showinfo(
                "Warning",
                "Please select a client.",
                icon='warning'
            )

    def load(self):
        """"""

        self.dicts = lib.list_page_clients()
        self.listbox.delete(0, tkinter.END)
        for diction in self.dicts:
            self.listbox.insert(tkinter.END, api.formatted_list_client_line(diction))

    def receive_check_btn(self):
        """"""

        if self.listbox.curselection() != ():
            if self.check_app is None:
                self.check_app = AppletReceiveCheck(
                    self, self.dicts[self.listbox.curselection()[0]])
            else:
                self.check_app.setclient(self.dicts[self.listbox.curselection()[0]])
            self.check_app.fill_client_open_invoice_box()
            self.check_app.root.deiconify()
            self.root.iconify()
        else:
            self.messagebox.showinfo(
                "Warning",
                "Please select a client.",
                icon='warning'
            )

    def search(self):
        """"""

        if self.querystring.get():
            self.dicts = lib.search_clients(self.querystring.get())
            self.listbox.delete(0, tkinter.END)
            for diction in self.dicts:
                self.listbox.insert(tkinter.END, api.formatted_list_client_line(diction))
        else:
            self.listbox.delete(0, tkinter.END)

    def search_btn(self):
        """"""

        self.search()


class ApplicationReminder(object):
    """"""

    def __init__(self, parent):
        """"""
        self.parent = parent
        self.root = tkinter.Tk()
        self.root.iconify()
        self.root.title('Reminders')
        self.root.geometry('900x%s' % 600)
        button_frame1 = tkinter.Frame(self.root)
        button_frame1.pack(side='top')
        skip_timecard_button = tkinter.Button(
            button_frame1,
            text="Reminders To Timecard",
            name="reminders-to-timecard-button",
            command=self.reminders_to_timecards_btn,
            padx=7, pady=2
        )
        skip_timecard_button.pack(side='left')
        reminders_to_timecard_button = tkinter.Button(
            button_frame1,
            text="Skip Timecard",
            name="skip-timecard-button",
            command=self.skip_timecard_btn,
            padx=7, pady=2
        )
        reminders_to_timecard_button.pack(side='left')
        home_button = tkinter.Button(
            button_frame1,
            text="Home",
            name="home-button",
            command=self.home_btn,
            padx=7, pady=2
        )
        home_button.pack(side='left')
        timecards_button = tkinter.Button(
            button_frame1,
            text="Timecards",
            name="timecards-button",
            command=self.timecards_btn,
            padx=7, pady=2
        )
        timecards_button.pack(side='left')
        quit_button = tkinter.Button(
            button_frame1,
            text="Quit",
            name="quit-button",
            command=quit,
            padx=7, pady=2
        )
        quit_button.pack(side='left')
        tkinter.Label(
            button_frame1,
            text="""Choose a pay period:""",
            justify=tkinter.LEFT,
            padx=20
        ).pack(side='top')
        button_frame2 = tkinter.Frame(self.root)
        button_frame2.pack(side='top')
        self.period = tkinter.IntVar()
        week_radio_btn = tkinter.Radiobutton(
            button_frame2,
            text="Weekly",
            variable=self.period,
            value=1,
            indicatoron=0,
            command=lambda *args: self.period_selected(1)
        )
        week_radio_btn.pack(side='left')
        biweek_radio_btn = tkinter.Radiobutton(
            button_frame2,
            text="Bi Week",
            variable=self.period,
            value=2,
            indicatoron=0,
            command=lambda *args: self.period_selected(2)
        )
        biweek_radio_btn.pack(side='left')
        semimonth_radio_btn = tkinter.Radiobutton(
            button_frame2,
            text="Semi Month",
            variable=self.period,
            value=3,
            indicatoron=0,
            command=lambda *args: self.period_selected(3)
        )
        semimonth_radio_btn.pack(side='left')
        month_radio_btn = tkinter.Radiobutton(
            button_frame2,
            text="Month",
            variable=self.period,
            value=4,
            indicatoron=0,
            command=lambda *args: self.period_selected(4)
        )
        month_radio_btn.pack(side='left')
        scrollbar = tkinter.Scrollbar(self.root)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.listbox = tkinter.Listbox(
            self.root,
            height=12,
            width=400,
            selectmode=tkinter.SINGLE,
            yscrollcommand=scrollbar.set
        )
        self.listbox.pack(side='top')
        scrollbar.config(command=self.listbox.yview)

    def home_btn(self):
        """"""

        self.parent.root.deiconify()
        self.root.iconify()

    def period_selected(self, selected_period_number):
        """"""

        t_set = lib.timecards_set()
        if selected_period_number == 1:
            print("Week")
            self.reminders = lib.reminders(
                dt.now() - td(days=REMINDERS_DAYS_BACK), dt.now(), t_set, 'week')
        elif selected_period_number == 2:
            print("BiWeek")
            self.reminders = lib.reminders(
                dt.now() - td(days=REMINDERS_DAYS_BACK), dt.now(), t_set, 'biweek')
        elif selected_period_number == 3:
            print("SemiMonth")
            self.reminders = lib.reminders(
                dt.now() - td(days=REMINDERS_DAYS_BACK), dt.now(), t_set,
                'semimonth')
        elif selected_period_number == 4:
            print("Month")
            self.reminders = lib.reminders(
                dt.now() - td(days=REMINDERS_DAYS_BACK), dt.now(), t_set, 'month')
        else:
            print("Error Bad Selection")
            return
        self.listbox.delete(0, tkinter.END)
        for reminder in self.reminders:
            rmdr = '%s %s %s %s' % (reminder[0].client.name, reminder[0].employee.firstname + ' ' +
                                    reminder[0].employee.lastname,
                                    dt.strftime(reminder[1], tk_forms.DATE_OUTPUT_READABLE_FORMAT),
                                    dt.strftime(reminder[2], tk_forms.DATE_OUTPUT_READABLE_FORMAT))
            self.listbox.insert(tkinter.END, rmdr)

    def reminders_to_timecards_btn(self):
        """"""

        selected_reminders = self.listbox.curselection()
        contract = self.reminders[selected_reminders[0]][0]
        start = self.reminders[selected_reminders[0]][1]
        end = self.reminders[selected_reminders[0]][2]
        lib.create_invoice_for_period(contract, start, end)
        self.reminders.remove(self.reminders[selected_reminders[0]])
        self.listbox.delete(selected_reminders[0])

    def skip_timecard_btn(self):
        """"""

        selected_reminders = self.listbox.curselection()
        contract = self.reminders[selected_reminders[0]][0]
        start = self.reminders[selected_reminders[0]][1]
        end = self.reminders[selected_reminders[0]][2]
        lib.skip_contract_interval(contract.id, start, end)
        self.reminders.remove(self.reminders[selected_reminders[0]])
        self.listbox.delete(selected_reminders[0])

    def timecards_btn(self):
        """"""

        self.parent.tc_app.load()
        self.parent.tc_app.root.deiconify()
        self.root.iconify()


class ApplicationTimecard(object):
    """"""

    def __init__(self, parent):
        """"""

        self.parent = parent
        self.edit_app = None
        self.timecard_dicts = None
        self.root = tkinter.Tk()
        self.root.iconify()
        self.root.title('Timecards')
        self.root.geometry('900x%s' % 600)
        button_frame = tkinter.Frame(self.root)
        button_frame.pack(side='top')
        timecards_button = tkinter.Button(
            button_frame,
            text="Refresh Timecards",
            name="refresh-timecards-button",
            command=self.load,
            padx=7, pady=2
        )
        timecards_button.pack(side='left')
        edit_invoice_button = tkinter.Button(
            button_frame,
            text="Edit Invoice",
            name="edit-invoice-button",
            command=self.edit_btn,
            padx=7, pady=2
        )
        edit_invoice_button.pack(side='left')
        post_invoice_button = tkinter.Button(
            button_frame,
            text="Post Invoice",
            name="post-invoice-button",
            command=self.post_btn,
            padx=7, pady=2
        )
        post_invoice_button.pack(side='left')
        home_invoice_button = tkinter.Button(
            button_frame,
            text="Home",
            name="home-button",
            command=self.home_btn,
            padx=7, pady=2
        )
        home_invoice_button.pack(side='left')
        reminders_button = tkinter.Button(
            button_frame,
            text="Reminders",
            name="reminders-button",
            command=self.reminders_btn,
            padx=7, pady=2
        )
        reminders_button.pack(side='left')
        quit_invoice_button = tkinter.Button(
            button_frame,
            text="Quit",
            name="quit-invoice-button",
            command=quit,
            padx=7, pady=2
        )
        quit_invoice_button.pack(side='left')
        scrollbar = tkinter.Scrollbar(self.root)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.listbox = tkinter.Listbox(
            self.root,
            height=12,
            width=400,
            selectmode=tkinter.SINGLE,
            yscrollcommand=scrollbar.set
        )
        self.listbox.pack(side='top')
        scrollbar.config(command=self.listbox.yview)

    def edit_btn(self):
        """"""

        if self.listbox.curselection() != ():
            self.edit_app = tk_applets.AppletEditTimecard(self)
            self.edit_app.set_edit_form(
                self.timecard_dicts[self.listbox.curselection()[0]])
            self.edit_app.root.deiconify()
        else:
            messagebox.showinfo("Error", "Please select a timecard.")

    def home_btn(self):
        """"""

        self.parent.root.deiconify()
        self.root.iconify()

    def load(self):
        """"""

        self.timecard_dicts = lib.list_page_timecards()
        self.listbox.delete(0, tkinter.END)
        for timecard in self.timecard_dicts:
            self.listbox.insert(
                tkinter.END, api.formatted_list_timecard_line(timecard))

    def post_btn(self):
        """fixme: put due date in invoice"""

        if self.listbox.curselection() != ():
            selected_timecard = self.timecard_dicts[self.listbox.curselection()[0]]
            generate_pdf(selected_timecard)
            print('posting %s' % selected_timecard['id'])
            lib.set_invoice_posted(selected_timecard['id'])
            self.load()
        else:
            messagebox.showinfo("Error", "Please select a completed timecard.")

    def reminders_btn(self):
        """"""

        self.root.iconify()
        self.parent.remind_app.root.deiconify()


class ApplicationVendor(object):  # pylint: disable=too-many-instance-attributes
    """"""

    def __init__(self, parent, states):
        """"""

        self.parent = parent
        self.states = states
        self.dicts = []
        self.select_msg = "Error", "Please select a vendor."
        self.edit_app = None
        self.create_app = None
        self.root = tkinter.Tk()
        self.root.iconify()
        self.root.title('Vendors Business')
        self.root.geometry('535x%s' % 600)
        self.messagebox = messagebox
        search_frame = tkinter.Frame(self.root)
        search_frame.pack(side='top')
        search_label = tkinter.Label(search_frame, text='Search')
        search_label.pack(side='left')
        self.querystring = tkinter.StringVar(search_frame)
        querystring_entry = tkinter.Entry(
            search_frame,
            textvariable=self.querystring,
            width=120
        )
        querystring_entry.pack(side='left')
        button_frame = tkinter.Frame(self.root)
        button_frame.pack(side='top')
        tkinter.Button(
            button_frame,
            text="Add",
            name="add-button",
            command=self.add_btn,
            padx=7, pady=2
        ).pack(side='left')
        tkinter.Button(
            button_frame,
            text="Delete",
            name="delete-button",
            command=self.delete_btn,
            padx=7, pady=2
        ).pack(side='left')
        tkinter.Button(
            button_frame,
            text="Edit",
            name="edit-button",
            command=self.edit_btn,
            padx=7, pady=2
        ).pack(side='left')
        tkinter.Button(
            button_frame,
            text="Home",
            name="home-button",
            command=self.home_btn,
            padx=7, pady=2
        ).pack(side='left')
        tkinter.Button(
            button_frame,
            text="Reload",
            name="reload-button",
            command=self.load,
            padx=7, pady=2
        ).pack(side='left')
        tkinter.Button(
            button_frame,
            text="Search",
            name="search-button",
            command=self.search_btn,
            padx=7, pady=2
        ).pack(side='left')
        tkinter.Button(
            button_frame,
            text="Quit",
            name="quit-button",
            command=quit,
            padx=7, pady=2
        ).pack(side='left')
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
            self.create_app = tk_applets.AppletCreateVendor(self, self.states)
        self.create_app.root.deiconify()
        self.create_app.initialize()
        self.root.iconify()

    def delete_btn(self):
        """"""

        if self.listbox.curselection() != ():
            result = messagebox.askquestion("Delete", "Are You Sure?", icon='warning')
            if result == 'yes':
                lib.delete_vendor(self.dicts[self.listbox.curselection()[0]]['id'])
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
                self.edit_app = tk_applets.AppletEditVendor(self, self.states)
            self.edit_app.set_edit_form(self.dicts[self.listbox.curselection()[0]])
            self.edit_app.root.deiconify()
            self.edit_app.root.title(
                'Edit Vendor - %s' % self.dicts[self.listbox.curselection()[0]]['name'])
            self.root.iconify()
        else:
            messagebox.showinfo("Error", "Please select a vendor.")

    def load(self):
        """"""

        self.querystring.set('')
        self.dicts = lib.list_page_vendors()
        self.listbox.delete(0, tkinter.END)
        for vendor_dict in self.dicts:
            self.listbox.insert(tkinter.END, api.formatted_list_vendor_line(vendor_dict))

    def search(self):
        """"""

        if self.querystring.get():
            self.dicts = lib.search_vendors(self.querystring.get())
            self.listbox.delete(0, tkinter.END)
            for vendor_dict in self.dicts:
                self.listbox.insert(tkinter.END, api.formatted_list_vendor_line(vendor_dict))
        else:
            self.listbox.delete(0, tkinter.END)

    def search_btn(self):
        """"""

        self.search()


class Gui(object):  # pylint: disable=too-many-instance-attributes
    """"""

    def __init__(self):
        """"""

        self.client_app = None
        self.expense_app = None
        self.remind_app = None
        self.tc_app = None
        self.v_app = None
        self.exp_cats = lib.list_dropdown_expense_categories()
        self.root = tkinter.Tk()
        self.root.title('Home Business')
        self.states = lib.get_states()
        button_frame = tkinter.Frame(self.root).pack(side='top')
        tkinter.Button(
            button_frame,
            text="Clients",
            name="clients-app-btn",
            command=self.clients_btn,
            padx=7, pady=2
        ).pack(side='left')
        tkinter.Button(
            button_frame,
            text="Expenses",
            name="expenses-app-btn",
            command=self.expenses_btn,
            padx=7, pady=2
        ).pack(side='left')
        tkinter.Button(
            button_frame,
            text="Reminders",
            name="reminds-app-btn",
            command=self.reminds_btn,
            padx=7, pady=2
        ).pack(side='left')
        tkinter.Button(
            button_frame,
            text="Timecards",
            name="timecards-app-btn",
            command=self.timecards_btn,
            padx=7, pady=2
        ).pack(side='left')
        tkinter.Button(
            button_frame,
            text="Vendors",
            name="vendors-app-btn",
            command=self.vendors_btn,
            padx=7, pady=2
        ).pack(side='left')
        tkinter.Button(
            button_frame,
            text="Quit",
            name="quit-btn",
            command=quit,
            padx=7, pady=2
        ).pack(side='left')

    def run(self):
        """"""

        self.root.mainloop()

    def clients_btn(self):
        """"""

        self.root.iconify()
        if self.client_app is None:
            self.client_app = ApplicationClient(self, self.states)
        self.client_app.root.deiconify()
        self.client_app.load()

    def expenses_btn(self):
        """"""

        self.root.iconify()
        if self.expense_app is None:
            self.expense_app = tk_expenses.ApplicationExpense(self, self.exp_cats)
        self.expense_app.root.deiconify()
        self.expense_app.load()

    def reminds_btn(self):
        """"""

        self.root.iconify()
        if self.remind_app is None:
            self.remind_app = ApplicationReminder(self)
        if self.tc_app is None:
            self.tc_app = ApplicationTimecard(self)
        self.remind_app.root.deiconify()

    def timecards_btn(self):
        """"""

        self.root.iconify()
        if self.remind_app is None:
            self.remind_app = ApplicationReminder(self)
        if self.tc_app is None:
            self.tc_app = ApplicationTimecard(self)
        self.tc_app.root.deiconify()
        self.tc_app.load()

    def vendors_btn(self):
        """"""

        self.root.iconify()
        if self.v_app is None:
            self.v_app = ApplicationVendor(self, self.states)
        self.v_app.root.deiconify()
        self.v_app.load()


APPLICATION = Gui()

if __name__ == '__main__':
    APPLICATION.run()
