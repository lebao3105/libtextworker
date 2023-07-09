from tkinter import Toplevel, Misc, Text
from tkinter.ttk import Button, Frame, Label, Notebook
from typing import AnyStr
from . import editor
from .. import available_licenses
from ... import LICENSES

class AboutDialog:

    # Project credits
    ArtMakers: str = ""
    Developers: str = ""
    Testers: str = ""
    Translators: str = ""

    # Project base infos
    ProjectName: str = ""
    ProjectVersion: AnyStr = ""
    ProjectSite: AnyStr = ""
    ProjectDescription: AnyStr = ""
    ProjectLicense: str = ""

    def SetArtMakers(self, _: list | str):
        self.ArtMakers = "\n\t".join(_) if isinstance(_, list) else _
    
    def SetDevelopers(self, _: list | str):
        self.Developers = "\n\t".join(_) if isinstance(_, list) else _
    
    def SetAppTesters(self, _: list | str):
        self.Testers = "\n\t".join(_) if isinstance(_, list) else _
    
    def SetAppTranslators(self, _: list | str):
        self.Translators = "\n\t".join(_) if isinstance(_, list) else _
    
    def SetProjectName(self, _: str):
        self.ProjectName = _
    
    def SetProjectVersion(self, _: AnyStr):
        self.ProjectVersion = _
    
    def SetProjectSite(self, _: AnyStr):
        self.ProjectSite = _
    
    def SetProjectDescription(self, _: AnyStr):
        self.ProjectDescription = _
    
    def SetProjectLicense(self, _: str):
        if _ in available_licenses:
            self.ProjectLicense = open(LICENSES + "/" +  _ + ".txt", "r").read()
        else:
            self.ProjectLicense = _
    
    def ShowDialog(self, master: Misc | None = None):
        """
        Here goes the real About dialog.
        If you don't like my style, just derive this function and
            start making your own.
        """
        dlg = Toplevel(master)
        dlg.wm_title(_("About this project"))
        dlg.geometry("350x450") # legit?

        project_infos = \
            _("About this project\n" \
            f"{self.ProjectName} version {self.ProjectVersion}\n" \
            f"Description: {self.ProjectDescription}\n" \
            f"Project website: {self.ProjectSite}")
        
        project_credits = \
            _("This software is made thanks to many contributors:\n" \
            f"Developers:\n{self.Developers}")
        
        if self.ArtMakers:
            project_credits += _(f"\nArtists:\n{self.ArtMakers}")
        
        if self.Testers:
            project_credits += _(f"\nTesters:\n{self.Testers}")
        
        if self.Translators:
            project_credits += _(f"\nTranslators:\n{self.Translators}")
        
        project_license = \
            f'{_("This project is licensed to the following license:")}' \
            f"\n\n\n{self.ProjectLicense}"

        nb = Notebook(dlg)
        nb.pack(fill="both", expand=True)

        # Make tabs
        license_te = editor.StyledTextControl(dlg, state="disabled", wrap="word")
        license_te.insert(1.0, project_license)
        license_te.pack(expand=True, fill="both")
        
        nb.add(Label(dlg, text=project_infos), text=_("This software"))
        nb.add(Label(dlg, text=project_credits), text=_("Contributors"))
        nb.add(license_te._frame, text=_("License"))

        # Bottom frame, containing a "OK" button
        bottomfm = Frame(dlg)
        quitbtn = Button(bottomfm, text="OK", default="active")
        quitbtn.bind("<Button-1>", lambda evt: (dlg.destroy()))
        quitbtn.pack(side="right")
        bottomfm.pack(fill="x", side="bottom")

        dlg.mainloop()