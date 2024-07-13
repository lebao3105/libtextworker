# Variable aliases and more

There are no aliases I have to make now.

But there are something to see:

## *NIX shell syntax

If you see something like `-{,{mouse,finder}}`, it's the same as:

* `-`
* `-mouse`
* `-finder`

No space between `mouse` and `finder` is indentional. If there's one then we will have:

* `{mouse, finder}` => `mouse` and ` finder`;
* `{mouse ,finder}` => `mouse ` and `finder`