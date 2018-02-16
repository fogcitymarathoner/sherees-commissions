# pylint: disable=too-many-lines
""""""
from datetime import datetime as dt
import tkinter
from tkinter.scrolledtext import ScrolledText

import tabulate

import tk_applet_applets
import api
import lib
from app import session
from rrg import models


def set_edit_timecard_msg(ui_var, timecard):
    """Writes invoice summary in edit timecard app"""
    # fixme: this should be a member function

    summary = ''
    summary += '%s\n' % timecard.contract.title
    data = [{
        'Description': item.description,
        'Amount': item.amount,
        'Quantity': item.quantity,} for item in timecard.invoice_items]
    summary += tabulate.tabulate(data)
    summary += '\n%.2f' % sum(
        float(timecard.amount) * float(timecard.quantity) for timecard in timecard.invoice_items)
    ui_var.set(summary)


class AppletCreateClient(object):  # pylint: disable=too-many-instance-attributes
    """"""

    def __init__(self, parent, states):  # pylint: disable=too-many-statements
        # pylint: disable=too-many-locals
        """"""

        self.parent = parent
        self.client_obj = None
        self.root = tkinter.Toplevel()
        self.root.iconify()
        self.root.geometry('500x%s' % 600)
        self.root.title('Add Client')
        self.msgvar = tkinter.StringVar(self.root)
        self.name = tkinter.StringVar(self.root, value='')
        self.street1 = tkinter.StringVar(self.root, value='')
        self.street2 = tkinter.StringVar(self.root, value='')
        self.city = tkinter.StringVar(self.root, value='')
        self.state = tkinter.StringVar(self.root)
        self.zip = tkinter.StringVar(self.root, value='')
        self.active = tkinter.IntVar()
        self.terms = tkinter.StringVar(self.root, value='')
        tkinter.Label(self.root, textvariable=self.msgvar).grid(row=0, column=0)
        tkinter.Label(self.root, text='Name').grid(row=1, column=0)
        tkinter.Entry(self.root, textvariable=self.name).grid(row=1, column=1)
        tkinter.Label(self.root, text='Street1').grid(row=2, column=0)
        tkinter.Entry(self.root, textvariable=self.street1).grid(row=2, column=1)
        tkinter.Label(self.root, text='Street2').grid(row=3, column=0)
        tkinter.Entry(self.root, textvariable=self.street2).grid(row=3, column=1)
        tkinter.Label(self.root, text='City').grid(row=4, column=0)
        tkinter.Entry(self.root, textvariable=self.city).grid(row=4, column=1)
        popup_menu = tkinter.OptionMenu(self.root, self.state, *states.keys())
        tkinter.Label(self.root, text="Choose a models.State").grid(row=5, column=0)
        popup_menu.grid(row=5, column=1)
        tkinter.Label(self.root, text='Zip').grid(row=6, column=0)
        tkinter.Entry(self.root, textvariable=self.zip).grid(row=6, column=1)
        active_inactive_button_frame = tkinter.Frame(self.root).grid(row=7, column=0)
        tkinter.Radiobutton(
            active_inactive_button_frame,
            text="Active",
            variable=self.active,
            value=1
        ).pack(side='left')
        tkinter.Radiobutton(
            active_inactive_button_frame,
            text="Inactive",
            variable=self.active,
            value=0
        ).pack(side='left')
        tkinter.Label(self.root, text='Terms').grid(row=8, column=0)
        tkinter.Entry(self.root, textvariable=self.terms).grid(row=8, column=1)
        button_frame = tkinter.Frame(self.root)
        button_frame.grid(row=9, column=1)
        cancel_button = tkinter.Button(
            button_frame,
            text="Cancel",
            name="cancel-client-button",
            command=self.cancel_btn,
            padx=7, pady=2
        )
        cancel_button.pack(side="left")
        save_button = tkinter.Button(
            button_frame,
            text="Save",
            name="save-client-button",
            command=self.save_btn,
            padx=7, pady=2
        )
        save_button.pack(side="left")

    def cancel_btn(self):
        """"""

        self.root.iconify()
        self.parent.root.deiconify()

    def _form_to_obj(self):
        """"""

        self.client_obj.name = self.name.get()
        self.client_obj.street1 = self.street1.get()
        self.client_obj.street2 = self.street2.get()
        self.client_obj.city = self.city.get()
        self.client_obj.zip = self.zip.get()
        self.client_obj.terms = self.terms.get()
        self.client_obj.active = True if self.active.get() == 1 else False
        self.client_obj.state = self.state.get()

    def initialize(self):
        """"""

        self.client_obj = api.Client()
        self.msgvar.set('Add new client')
        self.name.set('')
        self.street1.set('')
        self.street2.set('')
        self.city.set('')
        self.state.set('California')
        self.zip.set('')
        self.active.set(1)
        self.terms.set('30')

    def save_btn(self):
        """"""

        self._form_to_obj()
        print(self.client_obj.to_dict())
        result = api.ClientSchema().load(self.client_obj.to_dict())
        if result.errors:
            print(result.errors)
        else:
            lib.save_client(self.client_obj.to_dict())
            self.root.iconify()
            self.parent.root.deiconify()
            self.parent.load()


