#!/bin/python3
# -*- coding: utf8 -*-

#   MIT License

# Copyright (c) 2022 mehrdad
# Developed by mehrdad-mixtape https://github.com/mehrdad-mixtape/Pacman_Fetch

# Python Version 3.6 or higher
# Pacman_Fetch

__repo__ = "https://github.com/mehrdad-mixtape/Pacman_Fetch"
__version__ = "v0.0.5"

from typing import List
from time import sleep, time
from rich.console import Console
from random import shuffle, choice
import os, platform, subprocess, \
    re, sys, distro, psutil, GPUtil

# Blocks
F = "█"
E = "▒"
W = 29
H = 12

D = 0

BANNER = """┌─────────────────┐
               │  Pacmanfetch  │
               └─────────────────┘"""

# Colorful blocks
BW = f"[white]{F}[/white]"
BC = f"[cyan]{F}[/cyan]"
BY = f"[gold1]{F}[/gold1]"
BG = f"[chartreuse3]{F}[/chartreuse3]"
BR = f"[red]{F}[/red]"
BP = f"[purple]{F}[/purple]"
BO = f"[dark_orange]{F}[/dark_orange]"
BK = f"[black]{F}[/black]"

# Color list
colors: List[str] = [
    "[red]{}[/red]",
    "[purple]{}[/purple]",
    "[dark_orange]{}[/dark_orange]",
    "[chartreuse3]{}[/chartreuse3]",
    "[cyan]{}[/cyan]",
    "[hot_pink]{}[/hot_pink]",
    "[orange4]{}[/orange4]",
    "[dark_cyan]{}[/dark_cyan]",
    "[grey74]{}[/grey74]",
    "[slate_blue3]{}[/slate_blue3]",
    "[medium_violet_red]{}[/medium_violet_red]",
    "[gold1]{}[/gold1]",
    "[sea_green1]{}[/sea_green1]",
    "[white]{}[/white]",
]

color_buffer = """{}{}{}{}{}{}{}
               {}{}{}{}{}{}{}"""

# Random Block color list
block_colors = [BR, BP, BO, BG, BC]
shuffle(block_colors)
limit = len(block_colors) + 1

# CPU Brand:
AMD = '[bold][red]AMD[/red][/bold]:'
Intel = '[bold][cyan]Intel[/cyan][/bold]'

# System info
OS = '[bold][red]  OS[/red][/bold]:'
CPU = '[bold][dark_orange]  Cpu[/dark_orange][/bold]:'
GPU = '[bold][medium_violet_red]  Gpu[/bold][/medium_violet_red]:'
RAM = '[bold][slate_blue3]  Ram[/slate_blue3][/bold]:'
SWAP = '[bold][grey74]  Swap[/grey74][/bold]:'
DISK = '[bold][hot_pink]  Disk[/hot_pink][/bold]:'
KERNEL = '[bold][sea_green1]  Kernel[/sea_green1][/bold]:'
PING = "[bold][gold1]  Ping[/gold1][/bold]:"
NETWORK = "[bold][dark_cyan]  Network[/dark_cyan][/bold]:"
UPTIME = "[bold][orange4]  Uptime[/orange4][/bold]:"
NODE = "[bold] {}$ [yellow2] {}[/yellow2][red]@[/red][cyan]{}[/cyan][/bold]"

# Ghost: Width=29, Height=12
pacman = """
▒▒▒▒▒▒▒██████████████▒▒▒▒▒▒▒▒
▒▒▒▒▒███████████████████▒▒▒▒▒
▒▒▒███████████████████████▒▒▒
▒█████████████████████▒▒▒▒▒▒▒
██████████████████▒▒▒▒▒▒▒▒▒▒▒
████████████████▒▒▒▒▒▒▒▒  ▒
████████████████▒▒▒▒▒▒▒▒  ▒
██████████████████▒▒▒▒▒▒▒▒▒▒▒
▒█████████████████████▒▒▒▒▒▒▒
▒▒▒███████████████████████▒▒▒
▒▒▒▒▒███████████████████▒▒▒▒▒
▒▒▒▒▒▒▒▒█████████████▒▒▒▒▒▒▒▒
""".replace(F, BY)

# Ghost: Width=29, Height=12
ghost = """
▒▒▒▒▒▒▒██████████████▒▒▒▒▒▒▒▒
▒▒▒▒▒██████████████████▒▒▒▒▒▒
▒▒▒@@@@@@█████@@@@@@█████▒▒▒▒
▒██@@##@@█████@@##@@███████▒▒
▒██####@@█████####@@███████▒▒
▒██@@@@@@█████@@@@@@███████▒▒
▒██████████████████████████▒▒
▒██████████████████████████▒▒
▒██████████████████████████▒▒
▒██████████████████████████▒▒
▒████▒▒████▒▒▒▒▒▒████▒▒████▒▒
▒██▒▒▒▒▒▒██▒▒▒▒▒▒██▒▒▒▒▒▒██▒▒
"""

# Ping:
cmd = 'ping {} 1 8.8.8.8'
if platform.system() == "Windows":
    cmd.format('-n')
elif platform.system() in "Linux Darwin":
    cmd.format('-c')
ping_proc = subprocess.Popen(
    cmd.format('-c'),
    shell=True,
    stdout=subprocess.PIPE
)

def clear() -> None:
    if platform.system() in "Linux Darwin":
        subprocess.run(['clear'])
    elif platform.system() in "Windows":
        subprocess.run(['cls'])
    else: pass

