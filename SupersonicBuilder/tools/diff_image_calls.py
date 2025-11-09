import re, os, sys
path = "main.py"
if not os.path.exists(path):
    print("main.py not found")
    sys.exit(0)

src = open(path, "r", encoding="utf-8").read()
suggestions = []
for i, line in enumerate(src.splitlines(), start=1):
    if "Image(" in line and "make_image(" not in line and "make_svg(" not in line:
        suggestions.append((i, line.strip()))

if not suggestions:
    print("✅ No raw Image( calls found, you're good.")
else:
    print("⚠️  Found raw Image( calls. Consider replacing with helper calls:")
    for i, l in suggestions:
        print(f" - L{i}: {l}")
    print("\nExample replacement:")
    print('  img = make_svg("assets/diagram.svg", width=500)  # or make_image(...) for PNG/JPG')