class AppletCreateClientMemo(object):
    """"""

    def __init__(self, parent):
        """"""

        self.parent = parent
        self.memo_obj = None
        self.root = tkinter.Toplevel()
        self.root.iconify()
        self.root.title('Add Client Memo for client %s' % self.parent.parent.client_obj.name)
        self.date = tkinter.StringVar(self.root)
        tkinter.Label(self.root, text='Notes').grid(row=1, column=0)
        self.notes_entry = tkinter.Text(self.root, height=5, width=80)
        self.notes_entry.grid(row=1, column=1)
        tkinter.Label(self.root, text='Date').grid(row=2, column=0, sticky=tkinter.E)
        tkinter.Entry(self.root, textvariable=self.date).grid(row=2, column=1, sticky=tkinter.W)
        button_frame = tkinter.Frame(self.root)
        button_frame.grid(row=3, column=1)
        cancel_button = tkinter.Button(
            button_frame,
            text="Cancel",
            name="cancel-button",
            command=self.cancel_btn,
            padx=7, pady=2
        )
        cancel_button.pack(side='left')
        save_button = tkinter.Button(
            button_frame,
            text="Create",
            name="create-client-memo-button",
            command=self.save_btn,
            padx=7, pady=2
        )
        save_button.pack(side='left')
        self.initialize()

    def cancel_btn(self):
        """"""

        self.root.iconify()
        self.parent.root.deiconify()

    def form_to_obj(self):
        """"""

        self.memo_obj.set_notes(self.notes_entry.get('1.0', 'end-1c'))
        self.memo_obj.set_date(dt.strptime(
            self.date.get(),
            api.DATE_INPUT_FORMAT))

    def initialize(self):
        """"""

        self.memo_obj = api.ClientMemo(client_id=self.parent.parent.client_obj.id)
        self.notes_entry.delete('1.0', tkinter.END)
        self.date.set(dt.now().strftime(api.DATE_INPUT_FORMAT))

    def save_btn(self):
        """Save client memo"""

        self.form_to_obj()
        result = api.ClientMemoSchema().load(self.memo_obj.to_dict())
        if result.errors:
            print(result.errors)
        else:
            lib.save_client_memo(self.memo_obj.to_dict())
            self.root.iconify()
            self.parent.root.deiconify()
            self.parent.load()

class AppletCreateVendor(object):  # pylint: disable=too-many-instance-attributes
    """"""

    def __init__(self, parent, states):  # pylint: disable=too-many-locals
        # pylint: disable=too-many-statements
        """"""

        self.parent = parent
        self.vendor_obj = None
        self.root = tkinter.Toplevel()
        self.root.geometry('900x%s' % 600)
        self.root.title('Add Vendor Business')
        self.root.iconify()
        self.msgvar = tkinter.StringVar(self.root)
        self.name = tkinter.StringVar(self.root, value='')
        self.apphone1 = tkinter.StringVar(self.root, value='')
        self.apphone2 = tkinter.StringVar(self.root, value='')
        self.apfirstname = tkinter.StringVar(self.root, value='')
        self.aplastname = tkinter.StringVar(self.root, value='')
        self.accountnumber = tkinter.StringVar(self.root, value='')
        self.state = tkinter.StringVar(self.root)
        self.secretbits_entry = tkinter.Text(self.root, height=5, width=80)
        self.active = tkinter.IntVar()
        self.purpose = tkinter.StringVar(self.root, value='')
        self.street1 = tkinter.StringVar(self.root, value='')
        self.street2 = tkinter.StringVar(self.root, value='')
        self.city = tkinter.StringVar(self.root, value='')
        self.state = tkinter.StringVar(self.root)
        self.street2_entry = tkinter.Entry(self.root, textvariable=self.street2)
        self.street2_entry.grid(row=4, column=1)
        self.zip = tkinter.StringVar(self.root, value='')
        tkinter.Label(self.root, textvariable=self.msgvar).grid(row=0, column=0)
        tkinter.Label(self.root, text='Name').grid(row=1, column=0)
        tkinter.Entry(self.root, textvariable=self.name).grid(row=1, column=1)
        tkinter.Label(self.root, text='Purpose').grid(row=2, column=0)
        tkinter.Entry(self.root, textvariable=self.purpose).grid(row=2, column=1)
        tkinter.Label(self.root, text='Street1').grid(row=3, column=0)
        tkinter.Entry(self.root, textvariable=self.street1).grid(row=3, column=1)
        tkinter.Label(self.root, text='Street2').grid(row=4, column=0)
        tkinter.Label(self.root, text='City').grid(row=5, column=0)
        tkinter.Entry(self.root, textvariable=self.city).grid(row=5, column=1)
        tkinter.Label(self.root, text="Choose a state").grid(row=6, column=0)
        popup_menu = tkinter.OptionMenu(self.root, self.state, *states.keys())
        popup_menu.grid(row=6, column=1)
        tkinter.Label(self.root, text='Zip').grid(row=7, column=0)
        tkinter.Entry(self.root, textvariable=self.zip).grid(row=7, column=1)
        active_inactive_frame = tkinter.Frame(self.root)
        active_inactive_frame.grid(row=8, column=0)
        tkinter.Radiobutton(
            active_inactive_frame, text="Active", variable=self.active, value=1).pack(side='left')
        tkinter.Radiobutton(
            active_inactive_frame, text="Inactive", variable=self.active, value=0).pack(side='left')
        tkinter.Label(self.root, text='First').grid(row=9, column=0)
        tkinter.Entry(self.root, textvariable=self.apfirstname).grid(row=9, column=1)
        tkinter.Label(self.root, text='Last').grid(row=10, column=0)
        tkinter.Entry(self.root, textvariable=self.aplastname).grid(row=10, column=1)
        tkinter.Label(self.root, text='Phone1').grid(row=11, column=0)
        tkinter.Entry(self.root, textvariable=self.apphone1).grid(row=11, column=1)
        tkinter.Label(self.root, text='Phone1').grid(row=12, column=0)
        tkinter.Entry(self.root, textvariable=self.apphone2).grid(row=12, column=1)
        tkinter.Label(self.root, text='Account Number').grid(row=13, column=0)
        tkinter.Entry(self.root, textvariable=self.accountnumber, width=80).grid(row=13, column=1)
        tkinter.Label(self.root, text='Secret Bits').grid(row=14, column=0)
        tkinter.Text(self.root, height=5, width=80).grid(row=14, column=1)
        tkinter.Label(self.root, text='Notes').grid(row=15, column=0)
        self.notes_entry = tkinter.Text(self.root, height=5, width=80)
        self.notes_entry.grid(row=15, column=1)
        button_frame = tkinter.Frame(self.root)
        button_frame.grid(row=16, column=1)
        tkinter.Button(
            button_frame,
            text="Cancel",
            name="cancel-vendor-button",
            command=self.cancel_btn,
            padx=7, pady=2
        ).pack(side='left')
        tkinter.Button(
            button_frame,
            text="Save",
            name="save-vendor-button",
            command=self.save_btn,
            padx=7, pady=2
        ).pack(side='left')

    def cancel_btn(self):
        """"""
        self.root.iconify()
        self.parent.root.deiconify()

    def initialize(self):
        """"""

        self.vendor_obj = api.Vendor()
        self.msgvar.set('Add new vendor')
        self.name.set('')
        self.purpose.set('')
        self.street1.set('')
        self.street2.set('')
        self.apphone1.set('')
        self.apphone2.set('')
        self.city.set('')
        self.zip.set('')
        self.accountnumber.set('')
        self.secretbits_entry.delete('1.0', tkinter.END)
        self.secretbits_entry.insert(tkinter.END, '')
        self.notes_entry.delete('1.0', tkinter.END)
        self.notes_entry.insert(tkinter.END, '')
        self.active.set(True)
        self.state.set('California')

    def form_to_obj(self):
        """"""

        self.vendor_obj.name = self.name.get()
        self.vendor_obj.purpose = self.purpose.get()
        self.vendor_obj.street1 = self.street1.get()
        self.vendor_obj.street2 = self.street2.get()
        self.vendor_obj.apphone1 = self.apphone1.get()
        self.vendor_obj.apphone2 = self.apphone2.get()
        self.vendor_obj.apfirstname = self.apfirstname.get()
        self.vendor_obj.aplastname = self.aplastname.get()
        self.vendor_obj.city = self.city.get()
        self.vendor_obj.zip = self.zip.get()
        self.vendor_obj.accountnumber = self.accountnumber.get()
        self.vendor_obj.secretbits = self.secretbits_entry.get('1.0', 'end-1c')
        self.vendor_obj.notes = self.notes_entry.get('1.0', 'end-1c')
        self.vendor_obj.active = True if self.active.get() == 1 else False
        self.vendor_obj.state = self.state.get()

    def save_btn(self):
        """"""

        self.form_to_obj()
        result = api.VendorSchema().load(self.vendor_obj.to_dict())
        if result.errors:
            print(result.errors)
        else:
            lib.save_vendor(self.vendor_obj.to_dict())
            self.root.iconify()
            self.parent.root.deiconify()
            self.parent.load()


