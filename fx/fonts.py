SRC = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
MONO = ("𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉"
        "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣"
        "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿")
TBL = str.maketrans(SRC, MONO)
def mono(t: str) -> str: return t.translate(TBL)
def b(t: str) -> str: return f"<b>{t}</b>"
def i(t: str) -> str: return f"<i>{t}</i>"
def bi(t: str) -> str: return f"<b><i>{t}</i></b>"
def code(t: str) -> str: return f"<code>{t}</code>"
