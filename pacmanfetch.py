#!/bin/python3

from typing import List
from time import sleep
from rich.console import Console
from random import shuffle
import os, platform, subprocess, re, sys, distro

F = "█"
E = "▒"

BW = f"[white]{F}[/white]"
BC = f"[cyan]{F}[/cyan]"
BY = f"[gold1]{F}[/gold1]"
BG = f"[green]{F}[/green]"
BI = f"[hot_pink]{F}[/hot_pink]"
BR = f"[red]{F}[/red]"
BN = f"[deep_pink3]{F}[/deep_pink3]"
BP = f"[purple]{F}[/purple]"
BO = f"[dark_orange]{F}[/dark_orange]"
BS = f"[light_slate_blue]{F}[/light_slate_blue]"
BB = f"[royal_blue1]{F}[/royal_blue1]"
BE = f"[grey74]{F}[/grey74]"
BH = f"[khaki3]{F}[/khaki3]"
BK = f"[black]{F}[/black]"

colors = [BR, BP, BO, BG, BC]
shuffle(colors)

limit = len(colors) + 1

pacman = """
▒▒▒▒▒▒▒▒▒████████████▒▒▒▒▒▒▒▒▒
▒▒▒▒▒▒███████████████████▒▒▒▒▒
▒▒▒▒███████████████████████▒▒▒
▒▒███████████████████████▒▒▒▒▒
▒████████████████████▒▒▒▒▒▒▒▒▒
█████████████████▒▒▒▒▒▒▒▒▒▒▒▒▒
███████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
███████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
█████████████████▒▒▒▒▒▒▒▒▒▒▒▒▒
▒████████████████████▒▒▒▒▒▒▒▒▒
▒▒███████████████████████▒▒▒▒▒
▒▒▒▒███████████████████████▒▒▒
▒▒▒▒▒▒███████████████████▒▒▒▒▒
▒▒▒▒▒▒▒▒▒█████████████▒▒▒▒▒▒▒▒
""".replace(F, BY).replace('#', BK).replace('@', BW)

ghost = """
▒▒▒▒▒▒▒██████████████▒▒▒▒▒▒▒▒▒
▒▒▒▒▒██████████████████▒▒▒▒▒▒▒
▒▒▒@@@@@@█████@@@@@@█████▒▒▒▒▒
▒██@@##@@█████@@##@@███████▒▒▒
▒██####@@█████####@@███████▒▒▒
▒██@@@@@@█████@@@@@@███████▒▒▒
▒██████████████████████████▒▒▒
▒██████████████████████████▒▒▒
▒██████████████████████████▒▒▒
▒██████████████████████████▒▒▒
▒██████████████████████████▒▒▒
▒████▒▒████▒▒▒▒▒▒████▒▒████▒▒▒
▒██▒▒▒▒▒▒██▒▒▒▒▒▒██▒▒▒▒▒▒██▒▒▒
▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
"""

def clear() -> None:
    if platform.system() in "Linux Darwin":
        subprocess.run(['clear'])
    elif platform.system() in "Windows":
        subprocess.run(['cls'])
    else: pass

def cpu() -> str:
    if platform.system() == "Windows":
        return f"[bold][dark_orange]  Cpu[/dark_orange][/bold]: {platform.processor()}"
    elif platform.system() == "Darwin":
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        command ="sysctl -n machdep.cpu.brand_string"
        return f"[bold][dark_orange]  Cpu[/dark_orange][/bold]: {subprocess.check_output(command).strip()}"
    elif platform.system() == "Linux":
        command = "cat /proc/cpuinfo"
        all_info = subprocess.check_output(command, shell=True).decode().strip()
        for line in all_info.split("\n"):
            if "model name" in line:
                return f"[bold][dark_orange]  Cpu[/dark_orange][/bold]:{''.join(re.sub('.*model name.*:', '', line, 1).split('CPU @ '))}"
    return "Cpu None!"

def ram() -> str:
    mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    return f"[bold][slate_blue3]  Ram[/slate_blue3][/bold]: {round(mem_bytes / (1024 ** 3))} GB"

def oper() -> str:
    return f"[bold][red]  OS[/red][/bold]: {distro.id().title()} {distro.version()}"

def kernel() -> str:
    return f"[bold][chartreuse3]  Kernel[/chartreuse3][/bold]: {platform.release()}"

def node() -> str:
    os.environ.get('USERNAME')
    if platform.system() in "Linux Darwin":
        return f"[bold][yellow2]{os.environ.get('USER')}[/yellow2][red]@[/red][cyan]{platform.node()}[/cyan][/bold]"
    elif platform.system() == 'Windows':
        return f"[bold][yellow2]{os.environ.get('USERNAME')}[/yellow2][/bold]"


def main(arg: List[str]) -> None:
    console = Console()
    w = os.get_terminal_size().columns // 30
    m =  limit if w > limit else w

    clear()

    buffer = "{}" * m
    for n in range(15):
        console.print(buffer.format(
            pacman.split('\n')[n].replace('▒', ' '),
                *(
                    ghost.split('\n')[n] \
                        .replace('▒', ' ') \
                        .replace(F, colors[i]) \
                        .replace('@', BW) \
                        .replace('#', BK) \
                        for i in range(m - 1)
                ),
            )
        )
        if len(arg) == 1:
            sleep(0.0)
        elif len(arg) == 2:
            if arg[1].isdigit():
                sleep(int(arg[1]) / 1000)
            else:
                sleep(0.0)
        else:
            sleep(0.0)

    console.print(
        f"""[white]
        [bold][green]Pacmanfetch:[/green][/bold]
            {node()}
            {oper()}
            {kernel()}
            {cpu()}
            {ram()}
              {''.join(colors).replace(F, F * 3)}
        [/white]"""
    )

if __name__ == '__main__':
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        sys.exit()