class AppletCreateVendorMemo(object):
    """"""

    def __init__(self, parent):
        """"""

        self.parent = parent
        self.root = tkinter.Toplevel()
        self.root.iconify()
        self.root.title(
            'Add Business Vendor Memo for vendor %s' % self.parent.parent.vendor_obj.name)
        self.date = tkinter.StringVar(self.root)
        tkinter.Label(self.root, text='Notes').grid(row=1, column=0)
        self.notes_entry = tkinter.Text(self.root, height=5, width=80)
        self.notes_entry.grid(row=1, column=1)
        date_label = tkinter.Label(self.root, text='Date')
        date_label.grid(row=2, column=0, sticky=tkinter.E)
        tkinter.Entry(
            self.root, textvariable=self.date).grid(row=2, column=1, sticky=tkinter.W)
        button_frame = tkinter.Frame(self.root)
        button_frame.grid(row=3, column=1)
        tkinter.Button(
            button_frame,
            text="Cancel",
            name="cancel-button",
            command=self.cancel_btn,
            padx=7, pady=2
        ).pack(side='left')
        tkinter.Button(
            button_frame,
            text="Create",
            name="create-vendor-memo-button",
            command=self.save_btn,
            padx=7, pady=2
        ).pack(side='left')
        self.initialize()

    def cancel_btn(self):
        """"""

        self.root.iconify()
        self.parent.root.deiconify()

    def form_to_obj(self):
        """"""

        self.memo_obj.vendor = self.parent.parent.vendor_obj
        self.memo_obj.notes = self.notes_entry.get('1.0', 'end-1c')
        self.memo_obj.date = dt.strptime(
            self.date.get(), api.DATE_INPUT_FORMAT).strftime(api.DATE_ISO_FORMAT)

    def save_btn(self):
        """"""

        self.form_to_obj()
        result = api.VendorMemoSchema().load(self.memo_obj.to_dict())
        if result.errors:
            print(result.errors)
        else:
            lib.save_vendor_memo(self.memo_obj.to_dict())
            self.root.iconify()
            self.parent.root.deiconify()
            self.parent.load()

    def initialize(self):
        """"""

        self.memo_obj = api.VendorMemo(vendor_id=self.parent.parent.vendor_obj.id)
        self.date.set(dt.now().strftime(api.DATE_INPUT_FORMAT))


