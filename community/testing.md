# Qubes OS Forum — Testing

> 来源：https://forum.qubes-os.org
> 板块：Testing Team, 4.2 Testing, 4.1 Testing, 4.3 Testing, 4.4 Testing
> 爬取时间：2026-05-02 17:19

---

## Fedora 43 templates available for testing

> 板块: Testing Team

Dear Qubes OS 4.2 testers,

Fedora 43 templates (including  [Xfce](https://doc.qubes-os.org/en/latest/user/templates/xfce-templates.html), [minimal](https://doc.qubes-os.org/en/latest/user/templates/minimal-templates.html), and GNOME versions) for Qubes OS 4.2 are now available for testing in the [`qubes-templates-itl-testing`](https://yum.qubes-os.org/r4.2/templates-itl-testing/rpm/) repository. Here’s the associated issue:

https://github.com/QubesOS/qubes-issues/issues/10102

Please note that these templates have already been released for 4.3, which is why this testing is only for 4.2:

https://www.qubes-os.org/news/2026/02/06/fedora-43-templates-available/

Your feedback will be invaluable in helping us determine whether there any bugs that need to be fixed before the stable release of this template. For more information about how to test and provide feedback, please see:

https://doc.qubes-os.org/en/latest/user/downloading-installing-upgrading/testing.html

---

## First Fedora 44 templates for testing

> 板块: Testing Team

Today, the Qubes-OS team published the first fedora-44 templates for **testing**.

So please, test theses templates and report issues in the main fedora-44 issue.

## How to test ?

In dom0, launch `qvm-template-gui`. If not already done, add the `qubes-template-itl-testing` repository and refresh. Then install the wanted template from the available list:
- [fedora-44-xfce](https://github.com/QubesOS/updates-status/issues/6599)
- [fedora-44-gnome](https://github.com/QubesOS/updates-status/issues/6600)
- [fedora-44-minimal](https://github.com/QubesOS/updates-status/issues/6601)

Then create a new fedora-44 qube-app, and test it.

## How to report problem ?

Add a new comment in the below #10703 issue, with a description of the problem and the steps to reproduce it.

https://github.com/QubesOS/qubes-issues/issues/10703


Let's play ! 
```
user@dom0:~$ qvm-ls |grep fedora.44
fedora-44-xfce                Halted   TemplateVM    black   -                         -
test-fedora44                 Running  AppVM         red     fedora-44-xfce            sys-firewall
```

---

## Preloaded dispoables in 4.3

> 板块: Testing Team

I've had reports of issues with the preloaded disposables in 4.3, which
agree with my own experience.

I thought this would be a great new feature, but something seems off.
I find that the time saving is marginal, and if I start a number of
disposables quickly, the load time is actually *slower* than under 4.2.

I see that this is on GitHub as a possibility, but it's a regular
feature for me and some other users. Does anyone else see this behavior?
I'd like to get a feeling for incidence before going to GitHub.

---

## Debian 13 templates available for testing

> 板块: Testing Team

Dear Qubes testers,

Debian 13 templates (including standard, [minimal](https://doc.qubes-os.org/en/latest/user/templates/minimal-templates.html), and [Xfce](https://doc.qubes-os.org/en/latest/user/templates/xfce-templates.html) versions) for Qubes OS 4.2 and 4.3 are now available for testing in the `qubes-templates-itl-testing` repositories for [4.2](https://yum.qubes-os.org/r4.2/templates-itl-testing/rpm/) and [4.3](https://yum.qubes-os.org/r4.3/templates-itl-testing/rpm/), respectively. Here’s the associated issue:

https://github.com/QubesOS/qubes-issues/issues/8841

Your feedback will be invaluable in helping us determine whether there any bugs that need to be fixed before the stable release of this template. For more information about how to test and provide feedback, please see:

https://doc.qubes-os.org/en/latest/user/downloading-installing-upgrading/testing.html

---

## Dev: code-signing policy failed

> 板块: Testing Team

Very often when I do pull requests, my PRs fail the code-signing policy, but not always...

Last example : [qubes-builder-gentoo PR#12](https://github.com/QubesOS/qubes-builder-gentoo/pull/12), see the code-signing failed check.

Is another contributor can help me to understand what I do bad? Thanks.

---

## Dev : Using Qubes Builder v2

> 板块: Testing Team

# First guide : how to build your first package with Qubes Builder v2
This guide will help you to build your first packages with Qubes Builder v2.

## Context

Three years ago I used [Qubes Builder v1](https://github.com/QubesOS/qubes-doc/blob/master/developer/building/qubes-builder.md) regularly for building ArchLinux/Fedora/Debian packages.
Then Qubes Builder v2 replaced it, and I tried using it four or five times by following the [qubes-builderv2 README](https://github.com/QubesOS/qubes-builderv2/blob/main/README.md). And each time it failed with errors I couldn't solve without a very large investment.
Last week, the need to use the Qubes Builder v2 becomes more important for me while trying to solve a Gentoo template issue. Then I found the [Qubes Builder v2 dev guide (qubes-builder-v2)](https://doc.qubes-os.org/en/latest/developer/building/qubes-builder-v2.html) which is much simpler for a first usage. By following this guide I found some minor inaccuracies, so I write two simple scripts to automate the building of the required qubes. My main goal was to re-create easily this environment.

## What we will do?
We will :
1. create a template (**tpl-f42-builder**) with the required dependencies. 
2. create an app qube (**qbuilder**) used to build the packages from the source (git clone)
3. build two first `core-admin-client` packages for dom0

## Create the tpl-f42-builder template

Rewrite or copy the `create_builder_template.sh` [script](https://github.com/lubellier/qubes-recipes/blob/main/create_builder_template.sh) to dom0:
```bash
#! /bin/bash
# create $VM as the qubes-builder template
# qubes-builderv2, based on Augsch123's salt recipe (8774 issue)
set -o errexit
set -o nounset

TPL=fedora-42-xfce
VM=tpl-f42-builder-$(date +"%N")

qvm-clone $TPL $VM
# dependencies-fedora.txt
qvm-run --pass-io --no-gui $VM 'sudo dnf -y install asciidoc createrepo_c devscripts docker gpg m4 mock openssl pacman podman python3-click python3-docker python3-jinja2-cli python3-lxml python3-packaging python3-pathspec python3-podman python3-pyyaml rb_libtorrent-examples reprepro rpm rpm-sign rsync sequoia-chameleon-gnupg sequoia-sq sequoia-sqv tree'
# dependencies-fedora-qubes-executor.txt
qvm-run --pass-io --no-gui $VM 'sudo dnf -y install createrepo_c debootstrap devscripts dnf-plugins-core dpkg-dev git mock pbuilder perl-Digest-MD5 perl-Digest-SHA pykickstart python3-debian python3-pyyaml python3-sh reprepro rpm-build rpmdevtools systemd-udev wget which'

# Init docker env
qvm-run --pass-io --no-gui $VM 'sudo usermod -aG docker user'
qvm-shutdown --wait $VM
qvm-run --pass-io --no-gui $VM 'docker ps'

echo $VM created
qvm-shutdown $VM
echo $VM stopped
```
Steps:
 - replace the `TPL` variable value with your reference fedora template
 - execute the script
 - rename the `tpl-f42-builder-xxxxxx` template to `tpl-f42-builder`

## Create the qbuilder app qube

Rewrite or copy the `create_builder_qube.sh` [script](https://github.com/lubellier/qubes-recipes/blob/main/create_builder_qube.sh) to dom0:
```bash
#! /bin/bash
# create $VM as a builderv2 qube
# qbuilder v2, based on www.qubes-os.org/doc/qubes-builder-v2/
set -o errexit
set -o nounset

VM=qbuilder-$(date +"%N")
TPL=tpl-f42-builder

qvm-create $VM --class=AppVM --label=red --template=$TPL --prop=memory=600 --prop=maxmem=6000 
qvm-volume resize $VM:private 60GB
# persistent docker directory
qvm-run --pass-io --no-gui $VM 'sudo mkdir /rw/config/qubes-bind-dirs.d; echo "binds=( '/var/lib/docker' )" | sudo tee /rw/config/qubes-bind-dirs.d/docker.conf'
qvm-shutdown --wait $VM
sleep 2
qvm-start $VM
# qubes-builderv2 repo
qvm-run --pass-io --no-gui $VM 'cd /home/user ; git clone https://github.com/QubesOS/qubes-builderv2'
qvm-run --pass-io --no-gui $VM 'cd /home/user/qubes-builderv2 ; git submodule update --init'
# verify docker with an example
qvm-run --pass-io --no-gui $VM 'docker run hello-world'
qvm-shutdown --wait $VM
sleep 2
qvm-start $VM
# validate /var/lib/docker persistence
qvm-run --pass-io --no-gui $VM 'docker images'

echo $VM created
```
Steps:
 - execute the script
 - rename the `qbuilder-xxxxxxx`  app qube to `qbuilder`

## Build a package
For the next, follow the [qubes-builder-v2](https://www.qubes-os.org/doc/qubes-builder-v2/) guide:
- Open a terminal in `qbuilder`, then 
```bash
cd qubes-builderv2/
tools/generate-container-image.sh docker
```
- `tools/generate-container-image.sh docker` will create a **qubes-builder-fedora** docker image. This is your Qubes builder executor (fetch, build the packages). The `docker images` command should list it.
- Create the `builder.yml` configuration file, from the [*Configuration* section](https://doc.qubes-os.org/en/latest/developer/building/qubes-builder-v2.html#configuration) of qubes-builder-v2. This YAML file configures the above **qubes-builder-fedora** docker as an executor
- Build your first packages
```bash
./qb -c core-admin-client -d host-fc37 package fetch prep build
```
Your built packages for dom0 (`host-fc37`) are  : 
```bash
[user@qbuilder qubes-builderv2]$ ls -lh artifacts/components/core-admin-client/4.2.17-1.1/host-fc37/build/rpm/*.noarch.rpm 
-rw-rw-r--. 2 user user 631K Jul 22 22:38 artifacts/components/core-admin-client/4.2.17-1.1/host-fc37/build/rpm/python3-qubesadmin-4.2.17-1.1.fc37.noarch.rpm
-rw-rw-r--. 2 user user  72K Jul 22 22:38 artifacts/components/core-admin-client/4.2.17-1.1/host-fc37/build/rpm/qubes-core-admin-client-4.2.17-1.1.fc37.noarch.rpm
``` 

## What's next ?

Now you will be able to build the Qubes OS packages/templates/iso, so you can more easily test contributor PRs, fix Qubes OS issues or test your new features, then do Pull Requests to the official git repositories.

Resources : 

- Read the [8774 issue](https://github.com/QubesOS/qubes-issues/issues/8774#issuecomment-1867854489) with the Augsch123's Salt formulas
- Read the [qubes-builderv2 README](https://github.com/QubesOS/qubes-builderv2/blob/main/README.md)
- Read the recipe examples in the QubesOS git repositories (`.qubesbuilder`, CI `.gitlab-ci.yml`)
- Read the [qb](https://github.com/QubesOS/qubes-builderv2/blob/main/README.md#cli) documentation
- Try the other executors (disposable, podman, local, windows, ...)

---

## Fedora 42 templates available for testing

> 板块: Testing Team

Dear Qubes testers,

Fedora 42 templates (including standard, [minimal](https://www.qubes-os.org/doc/templates/minimal/), and [Xfce](https://www.qubes-os.org/doc/templates/xfce/) versions) for Qubes OS 4.2 and 4.3 are now available for testing in the `qubes-templates-itl-testing` repositories for [4.2](https://yum.qubes-os.org/r4.2/templates-itl-testing/rpm/) and [4.3](https://yum.qubes-os.org/r4.3/templates-itl-testing/rpm/), respectively. Here's the associated issue:

https://github.com/QubesOS/qubes-issues/issues/9807

Your feedback will be invaluable in helping us determine whether there any bugs that need to be fixed before the stable release of this template. For more information about how to test and provide feedback, please see:

https://www.qubes-os.org/doc/testing/

---

## Kicksecure Template for Qubes - Testers Wanted!

> 板块: Testing Team

Posted by @adrelanos in the [Kicksecure Forums](https://forums.kicksecure.com/):

https://forums.kicksecure.com/t/kicksecure-template-for-qubes-testers-wanted/1020

---

## Qubes-R4.2.4-rc1-x86_64 fails on DELL T7500, kernel panic, wired floppy seek on grub

> 板块: Testing Team

Hi, 

I took an old T7500 from DELL which should be able to run qubes and found wired behavior. I need to to verify the usb stick, but as dd did not throw write errors the writing should have been correct.
I said sync after dd and waited for the root prompt again #

What happened?
After long time wait for huge ecc ram to be initialized the machine booted from usb stick and started grub. Here I got a floppy seek (!) two times and an error about two missing files.
![IMG_20250208_211616|375x500](upload://eMj6MpH4Lv43yLudiKMjlptytjn.jpeg)

missing files:
![IMG_20250208_211651|666x500](upload://e8sAeCeRqta0oY5XlzjM1TJfYY8.jpeg)
looking for trouble:
![IMG_20250208_211705|666x500](upload://6CBM0EStZ0xusLMJGexxyJ8AG9I.jpeg)

Long time with black screen and fat blinking _ cursor, then cursor disappeared and re-appeared.
Then black screen with fat blinking _ cursor.

Badumm Tss. Kernel Panic. 

As this panic is only displayed shortly I had to rush to take the photo, it does not look good but it is readable. A problem with XEN as it seems to me.

![IMG_20250208_211841|666x500](upload://sc2wVn7i0TO17rBiuieQUIAQMEH.jpeg)

The machine rebooted quickly after displaying the panic.

@developers:
What about printf- / echo logging to line printer or rs232?

What about writing out numbers or text at the time when only the cursor can be seen.
I guess this is all XEN trying to do something.

Checks to be done, (but will not help much):
I need to run older qubes, memtest86 on the machine, also I need to verify the stick for errors.

Is there ioport 80 debugging sent while early booting? Need to grab a port 80 board somewhere.


Update:
looking for xen issues with the processor arch and ICH10 I only found this very old post.
https://lists.xen.org/archives/html/xen-devel/2011-08/msg00893.html

---

## Fedora 40 templates available for testing

> 板块: Testing Team

Dear Qubes testers,

Fedora 40 templates (including standard, [minimal](https://www.qubes-os.org/doc/templates/minimal/), and [Xfce](https://www.qubes-os.org/doc/templates/xfce/) versions) for Qubes 4.2 are now available for testing in the [`qubes-templates-itl-testing`](https://yum.qubes-os.org/r4.2/templates-itl-testing/rpm/) repository. Here is the associated issue:

https://github.com/QubesOS/qubes-issues/issues/8915

Your feedback will be invaluable in helping us determine whether there any bugs that need to be fixed before the stable release of this template. For more information about how to test and provide feedback, please see:

https://www.qubes-os.org/doc/testing/

(Note: Fedora 40 templates will not be available for Qubes 4.1.)

---

## Xen hypervisor allocated kernel memory conflicts with E820

> 板块: Testing Team

Hello, in order to solve https://github.com/QubesOS/qubes-issues/issues/8791 (issue that I have since months too) we found a solution at https://github.com/QubesOS/qubes-linux-kernel/pull/888 and I've built a dedicated ISO with it for kernel-latest https://qubes.notset.fr/iso-testing/Qubes-202401192112-x86_64.iso. As it changes general values and may have an impact for several motherboards, any help would be appreciated by just testing if installer with kernel-latest boots.

---

## Migration dom0 audio from pulseaudio to pipewire available for testing

> 板块: Testing Team

Recent updates include a migrating audio in dom0 from pulseaudio to pipewire. It should improve audio quality, especially for qubes already using pipewire too (all Fedora, and newer Debian). Related issue: https://github.com/QubesOS/qubes-issues/issues/8955. In theory the switch should be seamless and everything should remain working as it was, 
but since it's rather drastic change it needs some more testing.

The switch is implemented in `qubes-dom0-update` command that is in current-testing repository for now. Running a normal update with the updated command should switch to pipewire the first time it's called. But it's also possible to switch back and forth manually:
- `qubes-dom0-update --switch-audio-server-to=pipewire`
- `qubes-dom0-update --switch-audio-server-to=pulseaudio`

In theory it should automatically restart relevant services and no extra action should be needed, but in practice it may sometimes require either restarting some qubes or logging out of dom0 and logging back in.

Please check if audio (playing, recording etc) works correctly after the switch.

---

## Fedora 39 templates available for testing

> 板块: Testing Team

Dear Qubes testers,

Fedora 39 templates for Qubes 4.1 and 4.2 are now available for testing in the `qubes-templates-itl-testing` repository. Here is the associated issue:

https://github.com/QubesOS/qubes-issues/issues/8499

Your feedback will be invaluable in helping us determine whether there any bugs that need to be fixed before the stable release of this template. For more information about how to test and provide feedback, please see:

https://www.qubes-os.org/doc/testing/

---

## Bees and brtfs deduplication

> 板块: Testing Team

I tried to build qubes to have it build qubes 4.2 and integrate bees spec file of opensuse tumbleweed but was unsuccessful just building qubes from qubes-builder last month.


It was failing at get sources step with issues with fetchrd commit from a submodule.. Anyone here was successful recently?

I guess i could try only to build fedora-37 template and bees there. Poking here in advance to augment my chances of success! 

Thanks

---

## 4k sector testing

> 板块: Testing Team

Any specific peculiar manual setup needed or cryptsetup now does the right thing? Brtfs is well aligned out of the box? Some status updates?

Edit: changed name of post: there is no such thing as 4k templates under itel testing repo. Bad bing

---

## What to test? Where to get what to test? Where to report testing results?

> 板块: Testing Team

Quoting myself here to open discussion:

[quote="Insurgo, post:34, topic:13585, full:true"]
[quote="Insurgo, post:33, topic:13585"]
Otherwise who tests what, really?
[/quote]

@Demi don’t get me wrong on the tone here, but there were a lot of regressions on 4.1 as opposed to 4.0 stability experience.

My point here is that :

[quote="Demi, post:32, topic:13585"]
Merged already, will be in the next vmm-xen release.
[/quote]

Is not enough. I’m following [GitHub - QubesOS/updates-status: Track packages in testing repository](https://github.com/QubesOS/updates-status) as close as I can. And I see no vmm-xen to be tested, nor fixes for suspend/resume to be tested, with PR getting way too long to land even in unstable repo. I would expect things to be way more verbose under the testing section of this forum, and my guess is that there is a lot of confusion from even the willing testers to test something to be tested and if those things to be tested even reach willing testers.

How can we improve that should be discussed under the testing section, not here, but this subject will be a good quotation to justify testing discussions, which is why i’m writing it here. No blame or whatever here, but I see a lot of space for improvements through better communication and appropriate pointers.
[/quote]


So how do we improve this, taking suspend/resume pending PR and vmm-xen fixes for loopback performance issues as a first example to this?

Who are tracking and testing those PRs today?

---

## Whonix 17 available for testing in Qubes 4.2

> 板块: Testing Team

https://forums.whonix.org/t/qubes-whonix-17-for-qubes-r4-2-is-available-debian-12-bookworm-based-major-release-testers-wanted/16885

Thanks, @adrelanos!

---

## Debian 12 templates available for testing

> 板块: Testing Team

Dear Qubes Testers,

- The standard Debian 12 template is now available for testing  in Qubes 4.2 (see issue [#7134 ](https://github.com/QubesOS/qubes-issues/issues/7134)).

- The Debian 12 *minimal* template is not available for testing yet.

- The standard Debian 12 template still needs to be rebuilt for Qubes 4.1, since it was built before the official Debian 12 release. 

As usual, you can find the new template in the `qubes-templates-itl-testing` repository. As always, your feedback will be invaluable in helping us determine when to release the stable version of this template to the broader Qubes userbase and whether there any bugs that need to be fixed before that happens. For more information about testing and how to provide feedback, please see:

https://www.qubes-os.org/doc/testing/

---

## Updater stuck at 99% (whonix didn't finish update and blocked updater)

> 板块: Testing Team

Continuing the discussion from [[R4.2] whonix-gw-16 update failed](https://forum.qubes-os.org/t/r4-2-whonix-gw-16-update-failed/18360):

I'm not sure if it's related, but for me the updater is stuck at 100% on the whonix-ws. So I'm not sure if it's a whonix bug or an updater one. It kind of feels like an updater one just because a faulty template should be handled gracefully by the updater. Anyone experiencing this?

![update|464x500](upload://9ffVhmOxx7pyNOkEgkmQjOcJmPM.png)

This was from a freshly installed Qubes 4.2 rc1.

---

## [R4.2] whonix-gw-16 update failed

> 板块: Testing Team

There are multiple issues here.
1. Installing using the iso from http://qubes.notset.fr/iso/Qubes-4.2.202304291601-x86_64.iso,  I'm having trouble upgrading whonix-gw and whonix-ws. The error messages are like "500 unable to reach tinyproxy 127.0.0.1:8082". Reinstalling `qubes-template-whonix-gw-16-4.1.0-202303181802.noarch.rpm` didn't solve this. So I think there's probably something wrong with this template.

2. Restoring a whonix-gw-16 from R4.1 solved the above problem. However, the backup tool didn't make necessary changes to `/etc/apt/sources.list.d/qubes-r4.list`. For other templates, the shifting of R4.1 repos to R4.2 repos happened automatically. But it's not the case for whonix. I managed to manually editing `qubes-r4.list` and copying the keyring file to make apt happy.

Hoping these problems can get solved.

---

## [R4.2] debian-11-minimal templates gui agent crash

> 板块: Testing Team

If I upgrade the following packages in my debian-11-minimal template, the `qubes-gui-agent` systemd service will fail to start on next boot.
```
qubes-gui-agent 4.2.2-1+deb11u1 from 4.1.28-1+deb11u1
xserver-xorg-input-qubes 4.2.2-1+deb11u1 from 4.1.28-1+deb11u1
xserver-xorg-qubes-common 4.2.2-1+deb11u1 from 4.1.28-1+deb11u1
xserver-xorg-video-dummyqbs 4.2.2-1+deb11u1 from 4.1.28-1+deb11u1
```
Template: debian-11-minimal installed through qvm-template. No testing repo enabled.
Dom0: Testing repo enabled.

Logs are a bit hard to retrieve since there won't be any gui, but I'll try my best.

Systemctl status:

```
● qubes-gui-agent.service - Qubes GUI Agent
     Loaded: loaded (/lib/systemd/system/qubes-gui-agent.service; enabled; vendor preset: enabled)
     Active: failed (Result: exit-code) since Mon 2023-05-08 06:51:54 UTC; 19s ago
    Process: 461 ExecStartPre=/bin/sh -c /usr/lib/qubes/qubes-gui-agent-pre.sh (code=exited, status=0/SUCCESS)
    Process: 472 ExecStart=/usr/bin/qubes-gui $GUI_OPTS (code=exited, status=1/FAILURE)
   Main PID: 472 (code=exited, status=1/FAILURE)
        CPU: 136ms

May 08 06:51:52 debian-11-minimal systemd[1]: Started Qubes GUI Agent.
May 08 06:51:52 debian-11-minimal qubes-gui[472]: Waiting on /var/run/xf86-qubes-socket socket...
May 08 06:51:52 debian-11-minimal qubes-gui-runuser[489]: pam_unix(qubes-gui-agent:session): session opened for user user(uid=1000) by (uid=0)
May 08 06:51:53 debian-11-minimal qubes-gui[472]: Ok, somebody connected.
May 08 06:51:53 debian-11-minimal dbus-daemon[553]: [session uid=1000 pid=551] Activating service name='org.freedesktop.systemd1' requested by ':1.1' (uid=1000 pid=567 comm="systemctl --user show-environment ")
May 08 06:51:53 debian-11-minimal systemd[1]: qubes-gui-agent.service: Main process exited, code=exited, status=1/FAILURE
May 08 06:51:53 debian-11-minimal dbus-daemon[553]: [session uid=1000 pid=551] Activated service 'org.freedesktop.systemd1' failed: Process org.freedesktop.systemd1 exited with status 1
May 08 06:51:53 debian-11-minimal qubes-gui[472]: X connection to :0 broken (explicit kill or server shutdown).
May 08 06:51:54 debian-11-minimal qubes-gui-runuser[489]: pam_unix(qubes-gui-agent:session): session closed for user user
May 08 06:51:54 debian-11-minimal systemd[1]: qubes-gui-agent.service: Failed with result 'exit-code'.
```

---

## Development build - Graphics

> 板块: Testing Team

For people actively testing the developpement build of R4.2, do you have graphical instabilities and crash in dom0 ? 

Tested with a amd and nvidia card, with the nvidia card I don't even reach lightdm, and with the amd one, sometime it work, sometime I have graphical artifact in lightdm before it crash and restart the lightdm process. 
The funny part is: 
- In dom0, starting lightdm will most of the time result in a crash
Once you started your desktop environment: 
- Never any issue with graphical things for non-dom0 qubes
- In dom0, starting xterm never crash or have any kind of issues
- In dom0, starting xfce terminal ( or gnome terminal if you install it) will always result in a crash of the whole graphical interface and you go back to lightdm ( with crash ) 

Haven't tried to debug it yet. Will try to debug that at some point but now now ( Pretty confident it is a bug in one of the qubes component, that somehow impact the graphical drivers ) 

I just wanted to known if others testers have that kind of issue too :)

---

## Wrong autogenerated mount point

> 板块: Testing Team

I'm about to post one more bug in installation program: auto generated partitions may lead to error installing Linux firmware - you need to plan separate /boot/efi partition when you use dual boot (I use at least 3 OS booting ) and replace /boot/efi mount with your own partition prepared for use as efi . At least I have 3 efi partitions currently and it works. The bug, when triggered, is fatal - installation program allows only exit.

If this really matters I could upload the photo of partitioning triggering the bug. The problem, though, is easy - on /boot/efi I've Microsoft files & the space is not enough to store everything that Qubes OS wants to be there. Workaround is also simple - prepare the partition for /boot/efi as unformated and replace mount point after auto generating partitions.

---

## 4.1.2 testing upgrading issue (I wish to confirm)

> 板块: Testing Team

I've issues with upgrading via whonix VM. Looks like feature is broken. 
I've seen a post that upgrades via tor are broken due to tor gets looped kinda "connecting, we recommend to wait" forever. Looks like I'll have to upgrade via clear net at least once to get next update. :unamused:

My location has Tor network being well known as unstable (Russian Federation).

---

## Plans for Xen in Qubes 4.2?

> 板块: Testing Team

What version of Xen is the team aiming for 4.2?
What version of dom0 (Fedora) is the team aiming for 4.2? Well it looks like we got it going! But it’s Swiss cheese at the moment… just like core teams 5+ kernel lol!

---

## Xen + xmm-xen fixes to test (suspend/resume fixes, directio loopback devices, sys-usb fails to start, slowness vs bare metal)

> 板块: Testing Team

The issues
- https://github.com/QubesOS/qubes-issues/issues/7332 ( Use direct I/O for loop devices )
- https://github.com/QubesOS/qubes-issues/issues/6824 ( sys-usb sometimes fails to start )
- Some parts of https://github.com/QubesOS/qubes-issues/issues/7404 (clock problems, slowness vs bare metal operations) should be more efficient (kernel fixes for Fedora directly applied from dom0 upgrade to current-testing repo below)


Some of the issues above might be fixed with packages having landed under current-testing repos:
- Testing those packages should result from testers with at least a  :-1: :+1: the referred issue so that the packages are not deployed from current-testing to stable.
- If :-1: : Describing packages installed and telling what part of the issue is still present in those issues


```
dom0:
- sudo qubes-dom0-update --enablerepo=qubes-dom0-current-testing
[user@dom0 ~]$ sudo qubes-dom0-update --disablerepo=* --enablerepo=qubes-dom0-current-testing
Using sys-whonix as UpdateVM to download updates for Dom0; this may take some time...
Qubes OS Repository for Dom0                    3.9 MB/s |  88 kB     00:00    

kernel.x86_64                      1000:5.15.74-1.fc32.qubes   qubes-dom0-cached
kernel-qubes-vm.x86_64             1000:5.15.74-1.fc32.qubes   qubes-dom0-cached
linux-firmware.noarch              20220913-135.fc32           qubes-dom0-cached
linux-firmware-whence.noarch       20220913-135.fc32           qubes-dom0-cached
python3-qasync.noarch              0.23.0-2.fc32               qubes-dom0-cached
python3-xen.x86_64                 2001:4.14.5-9.fc32          qubes-dom0-cached
qubes-input-proxy.x86_64           1.0.28-1.fc32               qubes-dom0-cached
qubes-input-proxy-receiver.x86_64  1.0.28-1.fc32               qubes-dom0-cached
qubes-input-proxy-sender.x86_64    1.0.28-1.fc32               qubes-dom0-cached
xen.x86_64                         2001:4.14.5-9.fc32          qubes-dom0-cached
xen-hvm-stubdom-linux.x86_64       1.2.5-1.fc32                qubes-dom0-cached
xen-hvm-stubdom-linux-full.x86_64  1.2.5-1.fc32                qubes-dom0-cached
xen-hypervisor.x86_64              2001:4.14.5-9.fc32          qubes-dom0-cached
xen-libs.x86_64                    2001:4.14.5-9.fc32          qubes-dom0-cached
xen-licenses.x86_64                2001:4.14.5-9.fc32          qubes-dom0-cached
xen-runtime.x86_64                 2001:4.14.5-9.fc32          qubes-dom0-cached
xfwm4.x86_64                       1000:4.14.2-3.fc32          qubes-dom0-cached
zlib.x86_64                        1.2.12-5.fc32               qubes-dom0-cached
Qubes OS Repository for Dom0                    2.9 MB/s | 3.0 kB     00:00    
Dependencies resolved.
================================================================================
 Package               Arch   Version                   Repository         Size
================================================================================
Installing:
 kernel                x86_64 1000:5.15.74-1.fc32.qubes qubes-dom0-cached  69 M
 kernel-qubes-vm       x86_64 1000:5.15.74-1.fc32.qubes qubes-dom0-cached 102 M
Upgrading:
 linux-firmware        noarch 20220913-135.fc32         qubes-dom0-cached 107 M
 linux-firmware-whence noarch 20220913-135.fc32         qubes-dom0-cached  31 k
 python3-qasync        noarch 0.23.0-2.fc32             qubes-dom0-cached  32 k
 python3-xen           x86_64 2001:4.14.5-9.fc32        qubes-dom0-cached  60 k
 qubes-input-proxy     x86_64 1.0.28-1.fc32             qubes-dom0-cached  21 k
 qubes-input-proxy-receiver
                       x86_64 1.0.28-1.fc32             qubes-dom0-cached  17 k
 qubes-input-proxy-sender
                       x86_64 1.0.28-1.fc32             qubes-dom0-cached  17 k
 xen                   x86_64 2001:4.14.5-9.fc32        qubes-dom0-cached  20 k
 xen-hvm-stubdom-linux x86_64 1.2.5-1.fc32              qubes-dom0-cached  11 M
 xen-hvm-stubdom-linux-full
                       x86_64 1.2.5-1.fc32              qubes-dom0-cached  12 M
 xen-hypervisor        x86_64 2001:4.14.5-9.fc32        qubes-dom0-cached 7.8 M
 xen-libs              x86_64 2001:4.14.5-9.fc32        qubes-dom0-cached 626 k
 xen-licenses          x86_64 2001:4.14.5-9.fc32        qubes-dom0-cached  32 k
 xen-runtime           x86_64 2001:4.14.5-9.fc32        qubes-dom0-cached  19 M
 xfwm4                 x86_64 1000:4.14.2-3.fc32        qubes-dom0-cached 587 k
 zlib                  x86_64 1.2.12-5.fc32             qubes-dom0-cached  90 k
Removing:
 kernel                x86_64 1000:5.15.57-1.fc32.qubes @qubes-dom0-cached
                                                                          344 M
 kernel-qubes-vm       x86_64 1000:5.15.57-1.fc32.qubes @qubes-dom0-cached
                                                                          483 M

Transaction Summary
================================================================================
Install   2 Packages
Upgrade  16 Packages
Remove    2 Packages

Total size: 329 M
Is this ok [y/N]: y
```

Centos:
- apply same disablerepo, enablerepo runtime trick as applied for dom0.
 
Fedora:
- kernel-qubes-vm is downloaded from dom0 and used by default by fedora templates.

Debian bullseye/buster/bookworm: 
- to be written. Those repos are simply commented out and cannot be runtime applied as for Fedora/Centos

---

## Fedora 37 templates available for testing

> 板块: Testing Team

Dear Qubes Testers,

Fedora 37 templates are now available for testing (see issue [#7807](https://github.com/QubesOS/qubes-issues/issues/7807)). As usual, you can find them in the `qubes-templates-itl-testing` repository. As always, your feedback will be invaluable in helping us determine when to release the stable version of this template to the broader Qubes userbase and whether there any bugs that need to be fixed before that happens. For more information about testing and how to provide feedback, please see:

https://www.qubes-os.org/doc/testing/

---

## Some issues with 4.1.1 updates and kernel-latest

> 板块: Testing Team

I have reports of various issues with 4.1.1 and latest updates,
including kernel-latest(5.19.9-1)
These are issues with at least 5 reports:

1. Qubes running very hot - far hotter than 4.0 
2. Qubes running with increased RAM usage - for example, on x220/230 I had dom0 maxed
   at 1536M, service qubes at 3/400M, and could comfortably run 14+ qubes
   in 16GB RAM.
   Now I have had to push up dom0 allocation, push up per qube
   allocation, can run far fewer qubes without interruption, and regularly
   have qubes failing to start. I have reports from users who have not
   customised memory allocation
3. Random freezes and hard crashes - these have been reported in the
   Forum generally. Usually there is no relevant information in the
   logs.
4. Randomly qubes fail to start.  
5. Issues with sleep - sleep used to work flawlessly. If sys-net was
   left running, network connections were re-established and the Qubes
   network stack worked.
   Now, sys-net will reconnect, but downstream netvms become unusable.
   They provide no network access, and it is not possible to open a
   terminal using qvm-run xterm - the command just hangs.
   It is not possible to restart the qube - the logs contain only 
   "libvirtd: internal error: libxenlight failed to create new domain "

These issues affect machines with stock BIOS and coreboot, and some
certified machines.
I think that issue 5 is specific to kernel-latest.

I'd like to hear if you recognise any of these, and any thoughts on how
to proceed before raising issues at GitHub.

---

## Sys-usb 53% CPU usage if left open for more than 7 days

> 板块: Testing Team

Basically out of nowhere (it would seem), `sys-usb` and `sys-net` as a USB Qube seems to suddenly spike once it’s been left open after several days (7 days, I think….)

This is where it gets weird:
- Fans spin up all of a sudden and stay constantly on.
- Any USB HID devices “stutter” (the cursor moves around the screen, similar to watching a movie with dropped frames, that’s the best way I can describe it…) 
- `htop` in `sys-usb` says that everything is normal, and CPU usage is at 5%
- The process with the highest usage seems to be `qrexec-client`
- It should be noted that `systemd-journald` is the next-highest process
- `xl top` in dom0 says that CPU usage is ~50%
- After this happening a few times over the past couple of weeks, I got curious and left the machine on overnight this time, to see whether it would sort itself out. The fans were still continuously running at the same speed in the morning, with the same reported CPU usage. 
- `qvm-kill sys-usb; sleep 10; qvm-start sys-usb` seems to fix it (disposable VM)

Whilst I have already discovered a “fix” (a very hacky fix…), my intention is to assist in finding the part of the codebase that is causing this, to assist the devs. 

I’m happy to provide any machine info and/or logs (it is a testing machine, after all), but I honestly have no idea where to start….

---

## Qubes-remote-support - New features and support for Whonix 16

> 板块: Testing Team

I have forked the qubes-remote-support repo and have been playing around with it.

https://github.com/alzer89/qubes-remote-support

It’s got excellent potential. I could even see this in use in the corporate world, if it can become robust enough. 


**MY UPDATES**
- It now uses Whonix 16
- You can now specify the dom0 user name when you connect, as an argument (because not everyone names their dom0 user “user”)

**WHAT I’M WORKING ON**
- Adding extra features to the GTK (GUI) app
- Automating the process for setting up connections between dom0 and the VMs, so there’s less user interaction required to set up a connection (without compromising security, of course)
- Configuring the scripts to automatically use the Whonix templates installed on the machine, future-proofing it for versions beyond Whonix 16
- Potential for the secret words for authentication to be sent automatically by the script if the user chooses to do so (I haven’t determined the methods of sending yet, though….)


When it’s ready, I’d like to merge it. 

Anyone is welcome to comment, contribute, criticise, or otherwise interact with it. 

Let me know what you think!

---

## Fedora 36 templates available for testing

> 板块: Testing Team

Dear Qubes Testers,

Fedora 36 templates are now available for testing (see the comments on [#7342](https://github.com/QubesOS/qubes-issues/issues/7342)). As usual, you can find them in the `qubes-templates-itl-testing` repository. As always, your feedback will be invaluable in helping us determine when to release the stable version of this template to the broader Qubes userbase and whether there any bugs that need to be fixed before that happens. For more information about testing and how to provide feedback, please see:

https://www.qubes-os.org/doc/testing/

---

## I managed to make Firefox full-screen when it shouldn't have been able to

> 板块: Testing Team

I'm sorry for the lack of information, but I thought I'd better make a record of this.  

I'm not worried about any security issues on my own machine.  This post is purely about making this known, so that if it's actually a bug, it starts the process to getting it fixed.  

As far as I'm aware, this should not be able to happen...

**BACKGROUND:**
-  Full-screen is disabled on all of my machines

**STEPS TO RECREATE:**
-  I had Firefox open in a Qube (this forum, actually...)
-  I was holding my laptop with my thumb around the space bar, V, C, X, D, F, etc. keys
-  I can't remember exactly what keys I pressed (my thumb jiggled, and I think I might have pressed the Alt key and/or the Super key)
-  I looked up at the screen, and Firefox was full-screen ***and obscuring the XFCE panel***
-  I pressed F11 twice, and Firefox then went full-screen without obscuring the XFCE panel, as per the expected behaviour

**PARTICULARS:**
-  Qubes 4.1 
- `qubes-dom0-current-testing` branch
-  `fedora-34` template

If anyone needs any more information, I'll gladly provide it, but I don't really know what else I can provide that would be helpful...

---

## Fedora 35 templates available for testing (for both 4.0 and 4.1)

> 板块: Testing Team

Dear Qubes Testers,

Fedora 35 templates are now available for testing (see [#6969 ](https://github.com/QubesOS/qubes-issues/issues/6969)). As usual, you can find them in the `qubes-templates-itl-testing` repository for both Qubes 4.0 and 4.1. As always, your feedback will be invaluable in helping us determine when to release the stable version of this template to the broader Qubes userbase and whether there any bugs that need to be fixed before that happens. For more information about testing and how to provide feedback, please see:

https://www.qubes-os.org/doc/testing/

---

## Latest version of xen-hvm-stubdom-linux broke USB passthrough

> 板块: Testing Team

I upgraded xen-hvm-stubdom-linux on a vanilla install of Qubes 4.1, rebooted, and now USB passthrough does not work at all.  ```lsusb``` of dom0 shows no devices, and in sys-usb it only shows the hubs.  

Sorry.  I'm new to bug reporting, and don't know what exactly you need.  

What information/logs do you need from my machine?

---

## 4.1 -> 4.2 and 4.0 -> 4.1

> 板块: Testing Team

Is this the right time to move the category names up a version @unman?

---

## Sys-whonix tor control panel bug

> 板块: Testing Team

Qubes 4.1 

When I use 'custom bridges' & press accept the setting shown then for bridges is 'None'. Where should I report this as bug - for whonix project or for Qubes project on github?

How to reproduce:
Select Time Synchronisation Monitor in the Qubes system tray, choose in the menu appeared sys-whonix->Tor control panel , on opened 'Tor control panel' window choose configure, in 'Bridges type' choose 'Custom bridges', press 'Accept' . Now enter bridges received from tor project, press 'Accept'. The window shows Tor status connecting to Tor & then Tor is connected, but in user configuration part of the window the 'Bridges type' are shown as 'None' - this is a bug.

---

## Testing qvm-template 4.1.20

> 板块: Testing Team

# Context
The [#7133](https://github.com/QubesOS/qubes-issues/issues/7133) and [#7170](https://github.com/QubesOS/qubes-issues/issues/7170) tagged as solved for [qvm-template](https://www.qubes-os.org/doc/template-manager/). [Qubesos-bot](https://github.com/qubesos-bot) published the [core-admin-client v4.1.20 (r4.1)](https://github.com/QubesOS/updates-status/issues/2788) package for dom0.

# Installation
See [testing-repositories](https://www.qubes-os.org/doc/how-to-install-software-in-dom0/#testing-repositories), you should install the *qubes-core-admin-client* and *python3-qubesadmin* packages from the *current-testing* repository.

# Testing report

- :white_check_mark: `qvm-template repolist` displays the enabled repositories
- :white_check_mark: `qvm-template --enablerepo=qubes-templates-itl-testing list` lists the *debian-9* and *fedora-35* templates
- :white_check_mark: `qvm-template --enablerepo qubes-templates-community list` lists the *gentoo* and *whonix-16* templates
- :white_check_mark: `qvm-template --enablerepo qubes-templates-community-testing list` lists the *centos-8* and *kali* templates (and *gentoo-minimal*, *whonix-15* ...)
- :white_check_mark: `qvm-template --enablerepo qubes-templates-community-testing search centos` finds the *centos-8*, *centos-8-minimal* and *centos-8-xfce* templates. 
- :white_check_mark: `qvm-template --enablerepo qubes-templates-community-testing install centos-8` installs the *centos-8* template
- :white_check_mark: `qvm-template list --installed` lists the new installed template
- :white_check_mark: `qvm-template remove centos-8` removes the *centos-8* template
- :white_check_mark: the `qvm-template repolist --all` output matches the `grep -E "^\[" /etc/qubes/repo-templates/qubes-templates.repo` output

# Requested Feedback

Please test and give also a feedback.

---

## Reboots on upgrades?

> 板块: Testing Team

```
<[olli]> where can I make Dom0 upgrades to always prompt for reboot? I've my Qubes rebooted on upgrades at least two times w/o my explicit confirmation. That reboots are not very handy when talking about QA.
<godo> i am not aware of any kind of automated reboots on qubes
<[olli]> Then there's a bug I need to trace. I've used upgrade tool and my Qubes 4.0.3 has rebooted.
<[olli]> That is not always. But that's at least second time I'm using it.
<godo> i am not using the update tool in general, but automated reboots there would be ... unexpected.
<[olli]> I dislike, but accept auto-reboots if them're controlled by explicit user setting. 
<[olli]> Also this could matter:
<[olli]> I'm enabling updates for Qubes that are not marked for updates
<[olli]> Thus updates may come not in order.
```

Any comments? Should I dig it deeper or this is okay when Dom0 is marked for updates?

---

## 4.1-rc3: qube shutdown right after start: event lost, qvm-prefs changes require Qube Manager restart to apply

> 板块: Testing Team

Hello.

How to reproduce:
0. Change default timeouts:
in Dom0 terminal:
qubes-prefs default_qrexec_timeout 100
qubes-prefs default_shutdown_timeout 80

Step 0 is optional. I've same results after

qubes-prefs -D default_qrexec_timeout
qubes-prefs -D default_shutdown_timeout

1. Start firefox in 'personal' via main menu. 
What you see: the Qube Manager shows qube attempts start. Qube light is yellow. Qube light become green.
2. Via Qube Manager press Shutdown button when no firefox is running yet.
What you see: Qube Manager reports personal qube has started. The firefox starts, shutdown didn't happen. After default 60 seconds Qube Manager asks for killing qube. 
Expected (bug 1): firefox should not start , the shutdown of 'personal' should happen before firefox managed to start, or at least, right after start, firefox should be closed by shutdown.
Expected (bug 2): Qube Manager should ask about killing personal qube with message telling about 80 seconds. It asks about 80 seconds after Qube Manager manually restarted after step 0. I think it should renew qubes-prefs values w/o requirement to restart Qube Manager.

Reproducible: always reproducible.

Should I report these two bugs via github?

---

## Debian-11 templates available for 4.0

> 板块: Testing Team

There are Debian-11 and 11-minimal templates available in the
qubes-templates-itl-testing repository.

Please check that the bullseye template is a drop in replacement for
buster, and that all tools and processes work as expected, including the
Qubes Updater.
It would also be useful if you could clone a debian-10 and perform an in
place upgrade to bullseye, and confirm that full functionality is
present.

If you have time to test the minimal template, and its use as basis for
the various sys-qubes, that would be awesome.

Look forward to hearing from you, with any comments, good or bad.

---

## Cosmetic: some unicode fonts not found by grub

> 板块: Testing Team

I'm running 4.1 and this could be already fixed (then - just skip), but on boot grub reports:

error: file '/EFI/qubes/fonts/unicode.pf2' not found.

this is with grub2-*2.04-2*.x86_64 packages in Dom0.

It boots okay though. The unicode support in console is broken on fedora34 (at least I've got this on my non-Qubes laptop after upgrade to fedora-34 from 33, where I had correct unicode in console), so this grub issue may be an upstream problem also.

---

## 4.1-rc1: trouble updating fedora-34 template and a few other

> 板块: Testing Team

Didn't use 4.1 a few weeks. Having trouble updating now. 

Actually I don't remember what could be a reason for this, sorry, but now I can't update w/o hacks like enabling internet for template qube. The Updater shows that there are updates for fedora-34 template, but fails with exit status 20 when updating. Ends up with 'failed to return clean data' (fedora-34: retcode 126). 
And even when I enable internet for template vm (set sys-firewall as default network provider) - fedora-34 template doesn't update with 'dnf update' - instantly reproducible curl failure 'Recv failure: Connection reset by peer' when downloading metadata. I can walk to the failing fedora repository url from personal qube via firefox w/o connection resets. So another question appear - adding sys-firewall as network provider is not enough - I need to provide more changes to template for emergency updates, but where - firewall rules are set to allow all connections. 

Before that I used backup to restore a qube, but restore from backup should not touch the Dom0 - I 've used setting to restore only this qube. This backup story could be unrelated, sorry.


Also: the Net-VM qube shows that it should be restarted right after starting template qube it is based on.
I did not made any changes - just started template VM, but the Net-VM status in Qubes Manager shows a circle meaning that template has changes - is that the expected behavior?

And finally another problem - I've got Ctrl-Shift-V not working and can't find where the binding lies - it looks like I've bound it somewhere and forgot about it. Can't find the binding in  xfce4-keyboard-shortcuts and keyboard settings (via Dom0 menu) do not show this binding. 
Attempt to change Safe paste setting doesn't change it immediately:
'Q->Qubes Tools->Qubes Global Settings' opens a window with a lot of settings, including ability to change 'Secure paste' from Ctrl-Shift-V to Ctrl-Insert or Ctrl-Win-V. But changes to that setting do not affect behavior of these keys. Are these settings session bound and require logout and login again? Or reboot? If so - this should be noted inside the 'Qubes Global Settings' program itself.

Also I've got at least one immediate crashing-reboot (no stopping VMs and so on, just like someone pressed reset switch) after killing firewall-vm. And one more similar reset-like reboot when I can't prove that this is due to net-vm or firewall-vm manipulations.

Finally this seem to be easier to reinstall, especially when I know that rc2 is out.  If you need more technical details from this report - please ask quickly - I'm about to move to 4.1-rc2 today via full reinstall.

---

## Testing whonix-ws-16 and whonix-gw-16

> 板块: Testing Team

These became available recently for 4.0:
```
qubes-template-whonix-ws-16-4.0.6-202109061137
qubes-template-whonix-gw-16-4.0.6-202109061137
```

One issue so far: sys-whonix based on whonix-gw-16 doesn't work as an updatevm for `sudo qubes-dom0-update`:

```Curl error (6): Couldn't resolve host name [...] [Could not resolve host: mirrors.fedoraproject.org]```

---

## RC1 failed in initial setup: qvm-template install fedora-34

> 板块: Testing Team

Installed R4.1-RC1 from [the provided ISO](https://www.qubes-os.org/news/2021/10/11/qubes-4-1-rc1/)

Here's a screenshot:

![error|281x500](upload://se6b1u2D1pTDuSwMHVQAWjk8maL.jpeg)

Transcribing a bit of it here:
```python
['/usr/bin/qvm-template','install','--nogpgcheck','/var/lib/qubes/template-packages/qubes-template-fedora-34-4.0.6-202110081812.noarch.rpm'] failed:
stdout: ""

[...]

ERROR: Command ['qvm-template-postprocess', 'really','--no-installed-by-rpm','post-install','fedora-34','/var/tmp/tmplznv906y/var/lib/qubes/vm-templates/fedora-34'] returned non-zero exit status 1.
```

I chose the defaults in the initial setup. After clicking <kbd>OK</kbd> it did show up the usual qubes UI but only  fedora-34 was installed. No sys-net, no sys-vpn, etc.

Afterwards I repeated the whole process from the RC1 ISO and the same exact issue happened.

Lastly I decided to build the system myself and created the sys-firewall, sys-net, downloaded other templates and used it as normal.

Anyone else experiencing this?

---

## Testing 4.1 rc1

> 板块: Testing Team

I'm sure you will have seen the announcement of 4.1rc1

Now that we have a 4.1rc, it would be an excellent time to test the
following areas:
Installer - with template choice.
Upgrading - guide [here](https://www.qubes-os.org/doc/upgrade/4.1/)
Restoring 4.0 (and earlier) backups
General usability

Even if you don't want to upgrade your system, or you are already using
4.1, you can still help if you have an old drive, or a largish external
drive you could use.

Here are some areas to think about:

Installer:
selecting different language
alternative formats
custom installs
selection of templates

Upgrading:
In place upgrade - 
introducing a deliberate failure to the process at different stages
note the "known issues", and test them

Restore/Backup:
check backups with/without encryption in different languages
large backups
missing templates/netvms

I'm sure you can find other areas yourself.
We'll see a lot of comments here and at GitHub.

Exciting times.

---

## Using remote kvm for Qubes automated testing

> 板块: Testing Team

This post is going to be half advertisment (for a product I'm not selling) and half contribution offer. If you don't care about the ad then just scroll down

First the ad part.
Check out [PiKVM](https://pikvm.org/). PiKVM is an open source remote kvm that allows for full remote control of a pc on hardware level, it provides a virtual display, keyboard, mouse and cd drive to the controlled machine, has the ability to remotely press the power buttons (using an addon board connected to the front panel header). It's main use case is of course remote server management but the video latency is low enough that it can be reasonable used to control a desktop system. With an addition of an external kvm switch it can be used to control multiple devices (up to 16, depending on the switch used)

Now, why did I start with the ad? I happen to own a PiKVM and a 4 device switch, and have a few spare devices connected to it
As my contribution to the project I'd like to use those machines (and the remote management provided by PiKVM) to run Qubes automated tests. I know that Qubes already has an automation farm but these tests run in nested VMs under KVM instead of on real hardware therefore they're not completely representative of hardware anyone would actually run Qubes on. I'm already using one of the boxes to run Qubes 4.1 system-level tests and the whole setup works quite well aside from the fact that all virtual devices are provided over USB so the system cannot use disk encryption but that's not that big of a deal for test machines.
If necessary I can also provide a VPN connection to the PiKVM web interface in case somebody from the dev team needed remote access to any of the boxes.

Additionally, if someone much more skilled with Python than me were to integrate OpenQA with the PiKVM it would also be possible to run automated installation tests on real hardware instead of KVM. PiKVM already provides a raw video feed over vnc or webrtc and has pretty extensive rest api for cli control

---

## Testing Debian-11

> 板块: Testing Team

There will shortly be new builds for 4.1 of the Debian-11 template.
It would be really useful for 4.1 users to:
1. test the new template (I'll let you know once it is available), and
2. test the upgrade path from Debian-10.

The build for 4.0 is broken, so a new template wont be available for a
little while.
Until that is fixed, can you test the upgrade path from buster?

The upgrade instructions are at:
https://www.qubes-os.org/doc/template/debian/upgrade/

Please check that the bullseye template is a drop in replacement for
buster, and that all tools and processes work as expected, including the
Qubes Updater.

Look forward to hearing from you.

---

## Testing vmm-xen v4.14.2-2

> 板块: Testing Team

## Context

After the [QSB-070](https://forum.qubes-os.org/t/qsb-070-xen-issues-related-to-grant-tables-v2-and-iommu/5914) announce, I installed the dom0 xen packages from the *qubes-dom0-security-testing* repository.

Updates-status : [ vmm-xen v4.14.2-2 (r4.1) #2600](https://github.com/QubesOS/updates-status/issues/2600)

## Testing report

No installation issue and no detected issue after the dom0 reboot and a daily-like Qubes-OS usage.

Checks done:
- start/use/stop dom0
- start/use/stop domU
- read `xl dmesg` output

Xen packages after the installation:

```
$ rpm -qa ^xen*
xen-licenses-4.14.2-2.fc32.x86_64
xen-4.14.2-2.fc32.x86_64
xen-hvm-stubdom-legacy-4.13.0-1.fc32.x86_64
xen-runtime-4.14.2-2.fc32.x86_64
xen-hvm-stubdom-linux-full-1.2.0-1.fc32.x86_64
xen-hvm-stubdom-linux-1.2.0-1.fc32.x86_64
xen-hypervisor-4.14.2-2.fc32.x86_64
xen-libs-4.14.2-2.fc32.x86_64
```

## Requested Feedback

Please test and give also a feedback.

---

## 4.1 installer LVM partitioning - hard to customize, missing space

> 板块: Testing Team

* Using the qubes 4.1-beta installer, it is very difficult to add a standard ext4 partition to the end of the default LVM setup. Choosing Custom, if you try to resize down the existing LVM volumes it complains about requiring a mount point. Afterwards, you can't add a standard partition anyway. I could just be an LVM novice.
* In the `lvs` output of the installed system, vm-pool (676g) + root-pool (20g) + swap (4g) doesn't add up to the size of /dev/sda2 (800g). Is it normal to have 100g unaccounted for? This is the result of pre-making a standard partition at the end of the disk and letting the qubes installer automatically partition the remaining free space.

---

## Kernel 5.12 and up won't boot on my hw

> 板块: Testing Team

I have a ryzen 2700, vega56 reference video card, which work fine while using any kernel from the 5.10 or 5.11 range, yet when I try to boot from kernel 5.12, my monitors shut off shortly after entering LUKS pw. When I try to boot using kernel 5.13, I don't even get to the LUKS password entry 'form'. Anyone else experiencing this, or not?

 (I'm afraid I don't have any logs to offer, or photo's from the boot sequence loading info.)

---

## Dom0 Warnings Truncated with "..."

> 板块: Testing Team

As can be seen in the image, the dom0 warnings show:

![scr|424x129](upload://cXHN4Xk7ZXhSV9z23sg3eDt7NrA.png)

ASCII version (for plaintext people ;) ):

```
+-----------------------------------------------------------+
|    [qube image]   WARNING(test-inst-backedn: This VM...   |
|                   As a protection measure, the "overrid...|
|                   This message will only appear once p....|
+-----------------------------------------------------------+
```

I would expect the text to be a bit more readable in a security warning.

Also, do these kinds of posts fit here?

---

## Fedora-34-xfce AppVM has Screensaver and Lockscreen Enabled

> 板块: Testing Team

The following images show the lockscreen for the fedora-34-xfce-based AppVM. It shows as a maximised window (with borders) and then a dom0 warning telling us about the VM having tried to create a fullscreen element when not allowed ("As a protection measure, the "override...."

![scr2|690x494](upload://v4PbJV5U2LWCgb90Uy7KeuFvmkd.png)

Haven't found this yet on QubesIssues. Anyone having the same thing?

---

## Qubesd service not running on boot, cannot be started

> 板块: Testing Team

Clean install of 4.1 beta, with testing repos enabled.
I updated yesterday, and shut down.
Today the qubesd service isnt running - the task bar is pulsing as the
notification area isnt able to load the qui, cant start Qube Manager,
etc etc.
I cant start the service.
Any one else have similar experience?

---

## Installation questions

> 板块: Testing Team

1. Timezone
I don't recall the option to set timezone. Did this pass by without me noticing?

2. Language choice
Also, has anyone selected an input language other than US?
Were you surprised that the choice wasn't propagated to templates?

---

## Fedora 34 template available for testing (for both 4.0 and 4.1)

> 板块: Testing Team

Dear Qubes Testers,

The Fedora 34 template is now available for testing (see [#6568](https://github.com/QubesOS/qubes-issues/issues/6568)). As usual, you can find it in the qubes-templates-itl-testing repository for both Qubes 4.0 and 4.1. As always, your feedback will be invaluable in helping us determine when to release the stable version of this template to the broader Qubes userbase and whether there any bugs that need to be fixed before that happens. For more information about testing and how to provide feedback, please see:

https://www.qubes-os.org/doc/testing/

---

