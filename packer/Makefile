all: qemu-images/libreant-qemu.qcow2 vbox-images/libreant-vbox.ovf
BUILDFILES=libreant.tar.gz poweroff.timer autologin.conf install.sh 

qemu-images/libreant-qemu.qcow2: arch-template.json $(BUILDFILES)
	rm -rf qemu-images
	packer build -only qemu $<

vbox-images/libreant-vbox.ovf: arch-template.json $(BUILDFILES)
	packer build -only virtualbox-iso $<

libreant.tar.gz:
	rm -f $@
	tar -C ../.. -czf $@ $(shell git ls-files .. |grep -v /packer | xargs realpath --relative-to ../..)