class AppletEditClient():  # pylint: disable=too-many-instance-attributes
    """"""

    def __init__(self, parent, states):  # pylint: disable=too-many-statements
        # pylint: disable=too-many-locals
        """"""

        self.parent = parent
        self.root = tkinter.Toplevel()
        self.root.iconify()
        self.root.geometry('500x%s' % 600)
        self.memo_app = None
        self.root.title('Edit Client')
        self.client_obj = None
        self.msgvar = tkinter.StringVar(self.root)
        self.name = tkinter.StringVar(self.root)
        self.street1 = tkinter.StringVar(self.root, value='')
        self.street2 = tkinter.StringVar(self.root, value='')
        self.city = tkinter.StringVar(self.root, value='')
        self.state = tkinter.StringVar(self.root)
        self.zip = tkinter.StringVar(self.root, value='')
        self.active = tkinter.IntVar()
        self.terms = tkinter.StringVar(self.root, value='')
        tkinter.Label(self.root, textvariable=self.msgvar).grid(row=0, column=0)
        tkinter.Label(self.root, text='Name').grid(row=1, column=0)
        tkinter.StringVar(self.root, value='')
        tkinter.Entry(self.root, textvariable=self.name).grid(row=1, column=1)
        tkinter.Label(self.root, text='Street1').grid(row=2, column=0)
        tkinter.Entry(self.root, textvariable=self.street1).grid(row=2, column=1)
        tkinter.Label(self.root, text='Street2').grid(row=3, column=0)
        tkinter.Entry(self.root, textvariable=self.street2).grid(row=3, column=1)
        tkinter.Label(self.root, text='City').grid(row=4, column=0)
        tkinter.Entry(self.root, textvariable=self.city).grid(row=4, column=1)
        tkinter.Label(self.root, text="Choose a models.State").grid(row=5, column=0)
        popup_menu = tkinter.OptionMenu(self.root, self.state, *states.keys())
        popup_menu.grid(row=5, column=1)
        tkinter.Label(self.root, text='Zip').grid(row=6, column=0)
        tkinter.Entry(self.root, textvariable=self.zip).grid(row=6, column=1)
        active_inactive_button_frame = tkinter.Frame(self.root)
        active_inactive_button_frame.grid(row=7, column=0)
        tkinter.Radiobutton(
            active_inactive_button_frame,
            text="Active",
            variable=self.active,
            value=1
        ).pack(side='left')
        tkinter.Radiobutton(
            active_inactive_button_frame,
            text="Inactive",
            variable=self.active,
            value=0
        ).pack(side='left')
        tkinter.Label(self.root, text='Terms').grid(row=8, column=0)
        tkinter.Entry(self.root, textvariable=self.terms).grid(row=8, column=1)
        button_frame = tkinter.Frame(self.root)
        button_frame.grid(row=9, column=1)
        tkinter.Button(
            button_frame,
            text="Cancel",
            name="cancel-client-button",
            command=self.cancel_btn,
            padx=7, pady=2
        ).pack(side="left")
        tkinter.Button(
            button_frame,
            text="Memos",
            name="client-memos-button",
            command=self.memos_btn,
            padx=7, pady=2
        ).pack(side="left")
        tkinter.Button(
            button_frame,
            text="Save",
            name="save-client-button",
            command=self.save_btn,
            padx=7, pady=2
        ).pack(side="left")

    def cancel_btn(self):
        """"""

        self.root.iconify()
        self.parent.root.deiconify()

    def load_clients_listbox(self):
        """"""

        self.parent.load()

    def memos_btn(self):
        """"""

        if self.memo_app is None:
            self.memo_app = tk_applet_applets.AppletAppletClientMemo(self)
        self.memo_app.set(self.client_obj)
        self.memo_app.root.deiconify()
        self.root.iconify()

    def form_to_obj(self):
        """"""

        self.client_obj.name = self.name.get()
        self.client_obj.street1 = self.street1.get()
        self.client_obj.street2 = self.street2.get()
        self.client_obj.city = self.city.get()
        self.client_obj.zip = self.zip.get()
        self.client_obj.terms = self.terms.get()
        self.client_obj.active = True if self.active.get() == 1 else False
        self.client_obj.state = self.state.get()

    def set_edit_form(self, client_dict):
        """Set up tk client edit form"""

        self.client_obj = api.Client(**client_dict)
        self.msgvar.set(
            '%s: %s' % (
                client_dict['id'], client_dict['name']))
        self.name.set(client_dict['name'])
        self.street1.set(client_dict['street1'])
        self.street2.set(client_dict['street2'])
        self.city.set(client_dict['city'])
        self.state.set(client_dict['state'])
        self.zip.set(client_dict['zip'])
        self.active.set(client_dict['active'])
        self.terms.set(client_dict['terms'])

    def save_btn(self):
        """"""

        self.form_to_obj()

        result = api.ClientSchema().load(self.client_obj.to_dict())
        if result.errors:
            print(result.errors)
        else:
            lib.save_client(self.client_obj.to_dict())
            self.root.iconify()
            self.parent.root.deiconify()
            self.parent.load()


