"""
# Styles

* Description:

    Paths for stylesheets located within the toolkit module.
"""


from pathlib import Path
from typing import Union

from PySide6 import QtWidgets

import PySide6TK


def set_style(menu: QtWidgets.QWidget, style_path: Path) -> None:
    """Applies the style file contents to the given menu.

    Args:
        menu (Union[QtWidgets.QMainWindow, QtWidgets.QWidget]): The menu to
            apply the style to.
        style_path (Path): The path to the stylesheet file.
    """
    with open(style_path) as f:
        menu.setStyleSheet(f.read())


STYLE_PATH = Path(PySide6TK.RESOURCES_PATH, 'stylesheets')

# ----------QSS----------------------------------------------------------------
QSS_ADAPTIC = Path(STYLE_PATH, 'Adaptic.qss')
QSS_CHATBEE = Path(STYLE_PATH, 'Chatbee.qss')
QSS_CLIENTOR = Path(STYLE_PATH, 'Clientor.qss')
QSS_CLOCKER = Path(STYLE_PATH, 'Clocker.qss')
QSS_COMBINEAR = Path(STYLE_PATH, 'Combinear.qss')
QSS_CSTARTPAGE = Path(STYLE_PATH, 'Cstartpage.qss')
QSS_DARKEUM = Path(STYLE_PATH, 'Darkeum.qss')
QSS_DARKORANGE = Path(STYLE_PATH, 'DarkOrange.qss')
QSS_DEEPBOX = Path(STYLE_PATH, 'DeepBox.qss')
QSS_DEVSION = Path(STYLE_PATH, 'Devsion.qss')
QSS_DIFFNES = Path(STYLE_PATH, 'Diffnes.qss')
QSS_DIPLAYTAP = Path(STYLE_PATH, 'Diplaytap.qss')
QSS_DTOR = Path(STYLE_PATH, 'Dtor.qss')
QSS_EASYCODE = Path(STYLE_PATH, 'EasyCode.qss')
QSS_ECLIPPY = Path(STYLE_PATH, 'Eclippy.qss')
QSS_EXCELOFFICE = Path(STYLE_PATH, 'ExcelOffice.qss')
QSS_FIBERS = Path(STYLE_PATH, 'Fibers.qss')
QSS_FIBRARY = Path(STYLE_PATH, 'Fibrary.qss')
QSS_FILMOVIO = Path(STYLE_PATH, 'Filmovio.qss')
QSS_GENETIVE = Path(STYLE_PATH, 'Genetive.qss')
QSS_GEOO = Path(STYLE_PATH, 'Geoo.qss')
QSS_GRAVIRA = Path(STYLE_PATH, 'Gravira.qss')
QSS_HACKBOOK = Path(STYLE_PATH, 'HackBook.qss')
QSS_HOOKMARK = Path(STYLE_PATH, 'Hookmark.qss')
QSS_INCRYPT = Path(STYLE_PATH, 'Incrypt.qss')
QSS_INTEGRID = Path(STYLE_PATH, 'Integrid.qss')
QSS_IRRORATER = Path(STYLE_PATH, 'Irrorater.qss')
QSS_MAILSY = Path(STYLE_PATH, 'MailSy.qss')
QSS_MEDIZE = Path(STYLE_PATH, 'Medize.qss')
QSS_MIXCHAT = Path(STYLE_PATH, 'Mixchat.qss')
QSS_MYWATCH = Path(STYLE_PATH, 'MyWatch.qss')
QSS_OBIT = Path(STYLE_PATH, 'Obit.qss')
QSS_PERSTFIC = Path(STYLE_PATH, 'Perstfic.qss')
QSS_PHOTOXO = Path(STYLE_PATH, 'Photoxo.qss')
QSS_PICPAX = Path(STYLE_PATH, 'PicPax.qss')
QSS_REMOVER = Path(STYLE_PATH, 'Remover.qss')
QSS_SCALCULA = Path(STYLE_PATH, 'Scalcula.qss')
QSS_SPYBOT = Path(STYLE_PATH, 'SpyBot.qss')
QSS_SYNET = Path(STYLE_PATH, 'SyNet.qss')
QSS_TAKEZO = Path(STYLE_PATH, 'Takezo.qss')
QSS_TCOBRA = Path(STYLE_PATH, 'TCobra.qss')
QSS_TOOLERY = Path(STYLE_PATH, 'Toolery.qss')
QSS_VISUALSCRIPT = Path(STYLE_PATH, 'VisualScript.qss')
QSS_WEBMAS = Path(STYLE_PATH, 'Webmas.qss')
QSS_WORDOFFICE = Path(STYLE_PATH, 'WordOffice.qss')
QSS_WSTARTPAGE = Path(STYLE_PATH, 'Wstartpage.qss')
