import textwrap, re


swatch = {
    'black': '0;30', 'bright gray': '0;37',
    'blue': '0;34', 'white': '1;37',
    'green': '0;32', 'bright blue': '1;34',
    'cyan': '0;36', 'bright green': '1;32',
    'red': '0;31', 'bright cyan': '1;36',
    'purple': '0;35', 'bright red': '1;31',
    'yellow': '0;33', 'bright purple': '1;35',
    'dark gray': '1;30', 'bright yellow': '1;33',
    'dgray': '1;30', 'bgray': '0;37', 'bblue': '1;34',
    'bgreen': '1;32', 'bcyan': '1;36', 'bred': '1;31',
    'bpurple': '1;35', 'byellow': '1;33', 'default': '0',
    'normal': '0'
}


def colorfy(text, color):
    color = color.lower()
    key = "normal"
    if color in swatch:
        key = color
    text = text.replace("[0m", "[" + swatch[key] + "m")
    return "\033[" + swatch[key] + "m" + text + "\033[0m"


def wrap(text, cols=80, indent=""):
    t = AnsiIgnoreTextWrapper()
    t.break_long_words = True
    t.subsequent_indent = indent
    t.width = cols
    lines = text.splitlines()
    wrapped_lines = []
    for line in lines:
        toadd = t.wrap(line)
        if len(toadd) == 0:
            wrapped_lines.append("")
        else:
            wrapped_lines += toadd
    s = "\n".join(wrapped_lines)
    return s


class AnsiIgnoreTextWrapper(textwrap.TextWrapper):
    """Subclass of the TextWrapper that ignores ANSI escape codes"""
    def __init__(self):
        textwrap.TextWrapper.__init__(self)
        self.ansi_escape = re.compile(r'\x1b[^m]*m')

    def _len(self, text):
        return len(self.ansi_escape.sub('', text))

    def _wrap_chunks(self, chunks):
        """
        Does what the normal method does, except ignores ANSI stuff in len()
        """
        lines = []
        if self.width <= 0:
            raise ValueError("invalid width %r (must be > 0)" % self.width)

        chunks.reverse()

        while chunks:
            cur_line = []
            cur_len = 0

            # Figure out which static string will prefix this line.
            if lines:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent

            # Maximum width for this line.
            width = self.width - len(indent)

            # First chunk on line is whitespace -- drop it, unless this
            # is the very beginning of the text (ie. no lines started yet).
            if self.drop_whitespace and chunks[-1].strip() == '' and lines:
                del chunks[-1]

            while chunks:
                l = self._len(chunks[-1])

                # Can at least squeeze this chunk onto the current line.
                if cur_len + l <= width:
                    cur_line.append(chunks.pop())
                    cur_len += l

                # Nope, this line is full.
                else:
                    break

            # The current line is full, and the next chunk is too big to
            # fit on *any* line (not just this one).
            if chunks and self._len(chunks[-1]) > width:
                self._handle_long_word(chunks, cur_line, cur_len, width)

            # If the last chunk on this line is all whitespace, drop it.
            if self.drop_whitespace and cur_line and cur_line[-1].strip() == '':
                del cur_line[-1]

            # Convert current line back to a string and store it in list
            # of all lines (return value).
            if cur_line:
                lines.append(indent + ''.join(cur_line))

        return lines