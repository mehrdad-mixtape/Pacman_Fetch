#!/bin/python3
# -*- coding: utf8 -*-

# MIT License

# Copyright (c) 2022 mehrdad
# Developed by mehrdad-mixtape https://github.com/mehrdad-mixtape/Pacman_Fetch

# Python Version 3.6 or higher
# Pacman_Fetch

#TODO: Improve Option, "pacmanfetch -pi -v -d 10" != "pacmanfetch -d 10 -pi -v"

BETA = "[red]beta[/]"
ALPHA = "[purple]alpha[/]"
STABLE = "[green]stable[/]"

__repo__ = "https://github.com/mehrdad-mixtape/Pacman_Fetch"
__version__ = f"v1.2.0-{STABLE}"
__project__ = "Pacman Fetch"

import os
import re
import sys
import json
import time
import random
import inspect
import itertools
import subprocess
import dataclasses

from typing import (
    Tuple, List, Dict,
    Generator, Callable, Any
)

try:
    import psutil, distro
    from rich.box import HORIZONTALS
    from rich.text import Text
    from rich.table import Table
    from rich.console import Console
    from rich import pretty, traceback

    from threading import Thread

    # from bigtree.tree.construct import list_to_tree
    # from bigtree.tree.export import yield_tree

except ImportError as E:
    print(f"[*] Error. {E} - Please Install the Pkgs.")
    sys.exit()

else:
    pretty.install()
    traceback.install()

# Colors
# -------------------------------------------------------------------
SUPPORTED_COLOR = "red sea_green1 dark_orange medium_violet_red slate_blue3".split(' ') + \
"grey74 hot_pink gold1 dark_cyan blue purple chartreuse3 cyan orange4 white".split(' ') + \
"black green yellow grey66 salmon1".split(' ')

COLOR_BANNER = """{}{}{}{}{}{}{}
           {}{}{}{}{}{}{}"""

# Icons
# -------------------------------------------------------------------
GITHUB = '\uf113'
PYTHON = '\ue235'
HEART = '\uf004'
CPU = '\uf4bc'
BRAIN = '\ue28c'
LEGO = '\ue0ce'
SCREEN = '\ueb4c'
MEMORY = '\ue266'
SWAP = '\ue238'
DISK = '\ue240'
NETWORK = '\ueb3a'
UPTIME = '\uf0f4'
PING = '\uf0ec'
LINUX = '\uebc6'
HOTDOG = '\ue251'
DICE = '\ue270'
HAMBURGER = '\ue24d'

# Banners
# -------------------------------------------------------------------
BANNER = f"""
    ────━━━━ [blink][gold1]{__project__}[/][/] ━━━━────
        Version: {__version__}
        Source: {__repo__}
"""

MAIN_BANNER = f"""[bold][blink]┎─────────────────┒
            ║ {PYTHON} Pacmanfetch {GITHUB} ║
            ┖─────────────────┚[/][/]"""

# Functions
# -------------------------------------------------------------------
console = Console()
pprint = lambda *args, **kwargs: console.print(*args, **kwargs)

def clear() -> None:
    print('\033c', end='')


def goodbye(expression: bool, cause: str='Unknown'):
    if expression:
        pprint("{} {}#{}".format(
            cause,
            inspect.getouterframes(inspect.currentframe())[1].filename.split('/')[-1],
            inspect.getouterframes(inspect.currentframe())[1].lineno
        ))
        sys.exit()

