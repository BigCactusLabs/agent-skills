#!/usr/bin/env python3
"""Checks on the skill's own documents: frontmatter name and local links."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parent.parent


def slug(heading):
    heading = re.sub(r"[`*]", "", heading.strip().lower())
    return re.sub(r"[^\w\- ]", "", heading).replace(" ", "-")


class SkillDocsTests(unittest.TestCase):
    def setUp(self):
        self.docs = {path: path.read_text(encoding="utf-8") for path in ROOT.rglob("*.md")}

    def test_frontmatter_names_the_skill(self):
        frontmatter = self.docs[ROOT / "SKILL.md"].removeprefix("---\n").split("\n---\n", 1)[0]
        self.assertIn("name: codex-orchestrator", frontmatter)

    def test_local_links_and_anchors_resolve(self):
        anchors = {path: {slug(match) for match in re.findall(r"(?m)^#{1,6} (.+)$", text)}
                   for path, text in self.docs.items()}
        broken = []
        for path, text in self.docs.items():
            for target in re.findall(r"\[[^\]]+\]\(([^)\s]+)\)", text):
                if re.match(r"[a-z]+:", target):
                    continue
                name, _, fragment = target.partition("#")
                linked = (path.parent / name).resolve() if name else path
                if not linked.exists() or (fragment and linked in anchors and fragment not in anchors[linked]):
                    broken.append(f"{path.relative_to(ROOT)}: {target}")
        self.assertEqual(broken, [])


if __name__ == "__main__":
    unittest.main()
