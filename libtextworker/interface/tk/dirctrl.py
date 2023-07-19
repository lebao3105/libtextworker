import os
import tkinter.ttk as ttk


class DirCtrl(ttk.Treeview):
    nodes : dict

    def __init__(self, **kwds):
        self._frame = ttk.Frame(kwds.get("master", None))
        super().__init__(self._frame, **kwds)

        ysb = ttk.Scrollbar(self._frame, orient='vertical', command=self.yview)
        xsb = ttk.Scrollbar(self._frame, orient='horizontal', command=self.xview)
        self.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.heading('#0', text='Project tree', anchor='w')

        ysb.pack(fill="y", expand=True)
        xsb.pack(fill="x", expand=True)
        self.pack(expand=True, fill="both")

    def setpath(self, path: str):
        abspath = os.path.abspath(path)
        self.insert_node('', abspath, abspath)
        self.bind('<<TreeviewOpen>>', self.open_node)

    def insert_node(self, parent, text, abspath):
        node = self.insert(parent, 'end', text=text, open=False)
        if os.path.isdir(abspath):
            self.nodes[node] = abspath
            self.insert(node, 'end')

    def open_node(self, event):
        node = self.focus()
        abspath = self.nodes.pop(node, None)
        if abspath:
            self.delete(self.get_children(node))
            for p in os.listdir(abspath):
                self.insert_node(node, p, os.path.join(abspath, p))