# Decorators
# -------------------------------------------------------------------
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
# -------------------------------------------------------------------
@dataclasses.dataclass(slots=True, eq=False, frozen=True)
class Method:
    do_this: Callable[[Any], Any]
    has_input: bool
    type_input: type
    default_input: Any
    is_required: bool
    help_description: str


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
            
            @option('--opt')

            def do_you_wanna_something_to_do():
                ...
            
            @option('-s', '--opt')

            def do_you_wanna_something_to_do():
                ...
            
            @option('-s', '--opt', has_input=True, type_input=type)

            def do_you_wanna_something_to_do(arg: type):
                ...

            @option('-s', '--opt', required=True)

            def do_you_wanna_something_to_do():
                ...
    """

    __slots__ = ("project_name", "__option_method", "__run_without_help", "__intro")

    def __init__(self, project_name: str, intro: str='', run_without_help: bool=True):
        self.project_name = project_name
        self.__option_method: Dict[str, Method] = {
            ('--help',): Method(self.__help, False, None, None, False, f"Show help Screen of {project_name}")
        }
        self.__intro = intro
        self.__run_without_help = run_without_help


    def __repr__(self):
        return f"Input Args: {sys.argv} to parse"


    def __call__(
            self, *options: Tuple[str],
            has_input: bool=False,
            type_input: type=None,
            default_input: Any=None,
            is_required: bool=False,
            help_description: str="...",
        ):
        """
            options: start with - or --.
            has_input: maybe the options include the argument after them.
            type_input: type of arguments after option and depends on has_input.
            default_input: get default input if user don't give enough arg to option.
            is_required: force to use option.
            help_description: the description for option about how to use option.
        """
        def __decorator__(func: Callable[[Any], Any]) -> Callable[[None], None]:

            for exist_opt in self.__option_method:
                for opt in exist_opt:
                    goodbye(
                        opt in options,
                        cause="Duplicate option=({0}) selected for [bold]{1}[/], But now [bold]{2}[/] used for [bold]{3}[/]".format(
                            opt, func.__name__, opt, self.__option_method.get(exist_opt).do_this.__name__
                        )
                    )

            self.__option_method[options] = Method(func, has_input, type_input, default_input, is_required, help_description)

        return __decorator__


    @property
    def option_method(self) -> Dict[str, Method]:
        return self.__option_method


    @property
    def all_options(self) -> List[str]:
        opt_lst: List[str] = []

        for option in self.option_method:
            for opt in option: opt_lst.append(opt)

        return opt_lst


    def parse(self) -> Generator[Tuple[Tuple[str], Any], None, None]:

        goodbye(
            len(sys.argv) < 2 and not self.__run_without_help,
            cause=f"Run program with --help for more information."
        )

        # Handle option validation and combination
        for i, opt_argv in enumerate(sys.argv, start=1):
            if not opt_argv.startswith(('-', '--')):
                continue # valid options can start with - --

            # Handle the complete-options: Example ==> --add --list --dump
            else:
                goodbye( # if user enter just - or --
                    opt_argv in ('-', '--'),
                    cause=f"Invalid option=({opt_argv})"
                )

                for option in self.option_method:
                    if opt_argv in option: # -t in ('-t', '--type') ?
                        break

                else: goodbye(True, cause=f"Invalid option=({opt_argv})")

            yield self.__executer(option, i)                

            # TODO: It's not work properly!!!
            # Convert -ald to -a -l -d and parse it individually
            # Handle the abbreviation-options: Example ==> -a -l -d
            # Handle the mixed abbreviation-options: Example ==> -ald = -dal

        # Handle is_required flag
        for option, method in self.option_method.items():
            for opt in option:
                if not (opt not in sys.argv and method.is_required == True): break

            else:
                goodbye(
                    True,
                    cause="Input CMD: {0} <missing-option>\nThis missing-option=({1}) is Required, use --help to see".format(
                        ' '.join(sys.argv), ' '.join(option)
                ))


    def __executer(self, option: Tuple[str], option_index: int) -> Any:

        method: Method = self.option_method[option]
        output: Any = None

        if not method.has_input:
            return option, method.do_this()

        try:
            arg_input = sys.argv[option_index]

            goodbye(
                method.type_input is None,
                cause=f"Get type-of-arguments=({arg_input}) after [bold]{option}[/]",
            )
            goodbye(
                method.default_input is not None
                and not isinstance(method.default_input, method.type_input),
                cause="Gave bad-default-argument=({0}) after [bold]{1}[/], type_input=[bold]{2}[/] & default_input=[bold]{3}[/] are inconsistent!".format(
                    method.default_input, option, method.type_input.__name__, method.default_input
            ))
            # script.py -r 10 -o -p good // -o in middle and it has default input
            if arg_input in self.all_options:
                goodbye(
                    method.default_input is None,
                    cause=f"Not enough-argument after [bold]{option}[/], use --help for more information.",
                )
                goodbye(
                    not isinstance(method.default_input, method.type_input),
                    cause="Gave bad-default-argument=({0}) after [bold]{1}[/], type_input=[bold]{2}[/] & default_input=[bold]{3}[/] are inconsistent!".format(
                        method.default_input, option, method.type_input.__name__, method.default_input
                ))

                return option, method.do_this(method.type_input(method.default_input))

            arg_input = method.type_input(arg_input)
            output = method.do_this(arg_input)

        except IndexError:
            goodbye(
                method.default_input is None,
                cause=f"Not enough-argument after [bold]{option}[/], use --help for more information.",
            )
            goodbye(
                not isinstance(method.default_input, method.type_input),
                cause="Gave bad-default-argument=({0}) after [bold]{1}[/], type_input=[bold]{2}[/] & default_input=[bold]{3}[/] are inconsistent!".format(
                    method.default_input, option, method.type_input.__name__, method.default_input
            ))

            # script.py -r 10 -p good -o // -o in end and it has default input
            output = method.do_this(method.type_input(method.default_input))

        except ValueError:
            goodbye(
                method.default_input is None,
                cause="Gave bad-argument=({0}) after [bold]{1}[/], type_input=[bold]{2}[/] & arg_input=[bold]{3}[/] are inconsistent!".format(
                    arg_input, option, method.type_input.__name__, arg_input
            ))

            output = method.do_this(method.default_input)

        except TypeError:
            goodbye(
                True,
                cause=f"You enabled [bold]has_input[/] for {method.do_this.__name__}(), Write input-argument for it"
            )

        return option, output


    def __help(self) -> None:
        CYCLE_COLOR = itertools.cycle(SUPPORTED_COLOR)

        table = Table(
            "Options",
            "Required",
            # "Function",
            "Help",
            box=HORIZONTALS,
            title=f"""{self.project_name}""",
        )

        pprint(self.__intro)

        for option, method in self.option_method.items():
            table.add_row(
                Text(' '.join(option), style=f"bold italic {next(CYCLE_COLOR)}"),
                Text('<<<-----' if method.is_required else '', style="bold"),
                # method.do_this.__name__,
                Text(method.help_description, justify=True),

            )

        pprint(table)
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

# Random Block color list
# -------------------------------------------------------------------
block_colors = ['[red]', '[purple]', '[dark_orange]', '[green]', '[cyan]']
random.shuffle(block_colors)

# Variables
# ---------------------------------------------------------------------
pacman_delay = lambda x=[]: 0
pacman_ping = False
pacman_config = False
INFO = '[green]Info[/]'
NOTICE = '[purple]Notice[/]'
WARNING = '[dark_orange]Warning[/]'
ERROR = '[red]Error[/]'
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
progress_length = 20

# Options
# -------------------------------------------------------------------
option = Options(
    __project__,
    intro="""
    For Better Experience Install NerdFont: https://www.nerdfonts.com/
    """
)

@option(
    '-v', '--version',
    help_description=f"pacmanfetch -v. Show version of {__project__}."
)
def do_you_wanna_see_version() -> None:
    pprint(BANNER)
    exit(0)


@option(
    '-d', '--delay',
    has_input=True, type_input=int,
    help_description="pacmanfetch -d <0-...>. Type writer style printing"
)
def do_you_wanna_typewriter_style(speed: int) -> None:
    global pacman_delay
    if not speed:
        pacman_delay = random.choice
    else: pacman_delay = lambda x=[]: speed


@option(
    '-p', '--pacman',
    help_description="pacmanfetch -p. Show Pacman and Ghosts"
)
def do_you_wanna_show_pacman() -> None:
    ghost_buffer = "{}" * max_ghost 
    for n in range(H):
        pprint(ghost_buffer.format(
                PACMAN('[yellow]').split('\n')[n],
                *(GHOST(i).split('\n')[n] for i in range(max_ghost - 1)),
            )
        )
        time.sleep(pacman_delay(rand_waits) / 369)


@option(
    '-i', '--ping',
    help_description="pacmanfetch -i. Enable ping to check network connection"
)
def do_you_wanna_ping() -> None:
    global pacman_ping
    pacman_ping = True


@option(
    '-c', '--config',
    help_description="pacmanfetch -c. Use \"config.json\" file"
)
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


# OS logos
# -------------------------------------------------------------------
OS_name = distro.id()
OS_version = distro.version(pretty=True, best=True)

TTY = f" Term-({os.ttyname(sys.stdout.fileno())})"

OS_logos = {
    # It is not compatible for all os, because of icon-fonts.
    'nixos': '\uf313', 'ubuntu': '\uf31b', 'debian': '\uf306',
    'raspbian': '\uf315', 'elementary': '\uf309', 'mint': '\uf30e',
    'centos': '\uf304', 'fedora': '\uf30a', 'redhat': '\uf316',
    'arch': '\uf303', 'manjaro': '\uf312', 'opensuse': '\uf314',
    'slackware': '\uf319', 'alpine': '\uf300', 'bsd': '\uf30c',
    'gentoo': '\uf30d', 'kali': '\uf327', 'deepin': '\uf321',
    'garuda': '\uf337'
}

# CPU Brand:
# -------------------------------------------------------------------
AMD = '[red]AMD[/red]:'
Intel = '[blue]Intel[/blue]'

# System Info Structure
# -------------------------------------------------------------------
SYS_INFO_TITLE: List[str] = [
    f"{OS_logos.get(OS_name, LINUX)}  OS      ",
    f"{HEART}  Kernel  ",
    f"{BRAIN}  CPU     ",
    f"{LEGO}  GPU     ",
    f"{SCREEN}  Display ",
    f"{MEMORY}  Memory  ",
    f"{SWAP}  Swap    ",
    f"{DISK}  Disk    ",
    f"{NETWORK}  Network ",
    f"{UPTIME}  UpTime  ",
]

NODE = "[bold][white]\ue683 {0}{1}  [/white][yellow2]\ue23f {2}[/yellow2][red]@[/red][cyan]{3}[/cyan][/bold]"

SEHLL_SYMS: Dict[str, str] = {
    'zsh': '%',
    'bash': '$',
}

# IP addresses
# -------------------------------------------------------------------
ifaces_addr: List[str] = []

# Pacman: Width=29, Height=12
# -------------------------------------------------------------------
MINI_PACMAN = '[yellow]󰮯 [/]  [dark_orange]󰊠 [/] [cyan]󰊠 [/] [red]󰊠 [/] [green]󰊠 [/]'
PACMAN = lambda ci: """
{0}▒▒▒▒▒▒▒██████████████▒▒▒▒▒▒▒▒[/]
{0}▒▒▒▒▒███████████████████▒▒▒▒▒[/]
{0}▒▒▒███████████████████████▒▒▒[/]
{0}▒█████████████████████▒▒▒▒▒▒▒[/]
{0}██████████████████▒▒▒▒▒▒▒▒▒▒▒[/]
{0}████████████████▒▒▒▒[/]{1} {2} {3} {4} ▒
{0}██████████████████▒▒▒▒▒▒▒▒▒▒▒[/]
{0}▒█████████████████████▒▒▒▒▒▒▒[/]
{0}▒▒▒███████████████████████▒▒▒[/]
{0}▒▒▒▒▒███████████████████▒▒▒▒▒[/]
{0}▒▒▒▒▒▒▒▒█████████████▒▒▒▒▒▒▒▒[/]
""".format(ci, HAMBURGER, PYTHON, DICE, HOTDOG).replace(E, ' ')

# Ghost: Width=29, Height=12
# -------------------------------------------------------------------
GHOST = lambda ci: """
{0}▒▒▒▒▒▒▒██████████████▒▒▒▒▒▒▒▒[/]
{0}▒▒▒▒▒██████████████████▒▒▒▒▒▒[/]
{0}▒▒▒@@@@@@█████@@@@@@█████▒▒▒▒[/]
{0}▒██@@##@@█████@@##@@███████▒▒[/]
{0}▒██####@@█████####@@███████▒▒[/]
{0}▒██@@@@@@█████@@@@@@███████▒▒[/]
{0}▒██████████████████████████▒▒[/]
{0}▒██████████████████████████▒▒[/]
{0}▒██████████████████████████▒▒[/]
{0}▒████▒▒████▒▒▒▒▒▒████▒▒████▒▒[/]
{0}▒██▒▒▒▒▒▒██▒▒▒▒▒▒██▒▒▒▒▒▒██▒▒[/]
""".format(block_colors[ci]).replace(E, ' ').replace('@', f"[white]{F}[/]").replace('#', f"[black]{F}[/]")


def cpu() -> None:
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


@exception_handler(RuntimeWarning, PermissionError, OSError, cause=EXEC_ERROR.format('Memory'))
def memory() -> None:
    mem = psutil.virtual_memory()
    usage = round(mem.percent)
    total = round(mem.total / (1000 ** 3), 1)
    used =  round(abs(total - mem.available / (1000 ** 3)), 1)

    pu = usage * progress_length // 100
    pr = progress_length - pu

    outputs['Memory'] = f" Usage: 〉{'━' * pu}{'╍' * pr}〈 {usage:.2f}% =~ {used}GB / {total}GB"


@exception_handler(RuntimeWarning, PermissionError, OSError, cause=EXEC_ERROR.format('Swap'))
def swap() -> None:
    swap = psutil.swap_memory()
    usage = round(swap.percent)
    total = round(swap.total / (1000 ** 3), 1)
    used = round(abs(total - swap.free / (1000 ** 3)), 1)
    
    pu = usage * progress_length // 100
    pr = progress_length - pu

    outputs['Swap'] = f" Usage: 〉{'━' * pu}{'╍' * pr}〈 {usage:.2f}% =~ {used}GB / {total}GB"


@exception_handler(RuntimeWarning, PermissionError, OSError, cause=EXEC_ERROR.format('Disk'))
def disk() -> None:
    home = psutil.disk_usage('/home')
    home_total = f"{home.total / (1024 ** 3):.1f}"
    home_free = f"{home.free / (1024 ** 3):.1f}"

    root = psutil.disk_usage('/')
    root_total = f"{root.total / (1024 ** 3):.1f}"
    root_free = f"{root.free / (1024 ** 3):.1f}"
    
    outputs['Disk'] = f""" Root({root_total} GB) free: {root_free} GB ━ Home({home_total} GB) free: {home_free} GB"""


def ping() -> str:
    dns = config.get('dns', '8.8.8.8')
    cmd = f"ping -c 1 {dns}"

    if not ifaces_addr:
        return f"Ping: 999ms {PING}  {dns}"

    else:
        try:
            with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE) as ping_proc:
                stdout = ''.join(line.decode('utf-8') for line in ping_proc.stdout)
                time = re.findall(r"time=.*ms", stdout)[0].replace('time=', '')
                return f"Ping: {time} {PING}  {dns}"

        except Exception:
            return f"Ping: 999ms {PING}  {dns}"


@threader(daemon=pacman_ping)
def network() -> None:
    try:
        net_ifaces = psutil.net_if_addrs()

        for interface_name, interface_addresses in net_ifaces.items():
            for address in filter(lambda addr: addr.family.name == "AF_INET", interface_addresses):
                if interface_name.startswith(('t', 'n', 'wg')):
                    ifaces_addr.insert(0, f" VPN 󰢭  ")

                elif interface_name.startswith(('e', 'u', 'd', 'b')):
                    ifaces_addr.append(f" {interface_name} 󱘖  {address.address} 󰈀  ")

                elif interface_name.startswith('w'):
                    ifaces_addr.append(f" {interface_name} 󱘖  {address.address}   ")

    except (RuntimeWarning, PermissionError, OSError):
        outputs['Network'] = f" Check your 󱘖  Connections 󰌙 {ping() if pacman_ping else ''}"

        return

    if not ifaces_addr:
        outputs['Network'] = f" Check your 󱘖  Connections 󰌙 {ping() if pacman_ping else ''}"

    else:
        outputs['Network'] = f"{'║'.join(ifaces_addr)} {ping() if pacman_ping else ''}"


@threader(daemon=pacman_config)
def gpu() -> None:
    gpu_info = []

    if pacman_config:
        outputs['GPU'] = f" {config['gpu']}"
        return outputs['GPU']

    def extractor(brand: Dict[str, List[str]]) -> Generator[str, None, None]:
        patterns = {
            'AMD': r"\[AMD/ATI\] [a-zA-Z]*/?[a-zA-Z]*",
            'Intel': r"(U?HD Graphics [0-9]*?$)|(Iris Xe Graphics.*)",
            'NVIDIA': r"\[.*\].*"
        }
        for name, gpus in brand.items():
            for gpu in gpus:
                try:
                    yield re.search(patterns.get(name, r".*"), gpu) \
                        .group().replace('[', '').replace(']', '')

                except Exception:
                    yield ""

    stdout = subprocess.run('lspci', shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode('utf-8')

    amd: Dict[str, List[str]] = {'AMD': [
        *re.findall(r"VGA.*(\[AMD/ATI\].*) \(", stdout),
        *re.findall(r"3D.*(\[AMD/ATI\].*) \(", stdout),
        #*re.findall(r"Display.*(\[AMD/ATI\].*) \(", "Display controller [0830]: Advance, Inc. [AMD/ATI] lexa pro [Radeon RX 550/550X] [123:123] (rev c3)"),
        #"[AMD/ATI] Picasso/Raven 2 [Radeon Vega Series / Radeon Vega Mobile Series] (rev d2)",
        #"[AMD/ATI] Rembrandt (rev c8)",
    ]}
    intel: Dict[str, List[str]] = {'Intel': [
        *re.findall(r"VGA.*(Intel.*) \(", stdout),
        *re.findall(r"3D.*(Intel.*) \(", stdout),
    ]}
    nvidia: Dict[str, List[str]] = {'NVIDIA': [
        *re.findall(r"VGA.*(NVIDIA.*) \(", stdout),
        *re.findall(r"3D.*(NVIDIA.*) \(", stdout),
    ]}

    for brand in [amd, intel, nvidia]:
        for gpu in extractor(brand):
            gpu_info.append(f" {gpu} ")

    if not gpu_info:
        outputs['GPU'] = " Unknown Vendor!"

    else:
        outputs['GPU'] = '━'.join(gpu_info)


def operate() -> None:
    outputs['OS'] = f" {OS_name.title()} {OS_version}"


def kernel() -> None:
    outputs['Kernel'] = f" {os.uname()[2]}"


def display() -> None:
    try:
        cmd = "xrandr | awk 'match($0,/[0-9]*\.[0-9]*\*/)'"
        all_info = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.DEVNULL
        ).decode().strip().split('\n')

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
            displays.append(f" DP-{resolution} {max_refresh_rate}Hz ")

        outputs['Display'] = '━'.join(displays)
        # outputs['Display'] = displays


def node() -> str:
    global D

    shell = os.environ.get('SHELL').split('/')[-1]
    shell_symbol = SEHLL_SYMS.get(shell, '#')
    user = os.environ.get('USER')
    host = os.uname()[1]

    D = int(len(shell + user + host) * 1.5)
    return NODE.format(shell, shell_symbol, user, host)


def uptime() -> None:
    system_up = round(time.time() - psutil.boot_time())
    hours = system_up // 60 // 60
    minutes = system_up // 60 % 60
    seconds = system_up % 60

    outputs['UpTime'] = f" {hours}h {minutes}m {seconds}s"


@exception_handler(KeyboardInterrupt, cause=f"Ctrl+C", do_this=sys.exit)
def main() -> None:
    global config

    # Argument parsing
    # -------------------------------------------------------------------
    for _ in option.parse(): ...

    # Call system info
    # -------------------------------------------------------------------
    operate()
    kernel()
    cpu()
    gpu()
    display()
    memory()
    swap()
    disk()
    network()
    uptime()
    clear()

    # Draw system info
    # -------------------------------------------------------------------
    pprint(f"""
        {node()}
        {'─' * (D // 2 - 4)}╍╍╍╍━━━ {MINI_PACMAN}━━━╍╍╍╍{'─' * (D // 2 - 4)}""")

    for color, hw in zip(SUPPORTED_COLOR, outputs):
        try:
            details = outputs[hw]
            title = SYS_INFO_TITLE.pop(0)

        except IndexError:
            break

        else:
            pprint("         ║ ", end='')
            for char in title: # Type titles with color
                pprint(f"[{color}]{char}[/]", end='')
                time.sleep(pacman_delay(rand_waits) / 3333)

            pprint("║", end='')

            for char in details: # Type details without color
                pprint(f"{char}", end='')
                time.sleep(pacman_delay(rand_waits) / 3333)

            print()

    pprint(f"""        {'─' * (D // 2 - 4)}╍╍╍╍━━━ {MINI_PACMAN}━━━╍╍╍╍{'─' * (D // 2 - 4)}

          {COLOR_BANNER.format(*[f"[{color}]{E * 3}[/]" for color in SUPPORTED_COLOR])}
            [{random.choice(SUPPORTED_COLOR)}]{MAIN_BANNER}[/]""")

    # o = list_to_tree(outputs['Display'].split("║"), sep='-')
    # for m in yield_tree(o, style='rounded'):
    #     pprint(m[1], m[2].name)
    # o.show(style='rounded')

if __name__ == '__main__':
    main()
