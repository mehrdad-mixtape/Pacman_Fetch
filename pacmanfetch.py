from typing import List
from time import sleep
from rich.console import Console
import os, platform, subprocess, re, sys, distro

F = "█"
E = "▒"

BW = f"[white]{F}[/white]"
BC = f"[cyan]{F}[/cyan]"
BY = f"[gold1]{F}[/gold1]"
BR = f"[red]{F}[/red]"
BP = f"[purple]{F}[/purple]"
BO = f"[dark_orange]{F}[/dark_orange]"
BK = f"[black]{F}[/black]"

colors = [BR, BC, BP, BO]

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
""".replace(F, BY).replace('#', BK)

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
        return f"[bold][dark_orange]Cpu[/dark_orange][/bold]: {platform.processor()}"
    elif platform.system() == "Darwin":
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        command ="sysctl -n machdep.cpu.brand_string"
        return f"[bold][dark_orange]Cpu[/dark_orange][/bold]: {subprocess.check_output(command).strip()}"
    elif platform.system() == "Linux":
        command = "cat /proc/cpuinfo"
        all_info = subprocess.check_output(command, shell=True).decode().strip()
        for line in all_info.split("\n"):
            if "model name" in line:
                return f"[bold][dark_orange]Cpu[/dark_orange][/bold]:{''.join(re.sub('.*model name.*:', '', line, 1).split('CPU @ '))}"
    return "Cpu None!"

def ram() -> str:
    mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    return f"[bold][slate_blue3]Ram[/slate_blue3][/bold]: {round(mem_bytes / (1024 ** 3))} GB"

def oper() -> str:
    return f"[bold][red]OS[/red][/bold]: {distro.id().title()} {distro.version()}"

def kernel() -> str:
    return f"[bold][chartreuse3]Kernel[/chartreuse3][/bold]: {platform.release()}"

def node() -> str:
    os.environ.get('USERNAME')
    if platform.system() in "Linux Darwin":
        return f"[bold][yellow2]{os.environ.get('USER')}[/yellow2][red]@[/red][cyan]{platform.node()}[/cyan][/bold]"
    elif platform.system() == 'Windows':
        return f"[bold][yellow2]{os.environ.get('USERNAME')}[/yellow2][/bold]"


def main(arg: List[str]) -> None:
    console = Console()
    w = os.get_terminal_size().columns // 30
    m = 5 if w > 5 else w

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
        [bold][green]Rig:[/green][/bold]
            {node()}
            {oper()}
            {kernel()}
            {cpu()}
            {ram()}
        [/white]"""
    )

if __name__ == '__main__':
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        sys.exit()
