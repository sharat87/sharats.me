title: Installing Crunchbang Linux on my old lappy
tags: crunchbang, linux


I managed to install Crunchbang linux, the recently released Stetler, after
reading quite a positive review (I don't remember where). I am really liking
it, especially the openbox desktop environment. Also, coming from a lot of
experience on ubuntu, finding crunchbang look so bare-bones and simple, yet so
customizable is very refreshing. I will put my experience with installing it
and my initial thoughts, before I forget them :).

Now my laptop's got a defective and unreliable disk drive, so I chose to
install crunchbang from usb with the help of unetbootin. After downloading the
`#!` (crunchbang) iso file, I fired up unetbootin on my windows vista (on the
same laptop) and setup my 1GB pen drive to be bootable. After that, I had to
create a couple of symlinks (using cygwin) on the usb drive as following

```bash
ln -s live/vmlinuz1 vmlinuz
ln -s live/initrd1.img initrd.img
```

After that, the boot was pretty smooth, and I had to choose the graphical
installer as the text based installer wouldn't load, which I have no idea why.

Another interesting thing that happened was that at the end of the
installation, #! asked me if I wanted to install the grub boot loader, and that
it detects windows as another OS on the machine. However the grub it installed
does not list windows in the boot menu. I asked a question about this on
unix.stackexchange.com and got to know that a simple sudo update-grub added the
windows item to my boot menu. Not a major set-back, but still.

After that, using the OS is nothing but a pure pleasure. It feels amazingly
snappy and super productive. The conky based hotkey reference on the desktop is
a killer thing to look for. Oh, and dropbox installation is easier than on my
ubuntu box, if you use dropbox that is. Chrome, my browser of choice, is the
default browser, what more can I ask? Awesome distribution. I am looking
forward to exploring even more with my shiny new #!, and I seriously recommend
you give it a try :)