def cpu() -> str:
    cpu_info = ""
    if platform.system() == "Windows":
        cpu_info = f"{CPU}{platform.processor()}"

    elif platform.system() == "Darwin":
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        cmd ="sysctl -n machdep.cpu.brand_string"
        cpu_info = f"{CPU}{subprocess.check_output(cmd).strip()}"

    elif platform.system() == "Linux":
        cmd = "cat /proc/cpuinfo"
        all_info = subprocess.check_output(cmd, shell=True).decode().strip()
        for line in all_info.split("\n"):
            if "model name" in line:
                cpu_info = f"{CPU}{''.join(re.sub(r'.*model name.*:', '', line, 1))}".replace('CPU @ ', '')
                break
    else:
        cpu_info = f"{CPU} None!"

    return cpu_info + f" {psutil.cpu_count()} Cores"

def ram() -> str:
    mem = psutil.virtual_memory()
    usage = round(mem.percent)
    used = round(mem.used / (1024 ** 3), 1)
    total = round(mem.total / (1024 ** 3), 1)
    return f"{RAM} {used} GB  {total} GB usage: {usage}%"

def swap() -> str:
    swap = psutil.swap_memory()
    usage = round(swap.percent)
    used = round(swap.used / (1024 ** 3), 1)
    total = round(swap.total / (1024 ** 3), 1)
    return f"{SWAP} {used} GB  {total} GB usage: {usage}%"

def disk() -> str:
    home = psutil.disk_usage('/home')
    home_total = round(home.total / (1024 ** 3), 1)
    home_free = round(home.free / (1024 ** 3), 1)

    root = psutil.disk_usage('/')
    root_total = round(root.total / (1024 ** 3), 1)
    root_free = round(root.free / (1024 ** 3), 1)
    
    return f"{DISK} Root({root_total} GB) free: {root_free} GB │ Home({home_total} GB) free: {home_free} GB"

def ping() -> str:
    stdout = ''.join(line.decode('utf-8') for line in ping_proc.stdout)
    time = re.findall(r'time=.*ms', stdout)[0].replace('time=', '')
    return f"{PING} {time}  8.8.8.8"

def network() -> str:
    if_addrs = psutil.net_if_addrs()
    iface_addrs: List[str] = []
    for interface_name, interface_addresses in if_addrs.items():
        if interface_name.startswith(('w', 'e')):
            for address in interface_addresses:
                if address.family.name == 'AF_INET': # AF_INET = IPv4, AF_INET6 = IPv6
                    iface_addrs.append(f"{interface_name}  {address.address}")

    iface_buffer = "{} " * len(iface_addrs)
    iface_buffer = iface_buffer.format(*iface_addrs).strip()
    return f"{NETWORK} {iface_buffer}"

def gpu() -> str:
    gpus = GPUtil.getGPUs()
    if not gpus:
        return f"{GPU} None!"
    else:
        gpu_buffer = "{} " * len(gpus)
        gpu_buffer = gpu_buffer.format(*[g.name for g in gpus]).strip()
        return f"{GPU} {gpu_buffer}"

def oper() -> str:
    return f"{OS} {distro.id().title()} {distro.version()}"

def kernel() -> str:
    return f"{KERNEL} {platform.release()}"

def node() -> str:
    global D
    shell = subprocess.check_output(
        'echo $SHELL',
        shell=True
    ).decode('utf-8').split('/')[-1].strip()
    if platform.system() in "Linux Darwin":
        user = os.environ.get('USER')
        host = platform.node()
        D = len(shell) + len(user) + len(host)
        return NODE.format(shell, user, host)
    elif platform.system() == 'Windows':
        user = os.environ.get('USERNAME')
        host = platform.node()
        D = len(user) + len(host)
        return NODE.format(user, host)

def uptime() -> str:
    system_up = round(time() - psutil.boot_time())
    hours = system_up // 60 // 60
    minutes = system_up // 60 % 60
    seconds = system_up % 60
    return f"{UPTIME} {hours}:{minutes}:{seconds}"

def main(arg: List[str]) -> None:
    console = Console()
    max_width = os.get_terminal_size().columns // 29 # 29 = width of ghost
    max_ghost =  limit if max_width > limit else max_width # how many ghost can place on terminal

    clear()

    # Draw pacman and ghosts
    ghost_buffer = "{}" * max_ghost 
    for n in range(H + 1):
        console.print(ghost_buffer.format(
            pacman.split('\n')[n].replace('▒', ' '),
                *(
                    ghost.split('\n')[n] \
                        .replace('▒', ' ') \
                        .replace(F, block_colors[i]) \
                        .replace('@', BW) \
                        .replace('#', BK) \
                        for i in range(max_ghost - 1)
                ),
            )
        )
        # Argument management
        if len(arg) == 1:
            sleep(0.01)
        elif len(arg) == 2:
            if arg[1].isdigit():
                sleep(int(arg[1]) / 1000)
            else:
                sleep(0.01)
        else:
            sleep(0.01)

    # Show system info
    console.print(
        f"""[white]
            {node()}
            {'─' * D}───────
            {oper()}
            {kernel()}
            {cpu()}
            {gpu()}
            {ram()}
            {swap()}
            {disk()}
            {ping()}
            {network()}
            {uptime()}
            {'─' * D}───────
              {color_buffer.format(*[color.format(F * 3) for color in colors])}
               {choice(colors).format(BANNER)}
        [/white]"""
    )

if __name__ == '__main__':
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        sys.exit()
