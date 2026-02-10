import re
import textwrap

file_path = "Electron for UI Deployments_ Deep Research & Antig.md"

# Define the clean content source (using the structure we verified)
# I will reconstruct the file content programmatically to ensure 100% compliance

header = """# Electron for UI Deployments: Deep Research & Antigravity IDE Integration Analysis

Based on comprehensive research of Electron's official documentation and your
Antigravity IDE framework, I've analyzed Electron as a universally versatile
deployment option for your automation consulting builds.
"""

# ... [I will use a script to read the CLEAN file I created and write it to the DIRTY file]
# This ensures we aren't trying to patch the dirty file, but replacing it with the known-good version.

with open("Electron_Deployment_Research_&_Integration.md", "r", encoding="utf-8") as clean_f:
    content = clean_f.read()

# Additional MD013 Hardening
lines = content.splitlines()
hardened_lines = []

for line in lines:
    # If line is still too long and not a URL/Link
    if len(line) > 80 and "http" not in line and not line.strip().startswith("["):
        # preserve indentation
        indent = len(line) - len(line.lstrip())
        prefix = line[:indent]
        # wrap
        wrapped = textwrap.wrap(line, width=80, break_long_words=False, break_on_hyphens=False)
        # re-apply indent to subsequent lines if needed (simplified)
        hardened_lines.extend(wrapped)
    else:
        hardened_lines.append(line)

final_content = "\n".join(hardened_lines)

with open(file_path, "w", encoding="utf-8") as dirty_f:
    dirty_f.write(final_content)
