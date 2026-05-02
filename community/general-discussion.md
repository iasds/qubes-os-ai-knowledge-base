# Qubes OS Forum — General Discussion

> 来源：https://forum.qubes-os.org
> 板块：General Discussion
> 爬取时间：2026-05-02 18:39

---

## Backup failure - why can't we copy-and-paste our passwords into the wizard?

> 板块: General Discussion

I am looking at the unhappy prospect of having lost several year's work. The last backup has a corrupted header or a bad password.

There has been a lot of chaos, but I am reasonably certain the backup passphrase I keep in my most recent keepass database is the one I have always used. 

I wonder if I simply typed in the the wrong passphase on this last backup? Consistently, twice, when making the backup, which is a very 'me' mistake to make, which is why I love a good password manager...

Which brings me to ask: why, during the Backup tool's wizard, why in god's name can't the passphrase be pasted in from a database? Surely its safer and more effective?

---

## Split GPG and split GPG2

> 板块: General Discussion

Can you explain the difference between Split GPG and Split GPG2? 
Why is version 1 still around even though version 2 exists? 

It seems version 1 is installed by default—should I uninstall version 1 before installing version 2?

---

## V4.3 with new Browsers?

> 板块: General Discussion

I thought v4.3 have as default Brave, and WaterFox as pre-installations. I still see FireFox?

---

## NPU uses as essentials?

> 板块: General Discussion

Does the future version of QubesOS will need NPU? for any uses?

---

## How does and should Qubes OS handle firmware bugs which cause cpuid and APIC id mismatch?

> 板块: General Discussion

This mismatch means when, just as a quick example, that CPU 2 has cpuid 0x0002 but APIC 0x0004.
The example was made up but this firmware bug happened to me after upgrading to 4.3 and then updating dom0 after the upgrade. My guess is it was a bios update which is the reason for this. And I don't know why the bios update wasn't in 4,2.
I'm a security researcher and have looked into this and here is my research. I could only go so far with the research because it requires more specialized engineers to do the rest. I used the disgusting Meta's AI model to help with my research.

This error doesn't seem to cause any problem which breaks the system. It seems it just causes additional delays for the most part. Probably because the system needs to do additional work to assign a core to VM because of the mismatch.

But as a security researcher I wondered if this is a security vulnerability, which could be exploited with a side channel attacks. How you ask? Ok I'll answer your question.
If a qube is assigned CPU 2, then because of APIC mismatch, it's interrupted and rescheduled to another qube instead.
This causes both qubes to use the same cpu core and potentially leaking data between them.

But after doing some searching, not googling, I found that this firmware bug is not new. And security researchers haven't published CVEs or theoretical attack papers about it. That makes me think this firmware bug is not an exploitable attack vector.

Now here is an interesting question that could help a lot of people:
Is it possible to create a generic solution which detects and corrects cpuid and APIC mismatches?
Or do these solutions have to be hardware-specific?

A generic solution seems reasonable necaise it's just necessary to change the APIC value to be equal to cpuid value. Of course, it's not simple because you would still need to know which APIC should be used by which cpu. But it seems possible but maybe it's not possible without knowing the motherboard.

But if it's possible then it's better because we only need to solve this problem one time.
Then all users, who end up with this firmware bug at some point, there are many different motherboards out there, and everything changes all the time, 2 years from now, 5 years, and so on. Or else we have to make this solution many times for each motherboard. And it's a difficult troubleshooting process for most users to go through. And they probably don't want to broadcast this kind of identifying information on the internet to solve it.

Another possibility is adding a troubleshooting page in the documentation for qubes os, about this firmware bug. And that page should have step by step instructions on how to correct it. That way, a generic solution is possible in a targeted and optional way.

---

## Is anonymity possible using Qubes OS without DarkNet?

> 板块: General Discussion

Hi wise people.

I got a situation here: 1. I need to test a web app for a client. 2. The test must be anonymous, or Blue Team won't take it seriously. 3. I cannot use the DarkNet because the app does not allow connections from DarkNet servers.

So, up until now, my best bad idea is to get a dropPhone, and go connecting at some random place using such phone's hotspot wifi.

What do you think of this? Am I way too stupid? Is there any technical fixes that may turn this into a mediocre idea? Is there a better, known way to do this?

So sorry if this sounds a bit offtopic, but I honestly think that it is not, that this is a situation that other people may get into.

Thanks in advance for any tips, hints, or discussion.

---

## Getting dom0 Out of Both the Network and IPC Data Paths on Bare Xen

> 板块: General Discussion

Continuing on some of the previous posts on our custom bare-bones xen build:

We've been running a bare Xen setup on Alpine Linux (no Qubes, no libvirt, just xl and shell scripts) and I wanted to share what it took to fully isolate dom0 from both the network forwarding path and the IPC data path. This is something Qubes partially achieves with sys-net as a driver domain, but to my knowledge, even Qubes still routes all qrexec traffic through dom0. We went further and got dom0 completely out of both paths and parked it into an isolated corner where it does nothing after boot time and never sees the light of day. 

Hopefully this is useful to others building Xen-based appliances or exploring what's actually possible with the Xen primitives.

## Starting point

Five VMs on Xen 4.19: dom0 (Alpine), a network driver domain (net-vm, PCI passthrough of the physical NIC), and three application VMs. The application VMs needed to talk to each other over IPC (Xen vchan) and needed network connectivity through the driver domain.

The problems:
1. All VM network traffic was transiting dom0 because dom0 was the default vif backend for every VM
2. All IPC traffic was transiting dom0 because the IPC daemon ran in dom0 and relayed every message between domains

Dom0 was seeing every packet and every IPC message. For a security sensitive workload, that's exactly what we dont want.

## Part 1: Getting dom0 out of the network path

### The mechanism

This is straight out of the Qubes playbook. Xen supports specifying which domain acts as the netback for a vif using `backend=<domain-name>` in the vif spec. I think Qubes has used this for years with sys-net? On bare Xen with xl, you just add it to the xl config:

```
vif = ["ip=10.0.5.103,backend=net-vm"]
```

That's it. The vif appears inside net-vm instead of dom0. Dom0 doesn't forward anything.

### What actually broke

The simple part was the config change. The hard parts were everything around it.

**vif-watcher xenstore paths:** We had a polling daemon in net-vm (similar to Qubes' vif-route-qubes) that watched for new vifs and configured routes. It read the IP from xenstore using the frontend path (`/local/domain/<domid>/device/vif/<devid>/ip`). When net-vm is the backend instead of the frontend's dom0, the xenstore permissions are different. Net-vm couldn't read the frontend domain's xenstore entries. We had to add a fallback to the backend path (`/local/domain/<net-vm-domid>/backend/vif/<domid>/<devid>/ip`).

**Hardcoded IP in vif-watcher:** The watcher was assigning dom0s IP to every vif it configured (it was originally written when only dom0's vif existed). When a new VM's vif appeared, net-vm would accidentally claim dom0's IP address, making dom0 unreachable

**Firewall rule cleanup:** The old FORWARD chain had blanket accept rules between eth0 (dom0's vif) and eth1 (physical NIC). These carried all the forwarded traffic. After moving vif backends to net-vm, those rules became obsolete and needed to be replaced with targeted rules for the direct vifs.

**Boot ordering:** Net-vm must be fully running before any VM that uses it as a backend is created. On our system, VMs boot sequentially from a shell script in dom0, so this was already the case. But if youre doing parallel VM creation, you need to be careful about this

### The result

After the changes, dom0's routing table had no entries for any application VM. Net-vm's routing table showed direct routes to each VM via their vif interfaces. The only traffic on dom0's vif to net-vm was dom0's own management traffic (which we later eliminated too by removing dom0s IP entirely).

## Part 2: Getting dom0 out of the IPC data path

This was the harder and more interesting part. Qubes' qrexec runs a daemon in dom0 that mediates every inter-VM service call. Even though the actual data transport is vchan (shared memory between two domains), the routing goes through dom0: source agent sends to dom0 daemon, daemon evaluates policy and forwards to target agent. Dom0 sees every byte of IPC payload in the daemon's process memory.

We built a system that starts with dom0 as the relay (like qrexec) and then migrates to direct peer-to-peer vchan connections.

### How vchan works under the hood

The Xen vchan API (libxenvchan) is surprisingly flexible:
- `libxenvchan_server_init(remote_domain, xenstore_path)` creates a server endpoint. It writes rendezvous data to xenstore and waits for a client. The server domain must have write access to the xenstore path.
- `libxenvchan_client_init(remote_domain, xenstore_path)` connects to an existing server by reading the xenstore path.
- Each vchan handle has its own fd from `libxenvchan_fd_for_select()`, so you can poll multiple vchans in one process.
- There is NO global state. A single process can hold arbitrarily many server and client vchan handles.

The big insight: **vchan is symmetric between any two domains**. There is nothing in the libxenvchan API that requires dom0 to be involved. Any domU can be a vchan server, and any other domU can be a client. The constraint is xenstore permissions, not the vchan mechanism itself. As we will see later however, this configuration only works on static systems where every domU/appVM is known at boot time. We are not aware of a method to dynamically provision inter-guest IPC without dom0 involved in some way.

### The xenstore permission problem

When domU A wants to create a VchanServer for domU B, it writes the rendezvous under its own xenstore subtree (`/local/domain/<A>/ipc/direct/<B>`). Domain A owns this path and can write to it. But domain B needs read access to connect. By default, B can't read A's xenstore entries.

The solution: dom0 pre-provisions the xenstore permissions at boot. After creating all VMs, dom0's autostart script writes the rendezvous paths and grants the appropriate read permissions:

```sh
# sa-vm (domid 2) serves workload-vm (domid 3)
xenstore-write /local/domain/2/ipc/direct/3 ""
xenstore-chmod /local/domain/2/ipc/direct/3 b2 r3
```

Dom0 has write access to everything in xenstore, so it can set up the permissions for any pair. After this, the two domains can establish a vchan directly without any further dom0 involvement.

### Domain ID resolution

We hit an interesting problem with domain IDs. Xen assigns domain IDs at creation time and they increment monotonically. If you hardcode IDs in kernel cmdline parameters, they break if a VM is recreated or boot order changes.

Our solution: dom0 writes a name-to-domid mapping in xenstore after all VMs are created:

```sh
for vm in sa-vm workload-vm mgmt-vm; do
    domid=$(xl list | awk "/$vm/{print \$2}")
    xenstore-write /ipc/domain-map/$vm "$domid"
done
```

Each agent reads this mapping at startup to resolve peer names to domain IDs. The kernel cmdline only contains peer names:

```
extra = "console=hvc0 rdinit=/sbin/init ipc_serve=workload-vm,mgmt-vm ipc_connect=sa-vm"
```


### Policy evaluation

With dom0 out of the data path, someone still needs to enforce access control. We moved policy evaluation to the target domain's agent. Each serving domain has a baked-in policy file (subset of the central policy scoped to its own services). When a ServiceRequest arrives on a direct vchan, the agent checks the source domain name (Xen guarantees the remote domain ID in the vchan setup) against the local policy.

This is actually a smaller attack surface than centralized policy in dom0. Each domain only knows about its own authorized callers, not the entire system's policy. However, we still have open questions about whether an untrusted domU can securely manage it's own policy. This is a sharp-edge where dom0 actually provides some level of security.

### The result

After the full migration:
- Dom0 runs zero IPC processes at runtime. No daemon, no agent relay.
- Four direct vchan pairs carry all IPC traffic.
- Dom0's only boot-time roles: create VMs, write xenstore permissions, start agents. Then it's done.
- A dom0 compromise would require actively exploiting Xen grant table mechanisms to interfere with vchan. It can't just read the daemon's process memory because there is no daemon.

## What the Xen primitives actually support vs. what people think

Most Xen documentation and tutorials assume dom0 is a permanent, active participant in everything. It manages networking, it relays communications, it serves as the backend for all virtual devices. But the actual Xen API doesn't require any of this:

- vif backends can be any domain (the `backend=` directive)
- vchan works between any two domains (no dom0 mediation needed)
- xenstore permissions can be pre-provisioned (dom0 sets them at boot and leaves)
- grant tables are peer-to-peer (dom0 doesn't intermediate shared memory)

The Qubes project figured out the network piece years ago with sys-net as a driver domain. 

## Practical considerations

**Boot ordering matters.** The server domain for a vchan must be running and have its VchanServer created before the client domain tries to connect. We solved this with a retry loop in the client agent (10 seconds of retries at 500ms intervals for xenstore resolution).

**The agent's event loop needs to handle multiple fds.** Each vchan has its own event channel fd. Use `poll(2)` with all peer fds plus the local Unix socket for client connections. The existing Xen IPC daemon already does this (it polls N vchan server fds), so the pattern is proven.

**Test with throwaway VMs first.** We created two 64MB test VMs to prove the direct vchan path before touching any production VM. Found and fixed several issues (missing xenstore tools in the rootfs, domain ID hardcoding, missing `--no-daemon` flag) that would have been painful to debug on production VMs.

**Silent failures will hurt you.** The biggest time sink was things failing silently: curl fetches without `-f` that wrote HTTP error pages into binary files, OpenRC reporting `[ ok ]` for processes that crash 100ms after fork, missing shared libraries that only surface in logs you can't easily access inside a VM. Add build-time assertions (does the binary exist? can ldd resolve all libraries?) and loud runtime failures (check for xenstore-read on PATH before trying to use it).

## Summary

Dom0 on Xen is conventionally the center of everything: networking, IPC, device management, storage. But the Xen primitives don't actually require this. With vif backend reassignment and direct peer-to-peer vchan, you can reduce dom0 to a boot-time orchestrator that creates VMs, sets up xenstore permissions, and then does nothing. Every packet and every IPC message flows directly between the domains that need to communicate, with dom0 completely out of the path.

The Qubes architecture documents were our starting point, and the Xen wiki Driver Domain page documents the vif mechanism. The direct vchan piece doesn't seem to be documented anywhere, so hopefully this writeup fills that gap.

---

## Devuan Linux Template (non-official) available for testing

> 板块: General Discussion

inspired by this post https://forum.qubes-os.org/t/alpine-linux-template-non-official-available-for-testing/20595

This devuan template is in the **experimental stage and is unstable**. Please use it only for testing and non-critical activities.

My low development ability may lead to the construction of the template is not very good. Welcome anyone to help🙏

Built devuan template is similar to debian-13-minimal including a minimal X + alacritty and xterm with **openrc init**.

Default user and root passwd : devuan

https://codeberg.org/waterfish/allinone/releases

---

## Getting an app vm to access my home network – QUBES 4.3

> 板块: General Discussion

So, first of all, networking is not my strong point.  

I have a home network that has two networked media tanks (things to store tv shows and movies on) and a small home server.  I primarily use a windows pc to transfer things that I download (to the media tanks) and things to and from my server.  In reality the majority of this is handled by windows but there are times when a linux pc will want to go to the server for example.
I’ve always been able to get non-qubes linux pcs working but, despite many requests on linux forums and here I think, I have never received any instructions with regard to qubes that has worked.
What I want is to be able to do is access the home network from an app vm in qubes.   
So, after cleanly installing qubes 4.3 I was just noodling around getting used to the newer gui etc and wondered if AI could help with my long standing quest to network a qube.  Well, the answer is yes.  It provided me with a very simple solution that works.  This is what I did:
1.	 Create a new app vm based on fedora that I called ‘home network’.  Pretty innovative right there!
2.	I used the default settings that the qube was set up with (sys-firewall by default etc).  AI gives a long winded explanation about how qubes networks etc but in the end the default settings were spot on.
3.	In the fedora template I installed:
4. 
**sudo dnf install gvfs gvfs-smb*

*sudo dnf install samba-client cifs-utils**

5.	Shut the template down, restart and then restart ‘home network’.
6.	Use samba (smb://etc) to connect to all of my devices (Thunar).
It was as simple as that.  Because the devices are not switched on all of the time I just bookmarked the shares' addresses in Thunar and now they are accessible when they are on.  

This problem has literally bugged me for years.  I’m sure that some of the solutions that I have been offered in this time may have worked but were beyond my skill and understanding level so I couldn’t do it.  The above has to be probably the most elegant solution I can imagine.  Simple, easy to do and it works!

I’m also sure that some people will see this as someone (me) who couldn’t put two and two together from my previous successful linux networking, which may be true, but there may be others like me that struggle with networking.

I’m posting this just in case someone else is in the same boat and struggling to make this work.  And with 4.3 just being released its topical for now.

---

## KDE - changing the way you use Qubes

> 板块: General Discussion

I think KDE is a great match for Qubes, and makes the whole user
experience better.

KDE has a simple menu editor, that helps you to focus on the important
things - grouping qubes, ordering shortcuts, and so on.
There are simple tools to control (and master) many windows from
multiple qubes, and to quickly get to the window you want.

You can also use Activities - a way of making each desktop a separate
workspace, with its own wallpaper, widgets and launchers.
You can force windows from particular qubes to appear in distinct
activities. This helps to keep qubes separate as you want, and reduces
the risk of transferring data between the wrong qubes.

KDE is easy to control from the keyboard, and almost every aspect of
Qubes use can be dealt with, or automated.

I *think* that I can attach images to this email, and they will appear.
Maybe I can craft an HTML email by hand?
In the meantime, here (I hope) is a screenshot of a KDE menu, and two activities,
showing distinct wallpaper, widgets and launchers.

There are more images, and something like a basic guide with many screenshots,
over at https://github.com/unman/kde

You can install KDE in 4.0 with the following instructions:
  1. Open [Dom0] Terminal
  2. Type this: `sudo qubes-dom0-update @kde-desktop-qubes`
  3. Press enter
  4. Type ”y” then press enter
  5. Reboot when finished 

It will change the way you use Qubes.

If you have questions, problems, or tips about using KDE, post them here.

![kde_menu7.png|1025x576](upload://t5hqKQj1TU1h94nr1wS3rYpbu19.png)



![kde5.png|1025x576](upload://hKq7NfJgceL3HUYkAz5oPOFruT0.png)



![kde6.png|1025x576](upload://wi3nHCvqwTTpsza9gSJZ26oHzaD.png)

---

## Ubuntu 26.04 template

> 板块: General Discussion

Ubuntu 26.04, resolute raccoon, has been released.

If any one wants to try it out, I've pushed a template:
https://qubes.3isec.org/Templates_4.3/

I've built Qubes packages and they are available at [3isec](https://qubes.3isec.org/)

Official packages will be available soon, but the build isn't
yet straightforward so these are usable in the meantime.
The templates ship with the Qubes repository configured - you will need
to comment out the definition until those packages are built. If you
want to use the 3isec repo in the meantime, instructions for configuring
*that* repository are given.

Resolute leans on snap, so I have included the qubes-snap-helper. If you
want firefox you will need to `snap install firefox` in your qube.

---

## Issue with signatures on the Nitrokey security dongle after a system (OS) update

> 板块: General Discussion

English: 
After updating Qubes OS, there will inevitably be signature issues detected by both the "Coreboot Heads" firmware and the Nitrokey USB dongle. When your PC boots with Coreboot Heads installed, the firmware will detect a change in the signatures. I think you should follow the Nitrokey tutorial here in french or in english:  

French:
https://docs.nitrokey.com/fr/nitropad-nitropc/heads/system-update 

English:
https://docs.nitrokey.com/en/nitropad-nitropc/heads/system-update

 Problème  de signatures avec le dongle de sécurité Nitrokey after an update of systeme (OS).

French / Français: 
Après la mise à jour de Qubes OS, des problèmes de signature seront inévitablement détectés par le firmware « Coreboot Heads » et la clé USB Nitrokey. Lorsque votre PC démarrera avec Coreboot Heads installé, le firmware détectera une modification des signatures. Je vous recommande de suivre le tutoriel Nitrokey ici : https://docs.nitrokey.com/fr/nitropad-nitropc/heads/system-updateProblème de signatures avec le dongle de sécurité Nitrokey après une mise à jour du système (OS)

Je testerai cela plus tard et vous tiendrai au courant.

---

## Qubes OS AI Knowledge Base — 690 docs in one file for AI / LLMs

> 板块: General Discussion

**https://github.com/iasds/qubes-os-ai-knowledge-base**

## What

A single 4MB Markdown file containing **all 191 official Qubes OS documentation pages** (from [qubes-doc](https://github.com/QubesOS/qubes-doc)) plus **all 499 community guides** from this forum's [Guides category](https://forum.qubes-os.org/c/guides/14).

No summarization, no omission — every command, config, and warning is preserved.

## Why

Load the entire thing into an LLM context or RAG pipeline. Ask any Qubes question and the AI has the full knowledge base at hand. No more piecemeal copy-paste.

## Contents

| | Source | Count |
|---|--------|-------|
| Official docs | qubes-doc (RST → MD) | 191 |
| Forum guides | c/guides/14 (full crawl) | 499 |
| **Total** | | **690** |

## Quick start

```
git clone https://github.com/iasds/qubes-os-ai-knowledge-base.git
cat qubes-guides.md   # feed to your AI
```

Content as of 2026-04-23. PRs and stars welcome.

---

## Easy qubes.ConnectTCP pipes

> 板块: General Discussion

Now I'm very happy. This should make my life easier.

I tend to do all kinds of tests and coding in disposable templates and creating `qubes.ConnectTCP`-pipes is a PITA, so finally made myself a little dev-tool.

It lists all the VMs with services they are running on localhost so that I can create those TCP pipes and related policy rules with just point and click. Policies are saved to `/etc/qubes/policy.d/30-dev-tcp-temp.policy`

These are intended to be temporary, so everything is cleaned afterwards when interrupted or closed, it removes all the socat pipes and added policies.

It's still not very polished or battle tested but basic functionality seems to work just fine.

![Screenshot_2026-04-27_08-23-16|457x500](upload://1i5D8zf2gDeCxa8uRaP0agS4q8Y.png)


Now, installing things to dom0 is not recommended and I'm not advising anyone to use this. You probably shouldn't.

It requires this package:
`sudo qubes-dom0-update python3-tkinter`

[details="qube_pipes.py"]
```python
#!/usr/bin/python3

import tkinter as tk
from tkinter import messagebox
import subprocess
import signal
import atexit
import os
import sys
import threading
import time
import qubesadmin

# Configuration
POLICY_FILE = "/etc/qubes/policy.d/30-dev-tcp-temp.policy"
EXCLUDED_VMS = ["dom0", "mirage-firewall", "snitch-ui", "vault"]

# Visual Theme
THEME = {
    "bg": "#F0F2F5",             # Main canvas background
    "panel_bg": "#FFFFFF",       # Top bar background
    "text_main": "#333333",      # Standard text
    "text_muted": "#666666",     # Instructions text
    "vm_bg": "#FFFFFF",          # VM Card background
    "vm_border": "#CED4DA",      # VM Card border
    "vm_sel_bg": "#E7F1FF",      # Selected VM background
    "vm_sel_border": "#0D6EFD",  # Selected VM border
    "port_fill": "#20C997",      # Port circle
    "port_border": "#198754",    # Port border
    "line": "#0D6EFD",           # Connection line
}
FONT_MAIN = ("Helvetica", 10)
FONT_BOLD = ("Helvetica", 10, "bold")
FONT_LARGE = ("Helvetica", 11)

class VM:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.ports = []
        self.canvas_id = None
        self.port_ids = {} # port -> canvas item ID

    def update_ports(self, ports):
        self.ports = ports

class Connection:
    def __init__(self, client_name, local_port, server_name, remote_port):
        self.client_name = client_name
        self.local_port = local_port
        self.server_name = server_name
        self.remote_port = remote_port
        self.line_id = None
        self.process = None

class QubePipesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Qubes TCP Pipes")
        self.root.configure(bg=THEME["bg"])
        
        # --- UI Layout ---
        # Top Control Panel
        self.top_frame = tk.Frame(root, bg=THEME["panel_bg"], height=50, bd=1, relief=tk.RIDGE)
        self.top_frame.pack(fill=tk.X, side=tk.TOP)
        
        self.refresh_btn = tk.Button(
            self.top_frame, text="⟳ Refresh VMs", command=self.refresh_vms, 
            bg="#F8F9FA", activebackground="#E2E6EA", relief=tk.GROOVE, padx=10
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=15, pady=10)

        instructions = tk.Label(
            self.top_frame, 
            text="1. Click a VM box to select Client   |   2. Click a green port on another VM to connect", 
            bg=THEME["panel_bg"], fg=THEME["text_muted"], font=FONT_LARGE
        )
        instructions.pack(side=tk.LEFT, padx=20)

        # Main Canvas
        self.canvas = tk.Canvas(root, width=1200, height=800, bg=THEME["bg"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # --- State Variables ---
        self.vms = {}
        self.connections = []
        self.selected_source_vm = None
        
        self.setup_signals()
        self.refresh_vms()
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Configure>", self.on_resize)
        self.last_width = self.root.winfo_width()

    def setup_signals(self):
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)
        self.root.protocol("WM_DELETE_WINDOW", self.handle_exit_gui)
        atexit.register(self.cleanup)

    def handle_exit(self, signum, frame):
        self.cleanup()
        sys.exit(0)
        
    def handle_exit_gui(self):
        self.cleanup()
        self.root.destroy()
        sys.exit(0)

    def run_cmd(self, cmd, silent=False):
        try:
            if silent:
                subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                return ""
            else:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
                return result.stdout
        except Exception as e:
            print(f"Error running command {cmd}: {e}")
            return ""

    def get_running_vms(self):
        try:
            qapp = qubesadmin.Qubes()
            filtered = []
            for vm in qapp.domains:
                if (vm.is_running() and 
                    vm.klass not in ['TemplateVM', 'AdminVM'] and 
                    not vm.name.startswith("sys-") and 
                    vm.name not in EXCLUDED_VMS):
                    filtered.append(vm.name)
            return filtered
        except Exception as e:
            print(f"Error accessing qubesadmin: {e}")
            return []

    def get_listening_ports(self, vm):
        # Removed the grep so we get all listening TCP ports
        cmd = f'qvm-run -q --pass-io --no-gui --no-autostart {vm} "ss -ltn"'
        output = self.run_cmd(cmd)
        ports = []
        
        for line in output.splitlines():
            # Only process lines representing actively listening sockets
            if not line.startswith("LISTEN"):
                continue
                
            parts = line.split()
            # ss -ltn columns: State, Recv-Q, Send-Q, Local Address:Port, Peer Address:Port
            if len(parts) >= 4:
                addr_port = parts[3]
                
                if ":" in addr_port:
                    # rsplit(":", 1) splits by the LAST colon to safely handle IPv6 addresses
                    addr, port = addr_port.rsplit(":", 1)
                    
                    # Strip brackets from IPv6 formats (e.g., [::])
                    addr = addr.strip("[]")
                    
                    # Include it if it listens on all interfaces (*, 0.0.0.0, ::) 
                    # or explicitly on localhost (127.x.x.x, ::1)
                    if addr in ["*", "0.0.0.0", "::"] or addr.startswith("127.") or addr == "::1":
                        if port.isdigit():
                            ports.append(port)
                            
        return list(set(ports))

    def refresh_vms(self):
        self.selected_source_vm = None
        
        vm_names = self.get_running_vms()
        new_vms = {}
        for name in vm_names:
            new_vms[name] = VM(name, 0, 0)
            
        self.vms = new_vms
        
        # Keep valid connections, cleanup orphaned ones
        active_connections = []
        for conn in self.connections:
            # If either the client or server VM was shut down, kill the pipe
            if conn.client_name in self.vms and conn.server_name in self.vms:
                active_connections.append(conn)
            else:
                self.kill_connection(conn)
        self.connections = active_connections
            
        self.render_vms()
        threading.Thread(target=self.discover_ports_worker, daemon=True).start()

    def kill_connection(self, conn):
        if conn.process:
            conn.process.terminate()
            try:
                conn.process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                conn.process.kill()
                
        kill_cmd = f'qvm-run -q --no-gui --no-autostart {conn.client_name} "pkill -f \'socat TCP-LISTEN:{conn.local_port}\'"'
        subprocess.Popen(kill_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def on_resize(self, event):
        if abs(event.width - self.last_width) > 20:
            self.last_width = event.width
            self.render_vms(event.width)

    def render_vms(self, width=None):
        self.canvas.delete("vm_element")
        
        if not width:
            width = self.canvas.winfo_width()
        if width < 10: 
            width = 1200
            
        # Adjusted columns to account for wider screen space
        cols = max(1, width // 280) 
        
        for i, (name, vm) in enumerate(self.vms.items()):
            row = i // cols
            col = i % cols
            # Calculate center point for the VM box
            vm.x = 140 + col * 280
            vm.y = 80 + row * 160 
            self.draw_vm_box(vm)
            
            if vm.ports:
                self.update_vm_ports_ui(name, vm.ports)

        self.redraw_connections()
                
        for conn in self.connections:
            self.draw_connection_line(conn)

    def draw_vm_box(self, vm):
        # Increased padding slightly for a "card" look
        padding_x = 55
        padding_y = 45
        x1, y1 = vm.x - padding_x, vm.y - padding_y
        x2, y2 = vm.x + padding_x, vm.y + padding_y
        
        # Draw the main card body
        vm.canvas_id = self.canvas.create_rectangle(
            x1, y1, x2, y2, 
            fill=THEME["vm_bg"], outline=THEME["vm_border"], width=2, 
            tags=("vm_element", "vm_box", vm.name)
        )
        
        # Draw the VM Name text
        self.canvas.create_text(
            vm.x, vm.y, 
            text=vm.name, font=FONT_BOLD, fill=THEME["text_main"], 
            tags=("vm_element", "vm_box", vm.name)
        )

    def discover_ports_worker(self):
        for name, vm in self.vms.items():
            ports = self.get_listening_ports(name)
            self.root.after(0, self.update_vm_ports_ui, name, ports)

    def handle_source_vm_click(self, vm):
        if self.selected_source_vm == vm:
            self.canvas.itemconfig(vm.canvas_id, fill=THEME["vm_bg"], outline=THEME["vm_border"])
            self.selected_source_vm = None
            return

        if self.selected_source_vm:
            self.canvas.itemconfig(self.selected_source_vm.canvas_id, fill=THEME["vm_bg"], outline=THEME["vm_border"])
        
        self.selected_source_vm = vm
        self.canvas.itemconfig(vm.canvas_id, fill=THEME["vm_sel_bg"], outline=THEME["vm_sel_border"])

    def update_vm_ports_ui(self, name, ports):
        vm = self.vms[name]
        vm.update_ports(ports)
        
        padding_x = 55
        padding_y = 45
        x2 = vm.x + padding_x
        y1 = vm.y - padding_y
        y2 = vm.y + padding_y
        
        for i, port in enumerate(ports):
            py = y1 + (i + 1) * (y2 - y1) / (len(ports) + 1)
            
            # Draw port circle
            port_id = self.canvas.create_oval(
                x2-6, py-6, x2+6, py+6, 
                fill=THEME["port_fill"], outline=THEME["port_border"], width=1, 
                tags=("vm_element", "port")
            )
            # Draw port text
            self.canvas.create_text(
                x2+24, py, 
                text=port, font=FONT_MAIN, fill=THEME["text_main"], 
                tags=("vm_element", "port_text")
            )
            vm.port_ids[port] = port_id

        # Redraw connections now that new port coordinates are known
        self.redraw_connections()

    def on_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        if not item:
            return
        
        item_id = item[0]
        tags = self.canvas.gettags(item_id)
        
        if "port" in tags or "port_text" in tags:
            # User clicked near/on a destination port
            for vm in self.vms.values():
                for port, pid in vm.port_ids.items():
                    # Check distance manually to be generous with clicks if they hit the text
                    coords = self.canvas.coords(pid)
                    if coords:
                        cx = (coords[0] + coords[2]) / 2
                        cy = (coords[1] + coords[3]) / 2
                        if abs(event.x - cx) < 40 and abs(event.y - cy) < 15:
                            self.handle_target_port_click(vm, port)
                            return
        elif "vm_box" in tags:
            vm_name = tags[2]
            self.handle_source_vm_click(self.vms[vm_name])

    def handle_target_port_click(self, target_vm, remote_port):
        if not self.selected_source_vm:
            messagebox.showinfo("Select Client", "Please click a VM box first to select the source Client.")
            return
            
        client_vm = self.selected_source_vm
        
        if client_vm.name == target_vm.name:
            messagebox.showwarning("Warning", "Cannot connect a VM to itself.")
            self.canvas.itemconfig(client_vm.canvas_id, fill=THEME["vm_bg"], outline=THEME["vm_border"])
            self.selected_source_vm = None
            return

        local_port = remote_port
        self.create_connection(client_vm.name, local_port, target_vm.name, remote_port)
        
        # Reset visual selection
        self.canvas.itemconfig(client_vm.canvas_id, fill=THEME["vm_bg"], outline=THEME["vm_border"])
        self.selected_source_vm = None

    def create_connection(self, client_name, local_port, server_name, remote_port):
        rule = f"qubes.ConnectTCP +{remote_port} {client_name} {server_name} allow\n"
        try:
            with open(POLICY_FILE, "a") as f:
                f.write(rule)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write policy: {e}")
            return

        time.sleep(0.5)

        cmd = f'qvm-run --pass-io --no-gui --no-autostart {client_name} "qvm-connect-tcp {local_port}:{server_name}:{remote_port}"'
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        conn = Connection(client_name, local_port, server_name, remote_port)
        conn.process = process
        
        self.connections.append(conn)
        self.redraw_connections()

    def on_right_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        if not item:
            return
            
        tags = self.canvas.gettags(item[0])
        if "connection" not in tags:
            return
            
        # Find the unique connection tag we assigned
        conn_tag = next((t for t in tags if t.startswith("conn_")), None)
        if not conn_tag:
            return
            
        # Match the tag to the connection object
        target_conn = next((c for c in self.connections if f"conn_{id(c)}" == conn_tag), None)
        if not target_conn:
            return
            
        if messagebox.askyesno(
            "Delete Connection", 
            f"Sever connection from {target_conn.client_name} to {target_conn.server_name}:{target_conn.remote_port}?"
        ):
            self.delete_connection(target_conn)

    def delete_connection(self, conn):
        # 1. Kill the socat process
        self.kill_connection(conn)
        
        # 2. Remove from active connections list
        if conn in self.connections:
            self.connections.remove(conn)
            
        # 3. Remove rule from policy file
        self.remove_policy_rule(conn)
        
        # 4. Refresh UI
        self.redraw_connections()

    def remove_policy_rule(self, conn):
        rule_to_remove = f"qubes.ConnectTCP +{conn.remote_port} {conn.client_name} {conn.server_name} allow\n"
        if not os.path.exists(POLICY_FILE):
            return
            
        try:
            # Read all lines, keep everything except the one we want to delete
            with open(POLICY_FILE, "r") as f:
                lines = f.readlines()
                
            with open(POLICY_FILE, "w") as f:
                for line in lines:
                    if line != rule_to_remove:
                        f.write(line)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update policy file: {e}")

    def draw_connection_line(self, conn):
        client_vm = self.vms.get(conn.client_name)
        server_vm = self.vms.get(conn.server_name)
        
        if not client_vm or not server_vm or conn.remote_port not in server_vm.port_ids:
            return 
            
        src_x, src_y = client_vm.x, client_vm.y
        
        dst_coords = self.canvas.coords(server_vm.port_ids[conn.remote_port])
        # BUG FIX: Prevent crash if the port hasn't been rendered yet
        if not dst_coords:
            return
            
        dst_x = (dst_coords[0] + dst_coords[2]) / 2
        dst_y = (dst_coords[1] + dst_coords[3]) / 2
        
        # Create a unique tag for this specific connection
        conn_tag = f"conn_{id(conn)}"
        
        conn.line_id = self.canvas.create_line(
            src_x, src_y, dst_x, dst_y, 
            fill=THEME["line"], width=2.5, arrow=tk.LAST, 
            tags=("vm_element", "connection", conn_tag)
        )
        
        text_x, text_y = src_x + (dst_x - src_x) * 0.25, src_y + (dst_y - src_y) * 0.25
        
        text_id = self.canvas.create_text(
            text_x, text_y, 
            text=f" L:{conn.local_port} ", font=FONT_BOLD, fill=THEME["line"], 
            tags=("vm_element", "connection", conn_tag)
        )
        bbox = self.canvas.bbox(text_id)
        if bbox:
            bg_rect = self.canvas.create_rectangle(
                bbox[0]-2, bbox[1]-2, bbox[2]+2, bbox[3]+2, 
                fill=THEME["bg"], outline=THEME["line"], width=1, 
                tags=("vm_element", "connection", conn_tag)
            )
            self.canvas.tag_lower(bg_rect, text_id)
            self.canvas.tag_lower(conn.line_id, bg_rect)

    def redraw_connections(self):
        self.canvas.delete("connection")
        for conn in self.connections:
            self.draw_connection_line(conn)
        
    def cleanup(self):
        print("Cleaning up temporary pipes...")
        for conn in self.connections:
            self.kill_connection(conn)
            
        if os.path.exists(POLICY_FILE):
            try:
                os.remove(POLICY_FILE)
            except Exception:
                pass 
                
        self.connections = []

if __name__ == "__main__":
    root = tk.Tk()
    # Set a minimum window size so the UI doesn't crush
    root.minsize(800, 600)
    app = QubePipesApp(root)
    root.mainloop()
```
[/details]

E: couple of bug fixes
E2: added ability to right click delete connections

---

## How do I update Nitrokey signatures?

> 板块: General Discussion

Hello everyone. While unsuccessfully trying to follow a tutorial to bypass authentication on x.com using Google's Authenticator app on Android OS, I unknowingly messed up the shell yesterday. Today I booted my Coreboot laptop with the Coreboot Heads firmware. Here's the Nitrokey signature problem, shown in the screenshots. Artificial intelligence told me to update the Nitrokey signatures. I'm using a translator because I don't speak English. 
How do I update Nitrokey signatures?

[grid]
![IMG_20260427_173148|666x500](upload://3FHG1sZqebGZqzGHPHhbc8KI5Qr.jpeg)
![IMG_20260427_174031|375x500](upload://vZMxUI7jwpajDr0EOInWumDMl0Z.jpeg)
![IMG_20260427_174425|375x500](upload://yKkJsALqqozcnUCdoejr1qNcbtt.jpeg)
![IMG_20260427_174450|375x500](upload://5vGaWjL1954FpddixrM1KXnVMT8.jpeg)
![IMG_20260427_174502|375x500](upload://ejQxuAiKQJgdVCTBlVDPdac2o6Q.jpeg)
[/grid]

---

## Can QubesOS team reach out to AI security companies for reviews?

> 板块: General Discussion

Something like Claude Mythos, ChatGPT Cyber and maybe [V12](https://v12.sh/)? Not sure if latter offers free plan for FOSS projects.

Community can share some other too if they offer free plan for FOSS projects and with sources of actual findings reported by FOSS maintainers and not benchmaxxing or sloppy articles about how good it is at finding "security vulnerabilities".

---

## Framework Laptop 13 + Ultra 7 155H?

> 板块: General Discussion

I check the lists, and i do not see the Framework Laptop 13 + Ultra 7 155H?

---

## Alpine Linux Template (non-official) available for testing

> 板块: General Discussion

Thanks to Antoine Martin we have now a alpine(.rpm package for dom0) template. Thankyou very much!

https://lab.ilot.io/ayakael/qubes-builder-alpine/-/releases

https://agora.ilot.io/@ayakael/110958691297739390

https://github.com/QubesOS/qubes-issues/issues/7323#issuecomment-1694520402

---

## Theoretical dedicated gpu vm that paravirtualizes to other guest VMs

> 板块: General Discussion

I was just wondering is it theoretically possible to have a pcie dedicated GPU in a vm that then paravirtualizes its graphics to another guest vm. Or is this not how paravirtualization works

Like this:
PCIE GPU VM ---> virgl maybe --> app qube

Also is it it safer to do PCIE gpu vm to paravirtualization app qube, or is there no good reason to do this and just do straight up pcie gpu passthrough to the app qube

Has something like this existed or am I missing something

---

## Qube Manager redesign (visual connections between qubes, drag & drop, zooming)

> 板块: General Discussion

Hello Qubes Community,

I had the idea of redesigning the Qube Manager a while ago and just finished a mockup of the core change that my vision entails:

![mockup|690x464](upload://9Uvf716h8mvpxvwcIWUKeJb2uqb.png)

Please do enlarge the above mockup to view all details. The three "web-xxx" qubes are selected and sys-usb is being hovered on. A qube's features are represented by a tag list on the bottom on being hovered on or selected (e..g., "APP" for app qube, "DISP" for disposable, "USB" for sys-usb). It says "Qubes" in the upper right-hand corner because Qubes OS is actually a trademark and I wasn't sure whether I am allowed to use it in this way.

The core change is what I call "Deck view". It's the currently selected tab in the mockup and its features would be:

1. **Visual representation of relationships between qubes** (see "Qube connections" dropdown in the upper right-hand corner). Not just the network -- could also be, for example, policy permissions. Which qube is allowed to do what to another qube? This could be extended to be an editor as well. A real "under-the-hood" view.
2. **Drag and drop functionality**. Launch or stop qubes simply by dragging them from the main area into the stopped area and the other way around.
3. **Free zooming in and out and moving around**. Get an overview of your machine in seconds.

In addition to that, the familiar table view, as it is currently implemented in the Qube Manager, would always just be a click away.

What do you people think? Feedback is highly appreciated.

Warm regards,
Ferdinand Heinrich


----------------------------------------------------------------------------------

Legal:

I would like to highlight that I *currently* do not want somebody else to implement the above scheme without my explicit permission.

Licenses of the assets used in the mockup:

[details="Inter font license"]
Copyright (c) 2016 The Inter Project Authors (https://github.com/rsms/inter)

This Font Software is licensed under the SIL Open Font License, Version 1.1.
This license is copied below, and is also available with a FAQ at:
http://scripts.sil.org/OFL

-----------------------------------------------------------
SIL OPEN FONT LICENSE Version 1.1 - 26 February 2007
-----------------------------------------------------------

PREAMBLE
The goals of the Open Font License (OFL) are to stimulate worldwide
development of collaborative font projects, to support the font creation
efforts of academic and linguistic communities, and to provide a free and
open framework in which fonts may be shared and improved in partnership
with others.

The OFL allows the licensed fonts to be used, studied, modified and
redistributed freely as long as they are not sold by themselves. The
fonts, including any derivative works, can be bundled, embedded,
redistributed and/or sold with any software provided that any reserved
names are not used by derivative works. The fonts and derivatives,
however, cannot be released under any other type of license. The
requirement for fonts to remain under this license does not apply
to any document created using the fonts or their derivatives.

DEFINITIONS
"Font Software" refers to the set of files released by the Copyright
Holder(s) under this license and clearly marked as such. This may
include source files, build scripts and documentation.

"Reserved Font Name" refers to any names specified as such after the
copyright statement(s).

"Original Version" refers to the collection of Font Software components as
distributed by the Copyright Holder(s).

"Modified Version" refers to any derivative made by adding to, deleting,
or substituting -- in part or in whole -- any of the components of the
Original Version, by changing formats or by porting the Font Software to a
new environment.

"Author" refers to any designer, engineer, programmer, technical
writer or other person who contributed to the Font Software.

PERMISSION AND CONDITIONS
Permission is hereby granted, free of charge, to any person obtaining
a copy of the Font Software, to use, study, copy, merge, embed, modify,
redistribute, and sell modified and unmodified copies of the Font
Software, subject to the following conditions:

1) Neither the Font Software nor any of its individual components,
in Original or Modified Versions, may be sold by itself.

2) Original or Modified Versions of the Font Software may be bundled,
redistributed and/or sold with any software, provided that each copy
contains the above copyright notice and this license. These can be
included either as stand-alone text files, human-readable headers or
in the appropriate machine-readable metadata fields within text or
binary files as long as those fields can be easily viewed by the user.

3) No Modified Version of the Font Software may use the Reserved Font
Name(s) unless explicit written permission is granted by the corresponding
Copyright Holder. This restriction only applies to the primary font name as
presented to the users.

4) The name(s) of the Copyright Holder(s) or the Author(s) of the Font
Software shall not be used to promote, endorse or advertise any
Modified Version, except to acknowledge the contribution(s) of the
Copyright Holder(s) and the Author(s) or with their explicit written
permission.

5) The Font Software, modified or unmodified, in part or in whole,
must be distributed entirely under this license, and must not be
distributed under any other license. The requirement for fonts to
remain under this license does not apply to any document created
using the Font Software.

TERMINATION
This license becomes null and void if any of the above conditions are
not met.

DISCLAIMER
THE FONT SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
OF COPYRIGHT, PATENT, TRADEMARK, OR OTHER RIGHT. IN NO EVENT SHALL THE
COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
INCLUDING ANY GENERAL, SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL
DAMAGES, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF THE USE OR INABILITY TO USE THE FONT SOFTWARE OR FROM
OTHER DEALINGS IN THE FONT SOFTWARE.
[/details]

[details="Michroma font license"]
Copyright 2011 The Michroma Project Authors (https://github.com/googlefonts/Michroma-font)

This Font Software is licensed under the SIL Open Font License, Version 1.1.
This license is copied below, and is also available with a FAQ at:
https://scripts.sil.org/OFL


-----------------------------------------------------------
SIL OPEN FONT LICENSE Version 1.1 - 26 February 2007
-----------------------------------------------------------

PREAMBLE
The goals of the Open Font License (OFL) are to stimulate worldwide
development of collaborative font projects, to support the font creation
efforts of academic and linguistic communities, and to provide a free and
open framework in which fonts may be shared and improved in partnership
with others.

The OFL allows the licensed fonts to be used, studied, modified and
redistributed freely as long as they are not sold by themselves. The
fonts, including any derivative works, can be bundled, embedded, 
redistributed and/or sold with any software provided that any reserved
names are not used by derivative works. The fonts and derivatives,
however, cannot be released under any other type of license. The
requirement for fonts to remain under this license does not apply
to any document created using the fonts or their derivatives.

DEFINITIONS
"Font Software" refers to the set of files released by the Copyright
Holder(s) under this license and clearly marked as such. This may
include source files, build scripts and documentation.

"Reserved Font Name" refers to any names specified as such after the
copyright statement(s).

"Original Version" refers to the collection of Font Software components as
distributed by the Copyright Holder(s).

"Modified Version" refers to any derivative made by adding to, deleting,
or substituting -- in part or in whole -- any of the components of the
Original Version, by changing formats or by porting the Font Software to a
new environment.

"Author" refers to any designer, engineer, programmer, technical
writer or other person who contributed to the Font Software.

PERMISSION & CONDITIONS
Permission is hereby granted, free of charge, to any person obtaining
a copy of the Font Software, to use, study, copy, merge, embed, modify,
redistribute, and sell modified and unmodified copies of the Font
Software, subject to the following conditions:

1) Neither the Font Software nor any of its individual components,
in Original or Modified Versions, may be sold by itself.

2) Original or Modified Versions of the Font Software may be bundled,
redistributed and/or sold with any software, provided that each copy
contains the above copyright notice and this license. These can be
included either as stand-alone text files, human-readable headers or
in the appropriate machine-readable metadata fields within text or
binary files as long as those fields can be easily viewed by the user.

3) No Modified Version of the Font Software may use the Reserved Font
Name(s) unless explicit written permission is granted by the corresponding
Copyright Holder. This restriction only applies to the primary font name as
presented to the users.

4) The name(s) of the Copyright Holder(s) or the Author(s) of the Font
Software shall not be used to promote, endorse or advertise any
Modified Version, except to acknowledge the contribution(s) of the
Copyright Holder(s) and the Author(s) or with their explicit written
permission.

5) The Font Software, modified or unmodified, in part or in whole,
must be distributed entirely under this license, and must not be
distributed under any other license. The requirement for fonts to
remain under this license does not apply to any document created
using the Font Software.

TERMINATION
This license becomes null and void if any of the above conditions are
not met.

DISCLAIMER
THE FONT SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
OF COPYRIGHT, PATENT, TRADEMARK, OR OTHER RIGHT. IN NO EVENT SHALL THE
COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
INCLUDING ANY GENERAL, SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL
DAMAGES, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF THE USE OR INABILITY TO USE THE FONT SOFTWARE OR FROM
OTHER DEALINGS IN THE FONT SOFTWARE.
[/details]

[details="Breeze Icon Theme license"]
The Breeze Icon Theme in icons/

    Copyright (C) 2014 Uri Herrera <uri_herrera@nitrux.in> and others

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 3 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library. If not, see <http://www.gnu.org/licenses/>.

Clarification:

  The GNU Lesser General Public License or LGPL is written for
  software libraries in the first place. We expressly want the LGPL to
  be valid for this artwork library too.

  KDE Breeze theme icons is a special kind of software library, it is an
  artwork library, it's elements can be used in a Graphical User Interface, or
  GUI.

  Source code, for this library means:
   - where they exist, SVG;
   - otherwise, if applicable, the multi-layered formats xcf or psd, or
  otherwise png.

  The LGPL in some sections obliges you to make the files carry
  notices. With images this is in some cases impossible or hardly useful.

  With this library a notice is placed at a prominent place in the directory
  containing the elements. You may follow this practice.

  The exception in section 5 of the GNU Lesser General Public License covers
  the use of elements of this art library in a GUI.

 https://vdesign.kde.org/

-----
		   GNU LESSER GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.


  This version of the GNU Lesser General Public License incorporates
the terms and conditions of version 3 of the GNU General Public
License, supplemented by the additional permissions listed below.

  0. Additional Definitions. 

  As used herein, "this License" refers to version 3 of the GNU Lesser
General Public License, and the "GNU GPL" refers to version 3 of the GNU
General Public License.

  "The Library" refers to a covered work governed by this License,
other than an Application or a Combined Work as defined below.

  An "Application" is any work that makes use of an interface provided
by the Library, but which is not otherwise based on the Library.
Defining a subclass of a class defined by the Library is deemed a mode
of using an interface provided by the Library.

  A "Combined Work" is a work produced by combining or linking an
Application with the Library.  The particular version of the Library
with which the Combined Work was made is also called the "Linked
Version".

  The "Minimal Corresponding Source" for a Combined Work means the
Corresponding Source for the Combined Work, excluding any source code
for portions of the Combined Work that, considered in isolation, are
based on the Application, and not on the Linked Version.

  The "Corresponding Application Code" for a Combined Work means the
object code and/or source code for the Application, including any data
and utility programs needed for reproducing the Combined Work from the
Application, but excluding the System Libraries of the Combined Work.

  1. Exception to Section 3 of the GNU GPL.

  You may convey a covered work under sections 3 and 4 of this License
without being bound by section 3 of the GNU GPL.

  2. Conveying Modified Versions.

  If you modify a copy of the Library, and, in your modifications, a
facility refers to a function or data to be supplied by an Application
that uses the facility (other than as an argument passed when the
facility is invoked), then you may convey a copy of the modified
version:

   a) under this License, provided that you make a good faith effort to
   ensure that, in the event an Application does not supply the
   function or data, the facility still operates, and performs
   whatever part of its purpose remains meaningful, or

   b) under the GNU GPL, with none of the additional permissions of
   this License applicable to that copy.

  3. Object Code Incorporating Material from Library Header Files.

  The object code form of an Application may incorporate material from
a header file that is part of the Library.  You may convey such object
code under terms of your choice, provided that, if the incorporated
material is not limited to numerical parameters, data structure
layouts and accessors, or small macros, inline functions and templates
(ten or fewer lines in length), you do both of the following:

   a) Give prominent notice with each copy of the object code that the
   Library is used in it and that the Library and its use are
   covered by this License.

   b) Accompany the object code with a copy of the GNU GPL and this license
   document.

  4. Combined Works.

  You may convey a Combined Work under terms of your choice that,
taken together, effectively do not restrict modification of the
portions of the Library contained in the Combined Work and reverse
engineering for debugging such modifications, if you also do each of
the following:

   a) Give prominent notice with each copy of the Combined Work that
   the Library is used in it and that the Library and its use are
   covered by this License.

   b) Accompany the Combined Work with a copy of the GNU GPL and this license
   document.

   c) For a Combined Work that displays copyright notices during
   execution, include the copyright notice for the Library among
   these notices, as well as a reference directing the user to the
   copies of the GNU GPL and this license document.

   d) Do one of the following:

       0) Convey the Minimal Corresponding Source under the terms of this
       License, and the Corresponding Application Code in a form
       suitable for, and under terms that permit, the user to
       recombine or relink the Application with a modified version of
       the Linked Version to produce a modified Combined Work, in the
       manner specified by section 6 of the GNU GPL for conveying
       Corresponding Source.

       1) Use a suitable shared library mechanism for linking with the
       Library.  A suitable mechanism is one that (a) uses at run time
       a copy of the Library already present on the user's computer
       system, and (b) will operate properly with a modified version
       of the Library that is interface-compatible with the Linked
       Version. 

   e) Provide Installation Information, but only if you would otherwise
   be required to provide such information under section 6 of the
   GNU GPL, and only to the extent that such information is
   necessary to install and execute a modified version of the
   Combined Work produced by recombining or relinking the
   Application with a modified version of the Linked Version. (If
   you use option 4d0, the Installation Information must accompany
   the Minimal Corresponding Source and Corresponding Application
   Code. If you use option 4d1, you must provide the Installation
   Information in the manner specified by section 6 of the GNU GPL
   for conveying Corresponding Source.)

  5. Combined Libraries.

  You may place library facilities that are a work based on the
Library side by side in a single library together with other library
facilities that are not Applications and are not covered by this
License, and convey such a combined library under terms of your
choice, if you do both of the following:

   a) Accompany the combined library with a copy of the same work based
   on the Library, uncombined with any other library facilities,
   conveyed under the terms of this License.

   b) Give prominent notice with the combined library that part of it
   is a work based on the Library, and explaining where to find the
   accompanying uncombined form of the same work.

  6. Revised Versions of the GNU Lesser General Public License.

  The Free Software Foundation may publish revised and/or new versions
of the GNU Lesser General Public License from time to time. Such new
versions will be similar in spirit to the present version, but may
differ in detail to address new problems or concerns.

  Each version is given a distinguishing version number. If the
Library as you received it specifies that a certain numbered version
of the GNU Lesser General Public License "or any later version"
applies to it, you have the option of following the terms and
conditions either of that published version or of any later version
published by the Free Software Foundation. If the Library as you
received it does not specify a version number of the GNU Lesser
General Public License, you may choose any version of the GNU Lesser
General Public License ever published by the Free Software Foundation.

  If the Library as you received it specifies that a proxy can decide
whether future versions of the GNU Lesser General Public License shall
apply, that proxy's public statement of acceptance of any version is
permanent authorization for you to choose that version for the
Library.
[/details]

---

## What's the status of official incremental backups feature?

> 板块: General Discussion

The github issues about this seem long dead.

---

## Rocket.chat installation based Whonix Workstation

> 板块: General Discussion

Dear All, 
I have tried several option to install rocket.chat followed different guide but not succeed, Could you please guide me step by step how to install rocket.chat desktop in Whonix worksation 18

---

## Starbook - trustworthy?

> 板块: General Discussion

Dear Qubes Community,
&nbsp;
the Starbook by Star Labs (located in the UK) is officially Qubes-certified since 2024, but I got sceptical and would **appreciate your help if and how I could trust the Starbook.**
&nbsp;
&nbsp;
Background:
&nbsp;
**I have been happily using Qubes OS for many years** on Dell and Lenovo machines. I am loving Qubes OS and it is a daily part of my life - so, a huge thanks to the team, by the way!!

As I cannot increase memory (16 GB) in my current machines, I **wished for a new powerful and portable daily driver laptop** which would last me for many years.
&nbsp;
Thus, some days ago, **I spent a lot of money (3500 Euro) to order a Starbook Ultra 7** with maximum specs:

* 14-inch 4K IPS 625nits Display
* 1.40GHz 16-core Intel® Core™ Ultra 7 Processor 165H (Turbo Boost up to 5GHz, with 24MB Cache)
* 4TB Gen4 PCIe SSD
* 96GB of DDR5 memory
* Intel® Arc™ graphics (2.3 GHz Max Dynamic Frequency)
* coreboot
* preinstalled Ubuntu (I can install Qubes OS myself)
&nbsp;
&nbsp;

*Unfortunately, I am now sceptical...*
&nbsp;
**A) Should I keep the package closed when it arrives and return it within the 14-day period?** Since EU taxes and import duties might not be refunded, I might only get back 3000 of the 3500 Euros.
&nbsp;
**B) Could I be able to find trust in the product to use it as my daily driver with qubes?**
&nbsp;
&nbsp;
&nbsp;
*Why I got sceptical:*
&nbsp;
&nbsp;
**Reason 1: There seems to be Chinese budget hardware inside**
&nbsp;
1.1) In this review ( https://uk.trustpilot.com/users/6930521ad7ccaa027d5b7248 ), it is stated that: "**This isn't their design in no way(as they market it), but a copy of Chinese brand Machenike**(models Machcreator A, Machcreator 14, etc..), which I found by searching for a better fan and matched the part numbers."
&nbsp;
1.2) **Internals** from official Starbook disassembly ( see Step 3 of https://support.starlabs.systems/hc/star-labs/articles/starbook-mk-v-mk-vi-mk-vii-complete-disassembly-guide , i.e. https://cdn.shopify.com/s/files/1/2059/5897/files/IMG-8821.jpg ) look 95% **identical to the "Machenike MachCreator 14"** internals filmed in a YouTube review *"Best Budget Laptop 2022? - Machenike MachCreator 14 | Unboxing and Full Review"* at position of 3 minutes 42 seconds ( https://youtu.be/JCvDM2pUdus?t=222 ).
&nbsp;
1.3) The **aluminium chassis** looks identical between Starbook ( https://cdn.shopify.com/s/files/1/2059/5897/files/IMG-8816.jpg ) and Machenike MachCreator 14 ( https://youtu.be/JCvDM2pUdus?t=112 ). So I why is it written on the Starbook that it is "Designed by Star Labs" when it actually has the same design as the Machenike MachCreator 14?
&nbsp;
1.4) Star Labs officially state: "In 2017, we started using **Clevo** as a supplier" and "When 2018 came around, we started working on our very own laptops. **We used a variety of suppliers, design houses and factories**." and "2003 [...] We still use Linux and our hardware." ( https://de.starlabs.systems/pages/about-us ). So, what do they mean by "our hardware"? **And might they even still be using Clevo (see Reason 3)?**
&nbsp;
1.5) By the way, I wonder if it is "regular practice" that Linux laptop sellers, like System76 or Framework, buy Clevo / Tongfang / etc. hardware in China?? (see the company names mentioned on https://electronics.alibaba.com/buyingguides/tongfang-laptop-guide-how-to-choose-wisely )
&nbsp;
&nbsp;
&nbsp;
**Reason 2: The hardware might be risky to use**
&nbsp;
Users on this **Qubes forum** are reporting Starbook hardware issues, like
&nbsp;
2.1) "**The laptop died slowly while corrupting data (and back-ups) It is likely to be the motherboard (bad quality)**" ( https://forum.qubes-os.org/t/questions-about-qubes-os-on-starlabs-laptop/37322/5 )
&nbsp;
2.2) "I’ve only had this machine for about a year and have taken pretty good care of it. There are **sparkling pixel artifacts as well which is why I think it looks like my GPU is failing**. Sometimes the screen won’t come on at all or just blinks black and off. [...] Update - It does it in the BIOS and when booted from a Fedora live USB as well." ( https://forum.qubes-os.org/t/starlabs-starbook-screen-flickering/34687 )
&nbsp;
2.3) "the laptop would **randomly switch off** so I contacted support who believed it would be a faulty RAM module, which I believe it was after taking them out one at a time and testing" ( https://forum.qubes-os.org/t/nova-custom-nv41-or-star-labs-starbook/24857/20 )
&nbsp;
2.4) "the Star Labs StarBooks I just got (32 RAM btw) **gets nuclear HOT** even just sitting at the UEFI login" ( https://forum.qubes-os.org/t/a-laptop-that-can-withstand-coreboot-and-qubes-os/24436/11 )
&nbsp;
Outside the Qubes forum, I want to mention one review (I do not understand the coreboot critique)
&nbsp;
2.5) "First the hardware issues: the cooling solution(having only one tiny pipe and a single fan) proved to be highly inadequate and was **constantly failing to cool the CPU+GPU combo(even under medium load)**. It had been reaching 90 degrees with some basic load tests(basemark's web 3.0) not to mention running some phoronix's suites which made the top-right corner scorching to the touch [...] On the software side: the **coreboot saga makes those guys so ridiculous that only one word comes to my mind: you swindlers!** But here's my advice to starlabs: if I were you, I'd **test quite extensively all models offered by those Chinese before start shipping them trough the mail to customers**. I feel like a moron beta tester now of the crappiest laptop meant for mass-production and mass re-brading the Chinese could make up. But my pains are over - yesterday **the thing just died**. I carried it 200km in a backpack on a drive and when tried starting it, nothing happened - no screen, no fan, only the keyboard lightning and the side one. I am lucky that's not my single machine and have just received a successor from a reputable brand. [...] So, here's a recap: don't buy Starlab AMD(and don't buy Intel for sure)!" ( https://uk.trustpilot.com/users/6930521ad7ccaa027d5b7248 )
&nbsp;
&nbsp;
&nbsp;
**Reason 3: There could be security issues due to Chinese budget hardware**
&nbsp;
*Important: I don't know if Star Labs is still using Clevo as a supplier, but as cited in 1.4) above they have used them in the past. Also, I only did a very quick search on this topic - and it scares me what I have found already..*
&nbsp;
3.1) June 2024: "**RansomHub claims to have infiltrated Clevo’s network** and been able to move around its systems for a long time.” ( https://cybernews.com/news/clevo-laptop-ransomware-attack-gaming-ransonhub/ )
&nbsp;
3.2) March 2025: "Researchers have discovered a **major security vulnerability affecting multiple gaming laptop models using Clevo hardware**. [...] This incident highlights **ongoing challenges in firmware supply chain security**. [...] Users of affected devices should apply any security updates provided by manufacturers promptly, though the fundamental vulnerability may persist until hardware replacement occurs in some cases." ( https://cybersecuritynews.com/clevo-devices-boot-guard-private-key/ )
&nbsp;
3.3) October 2025: "**Clevo accidentally exposed private keys** used in its Intel Boot Guard implementation, allowing attackers to sign malicious firmware that would be trusted during the earliest boot stages [...] Researchers warn that **this leak can enable stealthy and persistent compromise on systems that use Clevo’s firmware, including devices from other brands that integrate Clevo’s platform components**." ( https://gbhackers.com/clevo-uefi-leak-allows-malicious-firmware/ also see https://cyberpress.org/exposure-of-clevo-uefi-bootguard-keys/ )
&nbsp;
&nbsp;
&nbsp;
My questions to you all:
&nbsp;
Based on the information I collected, **would you rather recommend me to**
&nbsp;
A) **return the unopenened package within 14 days of arrival** and try to get back as much of my money as possible?
&nbsp;
B) **aim on using the Starbook as my single daily driver, and run tests (see below) to build trust** to eventually store all my local keepass-databases, private email messages of the last decades, all my private and even work related confidential documents, online banking and crypto money on it?
&nbsp;
&nbsp;
In case of B):
&nbsp;
How do you think it would be able to
&nbsp;
...**build trust in the hardware's durability?**
...by using tools like memtest86 to test memory?
...by observing temperature levels?
...by stress testing CPU and GPU? (don't know how I would do that, yet)
...by running SMART tests on SSD?
...by any other procedures?
&nbsp;
...**build trust in the hardware's security?**
...by manually flashing a trusted firmware? (and would this require a hardware programming and debugging toolkit? I know that [Star Labs sold one fitting the Starbook](https://web.archive.org/web/20250815182249/https://starlabs.systems/collections/parts/products/programming-kit), but at the moment they don't seem to offer it)
...by monitoring network connections? (I would be open to learn it)
&nbsp;
&nbsp;
&nbsp;
**I am grateful for any thoughts, ideas, opinions, advices, resources, and instructions!**
&nbsp;
&nbsp;

---

## Xen -> KVM nested virtualization for testing

> 板块: General Discussion

Hey @marmarek

Can you give pointers to current bugs and qubes tickets to follow explaining why Xen is broken and not support this?

I'm testing Heads development on top of qemu under a standard qube and as you know, qemu tcg is used since KVM cannot.

I would love to know and be able to tackle the issues upstream and tracking current state would be helpful.

Feel free to move subject to proper category

---

## Framework Laptop 13 Pro is stable?

> 板块: General Discussion

Now with Framework Laptop 13 Pro: Core Ultra 5 325, Core Ultra X7 358H, & Core Ultra X9 388H? Now with CAMM RAM? Whose will try to tested as stable uses?

---

## How much do we gotta worry about this Linux "age verification" BS?

> 板块: General Discussion

I've been seeing news about the braindead bootlicker states of America trying to force "age verification" into Linux. I'm still not sure how much I should panic about this. I don't see any of the communities of the distros I use talking about it, but it seems serious seeing how these devs aren't anons and some of them may live in America.

How serious do you think this is on a scale from 1 to 10? With 1 being we laugh about it with our friends and 10 being we gonna have to manually remove the virus from the kernel every time we want to install a distro and risk prison time for doing it.

---

## What is the status of iGPU support for Qubes?

> 板块: General Discussion

What is the status of integrated graphics (iGPU) support for Qubes? I was thinking about buying a new x86 laptop with a strong iGPU. When browsing the forum threads, it sounds like an iGPU can be applied only to one VM at a time (or to dom0), just as dedicated graphics cards. If so, this changes what I plan to buy.

---

## How long did it take you to get used to Qubes?

> 板块: General Discussion

When I initially moved from Arch I first thought "This is so cool, I can finally play with my vms with way less hassle now". But in the coming weeks I got quite strange feeling. I dreaded having to use my own computer. I often found myself procrastinating in doing so when I had to do some important work or when I wanted to look something up. When I finally was doing so just casual internet browsing felt exhausting. I thought about how to separate my activities. What sites should be visited in what Qube to minimize tracking. How to network the Qubes so different vpns or no vpns are used in what vms and so on and so forth. Quite obviously it was not fun at all

In total it took me 4-6 weeks for this feeling to disappear for basic usage. Even learning to use and to install Arch linux took me less time and it felt less exhausting compared to Qubes. And I only explored the very basic usage. I got no problems learning to use global copy-paste and moving files between Qubes

I want to ask other users, how was your learning curve with Qubes? Did you have similar problems getting used to Qubes as a daily driver? How long it took you to get used to it and etc?

---

## Since you're using Qubes have you ever been hacked?

> 板块: General Discussion

Hi, i wanted to know if some users have noticed something suspicious that happened to them under Qubes

---

## Memes about Qubes OS

> 板块: General Discussion

This topic is a place for all the wallpaper and memes about QubesOS that can be found on internet or that the community made or will make

Don't hesite to post what you have or even create new one for everyone to enjoy

Cheers

---

## Why doesn't split GPG allow certification of keys

> 板块: General Discussion

Prior to using Qubes, I was using PGP with a hardware key as the ultimate trust. I used the key certification this way: once I have gained enough confidence about some public key I downloaded online, I will certify (sign) it with my PGP key on the hardware key.

Now that I moved to Qubes, I found that split-gpg 1 and 2 specifically forbids this usage. Why? The documentation didn't discuss at length, only stating that
> Therefore, it cannot differentiate between e.g. signatures of a piece of data or signatures of another key.

But why is that a problem? I can understand that, if the OS in which gpg is invoked is compromised, then gpg can be altered to always support signed key regardless of whether it's genuine. But we have the public key with the signature as data, and we have an hypothetically uncompromised private key protected air-gapped. Thus, we can always move the data to another machine and verify there, which is very easy in Qubes: just open a new qube and check the key certification there; and the compromised VM can't fake that, under the hypothesis that the private key is protected.

Therefore, I don't understand the incentive behind the prohibition of key certification, and hope to discuss it.

Thanks in advance.

---

## ProtonVPN installation based in fedora-43 minimal

> 板块: General Discussion

Hello everyone 
I want to install ProtonVPN based fedora-43 minimal, then I wan't to create sys-prtonvpn and another firewall and then connect AppVM which I want to run through ProtonVPN Could you please guide me regards this matter step by step

---

## Is there a way to auto template ? ex. for gaming, for android, for tails, for windows vm, for compromised, etc

> 板块: General Discussion

I know what i asking is quite risky, but if this one liner template/script is openly at git we all can work together hardened those template right? and the most important is having those auto template in official community watch lists... so we know reviewed one and unreviewed one the open port risk, etc.

for example 1 liner to create a gaming one, including for nvidia or amd gpu after run that 1 liner user can just open it and start gaming without headache setting this and that in result quitting qubes-os

or maybe we want just office, you know those nasty office comms with dirty unclean viruses /malware infected documents lurking in an everyday low paid offices... like dude help me write simple website for this documents open up then virus inside, we can just kill that one and reuse the auto backup before virus hit...

---

## Is Firefox really an appropriate default browser for Qubes?

> 板块: General Discussion

I've known about this ever since I installed my own DNS qube a while ago, but now I just gotta ask... why the hell is Firefox allowed to be the default browser on a privacy/security OS when **every time I launch it** it wants to call all of its friends back home? Literally all of them, even its grandma.

Sample roster of domains Firefox (at least the one in the Fedora templates) likes to call on every launch:

* contile.services.mozilla.com
* detectportal.firefox.com
* push.services.mozilla.com
* content-signature-2.cdn.mozilla.net
* aus5.mozilla.org
* shavar.services.mozilla.com
* www.inverse.com
* newrepublic.com
* www.theguardian.com
* www.vulture.com
* www.newyorker.com
* f3.o.lencr.org
* ocsp.digicert.com
* www.nytimes.com
* services.addons.mozilla.org
* classify-client.services.mozilla.com
* normandy.cdn.mozilla.com
* foundation.mozilla.org
* safebrowsing.googleapis.com
* theatlantic.com
* push.services.mozilla.com
* play.forgeofempires.com
* img-getpocket.cdn.mozilla.net
* firefox.settings.services.mozilla.com
* eat.hungryroot.com
* www.slashfilm.com
* ww55.affinity.net
* www.nationalgeographic.com
* twitter.com
* www.wikipedia.org
* www.reddit.com
* www.getpocket.com
* www.mozilla.org
* www.youtube.com
* sitereview.zscaler.com
* restrictmoderate.youtube.com
* restrict.youtube.com
* www.youtube-nocookie.com
* youtube.googleapis.com
* youtubei.googleapis.com
* m.youtube.com
* forcesafesearch.google.com
* google.com
* www.google.com
* ocsp.pki.goog

All of the mozilla and firefox ones I understand, but... Twitter? NY Times? National Geographic? Slashfilms? What the heck is even Slashfilms and why do they need to be notified every time I launch my browser? This smells like either a) capitalism or b) surveillance and I'm praying it's just the former.

I don't know about y'all but I'm making it next weekend's project to completely remove this bloatware spyware from all of my qubes. Screw all 'em weird domains. I'll probably get Librewolf unless I get better recommendations.

---

## Is 4.3 sluggish for you?

> 板块: General Discussion

I upgraded one computer to Q4.3 and it seems to be much (much) slower all around.  Booting takes longer, each Qube takes longer to open, context menus and applications take longer to open, etc.  Even on old qubes running the old templates.

This is subjective and hard to test.  But does anyone else have a similar experience?

16GB i7 computer.  And it was very smooth and comfortable under Q4.2.  Did something change?

---

## Xsane problems

> 板块: General Discussion

So, I have run into an odd behavior in Xsane for some reason the the qube that runs this is behaving completely different from the template. I open Xsane and it scans for devices an that's fine. This qube just defaults to the first device. An for some reasons that device is not a working device. 

In the template I have the same problem with this device. However the template gives me a choice of what device I want to use. An then I am able to just choose the working one and Roberts your mothers brother it works. 

Any suggestions on how to fix this. or perhaps a better scanner util than Xsane.

Not sure it should go here mods feel free to move it If this is the wrong place.

---

## Defining our target audience for community guides, accessibility for new users

> 板块: General Discussion

Hi

I would like to initiate a constructive community discussion following some unexpected feedback regarding recent documentation updates aimed at new users.

The goal of this conversation is to collectively clarify: **What audience do we aim to serve, and what is the minimum skill level we deem necessary for a successful adoption of Qubes OS?**

My perspective is guided by the following points:

Reducing cognitive overload: I would like us to provide tools and guidance to people who have general computer knowledge (coming from Windows, macOS, Android, or user-friendly Linux distributions) and to assist them in their journey with Qubes OS without a heavy cognitive load of "how do I get this done on Linux." They already have a lot to understand.

All potential users are not tech professionals, nor they are tech enthusiast. Some just want to secure their computer and data. We should help users to focus their energy on what truly matters: understanding and using the security principles of Qubes OS.

Using Windows, macOS, Android, Ubuntu, or even Tails allows users to maintain daily productivity without having to learn terminal tricks for routine tasks. Why shouldn't this be an equally valid goal in Qubes OS?

I know Qubes OS is not easy and it's a patchwork of various things tied together that try to be consistent and usable. But we can certainly do something to help beginners to get started.

Providing support to users with less pre-existing knowledge and skills should not negatively affect the experience or functionality for our power users.

I look forward to hear other's thoughts on this topic. Thank you for your engagement everyone :)

---

## Survey: CPU and VM boot time

> 板块: General Discussion

# **Submitted data (Debian only)**
### Current release
|User | CPU | VM kernel ver. | VM boot time (s) | Storage type | Qubes OS ver. | Modifications|
|--- | --- | --- | --- | --- | --- | ---|
|@fiftyfourthparallel | i7-1065G7 | 6.19.5 | 4.8 | NVMe (brtfs) | R4.3.0 ||
|@fiftyfourthparallel | i7-1065G7 | 6.19.5 | 4.9 | NVMe (brtfs) | R4.3.0 | systemd-binfmt |

&nbsp;

### Modifications
| Name | Creator |
|--------------------|--------------------|
| [systemd-binfmt](https://forum.qubes-os.org/t/survey-cpu-and-vm-boot-time/2790/118) | @renehoj |

&nbsp;
### **Past releases**
[details="R4.2"]
|User | CPU | VM kernel ver. | VM boot time (s) | Storage type | Qubes OS ver. | Modifications|
|--- | --- | --- | --- | --- | --- | ---|
|@fiftyfourthparallel | i7-1065G7 | 6.1.62 | 4.6 | NVMe (brtfs) | R4.2.0 | |
|@augsch | R5-5600U | 6.1.x | 4.5 | NVMe (btrfs) | R4.2 Alpha | |
|@augsch | R5-5600U | 6.1.62 | 3.5 | NVMe (btrfs) | R4.2.0 | |
|@renehoj | 9950X | 6.10.3 | 2.9 | NVMe (btrfs) | R4.2.2 | systemd-binfmt|
|@renehoj | i9-13900k | 6.1.62 | 3.4 | NVMe (btrfs) | R4.2.0 | |
|@solene | i7-1260P | 6.1.56 | 4.6 | NVMe | R4.2-RC4 | |
|@DVM | i9-12900k | 6.6.8 | 3.6 | NVMe (btrfs) | R4.2.0 | |
|@johnboy | R7 5700G | 6.1.62 | 4.0 | NVMe | R4.2.0 | |
|@johnboy | N100 | 6.10.3-1 | 5.24 | NVMe | R4.2.2 | |
|@kenosen | i5-8350U | 6.3.33 | 4.3 | NVMe (btrfs) | R4.2.1 | |
|@neoniobium | i7-3840QM | 6.6.2 | 7.5 | NVMe | R4.2.0 | |
|@lywarkel | i5-8250U | 6.1.62-1 | 6.1 | NVMe | R4.2.0 | |
|@lywarkel | i5-8250U | 6.1.62-1 | 5.7 | NVMe | R4.2.0 | systemd-binfmt|
|@OvalZero | i5-1240 | 6.8.8-1 | 4.6 | NVMe | R4.2.1 | |
|@dhimh | i5-14500T | 6.6.42-1 | 3.4 | NVMe (btrfs) | R4.2.2 | systemd-binfmt|
[/details]
[details="R4.1"]
| User | CPU | VM kernel ver. | VM boot time (s) | Storage type | Qubes OS ver.
|--------|--------------|-----|--------|-------|--------|
| @fiftyfourthparallel  | i7-1065G7 | 5.10 | 7.9 | SSD | R4.1 Alpha
| @fiftyfourthparallel | i7-1065G7 | 5.16 | 6.1 | SSD | R4.1.0
| @fiftyfourthparallel | i7-1065G7 | 6.02 | 6.7 | SSD | R4.1.1
| @GWeck | i5-7200U | 5.10 | 9.2 | USB-SSD | R4.1 Alpha
| @GWeck | i5-7200U | 5.11 | 9.1 | USB-SSD | R4.1 Alpha
| @GWeck | i5-7200U | 5.11 | 7.4 | USB-SSD | R4.1 Alpha with xen-pi-processor
| @augsch | R5-5600U | 5.10 | 4.75 | SSD(btrfs) | R4.1
| @augsch | R5-5600U | 5.10 | 4.1 | SSD-4k? | R4.1
| @wind.gmbh | V1605B | 5.10 | 6.5 | SSD | R4.1 Alpha
| @johnboy | R5 2400G | 5.10 | 5.16 | SSD (sata, btrfs) | R4.1
| @johnboy | R7 5700G | 5.15 | 4.2 | SSD (nvme, btfs) | R4.1.2
| @Raphael_Balthazar | AMD A10-5750M | 5.4 | 11.6 | SSD | R4.1 Alpha
| @Sname  | i7-9750H | 5.10 | 4.0 | SSD | R4.1
| @51lieal | i7-10750H | 5.16 | 3.4 | SSD-4k | R4.1
| @stachrom | AMD Ryzen 7 5700G | 5.17 | 5.2 | SSD | R4.1
| @Sven | i7-3840QM | 5.10 | 8.3 | SATA-SSD (btrfs) | R4.1
| @BenT | i7-1260P | 6.1.11  | 8.3 | nVME SSD | R4.1.1
| @taradiddles | i5-13600K | 6.2.10 | 5.6 | nvME SSD | R4.1.2
[/details]
[details="R4.0"]
| User | CPU | VM kernel ver. | VM boot time (s) | Storage type | Qubes OS ver.
|--------|--------------|-----|--------|-------|--------|
| @fiftyfourthparallel  | i7-1065G7 | 5.10 | 4.7 | SSD | R4.0
| @fiftyfourthparallel | i5-10210U | 4.19 | 4.8 | SSD | R4.0
| @fiftyfourthparallel | i5-10210U | 5.6 | 5.4 | SSD | R4.0
| @GWeck | i5-6600 | 5.4 | 7.3 | SATA-SSD | R4.0
| @GWeck | i5-7200U | 5.4 | 7.4 | SATA-SSD | R4.0
| @GWeck | i5-7200U | 5.4 | 7.4 | USB-SSD | R4.0
| @GWeck | i5-7200U | 5.10 | 7.1 | USB-SSD | R4.0
| @GWeck | i5-7200U | 5.11 | 7.2 | USB-SSD | R4.0
| @augsch | E3-1231v3 | 4.9 | 8.0 | HDD | R4.0
| @wind.gmbh | i7-3520M | 5.4 | 8.2 | SSD | R4.0
| @johnboy | R5 2400G | 5.4 | 5.2 | SSD (sata, btrfs) | R4.0.4
| @den1ed | i5-8350U 1.70GHz | 5.10 | 13.1 | HDD | R4.0.4
| @beto |Xeon® Silver 4114|5.4|8.5| SSD |R4.0
| @beto |i5-7260U|5.4|6.9| SSD |R4.0
| @sergiomatta | AMD FX-8300 | 5.4 | 9.2 | HDD | R4.0
[/details]

&nbsp;

---

&nbsp;

> While looking through various Qubes forums, I noticed that prospective Qubes users tend to worry about whether their systems are powerful enough. I’ve also wondered what the impact of CPU power on Qubes OS’ operating speed is. There aren’t any good resources on this. Since I don’t have access to a bunch of computers to experiment on myself, I came up with a standardized test we can use to create a handy reference table.

From [this thread](https://forum.qubes-os.org/t/measuring-cpu-impact-on-qubes-operation-the-first-step-to-a-qubes-performance-benchmark/2720?u=fiftyfourthparallel).

*tl;dr - This is a crude test that aims to find out the impact of CPU power on VM start times*

&nbsp;

## **How to submit data**

1. Install a new copy of the latest Debian minimal template. The template can be installed by entering `qvm-template install debian-13-minimal` into dom0 (rename your existing installation if necessary). Do not update or modify this template before the test

2. Shut down all other VMs using `qvm-shutdown --all` (if needed, `--exclude sys-usb`)

3. Run `time qvm-start debian-13-minimal` and make note of the `real time` returned. We recommend you run this test multiple times to get a more reliable result. @wind.gmbh wrote a script that's short enough to manually enter into dom0:
- 
  [details="dom0 script"]
  ```
  #!/usr/bin/bash

  qube="debian-13-minimal"

  get_real_time() {
    realtime="$(/usr/bin/time -f "%e" qvm-start -q ${qube})"
    qvm-shutdown --wait -q "${qube}"
    echo $realtime 
  }

  benchmark() {
    qvm-shutdown --all --wait -q
    for ((i = 0; i < 10 ; i++)); do
      sleep 15
      echo "$(get_real_time)"
    done
  } 

  benchmark
  ```
  [/details]


4. Enter your details into the table below, with the time rounded to one decimal place. If you ran multiple tests, enter the average. **This is a wiki post, so click 'edit' below**

    - We'll assume you're using the latest Debian for your release unless otherwise stated. E.g. If posting for R4.2 today, it’s assumed you're using Debian 12. If for R4.3; Debian 13. There are holes in this method (e.g. someone who didn't upgrade, or later releases) but this should be a good-enough approximation and takes care of the issue without adding new columns

---

## How can I open an Application via dom0 keyboard shortcut?

> 板块: General Discussion

*I suspect another way to ask this would be: what dom0 command do I use to open 'Firefox' in the 'work' AppVM - if such a command exists, that's all I need.*

_____

By **Application** I mean an individual application inside of an AppVM.  For example, the 'Firefox' application inside of the 'work' AppVM.  

By **open** I mean launch, from any state. Including the AppVM being shutdown.

By **dom0** I mean you can use the keyboard shortcut anywhere, in any window. I'm effectively asking about global keyboard shortcuts.

I have found the following:

System Settings > Keyboard > Application Shortcuts > Add

However I am only able to figure out how to add commands that manipulate dom0. I haven't gotten any commands to manipulate an application in an AppVM. And at this point, I am unsure whether this is even possible. 

Google and this forum are also shockingly silent on this question. So my secondary motivation here is to help others in the future. I can't be the only person who would like this :)

---

## Running a minimal Xen setup without Qubes - lessons learned from building a ~13MB stateless dom0

> 板块: General Discussion

Hey all, wanted to share some findings from a project where we needed Qubes-style VM isolation but couldn't use Qubes itself due to TCB size constraints. We ended up building a bare Xen setup on Alpine Linux that replicates the core Qubes architecture (sys-net pattern, cross-domain IPC, PCI passthrough) in about 13MB of RAM with zero Python and zero QEMU. Figured some of this might be useful to others thinking about minimal Xen deployments or just curious about what Qubes is doing under the hood.

### The setup

Xen 4.17.6 hypervisor (later migrated to 4.19.5), Alpine Linux dom0 running entirely from a gzipped cpio in RAM. After GRUB loads the hypervisor, kernel, and rootfs, the NVMe is never touched again. Four VMs auto-start from cold boot:

- dom0: xl toolstack, IPC broker, no physical NIC after boot
- net-vm: PCI passthrough of physical NIC (ixgbe), acts as network driver domain
- sa-vm: PCI passthrough of USB controller, dedicated to a hardware security device
- workload-vm: application VM, connects through net-vm for external traffic

The whole thing boots to a fully operational state in about 45 seconds with zero manual intervention.

### Qubes-style routed networking without Qubes

This was one of the more interesting parts. Qubes uses routed /32 point-to-point links between VMs instead of bridging, which eliminates layer 2 attacks between sibling VMs. We replicated this pattern using vanilla xl and iproute2.

The key mechanism is Xen's vif hotplug scripts. When xl creates a VM with a vif, it calls a hotplug script that can configure the interface however you want. We wrote a custom `vif-route-sh` that reads the VM's IP from xenstore (set via the `ip=` parameter in the xl vif config), adds a /32 host route, and enables proxy_arp. That's it. No bridge, no brctl, no xenbr0.

The dom0 auto-start script does a NIC handoff at boot: dom0 starts with the physical NIC, fetches VM images from a build server over HTTP, then unbinds the NIC from ixgbe, hands it to pciback, and creates net-vm with PCI passthrough. Dom0's IP moves to the vif backend interface and routes through net-vm. If the fetch fails (build server unreachable), the script aborts and dom0 keeps its NIC as a fallback.

Net-vm has `ip_forward=1` and `proxy_arp` on both interfaces. The build server reaches dom0 and other VMs through net-vm's proxy ARP. Exactly the Qubes sys-net pattern, just without the Qubes toolstack.

### The Xen toolstack version matching trap

This one cost us real time. If you're running the Xen 4.17 hypervisor (like from a Qubes install), you need the 4.17 toolstack. Not 4.18, not 4.20. The domctl/sysctl hypercall interface versions must match.

The confusing part is that some commands work with a mismatched toolstack and some don't. `xl info` and `xl list` use the sysctl interface, which wasn't bumped between 4.17 and 4.19. `xl create` uses the domctl interface, which was bumped. So you get a system where `xl list` works fine but `xl create` fails with "Permission denied" which is actually a version mismatch, not an access control issue. The error comes from `do_domctl()` returning -EACCES when the version doesn't match.

On Alpine, the toolstack version maps to the Alpine release: 3.18 ships Xen 4.17, 3.19 ships 4.18, 3.20 ships 4.18, 3.21 ships 4.19. We extract just the xl binary, xenstored, xenconsoled, and the xen-libs from the correct Alpine version inside a Docker build container.

### PVH on 4.19: the good and the bad

We migrated from 4.17 to 4.19 specifically for PVH support. PVH gives you hardware VT-x CPU isolation with PV drivers and zero QEMU. It's basically the best of both worlds.

The good: PVH domUs without PCI passthrough work perfectly on 4.19. Our workload VM boots as PVH and has hardware CPU isolation with no device model anywhere.

The bad: libxl explicitly blocks PCI passthrough for PVH domUs on x86. The error is `passthrough not yet supported for x86 PVH guests`. This is a toolstack limitation, not a hypervisor one. The vPCI infrastructure exists in the hypervisor but nobody has written the libxl code path for PVH domU passthrough. The upstream work (there's a patch series going through many revisions) is about passthrough FROM a PVH dom0 TO HVM domUs, which is a different thing.

Also, PVH dom0 breaks the ability to pass devices to domUs entirely. The NetBSD Xen docs are explicit about this for 4.19.

So if you need PCI passthrough (we do, for the NIC and USB controller), those VMs must stay PV. The architecture ends up being: VMs with passthrough run PV, VMs without passthrough run PVH. For our use case, the workload VM (which handles sensitive data and external requests) gets hardware CPU isolation, and the driver domains get IOMMU DMA isolation with minimal kernels.

### Replacing qrexec

We built a custom IPC system in Rust that replaces qrexec for cross-domain communication. Transport is Xen vchan (grant-table shared memory + event channels). Dom0 runs a broker daemon that evaluates a policy file and routes service requests between VMs. Each VM runs an agent that fork/execs service handler scripts.

A few things we learned the hard way about vchan:

**The event channel fd is edge-triggered, not level-triggered.** After poll() returns POLLIN, if you call your recv function and there's no data, you MUST call `libxenvchan_wait()` to consume the stale event channel notification. Otherwise poll() returns POLLIN immediately again and you get a 100% CPU busy loop. This one was fun to debug on real hardware.

**xenstore permissions matter for vchan.** After creating a VchanServer endpoint in dom0, you must `xenstore-chmod` the path to grant the target domain read access. Without this, the guest's VchanClient can't find the endpoint.

**Domain IDs are dynamic.** Xen assigns them at VM creation time. If you destroy and recreate a VM, it gets a new domain ID. Any daemon that was talking to the old domain ID now has stale vchan endpoints. We handle this by reading domain IDs from `xl list` after creation and passing them to the daemon via `--listen domid:name` pairs. The policy file uses names, not IDs.

### Things that are different from what you'd expect

**No devtmpfs under Xen PV.** Alpine's mdev can't scan /sys/dev under Xen PV. You have to create /dev/xen/* device nodes manually by parsing /proc/misc with awk and calling mknod. Same for /dev/hvc0 (the console device under PV).

**DHCP doesn't work under Xen PV dom0.** BPF/packet sockets are restricted. Static IP only. This might be a kernel CONFIG_PACKET issue or a fundamental Xen PV limitation, we didn't dig further since static was fine for our use case.

**dom0_mem needs the max: qualifier on large memory systems.** On a 128GB machine, `dom0_mem=4096M` without `max:4096M` causes the kernel to allocate struct page metadata for the full 128GB reservation (~2GB overhead), consuming the entire dom0 allocation. System freezes during grant table init. The `max:` caps the reservation.

**hvc0, not ttyS0.** Under Xen PV, the interactive console is /dev/hvc0. ttyS0 is owned by Xen for kernel printk. Userspace programs that try to use ttyS0 as a terminal fail silently. This manifests as what looks like a frozen system but is actually a system running fine with invisible output.

### Was it worth it?

I'll let you be the judge. We went from a ~30GB Qubes install to a 13MB stateless image. No Python, no QEMU, no persistent disk state. But I wouldn't recommend this path for general use. Qubes handles an enormous amount of complexity that you don't appreciate until you have to reimplement it. The VM auto-start sequencing, the NIC handoff, the vif routing, the IPC policy engine, the serial console workflows for remote hardware with no physical access... it's a lot of plumbing. We also strictly do not require a desktop OS, we needed something closer to the Qubes Air / headless setup.

If you're curious about any of this or have thoughts on the PVH passthrough situation, would love to hear. The Xen community seems to be actively working on PVH dom0 passthrough for 4.21 but PVH domU passthrough doesn't seem to be on anyone's roadmap.

---

## [Hiring] Graphene OS Template Developer (AOSP)

> 板块: General Discussion

Quoting @michael from [developer's mailing list](https://www.qubes-os.org/support/#qubes-devel)
[quote]

hi folks,

just a heads-up that some funding continues to exist to port AOSP into Qubes OS:

https://github.com/QubesOS/qubes-issues/issues/2233#issuecomment-594893074

"If you're interested in the development and maintenance of a production-oriented port of AOSP to QubesOS including putting together integration for clipboard support, etc. and you have a record of open
source contributions and relevant experience (not necessarily with AOSPitself but Java / Kotlin app development experience would be good), contact us at contact@grapheneos.org

There is funding available to get someone a nice workstation and a small stipend to work on it, but we can't currently fully fund the develop work ourselves. There are likely organizations interested in this among those that we're in contact with though and I would expect that I couldget someone full-time funding to work on this if they got things rolling."

--
Michael Carbone

Qubes OS | https://www.qubes-os.org
@QubesOS <https://www.twitter.com/QubesOS>
[/quote]

Related: 

https://forum.qubes-os.org/t/graphene-os-template/2948

---

## I don't like the redesigned menu

> 板块: General Discussion

I despise what you've done to the Qubes menu in 4.2.

**Old** menu: Click on the Q, qubes appear immediately under your pointer for fast access. OS is usable!

**New** menu: Click on the Q, qubes are like three inches over to the left, making it slow and awkward to do literally anything. (My Q is on top right.)

---

**Old** menu: Select a qube, apps and settings are immediately next to your pointer for fast access

**New** menu: Select a qube, apps and settings are often way above your pointer so you have to do this careful dance of sliding your pointer over in a ~10px lane until you get to the app pane (otherwise you'll select a different qube) then carefully move up often several inches to the app you want.

---

This whole thing is fussy, fiddly, and fragile. I gave feedback on it (in various places) when it was ostensibly still being designed but it has the same horrific usability shortcomings I mentioned then and I'm hard pressed to find a single change made after what was framed as a feedback period.

Since it's unusable on the right side I've now moved it over to the left and will have to retrain 8 years of muscle memory (thanks!) but it's still an abortion of an interface even on the left.

---

## What would you like to see improved in Qubes OS?

> 板块: General Discussion

Hello,

What are the things you would like to see improved in Qubes OS? It's not that I'm going to implement them, but I'd be curious to know what drives the users, and what is important to them.

---

## A Reasonably Secure Agentic System

> 板块: General Discussion

A Reasonably Secure Agentic System: 
Split-Brain Implementation of OpenClaw (Clawdbot)

-- Introduction:

The rise of AI agents like OpenClaw (formerly Clawdbot) presents a significant security challenge: these agents require deep system access to be useful, but granting an LLM direct terminal access is a violation of basic security hygiene.

By leveraging Qubes OS, we can implement a Sovereign AI Orchestrator that is proactive and powerful, yet physically incapable of breaching the TCB (Trusted Computing Base).

-- The Architecture: Split-Brain Isolation

Instead of a monolithic installation, we fragment the agent into three compartmentalized layers:

1. The "Brain" (sys-clawd AppVM):
Runs the OpenClaw Node.js environment and holds API keys. It has network access but zero private data. It communicates only via restricted qrexec calls.
2. The "Nervous System" (Custom RPC):
A set of sanitized scripts in dom0 that act as an API. It translates AI "intent tokens" into system actions.
3. The "Muscles" (Target AppVMs):
Your existing Work, Personal, or Disposable VMs where the actual tasks (browsing, research, emailing) occur.


   Technical Implementation

-- 1. The dom0 Executor (The Policy Firewall)

We avoid passing raw strings to a shell. Instead, we use a strict case statement to whitelist allowed actions.

Path: /usr/local/bin/clawd-executor (in dom0)

```bash
#!/bin/bash
# Usage: <action> <target_vm> <parameter>
read -r action target_vm param

# Basic Sanitization: Ensure target_vm is alphanumeric
[[ ! "$target_vm" =~ ^[a-zA-Z0-9-]+$ ]] && exit 1

case "$action" in
    "open-url")
        # Opens a URL in the target VM's default browser
        qvm-run -q -a "$target_vm" "qubes-open-url '$param'"
        ;;
    "search")
        # Triggers a search engine query in the target VM
        qvm-run -q -a "$target_vm" "firefox --search '$param'"
        ;;
    "install-app")
        # Requires 'ask' policy for manual approval
        notify-send "AI Request" "Install $param in $target_vm?"
        qvm-run -u root "$target_vm" "apt-get update && apt-get install -y $param"
        ;;
    *)
        exit 1
        ;;
esac

```

--2. The Security Policy (The Gatekeeper)

Using the Qrexec Policy v2 (Qubes 4.1+), we ensure every mutating action requires a human OK.

Path: /etc/qubes/policy.d/30-user.policy

```text
# Read-only status checks: Always allow
custom.ClawdRead  * sys-clawd  dom0  allow

# System changes: Always ask for confirmation
custom.ClawdWrite * sys-clawd  dom0  ask,default_target=dom0


-- Use Case: Parallel Multi-VM Orchestration

The primary benefit is Identity Isolation. A single prompt to the agent can orchestrate complex, cross-domain workflows:

"Open YouTube in social-vm, prepare an email draft in work-vm, and research pelican biology in a disp-vm."

The agent dispatches three separate RPC calls. dom0 validates the VM names and launches the processes. From the perspective of the web services, these are three different machines with three different fingerprints, yet they are coordinated by your personal AI.

-- Risk Mitigation

- Compromise of sys-clawd: If the agent's VM is hacked, the attacker is trapped. They cannot read your vault or your personal files. They can only attempt to trigger the pre-defined RPC actions, which will trigger a dom0 "Ask" prompt on your screen.

- Prompt Injection: Even if an LLM is tricked into trying "rm -rf /", that string will simply fail the case statement in dom0. The malware has no path to execution.

--Final Thoughts

Implementing AI agents in Qubes OS turns the OS from a collection of silos into a coordinated organism without sacrificing the security that makes us use Qubes in the first place. By shifting the trust from the AI's logic to the hypervisor's RPC policies, we can enjoy the benefits of agentic automation while keeping the digital kingdom under lock and key.

---

## Thank you Qubes Devs and Contributors!

> 板块: General Discussion

In the years I have been using Qubes and lurking and in the two years I've been on the forum, I've recently seen a marked decline in support requests for big issues, and a marked increase in feature requests. To me, this is a milestone in project stability and usability and says that Qubes has matured. 

Don't misunderstand: there's still a long way to go with a mile-long list of great things to add, from the GUI and audio virtualization, to more OSes (even if just Mirage, *BSD, and non-systemd Linux e.g. Alpine), to WYNG backup or similar, etc.

But the point is that the work put into Qubes has paid off, Qubes is *very* usable and has accomplished its major goal of reasonable security, and I'm very grateful to all the devs and contributors. I see Qubes going very far, current events notwithstanding.

Congratulations and thanks. I appreciate you.

---

## Bounty Available (>$2,000) for QubesOS BusKill package

> 板块: General Discussion

Friends,

We're happy to announce that **[we have funding available to package BusKill in QubesOS](https://www.buskill.in/qubes-package-bounty/)** as a contrib package.

[![Bounty Now Available for BusKill Contrib Package in QubesOS](upload://sSQg4yr5ifYlQqujokMRDIlDRyq.jpeg)](https://www.buskill.in/qubes-package-bounty/)

Thanks to a generous donation from [NovaCustom](https://www.buskill.in/qubes-package-bounty/), we're offering a bounty to anyone (including you!) who packages BusKill as an official [contrib package](https://www.buskill.in/qubes-package-bounty/) for QubesOS.

# About BusKill

BusKill is a laptop kill-cord. It's a USB cable with a magnetic breakaway that you attach to your body and connect to your computer.

| [![What is BusKill? (Explainer Video)](upload://21RsYpynwbimCOktGzLZbLxP30d.jpeg)](https://www.buskill.in/#demo) |
|:--:|
| *Watch the [BusKill Explainer Video](https://www.buskill.in/#demo) for more info [youtube.com/v/qPwyoD_cQR4](https://www.youtube.com/v/qPwyoD_cQR4)* |

If the connection between you to your computer is severed, then your device will lock, shutdown, or shred its encryption keys --- thus keeping your encrypted data safe from thieves that steal your device.

# About NovaCustom

In Mar 2015, Wessel klein Snakenborg (founder of NovaCustom) started selling highly-customizable Linux laptops from Europe.

In Aug 2021, NovaCustom released their first laptop (NV40) with **coreboot pre-installed** with Dasharo.

| [![Photo of a screw that&#39;s been covered with a unique pattern of (multi-color) glitter nail polish](upload://iKlbcSkGDUDjohrulnUkMvh6PoJ.jpeg)](https://www.buskill.in/qubes-package-bounty/) |
|:--:|
| NovaCustom offers anti-tamper options, including <a href="https://www.buskill.in/qubes-package-bounty/">glitter nail polish applied to the chassis screws</a> (photos sent to you via Proton Mail before shipment — specify PGP key at checkout for e2ee) |


Since 2023, NovaCustom has been a leader in hardware security:

- In Apr 2023, NovaCustom started offering [**Intel ME disabling**](https://www.buskill.in/qubes-package-bounty/)
- In May 2023, NovaCustom demonstrated their commitment to free software and the security community by [obtaining **Qubes certification**](https://www.buskill.in/qubes-package-bounty/) on their [NV41 Series](https://www.buskill.in/qubes-package-bounty/) laptop.
- In Sep 2023, NovaCustom [started offering **anti-interdiction**](https://www.buskill.in/qubes-package-bounty/) services, which includes applying a unique glitter pattern to your new laptop's chassis screws before shipment. This was inspired by Michael Altfield's [article about Trusted Boot](https://www.buskill.in/qubes-package-bounty/),
- In Feb 2024, NovaCustom started selling their NV41 laptop with **[Heads](https://www.buskill.in/qubes-package-bounty/) pre-installed**
- In Sep 2024, NovaCustom's [V56 laptop became **Qubes Certified**](https://www.buskill.in/qubes-package-bounty/)
- In Nov 2024, [**NovaCustom partnered with BusKill**](https://www.buskill.in/qubes-package-bounty/) to bundle their security laptops with BusKill Kits, including the option to [**purchase BusKill Kits in-person** (with cash)](https://www.buskill.in/qubes-package-bounty/) at their brick-and-mortar office in The Netherlands
- In Feb 2025, NovaCustom's [V54 laptop became **Qubes Certified**](https://www.buskill.in/qubes-package-bounty/)
- In Mar 2026, NovaCustom donated \$200 to BusKill, for packaging and **documenting [BusKill in `apt`](https://www.buskill.in/qubes-package-bounty/)**, making it easier (and safer) to install BusKill on Debian-based Linux distros

And now, in Apr 2026, NovaCustom is further working to increase the accessibility of BusKill to QubesOS users, by sponsoring the submission of an official QubesOS contrib package.

## Funding Available

If you'd like to claim this bounty for yourself, please

1.  Read the [details of the bounty](https://opencollective.com/buskill/projects/qubes-package), and then
2.  Submit a proposal by commenting on [this GitHub issue](https://github.com/BusKill/buskill-app/issues/106)

 
**[Claim Bounty](https://opencollective.com/buskill/projects/qubes-package)**   

[opencollective.com/buskill/projects/qubes-package](https://opencollective.com/buskill/projects/qubes-package)

Moreover, if you're a QubesOS user and you'd like to donate additional funds in support of this bounty, you can do so [here](https://opencollective.com/buskill/projects/qubes-package/donate).

- [opencollective.com/buskill](https://opencollective.com/buskill/projects/qubes-package/donate)

 

Stay safe,  

The BusKill Team  
https://www.buskill.in/  
http://www.buskillvampfih2iucxhit3qp36i2zzql3u6pmkeafvlxs3tlmot5yad.onion

---

## Share your desktop screen / workspace

> 板块: General Discussion

I'm currently trying different ways to manage my desktop's look-and-feel, but many things don't work properly, are not meant to operate within the dom0 scope etc. So I wonder if you guys would like to share how you manage your workspace, what DE you use, what dock, what theme etc(without compromising your privacy of course)?
And you're welcome to share something beyond this scope if you'd like to of course, I'll be more than happy.

---

## WINDOWS 11 - Install as a template or as APP, the best solution

> 板块: General Discussion

Hi,
my next task is to install a Windows 11 environment to run a few applications, where no equivalent LINUX app is available. The data storage requirements are only a few Gigabytes and a large or heavy processing power is really not required.

What is the easiest way to install Windows 11- as template or directly as app ??

I am very much interesting about your arguments and I appreciate your valuable input very much. Many thanks in advance for your kind participation in discussing this matter.

reagrds, hitam

---

## QubesOS and tampering

> 板块: General Discussion

Hi, long time QubesOS user here.

I use a very portable laptop and I noticed secure boot doesn't work, any way to make it work?

other than that 

I've been leaving my laptop in my hotel rooms over the years and recently this month my rooms have been getting inspected so to say, any way or tips on how to tell if my laptop was tampered with while I was out or how could I detect a physical keylogger or so?

would qubesos sys-usb protect from physical keylogger or extraction?

---

## How does the Overlay FS of DispVMs protect against forensics?

> 板块: General Discussion

Hi, I've been out of Qubes for a month or so playing with Arch Linux, getting myself into hardening this Linux image and I've learnt a lot.
I managed to create a volatile system and this got me wondering... When changes are applied to, let's say, a Disposable VM, and this writes are written into the disposable filesystem overlay... How are this writes protected against forensics?
In RAM overlays is simple, once a system shutdown happens, it gets deleted. It could also be done with the `sdmem` utility to wipe the RAM overlay after the DispVM dies.
But what about Overlay filesystems running in the disk? The container gets discarded, but the contents are not wiped afaik (and that's ideal, i don't want constant writes into my SSD).
Is there a way to make that Overlay filesystem encrypted with a random key that resides in RAM and gets discarded after the DispVM dies, rendering the disk Overlay FS container unreadable after?

---

## Xen Project 2026Q1 Weather Report VODS

> 板块: General Discussion

For anyone interested in the work being done on the Xen Project, here is the YouTube VOD playlist for the 2026Q1 Weather Report.

[https://www.youtube.com/watch?v=_yCWatiejNA&list=PLQMQQsKgvLnuMxYmHPjQrQIJVK0n8wsjO](https://www.youtube.com/watch?v=_yCWatiejNA&list=PLQMQQsKgvLnuMxYmHPjQrQIJVK0n8wsjO)

The part about UEFI Secure Boot is by the Qubes OS project lead.

https://www.youtube.com/watch?v=67HK7svkqwM

---

## How to reduce the load when configuring Kicksecure as a service in Qube

> 板块: General Discussion

Is there any way to reduce the load when Kicksecure is configured as a service in Qube, since it slows things down significantly?

---

## How to install Signal cli from github to Qubes os

> 板块: General Discussion

Hello everyone 
I wan't install Signal-cli  in Qubes OS  
 Could you please guide me

---

## Split ssh, gpg, or ? for commit signing

> 板块: General Discussion

As the title says, which is better for security and streamlined workflow given the features qubes-os has? Is there a better way to sign git commits?

Working with others who also use qubes.

---

## Spectrum OS Discussion

> 板块: General Discussion

Hi all,

I recently learned of [Spectrum OS](https://spectrum-os.org/) from this tweet:

https://twitter.com/pavolrusnak/status/1327943049842921472

[Quick summary from the developer, Alyssa Ross](https://github.com/sponsors/alyssais):
> a NixOS distribution focused around security through compartmentalisation in the style of Qubes OS, but with the diversity of hardware support and ease of maintenance afforded by the Linux kernel and Nix.

On the [motivation](https://spectrum-os.org/motivation.html) page, there's a discussion of Qubes:

> **Existing implementations of security by compartmentalization**
> 
> **Qubes OS**
> 
> Qubes OS is a distribution of the Xen hypervisor that isolates IO and user applications inside their own dedicated virtual machines. Many people interested in secure computing are aware of Qubes, however they are often hampered by usability issues:
>  - Hardware compatibility is extremely limited. People often have to buy a new computer just to use Qubes, and even then it can be a struggle to set up.
> 
>  - People are reluctant to use Xen on their computer for power management etc. reasons.
> 
>  - VMs are heavy, and there is no isolation between applications in the same domain (VM).
> 
>  - GUI applications are buggy, command line tools are mostly undocumented.
> 
>  - Maintaining many different TemplateVMs with persistent state is difficult. (Qubes can use Salt to mitigate this.)
> 
> It is important to note, however, that the Qubes developers have created utilities for using compartmentalized environments that could be very useful to other implementations. For example, Qubes allows clipboard data to be safely shared between isolated environments with explicit user action on both ends, and Qubes Split GPG allows one environment to perform operations using a GPG key stored in another environment, with permission granted on a per-operation basis.

The design page goes into more detail:

https://spectrum-os.org/design.html

I thought this might make make for an interesting discussion topic, and I'm curious to hear what you all think.

---

## Global clipboard improvement ideas

> 板块: General Discussion

Hello,

Global clipboard is very good for security but current implementation is very inconvenient. Example to copy from a web browser in one domain to a terminal in another domain.
1. Select text and press Ctrl+C. Make sure you don't press Ctrl+Shift+C, the combination you use to copy in a terminal, this opens the web inspector. As a consequence of habit I sometimes do this.
2. Use the Win+Shift+C to copy to global clipboard.
3. Select the the terminal window. Press Win+Shift+V to paste to terminal domain.
4. Press Ctrl+Shift+V to paste in terminal. Make sure you don't press Ctrl+C, this combination closes the active running program, this is bad if a CLI program is running and you want to paste some input. This has also happened to me a couple of times.

I personally use Win+C and Win+V for global clipboard to make things a little easier but it is still error prone. Suggestions:
1. Have the global clipboard run in parallel with the domain clipboards. Skip the step to copy to domain clipboard and allow direct copy to global clipboard by selecting text and directly use Win+C to copy to global clipboard. When you paste the global clipboard in another domain use Win+V to directly paste from global clipboard.
2. Allow pasting multiple times from global clipboard. If I need to copy from one domain to multiple domains it becomes very tedious... Achieve this by using a keepassxc style timer for global clipboard storage. After 10-15 seconds wipe the contents of global clipboard. 
3. Integrate global clipboard copy/paste in dropdown menu's. This probably isn't technically feasible but I just thought to throw this in.
4. In the tray icon for the global clipboard add option to copy and paste to global clipboard. This is useful if you use the mouse a lot, no need to touch the keyboard, do all operations from tray icon.

Thoughts ?

---

## Does any Qubes like Linux distro exist?

> 板块: General Discussion

From such distro I would expect:

* easy way to run every app in different user or container
* display all of such users'/containers' windows on some "master" user's display
* able to pass devices to such users/containers
* able to use different network for each user/container (for example different VPN servers simultaneously, or no VPN at all)

---

## Is anybody running Qubes on IntelME\AMD-PSP -free hardware?

> 板块: General Discussion

The most recent CPU lineup without such things is AMD 2011 bulldozer (Intel adds IntelME in everything since [2008](https://semiaccurate.com/2017/05/01/remote-security-exploit-2008-intel-platforms/); and AMD adds AMD-PSP since [2013](https://hothardware.com/news/amd-confirms-it-will-not-be-opensourcing-epycs-platform-security-processor-code)). 
Desktop Bulldozer CPUs (aka Zambezi) allow up to 32GB RAM, AMD-V, presumably RVI.
There are even [1 person in the whole HCL](https://www.qubes-os.org/hcl/#asus_crosshair-v-formula_amd-fx-8150_radeon-hd-4870-x2_randy-rowland_r3-2) who runs such CPU (8150)! But their sound is not working. Also table shows that it lacks IOMMU.

I wonder,
1) what would be the best qubes-compatible option to run bulldozer?
2) what threats presents lack of IOMMU and are there any options for mitigation?

---

## How can I successfully install Qubes OS on my laptop?

> 板块: General Discussion

Hi, I'm Dheeraj Sudan from the UK. I'm a software developer and also run a business with my wife Meenu Hinduja. I’m planning to install Qubes OS on my laptop, but I want to make sure I do it correctly and avoid common issues. I’d really appreciate any advice or suggestions from those with experience.

Regards
Dheeraj Sudan and Meenu Hinduja

---

## Booting a Stateless Alpine Linux Xen Dom0 from RAM

> 板块: General Discussion

Greetings. I am a longtime user of Qubes and have always had great interest in the bones and inner workings of the platform. I understand there has been interest in removing fedora as a dependency from dom0 for some time now. We recently carried out some research into a micro-kernel adjacent construction using Alpine linux as a base for dom0 in Xen. We wanted to share our notes here, in case this is ever of use to the community for future Qubes developments. 

TLDR: We were able to boot a fully RAM-resident Xen + Alpine linux for dom0 as the base. We believe this research is valuable to eventually migrate Qubes away from Fedora as the base for dom0.

## Summary

We booted a custom Alpine Linux dom0 under Xen 4.17 entirely from RAM on a 128GB server with no disk dependency after initial GRUB loading. The final image is a 34MB gzipped cpio archive containing a complete Xen toolstack, OpenRC init system, and SSH server. This post documents the specific technical problems encountered and their solutions.

## Motivation

The goal was a minimal, stateless Xen dom0 that runs entirely from tmpfs. No persistent storage after boot. Power cycle returns the system to a known-good state from the same image. The dom0 provides the Xen toolstack (xl, xenstored, xenconsoled), SSH access, and the ability to create and manage domU virtual machines.

## Boot Chain

The final working boot chain is:

```
UEFI PXE -> pxelinux (LOCALBOOT 0) -> NVMe EFI partition -> GRUB 2.06
  -> multiboot2 Xen 4.17.6 hypervisor
  -> module2 Alpine Linux 6.18.7-lts kernel (PV dom0)
  -> module2 --nounzip 34MB gzipped cpio rootfs
  -> OpenRC -> xenstored, xenconsoled, sshd
  -> Login prompt on hvc0
```

GRUB loads three files: the Xen hypervisor binary, the Linux kernel, and the rootfs archive. The kernel unpacks the cpio into tmpfs and runs /sbin/init. After GRUB finishes, the NVMe is never accessed again.

## Building the Rootfs

The rootfs is built inside a Docker container running Alpine 3.23. Base packages (openrc, openssh-server, dhcpcd, busybox) come from Alpine 3.23 repos. The Xen toolstack comes from Alpine 3.18 repos to match the 4.17 hypervisor (more on why below). Kernel modules are extracted from Alpine's modloop squashfs, trimmed to a allowlist of ~60 modules needed for the specific hardware, and bundled into the cpio along with all config files, SSH host keys, and an authorized_keys file. The entire build takes about two minutes.

The cpio is created with `find | cpio -o -H newc | gzip -9` from the container's root filesystem, excluding /proc, /sys, and /dev virtual filesystems.

## Problem 1: Console Under Xen PV

Symptom: After the kernel printed "Run /sbin/init as init process", the system appeared to freeze. No output, no response. This happened consistently.

Cause: Under Xen PV, dom0's interactive console is /dev/hvc0, not /dev/ttyS0. The physical UART (ttyS0) is owned by Xen for kernel printk output only. Userspace programs that try to open ttyS0 as a terminal fail silently. The system was actually booting and running OpenRC the entire time, but all output and the login prompt were going to hvc0 which was not connected to the serial console.

Fix: Add `console=hvc0` to the kernel command line (in addition to `console=ttyS0` for kernel messages). Configure the inittab getty to use hvc0:

```
hvc0::respawn:/sbin/getty 115200 hvc0
```

Both `console=ttyS0` (kernel messages visible through the serial port) and `console=hvc0` (userspace getty visible through the same serial port via Xen's console multiplexing) are needed.

## Problem 2: Xen Toolstack Version Mismatch

Symptom: xenstored failed to start with "FATAL: Failed to open connection to gnttab: No such file or directory". This happened even with all xen-gntdev, xen-gntalloc, and xen-privcmd kernel modules loaded and /dev/xen/ device nodes present.

Cause: Alpine 3.23 ships Xen 4.20 toolstack packages (xen-libs, xen, xl, xenstored). Our hypervisor was Xen 4.17.6. The Xen toolstack communicates with the hypervisor via domctl and sysctl hypercalls that include an interface version field. These version constants changed between 4.17 and 4.20. The 4.17 hypervisor rejected every hypercall from the 4.20 toolstack with a version mismatch error.

This is documented: libxenctrl (libxc) has an unstable ABI that must match the hypervisor version exactly.

Fix: Install the Xen toolstack from Alpine 3.18 repos, which ships Xen 4.17:

```bash
apk add --no-cache \
    --repository=http://dl-cdn.alpinelinux.org/alpine/v3.18/main \
    --repository=http://dl-cdn.alpinelinux.org/alpine/v3.18/community \
    xen
```

After this change, xenstored started cleanly and `xl list` showed Domain-0.

## Problem 3: Device Node Creation Without devtmpfs

Symptom: Even with kernel modules loaded successfully (confirmed via lsmod and /proc/misc), /dev/xen/ did not exist. xenstored could not open /dev/xen/gntdev.

Cause: Alpine's OpenRC boot environment uses mdev (BusyBox's lightweight device manager) instead of udev. devtmpfs was not mounted at /dev. The kernel registered all Xen misc devices in /proc/misc with correct minor numbers, but without devtmpfs or a working mdev scan, no device nodes were created in /dev.

Running `mdev -s` failed because /sys/dev did not exist in the Xen PV dom0 environment (PV dom0 has a stripped-down sysfs).

Fix: Create device nodes manually from /proc/misc in the boot init script. All Xen devices are misc devices with major number 10:

```sh
mkdir -p /dev/xen
awk '/xen\//{split($2,a,"/"); mknod="/dev/xen/"a[2]; system("mknod "mknod" c 10 "$1" 2>/dev/null")}' /proc/misc
chmod 600 /dev/xen/*
```

This reads /proc/misc, finds all entries under the xen/ namespace, extracts the minor number, and creates the device node. No udev, no mdev, no devtmpfs required.

The hvc0 console device also needed manual creation:

```sh
[ ! -e /dev/hvc0 ] && mknod /dev/hvc0 c 229 0 && chmod 666 /dev/hvc0
```

## Problem 4: dom0_mem and the Struct Page Trap

Symptom: Intermittent freezes during early kernel boot at "Grant tables using version 1 layout". The freeze was sensitive to rootfs size (34MB froze, 48MB sometimes worked). Removing dom0_mem entirely caused a different failure: "VFS: Unable to mount root fs on unknown-block(0,0)".

Cause: On a 128GB system, the Xen `dom0_mem` parameter has a subtle and destructive interaction with the Linux kernel's memory management.

With `dom0_mem=2048M` (no `max:` qualifier): Xen allocates 2GB to dom0 but sets the maximum reservation to the full 128GB. The Linux kernel allocates struct page metadata for all 128GB of potential pages, roughly 33.5 million pages at 64 bytes each, consuming approximately 2GB. This exhausts the entire dom0 allocation before the kernel reaches grant table initialization.

Without any `dom0_mem`: Xen gives dom0 nearly all 128GB. The resulting memory layout places the initramfs at a high physical address that becomes inaccessible due to e820 memory map conflicts in the PV dom0 builder. The kernel cannot extract the cpio, finds no rootfs, and panics trying to mount block device (0,0).

This is documented in the Xen Project blog post "Dom0 Memory, Where It Has Not Gone" and is the reason Qubes OS always specifies both min and max qualifiers.

Fix: Always specify both the allocation and the maximum:

```
dom0_mem=4096M,max:4096M
```

The `max:4096M` caps the maximum reservation, reducing struct page overhead to ~64MB and leaving 3.9GB for the kernel, initramfs extraction, and normal operation. 4GB provides comfortable headroom for a RAM-only rootfs.

## Problem 5: Module Dependencies in Trimmed Rootfs

Symptom: NIC drivers (ice, ixgbe) and USB host controller (xhci-hcd) failed to load with "Unknown symbol" errors. The ice driver couldn't find hwmon symbols, ixgbe couldn't find mdio/libphy symbols, xhci-hcd couldn't find usbcore symbols.

Cause: The module whitelist in the build script included the top-level drivers but not their dependency modules. When the modloop was trimmed from ~3700 modules to ~60, the dependency modules were stripped out. depmod regenerated modules.dep correctly for the remaining modules, but modprobe couldn't resolve the dependency chain because the required .ko files were missing from the filesystem.

Fix: Add the dependency modules to the whitelist:

```
hwmon          # needed by ice, ixgbe, nvme
libphy phylib  # needed by ixgbe (mdio bus)
usbcore usb-common  # needed by xhci-hcd
```

## The OpenRC Init Script

All of the Xen-specific boot logic is handled by a single OpenRC init script that runs in the boot runlevel before xenstored:

```sh
#!/sbin/openrc-run
description="Mount xenfs and load Xen modules"
depend() {
    need modules
    before xenstored
}
start() {
    ebegin "Loading Xen modules and mounting xenfs"
    modprobe xen_gntdev
    modprobe xen_gntalloc
    modprobe xen_privcmd
    modprobe xen_evtchn
    mkdir -p /dev/xen
    awk '/xen\//{split($2,a,"/"); m="/dev/xen/"a[2]; system("mknod "m" c 10 "$1" 2>/dev/null")}' /proc/misc
    chmod 600 /dev/xen/*
    [ ! -e /dev/hvc0 ] && mknod /dev/hvc0 c 229 0 && chmod 666 /dev/hvc0
    mkdir -p /proc/xen
    grep -q xenfs /proc/mounts || mount -t xenfs xenfs /proc/xen
    eend $?
}
```

This loads the four required Xen kernel modules, creates device nodes by parsing /proc/misc, creates the hvc0 console device, and mounts xenfs. After this script completes, xenstored can start and xl commands work.

## GRUB Configuration

The final working GRUB entry:

```
menuentry 'Alpine Xen 4.17 (dom0)' {
    insmod part_gpt
    insmod ext2
    insmod multiboot2
    search --no-floppy --fs-uuid --set=root <BOOT_PARTITION_UUID>
    multiboot2 /xen-4.17.6.gz console=com1,vga com1=115200,8n1 dom0_mem=4096M,max:4096M gnttab_max_frames=256 gnttab_max_maptrack_frames=1024 smt=off
    module2 /vmlinuz-alpine-lts rdinit=/sbin/init console=tty0 console=ttyS0,115200 console=hvc0
    module2 --nounzip /alpine-dom0-rootfs.gz
    boot
}
```

Key parameters:
- `dom0_mem=4096M,max:4096M` with the max qualifier to prevent struct page exhaustion
- `gnttab_max_frames=256` increased from default 64 for headroom
- `--nounzip` on the rootfs module to prevent GRUB from decompressing before Xen passes it to the kernel
- `rdinit=/sbin/init` to run OpenRC directly from the cpio rootfs
- `console=hvc0` for userspace output through Xen's console

## Final State

The system boots to a login prompt in approximately 3 seconds after GRUB hands off to Xen. The running dom0 provides:

- Xen hypervisor with full HVM, IOMMU, and HAP support for creating isolated domU VMs
- xl toolstack (xl list, xl create, xl info all functional)
- xenstored and xenconsoled running
- SSH server listening on port 22 with key-based authentication
- 127GB of free memory available for domU allocation
- 34MB total footprint, running entirely from RAM
- Stateless operation: power cycle returns to identical known-good state

## Lessons

1. When running under Xen PV, the userspace console is hvc0. The serial port (ttyS0) is for kernel messages only. This one fact explains an entire category of "system appears frozen" reports.

2. On systems with large RAM (64GB+), `dom0_mem` without `max:` is a trap. The kernel allocates struct page arrays for the maximum reservation, not the current allocation. Always specify both.

3. The Xen toolstack version must exactly match the hypervisor. The domctl/sysctl hypercall interface is versioned and there is no backward compatibility.

4. Minimal Linux environments (Alpine with mdev/busybox) that lack devtmpfs and udev need manual device node creation for Xen interfaces. Reading /proc/misc and calling mknod is reliable and dependency-free.

5. A complete Xen dom0 with toolstack, SSH, and networking fits in 34MB. Most of that is kernel modules. The userspace toolstack and init system together are under 10MB.

---

## Are these reasons valid to install and use Qubes?

> 板块: General Discussion

Hello,

I don't trust current geopolitical situation in general and I want to be well prepared for time, when software and speech freedom were significantly limited. What I want to achieve is to be prepared for hard times in the future, which we cannot predict of course, not to protect myself against advanced attacks because my threat model requires it, I'm not journalist, activist, whistleblower etc. I live in civilized EU country also.

Do you think that keeping Qubes OS installed on the separate disk apart from main Linux distro is a good idea? If the answer for that question is no, what do you think instead about installing Tails on some pendrive and upgrading it regularly and having Tails for bad times? What do you think about both?

My next motivation to install Qubes OS is just to learn cybersecurity, how Qubes OS works and testing or just isolating untrusted stuff in VMs.

---

## Using Qubes in windowed (non-seamless) mode (gui integration)

> 板块: General Discussion

Lately I've been tinkering around trying to get full desktop environment out of Debian and Fedora xfce templates. More specifically, I am curious to know what exactly prevents them from showing me their beautiful whiskers. I also want to do it without uninstalling stuff, just a reconfiguration, as minimal as possible, preferably easily reversible. Here's what I come up with:

```bash
#!/usr/bin/env bash
qvm-clone fedora-42-xfce mushroom
# run `systemctl set-default multi-user.target` to revert this
qvm-run -u root mushroom -- systemctl set-default graphical.target
 # Fedora login screen won't let you through without a password, and auto-login doesn't work for some reason.
qvm-run -u root mushroom -- 'echo "user" | passwd --stdin user'
qvm-prefs mushroom debug true
qvm-prefs mushroom virt_mode hvm
qvm-prefs mushroom kernel ''
qvm-prefs mushroom memory 1000
qvm-prefs mushroom maxmem 0
qvm-service mushroom lightdm on
qvm-shutdown mushroom
```

```bash
#!/usr/bin/env bash
qvm-clone debian-13-xfce plank
qvm-run -u root plank -- mv /etc/X11/xorg-qubes.conf /etc/X11/xorg-qubes.conf.backup
qvm-prefs plank debug true
qvm-prefs plank virt_mode hvm
qvm-prefs plank kernelopts "systemd.unit=graphical.target" # thanks ddevz!
qvm-service plank lightdm on
qvm-shutdown plank
```
I don't like two things about this. First, both cases require setting virt_mode to hvm - otherwise you won't get the window upon starting your vm. It would be nice to have a full-desktop pvh. Second, fedora boots and works with qubes kernel but won't start desktop environment (or at least it doesn't display it), which forces me to use distribution kernel and disable memory balancing. Not cool.

Perhaps most interesting discovery is the lightdm service. From `qvm-service` manual:
```rst
       lightdm:
              Default: disabled

              Start lightdm and avoid starting  qubes-gui-agent.   In  this  case,
              lightdm is responsible to start the X.org server.
```
Mainly because nobody seems to be aware of it on this forum, at least not in the related topics I have checked. It also doesn't do everything that manual says - it doesn't result in working xorg. You still need to set graphical target.

It would be nice to see full desktop VMs as first citizens in qubes. Without the jank of unresizeable window, at least. Right now we're mildly stuck with the templates we have.

Why am I doing this? 
![](upload://p6ucx9TVOJ0uHYI2TpLDt3z5Td4.png)
For fun, I guess. Speaking of fun: if you get full desktop in a template, windows there are marked as dom0's:
![mushroom|647x500, 100%](upload://orlEg3dgU6U42FFznKUwMwg7Bqm.png)

---

## Thunderbird absence

> 板块: General Discussion

I just installed the Fedora 43 xfce template for Qubes 4.2.4 and 'dnf list thunderbird' told me that the latter was not installed.  This is odd.  I had no trouble installing it, of course, but is it supposed to be absent or is my template broken?  As far as I know there could be other issues with it as well that I don't see.

I can't find any mention of such a change in the github issues or in any of the mailing lists.  There were no issues during template installation.

---

## Qubes OS Wallpapers

> 板块: General Discussion

What would you say if we gathered here creative ideas for making qubes os wallpapers? Do you like high tech wallpapers or do you prefer something minimalist like the one I made?

---

## 4.3-rc2 ISO is it safe to use?

> 板块: General Discussion

I have a USB flash drive that I fully trust because I have used it to install Qubes for years. Unfortunately, it is only 8 GB, and the Qubes ISO exceeded this size by 100 MB in the latest release. I noticed that 4.3-rc2 is the latest ISO that fits my USB stick. My question is: is it safe to use 4.3-rc2 and then update my system using qubes-dom0-update? What commits have been made since RC2; is there anything critical for security that updating from RC2 would not address?

Also, it would be great to have official signed ISO images without Fedora templates; I think that would reduce the size significantly. I don't use Fedora at all for my VMs, and there may be others like me. I could buy a larger USB flash drive, but it wouldn't be as safe as using my old stick that I fully trust.

Thanks.

---

## does anyone here play windows based games on wine using qubes?

> 板块: General Discussion

Hi, good evening.. is anyone here playing windows-based games on qubes? I tried running it on wine but couldn't because it can't play with a virtual machine.. I ran it without gpu passthrough and I tried playing growtopia.. thanks

---

## Questions before installing Qubes OS

> 板块: General Discussion

What performance should I expect if I decide to install Qubes OS on corebooted Lenovo ThinkPad X220 with the specs: Intel Core i5-2540M, 16 GB RAM, SATA SSD and on the second PC with 32 GB RAM, Intel Core i7-8750H CPU, NVME disk?

Can I run every task like running Docker containers, IDEs on the Qubes like I did on the Arch Linux, Gentoo?

Can Qubes OS be customized to run on ZFS or btrfs for example and to use some favorite lightweight window manager instead of Xfce?

Can I do GPU passthrough on Qubes and Qubes OS be used for running LLMs, compiling larger apps, playing games, commercial applications without significantly degrading performance if I run this stuff on top PC with spec like AMD Ryzen 9 9950X and 128 GB RAM?

---

## Arguments and use cases for and against qubes

> 板块: General Discussion

I have been going around making an argument that roughly goes something like:
"If you 1) care about not having backdoors and 2) run a bunch of un-audited code then you should use qubes because without qubes those are mutually exclusive".

This argument is not precise or technically true, but gets my view across pretty well.
I tend to make this argument to developers and since basically every single person cares about not having backdoors and since developers run a bunch of un-audited code I personally believe all developers should basically run qubes.

However I'm looking to explore counter-arguments to this. The most obvious one I can think of is that there is a bunch of "un-audited" code that a lot of people feel very comfortable running. Most standard linux distributions are un-audited from the perspective of the runner but they trust that the maintainers of the distro audit for them.
If someone responded to me and said "well I run a debian server for my web service and that seems totally fine" I think I wouldn't have much of a comeback to that.

I'm curious what you guys think of my argument. Good? Bad? Too simple?
Please come with counter-arguments and nitpicks as well as arguments you yourself think are stronger or alternative.

---

## RELIANT - Deniable encryption for Qubes OS

> 板块: General Discussion

Many users have been requesting plausible deniability in Qubes in some form, either for the installation as a whole or specific qubes. RELIANT is a project that provides multi-level plausible deniability in Qubes via [Shufflecake](https://shufflecake.net/), a modern deniable encryption system.

* dom0 is made live/volatile via intrinsic systemd functionality.
* Deniable qubes are stored in Shufflecake volumes.
* During boot you enter the standard LUKS password for dom0, and the Shufflecake password for the top volume you want to decrypt.
* RELIANT facilitates this through initramfs and userspace tooling.

We emphasize the importance of preventing and avoiding leakage of any information, direct or indirect, about the hidden volumes and qubes within. This is largely addressed by moving dom0 to RAM, supported by hash verification of non-volatile storage media. But there are side channels we cannot address, such as traffic analysis or eavesdropping. For more information, see the [README](https://codeberg.org/andersonarc/reliant-system/src/branch/master/README.md#).

The project is in a highly experimental state and uses several features not officially supported by QubesOS, and I do not have the time or resources to maintain a fork. However, subject to the developers' approval, I can start working on patches that will bring the necessary functionality into core Qubes codebase.

If anyone is interested in testing the system, I would be happy to provide support if you contact me. I have tested it myself and it does work, but as a developer I will inevitably be biased, especially regarding usability and convenience.

**Q:** How to update dom0 or templates?

**A:** There is a Maintenance Mode which can be entered by erasing `systemd.volatile=overlay` from the GRUB command line.

**Q:** Does volatile dom0 require lots of RAM?

**A:** Not really - most devices which can run Qubes, can run RELIANT as well.

**Q:** How to copy files between qubes?

**A:** Never copy directly between hidden qubes in different Shufflecake volumes - this will reveal the source qube's existence and name to the target. Use a proxy disposable qube.

**Q:** What are the prerequisites for installation?

**A:** Enough free space on disk for the Shufflecake partition, a bootstrap qube with Docker, good knowledge of Linux and Qubes for troubleshooting.

---

## Securing file integrity in offline storage qubes

> 板块: General Discussion

This is likely discussed elsewhere, but I couldn't find anything.

Threat model: a sophisticated and motivated adversary that targets us specifically. They can't compromise the Qubes isolation - they can't "break out of" a qube by compromising Xen or any of the Qubes code that insures isolation, or by exploiting a hardware side-channel vulnerability. Their goal would be to exfiltrate data or compromise as many qubes as possible.

We have an offline storage qube storage-1 that acts as file storage for documents, book, media and so on. If all we do is send files to storage-1 and open them in storage-1, any malicious file that could exploit storage-1 (e.g., a pdf exploiting the pdf reader) shouldn't be to exfiltrate any data since storage-1 is offline. An "offline" qube is, of course, one with "none" as the netvm, as well as "offline" disposable qubes that could be spawned from it.

However, we often need to send files *from* storage-1 to another, networked qube - in order to send them to someone else, for example.

How can we be sure that the file we sent to storage-1 (e.g., doc.pdf) is the same file leaving storage-1 afterwards, and not a file that renders as the same pdf, but, for example, includes a list of all other files in storage-1? Surely a malicious pdf would be able to somehow append "`find ~ -type f`" to any file without us noticing.

I can think of a few solutions:
1. Never open anything in storage-1.
1.1. Always open files in another offline qube using the "View in disposable qube" option.
This would ensure the integrity of the files in storage-1, as the "View in disposable qube" option doesn't modify anything on the source qube.
The downside is that it would be slow, as for each file we want to view, we would have to spawn a new disposable qube.
1.2. Always open files in another offline qube ("storage-2") that's dedicated to viewing files, but is not disposable.
This would be much faster, as we would only need to `qvm-copy` the file from storage-1 to storage-2.
Possibly we can make this easier from a UI point of view with dedicated GUI options like "View in storage-2".
However, storage-1 could still be compromised even without opening files in it - for example, by the file manager that parses the filenames and metadata.

2. Have storage-1 access the storage in a read-only way.
I'm not sure how that would work, but we can send a file to a qube ("storage-0") that only stores the files and doesn't spawn a file manager or much of anything. We can then access that storage from storage-1 by exposing storage-0's storage as read-only. One issue with that is that we'd need to organize the files in storage-0, which would leave us vulnerable to file manager or terminal exploits via filenames or file metadata when we move files around in storage-0. Otherwise, we would have all files in storage-0 in ~/QubesIncoming, which is not practical. Also, it seems like some of the filename or metadata exploits would still affect the storage-0 qube. 

4. Calculate the hashes of files sent to storage-1 and compare them to files sent from storage-1. If we receive "doc.pdf" and send it to storage-1, another qube (or service?) in between could hash the file and add an entry like "`f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2 doc.pdf`" outside storage-1. Later, when we want to send doc.pdf from storage-1, the same qube or service could hash the file again and check if it has that hash ("`f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2`") in its records, and if the filename is the same as "doc.pdf". This could be presented to the user with a prompt that shows the hash, the filename and whether the hash or the filename has changed since the table had been updated before with that entry. There could be several scenarios for what the prompt would show:
* "hash and filename match" - the user is safe to assume that this is the same doc.pdf they sent to storage-1 in the first place;
* "hash match and name mismatch" - the user would have to decide whether they renamed doc.pdf to something else, or if doc.pdf was maliciously switched with another file (e.g., "super_secret_doc.pdf").
* "hash mismatch" - the user would have to decide whether they edited doc.pdf. They could run a diff in another qube to see the changes. That could happen after extracting an archive, as well, since the hashes of the newly-extracted files wouldn't be recorded. So the user would have to consider that.

I'm not sure about how likely it would be to compromise a qube just via the filenames and metadata, how easy and useful it would be to expose one qube's storage as read-only to another qube, or how easy and useful it would be to calculate the hashes of incoming and outgoing files. I'm looking forward to a productive discussion on this.

---

## ParrotOS 7.1

> 板块: General Discussion

For anyone interested in a Parrot template, I've uploaded a  7.1
template, available from https://qubes.3isec.org/Templates

---

## Anyone using XFE (X File Explorer)?

> 板块: General Discussion

Hi,

I was looking for a lightweight file manager that can replace Thunar in Debian and PCManFM-QT in Whonix and found XFE.

It needs far less space to install, uses several times less memory and has more features. The only cons I see so far is that right-click menu sometimes shows out of the main window (on top left of the desktop) and the only way to hide it is to press Esc on the keyboard.

I see it supports custom scripting as well, so I suppose it could be possible to add the Qubes-specific copy/move to VM menus through that.

It seems a good fit for systems with limited resources or for anyone who prefers to keep things more minimal.

Anyone using it? Impressions?

---

## Install Problem Lenovo P72 R4.3.0

> 板块: General Discussion

Did a bare metal install on Lenovo P72
1000 gig drive
16 gig memory
And got the following message at the end of the install:

[‘/usr/bin/qvm-start’,’sys-firewall’] failed:stdout
stderr:”Error:Start failed: internal error:Unable to reset PCI device
0000:00:1f.6:no FLR, PM reset or bus reset available, see /var/log/libvirt/libxl/libxl-driver.log for details

Can not get to the log because the individual qubes won't run.
Messages when I try personal qube are sys-net, sys-firwall and sys-personal will not load.

Appreciate any guidance to run R4.3

---

## Hardware random number generators

> 板块: General Discussion

I just learned that about a decade ago the NSA backdoored a random number generator in order to crack RSA.
https://en.wikipedia.org/wiki/Dual_EC_DRBG

A hardware random number generator (HRNG) is a hardware device that produces random numbers using noise from physical processes (e.g., electronic noise, thermal noise, etc.).

When I search the forum I do not get many results for the phrases "hardware random number generator" or "HRNG".

Are there any Qubes-supported and Qubes-approved hardware random number generators that I can purchase online, that are supported by dom0 and that can protect me against this sort of attack vector?

---

## CPU, RAM and GPU advancments coming before 2030

> 板块: General Discussion

As the title suggests we will be getting cpu instruction and ram encryption by 2028, at the very least using ryzen we will have encrypted xen virtualization in a way even dom0 wont be able to infer what is happening in your qubes, lastly and most importantly we should have per-vm isolation in gpus.

I don't know about ya'll but I am stacking up my bank account for the next few years, these news are enough for me to drop my old 2012ish laptop and upgrade, just the fact that I can have encrypted qubes is enough for me to have a fever dream, the coming advancements in gpu architecture to pair with that fact is making me spasm from happiness, the only thing that is a splash on cold water to my face is that PSP needs to stay on for all these features to work correctly, at least AFAIK

I think that now I will be buying my first "new" computer since forever, if not for the fact that qubes will be encrypted, now I will also be able to have a dedicated GPU that all qubes will be able to share securely, notably I will be going with AMD since NVIDIA surely is too focused on performance rather then security

---

## Qubes OS updates Weekly Review - Y2025-W47

> 板块: General Discussion

# Qubes OS updates Weekly Review - Y2025-W47

### Introduction
Weekly review of new packages uploaded to Qubes OS repositories. Link to previous Newsletter [here](https://forum.qubes-os.org/t/qubes-os-updates-weekly-review-y2025-w46).

<details>
<summary>Alphabetically sorted list of new packages uploaded to Qubes OS repositories</summary>

```bash
kernel-515-5.15.196-1.qubes.fc37.x86_64.rpm
kernel-515-devel-5.15.196-1.qubes.fc37.x86_64.rpm
kernel-515-modules-5.15.196-1.qubes.fc37.x86_64.rpm
kernel-515-qubes-vm-5.15.196-1.qubes.fc37.x86_64.rpm
kernel-6.12.58-1.qubes.fc37.x86_64.rpm
kernel-6.12.58-1.qubes.fc41.x86_64.rpm
kernel-61-6.1.158-1.qubes.fc37.x86_64.rpm
kernel-61-devel-6.1.158-1.qubes.fc37.x86_64.rpm
kernel-61-modules-6.1.158-1.qubes.fc37.x86_64.rpm
kernel-61-qubes-vm-6.1.158-1.qubes.fc37.x86_64.rpm
kernel-66-6.6.116-1.qubes.fc37.x86_64.rpm
kernel-66-devel-6.6.116-1.qubes.fc37.x86_64.rpm
kernel-66-modules-6.6.116-1.qubes.fc37.x86_64.rpm
kernel-66-qubes-vm-6.6.116-1.qubes.fc37.x86_64.rpm
kernel-devel-6.12.58-1.qubes.fc37.x86_64.rpm
kernel-devel-6.12.58-1.qubes.fc41.x86_64.rpm
kernel-latest-6.17.8-1.qubes.fc37.x86_64.rpm
kernel-latest-6.17.8-1.qubes.fc41.x86_64.rpm
kernel-latest-6.17.8-2.qubes.fc37.x86_64.rpm
kernel-latest-6.17.8-2.qubes.fc41.x86_64.rpm
kernel-latest-devel-6.17.8-1.qubes.fc37.x86_64.rpm
kernel-latest-devel-6.17.8-1.qubes.fc41.x86_64.rpm
kernel-latest-devel-6.17.8-2.qubes.fc37.x86_64.rpm
kernel-latest-devel-6.17.8-2.qubes.fc41.x86_64.rpm
kernel-latest-modules-6.17.8-1.qubes.fc37.x86_64.rpm
kernel-latest-modules-6.17.8-1.qubes.fc41.x86_64.rpm
kernel-latest-modules-6.17.8-2.qubes.fc37.x86_64.rpm
kernel-latest-modules-6.17.8-2.qubes.fc41.x86_64.rpm
kernel-latest-qubes-vm-6.17.8-1.qubes.fc37.x86_64.rpm
kernel-latest-qubes-vm-6.17.8-1.qubes.fc41.x86_64.rpm
kernel-latest-qubes-vm-6.17.8-2.qubes.fc37.x86_64.rpm
kernel-latest-qubes-vm-6.17.8-2.qubes.fc41.x86_64.rpm
kernel-modules-6.12.58-1.qubes.fc37.x86_64.rpm
kernel-modules-6.12.58-1.qubes.fc41.x86_64.rpm
kernel-qubes-vm-6.12.58-1.qubes.fc37.x86_64.rpm
kernel-qubes-vm-6.12.58-1.qubes.fc41.x86_64.rpm
libnvpair3-2.3.5-1.fc37.x86_64.rpm
libnvpair3-2.3.5-1.fc41.x86_64.rpm
libuutil3-2.3.5-1.fc37.x86_64.rpm
libuutil3-2.3.5-1.fc41.x86_64.rpm
libzfs6-2.3.5-1.fc37.x86_64.rpm
libzfs6-2.3.5-1.fc41.x86_64.rpm
libzfs6-devel-2.3.5-1.fc37.x86_64.rpm
libzfs6-devel-2.3.5-1.fc41.x86_64.rpm
libzpool6-2.3.5-1.fc37.x86_64.rpm
libzpool6-2.3.5-1.fc41.x86_64.rpm
python3-pyzfs-2.3.5-1.fc37.noarch.rpm
python3-pyzfs-2.3.5-1.fc41.noarch.rpm
qubes-artwork-4.3.9-1.fc41.noarch.rpm
qubes-artwork-4.3.9-1.fc42.noarch.rpm
qubes-artwork-4.3.9-1.fc43.noarch.rpm
qubes-artwork-anaconda-4.3.9-1.fc41.noarch.rpm
qubes-artwork-anaconda-4.3.9-1.fc42.noarch.rpm
qubes-artwork-anaconda-4.3.9-1.fc43.noarch.rpm
qubes-artwork-efi-4.3.9-1.fc41.noarch.rpm
qubes-artwork-efi-4.3.9-1.fc42.noarch.rpm
qubes-artwork-efi-4.3.9-1.fc43.noarch.rpm
qubes-artwork-plymouth-4.3.9-1.fc41.noarch.rpm
qubes-artwork-plymouth-4.3.9-1.fc42.noarch.rpm
qubes-artwork-plymouth-4.3.9-1.fc43.noarch.rpm
qubes-artwork_4.3.9-1+deb12u1_amd64.deb
qubes-artwork_4.3.9-1+deb13u1_amd64.deb
qubes-artwork_4.3.9-1+jammy1_amd64.deb
qubes-artwork_4.3.9-1+noble1_amd64.deb
qubes-core-agent-4.3.36-1.fc41.x86_64.rpm
qubes-core-agent-4.3.36-1.fc42.x86_64.rpm
qubes-core-agent-4.3.36-1.fc43.x86_64.rpm
qubes-core-agent-caja-4.3.36-1.fc41.x86_64.rpm
qubes-core-agent-caja-4.3.36-1.fc42.x86_64.rpm
qubes-core-agent-caja-4.3.36-1.fc43.x86_64.rpm
qubes-core-agent-caja_4.3.36-1+deb12u1_amd64.deb
qubes-core-agent-caja_4.3.36-1+deb13u1_amd64.deb
qubes-core-agent-caja_4.3.36-1+jammy1_amd64.deb
qubes-core-agent-caja_4.3.36-1+noble1_amd64.deb
qubes-core-agent-dbgsym_4.3.36-1+deb12u1_amd64.deb
qubes-core-agent-dbgsym_4.3.36-1+deb13u1_amd64.deb
qubes-core-agent-dom0-updates-4.3.36-1.fc41.noarch.rpm
qubes-core-agent-dom0-updates-4.3.36-1.fc42.noarch.rpm
qubes-core-agent-dom0-updates-4.3.36-1.fc43.noarch.rpm
qubes-core-agent-dom0-updates_4.3.36-1+deb12u1_amd64.deb
qubes-core-agent-dom0-updates_4.3.36-1+deb13u1_amd64.deb
qubes-core-agent-dom0-updates_4.3.36-1+jammy1_amd64.deb
qubes-core-agent-dom0-updates_4.3.36-1+noble1_amd64.deb
qubes-core-agent-nautilus-4.3.36-1.fc41.x86_64.rpm
qubes-core-agent-nautilus-4.3.36-1.fc42.x86_64.rpm
qubes-core-agent-nautilus-4.3.36-1.fc43.x86_64.rpm
qubes-core-agent-nautilus_4.3.36-1+deb12u1_amd64.deb
qubes-core-agent-nautilus_4.3.36-1+deb13u1_amd64.deb
qubes-core-agent-nautilus_4.3.36-1+jammy1_amd64.deb
qubes-core-agent-nautilus_4.3.36-1+noble1_amd64.deb
qubes-core-agent-network-manager-4.3.36-1.fc41.noarch.rpm
qubes-core-agent-network-manager-4.3.36-1.fc42.noarch.rpm
qubes-core-agent-network-manager-4.3.36-1.fc43.noarch.rpm
qubes-core-agent-network-manager_4.3.36-1+deb12u1_amd64.deb
qubes-core-agent-network-manager_4.3.36-1+deb13u1_amd64.deb
qubes-core-agent-network-manager_4.3.36-1+jammy1_amd64.deb
qubes-core-agent-network-manager_4.3.36-1+noble1_amd64.deb
qubes-core-agent-networking-4.3.36-1.fc41.noarch.rpm
qubes-core-agent-networking-4.3.36-1.fc42.noarch.rpm
qubes-core-agent-networking-4.3.36-1.fc43.noarch.rpm
qubes-core-agent-networking_4.3.36-1+deb12u1_amd64.deb
qubes-core-agent-networking_4.3.36-1+deb13u1_amd64.deb
qubes-core-agent-networking_4.3.36-1+jammy1_amd64.deb
qubes-core-agent-networking_4.3.36-1+noble1_amd64.deb
qubes-core-agent-passwordless-root-4.3.36-1.fc41.noarch.rpm
qubes-core-agent-passwordless-root-4.3.36-1.fc42.noarch.rpm
qubes-core-agent-passwordless-root-4.3.36-1.fc43.noarch.rpm
qubes-core-agent-passwordless-root_4.3.36-1+deb12u1_amd64.deb
qubes-core-agent-passwordless-root_4.3.36-1+deb13u1_amd64.deb
qubes-core-agent-passwordless-root_4.3.36-1+jammy1_amd64.deb
qubes-core-agent-passwordless-root_4.3.36-1+noble1_amd64.deb
qubes-core-agent-pcmanfm-qt_4.3.36-1+deb12u1_amd64.deb
qubes-core-agent-pcmanfm-qt_4.3.36-1+deb13u1_amd64.deb
qubes-core-agent-pcmanfm-qt_4.3.36-1+jammy1_amd64.deb
qubes-core-agent-pcmanfm-qt_4.3.36-1+noble1_amd64.deb
qubes-core-agent-selinux-4.3.36-1.fc41.noarch.rpm
qubes-core-agent-selinux-4.3.36-1.fc42.noarch.rpm
qubes-core-agent-selinux-4.3.36-1.fc43.noarch.rpm
qubes-core-agent-systemd-4.3.36-1.fc41.x86_64.rpm
qubes-core-agent-systemd-4.3.36-1.fc42.x86_64.rpm
qubes-core-agent-systemd-4.3.36-1.fc43.x86_64.rpm
qubes-core-agent-thunar-4.3.36-1.fc41.x86_64.rpm
qubes-core-agent-thunar-4.3.36-1.fc42.x86_64.rpm
qubes-core-agent-thunar-4.3.36-1.fc43.x86_64.rpm
qubes-core-agent-thunar_4.3.36-1+deb12u1_amd64.deb
qubes-core-agent-thunar_4.3.36-1+deb13u1_amd64.deb
qubes-core-agent-thunar_4.3.36-1+jammy1_amd64.deb
qubes-core-agent-thunar_4.3.36-1+noble1_amd64.deb
qubes-core-agent_4.3.36-1+deb12u1_amd64.deb
qubes-core-agent_4.3.36-1+deb13u1_amd64.deb
qubes-core-agent_4.3.36-1+jammy1_amd64.deb
qubes-core-agent_4.3.36-1+noble1_amd64.deb
qubes-template-kicksecure-18-4.3.0-202511221309.noarch.rpm
qubes-video-companion-1.1.8-1.fc41.noarch.rpm
qubes-video-companion-1.1.8-1.fc42.noarch.rpm
qubes-video-companion-4.3.0-1.fc41.noarch.rpm
qubes-video-companion-4.3.0-1.fc42.noarch.rpm
qubes-video-companion-4.3.0-1.fc43.noarch.rpm
qubes-video-companion-docs-1.1.8-1.fc41.noarch.rpm
qubes-video-companion-docs-1.1.8-1.fc42.noarch.rpm
qubes-video-companion-docs-4.3.0-1.fc41.noarch.rpm
qubes-video-companion-docs-4.3.0-1.fc42.noarch.rpm
qubes-video-companion-docs-4.3.0-1.fc43.noarch.rpm
qubes-video-companion-dom0-1.1.8-1.fc37.noarch.rpm
qubes-video-companion-dom0-4.3.0-1.fc41.noarch.rpm
qubes-video-companion-license-1.1.8-1.fc41.noarch.rpm
qubes-video-companion-license-1.1.8-1.fc42.noarch.rpm
qubes-video-companion-license-4.3.0-1.fc41.noarch.rpm
qubes-video-companion-license-4.3.0-1.fc42.noarch.rpm
qubes-video-companion-license-4.3.0-1.fc43.noarch.rpm
qubes-video-companion-receiver-1.1.8-1.fc41.noarch.rpm
qubes-video-companion-receiver-1.1.8-1.fc42.noarch.rpm
qubes-video-companion-receiver-4.3.0-1.fc41.noarch.rpm
qubes-video-companion-receiver-4.3.0-1.fc42.noarch.rpm
qubes-video-companion-receiver-4.3.0-1.fc43.noarch.rpm
qubes-video-companion-sender-1.1.8-1.fc41.noarch.rpm
qubes-video-companion-sender-1.1.8-1.fc42.noarch.rpm
qubes-video-companion-sender-4.3.0-1.fc41.noarch.rpm
qubes-video-companion-sender-4.3.0-1.fc42.noarch.rpm
qubes-video-companion-sender-4.3.0-1.fc43.noarch.rpm
qubes-video-companion_1.1.8-1+deb12u1_all.deb
qubes-video-companion_1.1.8-1+deb13u1_all.deb
qubes-video-companion_1.1.8-1+jammy1_all.deb
qubes-video-companion_1.1.8-1+noble1_all.deb
qubes-video-companion_4.3.0-1+deb12u1_all.deb
qubes-video-companion_4.3.0-1+deb13u1_all.deb
qubes-video-companion_4.3.0-1+jammy1_all.deb
qubes-video-companion_4.3.0-1+noble1_all.deb
qubes-vm-caja-4.3.36-1-x86_64.pkg.tar.zst
qubes-vm-core-4.3.36-1-x86_64.pkg.tar.zst
qubes-vm-dom0-updates-4.3.36-1-x86_64.pkg.tar.zst
qubes-vm-keyring-4.3.36-1-x86_64.pkg.tar.zst
qubes-vm-nautilus-4.3.36-1-x86_64.pkg.tar.zst
qubes-vm-networking-4.3.36-1-x86_64.pkg.tar.zst
qubes-vm-passwordless-root-4.3.36-1-x86_64.pkg.tar.zst
qubes-vm-thunar-4.3.36-1-x86_64.pkg.tar.zst
qubes-windows-tools-4.2.2-1.fc41.noarch.rpm
zfs-2.3.5-1.fc37.x86_64.rpm
zfs-2.3.5-1.fc41.x86_64.rpm
zfs-dkms-2.3.5-1.fc37.noarch.rpm
zfs-dkms-2.3.5-1.fc41.noarch.rpm
zfs-dracut-2.3.5-1.fc37.noarch.rpm
zfs-dracut-2.3.5-1.fc41.noarch.rpm
zfs-test-2.3.5-1.fc37.x86_64.rpm
zfs-test-2.3.5-1.fc41.x86_64.rpm
```

</details>

### Highlights
- Major work on Qubes Video Companion.

### Details
In addition to the usual minor fixes and patches (full list [here](https://github.com/QubesOS/updates-status/issues?q=is%3Aissue+created%3A2025-11-17..2025-11-23)):

* **gui-agent-linux** [v4.3.15](https://github.com/QubesOS/updates-status/issues/6220) (r4.3)
    - Two patches related to `qubes-video-companion`. One for Debian based qubes and one for minimal ServiceVMs.
    - A major project is ongoing to allow delayed `gui-agent` connection to `gui-daemon`. As a necessity for preloaded disposables (but it has other benefits). While the patches on the GUI Daemon side is still in progress, some on the agent side are merged in this release.
    - The above project broke `sys-gui` (not `sys-gui-gpu`) connection to dom0 display(s). Fixes were necessary.

* **notification-proxy** [v1.0.6](https://github.com/QubesOS/updates-status/issues/6218) (r4.3)
    To allow delayed GUI session, the notification proxy start had to be waited as well.

* **linux-kernel-latest** [v6.17.8-2-latest](https://github.com/QubesOS/updates-status/issues/6211) (r4.3)
  **linux-kernel-latest** [v6.17.8-2-latest](https://github.com/QubesOS/updates-status/issues/6210) (r4.2)
  **linux-kernel-latest** [v6.17.8-1-latest](https://github.com/QubesOS/updates-status/issues/6197) (r4.3)
  **linux-kernel-latest** [v6.17.8-1-latest](https://github.com/QubesOS/updates-status/issues/6196) (r4.2)
  **linux-kernel** (current stable) [v6.12.58-1](https://github.com/QubesOS/updates-status/issues/6199) (r4.3)
  **linux-kernel** (current stable) [v6.12.58-1](https://github.com/QubesOS/updates-status/issues/6198) (r4.2)
  **linux-kernel-66** (old stable) [v6.6.116-1](https://github.com/QubesOS/updates-status/issues/6217) (r4.2)
  **linux-kernel-61** (older stable) [v6.1.158-1](https://github.com/QubesOS/updates-status/issues/6215) (r4.2)
  **linux-kernel-515** (ancient stable) [v5.15.196-1](https://github.com/QubesOS/updates-status/issues/6216) (r4.2)
    Linux kernel weekly updates. We have two for `kernel-latest` since some debugging was going on in the meantime.

* **qubes-template-whonix-workstation-18** [4.3.0-202511221309](https://github.com/QubesOS/updates-status/issues/6214) (r4.3)
  **qubes-template-whonix-gateway-18** [4.3.0-202511221309](https://github.com/QubesOS/updates-status/issues/6213) (r4.3)
    Failed attempt to build Whonix templates.

* **qubes-template-kicksecure-18** [4.3.0-202511221309](https://github.com/QubesOS/updates-status/issues/6212) (r4.3)
    A fresh Kicksecure template with latest updates.

* **installer-qubes-os-windows-tools** [v4.2.2-1](https://github.com/QubesOS/updates-status/issues/6209) (r4.3)
  **installer-qubes-os-windows-tools** [v4.2.1-1](https://github.com/QubesOS/updates-status/issues/6208) (r4.3)
    - This is a real new release of QWT.
    - Automatically accepting test-signed drivers via focus-stealing techniques.
    - QWT installer should allow user to select auto-login (I do not have a screenshot). 
    - Unlike Linux guests, QWT is not automatically updated. Users are supposed to manually mount the updated QWT ISO and upgrade (do not forget to backup/snapshot before upgrading). I have not tested this QWT release personally since my test system does not have enough storage space nor enough memory for a dedicated Windows qube.

* **windows-utils** [v4.2.2](https://github.com/QubesOS/updates-status/issues/6207) (r4.3)
    Cleanup and documentation on how to build from source. 

* **core-agent-windows** [v4.2.2](https://github.com/QubesOS/updates-status/issues/6206) (r4.3)
    - Cleanup and documentation on how to build from source. 
    - Auto-login code (to generate a random password, setting it in Windows registry, ...).
    - Allowing `qubes.StartApp` for Windows qubes which have auto-login enabled.

* **core-agent-linux** [v4.3.36](https://github.com/QubesOS/updates-status/issues/6204) (r4.3)
    Fixing `specialtarget=dns` for Qubes Firewall on DNS changes.

* **video-companion** [v4.3.0-1](https://github.com/QubesOS/updates-status/issues/6203) (r4.3)
  **video-companion** [v1.1.8-1](https://github.com/QubesOS/updates-status/issues/6202) (r4.3)
  **video-companion** [v1.1.8-1](https://github.com/QubesOS/updates-status/issues/6201) (r4.2)
    - Allowing `qubes-video-companion` on Kicksecure and Whonix qubes which have `sysmaint` enabled.
    - Continuation of the project to allow multiple webcams (or video input devices).
    - Major project to integrate `qubes-video-companion` to Qui Devices widget. After implemented, Qui Devices will prefer Qubes Video Companion to transfer video to target qube instead of attaching the USB camera directly. This will have security benefit (in case the firmware of the webcam/video-device is tampered).
    - Unfortunately screenshare is not integrated to Qui Devices (but appears to be easy).

* **artwork** [v4.3.9-1](https://github.com/QubesOS/updates-status/issues/6200) (r4.3)
    - The old raster PNG icons are deleted to allow new SVG icons to take effect.
    - Previously PNG icons had to be re-generated via [Inkscape script](https://github.com/QubesOS/qubes-artwork/blob/main/icons/Makefile.common#L71-L75) every time SVG icons were updated. And they were installed as a part of default Qubes XDG icon set. As far as I understand, DE and GUI toolkits (XFCE, GTK) might require to dynamically render SVGs on the fly now (for App Menu, Qui widgets and some other places). The performance penalty should be negligible these days.

* **zfs** [v2.3.5-1](https://github.com/QubesOS/updates-status/issues/6195) (r4.2)
  **zfs** [v2.3.5-1](https://github.com/QubesOS/updates-status/issues/6194) (r4.3)
  **zfs-dkms** [v2.3.5-1](https://github.com/QubesOS/updates-status/issues/6193) (r4.2)
  **zfs-dkms** [v2.3.5-1](https://github.com/QubesOS/updates-status/issues/6192) (r4.3)
    Bumping up to OpenZFS 2.3.5. Release notes [here](https://github.com/openzfs/zfs/releases/tag/zfs-2.3.5).

---

## Wayland in dom0 with KDE or qubes-wayland

> 板块: General Discussion

As far as I am aware, there are two ways to use wayland in qubes. The first is to install KDE, which lets you choose between a wayland session and an xorg session at the login screen. Second would be this: https://github.com/DemiMarie/qubes-wayland
Just to clarify, that would switch dom0 over from xorg to wayland, yes?
And as for the vms themselves, if I were to install it inside of a hvm, then that would switch it from xorg to wayland also?
Are there any side effects such as the copy-paste breaking? (for the second option) How about the GUI vm? Is it possible to use sys-gui with wayland if dom0 is running  on wayland?

---

## Is using xen as the hypervisor makes as much sense now as it made before?

> 板块: General Discussion

So, I decided to check if any employers care about sysadmins who know how to work with xen. Especially because it's my daily driver. But I wasn't able to find any. I also wasn't able to find any certifications for xen (at least in my location). So then I checked where xen was and is currently used. Apparently when Qubes-os was initially released xen as a hypervisor choice was a no brainer. Not only it's a microkernel with security by compartmentalization. It *was* used by all major cloud and vps providers. Nowdays most of them are using customized implementations of kvm. And there are really a lot of those. Or vmware/locally made closed source software by the same company. The only vps provider which claimed to use xen as their hypervisor was linode. Which is somewhat reassuring but it was the only big one I could find. But xen has it's uses in smart cars sector. And this is about it

Issue is - when Qubes-os was created there was really a lot of attention to it's hypervisor. So bugs were way less likely to stay hidden for long. Nowdays this attention is focused on kvm and the linux kernel itself

How does this really affects Qubes-os security? Wouldn't it make kvm based solutions a bit more secure from attention to the source code factor?

---

## PGP / GPG Recommendations

> 板块: General Discussion

Hi. What PGP software are you guys using?

I am using Kgpg

I see theres other choices like kleopatra

What is good for qubesos?

---

## What extra layers of protection should I add for better security on Qubes OS 4.3?

> 板块: General Discussion

What have you installed and/or configured on your qubes os thats proven to help you be more secure from all threats imaginable? I have a post quantum double vpn that routes traffic through whonix. Is there more that I can do?

---

## Guidance on using AI in Contributions

> 板块: General Discussion

We have published guidance on using generative AI when contributing to the project\.

The Full guidance is [here](https://doc.qubes-os.org/en/latest/introduction/contributing.html#using-ai-in-contributions)

TLDR \- You must disclose use of AI in \*\*any\*\* contribution to Qubes, and you remain responsible for the content\.

---

## Onion server down for maintenance

> 板块: General Discussion

The official Onion server is down for maintenance\.
Normal service will be restored as soon as possible\.

---

## A Moment of Kindness for Alyssa Ross and Spectrum OS

> 板块: General Discussion

If you haven’t heard of **Spectrum OS** , please take a look:
https://spectrum-os.org/

Behind it is **Alyssa Ross** , who has been quietly building this operating system almost entirely on her own. Her dedication, skill, and resilience are deeply inspiring. It’s not easy to carry such a project alone, and yet she continues with quiet determination.

Recently, **Demi Marie** another highly skilled developer stepped down from Qubes OS to join her bringing much-needed support. Still, Alyssa bears the greatest share of the work.

You don’t need to donate money. What would mean a lot are **small, kind actions** :

* Help with translation or documentation
* Test a build and share feedback
* Or simply offering encouragement

A few months ago, Alyssa asked for help with translation on Mastodon just one example of how light involvement can make a difference.

Open source thrives not just on code, but on **care, patience, and community** .

please offer a little of your time or kindness.

Let’s make sure Alyssa knows she’s not alone.

Mods please don't remove this post :pray:

---

## NovaCustom + BusKill partnership

> 板块: General Discussion

🇳🇱 [Nederlandse versie](https://buskill.in/netherlands-novacustom-nl/) van dit artikel  
🇫🇷 [Version française](https://buskill.in/netherlands-novacustom-fr/) de cet article  
🇩🇪 [Deutsche Version](https://buskill.in/netherlands-novacustom-de/) dieses Artikels  

We\'re happy to announce that **BusKill cables can now be purchased in-person** in Haaksbergen, Netherlands.

[![\[BusKill\] Our Dead Man Switch Magnetic USB Breakaway cables are Now Available in-person in The Netherlands at NovaCustom](https://www.buskill.in/wp-content/uploads/sites/8/netherlands-novacustom-featuredImage1.jpg)](https://buskill.in/netherlands-novacustom/)
The BusKill project has partnered with [NovaCustom](https://novacustom.com/?aff=10) to make BusKill laptop kill cords available from [another](/leipzig-proxystore/) brick-and-mortar location in Europe. You can now go to the NovaCustom office and purchase a BusKill cable with cash or cryptocurrency.

> ⚠ **NOTE: In-person orders at NovaCustom\'s offices require an appointment.** Please [contact them](https://novacustom.com/contact/?aff=10) over email or Signal to schedule an appointment before you go.
>    
> And, if paying with cash, bring the exact amount. They do not provide change.  

# About BusKill

BusKill is a laptop kill-cord. It's a USB cable with a magnetic breakaway that you attach to your body and connect to your computer.

| [![What is BusKill? (Explainer Video)](https://github.com/BusKill/buskill-app/raw/master/docs/images/buskill_explainer_video_20211210.gif?raw=true)](https://www.buskill.in/#demo) |
|:--:|
| *Watch the [BusKill Explainer Video](https://www.buskill.in/#demo) for more info [youtube.com/v/qPwyoD_cQR4](https://www.youtube.com/v/qPwyoD_cQR4)* |

If the connection between you to your computer is severed, then your device will lock, shutdown, or shred its encryption keys -- thus keeping your encrypted data safe from thieves that steal your device.

While [we do what we can](https://buskill.in/netherlands-novacustom/) to allow at-risk folks to [purchase BusKill cables anonymously](https://buskill.in/netherlands-novacustom/) (or [make](https://buskill.in/netherlands-novacustom/) their own), there is always the risk of [interdiction](https://buskill.in/netherlands-novacustom/).

We don't consider hologram stickers or tamper-evident tape/crisps/glitter to be sufficient solutions to supply-chain security. A better solution (in addition to making the hardware designs open-source) is to let users purchase the device anonymously. Generally, the best way to defeat interdiction is to go to a physical brick-and-mortar and pay with cash.

# About NovaCustom

In Mar 2015, Wessel klein Snakenborg (founder of NovaCustom) started selling highly-customizable Linux laptops from Europe.
In Aug 2021, NovaCustom released their first laptop (NV40) with **coreboot pre-installed** with Dasharo.

| [![Photo of a laptop showing the Dashero Boot Menu, running Heads](upload://vDAaz6RKO3u0vxiZl4LFiy2rzg9.png)](https://buskill.in/netherlands-novacustom/) | [![Photo of a screw that's been covered with a unique pattern of (multi-color) glitter nail polish](upload://qAwYG1DKRy1rgi1hcztH8nE0oom.png)](https://buskill.in/netherlands-novacustom/) |
|:--:|:--:|
| The Qubes-Certified NV41 with Heads pre-installed by NovaCustom  | NovaCustom offers anti-tamper options, including glitter nail polish applied to the chassis screws (photos sent to you via Proton Mail before shipment — specify PGP key at checkout for e2ee)  |


In 2023, NovaCustom caught the eye of many in the security community, as they announced a number of major milestones:

-   In Apr 2023, NovaCustom started offering [**Intel ME disabling**](https://novacustom.com/intel-me-disabling-feature/?aff=10)
-   In May 2023, NovaCustom demonstrated their commitment to free software and the security community by [obtaining **Qubes certification**](https://www.qubes-os.org/news/2023/05/03/novacustom-nv41-series-qubes-certified/) on their [NV41 Series](https://novacustom.com/product/nv41-series/?aff=10) laptop.
-   In Sep 2023, NovaCustom [started offering **anti-interdiction**](https://novacustom.com/anti-tamper-for-laptop/?aff=10) services, which includes applying a unique glitter pattern to your new laptop\'s chassis screws before shipment.

And in Feb 2024, NovaCustom started selling their NV41 laptop with **[Heads](https://tech.michaelaltfield.net/2023/02/16/evil-maid-heads-pureboot/) pre-installed**.

And now, as part of the partnership with the BusKill project, NovaCustom allows customers to place orders anonymously on their website, **pickup the order in-person, and pay with cash** (Euros only, exact cash required, and per-arranged appointment required for pickup). They also accept payments in Monero and Bitcoin.
We\'re excited to partner with another leader in privacy solutions for high-risk folks in Europe, and we hope you\'ll **consider buying a [Qubes-certified NovaCustom laptop](https://novacustom.com/qubes-os-certified-laptop/?aff=10) + [BusKill Kit](https://novacustom.com/product/buskill/?aff=10)** from NovaCustom in The Netherlands.

## Buy BusKill in-person in The Netherlands

Order at [novacustom.com](https://novacustom.com/product/buskill/?aff=10) or stop by in-store to purchase a BusKill cable.

Bitcoin, monero, and fiat (cash) are all accepted payment methods at NovaCustom.


Stay safe,  
The BusKill Team  
https://www.buskill.in/  
http://www.buskillvampfih2iucxhit3qp36i2zzql3u6pmkeafvlxs3tlmot5yad.onion

---

## Qubes OS could be honeypot?

> 板块: General Discussion

Have you considered that Qubes may be a honeypot?

As a typical PC user I have to just take peoples word for it that qubes is secure and all I really may be doing is telling the world that I have something to hide while gaining no added privacy.

I would assume government agents dont need qubes so who is it for? It seems as though most security people find an OS like Kali to be plenty secure. It sure is easier in Kali or Arch to know exactly what processes are running on your machine. and how they got there. Also as far as I know on Kali or Arch only one process can be hidden with a process hider. On qubes their are endless terminals so maybe endless programs could be hidden. I have no clue because I am not a computer scientist. 

I am not the one to take advise on technical matters but I am elite when it comes to smelling BS and critical thinking and this place certainly has a fishy smell.

After reading this it smells even worse as providing Firefox with less security than many other browsers along with no native tools to know if you are being surveilled seems more consistent with a honeypot than with a reasonably secure OS.

But I am just an idiot so take it for what it is worth witch could very well be nothing. But really just ask yourself if any of this makes sense, When I trust the words of others it does but when I think about my gut it says fishy fishy fishy.

One thing I do know is you would have to be nuts or a computer scientist to trust qubes for anything other than political dissidence against an "enemy" of the United states and its "allies". Even the encryption is a joke against an adversary with the ability to farm out decryption to every windows machine on the planet or more than likely use all the bitcoin mining machines as a network of encryption cracking processor units.

Either way it appears to be more about giving people protection from random criminals and a false sense of security than about actual security. Do we really think we have any idea what the US has? Do we really think we even have a clue what decryption algorithms the US government has? Sure with what we know it sounds reasonably secure but in case people have not noticed it has been atleast 20 years since the public has been aware of what the cutting edge of computing has been. 
If you think DARPA cant make Luks2 its B/tch you have not been paying attention. Well sorry for the rant and I am sure its tldr but I am autistic and have a compulsion to speak my mind sometimes.
sorry for wasting your time and good luck!

---

## Recommendations for mitigating supply chain attacks

> 板块: General Discussion

Last month, several American institutions, including the NSA, published a document on what to do in order to avoid or at least mitigate supply chain attacks in software development, like the SolarWinds compromise:

[Securing the Software Supply Chain](https://www.cisa.gov/uscert/sites/default/files/publications/ESF_SECURING_THE_SOFTWARE_SUPPLY_CHAIN_DEVELOPERS.PDF)

The relevant aspects of a secure development environment and process are described systematically and in great detail, which may help to identify any strengths and weaknesses in one's own environment. So this seems to me to be a valuable resource well worth reading.

Just a warning: While the practices described there are very good and worth to be adopted, the amount of work needed for that will probably be far beyond available resources, but it's the goal that counts!

I'm calling it especially to the attention of @adw and @marmarek, hoping that it will help with Qubes development, which - as far as I can see - is already using a lot of these techniques.

---

## KeePass, One file multiple templates

> 板块: General Discussion

WIth KeePass having a few different files for everything just bugs me and I don't know why.

Is where a way to have the main KeePass file say in the vault and whenever I pullup KeePass on a VM that KeePass is able to grab that password file?

---

## Tutorial: connect to a Wi-Fi access point

> 板块: General Discussion

After spending some time trying to figure out how to write a proper tutorial for Qubes, I ended up with this:

https://github.com/parulin/qubes-doc/blob/tutorials/user/tutorials/connect-to-wifi.rst

The HTML output is visible here:

https://parulin-qubes-doc.readthedocs.io/en/tutorials/user/tutorials/connect-to-wifi.html

If anyone would like to review it, I would appreciate it. I wrote this text with the idea to contribute to the official docs but I'm not sure if it would be appropriate. For sure, there are a lot of mistakes in it. I'm open to any suggestion, even if someone wants to nitpick. The things that must be wrong are:

* the grammar, etc.
* the description of the [First Qubes OS boot](https://parulin-qubes-doc.readthedocs.io/en/tutorials/user/tutorials/connect-to-wifi.html#first-qubes-os-boot) section
* [Why do we need *sys-net*?](https://parulin-qubes-doc.readthedocs.io/en/tutorials/user/tutorials/connect-to-wifi.html#why-do-we-need-sys-net) section
* the screenshots
* the instructions

About the screenshots, I tried to use openQA screenshots, with a custom script, to be able to update and correct them easily. Feel free to suggest anything about them, it should not be difficult if it is a fullscreen screenshot.

Right now, I spent too much time rereading and retrying my own instructions to be able to accurately spot my own mistakes. Feel free to discuss the method, anything.

---

## Fedora template update very slow running rpm scriptlet for kernel-core

> 板块: General Discussion

Every time I update fedora based template the last steps when running rpm scriptlets for kernel-modules but especially for kernel-core is very slow. It always takes hours until it finishes.

Does this happen for everyone? If not how can I further investigate it? memory and cpu usage in the template is very low during these steps

```
Updating fedora-42
Refreshing package info
Removed 0 files, 0 directories (total of 0 B). 0 errors occurred.
Fetching 55 packages [468.53 MiB]
Fetching kernel-0:6.18.7-100.fc42.x86_64 [223.69 KiB]
Fetching kernel-core-0:6.18.7-100.fc42.x86_64 [19.63 MiB]
Fetching kernel-modules-0:6.18.7-100.fc42.x86_64 [98.23 MiB]
Fetching kernel-modules-core-0:6.18.7-100.fc42.x86_64 [69.58 MiB]
Fetching alsa-lib-0:1.2.15.3-1.fc42.x86_64 [541.44 KiB]
Fetching alsa-sof-firmware-0:2025.12.1-1.fc42.noarch [10.28 MiB]
Fetching alsa-ucm-0:1.2.15.3-1.fc42.noarch [321.15 KiB]
Fetching alsa-utils-0:1.2.15.2-1.fc42.x86_64 [1.19 MiB]
Fetching assimp-0:5.3.1-6.fc42.x86_64 [2.42 MiB]
Fetching curl-0:8.11.1-7.fc42.x86_64 [219.51 KiB]
Fetching libcurl-0:8.11.1-7.fc42.x86_64 [371.06 KiB]
Fetching libcurl-0:8.11.1-7.fc42.i686 [397.46 KiB]
Fetching firefox-0:147.0.2-1.fc42.x86_64 [80.42 MiB]
Fetching freerdp-libs-2:3.21.0-1.fc42.x86_64 [1.28 MiB]
Fetching firefox-langpacks-0:147.0.2-1.fc42.x86_64 [31.93 MiB]
Fetching libwinpr-2:3.21.0-1.fc42.x86_64 [382.52 KiB]
Fetching ghostscript-0:10.05.1-6.fc42.x86_64 [35.60 KiB]
Fetching ghostscript-tools-fontutils-0:10.05.1-6.fc42.noarch [11.33 KiB]
Fetching ghostscript-tools-printing-0:10.05.1-6.fc42.noarch [11.93 KiB]
Fetching libgs-0:10.05.1-6.fc42.x86_64 [3.50 MiB]
Fetching glibc-0:2.41-16.fc42.x86_64 [2.22 MiB]
Fetching glibc-common-0:2.41-16.fc42.x86_64 [362.51 KiB]
Fetching glibc-gconv-extra-0:2.41-16.fc42.x86_64 [1.62 MiB]
Fetching glibc-0:2.41-16.fc42.i686 [2.02 MiB]
Fetching glibc-gconv-extra-0:2.41-16.fc42.i686 [1.63 MiB]
Fetching glibc-devel-0:2.41-16.fc42.x86_64 [599.88 KiB]
Fetching glibc-langpack-en-0:2.41-16.fc42.x86_64 [617.77 KiB]
Fetching glibc-minimal-langpack-0:2.41-16.fc42.x86_64 [75.42 KiB]
Fetching harfbuzz-0:10.4.0-2.fc42.x86_64 [1.05 MiB]
Fetching hplip-0:3.25.8-1.fc42.x86_64 [20.77 MiB]
Fetching harfbuzz-icu-0:10.4.0-2.fc42.x86_64 [14.07 KiB]
Fetching hplip-libs-0:3.25.8-1.fc42.x86_64 [162.93 KiB]
Fetching hplip-common-0:3.25.8-1.fc42.x86_64 [74.05 KiB]
Fetching libsane-hpaio-0:3.25.8-1.fc42.x86_64 [88.82 KiB]
Fetching kernel-tools-0:6.18.7-100.fc42.x86_64 [826.51 KiB]
Fetching kernel-tools-libs-0:6.18.7-100.fc42.x86_64 [236.42 KiB]
Fetching libgphoto2-0:2.5.33-1.fc42.x86_64 [1.34 MiB]
Fetching libmtp-0:1.1.22-2.fc42.x86_64 [155.44 KiB]
Fetching openssl-libs-1:3.2.6-3.fc42.x86_64 [2.33 MiB]
Fetching openssl-libs-1:3.2.6-3.fc42.i686 [2.32 MiB]
Fetching perl-Module-CoreList-tools-1:5.20260119-1.fc42.noarch [18.70 KiB]
Fetching perl-Module-CoreList-1:5.20260119-1.fc42.noarch [94.34 KiB]
Fetching publicsuffix-list-dafsa-0:20260116-1.fc42.noarch [60.31 KiB]
Fetching python3-perf-0:6.18.7-100.fc42.x86_64 [1.76 MiB]
Fetching selinux-policy-0:42.22-1.fc42.noarch [67.06 KiB]
Fetching selinux-policy-targeted-0:42.22-1.fc42.noarch [6.81 MiB]
Fetching vim-common-2:9.1.2086-1.fc42.x86_64 [8.11 MiB]
Fetching vim-data-2:9.1.2086-1.fc42.noarch [17.30 KiB]
Fetching vim-filesystem-2:9.1.2086-1.fc42.noarch [15.24 KiB]
Fetching vim-enhanced-2:9.1.2086-1.fc42.x86_64 [2.00 MiB]
Fetching wireplumber-0:0.5.13-1.fc42.x86_64 [122.25 KiB]
Fetching wireplumber-libs-0:0.5.13-1.fc42.x86_64 [426.37 KiB]
Fetching xxd-2:9.1.2086-1.fc42.x86_64 [31.02 KiB]
Fetching zed-0:0.221.4-1.fc42.x86_64 [88.55 MiB]
Fetching zed-cli-0:0.221.4-1.fc42.x86_64 [1.14 MiB]
Updating packages.
Running rpm scriptlet for firefox-0:147.0.2-1.fc42.x86_64
Running rpm scriptlet for selinux-policy-targeted-0:42.22-1.fc42.noarch
Running rpm scriptlet for alsa-sof-firmware-0:2025.12.1-1.fc42.noarch
Installing glibc-common-0:2.41-16.fc42.x86_64
Running rpm scriptlet for filesystem-0:3.18-47.fc42.x86_64
Installing glibc-gconv-extra-0:2.41-16.fc42.x86_64
Running rpm scriptlet for glibc-gconv-extra-0:2.41-16.fc42.x86_64
Installing glibc-langpack-en-0:2.41-16.fc42.x86_64
Running rpm scriptlet for glibc-0:2.41-16.fc42.x86_64
Installing glibc-0:2.41-16.fc42.x86_64
Running rpm scriptlet for filesystem-0:3.18-47.fc42.x86_64
Running rpm scriptlet for glibc-0:2.41-16.fc42.x86_64
Installing alsa-lib-0:1.2.15.3-1.fc42.x86_64
Running rpm scriptlet for filesystem-0:3.18-47.fc42.x86_64
Installing openssl-libs-1:3.2.6-3.fc42.x86_64
Installing kernel-modules-core-0:6.18.7-100.fc42.x86_64
Installing kernel-core-0:6.18.7-100.fc42.x86_64
Running rpm scriptlet for kernel-core-0:6.18.7-100.fc42.x86_64
Installing libcurl-0:8.11.1-7.fc42.x86_64
Installing curl-0:8.11.1-7.fc42.x86_64
Running rpm scriptlet for filesystem-0:3.18-47.fc42.x86_64
Installing kernel-modules-0:6.18.7-100.fc42.x86_64
Running rpm scriptlet for kernel-modules-0:6.18.7-100.fc42.x86_64
Installing libwinpr-2:3.21.0-1.fc42.x86_64
Installing alsa-ucm-0:1.2.15.3-1.fc42.noarch
Installing firefox-0:147.0.2-1.fc42.x86_64
Running rpm scriptlet for filesystem-0:3.18-47.fc42.x86_64
Installing libgs-0:10.05.1-6.fc42.x86_64
Installing ghostscript-tools-fontutils-0:10.05.1-6.fc42.noarch
Running rpm scriptlet for filesystem-0:3.18-47.fc42.x86_64
Installing ghostscript-tools-printing-0:10.05.1-6.fc42.noarch
Running rpm scriptlet for filesystem-0:3.18-47.fc42.x86_64
Installing ghostscript-0:10.05.1-6.fc42.x86_64
Running rpm scriptlet for filesystem-0:3.18-47.fc42.x86_64
Installing harfbuzz-0:10.4.0-2.fc42.x86_64
Installing kernel-tools-libs-0:6.18.7-100.fc42.x86_64
Running rpm scriptlet for kernel-tools-libs-0:6.18.7-100.fc42.x86_64
Installing wireplumber-libs-0:0.5.13-1.fc42.x86_64
Installing xxd-2:9.1.2086-1.fc42.x86_64
Running rpm scriptlet for filesystem-0:3.18-47.fc42.x86_64
Installing selinux-policy-0:42.22-1.fc42.noarch
Running rpm scriptlet for selinux-policy-0:42.22-1.fc42.noarch
Running rpm scriptlet for selinux-policy-0:42.22-1.fc42.noarch
Running rpm scriptlet for selinux-policy-targeted-0:42.22-1.fc42.noarch
Installing selinux-policy-targeted-0:42.22-1.fc42.noarch
Running rpm scriptlet for selinux-policy-targeted-0:42.22-1.fc42.noarch
Installing vim-filesystem-2:9.1.2086-1.fc42.noarch
Installing vim-data-2:9.1.2086-1.fc42.noarch
Installing vim-common-2:9.1.2086-1.fc42.x86_64
Installing perl-Module-CoreList-1:5.20260119-1.fc42.noarch
Installing hplip-common-0:3.25.8-1.fc42.x86_64
Installing hplip-libs-0:3.25.8-1.fc42.x86_64
Installing hplip-0:3.25.8-1.fc42.x86_64
Running rpm scriptlet for filesystem-0:3.18-47.fc42.x86_64
Running rpm scriptlet for hplip-0:3.25.8-1.fc42.x86_64
Installing libsane-hpaio-0:3.25.8-1.fc42.x86_64
Installing perl-Module-CoreList-tools-1:5.20260119-1.fc42.noarch
Running rpm scriptlet for filesystem-0:3.18-47.fc42.x86_64
Installing vim-enhanced-2:9.1.2086-1.fc42.x86_64
Running rpm scriptlet for filesystem-0:3.18-47.fc42.x86_64
Installing wireplumber-0:0.5.13-1.fc42.x86_64
Running rpm scriptlet for filesystem-0:3.18-47.fc42.x86_64
Installing kernel-tools-0:6.18.7-100.fc42.x86_64
Running rpm scriptlet for filesystem-0:3.18-47.fc42.x86_64
Installing harfbuzz-icu-0:10.4.0-2.fc42.x86_64
Installing firefox-langpacks-0:147.0.2-1.fc42.x86_64
Running rpm scriptlet for alsa-utils-0:1.2.15.2-1.fc42.x86_64
Installing alsa-utils-0:1.2.15.2-1.fc42.x86_64
Running rpm scriptlet for filesystem-0:3.18-47.fc42.x86_64
Running rpm scriptlet for alsa-utils-0:1.2.15.2-1.fc42.x86_64
Installing freerdp-libs-2:3.21.0-1.fc42.x86_64
Installing kernel-0:6.18.7-100.fc42.x86_64
Installing libgphoto2-0:2.5.33-1.fc42.x86_64
Installing zed-0:0.221.4-1.fc42.x86_64
Installing assimp-0:5.3.1-6.fc42.x86_64
Running rpm scriptlet for filesystem-0:3.18-47.fc42.x86_64
Installing glibc-devel-0:2.41-16.fc42.x86_64
Installing glibc-minimal-langpack-0:2.41-16.fc42.x86_64
Installing libmtp-0:1.1.22-2.fc42.x86_64
Installing python3-perf-0:6.18.7-100.fc42.x86_64
Installing zed-cli-0:0.221.4-1.fc42.x86_64
Running rpm scriptlet for filesystem-0:3.18-47.fc42.x86_64
Installing publicsuffix-list-dafsa-0:20260116-1.fc42.noarch
Installing alsa-sof-firmware-0:2025.12.1-1.fc42.noarch
Installing glibc-gconv-extra-0:2.41-16.fc42.i686
Running rpm scriptlet for glibc-gconv-extra-0:2.41-16.fc42.i686
Running rpm scriptlet for glibc-0:2.41-16.fc42.i686
Installing glibc-0:2.41-16.fc42.i686
Running rpm scriptlet for glibc-0:2.41-16.fc42.i686
Installing openssl-libs-1:3.2.6-3.fc42.i686
Installing libcurl-0:8.11.1-7.fc42.i686
Uninstalling libcurl-0:8.11.1-6.fc42.i686
Uninstalling openssl-libs-1:3.2.6-2.fc42.i686
Uninstalling libsane-hpaio-0:3.25.6-1.fc42.x86_64
Uninstalling hplip-0:3.25.6-1.fc42.x86_64
Uninstalling hplip-libs-0:3.25.6-1.fc42.x86_64
Uninstalling glibc-devel-0:2.41-12.fc42.x86_64
Uninstalling glibc-0:2.41-12.fc42.i686
Uninstalling perl-Module-CoreList-tools-1:5.20251220-1.fc42.noarch
Uninstalling glibc-minimal-langpack-0:2.41-12.fc42.x86_64
Uninstalling glibc-gconv-extra-0:2.41-12.fc42.i686
Running rpm scriptlet for glibc-gconv-extra-0:2.41-12.fc42.i686
Running rpm scriptlet for selinux-policy-0:42.20-1.fc42.noarch
Uninstalling selinux-policy-0:42.20-1.fc42.noarch
Running rpm scriptlet for selinux-policy-0:42.20-1.fc42.noarch
Uninstalling firefox-langpacks-0:147.0-1.fc42.x86_64
Uninstalling selinux-policy-targeted-0:42.20-1.fc42.noarch
Running rpm scriptlet for selinux-policy-targeted-0:42.20-1.fc42.noarch
Uninstalling perl-Module-CoreList-1:5.20251220-1.fc42.noarch
Uninstalling hplip-common-0:3.25.6-1.fc42.x86_64
Uninstalling publicsuffix-list-dafsa-0:20250616-1.fc42.noarch
Uninstalling alsa-sof-firmware-0:2025.05.1-1.fc42.noarch
Running rpm scriptlet for firefox-0:147.0-1.fc42.x86_64
Uninstalling firefox-0:147.0-1.fc42.x86_64
Uninstalling zed-0:0.219.5-1.fc42.x86_64
Running rpm scriptlet for alsa-utils-0:1.2.15.1-3.fc42.x86_64
Uninstalling alsa-utils-0:1.2.15.1-3.fc42.x86_64
Running rpm scriptlet for alsa-utils-0:1.2.15.1-3.fc42.x86_64
Uninstalling python3-perf-0:6.18.5-100.fc42.x86_64
Uninstalling freerdp-libs-2:3.20.2-1.fc42.x86_64
Uninstalling libwinpr-2:3.20.2-1.fc42.x86_64
Uninstalling zed-cli-0:0.219.5-1.fc42.x86_64
Uninstalling vim-enhanced-2:9.1.2068-1.fc42.x86_64
Uninstalling kernel-tools-0:6.18.5-100.fc42.x86_64
Uninstalling assimp-0:5.3.1-5.fc42.x86_64
Uninstalling libgphoto2-0:2.5.31-3.fc42.x86_64
Uninstalling curl-0:8.11.1-6.fc42.x86_64
Uninstalling libcurl-0:8.11.1-6.fc42.x86_64
Uninstalling openssl-libs-1:3.2.6-2.fc42.x86_64
Running rpm scriptlet for wireplumber-0:0.5.12-1.fc42.x86_64
Uninstalling wireplumber-0:0.5.12-1.fc42.x86_64
Uninstalling wireplumber-libs-0:0.5.12-1.fc42.x86_64
Uninstalling libmtp-0:1.1.19-9.fc42.x86_64
Uninstalling ghostscript-0:10.05.1-4.fc42.x86_64
Uninstalling libgs-0:10.05.1-4.fc42.x86_64
Uninstalling kernel-tools-libs-0:6.18.5-100.fc42.x86_64
Running rpm scriptlet for kernel-tools-libs-0:6.18.5-100.fc42.x86_64
Uninstalling harfbuzz-icu-0:10.4.0-1.fc42.x86_64
Uninstalling vim-common-2:9.1.2068-1.fc42.x86_64
Uninstalling alsa-ucm-0:1.2.15.1-1.fc42.noarch
Uninstalling vim-data-2:9.1.2068-1.fc42.noarch
Uninstalling vim-filesystem-2:9.1.2068-1.fc42.noarch
Uninstalling ghostscript-tools-fontutils-0:10.05.1-4.fc42.noarch
Uninstalling ghostscript-tools-printing-0:10.05.1-4.fc42.noarch
Uninstalling alsa-lib-0:1.2.15.1-1.fc42.x86_64
Uninstalling harfbuzz-0:10.4.0-1.fc42.x86_64
Uninstalling xxd-2:9.1.2068-1.fc42.x86_64
Uninstalling glibc-langpack-en-0:2.41-12.fc42.x86_64
Uninstalling glibc-0:2.41-12.fc42.x86_64
Uninstalling glibc-gconv-extra-0:2.41-12.fc42.x86_64
Running rpm scriptlet for glibc-gconv-extra-0:2.41-12.fc42.x86_64
Uninstalling glibc-common-0:2.41-12.fc42.x86_64
Running rpm scriptlet for kernel-modules-core-0:6.18.7-100.fc42.x86_64
Running rpm scriptlet for kernel-core-0:6.18.7-100.fc42.x86_64
```

---

## Windows 11 + Qubes OS 4.3 + QWT 4.2.2 progress and questions

> 板块: General Discussion

Hi other Windows 11 qube users,

With my first attempts to get windows 11 working properly, I'm getting closer to the ultimate OS!

I'm sharing my personal progress using windows 11 qube and some questions that I have if anyone can share their own experiences and insigths that would be helpfull.

Setup
- Windows 11 Pro Template + AppVM (per user)
- Qubes 4.3
- QWT 4.2.2-1

What is (almost) working

- Installation of windows 11 pro with local admin
- dGPU passthrough
- Installation of QWT (Without GUI agent & some buggy drivers)
    ?? Xen paravirtual bus and interface drivers
    ?? Required files and services
    NO GUI agent experimental
    OK Move users directory to the private image
    50% Enable user autologon with randomized password
    ?? Xen paravirtusalised network driver (Seems installed but no difference)
    OK XEN paravirtual disk drivers
    OK Sound
    OK Win template copy/paste from/to another qube (Not woking in AppvM)

What is not working...

- Some XEN Drivers buggy (XENBUSS CONS, XENVIF 0) What are they?
- Bluetooth (Probably need to install the drivers manually after passing the bluetooth adapter)
- Seamless mode, Would love it, anyone knows if someone is working on this?
- AppVM copy/paste from/to another qube (working in the template)
- Login different AppVM with different users. 

When I turn on the windows 11 template, I automatically log in as the admin as that I have set with

> Blockquote qvm-prefs $templateName default_user $adminName

But then I have created an AppVM base on that template and when I set

> Blockquote qvm-prefs $AppVMName default_user $userName

It does not work, I log in that AppVM with the $adminName anyway.

Is anyone able to login different account with different AppVM? Why you might want to ask? Because I want to keep my separate work and personal life separated just like with any other linux AppVM.

Anyone can copy/paste in/to a win11 AppVM?

Thanks!

---

## Maybe a more effective way to secure qubes root escalation rather then having nothing

> 板块: General Discussion

I am just wondering, wouldn't it be better to remove sudo altogether and
A)add a qvm-connect tcp 22:sys-root:<arbitrary-port> and allow only sys-root access to that port in /etc/qubes/policy.d
B)Bound ssh to localhost in every template
C)Create an ssh key for every template and transfer it to sys-root
D)setup remapping so localhost:<arbitrary-port> leads to to ie sys-firewall or whatever
E)Create a script that loads up an alpine podman container everytime you run ssh and ssh to your desired vm like root@sys-net

I can only see 2 problems with this method
A)An attacker with both vulnerabilities to containers and ssh can access your whole system by opening a reverse shell afaik, even the templates if you configure this wrong, maybe a second sys-template-root would be better for that case
B)Having an appvm and dispvm conflicts since if both are online they techincally bound to the same port, and so remapping wouldnt work correctly

Now A is not really a problem becuase having attacks to both ssh and containers would take a state-level attacker, which qubes does not protect against, on the contrary this whole method would protect you from mid-level hackers escalating attacks
And B, well there has to be a better way to do this whole thing, I just came up with the idea and wondered if anyone has done such a thing, in which case link me to the git please?

I wonder if whenever a qube comes online we can setup a script that runs as root, generates a new rsa-key and sends it to sys-root, maybe a Qubes-RPC magician can enlighten me

Dont get me wrong this (probably) could never be applied to vanilla qubes as part of the default way users operate their computers, I am thinking of this as a more advanced user setup but afaik ssh-reverse shell attacks are few in the wild and container while more common it is still the most realistic choice we have unless you wanna try out a freebsd domU, in which case the UX must be afoul for such a task

Edit: if there is a Qubes-RPC magician reading this and you can achieve such a task I think the whole cross-qube contamination can be solved completely in systems with high ram, if we can keep ssh-keys in a separate vm or in dom0 then we can spin-up disposable vms in a second in systems where you have enough ram to preload 2-3 of them, I could envision adding an option in my dmenu to run a disposable-root for sys-firewall and a window poping up already logged in via ssh to sys-firewall, but these are only nightmares for my 16gb ram unless I get around setting up an alpine template and locking the disposables at 256mb ram

---

## I LOVE QUBES

> 板块: General Discussion

idk why but i feel like i have an obsession with qubes os. so much so that i recently began to feel like im terry davis and qubes is divine god sent (in this case devs are prophets) like david agaisnt those dirty oppressors. i sometimes wake up late at night and try to come up with news things that will make it better (btw im working on o project that will transform qubes into the most handsome os). when i say someone even mention qubes i feel like fly amazed by bright light . qubes os is the truly only and the most secure way to go agaisnt those who try to force us to live in orwellian dystopia

---

## Intrusion detection and prevention in Qubes

> 板块: General Discussion

I look for option to active monitor and continuously secure my Qubes installation, with focus on sys-net qube and AppVM's.

Same option I think about:
1) OSSEC
2) Wazuh
3) Suricata
 
Have someone actual experience with run and maintain any IPS, IDS or another defense software in Qube to active protect and monitor Qubes?
Does anyone have an idea how to implement such solution without TPC/IP stack? (using build-in tools qrexec and salt in long run)

Previous discussion:
https://forum.qubes-os.org/t/intrusion-detectors-in-dom0-bad-idea/3461/27

---

## Security implications using native kernels (second edition)

> 板块: General Discussion

Question from 2023 ended without any answer:
https://forum.qubes-os.org/t/security-implications-using-native-kernels/15826

As author mention, we can use `pvgrub2-pvh` in order to be able to use PVH `virt_mod`.
According to unman answer, source: https://forum.qubes-os.org/t/managing-kernels/14048/10
Using kernels provided by dom0 makes it easier to control and update
that part of the Qubes “infrastructure”.

If user take responsibility and risk to maintain each template kernel, base on distro relevant kernel and known best practice to it.
Which security implications to entire QubesOS installation could we face?
Does it improve or reduce environment security?

Whonix gateway, workstation and Kicksecure templates,
How they can be affected by usage of pvgrub2_pvh in combination with distribution kernel?

---

## Packages needed for sys-net

> 板块: General Discussion

I recently tried migrating my sys-net to an archlinux template. However it seems that the needed packages are missing. Is there a list of which packages are needed? network-manager? A wifi trayicon?

---

## Title: GSoC 2026 proposal interest: Generalize the Qubes File Converter beyond PDFs

> 板块: General Discussion

Hi everyone @marmarek @Andrew clausen @ Jean-Philippe

I'm interested in applying for the  **GSoC 2026 project: Generalize the Qubes PDF Converter to Other File Types**.

What excites me about this project is simple — Qubes' DispVM isolation is already a great safety layer, and extending it beyond PDFs to Office documents, audio/video, and spreadsheets would make it useful for a much wider audience without changing the core security model.

I've already contributed to `qubes-app-linux-pdf-converter` — [PR #37](https://github.com/QubesOS/qubes-app-linux-pdf-converter/pull/37) fixes the cancel behavior in the GUI dialog, which gave me a solid understanding of the DispVM lifecycle and signal handling in the converter pipeline.

A couple of questions before I finalize the proposal:

* Are there specific issues in the repo you'd like me to tackle to demonstrate readiness, or would it make sense to open new issues for gaps I've spotted?
* Is the preferred design a separate `qvm-convert-file` entry point, or extending the existing tool?

I will drafted a rough proposal and would appreciate any early feedback on the direction before I submit it formally.

Thanks!

---

## Dom0 resource monitor for all domains?

> 板块: General Discussion

I'm obsessed with my task manager - I feel I get the most out of my machine when I carefully manage memory & CPU consumption

The native task manager is domain-specific. It'll graph activity within a given qube, but even at the dom0 level, it won't graph consumption across domains

So I find myself spamming 'xl  list' in the dom0 terminal to get a realtime-esque system memory feed. I havent found an existing GUI to graph it, though it feels as though one would be pretty straightforward to cobble together...

Does such a program already exist somewhere? Or should I get to coding?

---

## Burp. late at night stupid. delete

> 板块: General Discussion

burp, late at night.  delete

---

## Variance in usb transfer speeds

> 板块: General Discussion

I'm curious if other users have the same behavior or if this is due to my hardware

If i connect usb drive partition as a block device (mount as xvdi) i get 2-3x the transfer speed of connecting as a USB device (mount as sda)

---

## New contributor interested in helping Qubes OS

> 板块: General Discussion

Hi everyone,

I’ve been exploring Qubes OS and I really appreciate the project’s strong focus on security and thoughtful design. It’s impressive how much effort the community puts into maintaining high standards.

I’m new here and interested in contributing. I’ve read the contributing guidelines and would be grateful for suggestions on a good first issue or area where I can start helping.

Looking forward to learning and contributing.

---

## Display Devices Widget Relationships for USB Block Devices

> 板块: General Discussion

Does anyone feel that the devices widget would be easier if the USB block devices were listed as children of their parent USB device? 

Maybe this could help both new and experienced users to quickly see the relationships, when it is necessary to use the parent not the child, like in this case.

---

## What is the performance loss for gaming with GPU passthrough?

> 板块: General Discussion

Hello,

My dream is to have a desktop running Qubes that can also do a bit of gaming.
But for that I have a question: If you get GPU passthrough to work correctly, is there any performance loss expected compared to native gaming?

I.e. is there any performance loss running a Qubes Windows VM with GPU passthrough compared to running Windows natively? What if it's a Linux VM?

I hope some people with working GPU passthrough can share their experience and performance numbers.

Thank you

---

## Improving Qubes with a GUI that contain common information needed at first installation

> 板块: General Discussion

Qubes is missing a GUI that display every information needed to know to a user who never touched Qubes after the first installation. 

I asked the AI (Claude) to use zenity to create a GUI that will display those informations. I would like Qubes integrate something very similar for the future version of Qubes this could reduce a lot of post in the forum and make the life of a normal user much more easier. I tried to integrate the picture from https://forum.qubes-os.org/t/improve-qubesos-guides-and-documentation-using-ai/38671/41 in the script but that require to use a another package so i abandoned the idea. 

[grid]
![Howto|690x465](upload://4uFCZMAC0zOj2p24g0nNpPgWAuY.png)
![Mistakes|690x468](upload://rOKVZv5C4PmAPCL3Odlck6UpkwC.png)
![NetworkWarning|690x468](upload://oVHj6JMrIJrEm0bA6RGCpdEtMAg.png)
![WelcomeTo|690x470](upload://nEJkc0tKzTSghItf6DR2ELwR1GK.png)
[/grid]


```
#!/bin/bash


WINDOW_WIDTH=950
WINDOW_HEIGHT=700

# Path to Qubes logo
QUBES_LOGO="/home/user/qubes-logo-home.svg"

# Suppress GDK warnings
export GDK_DEBUG=""
unset GDK_SCALE

# Awesome Community guides links
declare -a awesome_guides=(
    "https://forum.qubes-os.org/t/set-firefox-arkenfox-preferences-in-template/38832/1"
    "https://forum.qubes-os.org/t/wireguard-vpn-setup-4-2-and-4-3/19141"
    "https://forum.qubes-os.org/t/easily-paste-into-dom0-but-securely/37477"
    "https://forum.qubes-os.org/t/set-custom-preferences-for-brave-browser-in-disposable-qube/27351/1"     
    "https://forum.qubes-os.org/t/qubes-os-live-mode-dom0-in-ram-non-persistent-boot-ram-wipe-protection-against-forensics-tails-mode-hardening-dom0-root-read-only-paranoid-security/38868/41"
)

# Function to generate awesome community guides list
generate_guides_list() {
    local guides_text="🌟 <b>Awesome Community Guides Link You May Want to See:</b>\n"
    for guide in "${awesome_guides[@]}"; do
        guides_text+="→ <u>$guide</u>\n"
    done
    echo -e "$guides_text"
}

# Function to set icon option
get_icon_option() {
    if [ -f "$QUBES_LOGO" ]; then
        echo "--icon=$QUBES_LOGO"
    else
        echo "--icon=dialog-information"
    fi
}

# Define all slides
declare -A slides=(
    [1_title]="Welcome to Qubes OS"
    [1_content]="<b><big>Welcome to Qubes OS</big></b>\n\n<i>Security through Compartmentalization</i>\n\nA more secure operating system designed to protect you from malware and security threats through innovative isolation technology.\n\nClick the arrow below to explore."

    [2_title]="⚠️ CRITICAL: Template Network Security"
    [2_content]="<b><big>⚠️ CRITICAL SECURITY WARNING</big></b>\n\n<b><span foreground='#FF0000'>NEVER CONNECT A TEMPLATE VM TO A NET VM</span></b>\n\n<b>Do NOT connect templates to:</b>\n• sys-net\n• sys-firewall\n• sys-whonix\n• Any other networking VM\n\n<b>YOU DON'T NEED IT AND YOU MUST NOT DO THAT!</b>\n\nTemplates are meant to be <b>network-isolated</b>. They receive updates through a secure proxy mechanism, not direct network access. Connecting a template directly to a NetVM severely compromises your system's security architecture.\n\n<b>This is one of the most critical mistakes in Qubes OS!</b>"

    [3_title]="Security Architecture"
    [3_content]="<b>Qubes OS Security Architecture</b>\n\nQubes OS implements <b>security through compartmentalization</b>. Each application runs in its own lightweight virtual machine (AppVM), isolated from others.\n\n<b>Key Features:</b>\n• Hardware-based isolation\n• Trusted boot\n• Minimal TCB (Trusted Computing Base)\n• Protection against malware spread"

    [4_title]="Virtual Machines"
    [4_content]="<b>Lightweight Virtual Machines</b>\n\nQubes uses Xen hypervisor-based technology to create lightweight VMs that consume minimal resources.\n\n<b>VM Types:</b>\n• <b>AppVM</b> - Application virtual machines\n• <b>TemplateVM</b> - Base OS templates\n• <b>StandaloneVM</b> - Independent VMs\n• <b>DisposableVM</b> - Temporary VMs\n\nEach VM is isolated and can be customized independently."

    [5_title]="Compartmentalization"
    [5_content]="<b>Security Through Compartmentalization</b>\n\nQubes OS isolates different aspects of your digital life into separate VMs:\n\n<b>Example Setup:</b>\n• <b>Personal VM</b> - Personal files and activities\n• <b>Work VM</b> - Work-related tasks\n• <b>Banking VM</b> - Financial transactions\n• <b>Untrusted VM</b> - Risky browsing activities\n• <b>Multimedia VM</b> - Media processing\n\nIf one VM is compromised, others remain protected."

    [6_title]="Qubes Manager"
    [6_content]="<b>Qubes Manager - System Control Hub</b>\n\nThe Qubes Manager is your central control interface for managing your entire system.\n\n<b>Key Capabilities:</b>\n• Create and manage VMs\n• Configure network settings\n• Manage storage and backups\n• Monitor system resources\n• Update templates\n• Backup and restore VMs"

    [7_title]="Getting Started"
    [7_content]="<b>Getting Started with Qubes OS</b>\n\n<b>First Steps:</b>\n1. Open Qubes Manager from Applications\n2. Create your first AppVM\n3. Select a template (Fedora, Debian, etc.)\n4. Configure network settings\n5. Install applications in VMs\n\n<b>Pro Tips:</b>\n• Start with 2-3 VMs\n• Use color coding for organization\n• Regular backups are essential"
    
    [8_title]="How to use git clone, curl, wget in the template"
    [8_content]="<b>By default if you try to execute wget, curl, git in the template it will not work because the template are not connected to sys-net, sys-firewall or sys-whonix and THEY MUST STAY LIKE THIS ! DO NOT connect directly the template to a netVM !</b>\n\n<b>First Steps:</b>\n1. Open a terminal in one of those templates\n2. Execute this command: <b>export all_proxy=http://127.0.0.1:8082/</b>\n3. Then execute the command you want \n4. The export command earlier will allow to use the update-proxy (sys-firewall, sys-whonix) to use wget, curl, git inside the template\n5. Installing software in template is easy there is not a big difference from a normal OS like debian-13 or Fedora you just execute the same commands apt-get -y install (software name) or dnf -y install (software name)\n\n<b>Pro Tips:</b>\n• Before installing a applications inside your template you can also create a Disposable VM to test the app\n• Instead of installing a app inside the official template provided you can also clone the template and make change in the cloned template so you keep the real template clean in case something go wrong\n• Install one or 3 software in a template don't install everything inside one template"

    [9_title]="Common Pitfalls - Part 1"
    [9_content]="<b>Mistakes to Avoid in Qubes OS (Part 1)</b>\n\n<b>⚠️ Misidentifying Issue Sources</b>\nDon't assume every problem is Qubes' fault. Issues often come from Fedora, XFCE, or other software. Test in different templates to confirm.\n\n<b>⚠️ Template Confusion</b>\nThree different things: <b>Templates</b> (base OS), <b>Disposable Templates</b> (AppVMs that spawn disposables), and <b>Disposables</b> (temporary VMs). Don't confuse them!\n\n<b>⚠️ Minimal Template Pitfall</b>\nMinimal templates lack dependencies. Only use them if you're advanced and willing to troubleshoot. Beginners should use full templates.\n\n<b>⚠️ Single Template Syndrome</b>\nSticking only to Fedora OR Debian limits solutions. Switching templates can fix compatibility issues. Use both!"

    [10_title]="Common Pitfalls - Part 2"
    [10_content]="<b>Mistakes to Avoid in Qubes OS (Part 2)</b>\n\n<b>⚠️ Networking Disasters</b>\nNEVER enable 'Provides Network' in templates. Don't set up VPN-Tor tunnels in templates. Don't change networking without understanding consequences. Network goes TO templates via proxies, not FROM them.\n\n<b>⚠️ Dom0 File Copying</b>\nNEVER copy files to dom0 (wallpapers, configs, etc.). Dom0 should ONLY manage Qubes. No browsing, no apps, no file navigation in dom0.\n\n<b>⚠️ USB Attachment Mistakes</b>\nDon't attach the same USB drive to multiple qubes simultaneously. Use <b>block devices</b> instead of USB passthrough when possible. Don't use sys-usb to mount drives directly—attach them to AppVMs instead."

    [11_title]="Common Pitfalls - Part 3"
    [11_content]="<b>Mistakes to Avoid in Qubes OS (Part 3)</b>\n\n<b>⚠️ Vault Misconception</b>\nVault is just a regular AppVM with a grey label and no network. It's NOT special or more secure. It's just a label for organization.\n\n<b>⚠️ Standalone Overuse</b>\nDon't overuse standalones. Use TemplateVM + AppVM instead. Standalones don't benefit from template updates and waste resources. Only use standalones when necessary.\n\n<b>⚠️ Disposable Misuse</b>\nDon't use disposable sys-net with WiFi without understanding disposables. Don't underestimate disposable power—they're efficient for temporary tasks.\n\n<b>⚠️ No Testing</b>\nAlways test changes in temporary test qubes first. It's easy to create and delete them. Never experiment on production qubes!"

    [12_title]="Thank You!"
    [12_content]="<b><big>Thank You for Exploring Qubes OS!</big></b>\n\nYou've learned about the core concepts of Qubes OS security architecture and important best practices to avoid common pitfalls.\n\n<b>What to do next:</b>\n• Visit the official documentation\n• Explore the Qubes community forums\n• Download Qubes OS and try it\n• Read the security guidelines\n\n$(generate_guides_list)\n\n<b>Qubes OS</b> - <i>Secure by Compartmentalization</i>"
)

# Function to display a slide with question dialog (smooth transitions)
show_slide() {
    local slide_num=$1
    local title="${slides[${slide_num}_title]}"
    local content="${slides[${slide_num}_content]}"
    local total_slides=12
    local icon_option=$(get_icon_option)

    # Show the slide using question dialog
    zenity --question \
        --title="$title" \
        --text="$content\n\n<small><i>Slide $slide_num of $total_slides</i></small>" \
        --width=$WINDOW_WIDTH \
        --height=$WINDOW_HEIGHT \
        --ok-label="→  Next" \
        --cancel-label="←  Back" \
        $icon_option 2>/dev/null

    return $?
}

# Main diaporama loop - optimized for smooth transitions
run_diaporama() {
    local current_slide=1
    local total_slides=12

    while true; do
        # Show current slide
        show_slide $current_slide
        local result=$?

        if [ $result -eq 0 ]; then
            # User clicked "Next" (OK button returns 0)
            if [ $current_slide -lt $total_slides ]; then
                current_slide=$((current_slide + 1))
                # No delay - smooth transition
            else
                # Reached the end
                break
            fi
        else
            # User clicked "Back" or closed dialog (Cancel returns 1)
            if [ $current_slide -gt 1 ]; then
                current_slide=$((current_slide - 1))
                # No delay - smooth transition
            else
                # At the beginning, exit immediately without confirmation
                return 1
            fi
        fi
    done

    return 0
}

# Main execution
main() {
    run_diaporama
    exit 0
}

# Run the script
main
```

The common pitfall information are coming from @parulin in this post https://forum.qubes-os.org/t/what-are-common-pitfalls-new-qubes-users-run-into/39016 (AI written the pitfall) i only write the information about wget , curl etc 

The script is far from being perfect i know some information are missing but this is just a example of what we must have in Qubes. So to resume the idea is : User log-in in the session for the first time > Display the GUI > In case the user need to read again then we must provide a way to let him read again the GUI

If you want to see the logo you have to download it here https://www.qubes-os.org/doc/visual-style-guide/ i used this one https://www.qubes-os.org/attachment/icons/qubes-logo-home.svg

What do you think about this ?

---

## Easy hardening for beginners

> 板块: General Discussion

I know this has been asked before (a lot!) but I don't think it's been asked like this. What are some ways that a beginner can harden their system? For example, using the security-testing repositories isn't too difficult but using openbsd as a netvm is. Sorry if this has been asked before!

---

## Generated .desktop files in dom0 from vms

> 板块: General Discussion

there are many generated .dekstop files in the `~/.local/share/applications`, I want to understand the naming pattern behind them
some have `org.qubes-os.vm._qube-name` and then the pattern breaks for me. sometimes it goes like `..._qube-name.app-name.desktop` and sometimes `..._qube-name_d...`
I don't understand the "_d" thing at all. why is it there?

---

## "Disposable template" terminology

> 板块: General Discussion

I'm struggling to have a clear picture of how we ended up with the "disposable template" term.

Things might have started with the introduction of [multiple disposable templates support in Qubes 4.0](https://doc.qubes-os.org/en/latest/developer/releases/4_0/release-notes.html)... There is a somewhat related issue:

https://github.com/QubesOS/qubes-issues/issues/2486

"DisposableVM-Template(VM)" was proposed, and the discussion seems to be about how to combine "disposable" and "template", with or without "VM". Is it something that might be reconsidered?

Some other terms have been considered for "disposables" (see https://github.com/QubesOS/qubes-issues/issues/4935 ) but I can't find anyone making a proposal to use a new term like "model", "base" or something else, instead of "disposable template". If I'm correct, some participants were against the idea of introducing a new term. But still, I think that the current disposable workflow is quite different from the template-app qubes one, having a new term for "disposable template" might help.

Everyone seemed to think at that time that this term would not be confusing. That's not in line with my personal experience and discussions here on the forum. 

From that discussion, it seems that `-dvm` was attached to the name of the unique disposable, in versions prior to Qubes 4.0. It doesn't make much sense anymore IMO. `-dvmt` has been considered but it is still ugly and inconsistent.

Am I missing something here?

---

## SERIOUS? qvm-firewall bypass? possibly if you do not understand qvm-firewall and qubes-firewall service!

> 板块: General Discussion

...Ok so I have a vpn qube and I want to control it with qvm-firewall rules so it can only reach the ip of the vpn server and block everything else. I noticed that it wasn't working so I "qvm-firewall vm_name reset" and removed the single accept rule that the reset makes. Now with the vpn qube off I add one rule to check my sanity "qvm-firewall vm_name add drop". Then I start the vpn qube and test with a ping to a well known site and it WORKS, I even manage to connect my vpn. PROVING what I did has not blocked everything leaving the vpn qube when it SHOULD (I think?) surely this is worrying as qvm-firewall is suppose to be a low level networking tool that you should be able to rely on....

---

## What is your “dream” QubesOS hardware?

> 板块: General Discussion

The title says it, but some extra clarification:

- Money is no object (assume it’s free)
- Can be built, is currently for sale, or release is imminent (realistically attainable, but not necessarily in stock)
- Laptop or workstation, your choice
- Security features or performance, your choice
- Proven “compatible” with QubesOS or not, your choice
- Approach it however you like, as your personal ideal or as a recommendation for a new user
- …

Personally, I’m very happy with a HEDT with a latest generation Threadripper Pro + lots of fast RAM and disk, on WRX90 platform.

(The downside to this platform, as others have suggested, is the presence of [AMD PSP](https://en.wikipedia.org/wiki/AMD_Platform_Security_Processor) but it’s not a major concern for me.)

Interested to hear others dream platforms

---

## RAM prices

> 板块: General Discussion

I mostly used laptops so far and because of many issues with GPU passthrough on laptops I was thinking of getting a PC, but then I noticed the RAM prices. It's crazy, some went up five times above the market price half year ago.
Anyone here maybe know the ins and outs of the real deal and can share above what media is trying to feed us?
And yeah, it is Qubes related of course :wink:

---

## General Backup Formatting Info

> 板块: General Discussion

Heading down the backup road with Qubes.  Can someone advise if the target needs to be formatted?

If yes, which formatting would be best for backup.

If it doesn't need to be formatted does Qubes format the entire target and remove any existing data?

Thanks.

---

## Potential for qrexec to be used for other things

> 板块: General Discussion

I’ve been experimenting with ```sys-audio``` (successful), ```sys-gui``` (successful), ```sys-gui-gpu``` (unsuccessful) and ```sys-gui-vnc``` (unsuccessful), and I have to say, the  ```qrexec``` protocol is very powerful and versatile. 

Well done devs! You’ve built a solid piece of software 😀

I’ve been thinking of other applications for ```qrexec```:

- Sharing (passthrough) of individual Bluetooth devices between a ```sys-bluetooth``` and VMs (instead of passing through the entire Bluetooth hardware)

- ```sys-printers```, allowing all VMs access to all the printers available to the machine, mitigating the potential risks of CUPS

- A control panel to direct port forwarding to certain qubes

Just a brainstorm. 

Are there any other things anyone’s had in their mind of what else could be done with ```qrexec```?

---

## In-place upgrade: missing App menu shortcuts

> 板块: General Discussion

After an almost successful in-place upgrade from Qubes OS 4.2 to 4.3, some shortcuts were missing, so I ran:

```bash
for qube in $( qvm-ls --class TemplateVM --fields NAME --raw-data ); do
    qvm-start --skip-if-running "$qube" && qvm-sync-appmenus "$qube"
    qvm-shutdown "$qube"
done
```

---

## ZFS and Qubes OS in 2026

> 板块: General Discussion

Some commentary, some open questions.

## dom0 impact of ZFS

`$ sudo qubes-dom0-update zfs` works. But it installs 218 packages with an installation footprint of 291 MB, and these packages must stay installed because the kernel module must be rebuilt for every kernel upgrade. That's tough to swallow re: security hygiene. I don't think there's any getting around this. The module build and some of the package footprint could be offloaded to an assistant VM, but ultimately you're going to be running the product of that build in your dom0.

## Swap memory under ZFS

ZFS swap datasets are unsound under high contention of memory, as ZFS must do memory allocation for metadata as part of storage, including swap storage, so there is a risk of OOM -> swap offloading -> ZFS allocation -> but OOM! --> doom.
- Related issue: https://github.com/openzfs/zfs/issues/7734
  - Summary: this appears to be an architectural problem in ZFS, perhaps solvable by pre-allocation of whatever ZFS metadata memory could be needed for managing swap. In any case, ZFS swap reliability requires upstream work.

It is not complicated to create a regular swap partition outside of the zpool and assign that for dom0's use. But what about `/dev/xvdc1` swap, in every running qube? Is that similarly risky if backed by ZFS? It is difficult to think through the possible memory contention scenarios, through the layers of abstraction/virtualization and my own partial understanding. Perhaps the risk is naturally mitigated by qube `maxmem` thresholds and `qmemmand`, and assigning extra slack memory to dom0 for ZFS's use; or perhaps it's more complicated.
- Plausible workaround for domU: `qubes-prefs default_pool_volatile` should be directed to a different 'regular' Qubes pool outside of ZFS? Is it as simple as that? How large should the pool be -- `n * 1024M`, where `n` is the max number of VMs you expect to run concurrently?
  - Drawback: loss of the data safety/integrity guarantees provided by ZFS vs ext4/xfs/etc.

For my present install I elected to YOLO dom0 swap and `/dev/xvdc` domU swap on ZFS, mostly because it was simplest to do, and rationalized with an intention to experiment with zram for less dependence on swap.

## `/boot` on ZFS

It's marginal, but I would prefer to move `/boot` to ZFS too for checksumming and mirroring but I'm skeptical this will Just Work with coreboot+Heads.
  - Related issue: https://github.com/linuxboot/heads/issues/187
  - btrfs instead? but maybe not: https://github.com/linuxboot/heads/issues/1202

## Separate ZFS pools or separate datasets within a single ZFS pool

Under LVM, the dom0 root and the domU vm-pool are separate logical volumes. Under ZFS, the topology could be two partitions (perhaps under LVM) for two ZFS pools -- one for dom0 root and another for the vm-pool -- or it could be a single partition of a single zpool holding separate datasets for dom0 root and vm-pool. I think the single zpool approach is more efficient from a ZFS perspective, and the datasets can be tuned and quota'd individually just the same as separate zpools can. I'm not sure if there is more to consider here.
- Are there security implications to including dom0 and domU storage within a single ZFS pool?

## SSDs and free space

SSDs perform better and last longer having some amount of free storage. In a default partitioning QubesOS reserves 10% of the LUKS partition (so, a little less than 10% of the whole disk) as free space for this cause. ZFS too performs better and is more reliable with some amount of free storage, and keeps its own reservation for this (IIUC, `1/(2^5) = ~3.2%` of the pool by default).
- Is it redundant or is it helpful to have two separate reservoirs of free space? Could I forgo or reduce Qubes's 10%?
- Then change ZFS's `spa_slop_shift` to 3 so that `1/(2^3) = 12.5%` is reserved? (or 4, `1 / 2^4 = 6.25%`?)

## ZFS ARC and dom0 assigned memory

ZFS caches filesystem reads in its in-memory ARC, which by default can/will grow to >90% of system memory in contemporary ZFS. Under `free` this will show as `used` rather than as `buff/cache`, but nonetheless the cache memory is reclaimable I am reassured.

The ARC lives on the dom0 VM. Usually dom0 is assigned a pretty small slice of system memory, the rest for VMs. But hosting the ARC, dom0 needs more memory. Also, probably best there be a tighter limit on the max size of the ARC --> less risk of OOM in dom0.
- Larger `dom0_mem=min:####M dom0_mem=max:####M` on `GRUB_CMDLINE_XEN_DEFAULT`. How much makes sense, I wonder? I am assigning a lot for now while I experiment with ARC sizes.

I am clamping the size of the ARC with a module config file:

**/etc/modprobe.d/zfs.conf**:
```
# ARC clamped to 3GB-4GB of memory
options zfs zfs_arc_max=4294967296
options zfs zfs_arc_min=3221225472
```
- Note: specify the max before the min, or it seems neither will take effect
- Still tuning the size. My first experiment clamped it to 4GB-6GB, and after a couple days of use metrics showed an ARC hit rate of 99.5%, which seems to me "too high", hence the decreased range.

More:
- https://blog.thalheim.io/2025/10/17/zfs-ate-my-ram-understanding-the-arc-cache/
- https://github.com/openzfs/zfs/discussions/14064

## Defaults

The qubes pool created by `qvm-pool add -o container=<zpool name>/<dataset name> <qubes pool name> zfs` has `revisions_to_keep` of 1, while the default LVM Qubes `vm-pool` has `revisions_to_keep` of 2. Not sure if this is an intended difference.

The dataset that `qvm-pool` creates has these properties (on a zpool created with all defaults / no property overrides):
```
[user@dom0 ~] zfs get all <zpool>/<dataset>
# ... most lines snipped ..
# recordsize  128K
# compression on     (implies lz4)
# atime       on
# xattr       sa
# copies      1
# dedup       off
# acltype     off
# relatime    on
# encryption  off
# direct      standard
# org.qubes-os:part-of-qvm-pool true
```

## Compression

On a system with between 100 and 200 VMs:
```
[user@dom0 ~]$ zfs get compressratio laptop laptop/ROOT/os laptop/dom0-swap laptop/vm-pool
NAME              PROPERTY       VALUE  SOURCE
laptop            compressratio  1.69x  -
laptop/ROOT/os    compressratio  1.68x  -
laptop/dom0-swap  compressratio  3.38x  -
laptop/vm-pool    compressratio  1.69x  -
```

An overall compression ratio of 1.69x, I think meaning the size would have been 1.69x larger under no compression, or equivalently the compressed size is `1 / 1.69 = 59%` the size of the uncompressed size, a storage savings of 41%. Pretty good!

## ZFS tuning

**The zpool**:
- I see `ashift=12` = 4k pool sector size recommended often, even for disks that report 512 byte sector size. But I also see it said that for many NVMe SSDs that (honestly) report 512B, `ashift=9` (512B pool sector size) is most performant. It's not clear to me if the potential performance gain/loss is worth the testing and tweaking, so I have left this at `ashift=0` (default, autodetect) which for me results in `ashift=9`, which aligns with what my SSDs self-report.
- ZFS `encryption` is not well maintained and no longer recommended by ZFS gurus, so encryption is best handled by LUKS
- `autotrim`?

**The vm-pool dataset**:
- Common case IO is characterized by random reads and writes within large VM image files. So a `recordsize` of 16k or 128k would make more general sense than 1M, I think, except for the bulk copy that happens when a VM is cloned. However, individual VMs have different purposes and can have very different IO characteristics. What's best for a vault qube is not what's best for a torrenting qube or a server qube. I think this property can be tweaked per-VM within the same vm-pool, as each VM is itself a (sub)dataset.
- `atime=off` and `relatime=off`? Nothing I work with cares about file access timestamps, and this saves some writes, specifically the kind-of dubious IO path of a write induced by a read.
- Compression is on by default, `compress=lz4`. As shown above, this compression provides major space saving for VMs, with minimal processing cost.
- Deduplication through `dedup`, though better than it used to be, is still probably not worth the RAM/metadata and processing cost? Maybe it would have value in a templates-only vm-pool/dataset? (se below)
- `direct` is a newer IO feature said to be beneficial for NVMe and for virtualization, but maybe only for a carefully tuned workload? There is not much information on this yet. I am leaving it at its default (`direct=standard`)

**The dom0 root dataset**:
- In hour-to-hour use dom0 is mostly read-only, with trickles of writes for logging. Occasionally, package upgrades. Rarely, a bulk copy during template installation. If this is a good summary, there's little to gain (and I guess little to lose) in tuning.

## Template deduplication?

It's a refrain in ZFS literature that dataset deduplication doesn't provide the tradeoffs the admin hopes it will, outside pretty specific workloads. If `dedup` is on and the `recordsize` is small then as the data grows so does the memory+processing cost of maintaining the metadata - the tracking for every single small block. The costs grow supralinearly, I understand. Major space savings, but not for free.

I am curious if it could have useful application specifically for a TemplateVM dataset in the zpool, for users who have many custom templates. I have very many templates, most of which are dupes of each other modulo a few packages. If all of these templates, and only templates, and perhaps only the root images of the templates, were placed in a dataset with deduplication enabled and a large `recordsize` (1 MB or greater) then perhaps the costs would be workable.
- Large `recordsize` means fewer total blocks and less metadata tracking
- VM images are big single files, so no storage waste due to small files + large `recordsize`
- Template root images are mostly duplicate data, so few(er) unique blocks overall
- Tempates are only written to during Qubes Update, so write performance isn't that important, and the write amplication impact to SSDs from large `recordsize` would be mitigated by the hopefully much smaller total on-disk footprint.

On the other hand: like most users I have plenty of storage, and anyway compression is already providing good savings.

## Misc notes

- Sometimes `qvm-remove` will leave an empty directory/dataset for the VM in the zpool. `zfs list` shows several `laptop/vm-pool/disp####`, for example. Also `laptop/vm-pool/.importing` and `laptop/vm-pool/.tmp` - perhaps leftovers from a `qvm-backup-restore` run?

---

## What are the Privacy Implications of NTP Requests (time sync) and how to mitigate them?

> 板块: General Discussion

Continuing the discussion from [Prevent Qubes OS clearnet leaks](https://forum.qubes-os.org/t/prevent-qubes-os-clearnet-leaks/31735):

[quote] 
Update: After a week, I received clearnet traffic from Fedora today. My observation was incorrect. Sorry about that... :pensive:
[/quote]
Of course.

I set clockVM as downstream qube,(if at all), and block update checks
from sys-net and sy-firewall.
I also set the firewall to block any traffic originating from those
infrastructure qubes.
<small>
I never presume to speak for the Qubes team.
When I comment in the Forum I speak for myself.
</small>

---

## Cannot use spychip-free architecture w/Qubes b/c of 6gb RAM requirement. Why so fat?

> 板块: General Discussion

QOS [requires](https://doc.qubes-os.org/en/latest/user/hardware/system-requirements.html) a minimum of 6gb RAM. I just tried installing QOS on a spare Thinkpad T61 w/3gb RAM. I could easily go to 4gb but apparently that would make no difference. The error was “X startup failed, aborting installation”

This seems to kill off any possibilty to use 2008 and older Thinkpads -- precisely those that pre-date the Intel Management Engine. IIUC, the only way to run Qubes on non-spychip hardware is on a ~2008 desktop that can do ~16gb or so RAM.

I wonder why it’s so fat. Around 5 yrs ago, my T61 ran Debian just fine on 2gb RAM. I maxed it out to 4gb merely because I came across some cheap memory. I did not notice much difference. Today I still run Debian on a T61 w/4gb ram. I can open ~30+ tabs without issue. I can also run virtualbox on that with tinyXP and tiny7 without too much struggle.

I have some dumpster-harvested PCs that are newer, with spychips. These are just for tinkering and they are airgapped. I could put QOS on them but it’s somewhat purpose-defeating to run QOS on an airgapped box.

The IBM Power 9 chip is a modern day spychip-free architecture.. but it’s costly server grade stuff. 

I heard these emerging RISC-V things are spychip-free. Perhaps QOS would make sense on those.. but IIUC they are very new and likely not ready for prime time yet.

---

## Auto-cpufreq inside dom0?

> 板块: General Discussion

do you guys tried to use [auto cpufreq](https://github.com/AdnanHodzic/auto-cpufreq) in dom0? is it a huge risk to install it in dom0? also i'd like to know if this can help to have a better battery

---

## Tutorials: basic toolset for creating diagrams

> 板块: General Discussion

Some additions to the docs don't streamline well, since there seem to be different base icons and fonts in use. [Please compare](https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-organize-your-qubes.html):

**Carol, the investor**
![](upload://pp9TD4DFKYqhJ684J5yJzyV3meB.png)
**John, the teacher**
![](upload://b1izEpuNuxSjhrpYuMQfb3fezuC.png)
I'd **highly** prefer the first design. Is there a general advice on using software, icons and fonts for creating diagrams? The style guide doesn't mention anything.

---

## QubesOS on VPS Hosting

> 板块: General Discussion

I am looking at using dedicated hosting through OVHCloud to run a Qubes OS remote environment.  The idea is to set up a secure, encrypted connection to the VPS to perform sensitive work remotely, which is useful for improving security of mobile devices and laptops and anything else that could temporarily connect for some search requests then disconnect when the info is received.

Is this reasonable to do?  Does this actually improve or harden security in any way?  What could be some alternative use cases for something like this?

---

## How to contact an official to get the most accurate answer

> 板块: General Discussion

Asking questions in the community is a good choice, but sometimes you will face two problems:

1.No one answered

2. You don’t know whether the answer is correct

So can I find an official answer to the question? Is there any such channel?

---

## X230 - SPI Chip Brick Recovery - Coreboot upgrade

> 板块: General Discussion

Any experience with upgrading the Coreboot SPI firmware on x230? 


Attempted upgrade to most recent coreboot, but the flash didn't work, bricked the SPI chip.

using raspberry pi and flashprog on with pomona clip.

Looking for coreboot support and appropriate ROM file for SPI flash for EON chip.

unsure which flashprog command to use for read/writes and backing up the SPI chip.

Using Pi GPIO interface to flash.

Having posts like this:

https://github.com/0xbb/coreboot-x230/blob/master/README.md

https://www.surosec.com/posts/coreboot-x230-ime-disable.html

Using rasp pi 5 model B Rev 1.0

Trying to fix a bricked SPI on x230 basically.


Using also these guides:

https://osresearch.net/Install-and-Configure

https://osresearch.net/Downloading

https://app.circleci.com/pipelines/github/linuxboot/heads/998/workflows/cb76cb16-c555-4006-bcf1-e53207de9495/jobs/26411

https://osresearch.net/x230-maximized-flashing/

https://github.com/linuxboot/heads/

https://www.surosec.com/posts/coreboot-x230-ime-disable.html

https://kennyballou.com/blog/2017/01/coreboot-x230/

https://osresearch.net/Prerequisites#supported-devices

https://osresearch.net/Downloading

https://app.circleci.com/pipelines/github/linuxboot/heads/998/workflows/cb76cb16-c555-4006-bcf1-e53207de9495/jobs/26411

---

## How is the QubesOS firewall implemented?

> 板块: General Discussion

I have successfully created firewall rules by the two methods in QubesOS:
1) `qvm-firewall` - the python script in the host OS (dom0) which writes to `/var/lib/qubes/appvms/<vm-name>/firewall.xml` and outputs my rules with: 
`qvm-firewall  <vm-name> list`
2) The GUI: Qubes Settings > Firewall Rules

But I cant find information in the docs on how and where my rules are then implemented. Iv been looking in `iptables -L -v` on the relevant netVM and even in the appVM and I dont see the implementation of the rules I defined anywhere. Please can someone provide more information or a link to more information on how and where my rules are implemented?

---

## What's the best way to set default Firefox settings for AppVMs based on a TemplateVM?

> 板块: General Discussion

I typically create a new AppVM for each online service I interact with (to limit damage in case a serious vulnerability in Firefox is exploited by the website).

Unfortunately, this also means I spend a lot of time reconfiguring Firefox, since each new online service necessitates a new AppVM.

Is there a way to set the values once, and thereafter inherit those across multiple AppVMs? The solution doesn't need to affect existing child VMs, just new ones.

FWIW, my TemplateVM is debian-12-xfce. ChatGPT's suggestion was to choose the settings once in the TemplateVM. It claims that new AppVMs will inherit these settings. But, that didn't turn out to work.

---

## Why is `salt` used in Qubes OS for automation while being SO BAD?

> 板块: General Discussion

## Why is `salt` used in Qubes OS for automation while being SO BAD?

I am certain that using salt stack for automation in Qubes OS is not an optimal solution. Because salt is too unreliable and too often break things.

Here are some of the reasons:

### Bad error handling, mostly not handling errors at all

Salt has no proper error handling. If any step of declarative commands goes wrong with error, user sees a wall of text with call stack and un-handled exception, even in simple cases.

E.g. run on Qubes OS R4.3 this:
```bash
sudo qubesctl top.enable AAA
```

It will show you 3 screens of text with call stack. 
- What the hell is that error processing?
- Why no proper error messages?
- Why such basic exception was un-handled? 

**Terrible software design**.

### No reverts, not preserving system consistency but breaking OS

`Salt` is not able to actually revert changes if something goes wrong. I mean it can be Turing-complete language, so it can have proper processing *in theory*, but I've never saw it to be the case in `Qubes OS`, nor anywhere else.

Salt just leaves the user's system in half-way semi-broken state almost always.

- No free space? Terminate half-way!
- You have different qube name for firewall? No checks, terminate half-way!
- Syntax of some external command has changed? Terminate half-way! 

In all cases it shows ridiculous error debug-level error message and leaving a lot of un-reverted changes in the OS.
No information what should be done, no human error messages, no proper revert/undo features in case of any errors. So, every call of salt I ever make is gamble, and in many cases I regret I used it at all.

### Declarative language without any validation nor compilation

The whole syntax of salt files is terrible. You never can know in advance what fields are possible, what values are allowed. Any typo in text string in any field and you will have half-ruined OS after running this script (due to execution being stop in the middle).

It would be good to have some type of scripts validation, or compilation would be good to have on the language level.


### Salt is not for Qubes OS

Even in case salt does not fail (as often happens for me), it still is designed for different type of big-network-systems, with multiple computers, master-minions relations and etc. Qubes OS uses only part of it. The whole technology looks as alien and over-engineered technology, that does not suit Qubes OS and does not work reliably at all.

### Proper alternatives?

Maybe there are good alternatives to `salt`, that can work reliably, be well-designed, and hopefully allow interactive run like port installation scripts in FreeBSD.

Even good python or even bash automation scripts would be better in most cases.

Let's consider on task that needs automation: creating `sys-audio` qube. The proper automation solution should:

- guide user, telling what is happening on each step,
- ask questions, explaining possible options,
- revert changes if something failed at each step,
- telling user what exactly failed and what should be checked to solve the issue.

And **salt is terrible in all that**, showing walls of stack traces in every basic trouble, as we have in the current issue.

I decided to install sys-audio on R4.3 via salt commands: https://github.com/ben-grande/qusal/tree/main/salt/sys-audio . But running the first command `sudo qubesctl top.enable sys-audio` in `dom0` showed a huge 3-screen-size output with python exceptions, probably telling that sys-audio.top file was not found or something. I hope this command execution did not break anything already. I am afraid to run such commands again.

### Why is salt so bad?

I do not know, you tell me.

Each time I touch it as a user, I suffer and risk getting broken system. EACH TIME.

Can you imagine that running
```
sudo dnf install AAAA
``` 
would also show 100 lines of internal call stack with several unhandled exceptions in them instead of proper ERROR text? 
And would also leave the system in unknown state (user does not know what part of automation was done before unhandled exceptions were thrown).

Can salt be a dead-end approach for Qubes OS?

---

## Giving network access to template vms

> 板块: General Discussion

Hello, I just started using qubesos,

I was wondering if it was a good idea to give network access to the template vms, I did that because I wanted to install third party apps like signal and vscodium via the official method.

for example the official download instructions for signal:
```
# 1. Install our official public software signing key:
wget -O- https://updates.signal.org/desktop/apt/keys.asc | gpg --dearmor > signal-desktop-keyring.gpg;
cat signal-desktop-keyring.gpg | sudo tee /usr/share/keyrings/signal-desktop-keyring.gpg > /dev/null

# 2. Add our repository to your list of repositories:
wget -O signal-desktop.sources https://updates.signal.org/static/desktop/apt/signal-desktop.sources;
cat signal-desktop.sources | sudo tee /etc/apt/sources.list.d/signal-desktop.sources > /dev/null

# 3. Update your package database and install Signal:
sudo apt update && sudo apt install signal-desktop
```

these do not work on the debian-13-xfce template vm, please let me know if there was a better way to do this other than setting the netvm for the template vm to sys-firewall (there are other apps I want to install that install in a similar way issue not specific to signal)

---

## Qvm-backup compression filter execution time and output size comparison

> 板块: General Discussion

Hi,

I was curious to know how to improve the default backup tool. I saw gzip was CPU bound and thought at proposing pigz as a replacement, because it's in fedora repository and doesn't change the output format, so it's still easy to decompress for unattended backup restore.

Then, I thought it would be nice to compare with xz because it's already there, and I remembered reading about someone asking to use zstd, but it was dismissed because zstd isn't always available in you need to restore your backups in emergency, so I added to the list for more fun.

![qvm-backup|690x433](upload://tb09NJtnAOWWYsxyh8m5q2kbxg5.png)

My conclusion is it would be interesting to use pigz instead of gzip as a default compression filter, using 2 or 3 cores in its command line. This would only require Qubes OS to add this small package in the default installation. There is no drawback, and the output remains a gzip file.

Trivia: `qvm-backup --compress-filter=params` has an issue, `params` can't have parameters despite `tar --use-compress-program=params` being compatible with parameters. I had to use a shell script with the command in it, like `xz -T 5 --fast` and used that script in `--compress-filter=/my/script`.

---

## Building a PC for Qubes with coreboot or HEADS

> 板块: General Discussion

Perhaps this is covered elsewhere, but I have searched through the coreboot + HEADS documentation (and this forum) and have not found everything I needed. So I'd like to start a thread for advice, experiences, and instructions, both for myself, and for whoever may need it in the future. I will also document my success (or lack thereof) for later use in this thread.

I am currently building my own PC, with the goal of it being optimized for Qubes and running some kind of distribution of coreboot (ideally HEADS, but not necessary). My needs are not covered by the currently available machines that come with a pre-installed distribution of coreboot (and some are far too expensive) and I like to have my own custom set-up.

**Starting questions:**

* I've come to understand that a simple end-user can implement HEADS or coreboot on their own device, without needing to buy a device with it pre-installed. That's at least what I've inferred from reading through the various docs. Is this correct? 
* From what I understand, coreboot compatibility comes down to whether a particular motherboard supports it. I imagine I am covered if I purchase a motherboard listed here (https://github.com/linuxboot/heads/tree/master/boards) - of those, only the MSI Pro Z790-P fits my needs, though it is untested. Is this correct? And is there anything else to consider?
* I want to have the Qubes OS bootloader separately, on an usb memory stick instead of on the main drive/direct on the PC. Are there any considerations with doing this with coreboot/HEADS? 
* Compatibility issues, things to consider before taking the plunge, any resources I need to look over that I may have missed?

Moreover, from the coreboot page it says:

> coreboot is a source-only distribution, and as such requires building an image from source for your specific board/device.

Does this mean that I can build coreboot on my own for any kind of device, as an end user? How is this done? I'm certain this is probably covered in the coreboot docs but I haven't been able to find the particulars of it or instructions on how it is done.

Thanks for your time to whoever reads this, I will keep updating the thread if I find more answers or solutions on my own. I'm also very interested to hear about your own experiences and set-up.

---

## How stable is Qubes backup?

> 板块: General Discussion

I  would like to have feedback from users about the qubes backup mechanism did you have any bug ?  data lost? by using qubes backup or not ? 

My goal is to restore all my vm with my config software etc.. in case something go wrong in a future update are you using bash script or qubes salt for such things instead of qubes backup ?  I wonder if i should instead try to build my own qubes iso to do that

---

## Apparmor and Qubes kernel question

> 板块: General Discussion

Hey everyone so i'm creating apparmor profile to make every debian vm more safe for everyone using a debian template https://codeberg.org/dkzkz/apparmor-qubes 

I tested to load every profile in my repository in the Qubes kernel by doing apparmor_parser -r [see](https://manpages.ubuntu.com/manpages/trusty/man8/apparmor_parser.8.html) and it works great without any issue at this time.

But.. i'd ike to know something what exactly could happen if Qubes update the Qubes kernel for the vm ? Do the qubes kernel update will remove the profile inside the current debian-13 kernel ? It's unclear to me if a qubes kernel update will break the vm or not and in this case i must find something to do about that

I don't know if i was clear enough i hope so..

---

## Did 11/02/26 dom0 updates break qvm-run?

> 板块: General Discussion

I'm not sure if I'm just tired, or if the behavior of qvm-run is different now, since updating dom0 a couple of days ago.

Now when I run:

`
qvm-run -u root <vm_name> xterm
`

I get a terminal under the user account, not root.  That's different from how it was a few days ago.  At least, I think it is?  I only upgraded to 4.3 recently.

Also, should sysmaint apply to debian-13 templates, or just whonix?  Because it's not present on debian-13.

Also, several of my templates (ex: debian-13-xfce, fedora-42) are failing to update using the update manager.  But they succeed when I do it manually.

Did this new dom0 upgrade change the updater code somewhere?

Am I right or am I just tired?

---

## Programming approaches to Alternative Appmenu icon effects, Setting default workspace per qube, Additional label colors

> 板块: General Discussion

### tl;dr:
This is a work in progress. `qubes-label` is renamed to `qubes-label-tt` and `qvm-appmenus-tweak-tools` is renamed to `qvm-appmenus-tt`. Once our job is done, Independent and proper community guidelines will be posted with references to this thread. Please read the entire thread for more information.

#### Original thread:

I have been working on a tool to create additional custom labels and colors for Qubes OS. So far,  I have created a rapid [prototype](https://github.com/alimirjamali/personal-qubesos/blob/qubes-label/bin/qubes-label) to manage labels in Qubes OS database to analyze effect of new labels on behaviour of different GUI tools. Here is the output of this tool with `--help` option:
```
This tool is a simple command line utility to manage Qubes OS labels. It could
list, create, get value, print index or remove labels from Qubes OS database.
In order to avoid possible conflicts with any probable official labels which 
might be introduced in the future, it is advisable to prepend a suffix to new
custom labels. Good examples are 'custom', 'user', 'personal', etc. 
Also never ever remove standard labels!

usage: qubes-label [--verbose] [-assume-yes] [--help] [--ANSI] COMMAND ...

options:
  -v, --verbose             verbose operation
  -h, --help                show command help
  -y, --assume-yes          automatically answer yes to all questions
  --ANSI                    print label values in color with ANSI X3.64
                            (ISO/IEC 6429) escape codes in terminal. it requires
                            color capable tty such as xterm or xfce4-terminal
  --raw-data                output data in easy to parse format without headers
                            intended for bash-parsing. this will disable ANSI &
                            verbose options.

subcommands:
   list                     List all labels and their values
   create <LABEL> <VALUE>   Create a new label with the provided color value.
                            Value should be in '0xRRGGBB' format.
   get <LABEL|INDEX>        Print hexadecimal value of label
   index <LABEL>            Print index of the label in Qubes database
   remove <LABEL|INDEX>     Remove label from Qubes database.
```

My initial findings are as follow:
1. Calling `admin.label.*` API functions via `qubesd-query` is on the slow side. I did not try to switch to Python at the moment since I wanted to keep this tool as a pure bash script for the time. However, 413ms for each admin.label.Get call is not very impressive (neither end of the world). Even on this old i5-4300u based laptop. To reproduce: ```time for 1 in $(seq 0 9); do qubesd-query dom0 admin.label.Get dom0 red --empty > /dev/null;done```
I am not aware if there is any better alternative to `qubesd-query` for Admin API calls in bash. I have asked before on forum but received no feedback.
2. I wonder if any input sanitation is performed at API side. Such as SQL injection protection. Or whether clients should implement it. If anyone has information on this, please inform me.
3. I did not find any information on maximum label string length or allowed characters.
4. API has some protection against user error. For example you could not delete a label if it is used by a Qube.
5. You could inquire `admin.label.Get` with both label name and its Index. I believe this is not documented.
6. After creating the label, the necessary png/svg files has to generated and copied to `/usr/share/icons/hicolor` folder. I wonder if `~/.local/share/icons/hicolor/` would be a viable alternative. Since even the former location is not fully functional (see next points).
7. Generating all PNG/SVG files from one or more source SVG files is easy, if ImageMagick is installed.
8. Some GUI tools work perfectly with custom labels and icons. The old Qubes Manager works fine.
9. Even if you replicate all and every png/svg of existing label for your new custom label, some GUI tools would still fail. I wonder if this is because of hard-coded labels in such tools, or there are something else beside API DB and icons that I am missing. If you set a new label for any Qube, Qubes  Domains tray widget (qui-domains) goes to a restart loop on next login. `qubes-app-menu` is another GUI widget which does not recognize custom labels. Investigating these tools is the next logical step
10. Reusing existing Qubes OS icons should be OK as they are shared with CC-BY-SA license under `qubes-artwork` Github repository.
11. Using Distro Logos (e.g. Debian's, Fedora's, Arch, ...) should be OK as long as it is allowed by the their copyright guides. I tried a custom debian label with 0xd70a53 color and Debian logo. I would like this as an alternative to the current template icons.

I am trying to look beyond this and explore other possible options. There are many open or closed issues on Github with constructive feedback from users and the Qubes team. Some of them are relatively new and some are really old (over two years). I would really like to know if the team is actively working on this in parallel with a viable outcome in short term.

It would be very nice if a custom property/feature could be added to domains for effect style. Similar to what we currently have for tray icons (overlayed using Alpha channel, thin/thick borders, tint and untoched). An alternative to `qvm-get-image` and `qvm-get-tinted-image` and improved `qubesimgconvert` library.

A custom property/feature for domains to open their Windows in specific Workspaces would be very nice. This could be done via readily available tools such as `devilspice(1)`. And each workspace could have their own individual background. Nice colored backgrounds are already made by the UI/UX team.

---

## Yet another set of VPN qube DNS configuration settings

> 板块: General Discussion

I'm posting this here in case this is useful to someone. I spent quite some time to find a working solution for DNS with a VPN gateway qube.

Please note:

* I have verified that these work in practice, but my knowledge of linux network is still limited, so use these at your own risk and do your research to make sure that you stay safe
* I'm using OpenVPN, things may or may not be different with Wireguard and other protocols


Background: I have a VPN gateway qube (sys-vpn) which provides network for qubes which I want to route through a VPN tunnel. I don't use any VPN apps but only openvpn official software with command line. Using Mullvad VPN service was easy as it hijacks and redirects DNS traffic, but other services don't so I ended up with DNS issues.


First leak protection in case the VPN tunnel breaks - I put this into /rw/config/qubes-firewall-user-script:

```
iptables -I FORWARD -o eth0 -j DROP
iptables -I FORWARD -i eth0 -j DROP
```


Then setting up DNS and starting VPN with a script, let's call it "start_vpn.sh", run it as root:

```
#!/bin/bash

#cp /etc/resolv.conf /root/resolv.conf.backup
#cp resolv.conf.vpn /etc/resolv.conf
#chattr +i /etc/resolv.conf

q_dns1=10.139.1.1
q_dns2=10.139.1.2
v_dns=10.8.0.1

iptables -t nat -F PREROUTING

iptables -t nat -A PREROUTING -d $q_dns1 -p udp --dport 53 -j DNAT --to-destination $v_dns
iptables -t nat -A PREROUTING -d $q_dns1 -p tcp --dport 53 -j DNAT --to-destination $v_dns
iptables -t nat -A PREROUTING -d $q_dns2 -p udp --dport 53 -j DNAT --to-destination $v_dns
iptables -t nat -A PREROUTING -d $q_dns2 -p tcp --dport 53 -j DNAT --to-destination $v_dns

iptables -t nat -A PREROUTING -p udp --dport 53 -j LOG --log-prefix 'should not happen: '
iptables -t nat -A PREROUTING -p udp --dport 53 -j DNAT --to-destination $v_dns
iptables -t nat -A PREROUTING -p tcp --dport 53 -j LOG --log-prefix 'should not happen: '
iptables -t nat -A PREROUTING -p tcp --dport 53 -j DNAT --to-destination $v_dns

#RUN OpenVPN
openvpn --config vpn_service_config.conf

#chattr -i /etc/resolv.conf
#mv /root/resolv.conf.backup /etc/resolv.conf

iptables -t nat -F PREROUTING
```

Rationale:

* All qubes use 10.139.1.{1,2} as their DNS address, it's the Qubes virtual DNS address. However, when the VPN gateway is in use, DNS queries go through the VPN into these addresses which doesn't work of course.
* Exception is Mullvad VPN which hijacks and redirects all DNS traffic on their servers, that's why I didn't even notice any problems until I tried another VPN service. 
* So here the iptables rules are used to redirect DNS queries into the VPN service DNS address, in this case I'm using Mullvad VPN as the example, their address is 10.8.0.1. Change it to whatever address is used by your service.
* The resolv.conf changes are used to configure DNS in the gateway qube, but it's probably not needed (hence commented out) since no applications should be used in the gateway qube 
* I verified with wireshark that no traffic happens outside the VPN tunnel when this solution is used... but use at your own risk anyway.
* If you do not want to run openvpn as root, there was a way to run it as a limited user that had privilege to do network configurations that normally require root... but I'm not sure if that method works anymore. I can post details if someone wants. Since openvpn is isolated in the gateway qube anyway there is less risk in running it as root in my opinion...

---

## Dangerzone for Qubes (alpha version) Available (Qubes Trusted PDF cousin)

> 板块: General Discussion

Hi all! *(Taking off my forum moderator hat for a moment)*

As some of you may know, I'm one of the developers of [Dangerzone](dangerzone.rocks), the cross-platform Qubes Trusted PDF cousin, originally developed by Micah Lee and taken under Freedom of the Press Foundation (FPF) [since 2022](https://freedom.press/news/welcome-to-the-dangerzone/). We recently started working on Dangerzone's Qubes integration and I wanted to share some updates and welcome testers for our alpha version.

For some background, [Dangerzone](https://dangerzone.rocks) essentially reimplements Qubes Trusted PDF but cross-platform, using containers. It does however have some features beyond Qubes Trusted PDF, particularly OCR support (to make the final doc searchable), PDF compression, offline conversion by default and supporting multiple file types (images and documents).

The [alpha Qubes support](https://github.com/freedomofpress/dangerzone/issues/411) is already out, which means that Dangerzone can work in Qubes natively, using disposable qubes instead of containers for conversions. There are two caveats, though:
  - it requires manual installation from source, and configuring a diposable qube (subject to change)
  - we have not yet implemented security "guard rails", so please use **only with documents you trust** :warning: 

## Want to help testing?
Follow [these instructions](https://github.com/freedomofpress/dangerzone/blob/main/BUILD.md#qubes-os). If you encounter problems, report them on our [bug tracker](https://github.com/freedomofpress/dangerzone/issues) and give us feedback here or [on our Github Forum](https://github.com/freedomofpress/dangerzone/discussions/536).

## Next Steps

Now we're working on the [beta version](https://github.com/freedomofpress/dangerzone/issues/412) which will make Dangerzone available as a package and close some of the implementation gaps, particularly making sure we handle errors correctly and adding timeouts.

Then, we'll work towards the [stable version](https://github.com/freedomofpress/dangerzone/issues/413). This will be focused on thinking more systematically about the multi-VM architecture of Dangerzone, in particular how we can make it easier to install and maintain. I have shared some thoughts on this already [on the forum](https://forum.qubes-os.org/t/whats-the-future-of-multi-vm-applications-securedrop-workstation-inspired/18649/6) but more is to come.

### SecureDrop Workstation Integration
An additional goal is to integrate Dangerzone with [FPF's Qubes-based SecureDrop Workstation](https://securedrop.org/news/future-directions-for-securedrop/) to add document santization to journalists' workflow when exporting files to less safe systems in the newsroom. Dangerzone will keep being a standalone project but just have this extra integration.

---

## Apparmor profiles for docker containers available need tester

> 板块: General Discussion

I've made a apparmor profiles for the docker container "searxng " it works really great for me i'd like people test it to see if you have some issue with it or not 

1. To use it go take the file at my repo https://codeberg.org/dkzkz/apparmor-qubes/src/branch/main/selfhost  (? why my link have this name wtf?)
2. Take the profile for "docker" and go to "containers" and take "docker-searxng" 
3. Place them `sudo mv docker /etc/apparmor.d/ && sudo mv docker-searxng /etc/apparmor.d/ && sudo aa-enforce /etc/apparmor.d/docker && sudo aa-enforce /etc/apparmor.d/docker-searxng`
5. If u have a error protocol complaining run the aa-enforce command again it's a bug i opened a issue about that in the gitlab of apparmor https://gitlab.com/apparmor/apparmor/-/issues/592
6. Then go into your dispvm or appvm or whatever and run this command 

`docker run --security-opt apparmor=docker-searxng -p 80:8080 -d --name apparmor-docker-searxng searxng/searxng`

7. You can replace the port with the port you would like to use 
8. As sudo do aa-status you must see something like this 
![dockersearx|690x349](upload://a2aZ4PaBUbz8qb9POw3IDNspsyj.png)

Tell me if it worked for you it was really hard to create this apparmor profiles because the official documentation https://docs.docker.com/engine/security/apparmor/ do not explain how to create apparmor profiles for docker containers... i spend like 2 hours to learn how to do that

---

## Daily reminder Qubes collect your IP when you update your system

> 板块: General Discussion

They store your IP for 3 months see https://doc.qubes-os.org/en/latest/introduction/privacy.html and https://doc.qubes-os.org/en/latest/introduction/statistics.html

The only way to protect yourself is using whonix or vpn if you want to stay "anonymous" 

**This post  is not about creating drama or any conspiracy theory** this is just a reminder for those who didn't know about it also i think tails is doing the same thing if i'm not wrong ?

---

## Can a YubiKey static password be used on an SSD password entry screen?

> 板块: General Discussion

Has using a YubiKey static password on an SSD password entry screen become impossible? I feel like it used to work before. 
For people who don't use static passwords, do they memorize long passwords?

---

## Offline Qubes documentation + synchronized database of Qubes GitHub issues

> 板块: General Discussion

Hi,
Would it be a good idea for Qubes to include all offline documentation + all reported GitHub issues, which would be accessible via a local search engine?

For example, I had a problem updating Qubes 4.3 on-site—an error was displayed saying that the updater wanted to remove a protected dnf package.
I found the solution to this problem on GitHub.
What if Qubes had a search engine where I could paste the error message and then get the solution from a comment on GitHub?

Another problem I encountered was the complete corruption of a Windows virtual machine caused by uninstalling QWT.
I wanted to restore a snapshot and remembered that the command contained the phrase “revert.” What if I could type the phrase “revert” into an offline search engine and it would find the command I needed, along with a reference to the offline documentation?

---

## Clean ISO verification workflow (QMSK / RSK) for major upgrade?

> 板块: General Discussion

Hi all,

I’m preparing for the next major Qubes upgrade and plan to do what worked well for me from 4.2 → 4.3:

* download ISO
* verify
* write to USB
* fresh bare-metal install
* restore from Qubes backup

The reinstall + restore approach has been very smooth so far.

What I’m unsure about is the *cleanest* verification workflow regarding QMSK and RSK.

As I understand it:

* ISO is signed by the Release Signing Key (RSK)
* RSK is signed by the Qubes Master Signing Key (QMSK)
* QMSK is the root of trust

So should the correct chain be:

1. Import QMSK
2. Verify its fingerprint out-of-band
3. Import RSK
4. Verify RSK is signed by QMSK
5. Verify ISO with RSK

Or is verifying the ISO against a validated RSK sufficient in practice?

Also:

* Do you verify in a dedicated offline qube?
* Do you keep QMSK persistent, or import it fresh each time?
* Is using a separate “verify” VM preferred over Vault?

I’m trying to keep trust domains clean without overengineering the process.

Curious how experienced users handle this.

Thanks.

---

## Looking for some background about the disposable implementation

> 板块: General Discussion

I've been looking for some background about the disposable implementation, I've searched:

* the docs
* the news
* qubes-devel
* the forum

But nothing really answers my questions. I would like to know if a reversed approach has been considered. Currently:

* creating/managing named disposables is quite identical to creating a regular app qube
* creating/managing unnamed disposables requires making some changes on another app qube

I don't like how it is handled in the app menu, and I think that having to create an unnamed disposable, like we do for named disposables, would be a way to fix this. But the probability of me reinventing the wheel or not considering major issues already studied somewhere else is high.

---

## 8gb is a bit bandwidth intensive. Can we get a jigdo template for the 4.3.0 ISO image?

> 板块: General Discussion

I have Qubes-R4.2.4-x86_64.iso, which required borrowing someone else’s decent Internet connection to obtain. Now I would like 4.3.0, without having the fetch all 8 gigs of that ISO. In principle, it should be possible to mount an old ISO image and grab a jigdo template, to then just grab the differences needed to build the latest ISO.

---

## Script to automate the backup of the data inside a qube

> 板块: General Discussion

Continuing the discussion from [How do you organize your backups?](https://forum.qubes-os.org/t/how-do-you-organize-your-backups/3986/19):

@unman Do you have a script that automates that whole process ? (and any update in your setup since your last message in 2023?)

As a new user, one of the things that's scaring me in transitioning to QubesOS is the lack of incremental backup.

I have read a number of related posts on this forum. There seems to have been quite some effort around `wyng`, however after reading the most recent threads (e.g. https://forum.qubes-os.org/t/wyng-for-noobs/28472) it is (from my perspective) far from user-friendly.

I have seen you advocate instead in several threads for an approach that backs up the data inside the qubes directly, instead of the qubes themselves, which I find attractive. If I understand correctly, part of your reasoning is that the qubes creation process on your end is mostly automated and reproducible via `salt`.
*(Honestly, as a new user `salt` in QubesOs feels very unintuitive, and the docs are very minimal (imo), but I can always use bash scripts in dom0 to recreate the same outcome.)*

I find your argument compelling - but I'm not quite sure how you're implementing this in practice, and am guessing you have a script to automate most of the steps.

What I had in mind was to conceptually:
* Plug a usb device and attach it to a disposable AppVM "BackupVM" `Bk`
* For each Qube `Q` to backup:
  * "Mount `Q` as read-only in `Bk`" (whatever that means - somehow make `Q`'s files of interest readable by `Bk`)
  * Use a backup tool (`Kopia` in my case, that's what I'm used to) to backup those files to the usb device, in a folder named after the VM being backed up (=> how to handle renames, is there a unique ID ?)

Would you have any input/advice in that regard ?

---

## Which apparmor profiles you would like to have in Qubes?

> 板块: General Discussion

2 weeks ago i wrote this post https://forum.qubes-os.org/t/apparmor-profile-for-qubes-available/38891 I've made a lot of progress and added multiples apparmor profiles in the codeberg repository i would like to ask to the community which app you're using missing ? 

The goal is to make a lot of apparmor profiles for Qubes users and in the future i will ask to the qubes dev to make it available for every debian template of course i will maintain them myself or with other people (?) i don't know but it's not hard to do that alone anyway

[I created a issue in the apparmor gitlab repository to ask the dev from apparmor why we have a protocol error](https://gitlab.com/apparmor/apparmor/-/issues/592) when a user do aa-enforce x profile i'm worried about that every apps works fine but the error is strange..

---

## Qubes as a tool for digital sovereignty

> 板块: General Discussion

There is now growing concern, partly due to current political developments, that the strong dependence of European and, in particular, German IT on non-European, especially American and Chinese, products may become a risk factor that can no longer be controlled.

Therefore, the German Informatics Society GI has set up a [presidential working group on "Digital Sovereignty"](https://pak-digs.gi.de/) to examine this dependency more closely and identify ways to reduce it.

I have written a description of possible application aspects of Qubes for this working group:

[Qubes_usage.pdf.gz|attachment](upload://gLkX8bIlyjuIwN175n8tm59oTyn.gz) (129.6 KB)

As an open-source system with increased security, Qubes would definitely be an important building block for gradually freeing ourselves from the lock-ins of Microsoft and Apple. But first, you must know that the system exists and then know what you can achieve. I have therefore addressed the following points in the description:

- Open source - availability and maintenance
- Hardware requirements and installation
- Operation by end users
- Configuration and deployment
- Administration during operation
- Application scenarios
- Use to strengthen digital sovereignty

I hope this is a little nudge to wake some people up!

---

## Highlighting @neowutran's technical doc about Qubes

> 板块: General Discussion

Found deep in this thread:

[quote="neowutran, post:33, topic:21350, full:true"]
For one year and a half I am self hosting my domain “neowutran.ovh” on my computer.
It is a set of around 20 VM.
I started to document how it work (for a subpart of the servers vm) here: https://neowutran.ovh/qubes/articles/homeserver.pdf
For the moment it is mostly just technical infos / scripts specific to QubesOS.

I welcome feedback on how to improve the setup or documentation, and if there are better way to do some of the things I am doing, any bad things I have done regarding qubes security, …
[/quote]
And then updated most recently last month:

https://forum.qubes-os.org/t/has-anyone-used-qubes-to-host-virtual-servers/21350/40


It's a comprehensive 62 page document with a lot of code and commentary, the custom qubes @neowutran has created for his home server.

Here's the table of contents, so you can see what it covers:
[quote]
**1 Goal**
1.1 Disclaimer

**2 Rant, security and choices**
2.1 TLS 
2.2 QubesOS 
2.2.1 Where to put ﬁrewall rules

**3 External services conﬁguration**

**4 Performance**

**5 Templates**

**6 Network**
6.1 Ports 
6.2 IpV4/IpV6

**7 Qubes policy restrictions**

**8 Qubes**
8.1 Dom0 
8.2 server-tor 
8.3 server-tor-relay 
8.4 server-web 
8.5 server-vpn 
8.6 server-nginx-interne 
8.7 server-email 
8.8 server-searxng 
8.9 server-peertube 
8.10 server-matrix 
8.11 server-nextcloud 
8.12 server-upload 
8.13 server-nginx 
8.14 dnssec 
8.15 server-dns 
8.16 server-admin-vm 
8.17 server-ca 
8.17.1 Notes
[/quote]

It looks like a pretty helpful reference to me, so I wanted to highlight it.

FYI, you will get a certificate warning when you browse to the doc. The reason for which is explained in section 2.1. :)

---

## Always check your keys. Be careful of GPTs

> 板块: General Discussion

From the [official Qubes website](https://doc.qubes-os.org/en/latest/project-security/verifying-signatures.html):

> Many important Qubes OS Project assets (e.g., ISOs, RPMs, TGZs, and Git objects) are digitally signed by an official team member’s key or by a release signing key (RSK). Each such key is, in turn, signed by the [Qubes Master Signing Key (QMSK)](https://keys.qubes-os.org/keys/qubes-master-signing-key.asc) (`0x427F11FD0FAA4B080123F01CDDFA1A3E36879494` ). In this way, the QMSK is the ultimate root of trust for the Qubes OS Project.

Also, from the officlal Qubes website:

> Once you’ve obtained the QMSK, you must verify that it’s authentic rather than a forgery. Anyone can create a PGP key with the name “Qubes Master Signing Key” and the short key ID `0x36879494` , so you cannot rely on these alone. You also should not rely on any single website, not even over HTTPS.

From ChatGPT 5:

> 1. Check the Fingerprint Online
> 
> The official Qubes Master Signing Key fingerprint is:
> ```
> 427F 11FD 0FAA 4B08 0EF9  C65B 7314 89FE 9730 5480
> ```
> You can find this on:
> * Qubes OS website
> * [Qubes security GitHub repo](https://github.com/QubesOS/qubes-secpack)
> * Mailing list archives

Me:
```
git clone https://github.com/QubesOS/qubes-secpack.git
Cloning into 'qubes-secpack'...
remote: Enumerating objects: 5196, done.
remote: Counting objects: 100% (194/194), done.
remote: Compressing objects: 100% (128/128), done.
remote: Total 5196 (delta 81), reused 113 (delta 66), pack-reused 5002 (from 2)
Receiving objects: 100% (5196/5196), 2.11 MiB | 4.02 MiB/s, done.
Resolving deltas: 100% (2496/2496), done.
user@qube:~/Downloads$ gpg --show-keys --with-fingerprint qubes-secpack/keys/master-key/qubes-master-key.asc 
pub   rsa4096 2010-04-01 [SC]
      427F 11FD 0FAA 4B08 0123  F01C DDFA 1A3E 3687 9494
uid                      Qubes Master Signing Key
user@qube:~/Downloads$ gpg --show-keys --with-fingerprint qubes-secpack/keys/release-keys/qubes-release-4.3-signing-key.asc 
pub   rsa4096 2024-04-10 [SC]
      F3FA 3F99 D628 1F7B 3A3E  5E87 1C3D 9B62 7F3F ADA4
uid                      Qubes OS Release 4.3 Signing Key
```

Huh.

Me:
> It concerns me that the QMSK you purport to be "The Official Qubes Master Signing Key fingerprint is: "427F 11FD 0FAA 4B08 0EF9 C65B 7314 89FE 9730 5480" which it is not...

GPT5:
...after waiting several minutes!...it normally does not think that long with a simple question...

> Thought
> 
> You’re 100% right—my earlier fingerprint was wrong. Thanks for catching it.
> 
> The **correct Qubes Master Signing Key (QMSK) fingerprint** is:
> ```
> 427F 11FD 0FAA 4B08 0123 F01C DDFA 1A3E 3687 9494
> ```

So I am left wondering, at least one person is out there running a 'dirty' Qubes version? I wonder who or what owns that key? How did it work its way in to GPT memory? 

**Moral of the story**
* Stay vigilant.
* Always check your keys.
* Never implicitly trust Open Source if you did not check the source ***yourself***. 
* Never implicitly trust software/package repositories. 
* Never implicitly trust ChatGPT (or a website) even if it has SSL or keys check out.
* Always check multiple sources/channels. 
* Trust, but verify.

Strange Days.

---

## Custom Qubes OS installer ISO with preconfigured templates and pre-created AppVMs possible?

> 板块: General Discussion

A few years ago, with Ubuntu, I used remastering tools to create a custom bootable installer ISO from my fully configured system. This ISO included all installed software, user configurations, and settings, so after a fresh install, the system was immediately ready to use without further setup.

Is it possible to do something similar for Qubes OS? Producing a bootable installer ISO that, after installation, results in a system that is essentially ready to go, including pre installed and customized templates and pre created AppVMs with specific settings?

Is this feasible in Qubes?

If this becomes possible, it will enable sysadmins to create a ready to use Qubes OS for non technical users, requiring very little further configuration.

---

## 4.3 is hitting RAM limits earlier than in 4.2

> 板块: General Discussion

I started another thread about 4.3 being "sluggish" and since then I've installed on a second computer.  Again, it's sluggish, and the more disturbing thing (because it affects my ability to work) is that I am much more limited in the number of virtual machines I have open.

I usually have 20 or so qubes open, now after about 8, if I try to open another, I am told I can't open it because there's not enough RAM.

This is on the same laptop that handled 20 qubes at one time with no errors, same RAM, etc.  So this might account for why my installation is more sluggish.

Does anyone know what information I could gather to provide a useful bug report on this topic?

Thank you.

---

## debian-14 templates for testing

> 板块: General Discussion

I put up a couple of Debian\-14  templates, for any one who&#39;d like to try
them in 4\.3
There&#39;s a debian\-14\-xfce and debian\-14\-minimal \- some rough edges on the
build, but otherwise pretty usable\. You probably should check the
repository definitions to see if they need tuning for use with/without
cacher\.

I think it&#39;s a little early for an official build, but I&#39;ll put up PRs
to allow this\.
The templates are available here, signed with my Qubes signing key:
https://qubes.3isec.org

A new kali\-core follows shortly, based on forky as it should be\.\.

---

## Fedora 43 template?

> 板块: General Discussion

I've noticed that the `fedora-43` template is available in the `qubes-templates-itl` repository instead of the testing repository.

However, there has been no official announcement about the Fedora 43 template being released to stable.

If it's still considered a testing package, why is it in the stable repo instead of testing?

If it has been released to stable, why was there no announcement?

---

## 4.3.0-crash with unknown cause, major issues and other qubes-problems

> 板块: General Discussion

Hello,

I had a completely unexpected system crash, which I would like to report in detail. It is a long text because serious problems and errors occurred during the reinstallation, and I want to contribute to the resolution of these errors thru as detailed a description as possible:

I had (see last post) installed Qubes 4.3.0 with kernel 6.12.59.1 and debian-13 (but no Fedora) and Whonix. From the Whonix system, I created a second clone. Then I made a backup (with settings). The system ran very well.

For testing purposes, I cloned the debian-13 template and installed "Gimp" in it to test it thoroughly. That worked well at first.

Then extensive updates came, and the new kernel was installed.

During a restart, the system suddenly froze. The interface was built up to the point where the control bar in the top right corner was being constructed from right to left. One had the impression that it was trying, but it didn't succeed. The app menu on the left was missing. However, when I right-clicked in the middle of the screen, I was able to open a terminal from the small menu and save journal log files, of which I am uploading the most important ones as photos:















![IMG_8966a|666x500](upload://apBgwUj7Y2lNvIHYzFpUrhEJHmN.jpeg)


![IMG_8978a|690x333](upload://fVQmE7oEdaq8VxtQWC2k2wyAfr2.jpeg)






After further unsuccessful attempts to start, I reinstalled the system (the version with kernel 6.12.59, but only with debian-13-xfce). The other VM systems like Whonix, a complete clone of it, and some app VMs were on the backup, and I wanted to install them from it (with saved settings).

The restoration only worked superficially. The system was operational in terms of basic functions, but the following problems occurred:

- Whonix VMs and a second clone of them from the backup are restored from the backup, but they do not contain any programs, meaning the application menu is empty and thus useless. I am aware of this phenomenon in Qubes itself, as the Qubes Creator menu indicates that a clone can only be created from an already existing template or its system. But I didn't know that you can't restore a template clone from a backup with everything. If this is not an error but a general fact, it should be explicitly mentioned in the backup menu.

I then tried to install a Whonix system from the "Template Switcher," which also worked. However, if you create a clone from it, the manager does not recognize the clones or the "originals" (such as sys-whonix-2, whonix-ws-18-2, whonix-gw-18-2, as well as whonix-ws-18–2-dvm and an AppVM) correctly, with serious consequences:

- In the basic menu, for example, sys-whonix and anon-whonix could not be assigned correctly or did not appear in the menu (see photo)

![IMG_9010a|690x320](upload://mGRRrvoaZ7y98P3LDyfJiih8eoN.jpeg)


![IMG_9017a|690x489](upload://guz7ntUoqDBOVmpcLLFrBexuar.jpeg)

False anonymity warnings were also issued:

![IMG_9009a|690x462](upload://hkTMTzNDZVsloZeHQoFt4OwcsE3.jpeg)


- I wanted to create a new VM (e.g., sys-whonix) under "Create Qube," but I couldn't make any reasonable network settings here either. Additionally, the new Qube did not appear under "Services" in the app menu on the left, but as an App-VM (see photo):

![IMG_9011a|600x430](upload://1L7NkSz69snQXNPW6qSd9cEUVtq.jpeg)

General: In the backup function, in the Qubes Template Switcher (?), there were major issues that need to be checked and fixed.

As a consequence, I then completely reinstalled the entire system (including Whonix, etc.) from the boot stick just like the first time, but without using anything from the backup. The creation of clones, VMs, etc., has been working perfectly since then.

However, I have not performed an update to the new kernel (6.12.63) and test installations since then, as I want to wait for the discussion here first.

Apart from the crash issue, I have noticed other things that I would like to mention in this context:

1. USB drives are not always reliably recognized by individual VMs (since I only have two USB controllers, I did not create a usb-Qube). You can assign the drive and the text appears bold, but no drive appears in the VM's Thunar manager. This problem is irregular and can occur with USB drives of all kinds. A restart of the entire system (not the VM!) often helps, but not always. It has nothing to do with the whonix-Sysmaint system, which works well.

2a. Cloning a disp-VM template using the Qube Manager doesn't always work perfectly; it doesn't always appear in the app menu, and assignments are not carried over. If you create it in the dom0 terminal with qvm-create etc., it works perfectly. The problem existed in Qubes 4.2 as well.

2b. Program assignments in a disp-VM template are not always immediately displayed in the app menu. You first have to move the programs to the right, then assign them, confirm, close the window and reopen it, move the programs to the left and then back to the right, assign them again, and only then do they appear on the left in the app menu.

3. If you move the mouse in the APPS menu to the far right column on any row, the blue-highlighted row often flickers. This occurs irregularly, but often (the mouse is not to blame).

4. Similarly, sometimes it is the case with the Tor Control menu in the top right. It has often been difficult to access since Qubes 4.3.

5. After installing Qubes, if I remove the stick to reboot and complete the installation, the screen hangs and only a cursor symbol appears in the top left corner. Only after interrupting the power supply and restarting the computer was I able to continue.

6. During my initial installation of Qubes 4.3.0, you could enter the encryption password in the GUI at startup to complete the boot process. As intended. When reinstalling the same system, it no longer works – the password must be entered directly from the boot script, which stops after about 5 seconds, as a code line. The rest proceeds completely normally, and the "user" password can then be entered via the GUI.

So far, so good, and thank you very much for the opinions on this. If needed, I will upload more photos.

---

## Intel ME Neuter vs. HAP Bit Switch vs. RISC-V vs. ARM (Rockchip)

> 板块: General Discussion

Which of the IntelME mitigation methods is most open and effective?

IntelME neuter (me_cleaner)

HAP AltMEDisable Bit Switch (BIOS/UEFI)

RISC-V 

ARM (Rockchip)


Intel machine SPI chips can be flashed with Coreboot/Libreboot

It doesn't look like RISC-V, or ARM has Coreboot/Libreboot support

There is still the issue of CPU microcode, part of which can be 

lifted from the UEFI/BIOS firmware (/lib/firmware/intel_ucode/)

---

## Non-persistent dom0

> 板块: General Discussion

After reading [this incredibly cool guide](https://forum.qubes-os.org/t/qubes-os-live-mode-dom0-in-ram-non-persistent-boot-protection-against-forensics-tails-mode-hardening-dom0/38868) one more thing struck me: persistent dom0 adds ZERO usability! We could have "settings-vm" to fetch custom policy files and (maybe) desktop customizations from on boot, and the rest is already dynamic. This works towards more clean architecture I think.

---

## How I learned to love Liteqube (and why you should, too, even if you have enough RAM)

> 板块: General Discussion

The early installation scripts had glitches, and I can understand why people are hesitant to use Liteqube. However, I assure you that it is very much worth it, **even if you have 64Gb RAM like I do**.

The biggest advantage of Liteqube is not the reduced RAM usage, but rather the more organized and secure template system for service qubes. It's faster, more secure, conserves resources, and is more reliable. There are fewer moving parts, and those that remain are expertly configured in a failproof way. Personally, I love the read-only rootfs on disposable qubes, which proves that things are done correctly.

*But I run sys-\* from minimal template dvm's already, there is little to be done beyond that!*

Wrong. The "minimal" templates are actually quite bloated and lack the dedicated security features and elegance of litequbes, and the way you fine tune it for a specific purpose is barbaric.

Furthermore, some people criticize the lack of essential features in core-* services. However, I haven't yet found anything that I would really miss. There are no notification icons from the service qubes, and for good reason. It should be done completely differently, definitely not by running a dependency-heavy GUI app from within. **Regular core-\* qubes are fully headless and it is a good thing**. Someday we will have those icons implemented via core-xorg qube and rpc calls as it should be, just not right now.

The advantages of a secure design and organized installation scripts go far beyond your current threat model. In practical terms, 99% of the attack surface (excluding OPSEC-dependant and after we take your mobile phone out of the scope) is your browser, not your sys-net. Nevertheless, we all like having fewer things to worry about, and Liteqube provides peace of mind in this area. Additionally, it won't allow you to shoot yourself in the foot by mindlessly installing applications into your "minimal" template; still retaining all the essential functionality and providing a nice framework for things you really need!

Ah, the updates proxy. Updates are now cached in tmpfs, so you should never worry why your updatevm suddenly stopped working as intended and which file system ran out of space. Why hasn't it been done before?

---

## Insurgo Privacy Beast X230 - Still Available?

> 板块: General Discussion

Insurgo Privacy Beast x230 still available?

https://insurgo.ca/produit/qubesos-certified-privacybeast_x230-reasonably-secured-laptop/

Link returns 404

---

## Qubes - Heads - Financing

> 板块: General Discussion

It is possible to use a cryptocurrency to raise funds for QubesOS, Heads, 

Insurgo development?

This would be desirable for funding this project?

---

## "Praise and Problems in 4.3.0"

> 板块: General Discussion

Hello,

I have freshly installed and tested Qubes 4.3.0 and would like to point out some issues I noticed during the installation and testing.

The computer used is an Intel NUC I 5 MYHE with a Broadwell processor and 8 GB of RAM, and a 24-inch monitor with a resolution of 1920 x 1080.

Before installing, I first created a bootable USB stick with Rufus on a Windows 10 computer. That worked well.

1. When trying to select "Test the medium and install Qubes" in the boot menu, the following error message appeared after approximately 4% of the check (see image):

![Q430_verifmediumfail|666x500](upload://51dQfw305uK5nqerFTyt1dVVRM6.jpeg)




I repeated this several times, both with other USB sticks and on another computer. The error always occurred. It seems to be an issue with Rufus and not with Qubes itself, because then I used BalenaEtcher on a ten-year-old Macbook. The creation worked flawlessly, and the testing of the medium along with the installation went smoothly.

The only exception is that due to the limited storage, no preload disp VMs were installed, which is of course not due to Qubes 4.3.0, but to the computer.

2. Generally, Qubes 4.3.0 seems to be considerably slower than 4.2.4, which I had on the same computer before. Scrolling, for example, stutters more often, and opening windows or app VMs takes longer than before.

3. The window management is causing problems. Some newly opened windows stick to the left and top edges, and the frame disappears. They cannot be moved, no matter what you change in the window settings. You have to close them again for the window to disappear.

Some windows take up more space than the screen; they can only be removed by closing them, not by resizing or moving them.

The problems mainly occur with the whonix-disp VMs and not with the debian-13-based VMs, but also, for example, with the sound mixer window in the bar.

In general, the window management should be reconsidered and simplified, as it is not optimal and also complicated in XFCE.

4. In the app menu, some icons cannot always be clicked; nothing happens. This happens irregularly and is not tied to specific VMs.

5. When you call the Template Manager, sys-whonix will automatically start if it wasn't already on, provided you have defined sys-whonix as the general VM for updates. This is very convenient, but it can pose a security risk if, for example, a sys-whonix clone is already turned on and a user forgets about it.

Maybe a corresponding note in the template switcher would be useful to indicate that this doesn't happen.

Otherwise, Qubes 4.3.0 is very successful; there have been no major issues so far except for the ones mentioned. Many things are also visually very appealing, such as more readable fonts, the choice between dark and light mode, the warning triangles when assigning dvm templates and the explanations for them, the new settings in the "Global Config," and the Kicksecure implementation with the boot functions, and much more. It's a lot of fun!

I still need to test Kicksecure or Whonix-18 thoroughly and will report back there.

---

## Why are some pci device names so long in 4.3? dom0:00_01.2-00_00.0-00_03.0-00_00.0-00_01.0-00_00.0

> 板块: General Discussion

So I'm upgrading to 4.3 from 4.2 and while I was at it updated my motherboard BIOS and noticed the `qvm-device pci list` looks entirely different now.

I checked over the [4.3 release notes](https://doc.qubes-os.org/en/latest/developer/releases/4_3/release-notes.html) and while I didn't see information about this I did see [one of the images](https://doc.qubes-os.org/en/latest/_images/4-3_device-ux-assignments.png) show with a pci device having a similar scheme (dom0:00_1c.3-00_00.0).  It's very different from what I used in 4.2 and which was similar to the `lspci` output.


I wouldn't be surprised to find out that my motherboard is doing something to make these names especially long but the core question is why? What is it trying to tell me? 

I didn't find anything on the forums either but I suspect that's more me not thinking up good search terms. Please post a link if you know of a thread.


Here's a some of the `qvm-device pci list` output
```
dom0:00_01.2-00_00.0                                  PCI_Bridge: Advanced Micro Devices, Inc. [AMD] Matisse Switch Upstream                                       
dom0:00_01.2-00_00.0-00_03.0                          PCI_Bridge: Advanced Micro Devices, Inc. [AMD] Matisse PCIe GPP Bridge                                       
dom0:00_01.2-00_00.0-00_03.0-00_00.0                  PCI_Bridge: ASMedia Technology Inc. ASM1184e 4-Port PCIe x1 Gen2 Packet Switch                               
dom0:00_01.2-00_00.0-00_03.0-00_00.0-00_01.0          PCI_Bridge: ASMedia Technology Inc. ASM1184e 4-Port PCIe x1 Gen2 Packet Switch                               
dom0:00_01.2-00_00.0-00_03.0-00_00.0-00_01.0-00_00.0  Network: Intel Corporation Wi-Fi 6 AX200                                                                     sys-net (attached)
dom0:00_01.2-00_00.0-00_03.0-00_00.0-00_03.0          PCI_Bridge: ASMedia Technology Inc. ASM1184e 4-Port PCIe x1 Gen2 Packet Switch                               
dom0:00_01.2-00_00.0-00_03.0-00_00.0-00_05.0          PCI_Bridge: ASMedia Technology Inc. ASM1184e 4-Port PCIe x1 Gen2 Packet Switch                               
dom0:00_01.2-00_00.0-00_03.0-00_00.0-00_05.0-00_00.0  Network: Intel Corporation I211 Gigabit Network Connection                                                   sys-net (attached)
dom0:00_01.2-00_00.0-00_03.0-00_00.0-00_07.0          PCI_Bridge: ASMedia Technology Inc. ASM1184e 4-Port PCIe x1 Gen2 Packet Switch                               
dom0:00_01.2-00_00.0-00_08.0                          PCI_Bridge: Advanced Micro Devices, Inc. [AMD] Matisse PCIe GPP Bridge                                       
dom0:00_01.2-00_00.0-00_08.0-00_00.0                  Non-Essential Instrumentation: Advanced Micro Devices, Inc. [AMD] Starship/Matisse Reserved SPP              
```

---

## How I got a cube to actually print on a debian-13-xfce template - (novice ramblings)

> 板块: General Discussion

I am just recounting how I actually got a app qube to print for anyone that may be struggling with this. This is by no means the right way to do things but it worked for me. An as a full time linux user for just that past few years. I ran into hurdles that are probably trivial for most.  There also may be some stuff that the devs can steal from this, IDK.

Long story short I have two printers a Brother and an Epson both print scan combos. I haven't tested scanning yet at all. 

I manually installed the epson. following the instructions for installing a printer you can basically find from a google search. The big stumbling block I found as a linux noob was to open the printer config as root from terminal. The command is 

*$ sudo system-config-printer*.

No one ever tells you this. It's just assumed. If you don't do it this way your putting settings in that wont take. The reason I mention manually installing at all is because this is the way I did it. It may not be necessary. You may just be able to use the install script that I found for the brother printer at.

[https://help.brother-usa.com/app/answers/detail/a_id/52188/~/install-drivers-%28deb-or-rpm%29-using-the-driver-install-tool---linux](https://help.brother-usa.com/app/answers/detail/a_id/52188/~/install-drivers-%28deb-or-rpm%29-using-the-driver-install-tool---linux)

I thinks this bash script installs some sort of service. Once it runs both printers suddenly work in the template. Note I failed to get the Epson running manually, but the script fixed it kinda.

The strange part is that the service seems to create printers on the fly for printing. They appear in the print settings when I start a job then disappear shortly after. They always have usb in the name.  The details are as follows, I took out the model info and local-host address.  I imagine it dose not apply to other users. 

Description: Brother {model#} series (USB)
Device URI: ipp://localhost:{removed}/ipp/print
Make and Model: Printer -IPP Everywhere

Description: Epson {model#} Series (USB)
Device URI: ipp://localhost:{removed}/ipp/print
Make and Model: Printer - IPP Everywhere

Note if I make the self created printers Device URI that of the USB printer it breaks; and it wont print in the template from either printer.

 If, I flat out clone the USB Printer. It still wont print in the template from the clone. But if I Clone the USB printer in the template and then print in the app QUBE it works. 


It's also very odd to me because if I print  in the template the USB Printers appear in the Libre Office print selector even though there not in the print settings until after I hit print. IDK. The install script may be the cheat code for setting up printers.

I know this isn't best practice and proprietary bash script can have all kinds of junk in it but I do need to print things from time to time an until Qubes gets more polished this worked for me. 

I would be happy to hear how I should be doing it instead. The reason I think the devs maybe able to steal something here is getting printers to work is probably the hardest thing I have had to to do in Qubes. I am going on 8 hours over the past two weeks to get things going. 

I think most qubes users are power user and just set up a network print server but if your not this seems to work.

---

## Best qube chaining?

> 板块: General Discussion

Hi,

I have a question regarding chaining my qubes to have best anonyimity/privacy. I have the following qubes:
sys-net: Default qubes for network
sys-dnscrypt: running dnscrypt
sys-vpn: running a vpn with wireguard
sys-whonix: default whonix gateway

Which chaining would be best to have best privacy/anonymity for:

* an appQube which does not use tor
* an app qube which uses tor

I would like to have dnscrypt proxy for both situations

Thanks in advance!

---

## Thoughts about host-internal firewalling

> 板块: General Discussion

I'm thinking about a general firewall solution, working between local qubes only.

# task
I want to be able to implement a client-server model like DB-Server-VM / DB-Client-VM with default network communication mechanisms.

# nice
As far as possible, I want to stay on the default Qubes' way.

# idea
- creating a virtual network interface in dom0
- connecting a vm-net-local to this device
- connecting a vm-firewall-local to vm-net-local
- connecting DB-Server-VM and DB-Client-VM to that firewall
- creating the needed firewall rules in vm-firewall-local

I'm not very familiar with Xen:
Is it possible to create the interface in dom0 using the dummy kernel module, so that Xen accepts it as a normal network interface? 

In that case it would show up in vm-net-local and all following tasks would go the normal Qubes' way.

Any suggestions?

---

## No Qubes on DistroSea - why?

> 板块: General Discussion

I was wondering why there is currently no way to test Qubes OS on platforms like distrosea.com or similar online distro testing services.

From a user perspective, being listed there could still be useful: it would lower the entry barrier for curious or less technical users, allow a quick first look at the UI and basic concepts, and help people decide whether it is worth investing time in a proper installation on real hardware.

---

## Mullvad Browser has released package repos for Debian and Fedora

> 板块: General Discussion

Source: https://www.mullvad.net/en/blog/2024/6/26/mullvad-browser-135-released-with-letterboxing-improvements-and-new-installation-options/

**Source Tor:** http://o54hon2e2vj6c7m3aqqu6uyece65by3vgoxxhlqlsvkmacw6a7m7kiad.onion/en/blog/2024/6/26/mullvad-browser-135-released-with-letterboxing-improvements-and-new-installation-options

By adding their debian repo to your apt-sources, you can manage the installation of mullvad browser on the debian/fedora template.  Easily install and easily upgrade to the latest version.  And have mullvad browser become available on the disposable templates.  This new installation option for mullvad should simplify the myriad of threads we had on "how to run mullvad browser in disposable qubes?"

EDIT: Find my installation guide here: https://forum.qubes-os.org/t/mullvad-browser-has-released-package-repos-for-debian-and-fedora/27291/5

---

## How do you organize your backups?

> 板块: General Discussion

Before I discovered "Qubes OS" (it's smart now I'm addicted), I was using Debian and my backups were done with rsync on two external media and with "duplicati" to a remote server. The advantage is that my backups were incremental and I didn't have to do a full backup every time.

If I understand correctly, I have to make a full backup (of each vm) each time, which can quickly become time consuming if my vm occupy a lot of space.

I would like to have your point of view on how you organize your backups.

---

## YASA - Yet Another Salt Alternative (incremental searchable backups & enforceable declarative architecture)

> 板块: General Discussion

*[Nb: Not sure if this fits in `Guides` or `General Discussion`]*

![](upload://7a17x0yBzZ9ogLVRMbvafv8JnGn.png)
Lack of incremental searchable backups is the final hurdle that prevents me from using QubesOS as a daily driver.

I experimented with the usual suspects (Salt, Ansible, Wyng) but found that they were either incredibly rigid, lacked some basic functionalities, or required linux-wizard level to use *(personal opinion: decent backup solution should be available to all users regardless of their technical level, and without reading through 10 pages of docs)*.

I ended creating my own tool `YASA - Yet Another Salt Alternative` (source [on Codeberg](https://codeberg.org/appih5587/QubesOS_YASA)).

---
**Disclaimer: I'm not here to diss on the existing backup tools. Other contributors have clearly spent an important amount of time building them up, and I'm sure they work great for *their* use case - unfortunately they absolutely didn't fit my own expectations. I’m not claiming YASA is objectively better than something like Salt; to me, though, it’s a much smoother experience, and I hope it can help others in the same boat.**

---
Feel free to browse through the README, docs and examples on the repository.

Here's a quick summary:
- YASA is a `python3` framework that runs on "base" `dom0` (no dependencies)
- Since it's python, you don't need to learn a new language. Also, it's very flexible, if you don't like my interface you can just write your own wrappers. You can very easily extend the code to fit your own use cases.
- From the "Salt" side, YASA enables to declaratively define Qubes's "architecture" (e.g. anything but their volume's data), as well as run commands and install packages in templates.
- YASA also enables easy incremental, searchable backups using `Kopia`. Since the "architecture" is declaratively defined, only the AppVM's `/home` needs to be backed-up.

---
### A few examples:

Declaratively define the "architecture":

```python
def t_signal():
    """Signal-desktop template"""
    base = "debian-13-minimal"
    tname = "T-signal"
    misc.enforce_template_exists(tname, base, "black")

    with misc.ctx_vm_running(tname):
        debian.config_minimal_network(tname)

        cmds = """
if ! command -v signal-desktop &> /dev/null; then
    wget -O- https://updates.signal.org/desktop/apt/keys.asc | gpg --dearmor > signal-desktop-keyring.gpg
    cat signal-desktop-keyring.gpg | sudo tee /usr/share/keyrings/signal-desktop-keyring.gpg > /dev/null
    wget -O signal-desktop.sources https://updates.signal.org/static/desktop/apt/signal-desktop.sources
    cat signal-desktop.sources | sudo tee /etc/apt/sources.list.d/signal-desktop.sources > /dev/nul
fi
"""
        misc.run_commands(tname, cmds, proxy=True)
        debian.install_packages(tname, ["signal-desktop"], update=True)

t_signal()

misc.enforce_vm(
        "personal-signal",
        "T-signal",
        "yellow",
        {"features": {"menu-items": "signal-desktop.desktop debian-xterm.desktop"}},
)
```

Perform backups:
```python
# Backup a single AppVM
kopia_repo = backup.KopiaRepo(source="dom0:sdc1", path="kopia")
backup.kopia_backup_vm("MyVM", kopia_repo)
# -- wipe vm's data --
backup.kopia_restore_vm("MyVM", kopia_repo)

# Backup all AppVMs
backup.backup_all_appvms(kopia_repo)

# Functional non-destructive test: restore to a new "cloned" (except data) AppVM, then manually check that the data was restored
backup.test_backup_and_restore_vm_to_Z("MyVM", kopia_repo)
```

---
Note: This is obviously early-development:
- I am a QubesOS newcomer
- I have only tested it on my specific configuration (nb: running from a USB), and am likely missing many edge cases
- Expect bugs
- Documentation is far from prefect, but it should be reasonably understandable

---
I welcome **any** kind of feedback (and of course contributions).

---

## Packaged tools for 4.3

> 板块: General Discussion

I've uploaded some packages for 4.3 - available from
https://qubes.3isec.org/tasks.html

The packages can be used to install:

cacher - a drop in replacement for the Update Proxy that caches packages
to speed updates and reduce network load.

mirage-firewall 0.9.5 - a drop in replacement for sys-firewall that uses minimal RAM and boots very quickly.

mullvad-vpn
Thanks to the folk at Mullvad VPN this creates a qube ready for use with varieties of Mullvad VPN.
The package installs a Mullvad Proxy with the Mullvad GUI to make it
easy to set up the VPN. It also creates a disposable template, so you
can run disposables which have the Mullvad GUI and Mullvad browser
pre-installed. You can use the Mullvad browser without using a Mullvad
VPN - it's been developed with the Tor Browser team, to provide secure
browsing out of the box.

pihole
Creates a pihole standalone as a drop in replacement for sys-firewall to block ads and trackers.

sys-multimedia
Creates a "media" qube for storage of media files, and a disposable
called "multimedia". The "media" qube is configured so that opening
a file will launch multimedia, and play the file in the right app. By
default multimedia is offline. This means that you can (fairly) safely
work with content from untrusted sources.

---

## Restricting access to home-network be default - Guestnetwork setting

> 板块: General Discussion

Hi, 
I would like to generally restrict access to my home network (like a guest network setting). So that my default qubes are isolated from other devices in the network but have internet access. 
I already set up a qube who is the opposite and only have access to devices on the network but not to the internet (for access to home cloud, printer etc.) 

I would like your opinions and experiences on that matter. 
Is that whole idea necessary? If you do something similar how do you do it? 
Do you use the firewall rules or a VPN qube or something else? 

Thanks in advance!

---

## Antivirus, clamav, LMD, chkrootkit

> 板块: General Discussion

Hey there,

are there any advantages of using clamav, LMD, and chkrootkit on qubes? In other forums it seems controversial. I am not a high value target and will probably never be targeted by nation state actors. I just want to protect not only myself but other people i send documents too who may not have qubes.

I've looked into commercial AV products too like bitdefender. Besides the potential data mining, would any commericial licenses be of any benefit vs clamav?

Thanks.

---

## How do I set up systemd service with systemd timer?

> 板块: General Discussion

I already set up a system timer that trigger a systemd service. I use only debian-13 for template. So I put 2 systemd files at /etc/systemd/system/ folder  inside debian-13. Systemd service run a bash script.  Systemd timer use OnCalendar=*-*-*  that runs at specific times.

Those 3 files I used only one AppVM. It works perfect with one problem. Persistent=true inside timer not save to hard disk then when I reboot qubes or AppVm systemd service run again.

How do I solve that?

systemd timer

[Unit]
Description=

[Timer]
OnCalendar=*-*-* 07:00:00
OnCalendar=*-*-* 14:00:00
OnCalendar=*-*-* 21:00:00
OnCalendar=Sat,Sun 18:00
RandomizedDelaySec=10m
Persistent=true
Unit=backup_untrusted.service

[Install]
WantedBy=timers.target


Systemd service

[Unit]
Description=Backup bookmarks from librewolf software

[Service]
User=user
Group=user
Type=oneshot
RemainAfterExit=yes
StartLimitBurst=2
StartLimitInterval=50
ExecStart=/usr/local/bin/backup_untrusted.sh
Restart=on-failure
#StandardOutput=null
StandardError=journal
Environment="DISPLAY=:0"

---

## [Guide Request] Installing Trezor Suite (so it fully works) on Qubes/Whonix Installation

> 板块: General Discussion

I was wondering if someone could create a guide or tutorial to properly install [Trezor Suite](https://trezor.io/trezor-suite) on Qubes/Whonix. I cannot get it fully working with a Trezor Model T.

---

## Best Management Software for Maximizing Efficiency in Qubes OS?

> 板块: General Discussion

Hey everyone!

I've been using Qubes OS for a while now and I absolutely love its security and compartmentalization features. However, I've been facing some challenges when it comes to managing and organizing my different qubes effectively. It can be quite overwhelming to keep track of all the applications, files, and activities across multiple qubes.

To streamline my workflow and enhance efficiency, I've been considering using a [management software](https://www.lenovo.com/us/en/servers-storage/software/management/) specifically designed for Qubes OS. I've heard that such software can provide a centralized interface to manage and monitor qubes, simplify navigation between different domains, and optimize resource allocation.

I would love to hear from the community about their experiences with Qubes OS management software. Which management software have you found to be the most effective for organizing and maintaining your qubes? What features or functionalities do you find essential in a management software for Qubes OS?

Here are a few specific questions I have:

Are there any open-source management software options available for Qubes OS?
How user-friendly are these management software tools? Do they require advanced technical knowledge?
Are there any notable differences between various management software in terms of performance, security, or integration with Qubes OS?

Do these software tools offer any additional features beyond basic qube management, such as resource monitoring, automatic updates, or integration with other software?
Please feel free to share your personal recommendations, tips, or any insights you have gained from your own experiences. Any information or advice on the best management software for Qubes OS would be greatly appreciated!

Thank you all in advance for your help and support. Let's continue making the most out of our Qubes OS experience together!

Best regards,

---

## Introduction to Qubes OS when you do not know what it is

> 板块: General Discussion

I wrote a simple intro to Qubes OS for the average Linux user, without going into too much details.

I'd be happy to receive feedback about it, in case it's bad, if I forgot to mention something really important or whatever? :slight_smile: 

https://dataswamp.org/~solene/2025-08-03-introduction-to-qubes-os.html

---

## Motherboard recommendation for Ryzen 9 7950X and 128 gb of RAM

> 板块: General Discussion

Hi,

I am looking for motherboard recommendations. I'd like to have a box which works great with Qubes. 

Thanks!

---

## Mullvad-Browser on Desktop of my start screen

> 板块: General Discussion

Hey :)

The following problem...

I want to get the Mullvad Browser desktop file in my Work VM onto the desktop of my start screen, but I can’t manage to do it.

So far, it was relatively simple.
I created a desktop file for the respective AppImage with:

mkdir -p ~/.local/share/applications and nano ~/.local/share/applications/sample.desktop.

Then I inserted the following content:

[Desktop Entry]
Name=Sample
Comment=Start Sample Exec=/home/user/Applications/sample-2.10.2.AppImage Icon=/home/user/Applications/sample-icon.png Terminal=false
Type=Application
Categories=Utility;

In the next step, in Dom0, I updated the app menu list of the Work VM with:

qvm-sync-appmenus work.

Now my desired file appears in the list, where I can right-click it to add it to Favorites and from there simply drag it with the mouse cursor onto the desktop of my start screen.

However, now the situation is that Mullvad Browser already provides a ready-made desktop file, and the Mullvad Browser is not an AppImage but a mullvad.real file.

For some reason, the provided desktop file does not appear in the list.

Can someone help me get the Mullvad Browser from my Work VM onto the desktop of my start screen so that clicking the icon automatically opens the Mullvad Browser in the Work VM?

Thanks 🙏

---

## Custom persist should replace named disposables based on templates?

> 板块: General Discussion

I've experimented with custom-persist a little, and I think it should completely replace the current template persistence for named disposables like this:

- Add an option for custom-persist to have files reset on boot, like current template architecture already does. 
- Make an option for named disposables straight from templates.

There. If you want a named disposable with customization, use custom-persist. If you want an empty disposable, then just base it on a template. If you want the dispXXXX disposables, then you have the usual way.

---
This is meant to be a suggestion, just phrased this way because I'm trying to template out a system, and I wish it were simpler instead of having to manage ten different dvm-templates for ten different nameed disposables simply because they have different templates. Feels like wasted space, even moreso for the ones that need customization. Take this with a grain of salt.

---

## Qubes OS 4.3 – Block device panel no longer shows SATA drive sizes (UX regression)

> 板块: General Discussion

After upgrading to Qubes OS 4.3, I noticed a regression in the dom0 panel block-device overview:

In Qubes 4.2, the panel showed the size of attached SATA drives, which made it easy to distinguish between multiple internal disks. In Qubes 4.3, the size information for SATA devices is no longer displayed. Only the device name (e.g. dom0:sdX) and model (e.g. TOSHIBA HDWE140) is shown.

While this does not break functionality, it significantly reduces usability on systems with more than one internal disk, as it becomes harder to identify the correct device when attaching disks to VMs. From an admin/user perspective, this feels like a UX regression compared to 4.2.

The information is still available via dom0 CLI tools (lsblk, qvm-block), but having basic metadata like drive size directly in the panel was very helpful and reduced the risk of attaching the wrong disk.

It would be great if drive size could be reintroduced in the panel block-device menu, or made optional.

---

## Thanks, but no thanks [Kudos to Qubes and Kicksecure/Whonix, but not confident enough to use them]

> 板块: General Discussion

Though I truly appreciate the complexities of projects like Kicksecure, Whonix and Qubes, and I enjoy ‘messing’ with computers and Linux, I cannot get any of these applications/distros to work reliably. By that I mean being confident enough to take them into the ‘field’, so to speak, and be confident I could rely on them.

So, back to good old TAILS OS for me.

As I say, kudos to all involved in these projects but they are not for me.

---

## What's new in the docs since the migration?

> 板块: General Discussion

**Note:** While reading an issue about the [last update date of documentation pages](https://github.com/QubesOS/qubes-issues/issues/2169), I thought that it could be useful to have some kind of [weekly reviews](https://forum.qubes-os.org/tag/weekly-review) but for the docs. The following is a modest attempt to provide such a thing. I have only kept the substantial changes since the [migration to Read the docs](https://www.qubes-os.org/news/2025/09/11/qubes-documentation-has-successfully-migrated-to-read-the-docs/), in September.

---

# Disposables

The pages related to disposables now introduce the preloaded disposables (a new feature of Qubes OS R4.3). The whole content (text and screenshots) has been corrected, improved and expanded:

* [How to use disposables](https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-use-disposables.html#how-to-use-disposables)
* [Disposable customization](https://doc.qubes-os.org/en/latest/user/advanced-topics/disposable-customization.html#disposable-customization)
* [Disposable implementation](https://doc.qubes-os.org/en/latest/developer/services/disposablevm-implementation.html#disposable-implementation)

# Windows qubes

All the pages related to [Windows qubes](https://doc.qubes-os.org/en/latest/user/templates/windows/index.html) have been updated to the latest Windows, QWT and Qubes OS versions.

# How-tos

There are three new pages:

  * [How to take screenshots and set a wallpaper](https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-set-a-wallpaper.html#how-to-take-screenshots-and-set-a-wallpaper)
  * [How to edit a policy](https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-edit-a-policy.html#how-to-edit-a-policy)
  * [How to enable a qube service](https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-enable-a-service.html#how-to-enable-a-qube-service)

# Pages related to Qubes OS R4.3

[Qubes R4.3 release schedule](https://doc.qubes-os.org/en/latest/developer/releases/4_3/schedule.html#qubes-r4-3-release-schedule) and [Qubes OS 4.3 release notes](https://doc.qubes-os.org/en/latest/developer/releases/4_3/release-notes.html#qubes-os-4-3-release-notes) have been added to the docs.

The screenshots and the configuration screen description of the [Installation guide](https://doc.qubes-os.org/en/latest/user/downloading-installing-upgrading/installation-guide.html) have been updated to the Qubes OS R4.3 installer.

# Split GPG-2

The page about [Split GPG-2](https://doc.qubes-os.org/en/latest/user/security-in-qubes/split-gpg-2.html) has been improved but there is still some work to do here.

# For developers

The section about [Automated tests with openQA](https://doc.qubes-os.org/en/latest/developer/debugging/automated-tests.html#automated-tests-with-openqa) has been expanded.

# Bonus: new community guides

* 2025-09-11: [Allow temporary VM keyboard capture with user consent](https://forum.qubes-os.org/t/36062)
* 2025-09-15: [Wi-Fi hotspot from Qubes OS](https://forum.qubes-os.org/t/36140)
* 2025-09-17: [Wi-Fi hotspot from Qubes OS using udev](https://forum.qubes-os.org/t/36171)
* 2025-09-18: [BTRFS migration 4.2 to 4.3(-rc1) howto](https://forum.qubes-os.org/t/36191)
* 2025-09-21: [Safing Portmaster v2 in Fedora VMs](https://forum.qubes-os.org/t/36253)
* 2025-09-23: [Add new device to the default `vm-pool`](https://forum.qubes-os.org/t/36302)
* 2025-09-26: [How to Set Up NetVM with VLESS Protocol on Sing-Box](https://forum.qubes-os.org/t/36356)
* 2025-09-27: [How to fix NVIDIA's installer "Extraction failed" issue for templates](https://forum.qubes-os.org/t/36365)
* 2025-10-03: [Minimal disposable Wi-Fi hotspot from Qubes OS](https://forum.qubes-os.org/t/36514)
* 2025-10-09: [Guide to setup a ProtonVPN ProxyVM for Qubes OS R4.3.0-rc2](https://forum.qubes-os.org/t/36590)
* 2025-10-13: [Automatically attaching known devices by UUID (like SD cards)](https://forum.qubes-os.org/t/36661)
* 2025-10-13: [Quick tip for organizing custom RPC policies](https://forum.qubes-os.org/t/36665)
* 2025-10-18: [Quick and dirty video tutorial for ProtonVPN gnome app](https://forum.qubes-os.org/t/36788)
* 2025-10-19: [Guide how to increase `dom0` free disk space to avoid problems with big templates and backups](https://forum.qubes-os.org/t/36800)
* 2025-10-20: [Step-by-step nvidia GPU passthrough for cuda/vulkan compute applications](https://forum.qubes-os.org/t/36813)
* 2025-10-24: [An very easy and safe way to change template's default shell from bash to zsh for root and user](https://forum.qubes-os.org/t/36940)
* 2025-10-29: [Qubes 4.2.4 LOCKDOWN : Before, During &amp; After installation - *For HIGH RISK users (WIP)](https://forum.qubes-os.org/t/37051)
* 2025-11-11: [Flatpak Template Installation (Updated November 2025)](https://forum.qubes-os.org/t/37301)
* 2025-11-12: [Installing KDE in a debian-13 template](https://forum.qubes-os.org/t/37324)
* 2025-11-15: [Guide: Offline VM with Encrypted Disk on Qubes OS - V4 Setup: /dev/sdb1 - Internal Drive - Manual Unlock](https://forum.qubes-os.org/t/37363)
* 2025-11-21: [Nym VPN Mixnet Guide (GUI)](https://forum.qubes-os.org/t/37446)
* 2025-11-21: [Resolving `xterm: cannot load font -misc-fixed-medium-r-semicondensed--13-120-75-75-c-60-iso10646-1`](https://forum.qubes-os.org/t/37447)
* 2025-11-23: [Easily paste into dom0 - but securely](https://forum.qubes-os.org/t/37477)
* 2025-11-25: [[How-to] Network between VMs](https://forum.qubes-os.org/t/37533)
* 2025-12-08: [Split-OpenSnitch with Per-VM Identity (qubes-opensnitch-pipes)](https://forum.qubes-os.org/t/37783)
* 2025-12-08: [Windows 10 Theme for Qubes](https://forum.qubes-os.org/t/37791)
* 2025-12-09: [Nvidia GPU Pass-through on Qubes 4.3 (Fedora 43 Template)](https://forum.qubes-os.org/t/37795)
* 2025-12-10: [How to use qvm-copy-to-vm on other vm with iso](https://forum.qubes-os.org/t/37824)
* 2025-12-11: [Setting an Animated Interactive Wallpaper / Video Wallpaper for dom0 from an AppVM [No Dom0 Modifications]](https://forum.qubes-os.org/t/37860)
* 2025-12-22: [Fix slow Libreoffice](https://forum.qubes-os.org/t/38035)
* 2025-12-22: [4.3: Disable minimal-usbvm service in sys-usb to use external storage](https://forum.qubes-os.org/t/38039)
* 2025-12-27: [CAD/CAM + GRBL based CNC machines workflow](https://forum.qubes-os.org/t/38163)
* 2025-12-28: [Printing in Qubes the easy way (USB needed)](https://forum.qubes-os.org/t/38182)
* 2025-12-29: [[SOLVED] Qualcomm QCNFA765 (ath11k/wcn6855) WiFi working on Thinkpad P14s Gen4 AMD](https://forum.qubes-os.org/t/38192)
* 2026-01-07: [DRAFT OpenVPN VPN setup (4.3)](https://forum.qubes-os.org/t/38457)
* 2026-01-07: [Meta-topic: List of all VPN guides](https://forum.qubes-os.org/t/38466)
* 2026-01-11: [Devilspie2 in dom0 on Qubes 4.3](https://forum.qubes-os.org/t/38562)
* 2026-01-14: [How To make an OpenVPN Gateway in Qubes (4.2, 4.3)](https://forum.qubes-os.org/t/38632)
* 2026-01-16: [Setting up webcam and screensharing at the same time for video calls](https://forum.qubes-os.org/t/38683)
* 2026-01-18: [Widget for detailed memory usage](https://forum.qubes-os.org/t/38726)
* 2026-01-18: [[Guide] Customize Qubes OS 4.3 Login Screen (Avatar + Dark Mode)](https://forum.qubes-os.org/t/38728)
* 2026-01-20: [Guide to "sys-mini" template](https://forum.qubes-os.org/t/38764)

---

## Lenovo P1 Gen 3 issues

> 板块: General Discussion

Can any kind souls help? Been using 4.2.x (most recently .3) on a 32MB Lenovo T450 for ages, and loved it.  Bought a bigger spec laptop to run more Qubes, a P1 Gen 3 - i9/64GB which I thought would run 4.3 beautifully.  

First problem: it's a 4K screen, so everything is *tiny*  I managed to fix most of this with XFCE window scaling = 2 and a High DPI theme.  Qubes Manager etc.  still very small - how do I scale these?

Second problem: 4.3 runs like molasses on this system.  So I thought I'd go back to 4.2.4.  However, although I can get the installation screen up (providing I edit the GRUB line to include nomodeset acpi=off) I end up on the language selection page of the install with no mouse or keyboard?

Anybody have any thoughts as to how I should proceed?  Many thanks...

---

## Confusion about how the date and time is working in Qubes

> 板块: General Discussion

I've read https://forum.qubes-os.org/t/understanding-and-fixing-issues-with-time-clock/19030 but i have multiples question if @unman could reply to this post it will be great i think he have the most information about this subject 

1. What happen if a user disable systemd-timesyncd in net-vm-template ? Let's say a user want to replace systemd-timesyncd by chrony or ntpd or whatever do Qubes still can sync the date and time without any trouble from sys-net ?
2. It's unclear if Qubes depend on "systemd-timesyncd" to sync the date and time it's unclear if the user can replace this by something else
3. If a user want to replace systemd-timesyncd by chrony for example what he have to do ? Should the user modify the service like `qubes-sync-time` ?

---

## Removing Root from AppVMs and Disposable – similar Tails Without Root

> 板块: General Discussion

Tails OS deliberately disables root access by default to increase security. Removing root privileges makes privilege escalation attacks such as zero‑click exploits much harder because malicious code cannot obtain administrator rights. While this reduces the attack surface, vulnerabilities in regular privilege applications can still be exploited, allowing an attacker to operate within those limits. Privilege escalation remains possible if there are bugs that permit code execution with higher privileges. Therefore, removing root does not eliminate all risk. Since Tails removes root to gain this security benefit, why doesn’t Qubes OS optionally use the same approach for its AppVMs or disposable templates when performing particularly sensitive operations? 
Do Qubes developers consider this a worthwhile hardening measure? 
Is it a valid security enhancement?
I tested the root_annihilator script to strip root access in AppVMs and Disposable VMs using the procedure below:
https://github.com/leandroibov/root_annihilator
What improvements could be made to the script so that it matches or exceeds the “no‑root” mode used by Tails? 
Any suggestions would be appreciated. Procedure I Followed

In the target AppVM or Disposable Template, clone the VM to create a backup.

Edit /rw/config/rc.local inside the VM:
sudo nano /rw/config/rc.local

Copy and paste the contents of the script located at:
https://github.com/leandroibov/root_annihilator/blob/main/root_annihilator.sh

Save the file and reboot the system.
On each boot, /rw/config/rc.local runs the root_annihilator script by /rw/config/rc.local !

Result
Root can no longer be used to run arbitrary scripts or perform privileged tasks, but it is still possible to execute updates with sudo, for example:
sudo apt update
sudo apt upgrade
Is it possible to completely eliminate this capability? Or is it safe enough to leave it as is?
Why I BackUp the VM
Modifying /rw/config/rc.local becomes impossible once the VM boots without root, because the script disables root. To edit the file again, I would need to mount the VM’s disk partition from another environment and manually change the script something that is far more cumbersome than simply restoring the cloned backup.

---

## How can i delete my account on this forum?

> 板块: General Discussion

How can i delete my account? If its not possible, an admin can delete my acc please?

---

## Best system/way to learn Qubes OS?

> 板块: General Discussion

Hello everyone. New here, first post etc.

I had hoped to get some brief advice initially on a couple of things.

Firstly, would a Lenovo Thinkpad T470 i5 7th gen laptop be ok to install QubesOS onto? Or would you suggest installing via VM in the first instance?

Secondly, as someone who isn't 'technical' in the sense that I've never written code etc. and would in effect be a complete beginner, would you advise against me using QubesOs in any event?

My reason for wanting to use it is nothing more than I like the concept, and the privacy aspect (I use, and love, Graphene OS).

Are there are tutorials that I can be pointed to that makes the initial process a little easier than reading through all of the pages of the QubesOS documentation, or is that a necessary part of learning just how complex the system is so as not to make any missteps when using?

Thank you all in advance for any advice and best regards.

---

## Qubes OS print books from Amazon

> 板块: General Discussion

Hi

There are physical books about Qubes OS available on Amazon. I learn best with a physical book; unfortunately, I am from that generation.

Unfortunately, many books on Amazon are written with AI :-1: Can anyone recommend a specific book from Amazon? I am a complete beginner with Qubes OS, but not with Linux.

Thank you

---

## BIOS/UEFI/COREBOOT Directory Structure

> 板块: General Discussion

Any users having an idea of the BIOS/UEFI/Coreboot directory structure?

Any idea where a CPU microcode file might be found?

---

## Qubes OS Sales Figure Estimate

> 板块: General Discussion

Hello,

Any concept of QubesOS product sales figures? Any idea?

---

## Mobile OS Compatible With Qubes OS Workflow

> 板块: General Discussion

what would be the best OS for telephone that can be compatible to Qubes hygiene ?

---

## Kicksecure vs. Mirage

> 板块: General Discussion

Hi, I was considering to use Kicksecure but I've encountered Mirage OS (https://mirage.io/), what do you recommend? Thanks!

---

## Need for an Official VPN Gateway Guide!

> 板块: General Discussion

For far too long the community has been requesting an updated, official guide for setting up a secure VPN Gateway within Qubes OS. The existing documentation references instructions tailored for Qubes OS 4.1, which are no longer compatible with v4.2 or v4.3. As a result, many users are left searching through outdated resources or relying on unofficial, potentially insecure guides.

This ongoing issue has led to numerous forum threads and community discussions, highlighting the urgent need for clear, official guidance. Unfortunately, despite awareness of this gap, developer responses and support have been noticeably absent—mailing list threads and community requests have gone unanswered.

Given that Qubes OS prides itself on being a security-centric operating system, the absence of official VPN setup instructions is concerning. A properly configured VPN Gateway is a cornerstone of a comprehensive security posture, and the community’s trust hinges on transparent, supported guidance from the developers.

**I urge the Qubes OS team to acknowledge this need and provide an official, up-to-date VPN Gateway setup guide.** The community deserves clarity and confidence in their security configurations.

I will be raising this issue via the **Qubes GitHub** repository and **mailing lists** to emphasize the importance of official support.

**Please support this petition by commenting or liking this post.**

---

## Surviving my days with Qubes 😅

> 板块: General Discussion

Today I’m learning something new:

SSH for my homework, with Ubuntu and Qubes.

I used:
scp -r [name@xx.xx.xx](mailto:name@xx.xx.xx):/home/user/ ~/Documents

At first, I ran the command on the server directory, so I copied it on the same laptop 😅 Then I understood what I needed to do — run the same command, but in the destination terminal!

It took me about 4 hours to do that, to understand the process, manage the VMs, and everything else…

after that,

LuksOpen
sudo mount mapper
and qvm-block attach

qvm-copy-to-vm for send file in other VM

Because I have an offline VM and a detached sdb for safety. The sdb is in my dom0.

![](https://www.linuxquestions.org/questions/images/smilies/jawa.gif "Linux Monk")

21:21 — Nothing worked :')) My VM didn’t have enough allocated space, so it couldn’t receive everything. Since I have a 900 GB disk that’s encrypted and only partially attached, I can’t send everything to the disk at once. When you send a file through another VM, it’s actually written in the source VM’s memory — the one you configured.

After tweaking things too much, I got lost with /mnt/mapper, luksOpen, and qvm-block.

I managed to fix my issues with /mnt/mapper and the rest. Now I just need to recreate a VM with the encrypted sdb1 disk as its allocated space. :S
Anyway, I’m going to sleep — I’ll deal with it tomorrow!


:cowboy_hat_face:

---

## Feedback gathering: what features made you switch to Qubes OS?

> 板块: General Discussion

Hello :wave: 

I'm quite curious to know what are the Qubes OS features that are seen as the most valuable by its users, or what Qubes OS offered you that you couldn't achieve in another operating system?

(this is a personal topic, nothing official :slight_smile: )

---
**Edit:**
[details="summary of the answers"]
The following items with emphasis (bold) are mentioned more than once:

- Xen-level **compartmentalization/isolation**: 
  - **to control the software**
  - to protect myself from a hostile WAN and a browser (any browser) with organization-level cross-incentives
  - ... that already worked enough (within reason) out of the box
  - slick
  - clear
- Totally doable system/network admin scriptability/orchestration
- **Pretty good integration with Whonix/Tor**:
  - torify arbitrary applications without fearing leaks
- Free, libre, open source (comment: [Is Qubes OS free and open-source software?](https://doc.qubes-os.org/en/latest/introduction/faq.html#is-qubes-os-free-and-open-source-software))
- doesn't have a suspicious license agreement
- **Helpful user community**, active forum that celebrates useful ideas, people, and solutions.
- **accessible and careful devs** 
- **ability to set up offline qubes** for storing secrets such as passwords and GPG keys
- **Idea of templates, appVM, and dvm is brilliant**:
  - working with many Linux distros, Windows, it is fast and it takes up little disk space
  - using cool tools that work only with older Debian/Ubuntu versions, without worrying about it
  - installing apps without worrying about dependencies
  - using many VPNs simultaneously.
  - **Disposable vms**:
    - for security
    - The ability to create nuanced disposable templates to investigate and test with save so much prep work.
- excellent and very convenient forensic protection, thanks to the large fantastic community for guides.
- ability to run virtual machines with integration between VMs
- minimize any damage from Malware, phishing, and other unpleasant efforts
- the UI:
  - a **single app running in a VM can integrate well in the GUI domain**, almost as a regular app in a regular distro
  - **VM-dependent description and window colors** help to refrain from doing stupid things
- Isolating base OS from the network and letting only virtual vm’s to have network/internet.
- the possibility of attaching a webcam to a virtual machine and have it working out-of-the-box for video calls
- The security that allows a complex Windows 7 environment to still be used
- **For testing, the creation of VM clones at a click**, stopping to make disastrous tests expensive, with client/server environments on just one machine
- The peace of mind when doing things like going to dangerous websites or opening documents of doubtful origin.
- Having a modern software system showing, in teaching, where software development is / should be going nowadays.
- Tails-like amnesic behavior when wanted, but with full customization and the ability to install whatever apps
- And the flexibility to run any OS in isolated qubes, with strong security guarantees, is unmatched.
- The **networking that gives absolute control** (up to what sys-net is doing within itself) because each netvm is a router we can audit and monitor
- That networking allowed me to build complex systems **using many VPNs**, although it was possible on OpenBSD using multiple routing tables or Linux with ip rules, it was easier to use on Qubes OS
- in freelance/professional activity, **being able to separate the systems used for each client and their VPN was a must**
- to be able to `npm install ...` to get work done and I don't want to have to worry about getting infected everytime I need to do so.
- separating applications into qubes allows better stability: when I'm "fidgeting", installing or making changes in certain qubes (media, personal) it will never affect my work qubes. 
- Qubes seems to be the only option which gives actual protection against digital fingerprinting:
  - ability to run whatever apps without worrying that I will end up with identity stolen.
  - make Youtube show me only the content I want. If I want to learn a skill I can create a vm for this topic. And Youtube will show me videos about this topic specifically
[/details]

---

## Is the ephemeral_volatile option in qvm-pool safe and stable?

> 板块: General Discussion

There isn't much discussion about the `ephemeral_volatile` option that can be enabled with `qvm-pool set vm-pool -o ephemeral_volatile=True`. When `True`, this option automatically encrypts DispVM's volumes with ephemeral keys. I discovered the option in a Github issue:

https://github.com/QubesOS/qubes-issues/issues/6958

**Is this option safe and stable to enable on the primary `vm-pool`?**

---

## Does Qubes use the Cloudflare dmcrypt patches?

> 板块: General Discussion

In 2020, Cloudflare made a [series of patches](https://blog.cloudflare.com/speeding-up-linux-disk-encryption/) to dmcrypt to get it to near native speeds. Given that Qubes uses the same fde scheme, were these patches ever incorporated into QubesOS? They’re stable enough to have made it into the Linux kernel and any concerns about architecture are moot given Qubes is x86 only.

---

## Qubes OpSec guidelines

> 板块: General Discussion

I tried to make a simple post name and setup for this, @unman i had contact with you a while ago but through deleting the qube i had setup we lost contact are you able to message me here so we can get back in contact and i can discuss our previous conversations as it was a business description.

---

## A mouse (or mice) on wallpaper suddenly appeared?

> 板块: General Discussion

Hey folks, sup? I went away from my computer so, once I was back, I had to log in again. But when I clicked on power button so the screen would flash again from its black mode, instead of the usual wallpaper, there was this blue wallpaper with a grey mouse/mice on it?? I clicked "cancel", it went black again and then, when I clicked any key all over, the usual Q screen showed up...?

Has it ever happened with anyone? Shall I worry about it? A brief top command didn't give me anything, but then again...? Thanks in advance!

---

## Qvm-console vs qvm-console-dispvm

> 板块: General Discussion

What is the purpose of `qvm-console` in Qubes 4.3? All I have is this:

```
Usage: /usr/bin/qvm-console vmname
Connects to another VM console using the admin.vm.Console RPC service.
```

And all I get is that it `Cannot connect to <QUBE_NAME>`

I got used to type `qvm-con<TAB>` to get `qvm-console-dispvm` :slight_smile:

---

## Qubes kaso-chan

> 板块: General Discussion

Edit by @fsflover: 
continuing discussion from [Qubes OS Wallpapers](https://forum.qubes-os.org/t/qubes-os-wallpapers/2819/21):

[quote="fgogachaddict8, post:20, topic:2819, full:true"]
[Finished the OS-tan at last ](https://www.pixiv.net/en/users/34232659). Also used sebuq’s wallpaper.

![qubeOS-tan](upload://1iMl5gYpGiltUR6ixaX90JMqHzi)

![01](upload://hEBtYtc95mXCPihUX085rKFnTkB)

![02](upload://uwalOQIAZsjnkCcq1IE1j6Nn65U)

Onion shaped earrings (and violet tie) - TOR
Cap - Xen
Dark blue color - Fedora
[/quote]

Original post by @whoareyou below:

________________________


Never thought Qubes has OS-tan design wwwww, btw appreciate the artworks

---

## 4.2.4 > 4.3 in-place upgrade on a NovaCustom Machine

> 板块: General Discussion

Has anyone done an in place upgrade on Novacustom v56 or v54? Where there any issues? Just trying to get some info before I decide which way I want to upgrade

---

## Onion documentation

> 板块: General Discussion

You probably know that the Qubes website is available (mostly) as an
onion site, at `http://qubesosfasa4zl44o4tws22di6kepyzfeqv3tg4e3ztknltfxqrymdad.onion/`

Qubes documentation is also now available as an onion at `http://doc.qubesosfasa4zl44o4tws22di6kepyzfeqv3tg4e3ztknltfxqrymdad.onion/`
It's a work in progress - there are links that take you outwith the Tor
network, but these are marked - generally it's self contained.

The `Documentation` link on the onion site now takes you to the onion
doc site. Much better.

If you dont know what an onion site is, or why you might want to use
it, read [this](https://support.torproject.org/tor-browser/features/onion-services/)

The source for documentation is on [GitHub](https://github.com/qubesos/qubes-doc). The onion site is mirrored
from source, and built with minor link rewritings.

The documentation is a community effort. Please help us improve it. This
is a good way to make a contribution to the project.  Contributions are
always welcome - look at [this page](https://doc.qubes-os.org/en/latest/developer/general/how-to-edit-the-rst-documentation.html) or on the [onion](http://doc.qubesosfasa4zl44o4tws22di6kepyzfeqv3tg4e3ztknltfxqrymdad.onion/developer/general/how-to-edit-the-rst-documentation.html)

You can see the open issues re documentation on GitHub using the `C:doc` tag.
If you dont want to use GitHub, (and I completely understand that), you
can email or PM me with your contribution and I'll merge it with credit
(if wanted).

---

## Qubes-mirage-firewall v0.9.5

> 板块: General Discussion

I am happy to announce that the latest release of Qubes Mirage Firewall has just been released ([0.9.5](https://github.com/mirage/qubes-mirage-firewall/releases/tag/v0.9.5)).

In addition to ecosystem and compiler updates, this release update ARP entry behavior: the unikernel now responds with its MAC address for every APR request from a client. This fixes issues with some VPN clients ([#221](https://github.com/mirage/qubes-mirage-firewall/pull/221)). Also, this version update HVM client handling: HVM Clients, such as Windows, have two network interfaces but only use one. This causes deadlock states because the connection protocol for one interface is not completed, leading the unikernel to wait for the client to shut down. Now, each connection uses its own thread, and the unikernel can handle Windows HVM ([#219](https://github.com/mirage/qubes-mirage-firewall/pull/219)).

You can update either manually (local compilation with podman/docker, or download from github, check hashsum, copy to dom0) or with the salt formula available on the github repository, or with @ben-grande or @unman’s repositories.

If you have any comments, please let us know, on this forum or on github.

---

## Paper on mitigation of IT risks

> 板块: General Discussion

In my work in the digital sovereignty working group of the German Gesellschaft für Informatik, I created a paper outlining the typical risks we are confronted with using standard proprietary IT systems like Windows and possibilities for mitigating these risks, including the use of Qubes OS.

The paper is structured as follows:

1 Awareness of the risks of IT use
2 Vulnerabilities and risks
3 Causes and originators of threats
4 Improving technical protection
5 Necessary changes in IT usage
6 Conclusion

If you are interested, please have a look at it:

[IT-Risks_and_Sovereignty_V3_0 en-US.pdf.gz|attachment](upload://oGj4oSXhwgOOWEedGR1mre5cRHd.gz) (94.6 KB)

I would greatly appreciate any comments!

---

## Qubes OS - is it for me?

> 板块: General Discussion

Hi, I love to play with different operating systems and I'm distro-hopper. I just can't stop myself from trying different operating systems. For right now I'm using NixOS.

I'm really interested about QubesOS and I love idea behind it, also I'm looking for challenges. But I'm not sure is it for my use case. 

I'm doing a lot of stuff on my computer - programming, system administration, watching videos, internet browsing, music production, gaming (open source games and I can live without them, I don't playing games too much), writing documents and I still try new things. But I also need security and privacy so I sometimes need to boot into TailsOS from my pendrive. It will be cool for me to have really secure and private workstation like QubesOS.

Of course QubesOS have some cons. It need a lot of resources, but I have good, modern PC with AMD Ryzen 7 7700 and 32 GB DDR5 6400MHz RAM on ASRock B650M motherboard. When I was using Gentoo I was able to compile software and doing my work or playing video game at the same time. Performance shouldn't be problem for me. One thing which I hate about my hardware is that I don't have motherboard open source firmware which can be huge security problem.

Also as I heard QubesOS don't using GPU acceleration by default. I have Nvidia RTX 4060 Ti but I'll changing it soon for something from AMD because of terrible support for Linux. I was always doing all my stuff requiring GPU in KVM with GPU Passthrough.

From what I've seen on this forum GPU Passthrough on Xen is possible so as I have integrated GPU I can use it. But configuration like this is usable for stuff like gaming, blender, AI etc. ? People are saying that this is hard to make it work, it's really like that? There are sources on forum how to do this step by step so it shouldn't be that bad. And [in this thread](https://forum.qubes-os.org/t/create-a-gaming-hvm/19000) which is about GPU Passthrough there's info that there's need to have additional keyboard or mouse if we're not planning to use VirtualGL. When I was using my KVM I was just pressing shortcut which was just switching my mouse and keyboard input between machine and VM with evdev - is it possible with XEN too? I don't have any other keyboard than this one which I'm using currently so I can at least just switch usb port physically or something to use it in VM?

And how about audio production? Any of you have experience with that on QubesOS? I'm not doing music professionally and I would like to try it.

Thank you in advance for your answers and suggestions!

---

## Light video editor for qubes?

> 板块: General Discussion

Before trying a bunch of video editors, has anyone here found one that works well despite the lack of gpu acceleration? I'm on a laptop without a dgpu, so pass through is not an option. This mostly resizing and cut / paste of screen recordings and cell phone videos. Nothing fancy.

---

## Question about my sys-net-monitor configuration

> 板块: General Discussion

Hey! First post, but have been lurking and troubleshooting here for close to a year now..

Anyway, I had this idea to create an network attached appvm that monitors network traffic using programs like Etherape and Wireshark but also doubles as a system wide VPN tunnel...

I created a sys-net-mon from a kicksecure template, installed Etherape, Wireshark, NorskVPN GUI and UFW. I set UFW to deny all inbound by default, and I'm not sure if this is correct practice or not, but I also set IP-Tables rules such as drop all inbound and allow loopback and I used IP-Tables-Persistent and Net-Filter-Persistent to enable the rules..

Now heres my question.. I have sys-net-mon in-between sys-net and sys-firewall as my thought process was that I want to inspect all connections and packets across all qubes and tunnel all traffic through a system-wide VPN with TOR running on top. 

It works. It works great. But is it good practice? 

Is it wise to have an appvm connected directly to sys-net, or would it be smarter to put sys-net-mon on top of sys-firewall and monitor traffic on a per qube basis connecting qubes to sys-net-mon instead of sys-firewall...

I'm an intermediate user and am still getting used to the quirks and am no expert on networking or whatever, but i like the way my system is at the moment but fear I am putting my station at rist by having an appvm connected directly to sys-net and running sys-firewall off that..

But I tell ya.. When I fire up Etherape and see that one green line that expands and contracts with network activity from all qubes being tunneled is a great feeling.. I just hope I haven't put my entire system at risk by doing this....

Any input would be appreciated or suggestions for a better way and correct practice..

Cheers :)

---

## Field Report: Simultaneous Network Configurations

> 板块: General Discussion

I ran into an niche use case for my Qubes setup, didn't readily find any threads discussing my particular issue. Now that Ive resolved it, I can document the process for public memory

**Background**: I maintain a handful of IoT devices on a secondary VLAN, isolated from the main network on which my computer & other trusted devices operate. I strictly limit the WLAN internet connections that can be made from this VLAN via router firewall. I have two network interfaces: a USB WiFi adapter, and an ethernet adapter

**Problem:**

* I need to interface with these IoT devices over WiFi, for updates & day-to-day operation. 
* I must maintain access to WLAN internet from Qubes through my primary network over ethernet, while simultaneously connecting to IoT devices over the VLAN with WiFi
* I should be able to quickly boot up a program & interface with any particular IoT device
* At rest, my desktop should not establish or maintain a connection to the VLAN

**Solution**

1. Create a qube, from which you will run whatever programs you will need. I have one or two rather complex programs requiring persistent home & root, so I opted for a standalonevm. But a simpler setup could use a disposable or appvm. I named mine 'iot'
2. Clone sys-firewall. I renamed my clone 'sys-firewall-iot'. Under 'iot' settings, change the network vm to this new qube
3. Clone sys-net. I renamed my clone 'sys-net-iot'. Under 'sys-firewall-iot' settings, change the network vm to this new qube. You will also need to remove the default network adapter from Devices, or you will encounter an error as the qube attempts to attach a device already belonging to sys-net
4. Start the 'iot' qube. If you configured the prior steps properly, sys-firewall-iot and sys-net-iot should also start
5. You'll now need to attach your secondary network adapter to the new sys-net-iot qube, and set this to happen automatically upon qube boot. If it's a USB adapter like mine, this should be easily accessible through the sys-usb icon on your primary display's panel tray
6. Kill all three qubes (iot, sys-firewall-iot, sys-net-iot)
7. Optional: use qube firewall to limit network connections through this new interface. I have a small number of IPs, and will only be using SSH & SFTP, so I limited connections to only these protocols from the iot qube
8. Restart iot. Once again, sys-firewall-iot and sys-net-iot should start
9. Under your panel tray, you should see a new network manager icon. So long as your system has the necessary drivers to run this network controller, it should populate with network options. If using WiFi, select your network & save credentials
10. Optional: I did not want the IoT network config to run by default, so I disabled start on boot across all three qubes

**End Result:** by default, my system only connects to my main network via ethernet adapter through sys-net. But when I need to work on my IoT devices, I can launch the IoT cube: sys-net-iot automatically connects to my IoT VLAN, and I can begin work immediately. I maintain connection to my main network throughout, allowing me to assess other sites or cloud services if needed. When finished, I manually kill the three IoT cubes to disconnect from the network 

**Limitations:** A given network adapter cannot simultaneously be assigned to two qubes. In this example, I maintain primary internet access through an ethernet adapter on sys-net, and IoT WiFi connection through a separate USB dongle on sys-net-IoT. You will be unable to configure this with a single physical network interface. USB Wifi dongles can be picked up from your local retailer for pretty cheap

---

