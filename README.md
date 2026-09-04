# Pacman Fetch
<img src="index.gif">

## An other Fetch Family!

- nerdfetch? no!
- pfetch? no!
- neofetch? no!
- **pacmanfetch?** YES!

## Interview:
![image](https://github.com/mehrdad-mixtape/Pacman_Fetch/blob/master/index.png)

## Platform:
- **Linux**
	- **WSL: Windows Sub System(recommended)** is a Linux too, **Windows terminal** app is better than powershell and cmd.
	- `pacmanfetch` reads `/proc`, `lscpu`, `lspci` and `xrandr`, so on any other system the panel stays empty.

## Font:
Every icon of the panel comes from a **nerd-font**, without a patched font you only see empty boxes.
1. download your favorite **nerd-font** from this [link](https://www.nerdfonts.com/font-downloads)
2. copy your **nerd-font** to `~/.fonts` and `~/.local/share/fonts`
3. go to *preference* or *settings* of your terminal, change the font of terminal to your **nerd-font**

## File structure:
```text
Pacman_Fetch
├── __main__.py      # the whole tool: option parser, collectors and the panel
├── config.json      # optional, only read with -c ("dns" and "gpu"), gitignored
├── requirements.txt # rich, psutil, distro
├── index.gif        # the animation on top of this page
└── index.png        # a screenshot of the panel
```
There is only **one** python file, nothing to install and nothing to import.

## How to use?
1. Install requirements, **python 3.10 or higher** (the option parser uses `dataclass(slots=True)`):
    ```bash
    pip3 install -r requirements.txt
    ```
2. Run
    ```bash
    python3 __main__.py
    ```

### Check the switches of pacmanfetch:
```text
                                    Pacman Fetch                                     
 ─────────────────────────────────────────────────────────────────────────────────── 
  Options        Required   Help                                                     
 ─────────────────────────────────────────────────────────────────────────────────── 
  --help                    Show help Screen of Pacman Fetch                         
  -v --version              pacmanfetch -v. Show version of Pacman Fetch.            
  -d --delay                pacmanfetch -d <0-...>. Type writer style printing       
  -p --pacman               pacmanfetch -p. Show Pacman and Ghosts                   
  -i --ping                 pacmanfetch -i. Enable ping to check network connection  
  -c --config               pacmanfetch -c. Use "config.json" file                   
 ───────────────────────────────────────────────────────────────────────────────────
```

### Bundling the short options:
Short options can be written one by one or bundled together, and the input-argument of an
option like `-d` may be glued to it:
```bash
python3 __main__.py -p -i -c     # options one by one
python3 __main__.py -pic          # the same, bundled
python3 __main__.py -d 10         # typewriter speed 10
python3 __main__.py -d10          # the same, value glued to -d
python3 __main__.py -pd10         # bundle + glued value
```
A wrong command-line never ends in a traceback, `pacmanfetch` says what is wrong and where
(the `__main__.py#<line>` at the end is the check that stopped it):
```text
Invalid option=(-z) __main__.py#507
Not enough-argument after ('-d', '--delay'), use --help for more information. __main__.py#677
Gave bad-argument=(abc) after ('-d', '--delay'), type_input=int & arg_input=abc are inconsistent! __main__.py#698
```

### config.json
`config.json` is used when you run `pacmanfetch -c`:
1. set dns address to ping it (`-i`).
2. set gpu_info, if your gpu_info not found!

If the file is not there, `-c` creates it next to `__main__.py` with these default values, and
it is gitignored so your own config stays yours:
```json
{"dns": "8.8.8.8", "gpu": "VGA"}
```

### What do you get?
| Row | Where it comes from |
|:----|:--------------------|
| **OS** | `distro`, with the nerd-font logo of Arch, Manjaro, Garuda, NixOS, Ubuntu, Debian, Raspbian, Mint, elementary, Fedora, CentOS, RedHat, openSUSE, Slackware, Alpine, Gentoo, Kali, Deepin and BSD, a generic logo for the rest |
| **Kernel** | `os.uname()` |
| **CPU** | `lscpu` / `/proc/cpuinfo`, the model, the cores and the max clock of AMD and Intel |
| **GPU** | `lspci` for `AMD/ATI`, `Intel` and `NVIDIA`, or `config.json` with `-c` |
| **Display** | `xrandr` resolution + refresh rate of every monitor, or the `TTY` name on a bare console |
| **Memory / Swap** | `psutil`, as a usage bar |
| **Disk** | `psutil`, the free space of `/` and `/home` |
| **Network** | the ip of wireless, wired and tunnel interfaces, `Ping:` when `-i` is given |
| **UpTime** | `psutil.boot_time()` |

### Tips:
- Without `-d` the panel is printed at once, `-d 0` is the random typewriter speed and `-d <number>` a fixed one.
- How many ghosts chase pacman (`-p`) depends on the width of your terminal.
- The output is safe to pipe or redirect: `python3 __main__.py > report.txt`.

## License
MIT, see [LICENSE](LICENSE).

