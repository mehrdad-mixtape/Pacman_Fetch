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
__version__ = f"v0.8.2-{BETA}"

""" Pacman Fetch!
For Better Experience Install icon-in-terminal:
Github repo: https://github.com/sebastiencs/icons-in-terminal """

import os, subprocess, re, sys, json, random
from typing import Tuple, List, Dict, Generator, Callable, Any
from time import sleep, time

try:
    import psutil, distro
    from rich.console import Console
    from rich.table import Table
    from rich import pretty, traceback
    from threading import Thread

except ImportError as E:
    print(f"[*] Error. {E} - Please Install the Pkgs.")
    sys.exit()

else:
    pretty.install()
    traceback.install()

#TODO: Improve Option, "pacmanfetch -pi -v -d 10" != "pacmanfetch -d 10 -pi -v"

# Banners
# -------------------------------------------------------------------
MAIN_BANNER = """[bold][blink]┌───────────────────┐
           │   Pacmanfetch   │
           └───────────────────┘[/blink][/bold]"""

HELP = f"""
Intro:
    Fetch your system!
    ---===❰ [blink]  [gold1]Pacmanfetch[/gold1]   [/blink] ❱===---

Helps:
    [bold][red]-d --delay[/red][/bold]: Get delay to show you typewriter style
        $ pacmanfetch -d 10
    [bold][cyan]-p --pacman[/cyan][/bold]: Show you big pacman
        $ pacmanfetch -p
    [bold][green]-v --version[/green][/bold]: Show you version
        $ pacmanfetch -v
    [bold][gold1]-i --ping[/gold1][/bold]: Enable or Disable ping
        $ pacmanfetch -i
    [bold][medium_violet_red]-c --config[/medium_violet_red][/bold]: Use config file
        $ pacmanfetch -c
    [bold][orange4]-h --help[/orange4][/bold]: Show help
        $ pacmanfetch -h
"""

# Functions
# ---------------------------------------------------------------------
pprint = lambda *args, **kwargs: Console().print(*args, **kwargs)

def clear() -> None:
    print('\033c', end='')


def goodbye(expression: bool, cause: str='Unknown'):
    if expression:
        pprint(f"[{ERROR}]. {cause}")
        sys.exit()

# Decorators
# --------------------------------------------------------------------
def exception_handler(*exceptions, cause: str='', do_this: Callable=sys.exit) -> Callable[[Any], Any]:
    def __decorator__(func: Callable) -> Callable[[Any], Any]:
        def __wrapper__(*args, **kwargs) -> Any:
            try:
                results = func(*args, **kwargs)
            except exceptions as err:
                if cause:
                    pprint(f"\n[{ERROR}]. {cause}")
                else:
                    pprint(f"\n[{ERROR}]. {err}")
                do_this()
            else:
                return results
        return __wrapper__
    return __decorator__


def threader(daemon: bool=False) -> Callable[[Callable], Any]:
    def __decorator__(func: Callable) -> Callable[[Any], Any]:
        def __wrapper__(*args, **kwargs) -> None:
            thread = Thread(
                target=func,
                args=args,
                kwargs=kwargs,
                daemon=daemon
            )
            thread.start()
            if daemon:
                threads.append(thread)
            else:
                threads.append(thread)
                thread.join()
        return __wrapper__
    return __decorator__

