import os
import re


def beautify_ts(filepath):
    """Normalizes XML tags, fixes corrupted entities, and standardizes indentation."""
    # Read the file
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Tags cleanup: < message > -> <message>
    content = re.sub(r"<[ \t]+([a-zA-Z0-9_]+)", r"<\1", content)
    content = re.sub(r"([a-zA-Z0-9_]+)[ \t]+>", r"\1>", content)
    content = re.sub(r"[ \t]+/>", " />", content)

    # 2. Clean broken entities: & amp; -> &amp;
    content = re.sub(r"& amp;", r"&amp;", content)
    content = re.sub(r"& gt;", r"&gt;", content)
    content = re.sub(r"& lt;", r"&lt;", content)
    content = re.sub(r"& quot;", r"&quot;", content)
    content = re.sub(r"& apos;", r"&apos;", content)

    # 3. Clean spaces around = in attributes: line = "39" -> line="39"
    content = re.sub(r'([a-zA-Z0-9_]+)[ \t]*=[ \t]*"', r'\1="', content)

    # 4. Manual indentation and tag cleanup
    lines = content.split("\n")
    new_lines = []
    level = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect context name with trailing space
        line = re.sub(r"<name>(.*)[ ]+</name>", r"<name>\1</name>", line)

        if line.startswith("</"):
            level -= 1

        new_lines.append("    " * max(0, level) + line)

        if (
            line.startswith("<")
            and not line.startswith("</")
            and not line.endswith("/>")
            and "</" not in line
        ):
            # Simple heuristic for opening tags that increase indentation
            tag_name = re.match(r"<([a-zA-Z0-9_]+)", line)
            if tag_name and tag_name.group(1) in ["TS", "context", "message"]:
                level += 1

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if os.path.isfile(arg):
                print(f"Beautifying {arg}...")
                beautify_ts(arg)
    else:
        i18n_dir = "i18n"
        if os.path.isdir(i18n_dir):
            for filename in os.listdir(i18n_dir):
                if filename.endswith(".ts"):
                    print(f"Beautifying {filename}...")
                    beautify_ts(os.path.join(i18n_dir, filename))
        else:
            print("Usage: python3 clean_translations.py [file1.ts ...]")
