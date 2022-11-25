#!/bin/python3.8
# -*- coding: utf8 -*-

# MIT License

# Copyright (c) 2022 mehrdad
# Developed by mehrdad-mixtape https://github.com/mehrdad-mixtape/Pacman_Fetch

# Python Version 3.6 or higher
# Pacman_Fetch

__repo__ = "https://github.com/mehrdad-mixtape/Pacman_Fetch"
__version__ = "v0.4.9"

""" Pacman Fetch!
For Better Experience Install icon-in-terminal:
Github repo: https://github.com/sebastiencs/icons-in-terminal """

from typing import List, Dict, Generator
from time import sleep, time
from rich.console import Console
from random import shuffle, choice
from argparse import ArgumentParser
import os, platform, subprocess, \
    re, sys, distro, psutil

# Blocks
# -------------------------------------------------------------------
F = "█"
E = "▒"

# Height and Width of Pacman & Ghost
# -------------------------------------------------------------------
W = 29
H = 12

# length of separator
# -------------------------------------------------------------------
D = 0

MAIN_BANNER = """[blink]┌───────────────────┐
           │   Pacmanfetch   │
           └───────────────────┘[/blink]"""

# Color list
# -------------------------------------------------------------------
colors: List[str] = [
    "[red]{}[/red]", #0
    "[purple]{}[/purple]", #1
    "[dark_orange]{}[/dark_orange]", #2
    "[chartreuse3]{}[/chartreuse3]", #3
    "[cyan]{}[/cyan]", #4
    "[hot_pink]{}[/hot_pink]", #5
    "[orange4]{}[/orange4]", #6
    "[dark_cyan]{}[/dark_cyan]", #7
    "[grey74]{}[/grey74]", #8
    "[slate_blue3]{}[/slate_blue3]", #9
    "[medium_violet_red]{}[/medium_violet_red]", #10
    "[gold1]{}[/gold1]", #11
    "[sea_green1]{}[/sea_green1]", #12
    "[white]{}[/white]", #13
    "[black]{}[/black]", #14
]

# Colorful blocks
# -------------------------------------------------------------------
BW = colors[13].format(F)
BC = colors[4].format(F)
BY = colors[11].format(F)
BG = colors[3].format(F)
BR = colors[0].format(F)
BP = colors[1].format(F)
BO = colors[2].format(F)
BK = colors[14].format(F)

COLOR_BANNER = """{}{}{}{}{}{}{}
           {}{}{}{}{}{}{}"""

# OS logos
# -------------------------------------------------------------------
OS_name = distro.id()
OS_logos = {
    # It is not compatible for all os, because of icon-fonts.
    'nix': ' ',
    'ubuntu': ' ',
    'debian': ' ',
    'raspbian': ' ',
    'elementary': ' ',
    'mint': ' ',
    'centos': ' ',
    'fedora': ' ',
    'redhat': ' ',
    'arch': ' ',
    'manjaro': ' ',
    'suse': ' ',
    'slackware': ' ',
    'alpine': '',
    'bsd': ' ',
    'gentoo': ' ',
    'darwin': ' ',
    'macos': ' ',
    'mac': ' ',
    'windows': ' ',
}

# Random Block color list
# -------------------------------------------------------------------
block_colors = [BR, BP, BO, BG, BC]
shuffle(block_colors)
limit = len(block_colors) + 1

# CPU Brand:
# -------------------------------------------------------------------
AMD = '[red]AMD[/red]:'
Intel = '[blue]Intel[/blue]'

# System info
# -------------------------------------------------------------------
system_info_colors = [
    'red', 'sea_green1', 'dark_orange', 'medium_violet_red', 'slate_blue3',
    'grey74', 'hot_pink', 'gold1', 'dark_cyan', 'orange4', 'orange4', 
]

system_info_title = [
    f"        {OS_logos.get(OS_name, ' ')} OS:",
    '          Kernel:',
    '          Cpu:',
    '          Gpu:',
    '          Ram:',
    '          Swap:',
    '          Disk:',
    '          Network:',
    '          Ping:',
    '          Uptime:',
]

