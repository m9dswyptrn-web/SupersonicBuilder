import os, re, glob, sys
def say(m): print(m)

issues = 0

# Check for heavy images without svg equivalents
pngs = glob.glob("assets/*.png")
svgs = set(os.path.basename(x) for x in glob.glob("assets/*.svg"))
for p in pngs:
    base = os.path.splitext(os.path.basename(p))[0] + ".svg"
    if base not in svgs:
        say(f"⚠️  Consider adding vector version for: {os.path.basename(p)}")

# Basic config presence
yamls = glob.glob("config/*.yaml")
if not yamls:
    say("⚠️  No YAML files in /config")
else:
    say(f"✅ Found {len(yamls)} YAML file(s)")

print("Lint complete.")
