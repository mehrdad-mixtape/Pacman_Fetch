#!/bin/python3
# -*- coding: utf8 -*-

# MIT License

# Copyright (c) 2022 mehrdad
# Developed by mehrdad-mixtape https://github.com/mehrdad-mixtape/Pacman_Fetch

# Python Version 3.6 or higher
# Pacman_Fetch

ALPHA = "[purple]alpha[/purple]"
BETA = "[red]beta[/red]"
STABLE = "[green]stable[/green]"

__repo__ = "https://github.com/mehrdad-mixtape/Pacman_Fetch"
__version__ = f"v0.6.0-{BETA}"

""" Pacman Fetch!
For Better Experience Install icon-in-terminal:
Github repo: https://github.com/sebastiencs/icons-in-terminal """

from typing import Tuple, List, Dict, \
    Generator, Callable, Any
from time import sleep, time
from rich.console import Console
from rich.table import Table
from rich import pretty, traceback
pretty.install()
traceback.install()
from random import shuffle, choice
import os, platform, subprocess, \
    re, sys, distro, psutil

# Decorators
# --------------------------------------------------------------------
def exception_handler(*exceptions, cause: str=UNSUPPORTED_BANNER, do_this=sys.exit) -> Callable[[Any], Any]:
    def __decorator__(func: Callable) -> Callable[[Any], Any]:
        def __wrapper__(*args, **kwargs) -> Any:
            try:
                results = func(*args, **kwargs)
            except exceptions:
                clear()
                pprint("---===❰ [blink]  [italic][gold1]Pacmanfetch[/gold1][/italic]   [/blink] ❱===---")
                pprint(f"[*] {ERROR}. {cause}")
                do_this()
            else:
                return results
        return __wrapper__
    return __decorator__

# Classes
# --------------------------------------------------------------------
class Options:
    __slots__ = "__option_list", "__option_method"
    def __init__(self):
        self.__option_list: List[str] = []
        self.__option_method: Dict[str, Tuple[Callable, bool, int]] = {}

    def __str__(self):
        table = Table()
        table.add_column('Switches')
        table.add_column('Methods')
        for switch, method in self.option_method.items():
            table.add_row(switch, method.__name__)
        pprint(table)
        return '\r'

    def __call__(
            self, *switches: str,
            has_input: bool=False,
            type_of_input: type=None
        ):
        """
            switches: start with - or --.
            has_input: maybe the switches include the argument after them.
            type_of_input: hint the type_of_input that become after switch
        """
        self.__option_list.extend(switches)
        def __decorator__(func: Callable) -> Callable[[None], None]:
            for sw in switches:
                self[sw] = (func, has_input, type_of_input)
        return __decorator__

    def __setitem__(self, attr, value) -> None:
        self.__option_method[attr] = value

    def __getitem__(self, attr) -> Any:
        return self.__option_method[attr]

    def manage(self) -> Generator[Any, None, None]:
        for i, sw in enumerate(sys.argv): # sys.argv converted to set to remove the duplicate switches
            if not sw.startswith(('-', '--')): continue # valid switches can start with - --
            func, has_input, type_of_input= self.option_method[sw] # func is __wrapper__ in __call__ that defined in Options class
            # if switch has input, I should pass the location of input to func, if it hasn't, it will be handle in __wrapper__ with has_input
            # eval(f"{func}({i + 1})")
            if not has_input:
                yield func()
            else:
                arg_input = sys.argv[i + 1].__str__()
                goodbye(
                    type_of_input is None,
                    cause=f"Get type-of-arguments=({arg_input}) after {sw}",
                    silent=True
                )
                try:
                    arg_input = type_of_input(arg_input)
                except ValueError:
                    goodbye(
                        True,
                        cause=f"Gave bad-argument=({arg_input}) after {sw}",
                        silent=True
                    )
                yield func(arg_input)

    @property
    def option_list(self) -> List[str]:
        return self.__option_list

    @property
    def option_method(self) -> Dict[str, str]:
        return self.__option_method

# Options
# -------------------------------------------------------------------
option = Options()

@option('-v', '--version')
def do_you_wanna_see_version() -> None:
    pprint(
    f"""
    ---===❰ [blink]  [italic][gold1]Pacmanfetch[/gold1][/italic]   [/blink] ❱===---
    Version: {__version__}
    Source: {__repo__}
    """
    )
    sys.exit()

@option('-d', '--delay', has_input=True, type_of_input=int)
def do_you_wanna_typewriter_style(speed: int) -> None:
    global delay
    delay = speed