class AppletEditClientMemo(object):
    """"""

    def __init__(self, parent):
        """"""

        self.parent = parent
        self.root = tkinter.Toplevel()
        self.root.iconify()
        self.memo_obj = None
        self.date = tkinter.StringVar(self.root)
        notes_label = tkinter.Label(self.root, text='Notes')
        notes_label.grid(row=1, column=0)
        self.notes_entry = tkinter.Text(self.root, height=5, width=80)
        self.notes_entry.grid(row=1, column=1)
        tkinter.Label(
            self.root,
            text='Date'
        ).grid(row=2, column=0, sticky=tkinter.E)
        tkinter.Entry(
            self.root,
            textvariable=self.date
        ).grid(row=2, column=1, sticky=tkinter.W)
        button_frame = tkinter.Frame(
            self.root
        ).grid(row=3, column=1)
        tkinter.Button(
            button_frame,
            text="Cancel",
            name="cancel-button",
            command=self.cancel_btn,
            padx=7, pady=2
        ).pack(side='left')
        tkinter.Button(
            button_frame,
            text="Save",
            name="save-button",
            command=self.save_btn,
            padx=7, pady=2
        ).pack(side='left')

    def cancel_btn(self):
        """"""
        self.root.iconify()
        self.parent.root.deiconify()

    def set(self, client_memo):
        """"""

        self.memo_obj = client_memo
        self.notes_entry.delete('1.0', tkinter.END)
        self.notes_entry.insert(tkinter.INSERT, self.memo_obj.notes)
        self.date.set(self.memo_obj.date)

    def form_to_obj(self):
        """"""

        self.memo_obj.notes = self.notes_entry.get('1.0', 'end-1c')
        self.memo_obj.date = dt.strptime(self.date.get(), api.DATE_INPUT_FORMAT)

    def save_btn(self):
        """Save client memo"""

        self.form_to_obj()
        result = api.ClientMemoSchema().load(self.memo_obj.to_dict())
        if result.errors:
            print(result.errors)
        else:
            lib.save_client_memo(self.memo_obj.to_dict())
            self.root.iconify()
            self.parent.root.deiconify()
            self.parent.load()


class AppletEditTimecard(object):  # pylint: disable=too-many-instance-attributes
    """"""

    def __init__(self, parent):
        """"""

        self.parent = parent
        self.timecard_obj = None
        self.edit_amt_app = None
        self.root = tkinter.Toplevel()
        self.root.iconify()
        self.root.title('Edit Timecard')
        self.root.geometry('800x%s' % 600)
        self.msgvar = tkinter.StringVar(self.root)
        self.date = tkinter.StringVar(self.root)
        tkinter.Label(
            self.root,
            text='Description'
        ).grid(row=0, column=0)
        self.msg = tkinter.Message(
            self.root,
            textvariable=self.msgvar
        ).grid(row=0, column=1, sticky=tkinter.E)
        tkinter.Label(
            self.root,
            text='Date'
        ).grid(row=1, column=0, sticky=tkinter.E)
        tkinter.Entry(
            self.root,
            textvariable=self.date
        ).grid(row=1, column=1, sticky=tkinter.W)
        tkinter.Label(
            self.root,
            text='Notes'
        ).grid(row=2, column=0, sticky=tkinter.E)
        self.notes_entry = ScrolledText(self.root, height=10)
        self.notes_entry.grid(row=2, column=1, sticky=tkinter.W)
        tkinter.Label(
            self.root,
            text='Period Start'
        ).grid(row=3, column=0, sticky=tkinter.E)
        self.period_start = tkinter.StringVar(self.root)
        self.period_start_entry = tkinter.Entry(self.root, textvariable=self.period_start)
        self.period_start_entry.grid(row=3, column=1, sticky=tkinter.W)
        period_end_label = tkinter.Label(self.root, text='Period End')
        period_end_label.grid(row=4, column=0, sticky=tkinter.E)
        self.period_end = tkinter.StringVar(self.root)
        self.period_end_entry = tkinter.Entry(self.root, textvariable=self.period_end)
        self.period_end_entry.grid(row=4, column=1, sticky=tkinter.W)
        message_label = tkinter.Label(self.root, text='Message')
        message_label.grid(row=5, column=0, sticky=tkinter.E)
        self.message_entry = tkinter.Text(self.root, height=2)
        self.message_entry.grid(row=5, column=1, sticky=tkinter.W)
        button_frame = tkinter.Frame(self.root)
        button_frame.grid(row=6, column=1, sticky=tkinter.E)
        save_button = tkinter.Button(
            button_frame,
            text="Save",
            name="save-button",
            command=self.save_btn,
            padx=7, pady=2)
        save_button.pack(side='left')
        edit_amounts_btn = tkinter.Button(
            button_frame,
            text="Edit Amounts",
            name="edit-amounts-button",
            command=self.edit_amounts_btn_cb,
            padx=7, pady=2)
        edit_amounts_btn.pack(side='left')
        cancel_button = tkinter.Button(
            button_frame,
            text="Cancel",
            name="cancel-button",
            command=self.cancel_btn,
            padx=7, pady=2)
        cancel_button.pack(side='left')

    def cancel_btn(self):
        """"""

        self.parent.root.deiconify()
        self.root.iconify()

    def edit_amounts_btn_cb(self):
        """"""
        if self.edit_amt_app is None:
            self.edit_amt_app = AppletEditTimecardAmounts(self)
        self.root.iconify()
        self.edit_amt_app.root.deiconify()
        self.edit_amt_app.set_edit_form(self.timecard_obj)

    def form_to_obj(self):
        """Update Timecard obj from form"""

        self.timecard_obj.period_start = dt.strptime(self.period_start.get(),
                        api.DATE_INPUT_FORMAT).strftime(api.DATE_ISO_FORMAT)
        self.timecard_obj.period_end = dt.strptime(
            self.period_end.get(), api.DATE_INPUT_FORMAT).strftime(api.DATE_ISO_FORMAT)
        self.timecard_obj.date = dt.strptime(self.date.get(), api.DATE_INPUT_FORMAT).strftime(api.DATE_ISO_FORMAT)
        self.timecard_obj.message = self.message_entry.get('1.0', 'end-1c')
        self.timecard_obj.notes = self.notes_entry.get('1.0', 'end-1c')

    def save_btn(self):
        """Saves edited timecard before posting."""

        self.form_to_obj()
        print(self.timecard_obj.to_dict())
        result = api.TimecardSchema().load(self.timecard_obj.to_dict())
        if result.errors:
            print(result.errors)
        else:
            lib.save_timecard(self.timecard_obj.to_dict())
            self.root.iconify()
            self.parent.root.deiconify()
            self.parent.load()

    def set_edit_form(self, timecard_dict):
        """"""

        self.timecard_obj = api.Timecard(**timecard_dict)
        self.root.title('Edit Timecard Number %s' % self.timecard_obj.id)
        self.date.set(dt.strptime(
                self.timecard_obj.date,
                api.DATE_ISO_FORMAT).strftime(api.DATE_INPUT_FORMAT))
        self.notes_entry.delete('1.0', tkinter.END)
        self.notes_entry.insert(
            tkinter.END, self.timecard_obj.notes if self.timecard_obj.notes else '')
        self.period_start.set(
            dt.strptime(
                self.timecard_obj.period_start,
                api.DATE_ISO_FORMAT).strftime(api.DATE_INPUT_FORMAT))
        self.period_end.set(
            dt.strptime(
                self.timecard_obj.period_end, api.DATE_ISO_FORMAT).strftime(api.DATE_INPUT_FORMAT))
        self.message_entry.delete('1.0', tkinter.END)
        self.message_entry.insert(
            tkinter.END, self.timecard_obj.message if self.timecard_obj.message else '')

        self.update_summary()


    def update_summary(self):
        """"""

        set_edit_timecard_msg(self.msgvar, self.timecard_obj)


