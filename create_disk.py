from machfs import Volume, Folder, File


def make_floppy():
    v = Volume()

    v['Folder'] = Folder()

    v['Folder']['File'] = File()
    v['Folder']['File'].data = b'Hello from Python!\r'
    v['Folder']['File'].rsrc = b''  # Use the macresources library to work with resource forks
    v['Folder']['File'].type = b'TEXT'
    v['Folder']['File'].creator = b'ttxt'  # Teach Text/SimpleText

    with open('FloppyImage.dsk', 'wb') as f:
        flat = v.write(
            size=1440 * 1024,  # "High Density" floppy
            align=512,  # Allocation block alignment modulus (2048 for CDs)
            desktopdb=True,  # Create a dummy Desktop Database to prevent a rebuild on boot
            bootable=True,  # This requires a folder with a ZSYS and a FNDR file
            startapp=('Folder', 'File'),  # Path (as tuple) to an app to open at boot
        )
        f.write(flat)
