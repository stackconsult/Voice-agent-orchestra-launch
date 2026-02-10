
file_path = "/Users/kirtissiemens/Documents/antigravity-playground/Electron for UI Deployments_ Deep Research & Antig.md"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

fixed_lines = []
for i, line in enumerate(lines):
    fixed_lines.append(line)
    
    # Check if this line is a header
    stripped = line.strip()
    if stripped.startswith("#") and i < len(lines) - 1:
        next_line = lines[i+1].strip()
        # If the next line is NOT empty, insert a blank line
        if next_line:
            fixed_lines.append("\n")

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(fixed_lines)
