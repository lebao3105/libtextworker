"""
@package libtextworker.interface.tk.about
@brief About dialog for Tkinter projects
"""

#	A cross-platform library for Python apps.
#	Copyright (C) 2023 Le Bao Nguyen and contributors.
#	This is a part of the libtextworker project.
#	Licensed under the GNU General Public License version 3.0 or later.

from tkinter import Toplevel, Misc
from tkinter.ttk import Button, Frame, Label, Notebook

from . import editor
from ... import _


class AboutDialog:
    """
    A custom About dialog for Tkinter.
    """

    # Project credits
    ArtMakers: str = ""
    Developers: str = ""
    Testers: str = ""
    Translators: str = ""

    # Project base infos
    ProjectName: str = ""
    ProjectVersion: str = ""
    ProjectSite: str = ""
    ProjectDescription: str = ""
    ProjectLicense: str = ""

    def SetArtMakers(this, names: list | str):
        this.ArtMakers = "\n\t".join(names) if isinstance(names, list) else names

    def SetDevelopers(this, names: list | str):
        this.Developers = "\n\t".join(names) if isinstance(names, list) else names

    def SetAppTesters(this, names: list | str):
        this.Testers = "\n\t".join(names) if isinstance(names, list) else names

    def SetAppTranslators(this, names: list | str):
        this.Translators = "\n\t".join(names) if isinstance(names, list) else names

    def SetProjectName(this, name: str):
        this.ProjectName = name

    def SetProjectVersion(this, version: str):
        this.ProjectVersion = version

    def SetProjectSite(this, address: str):
        this.ProjectSite = address

    def SetProjectDescription(this, description: str):
        this.ProjectDescription = description

    def SetProjectLicense(this, license: str):
        this.ProjectLicense = license

    def ShowDialog(this, master: Misc | None = None):
        """
        Here goes the real About dialog.
        If you don't like my style, just derive this function and
            start making your own.
        TODO: Modifyable UI without remaking from scratch.
        """
        dlg = Toplevel(master)
        dlg.wm_title(_("About this project"))
        dlg.grab_set()
        dlg.geometry("350x450")  # legit?

        project_infos = _("About this project\n"
                          f"{this.ProjectName} version {this.ProjectVersion}\n"
                          f"Description: {this.ProjectDescription}\n"
                          f"Project website: {this.ProjectSite}")

        project_credits = _("This software is made thanks to many contributors:\n"
                            f"Developers:\n{this.Developers}")

        if this.ArtMakers:
            project_credits += _(f"\nArtists:\n{this.ArtMakers}")

        if this.Testers:
            project_credits += _(f"\nTesters:\n{this.Testers}")

        if this.Translators:
            project_credits += _(f"\nTranslators:\n{this.Translators}")

        project_license = _("This project is licensed to the following license:") + \
                          f"\n\n\n{this.ProjectLicense}"

        nb = Notebook(dlg)
        nb.pack(fill="both", expand=True)

        # Make tabs
        license_te = editor.StyledTextControl(dlg, wrap="word")
        license_te.insert(1.0, project_license)
        license_te.configure(state="disabled")
        license_te.pack(expand=True, fill="both", anchor="nw")

        nb.add(Label(dlg, text=project_infos, anchor="nw"), text=_("This software"))
        nb.add(Label(dlg, text=project_credits, anchor="nw"), text=_("Contributors"))
        nb.add(license_te._frame, text=_("License"))

        # Bottom frame, containing a "OK" button
        bottomfm = Frame(dlg)
        quitbtn = Button(bottomfm, text="OK", default="active")
        quitbtn.bind("<Button-1>", lambda evt: (dlg.destroy()))
        quitbtn.pack(side="right")
        bottomfm.pack(fill="x", side="bottom")

        dlg.mainloop()
