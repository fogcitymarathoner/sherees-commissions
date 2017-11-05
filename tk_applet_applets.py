from tkinter import *
from tkinter import messagebox

import lib
import tk_applets
import tk_forms

# todo: make AppletAppletClientCheck

class AppletAppletClientMemo(object):
    def __init__(self, parent):

        self.vendor = None
        self.parent = parent
        self.create_app = None
        self.edit_app = None
        self.root = Toplevel()
        self.root.iconify()
        self.memo_objs = []
        button_frame = Frame(self.root)
        button_frame.pack()
        edit_button = Button(
            button_frame,
            text="Edit",
            name="edit-button",
            command=self.edit_btn,
            padx=7, pady=2
        )
        edit_button.pack(side="left")
        create_button = Button(
            button_frame,
            text="Add",
            name="add-button",
            command=self.add_btn,
            padx=7, pady=2
        )
        create_button.pack(side="left")
        cancel_btn = Button(
            button_frame,
            text="Cancel",
            name="cancel-button",
            command=self.cancel_btn,
            padx=7, pady=2
        )
        cancel_btn.pack(side='left')
        delete_button = Button(
            button_frame,
            text="Delete",
            name="delete-vendor-memo-button",
            command=self.delete_btn,
            padx=7, pady=2
        )
        delete_button.pack(side='left')
        scrollbar = Scrollbar(self.root)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox = Listbox(
            self.root,
            height=20,
            width=400,
            selectmode=SINGLE,
            yscrollcommand=scrollbar.set
        )

    def add_btn(self):

        self.root.iconify()
        if self.create_app is None:
            self.create_app = tk_applets.AppletCreateClientMemo(self)
        self.create_app.root.deiconify()

    def cancel_btn(self):

        self.root.iconify()
        self.parent.root.deiconify()

    def delete_btn(self):
        """Delete client memo"""

        if self.listbox.curselection() != ():
            result = messagebox.askquestion("Delete", "Are You Sure?", icon='warning')
            if result == 'yes':
                lib.delete_client_memo(self.memo_dicts[self.listbox.curselection()[0]]['id'])
                self.load()
            else:
                print("Delete canceled.")
        else:
            messagebox.showinfo(self.select_msg)
        self.load()

    def edit_btn(self):

        if self.listbox.curselection() != ():
            selected_memo = self.parent.client_obj.memos[self.listbox.curselection()[0]]
            if self.edit_app is None:
                self.edit_app = tk_applets.AppletEditClientMemo(self)
            self.edit_app.set(selected_memo)
            self.root.iconify()
            self.edit_app.root.deiconify()
        else:
            messagebox.showinfo("Error", "Please select a client memo.")

    def load(self):

        self.listbox.delete(0, END)
        self.memo_dicts = lib.list_page_clients_memos(self.parent.client_obj.id)
        for i in self.memo_dicts:
            # fixme: refactor this to be used with vendor memos formatted_vendor memo list ..
            self.listbox.insert(END,
                                '%s: %s - %s' % (i['id'], i['date'], i['notes']))
        self.listbox.pack()

    def set(self, client):

        self.root.title('Client Memos for %s' % self.parent.client_obj.name)
        self.load()


class AppletAppletVendorMemo(object):

    def __init__(self, parent):
        """"""

        self.vendor = None
        self.parent = parent
        self.create_app = None
        self.edit_app = None
        self.root = Toplevel()
        self.root.iconify()
        self.memo_dicts = []
        button_frame = Frame(self.root)
        button_frame.pack()
        edit_button = Button(
            button_frame,
            text="Edit",
            name="edit-button",
            command=self.edit_btn,
            padx=7, pady=2
        )
        edit_button.pack(side="left")
        create_button = Button(
            button_frame,
            text="Add",
            name="add-button",
            command=self.add_btn,
            padx=7, pady=2
        )
        create_button.pack(side="left")
        cancel_btn = Button(
            button_frame,
            text="Cancel",
            name="cancel-button",
            command=self.cancel_btn,
            padx=7, pady=2
        )
        cancel_btn.pack(side='left')
        delete_button = Button(
            button_frame,
            text="Delete",
            name="delete-vendor-memo-button",
            command=self.delete_btn,
            padx=7, pady=2
        )
        delete_button.pack(side='left')
        scrollbar = Scrollbar(self.root)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox = Listbox(
            self.root,
            height=20,
            width=400,
            selectmode=SINGLE,
            yscrollcommand=scrollbar.set
        )

    def add_btn(self):
        """Add vendor memo"""

        if self.create_app is None:
            self.create_app = tk_applets.AppletCreateVendorMemo(self)
        self.create_app.root.deiconify()
        self.root.iconify()

    def cancel_btn(self):
        """Exit to Edit Vendor"""

        self.root.iconify()
        self.parent.root.deiconify()

    def delete_btn(self):
        """Delete vendor memo"""

        if self.listbox.curselection() != ():
            result = messagebox.askquestion("Delete", "Are You Sure?", icon='warning')
            if result == 'yes':
                lib.delete_vendor_memo(self.memo_dicts[self.listbox.curselection()[0]]['id'])
                self.load()
            else:
                print("Delete canceled.")
        else:
            messagebox.showinfo(self.select_msg)
        self.load()

    def edit_btn(self):
        """Edit vendor memo"""

        if self.listbox.curselection() != ():
            selected_memo = self.memo_dicts[self.listbox.curselection()[0]]
            if self.edit_app is None:
                self.edit_app = tk_applets.AppletEditVendorMemo(self)
            self.edit_app.set_edit_form(selected_memo)
            self.root.iconify()
            self.edit_app.root.deiconify()
        else:
            messagebox.showinfo("Error", "Please select a vendor memo.")

    def load(self):
        """"""

        self.listbox.delete(0, END)
        # fixme: format vendor memo list lines
        self.memo_dicts = lib.list_page_vendors_memos(self.vendor.id)
        for i in self.memo_dicts:
            self.listbox.insert(END, i)
        self.listbox.pack()

    def set_edit_form(self, vendor_obj):
        """"""

        self.vendor = vendor_obj
        self.root.title('Vendors Memos for %s' % self.vendor.name)
        self.load()
