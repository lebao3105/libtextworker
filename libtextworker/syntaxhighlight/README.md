## Syntax highlighting support from libtextworker
It's can only be used for wxPython's StyledTextCtrl (located in the ```wx.stc``` module).

## How does it work
* blank here *

## Make a new one!
Create a file named ```<language>.ini``` with this template:
```ini
[project]
name = 'your language name here'
file_extensions = 'exts' 'start by a dot' 'and separated like this'

[wxSTC]
; Configs for wx StyledTextCtrl
; Check /Items.txt for all what you need
lexer_suffix = 'Python' ; STC_LEX_[lexer_suffix in uppercase]
short_name = 'P' ; STC_[short_name]_*

[highlight]
; Check for STC_[short_name]_*
; Syntax (for all): fore:(hex color),back:(hex color)
; fore means 'foreground', 'back' means 'background'
; Use %(foreclr) or %(backclr) to use libtextworker's default color

; Below is an example (for Python)
CHARACTER = 'fore:#0040ff,back:#9281a9'
COMMENTLINE = 'fore:%(foreclr)'

[keywords] ; should be syntax:)
; implement everything here, separated by '|':
NUMBERS = '0|1|2|3|4|5|6|7|8|9'
```

Place the file at the same folder with the file you're reading:)