class AppletEditTimecardAmounts(object):  # pylint: disable=too-many-instance-attributes
    """"""

    def __init__(self, parent):
        """"""

        self.timecard = None
        self.parent = parent
        self.timecard_obj = None
        self.root = tkinter.Toplevel()
        self.root.iconify()
        self.root.title('Edit Timecard Amounts')
        self.root.geometry('500x%s' % 600)
        self.frames = []
        self.msgvar = tkinter.StringVar(self.root)
        msg = tkinter.Label(self.root, textvariable=self.msgvar)
        msg.pack(side='top')
        self.items = []
        self.items_amounts_vars = []
        self.items_quantities_vars = []
        self.items_amounts_entries = []
        self.items_quantities_entries = []
        button_frame = tkinter.Frame(self.root)
        button_frame.pack(side='top')
        save_button = tkinter.Button(
            button_frame,
            text="save",
            name="save-items-button",
            command=self.save_btn,
            padx=7, pady=2
        )
        save_button.pack(side='left')
        save_button = tkinter.Button(
            button_frame,
            text="cancel",
            name="cancel-items-button",
            command=self.cancel_btn,
            padx=7, pady=2
        )
        save_button.pack(side='left')

    def cancel_btn(self):
        """"""

        self.parent.root.deiconify()
        self.root.iconify()

    def form_to_obj(self):
        """Update Timecard obj from form"""

        for indx, titem in enumerate(self.timecard_obj.invoice_items):
            titem.quantity = float(self.items_quantities_vars[indx].get())
            titem.amount = float(self.items_amounts_vars[indx].get())

    def save_btn(self):
        """"""

        self.form_to_obj()
        result = api.TimecardSchema().load(self.timecard_obj.to_dict())
        for timecard_item in self.timecard_obj.invoice_items:
            result = api.InvoiceItemSchema().load(timecard_item.to_dict())

            if result.errors:
                print(result.errors)
            else:
                lib.save_timecard_item(timecard_item.to_dict())
        set_edit_timecard_msg(self.parent.msgvar, self.timecard_obj)
        self.parent.update_summary()
        self.parent.root.deiconify()
        self.root.iconify()

    def set_edit_form(self, timecard_obj):
        """"""
        for f in self.frames:
            f.destroy()
        self.timecard_obj = timecard_obj
        self.items = []
        self.items_amounts_vars = []
        self.items_quantities_vars = []
        self.items_amounts_entries = []
        self.items_quantities_entries = []
        self.items = [iitem for iitem in self.timecard_obj.invoice_items]
        self.items_amounts_vars = [
            tkinter.StringVar(self.root) for _ in self.timecard_obj.invoice_items]
        self.items_quantities_vars = [
            tkinter.StringVar(self.root) for _ in self.timecard_obj.invoice_items]
        self.frames = [tkinter.Frame(self.root) for _ in self.timecard_obj.invoice_items]
        self.items_amounts_entries = [tkinter.Entry(
            self.frames[i], textvariable=self.items_amounts_vars[i]) for i, j in
                                      enumerate(self.timecard_obj.invoice_items)]
        self.items_quantities_entries = [tkinter.Entry(
            self.frames[indx], textvariable=self.items_quantities_vars[indx])
                                         for
                                         indx, _ in
                                         enumerate(self.timecard_obj.invoice_items)]
        for indx, _ in enumerate(self.timecard_obj.invoice_items):
            self.frames[indx].pack(side='top')
            self.items_amounts_vars[indx].set(self.items[indx].amount)
            self.items_quantities_vars[indx].set(self.items[indx].quantity)
            label = tkinter.Label(self.frames[indx], text=self.items[indx].id)
            label.pack(side='left')
            label = tkinter.Label(self.frames[indx], text=self.items[indx].description)
            label.pack(side='left')
            label = tkinter.Label(self.frames[indx], text='| amount:')
            label.pack(side='left')
            self.items_amounts_entries[indx].pack(side='left')
            label = tkinter.Label(self.frames[indx], text='| quantity:')
            label.pack(side='left')
            self.items_quantities_entries[indx].pack(side='left')