NODE = "[white]  {}$ [/white][yellow2] {}[/yellow2][red]@[/red][cyan]{}[/cyan]"

# IP addresses
# -------------------------------------------------------------------
iface_addrs: List[str] = []

# Ghost: Width=29, Height=12
# -------------------------------------------------------------------
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
# -------------------------------------------------------------------
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

def clear() -> None:
    if platform.system() in "Linux Darwin":
        subprocess.run(['clear'])
    elif platform.system() in "Windows":
        subprocess.run(['cls'])
    else: pass

def cpu() -> str:
    cpu_info = " Platform unsupported!"
    if platform.system() == 'Linux':
        cmd = 'cat /proc/cpuinfo'
        all_info = subprocess.check_output(cmd, shell=True).decode().strip()
        for line in all_info.split('\n'):
            if 'model name' in line:
                cpu_info = ''.join(re.sub(r".*model name.*:", '', line)).replace('CPU @ ', '').strip()
                break
            elif 'Hardware' in line:
                cpu_info = ''.join(re.sub(r"(.*Hardware.*:)|(\(.*\))", '', line)).strip()
                break

    elif platform.system() == 'Darwin':
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        cmd ='sysctl -n machdep.cpu.brand_string'
        cpu_info = subprocess.check_output(cmd).strip()

    elif platform.system() == 'Windows':
        cpu_info = platform.processor().strip()

    return f" {cpu_info} {psutil.cpu_count()} Cores"

def ram() -> str:
    mem = psutil.virtual_memory()
    usage = round(mem.percent)
    used = round(mem.used / (1024 ** 3), 1)
    total = round(mem.total / (1024 ** 3), 1)
    return f" {used} GB  {total} GB usage: {usage}%"

def swap() -> str:
    swap = psutil.swap_memory()
    usage = round(swap.percent)
    used = round(swap.used / (1024 ** 3), 1)
    total = round(swap.total / (1024 ** 3), 1)
    return f" {used} GB  {total} GB usage: {usage}%"

def disk() -> str:
    home = psutil.disk_usage('/home')
    home_total = round(home.total / (1024 ** 3), 1)
    home_free = round(home.free / (1024 ** 3), 1)

    root = psutil.disk_usage('/')
    root_total = round(root.total / (1024 ** 3), 1)
    root_free = round(root.free / (1024 ** 3), 1)
    
    return f" Root({root_total} GB) free: {root_free} GB │ Home({home_total} GB) free: {home_free} GB"

def ping() -> str:
    cmd = 'ping {} 1 8.8.8.8'
    if platform.system() == "Windows":
        cmd = cmd.format('-n')
    elif platform.system() in "Linux Darwin":
        cmd = cmd.format('-c')
    try:
        if not iface_addrs:
            return f" 999ms   8.8.8.8"
        else:
            ping_proc = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE
            )
            stdout = ''.join(line.decode('utf-8') for line in ping_proc.stdout)
            time = re.findall(r"time=.*ms", stdout)[0].replace('time=', '')
            return f" {time}   8.8.8.8"
    except Exception:
        return f" 999ms   8.8.8.8"

def network() -> str:
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        if interface_name.startswith(('w', 'e', 'u', 't')):
            for address in interface_addresses:
                if address.family.name == 'AF_INET': # AF_INET = IPv4, AF_INET6 = IPv6
                    iface_addrs.append(f"{interface_name}   {address.address} │")

    if not iface_addrs:
        return ' Check your   Connections'
    else:
        iface_buffer = "{} " * len(iface_addrs)
        iface_buffer = iface_buffer.format(*iface_addrs).strip(' │')
        return f" {iface_buffer}"