# Classes
# --------------------------------------------------------------------
class Options:
    """
    Argument Parser!
    
    1. Make option object:
    
        option = Option()
    
    2. Assign function to option object:
    
        - Decorate function with option object
    
            @option('-s')

            def do_you_wanna_something_to_do():
                ...
            
            @option('--switch')

            def do_you_wanna_something_to_do():
                ...
            
            @option('-s', '--switch')

            def do_you_wanna_something_to_do():
                ...
            
            @option('-s', '--switch', has_input=True, type_of_input=type)

            def do_you_wanna_something_to_do(arg: type):
                ...
    
        - Directly

            option['- or -- switch'] = (function, has_input(True or False), type_of_input=(str, int, ...))

            option['-s'] = (do_you_wanna_something_to_do)
            
            option['-s'] = (do_you_wanna_something_to_do, True, type)

            option['--switch'] = (do_you_wanna_something_to_do)
            
            option['--switch'] = (do_you_wanna_something_to_do, True, type)
    """

    __slots__ = "__option_list", "__option_method"

    def __init__(self):
        self.__option_list: List[str] = []
        self.__option_method: Dict[str, Tuple[Callable[[Any], Any], bool, type]] = {}


    def __str__(self):
        table = Table()
        table.add_column('Switches')
        table.add_column('Methods')
        for switch, method in self.option_method.items():
            table.add_row(switch, method[0].__name__)
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
            type_of_input: type of arguments after switch and depends on has_input.
        """
        def __decorator__(func: Callable[[Any], Any]) -> Callable[[None], None]:
            for sw in switches:
                goodbye(
                    sw in self.__option_method.keys(),
                    cause="Duplicate switch={0}, [bold]{1}[/bold] used for [bold]{2}[/bold]".format(
                        sw, sw, self.__option_method.get(sw, (print,))[0].__name__
                    )
                )
                self.__option_method[sw] = (func, has_input, type_of_input)

            self.__option_list.extend(switches)

        return __decorator__


    def __setitem__(self, key: str, value: tuple) -> None:
        goodbye(
            not ((not isinstance(value, tuple) or value.__len__() < 3) and callable(value[0])),
            cause="""Bad value format.\nValid format:
        option_obj['-s' or '--switch' or '-s --switch'] = (
            function, # Should be Callable.
            True or False, # If your function should get argument, set it True or not False.
            type, # Set type of argument that will pass to function (str, int, ...).
        )""",
        )
        self.__option_method[key] = value


    def __getitem__(self, key: str) -> Any:
        return self.__option_method.get(key, None)

    def parse(self) -> Generator[Any, None, None]:
        for i, sw in enumerate(sys.argv, start=1):
            # goodbye(sw.startswith(('+', '=', '/', '\\', '$', '#', '>', '<', '@', '!', '`', '~')))

            if not sw.startswith(('-', '--')):
                continue # valid switches can start with - --            
            
            # Handle the complete-switches: Example ==> --add --list --dump
            if '--' in sw:
                yield self.__switch_executer(sw, i)
                continue
            
            # Handle the abbreviation-switches: Example ==> -a -l -d
            # Handle the mixed abbreviation-switches: Example ==> -ald = -dal
            for chr in sw:
                goodbye( # if user enter just -
                    sw.__len__() == 1,
                    cause=f"Invalid Switch=({sw})"
                )
                if chr == '-': continue
                e_sw = f"-{chr}" # esw = extracted_switch
                yield self.__switch_executer(e_sw, i)


    def __switch_executer(self, switch: str, switch_index: int) -> None:
        try:
            func, has_input, type_of_input = self.option_method[switch]
            # func is __wrapper__ in __call__ that defined in Options class
            # if switch has input, I should pass the location of input to func
            # if it hasn't, it will be handle in __wrapper__ with has_input
        except KeyError:
            goodbye(True, cause=f"Invalid Switch=({switch})")
        # eval(f"{func}({i + 1})")
        if not has_input:
            return func()
        else:
            arg_input = sys.argv[switch_index].__str__()
            goodbye(
                type_of_input is None,
                cause=f"Get type-of-arguments=({arg_input}) after [bold]{switch}[/bold]",
            )
            try:
                arg_input = type_of_input(arg_input)
            except ValueError:
                goodbye(
                    True,
                    cause=f"Gave bad-argument=({arg_input}) after [bold]{switch}[/bold]",
                )
            return func(arg_input)


    @property
    def option_list(self) -> List[str]:
        return self.__option_list


    @property
    def option_method(self) -> Dict[str, str]:
        return self.__option_method

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
colors: Tuple[str] = (
    "[red]{}[/red]",                                #0
    "[purple]{}[/purple]",                          #1
    "[dark_orange]{}[/dark_orange]",                #2
    "[chartreuse3]{}[/chartreuse3]",                #3
    "[cyan]{}[/cyan]",                              #4
    "[hot_pink]{}[/hot_pink]",                      #5
    "[orange4]{}[/orange4]",                        #6
    "[dark_cyan]{}[/dark_cyan]",                    #7
    "[grey74]{}[/grey74]",                          #8
    "[slate_blue3]{}[/slate_blue3]",                #9
    "[medium_violet_red]{}[/medium_violet_red]",    #10
    "[gold1]{}[/gold1]",                            #11
    "[sea_green1]{}[/sea_green1]",                  #12
    "[white]{}[/white]",                            #13
    "[black]{}[/black]",                            #14
)

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

# Random Block color list
# -------------------------------------------------------------------
block_colors = [BR, BP, BO, BG, BC]
random.shuffle(block_colors)

# Variables
# ---------------------------------------------------------------------
pacman_delay = lambda x=[]: 0
pacman_ping = False
pacman_config = False
INFO = '[green]Info[/green]'
NOTICE = '[purple]Notice[/purple]'
WARNING = '[dark_orange]Warning[/dark_orange]'
ERROR = '[red]Error[/red]'
EXEC_ERROR = 'OS or Permission Error Occurred for Get {} Info'
threads: List[Thread] = []
outputs: Dict[str, str] = {
    'OS': '',
    'Kernel': '',
    'CPU': '',
    'GPU': '',
    'Display': '',
    'Memory': '',
    'Swap': '',
    'Disk': '',
    'Network': '',
    'UpTime': '',
}
limit = len(block_colors) + 1
max_width = os.get_terminal_size().columns // 29 # width of ghost
max_ghost = limit if max_width >= limit else max_width # How many ghost can place on terminal
config: Dict[str, str] = {}
rand_waits: List[int] = [0, 0, 0, 0, 0, 69, 69, 69, 69, 0, 0, 0, 0, 0]

# Options
# -------------------------------------------------------------------
option = Options()

@option('-v', '--version')
def do_you_wanna_see_version() -> None:
    pprint(
    f"""
    ---===❰ [blink]  [gold1]Pacmanfetch[/gold1]  [/blink]❱===---
    Version: {__version__}
    Source: {__repo__}
    """
    )


@option('-d', '--delay', has_input=True, type_of_input=int)
def do_you_wanna_typewriter_style(speed: int) -> None:
    global pacman_delay
    if not speed:
        pacman_delay = random.choice
    else: pacman_delay = lambda x=[]: speed


@option('-p', '--pacman')
def do_you_wanna_show_pacman() -> None:
    ghost_buffer = "{}" * max_ghost 
    for n in range(H + 1):
        pprint(ghost_buffer.format(
            PACMAN.split('\n')[n].replace('▒', ' '),
                *(
                    GHOST.split('\n')[n] \
                        .replace('▒', ' ') \
                        .replace(F, block_colors[i]) \
                        .replace('@', BW) \
                        .replace('#', BK) \
                        for i in range(max_ghost - 1)
                ),
            )
        )
        sleep(pacman_delay(rand_waits) / 369)


@option('-i', '--ping')
def do_you_wanna_ping() -> None:
    global pacman_ping
    pacman_ping = True


@option('-c', '--config')
def do_you_wanna_use_config() -> None:
    global pacman_config, config
    pacman_config = True

    config_path = os.path.dirname(os.path.abspath(__file__))
    if "config.json" in os.listdir(f"{config_path}/"):
        config_file = open(f"{config_path}/config.json", mode='r')
    else:
        default_conf = {
            "dns": "8.8.8.8",
            "gpu": "VGA"
        }
        with open(f"{config_path}/config.json", mode='w') as file:
            json.dump(default_conf, file)
        config_file = open(f"{config_path}/config.json", mode='r')
        pprint(f"[{NOTICE}]. config_file created!")

    config = json.load(config_file)
    
    config_file.close()


@option('-h', '--help')
def do_you_wanna_help() -> None:
    pprint(HELP)
    sys.exit()


# OS logos
# -------------------------------------------------------------------
# OS_name = os.uname()[3].split()[0].split('-')[1].lower()
# OS_version = os.uname()[3].split()[0].split('-')[0].split('~')[1]
OS_name = distro.id()
OS_version = distro.version(pretty=True, best=True)

TTY = f" {os.ttyname(sys.stdout.fileno())}"

OS_logos = {
    # It is not compatible for all os, because of icon-fonts.
    'nixos': ' ', 'ubuntu': ' ', 'debian': ' ',
    'raspbian': ' ', 'elementary': ' ', 'mint': ' ',
    'centos': ' ', 'fedora': ' ', 'redhat': ' ',
    'arch': ' ', 'manjaro': ' ', 'suse': ' ',
    'slackware': ' ', 'alpine': ' ', 'bsd': ' ',
    'gentoo': ' '
}

# CPU Brand:
# -------------------------------------------------------------------
AMD = '[red]AMD[/red]:'
Intel = '[blue]Intel[/blue]'

# System Info Structure
# -------------------------------------------------------------------
system_info_colors: List[str] = [
    'red',                  # os
    'sea_green1',           # kernel
    'dark_orange',          # cpu
    'medium_violet_red',    # gpu
    'slate_blue3',          # resolution
    'grey74',               # ram
    'hot_pink',             # swap
    'gold1',                # disk
    'dark_cyan',            # network
    'blue',                 # uptime
]

system_info_title: List[str] = [
    f"        OS {OS_logos.get(OS_name, ' ')}      │", # os
    '        Kernel    │', # kernel
    '        CPU       │', # cpu
    '        GPU       │', # gpu
    '        Display   │', # resolution
    '        Memory    │', # ram
    '        Swap      │', # swap
    '        Disk      │', # disk
    '        Network   │', # network
    '        UpTime    │', # uptime
]

NODE = "[bold][white] {0}{1}  [/white][yellow2] {2}[/yellow2][red]@[/red][cyan]{3}[/cyan][/bold]"

shell_symbols: Dict[str, str] = {
    'zsh': '%',
    'bash': '$',
}

# IP addresses
# -------------------------------------------------------------------
ifaces_addr: List[str] = []

# Pacman: Width=29, Height=12
# -------------------------------------------------------------------
MINI_PACMAN = '[yellow]󰮯 [/yellow]  [dark_orange]󰊠 [/dark_orange] [cyan]󰊠 [/cyan] [red]󰊠 [/red] [green]󰊠 [/green]'
PACMAN = """
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
GHOST = """
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
    cpu_freq = 0.0
    cmd = 'lscpu'
    all_info = subprocess.check_output(cmd, shell=True).decode().strip()
    for line in all_info.split('\n'):
        if re.search('Model name', line):
            cpu_info = ''.join(re.sub(r".*Model name.*: *", '', line)).replace('CPU @ ', '')

        elif re.search('CPU max MHz', line):
            cpu_freq = float(''.join(re.sub(r".*CPU max MHz.*: *", '', line))) / 1000
            break

    if 'AMD' in cpu_info:
        outputs['CPU'] = f" {cpu_info} {psutil.cpu_count()} Cores {cpu_freq:.1f} GHz"
    else:
        outputs['CPU'] = f" {cpu_info} {psutil.cpu_count()} Cores"

    return outputs['CPU']


@exception_handler(RuntimeWarning, PermissionError, OSError, cause=EXEC_ERROR.format('Memory'))
def ram() -> str:
    mem = psutil.virtual_memory()
    usage = f"{mem.percent:.1f}"
    used = f"{mem.used / (1024 ** 3):.1f}"
    total = f"{mem.total / (1024 ** 3):.1f}"

    outputs['Memory'] = f" {used} GB / {total} GB usage: {usage}%"
    return outputs['Memory']


@exception_handler(RuntimeWarning, PermissionError, OSError, cause=EXEC_ERROR.format('Swap'))
def swap() -> str:
    swap = psutil.swap_memory()
    usage = f"{swap.percent:.1f}"
    used = f"{swap.used / (1024 ** 3):.1f}"
    total = f"{swap.total / (1024 ** 3):.1f}"

    outputs['Swap'] = f" {used} GB / {total} GB usage: {usage}%"
    return outputs['Swap']


@exception_handler(RuntimeWarning, PermissionError, OSError, cause=EXEC_ERROR.format('Disk'))
def disk() -> str:
    home = psutil.disk_usage('/home')
    home_total = f"{home.total / (1024 ** 3):.1f}"
    home_free = f"{home.free / (1024 ** 3):.1f}"

    root = psutil.disk_usage('/')
    root_total = f"{root.total / (1024 ** 3):.1f}"
    root_free = f"{root.free / (1024 ** 3):.1f}"
    
    outputs['Disk'] = f" Root({root_total} GB) free: {root_free} GB │ Home({home_total} GB) free: {home_free} GB"
    return outputs['Disk']


def ping() -> str:
    dns = config.get('dns', '8.8.8.8')
    cmd = f"ping -c 1 {dns}"
    try:
        if not ifaces_addr:
            return f" 999ms   {dns}"
        else:
            with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE) as ping_proc:
                stdout = ''.join(line.decode('utf-8') for line in ping_proc.stdout)
                time = re.findall(r"time=.*ms", stdout)[0].replace('time=', '')
                return f" {time}   {dns}"

    except Exception:
        return f" 999ms   {dns}"


@threader(daemon=pacman_ping)
def network() -> str:
    try:
        net_ifaces = psutil.net_if_addrs()

        for interface_name, interface_addresses in net_ifaces.items():
            if interface_name.startswith(('w', 'e', 'u', 't', 'n')):
                for address in interface_addresses:
                    if address.family.name == 'AF_INET': # AF_INET = IPv4, AF_INET6 = IPv6
                        if interface_name.startswith(('t', 'n')):
                            ifaces_addr.insert(0, f"VPN  │")
                        else:
                            ifaces_addr.append(f"{interface_name}   {address.address} │")
    except (RuntimeWarning, PermissionError, OSError):
        outputs['Network'] = f" Check your   Connections {ping() if pacman_ping else ''}"
        return outputs['Network']

    if not ifaces_addr:
        outputs['Network'] = f" Check your   Connections {ping() if pacman_ping else ''}"
        return outputs['Network']
    else:
        iface_buffer = "{} " * len(ifaces_addr)
        iface_buffer = iface_buffer.format(*ifaces_addr).strip(' │')

        outputs['Network'] = f" {iface_buffer} {ping() if pacman_ping else ''}"
        return outputs['Network']


@threader(daemon=pacman_config)
def gpu() -> str:
    gpu_info = ''

    if pacman_config:
        gpu_info = config["gpu"]
        outputs['GPU'] = f" {gpu_info}"
        return outputs['GPU']
        
    def finder(brand: Dict[str, List[str]]) -> Generator[str, None, None]:
        patterns = {
            'AMD': r"\[.*\] Rembrandt",
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
                    yield f"{temp} │ "

    stdout = subprocess.run(
        'lspci',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    ).stdout.decode('utf-8')

    amd: Dict[str, List[str]] = {'AMD': [
        *re.findall(r"VGA.*(Advanced Micro Devices.*AMD.*) \(.*", stdout),
        *re.findall(r"3D.*(Advanced Micro Devices.*AMD.*) \(.*", stdout),
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
        gpu_info = config["gpu"]
    else:
        gpu_info = gpu_info.strip('│ ')

    outputs['GPU'] = f" {gpu_info}"
    return outputs['GPU']


def operate() -> str:
    outputs['OS'] = f" {OS_name.title()} {OS_version}"
    return outputs['OS']


def kernel() -> str:
    outputs['Kernel'] = f" {os.uname()[2]}"
    return outputs['Kernel']


def display() -> str:
    try:
        cmd = "xrandr | awk 'match($0,/[0-9]*\.[0-9]*\*/)'"
        all_info = subprocess.check_output(cmd, shell=True).decode().strip().split('\n')
        if not all_info[0]:
            outputs['Display'] = TTY
            return TTY

    except FileNotFoundError:
        outputs['Display'] = TTY
        return TTY

    else:
        displays = []
        for i, info in enumerate(all_info, start=1):
            resolution = info.split()[0]
            max_refresh_rate = max(
                [re.sub(r"(\*\+)|(\*)", '', ref) for ref in info.split()[1:]],
                key=len
            )
            displays.append(f" DP-{i}({resolution} {max_refresh_rate}Hz) ")

        outputs['Display'] = '│'.join(displays)
        return outputs['Display']


def node() -> str:
    global D
    shell = os.environ.get('SHELL').split('/')[-1]
    shell_symbol = shell_symbols.get(shell, '#')
    user = os.environ.get('USER')
    host = os.uname()[1]

    D = len(shell) + len(user) + len(host)
    return NODE.format(shell, shell_symbol, user, host)


def uptime() -> str:
    system_up = round(time() - psutil.boot_time())
    hours = system_up // 60 // 60
    minutes = system_up // 60 % 60
    seconds = system_up % 60

    outputs['UpTime'] = f" {hours}h {minutes}m {seconds}s"
    return outputs['UpTime']


@exception_handler(IndexError, cause=f"Not enough arguments")
@exception_handler(KeyboardInterrupt, cause=f"Ctrl+C", do_this=sys.exit)
def main() -> None:
    global config

    clear()

    # Argument parsing
    # -------------------------------------------------------------------
    for _ in option.parse(): ...

    # Draw system info
    # -------------------------------------------------------------------
    # system_info_details: List[str] = [
    operate()
    kernel()
    cpu()
    gpu()
    display()
    ram()
    swap()
    disk()
    network()
    uptime()
    # ]

    pprint(f"""
        {node()}
        {'─' * (int(D // 2) - 2)}── {MINI_PACMAN}{'─' * (int(D // 2) - 1)}""")

    for color, hw in zip(system_info_colors, outputs.keys()):
        try:
            # details = system_info_details.pop(0)
            details = outputs[hw]
            title = system_info_title.pop(0)
        except IndexError:
            break
        else:
            for char in title: # Type titles with color
                pprint(f"[{color}]{char}[/{color}]", end='')
                sleep(pacman_delay(rand_waits) / 3333)
            for char in details: # Type details without color
                pprint(f"{char}", end='')
                sleep(pacman_delay(rand_waits) / 3333)
            print()

    pprint(f"""        {'─' * (int(D // 2) - 2)}── {MINI_PACMAN}{'─' * (int(D // 2) - 1)}

          {COLOR_BANNER.format(*[color.format(F * 3) for color in colors])}
           {random.choice(colors).format(MAIN_BANNER)}""")

if __name__ == '__main__':
    main()
