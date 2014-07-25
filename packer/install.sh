#!/usr/bin/env bash

DISK='/dev/sda'
FQDN='libreant.taz'
KEYMAP='it'
LANGUAGE='it_IT.UTF-8'
PASSWORD=$(/usr/bin/openssl passwd -crypt 'pass')
LIBREANT_PASSWORD=$(/usr/bin/openssl passwd -crypt 'libreant')
TIMEZONE='UTC'

CONFIG_SCRIPT='/usr/local/bin/arch-config.sh'
ROOT_PARTITION="${DISK}1"
TARGET_DIR='/mnt'

echo "==> new repositories"
/usr/bin/cat <<EOPAC >> /etc/pacman.conf
[xyne-x86_64]
SigLevel = Required
Server = http://xyne.archlinux.ca/repos/xyne
EOPAC
/usr/bin/pacman -Syyq --noconfirm pacserve
/usr/bin/pacman.conf-insert_pacserve > p.conf
mv p.conf /etc/pacman.conf
/usr/bin/cat <<EOPAC >> /etc/pacserve/pacserve.service.conf
PACSERVE_ARGS="--multicast --peer http://10.0.2.2:15678 --list-remote"
EOPAC
/usr/bin/systemctl start pacserve

echo "==> clearing partition table on ${DISK}"
/usr/bin/sgdisk --zap ${DISK}

echo "==> destroying magic strings and signatures on ${DISK}"
/usr/bin/dd if=/dev/zero of=${DISK} bs=512 count=2048
/usr/bin/wipefs --all ${DISK}

echo "==> creating /root partition on ${DISK}"
/usr/bin/sgdisk --new=1:0:0 ${DISK}

echo "==> setting ${DISK} bootable"
/usr/bin/sgdisk ${DISK} --attributes=1:set:2

echo '==> creating /root filesystem (ext4)'
/usr/bin/mkfs.ext4 -F -m 0 -q -L root ${ROOT_PARTITION}

echo "==> mounting ${ROOT_PARTITION} to ${TARGET_DIR}"
/usr/bin/mount -o noatime,errors=remount-ro ${ROOT_PARTITION} ${TARGET_DIR}

echo '==> bootstrapping the base installation'
/usr/bin/pacstrap ${TARGET_DIR} base base-devel
/usr/bin/arch-chroot ${TARGET_DIR} pacman -Sq  --needed --noconfirm gptfdisk openssh syslinux ucommon
/usr/bin/arch-chroot ${TARGET_DIR} syslinux-install_update -i -a -m
/usr/bin/sed -i 's/sda3/sda1/' "${TARGET_DIR}/boot/syslinux/syslinux.cfg"
/usr/bin/sed -i 's/TIMEOUT 50/TIMEOUT 10/' "${TARGET_DIR}/boot/syslinux/syslinux.cfg"

echo '==> generating the filesystem table'
/usr/bin/genfstab -p ${TARGET_DIR} >> "${TARGET_DIR}/etc/fstab"

echo '==> generating the system configuration script'
/usr/bin/install --mode=0755 /dev/null "${TARGET_DIR}${CONFIG_SCRIPT}"

echo '==> preseeding pacman cache'
/usr/bin/mkdir -p ${TARGET_DIR}/var/cache/pacman/pkg/
/usr/bin/cp -f /var/cache/pacman/pkg/*.pkg.* ${TARGET_DIR}/var/cache/pacman/pkg/

/usr/bin/mv libreant.tar.gz ${TARGET_DIR}
/usr/bin/mv autologin.conf ${TARGET_DIR}
/usr/bin/mv install-* ${TARGET_DIR}

cat <<-EOF > "${TARGET_DIR}${CONFIG_SCRIPT}"
	echo '${FQDN}' > /etc/hostname
	/usr/bin/ln -s /usr/share/zoneinfo/${TIMEZONE} /etc/localtime
	echo 'KEYMAP=${KEYMAP}' > /etc/vconsole.conf
	/usr/bin/sed -i 's/#${LANGUAGE}/${LANGUAGE}/' /etc/locale.gen
	/usr/bin/locale-gen
	/usr/bin/mkinitcpio -p linux
	/usr/bin/usermod --password ${PASSWORD} root

	# https://wiki.archlinux.org/index.php/Network_Configuration#Device_names
	/usr/bin/ln -s /dev/null /etc/udev/rules.d/80-net-setup-link.rules
	/usr/bin/ln -s '/usr/lib/systemd/system/dhcpcd@.service' '/etc/systemd/system/multi-user.target.wants/dhcpcd@eth0.service'
	/usr/bin/sed -i 's/#UseDNS yes/UseDNS no/' /etc/ssh/sshd_config
	/usr/bin/systemctl enable sshd.service

	echo '==> new repositories'
	/usr/bin/cat <<EOPAC >> /etc/pacman.conf
[xyne-x86_64]
SigLevel = Required
Server = http://xyne.archlinux.ca/repos/xyne
EOPAC
	/usr/bin/pacman -Syyq --noconfirm pacserve
	/usr/bin/pacman.conf-insert_pacserve > p.conf
	mv p.conf /etc/pacman.conf
	/usr/bin/cat <<EOPAC >> /etc/pacserve/pacserve.service.conf
	PACSERVE_ARGS="--multicast --peer http://10.0.2.2:15678 --list-remote"
	EOPAC
	/usr/bin/systemctl start pacserve

	LIBREANT_PASSWORD="$LIBREANT_PASSWORD"
	PASSWORD="$PASSWORD"
	ROOT_PARTITION="$ROOT_PARTITION"
    # Install scripts!
    run-parts --list / | while read installer; do
        echo "----> Running \$installer"
        source "\$installer"
    done
EOF

echo '==> entering chroot and configuring system'
if ! /usr/bin/arch-chroot ${TARGET_DIR} ${CONFIG_SCRIPT}; then
	echo "Errors in chroot, inspect freely"
	exit 1
fi
rm "${TARGET_DIR}${CONFIG_SCRIPT}"

# http://comments.gmane.org/gmane.linux.arch.general/48739
echo '==> adding workaround for shutdown race condition'
/usr/bin/install --mode=0644 poweroff.timer "${TARGET_DIR}/etc/systemd/system/poweroff.timer"

echo '==> installation complete!'
/usr/bin/sleep 3
/usr/bin/umount ${TARGET_DIR}
/usr/bin/systemctl reboot
