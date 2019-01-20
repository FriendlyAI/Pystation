Prerequisites
-------------
You need to have libshout 2 installed. If you have pkg-config installed,
make sure it can find shout (you may need to adjust `PKG_CONFIG_PATH` to
contain `$shout_prefix/lib/pkgcofig`). Otherwise, shout-config must appear in
your path.

Installation
------------
Run `python3 setup.py install`

Debian
------------
Run `sudo apt-get install libshout3-dev` (Needed for header files)