class AppletEditVendor(object):  # pylint: disable=too-many-instance-attributes
    """"""

    def __init__(self, parent, states):  # pylint: disable=too-many-statements
        # pylint: disable=too-many-locals
        """"""

        self.parent = parent
        self.vendor_obj = None
        self.memo_app = None
        self.root = tkinter.Toplevel()
        self.root.title('Edit Vendor Business')
        self.root.geometry('900x%s' % 600)
        self.root.iconify()
        self.msgvar = tkinter.StringVar(self.root)
        self.name = tkinter.StringVar(self.root, value='')
        self.apphone1 = tkinter.StringVar(self.root, value='')
        self.apphone2 = tkinter.StringVar(self.root, value='')
        self.apfirstname = tkinter.StringVar(self.root, value='')
        self.aplastname = tkinter.StringVar(self.root, value='')
        self.secretbits_entry = tkinter.Text(self.root, height=5, width=80)
        self.state = tkinter.StringVar(self.root)
        self.purpose = tkinter.StringVar(self.root, value='')
        self.street1 = tkinter.StringVar(self.root, value='')
        self.street2 = tkinter.StringVar(self.root, value='')
        self.city = tkinter.StringVar(self.root, value='')
        self.zip = tkinter.StringVar(self.root, value='')
        self.active = tkinter.IntVar()
        self.accountnumber = tkinter.StringVar(self.root, value='')
        self.secretbits_entry.grid(row=14, column=1)
        tkinter.Label(self.root, textvariable=self.msgvar).grid(row=0, column=0)
        tkinter.Label(self.root, text='Name').grid(row=1, column=0)
        tkinter.Entry(self.root, textvariable=self.name).grid(row=1, column=1)
        tkinter.Label(self.root, text='Purpose').grid(row=2, column=0)
        tkinter.Entry(self.root, textvariable=self.purpose).grid(row=2, column=1)
        tkinter.Label(self.root, text='Street1').grid(row=3, column=0)
        tkinter.Entry(self.root, textvariable=self.street1).grid(row=3, column=1)
        tkinter.Label(self.root, text='Street2').grid(row=4, column=0)
        tkinter.Entry(self.root, textvariable=self.street2).grid(row=4, column=1)
        tkinter.Label(self.root, text='City').grid(row=5, column=0)
        tkinter.Entry(self.root, textvariable=self.city).grid(row=5, column=1)
        tkinter.Label(self.root, text="Choose a state").grid(row=6, column=0)
        tkinter.OptionMenu(self.root, self.state, *states.keys()).grid(row=6, column=1)
        tkinter.Label(self.root, text='Zip').grid(row=7, column=0)
        tkinter.Entry(self.root, textvariable=self.zip).grid(row=7, column=1)
        active_inactive_frame = tkinter.Frame(self.root)
        active_inactive_frame.grid(row=8, column=0)
        tkinter.Radiobutton(
            active_inactive_frame, text="Active", variable=self.active, value=1).pack(side='left')
        tkinter.Radiobutton(
            active_inactive_frame, text="Inactive", variable=self.active, value=0).pack(side='left')
        tkinter.Label(self.root, text='First').grid(row=9, column=0)
        tkinter.Entry(self.root, textvariable=self.apfirstname).grid(row=9, column=1)
        tkinter.Label(self.root, text='Last').grid(row=10, column=0)
        tkinter.Entry(self.root, textvariable=self.aplastname).grid(row=10, column=1)
        tkinter.Label(self.root, text='Phone1').grid(row=11, column=0)
        tkinter.Entry(self.root, textvariable=self.apphone1).grid(row=11, column=1)
        tkinter.Label(self.root, text='Phone1').grid(row=12, column=0)
        tkinter.Entry(self.root, textvariable=self.apphone2).grid(row=12, column=1)
        tkinter.Label(self.root, text='Account Number').grid(row=13, column=0)
        tkinter.Entry(self.root, textvariable=self.accountnumber, width=80).grid(row=13, column=1)
        tkinter.Label(self.root, text='Secret Bits').grid(row=14, column=0)
        tkinter.Label(self.root, text='Notes').grid(row=15, column=0)
        self.notes_entry = tkinter.Text(self.root, height=5, width=80)
        self.notes_entry.grid(row=15, column=1)
        button_frame = tkinter.Frame(self.root)
        button_frame.grid(row=16, column=1)
        cancel_button = tkinter.Button(
            button_frame,
            text="Cancel",
            name="cancel-vendor-button",
            command=self.cancel_btn,
            padx=7, pady=2
        )
        cancel_button.pack(side='left')
        tkinter.Button(
            button_frame,
            text="Save",
            name="save-vendor-button",
            command=self.save_btn,
            padx=7, pady=2
        ).pack(side='left')
        memos_btn = tkinter.Button(
            button_frame,
            text="Memos",
            name="memos-button",
            command=self.memos_btn,
            padx=7, pady=2
        )
        memos_btn.pack(side='left')

    def cancel_btn(self):
        """Edit Vendor Cancel Button"""

        self.root.iconify()
        self.parent.root.deiconify()

    def memos_btn(self):
        """Edit Vendor Start Memos Applet-Applet"""

        self.memo_app = tk_applet_applets.AppletAppletVendorMemo(self)
        self.memo_app.set_edit_form(self.vendor_obj)
        self.memo_app.root.deiconify()
        self.root.iconify()

    def _form_to_obj(self):
        """"""

        self.vendor_obj.name = self.name.get()
        self.vendor_obj.purpose = self.purpose.get()
        self.vendor_obj.street1 = self.street1.get()
        self.vendor_obj.street2 = self.street2.get()
        self.vendor_obj.apphone1 = self.apphone1.get()
        self.vendor_obj.apphone2 = self.apphone2.get()
        self.vendor_obj.apfirstname = self.apfirstname.get()
        self.vendor_obj.aplastname = self.aplastname.get()
        self.vendor_obj.city = self.city.get()
        self.vendor_obj.zip = self.zip.get()
        self.vendor_obj.accountnumber = self.accountnumber.get()
        self.vendor_obj.secretbits = self.secretbits_entry.get('1.0', 'end-1c')
        self.vendor_obj.notes = self.notes_entry.get('1.0', 'end-1c')
        self.vendor_obj.active = True if self.active.get() == 1 else False
        self.vendor_obj.state = self.state.get()

    def save_btn(self):
        """"""

        self._form_to_obj()

        result = api.VendorSchema().load(self.vendor_obj.to_dict())
        if result.errors:
            print(result.errors)
        else:
            lib.save_vendor(self.vendor_obj.to_dict())
            self.root.iconify()
            self.parent.root.deiconify()
            self.parent.load()

    def set_edit_form(self, vendor_dict):
        """"""

        # fixme: added memos digestion for Vendor Edit and Client Edit
        self.vendor_obj = api.Vendor(**vendor_dict)
        self.msgvar.set('%s %s' % (self.vendor_obj.id, self.vendor_obj.name))
        self.name.set(self.vendor_obj.name)
        self.purpose.set(self.vendor_obj.purpose)
        self.street1.set(self.vendor_obj.street1)
        self.street2.set(self.vendor_obj.street2)
        self.city.set(self.vendor_obj.city)
        self.state.set(self.vendor_obj.state)
        self.zip.set(self.vendor_obj.zip)
        self.apphone1.set(self.vendor_obj.apphone1)
        self.apphone2.set(self.vendor_obj.apphone2)
        self.apfirstname.set(self.vendor_obj.apfirstname)
        self.aplastname.set(self.vendor_obj.aplastname)
        self.accountnumber.set(self.vendor_obj.accountnumber)
        self.secretbits_entry.delete('1.0', tkinter.END)
        self.notes_entry.delete('1.0', tkinter.END)
        self.notes_entry.insert(
            tkinter.END, self.vendor_obj.notes if self.vendor_obj.notes else False)
        self.secretbits_entry.insert(
            tkinter.END, self.vendor_obj.secretbits if self.vendor_obj.secretbits else False)
        self.active.set(self.vendor_obj.active if self.vendor_obj.active else False)


