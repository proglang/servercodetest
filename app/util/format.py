import re


class Tags:
    tag = "SCT"
    tags = {}

    class BASE:
        @classmethod
        def to_html(cls, data, open):
            return ""

        @classmethod
        def format(cls, text: str, *args, open=None, **kw):
            return Tags.format(text, cls, open=open)
    class BASE_STRUCT(BASE):
        @classmethod
        def format(cls, text: str, *args, open=None, **kw):
            return Tags.format(None, cls,text, open=True)

    class COLOR(BASE):
        @classmethod
        def to_html(cls, data, open):
            if open:
                return f'<span style="color: {data.lower()}">'
            return "</span>"

        @classmethod
        def format(cls, text: str, color: str, *args, **kw):
            return Tags.format(text, cls, color.upper(), **kw)

    class BOLD(BASE):
        @classmethod
        def to_html(cls, data, open):
            if open:
                return '<span style="font-weight:bold">'
            return "</span>"

    class HEADER(BASE_STRUCT):
        @classmethod
        def to_html(cls, data, open):
            return f'<div class="sct_header"><span>&#8649; {data} &#8647;</span></div>'

    class SECTION(BASE_STRUCT):
        @classmethod
        def to_html(cls, data, open):
            return f'<div class="sct_separator sct_section"><span>&#8650; {data} &#8650;</span></div>'

    class SUBSECTION(BASE_STRUCT):
        @classmethod
        def to_html(cls, data, open):
            return f'<div class="sct_separator sct_subsection"><span>&darr; {data} &darr;</span></div>'

    @classmethod
    def format(cls, text, tag, *args, open=None):
        if issubclass(tag, cls.BASE):
            tag = tag.__name__
        if tag == None:
            return text
        tag = ":".join([cls.tag, tag, *args])
        if open == True:
            return f"<{tag}>"
        if open == False:
            return f"<!{tag}>"
        return f"<{tag}>{text}<!{tag}>"

    @classmethod
    def _to_html(cls, match: re.Match):
        (start, data) = match.groups()
        (tag, _, cmd) = re.match("^(.*?)(|:(.*))$", data).groups()
        if _tag := cls.tags.get(tag, None):
            return _tag.to_html(cmd, start == "")
        return ""

    @classmethod
    def to_html(cls, text):
        cls.init()
        text = re.sub("<", "&lt;", text)
        text = re.sub(">", "&gt;", text)
        return re.sub(f"&lt;(!?){cls.tag}:(.*?)&gt;", cls._to_html, text)

    @classmethod
    def init(cls):
        if len(cls.tags) > 0:
            return
        attrib = map(lambda key: getattr(cls, key), dir(cls))
        attrib = filter(lambda elem: isinstance(elem, type), attrib)
        attrib = filter(lambda elem: issubclass(elem, cls.BASE), attrib)
        cls.tags = {elem.__name__:elem for elem in attrib}

bold = Tags.BOLD.format
color = Tags.COLOR.format
red = lambda x, open=None: Tags.COLOR.format(x, "red", open=open)
green = lambda x, open=None: Tags.COLOR.format(x, "green", open=open)
blue = lambda x, open=None: Tags.COLOR.format(x, "blue", open=open)
header = Tags.HEADER.format
section = Tags.SECTION.format
subsection = Tags.SUBSECTION.format

class ANSI:
    REGEX = re.compile(r"\x1b\[([^m]*)m")
    ESCAPE = {
        "1": bold,
        "31": red,
        "32": green,
    }

    def __init__(self, text):
        self.text = text
        self.keys = []

    def get_repl(self, key, close=False):
        repl = self.ESCAPE.get(key, None)
        if repl == None:
            return ""
        return repl(None, open=not close)

    def close(self):
        repl = ""
        self.keys.reverse()
        for key in self.keys:
            repl += self.get_repl(key, True)
        self.keys.clear()
        return repl

    def repl(self, text):
        self.text = self.REGEX.sub(text, self.text, 1)

    def _escape(self):
        while (pos := self.text.find("\x1b[")) >= 0:
            data = self.REGEX.match(self.text, pos)
            key = data.groups()[0]
            if key == "0":
                self.repl(self.close())
                continue
            val = self.ESCAPE.get(key)
            if val == None:
                continue
            self.keys.append(key)
            self.repl(self.get_repl(key))
        self.close()
        return self.text

    @classmethod
    def escape(cls, text):
        return cls(text)._escape()

escape_ansi = ANSI.escape
to_html = lambda text: Tags.to_html(escape_ansi(text))
