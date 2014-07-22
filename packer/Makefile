all: qemu-images/libreant-qemu.qcow2
BUILDFILES=libreant.tar.gz poweroff.timer autologin.conf

qemu-images/libreant-qemu.qcow2: arch-template.json install-qemu.sh $(BUILDFILES)
	rm -rf qemu-images
	packer build -only qemu arch-template.json

vbox-images/libreant-vbox.ova: arch-template.json install-virtualbox.sh $(BUILDFILES)
	packer build -only virtualbox-iso arch-template.json

libreant.tar.gz:
	rm -f $@
	tar -C ../.. -czf $@ $(shell git ls-files .. |grep -v /packer | xargs realpath --relative-to ../..)