def gpu() -> str:
    gpu_info = ''
    def finder(brand: Dict[str, List[str]]) -> Generator[str, None, None]:
        patterns = {
            'AMD': r"\[.*\].*\[.*\]",
            'Intel': r"(U?HD Graphics [0-9]*?$)|(Iris Xe Graphics.*)",
            'NVIDIA': r"\[.*\]"
        }
        for name, gpus in brand.items():
            for gpu in gpus:
                try:
                    temp = re.search(patterns.get(name, r".*"), gpu)\
                        .group().replace('[', '').replace(']', '')
                except Exception:
                    yield ""
                else:
                    yield f"{name} {temp} │ "

    # TODO: test gpu info for other os and hardwares.
    # This is Beta!
    if platform.system() == 'Linux':
        stdout = subprocess.run(
            'lspci',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        ).stdout.decode('utf-8')
        amd: Dict[str, List[str]] = {'AMD': [
            *re.findall(r"VGA.*(AMD.*) \(.*", stdout),
            *re.findall(r"3D.*(AMD.*) \(.*", stdout),
        ]}
        intel: Dict[str, List[str]] = {'Intel': [
            *re.findall(r"VGA.*(Intel.*) \(.*", stdout),
            *re.findall(r"3D.*(Intel.*) \(.*", stdout),
        ]}
        nvidia: Dict[str, List[str]] = {'NVIDIA': [
            *re.findall(r"VGA.*(NVIDIA.*) \(.*", stdout),
            *re.findall(r"3D.*(NVIDIA.*) \(.*", stdout),
        ]}

        for brand in [amd, intel, nvidia]:
            for gpu in finder(brand):
                gpu_info += gpu
        
        if not gpu_info:
            gpu_info = 'Can\'t find Gpu'
        else:
            gpu_info = gpu_info.strip('│ ')

    elif platform.system() == 'Darwin':
        gpu_info = 'Can\'t find Gpu and Not implemented'
        ... # system_profiler SPDisplaysDataType

    elif platform.system() == 'Windows':
        gpu_info = 'Can\'t find Gpu and Not implemented'
        ... # wmic path Win32_VideoController get caption
    
    else:
        gpu_info = 'Platform unsupported!'

    return f" {gpu_info}"

def operate() -> str:
    return f" {OS_name.title()} {distro.version()}"

def kernel() -> str:
    return f" {platform.release()}"

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
        return NODE.format(':\>', user, host)

def uptime() -> str:
    system_up = round(time() - psutil.boot_time())
    hours = system_up // 60 // 60
    minutes = system_up // 60 % 60
    seconds = system_up % 60
    return f" {hours}h {minutes}m {seconds}s"

def main() -> None:
    clear()
    delay = 0
    console = Console()
    max_width = os.get_terminal_size().columns // (29) # 29 = width of ghost
    max_ghost = limit if max_width >= limit else max_width # How many ghost can place on terminal

    # Argument parsing
    # -------------------------------------------------------------------
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', help="show version", action='store_false', required=False)
    parser.add_argument('-d', '--delay', help="typewriter style show itself if you set delay <ms>", type=int, required=False)
    args = parser.parse_args()
    
    if args.delay:
        delay = args.delay
    elif not args.version:
        console.print(f"""
           {choice(colors).format(MAIN_BANNER)}
           Version: {__version__}
           Source: {__repo__}
        """)
        sys.exit()

    # Draw pacman & ghosts
    # -------------------------------------------------------------------
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
        sleep(delay / 1000)

    # Draw system info
    # -------------------------------------------------------------------
    system_info_details: List[str] = [
        operate(), kernel(), cpu(),
        gpu(), ram(), swap(), disk(),
        network(), ping(), uptime()
    ]

    console.print(f"""
        {node()}
        {'─' * D}────────""")
    for color in system_info_colors:
        try:
            details = system_info_details.pop(0)
            title = system_info_title.pop(0)
        except IndexError: break
        else:
            for char in title: # Type titles with color
                console.print(f"[{color}]{char}[/{color}]", end='')
                sleep(delay / 1000)
            for char in details: # Type details without color
                console.print(f"{char}", end='')
                sleep(delay / 1000)
            print()
    console.print(f"""        {'─' * D}────────
          {COLOR_BANNER.format(*[color.format(F * 3) for color in colors])}
           {choice(colors).format(MAIN_BANNER)}""")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
