Packer
===========

This directory is devoted to the creation of virtual appliances ready to be used in virtualbox/qemu.
There are two main goals for this:
* easy testing/development/showcase
* easy setup


Run the VM
==========
run it with

```sh
qemu-system-x86_64  -hda qemu-images/libreant-qemu.qcow2 -m 512 -enable-kvm -netdev
user,id=interna,hostfwd=tcp::5000-:5000,restrict=off -device virtio-net-pci,netdev=interna -smp cpus=2
```

Inside the vm, run

```sh
./libre_ve/bin/webant
```

Then open your "normal" browser, and open http://localhost:5000/
You should see libreant!
