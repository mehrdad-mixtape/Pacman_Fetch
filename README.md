# Pacman Fetch
<img src="index.gif">

## An other Fetch Family!

- nerdfetch? no!
- pfetch? no!
- neofetch? no!
    ### **pacmanfetch?** YES!

## Interview:
![image](https://github.com/mehrdad-mixtape/Pacman_Fetch/blob/master/index.png)

## Platform:
- **Linux**
- **WSL: Windows Sub System(recommended)**
	- **Windows terminal** app is better than powershell and cmd
- **Mac?** Test and tell me result ;)

## Font:
icon_in_terminal project [github](https://github.com/sebastiencs/icons-in-terminal) link
1. requierment package:
	- Debian:
	```bash
	sudo apt install fontconfig
    ```
2. copy all fonts that exist on `icon-terminal-terminal/fonts` to `~/.fonts` and `~/.local/share/fonts`
    - if `~/.fonts` and `~/.local/share/fonts` does not exist, then create them!
        ```bash
        mkdir ~/.fonts ~/.local/share/fonts
        ```
3. download your favorite **nerd-font** from this [link](https://www.nerdfonts.com/font-downloads)
    1. copy your **nerd-font** to `~/.fonts` and `~/.local/share/fonts`
    2. go to *preference* or *settings* of your terminal, change the font of terminal to your **nerd-font**
4. go to `icon-terminal-terminal/` and execute the **install.sh**
    ```bash
    ./install.sh
    ```
5. close your terminal and open it again, then go to `icon-terminal-terminal/` and execute the **print_icons.sh**
    ```bash
    ./print_icons.sh
    ```
- Check this [tutorial](https://drive.google.com/file/d/1OzPaTG-C80zPBTJEpZWSkWy1y1jB03Pq/view?usp=sharing) for install fonts

## How to use?
- **First way(Support *linux* and *wsl*)**: Run executable file that exist on **bin/** and run it.
    ```bash
    ./bin/pacmanfetch
    ```
- **Second way**: Run pacmanfetch.py
    1. Install requirements
        - Linux or mac or WSL:
            ```bash
            pip3 install -r requirements.txt
            ```
        - Windows:
            - **Notice! If you wanna install `psutil` on windows (WSL is not enable) you may get this error:**
            
            *Microsoft Visual C++ 14.0 or greater is required (check and install new version of Microsoft Visual C++)*
            ```bash
            pip install -r requirements.txt
            ```
            - I don't recommend to use it on **cmd** or **powershell**
    2. Run
        - Linux or mac or WSL:
            ```bash
            python3 pacmanfetch.py
            ```

    - Check the switches of pacmanfetch:
    ```bash
    python3 pacmanfetch -h
    ```
    - Get delay:
    ```bash
    # typewriter style
    python3 pacmanfetch -d 10
    ```