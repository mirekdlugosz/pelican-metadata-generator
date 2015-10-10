# Pelican Metadata Generator 

Graphical application that creates Pelican (<http://blog.getpelican.com/>)
post metadata. Written in Python 3.x and Qt 5.x (PyQt).

## Rationale

Pelican is static website generator that does not provide any way of
accessing exisiting content at new page creation. Simple typo in category 
name or tag name will create spurious entity that you might not catch in 
time and push to live site.

This application tries to prevent these mistakes from happening by 
exposing existing Pelican data in graphical user interface. Re-using
previous name is as easy as picking it up from GUI. Creation of new
categories or tags must be opted-in.

Added value is that slug will be generated automatically from post title
and will serve as post file name, if you decide to save data on disk.

## Limitations

See TODO file.

## Copying

Distributed under GNU AGPLv3, the same as Pelican. See LICENSE file.
