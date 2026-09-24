import subprocess
import tomlkit
import time
import re
from typing import Any, Dict

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


#Define indices. Not in an enum for ease of use
FG = 0
BG = 1

subprocess.run(["starship", "preset", "nerd-font-symbols", "-o", "./nfs.toml"])
subprocess.run(["starship", "preset", "bracketed-segments", "-o", "./bracketed.toml"])

nfsDict = tomlkit.parse(open("./nfs.toml", "r").read())
bsDict = tomlkit.parse(open("./bracketed.toml", "r").read())
#configStr = subprocess.run(["tomlq", "-t", "-s", "'.[0] * .[1]'", "./nfs.toml", "./bracketed.toml"], capture_output=True, text=True).stdout
#print(configStr)
config = merge_dicts(nfsDict, bsDict)
#config = tomlkit.parse(configStr)

segmentColors = {
    "info":      ("#000000", "#a3aed2"),
    "directory": ("#e3e5e5", "#769ff0"),
    "git":       ("#769ff0", "#394260"),
    "lang":      ("#769ff0", "#212736"),
    "time":      ("#a0a9cb", "#1d2230")
}
segmentContents = {
        "info":      ["$username"],
    "directory": [],
    "git":       ["$git_branch", "$git_status"],
    "lang":      ["$c", "$cpp", "$rust", "$golang", "$nodejs", "$bun", "$php", "$java", "$kotlin", "$haskell", "$python"],
    "time":      ["$time"],
    "prompt":    ["$directory","$character"]
}
# List of modules that have dynamic colors, and thus should not have an fg style set
dynColorModules = []
segmentOrder = ["info", "directory", "git", "lang", "time"]

# Generate format and apply styles
breg = re.compile(r"\[(.*)\]")
shellFormat = f"[]({segmentColors[segmentOrder[0]][1]})"
for i in range(len(segmentOrder)):
    segment = segmentOrder[i]
    contents = segmentContents[segment]
    colors = segmentColors[segment]
    for j in range(len(contents)):
        shellFormat += contents[j]
        moduleName = contents[j][1::]
        if(moduleName in ["os"]):
            config[moduleName]["disabled"] = False

        if(not moduleName in dynColorModules):
            styleStr = f"fg:{colors[FG]} bg:{colors[BG]}"
        else:
            styleStr = f"bg:{colors[BG]}"

        config[moduleName]["style"] = styleStr
        try:
            moduleFormat: str = config[moduleName]["format"]
            moduleFormat = moduleFormat.replace("\\[", "").replace("\\]", "")
            moduleFormat = breg.sub(r"[[ \1 ]("+styleStr+")]", moduleFormat)
            config[moduleName]["format"] = moduleFormat
        except:
            if(moduleName=="directory"):
                config[moduleName]["format"] = "[ $path ]($style)"
            pass

    bgStr = f"bg:{segmentColors[segmentOrder[i+1]][1]}" if i < len(segmentOrder) - 1 else ""
    shellFormat += f"[](fg:{segmentColors[segment][1]} {bgStr})"

shellFormat += "$line_break"
for i in range(len(segmentContents["prompt"])):
    shellFormat += segmentContents["prompt"][i]

config["format"] = shellFormat

print(tomlkit.dumps(config))