class AppletEditVendorMemo(object):
    """"""

    def __init__(self, parent):
        """"""

        self.parent = parent
        self.memo_obj = None
        self.root = tkinter.Toplevel()
        self.root.iconify()
        self.date = tkinter.StringVar(self.root)
        notes_label = tkinter.Label(self.root, text='Notes')
        notes_label.grid(row=1, column=0)
        self.notes_entry = tkinter.Text(self.root, height=5, width=80)
        self.notes_entry.grid(row=1, column=1)
        date_label = tkinter.Label(self.root, text='Date')
        date_label.grid(row=2, column=0, sticky=tkinter.E)
        tkinter.Entry(self.root, textvariable=self.date).grid(row=2, column=1, sticky=tkinter.W)
        button_frame = tkinter.Frame(self.root)
        button_frame.grid(row=3, column=1)
        tkinter.Button(
            button_frame,
            text="Save",
            name="save-button",
            command=self.save_btn,
            padx=7, pady=2
        ).pack(side='left')
        tkinter.Button(
            button_frame,
            text="Cancel",
            name="cancel-button",
            command=self.cancel_btn,
            padx=7, pady=2
        ).pack(side='left')

    def cancel_btn(self):
        """"""

        self.root.iconify()
        self.parent.root.deiconify()

    def initialize(self):
        """"""

        self.notes_entry.delete('1.0', tkinter.END)
        self.date.set(dt.now().strftime(api.DATE_INPUT_FORMAT))

    def set_edit_form(self, vendor_memo):
        """"""

        self.memo_obj = api.VendorMemo(**vendor_memo)
        self.root.title = 'Memo for business vendor %s' % self.parent.parent.vendor_obj.name
        self.notes_entry.delete('1.0', tkinter.END)
        self.notes_entry.insert(tkinter.END, vendor_memo['notes'])
        self.date.set(
            dt.strptime(vendor_memo['date'],
                        api.DATE_ISO_FORMAT).strftime(api.DATE_INPUT_FORMAT)
        )

    def form_to_obj(self):
        """"""

        self.memo_obj.notes = self.notes_entry.get('1.0', 'end-1c')
        self.memo_obj.date = dt.strptime(
            self.date.get(), api.DATE_INPUT_FORMAT).strftime(api.DATE_ISO_FORMAT)

    def save_btn(self):
        """"""

        self.form_to_obj()
        result = api.VendorMemoSchema().load(self.memo_obj.to_dict())
        if result.errors:
            print(result.errors)
        else:
            lib.save_vendor_memo(self.memo_obj.to_dict())
            self.root.iconify()
            self.parent.root.deiconify()
            self.parent.load()
