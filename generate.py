import subprocess
import tomlkit
import time
import re
from typing import Any, Dict

# Source: https://github.com/toml-lang/toml/discussions/1011
def merge_dicts(a: Dict[Any, Any], b: Dict[Any, Any]) -> Dict[Any, Any]:
    """Merge two dictionaries recursively.

    If both have the same key and their values are dictionaries, merge them recursively.
    Otherwise, b overrides a.
    """
    result = a.copy()
    for key, b_val in b.items():
        a_val = result.get(key)
        if isinstance(a_val, dict) and isinstance(b_val, dict):
            result[key] = merge_dicts(a_val, b_val)
        else:
            result[key] = b_val
    return result


# Define indices. Not in an enum for ease of use
FG = 0
BG = 1

# Config values
# Use nerd font instead of emojis
USENERDFONT = True
# Have the prompt and the info bar be on separate lines
TWOLINEPROMPT = True

# Get base presets
subprocess.run(["starship", "preset", "nerd-font-symbols", "-o", "./nfs.toml"])
subprocess.run(["starship", "preset", "bracketed-segments", "-o", "./bracketed.toml"])
if(USENERDFONT):
    nfsDict = tomlkit.parse(open("./nfs.toml", "r").read())
else:
    nfsDict = {}
bsDict = tomlkit.parse(open("./bracketed.toml", "r").read())
# Merge base presets
config = merge_dicts(nfsDict, bsDict)

# Define segment colors - first element is fg, second is bg
segmentColors = [
    ("#000000", "#a3aed2"),
    ("#e3e5e5", "#769ff0"),
    ("#769ff0", "#394260"),
    ("#769ff0", "#212736"),
    ("#a0a9cb", "#1d2230")
]

# Define segment contents
# Values starting with $'s are modules, all others are interpreted as plaintext
segmentContents = {
    "info":      ["$username","$hostname"],
    "directory": [],
    "git":       ["$git_branch", "$git_status"],
    "lang":      ["$c", "$cpp", "$rust", "$golang", "$nodejs", "$bun", "$php", "$java", "$kotlin", "$haskell", "$python"],
    "time":      ["$time"],
    "sys-stats": ["$memory_usage", "$jobs", "$battery"],
    "empty":     [],
    "prompt":    ["$directory","$character"]
}
# List of modules that have dynamic colors, and thus should not have an fg style set
dynColorModules = []
# The order of the segments. The list should not be longer than segmentColors
segmentOrder = ["info", "git", "lang", "sys-stats"]
assert len(segmentOrder) <= len(segmentColors)

# Generate format and apply styles
# bracket regex
breg = re.compile(r"\[(.*)\]")
# Initialize the shell format string
shellFormat = f"[]({segmentColors[0][1]})"
for i in range(len(segmentOrder)):
    segment = segmentOrder[i]
    contents = segmentContents[segment]
    colors = segmentColors[i]
    # Loop through segment contents and add them to the format
    for j in range(len(contents)):
        shellFormat += contents[j]
        # Various pieces of logic that apply only to modules
        if(contents[j].startswith("$")):
            # Strip the starting $ to get the module's name
            moduleName = contents[j][1::]

            # Re-enable modules that are disabled by default
            if(moduleName in ["os", "memory_usage", "battery"]):
                config[moduleName]["disabled"] = False

            # Generate the style string. fg is only defined if the module isn't dynamically colored
            if(not moduleName in dynColorModules):
                styleStr = f"fg:{colors[FG]} bg:{colors[BG]}"
            else:
                styleStr = f"bg:{colors[BG]}"

            config[moduleName]["style"] = styleStr

            # Modify the module's format
            try:
                moduleFormat: str = config[moduleName]["format"]
                moduleFormat = moduleFormat.replace("\\[", "").replace("\\]", "")
                moduleFormat = breg.sub(r"[[ \1 ]("+styleStr+")]", moduleFormat)
                config[moduleName]["format"] = moduleFormat.strip()
            except:
                # Apply a format to the directory module, which doesn't have one by default
                if(moduleName=="directory"):
                    config[moduleName]["format"] = "[ $path ]($style)"
                # Gracefully fail if the module doesn't have a format defined
                pass

    # Cap off the segment
    bgStr = f"bg:{segmentColors[i+1][1]}" if i < len(segmentOrder) - 1 else ""
    shellFormat += f"[{'' if i < len(segmentOrder) -1 else ''}](fg:{segmentColors[i][1]} {bgStr})"

# Add the prompt
config["line_break"]["disabled"] = not TWOLINEPROMPT
shellFormat += "$line_break"
for i in range(len(segmentContents["prompt"])):
    shellFormat += segmentContents["prompt"][i]

# Apply the format string
config["format"] = shellFormat

# Output the final config
print(tomlkit.dumps(config))
