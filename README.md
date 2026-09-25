# Suckless Tokyo-Night
I really liked the Tokyo-Night preset, but (no shade to the developers or anything) it had a few deficiencies that made it not a viable option for me. So I decided to make my own!
This preset uses Tokyo-Night's colors, but is shaped more like Gruvbox Rainbow. However, it's not just a pallete swap. The big upside with this preset is it's customizability: instead of just giving you a premade .toml, this repository contains a python script that will generate the .toml for you. Because of this, it allows for customizability that you couldn't easily get just by editing the .toml. It allows the definition of custom "segments", which can be reordered and repositioned. The color pallete can also be easily changed, which is something you can easily do in the .toml by adding a pallete, but this program also allows for the addition of new colors if you want to have more segments.

## Usage:
To generate the Suckless Tokyo-Night preset, make sure you have starship installed (this program uses a combination of the bracketed segments and nerd font symbols presets as its base preset, so it requires starship to be installed so it can get those presets), and set up a standard python environment (`py -m venv .venv`, `pip install -r requirements.txt`, etc.). Then, just run generate.py, and it will output the generated .toml to stdout. To apply the config, just run `python generate.py > ~/.config/starship.toml`.

## Customization:
To customize this preset or make your own using this framework, just edit generate.py. It's well commented and relatively short, so that shouldn't be an issue. If you have any problems or don't understand something, feel free to make an issue and I'll do my best to help.