@option('-h', '--help')
def do_you_wanna_help() -> None:
    pprint(HELP)
    sys.exit()

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
    'nixos': ' ', 'ubuntu': ' ', 'debian': ' ',
    'raspbian': ' ', 'elementary': ' ', 'mint': ' ',
    'centos': ' ', 'fedora': ' ', 'redhat': ' ',
    'arch': ' ', 'manjaro': ' ', 'suse': ' ',
    'slackware': ' ', 'alpine': ' ', 'bsd': ' ',
    'gentoo': ' ', 'darwin': ' ', 'macos': ' ',
    'mac': ' ', 'windows': ' ',
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
    f"       │ {OS_logos.get(OS_name, ' ')} OS:",
    '       │   Kernel:',
    '       │   Cpu:',
    '       │   Gpu:',
    '       │   Ram:',
    '       │   Swap:',
    '       │   Disk:',
    '       │   Network:',
    '       │   Ping:',
    '       │   Uptime:',
]

NODE = "[white]  {}$ [/white][yellow2] {}[/yellow2][red]@[/red][cyan]{}[/cyan]"

# IP addresses
# -------------------------------------------------------------------
iface_addrs: List[str] = []

# Pacman: Width=29, Height=12
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

def cpu() -> str:
    cpu_info = ''
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
    
    else:
        cpu_info = UNSUPPORTED_BANNER

    return f" {cpu_info} {psutil.cpu_count()} Cores"

@exception_handler(RuntimeWarning, PermissionError, OSError)
def ram() -> str:
    mem = psutil.virtual_memory()
    usage = round(mem.percent)
    used = round(mem.used / (1024 ** 3), 1)
    total = round(mem.total / (1024 ** 3), 1)
    return f" {used} GB  {total} GB usage: {usage}%"

@exception_handler(RuntimeWarning, PermissionError, OSError)
def swap() -> str:
    swap = psutil.swap_memory()
    usage = round(swap.percent)
    used = round(swap.used / (1024 ** 3), 1)
    total = round(swap.total / (1024 ** 3), 1)
    return f" {used} GB  {total} GB usage: {usage}%"

@exception_handler(RuntimeWarning, PermissionError, OSError)
def disk() -> str:
    home = psutil.disk_usage('/home')
    home_total = round(home.total / (1024 ** 3), 1)
    home_free = round(home.free / (1024 ** 3), 1)

    root = psutil.disk_usage('/')
    root_total = round(root.total / (1024 ** 3), 1)
    root_free = round(root.free / (1024 ** 3), 1)
    
    return f" Root({root_total} GB) free: {root_free} GB │ Home({home_total} GB) free: {home_free} GB"

async def ping() -> str:
    cmd = 'ping {} 1 8.8.8.8'
    if platform.system() == "Windows":
        cmd = cmd.format('-n')
    elif platform.system() in "Linux Darwin":
        cmd = cmd.format('-c')
    try:
        if not iface_addrs:
            return ' 999ms   8.8.8.8'
        else:
            with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE) as ping_proc:
                stdout = ''.join(line.decode('utf-8') for line in ping_proc.stdout)
                time = re.findall(r"time=.*ms", stdout)[0].replace('time=', '')
                return f" {time}   8.8.8.8"
    except Exception:
        return ' 999ms   8.8.8.8'

@exception_handler(RuntimeWarning, PermissionError, OSError)
def network() -> str:
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        if interface_name.startswith(('w', 'e', 'u', 't')):
            for address in interface_addresses:
                if address.family.name == 'AF_INET': # AF_INET = IPv4, AF_INET6 = IPv6
                    if interface_name.startswith(('t')):
                        iface_addrs.append(f"VPN is Connected │")
                    else:
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
            gpu_info = 'Platform unsupported'
        else:
            gpu_info = gpu_info.strip('│ ')

    elif platform.system() == 'Darwin':
        gpu_info = 'Not implemented'
        ... # system_profiler SPDisplaysDataType

    elif platform.system() == 'Windows':
        gpu_info = 'Not implemented'
        ... # wmic path Win32_VideoController get caption
    
    else:
        gpu_info = UNSUPPORTED_BANNER

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
        pprint(ghost_buffer.format(
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
        [italic]{node()}[/italic]
        {'─' * D}────────""")
    for color in system_info_colors:
        try:
            details = system_info_details.pop(0)
            title = system_info_title.pop(0)
        except IndexError:
            break
        else:
            for char in title: # Type titles with color
                pprint(f"[italic][{color}]{char}[/{color}][/italic]", end='')
                sleep(delay / 1000)
            for char in details: # Type details without color
                pprint(f"{char}", end='')
                sleep(delay / 1000)
            print()
    pprint(f"""        {'─' * D}────────
          {COLOR_BANNER.format(*[color.format(F * 3) for color in colors])}
           {choice(colors).format(MAIN_BANNER)}""")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
