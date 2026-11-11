#!/usr/bin/env python3
"""Checks on the skill's own documents: the SKILL.md size limit, local links, and the ladder stated twice."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parent.parent
# After compaction Claude Code re-attaches only the start of an invoked skill: 20,000 characters, counting a
# header that carries the skill's path and not counting frontmatter (probed on 2.1.321; REFERENCE.md, skill size
# and compaction evidence). That leaves about 19,800 for the body at the installed path. Text past the cut is
# gone for the rest of the session, so step detail goes in references/.
SKILL_BODY_CHARS = 19_500
LADDER = re.compile(r"luna `max` → .*? → astra `xhigh`")


def slug(heading):
    heading = re.sub(r"[`*]", "", heading.strip().lower())
    return re.sub(r"[^\w\- ]", "", heading).replace(" ", "-")


class SkillDocsTests(unittest.TestCase):
    def setUp(self):
        self.docs = {path: path.read_text(encoding="utf-8") for path in ROOT.rglob("*.md")}

    def test_skill_md_fits_what_survives_compaction(self):
        frontmatter, body = self.docs[ROOT / "SKILL.md"].removeprefix("---\n").split("\n---\n", 1)
        self.assertIn("name: orchestrator", frontmatter)
        self.assertLess(len(body), SKILL_BODY_CHARS, "move step detail to references/ and add its read trigger to SKILL.md")

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

    def test_the_codex_ladder_reads_the_same_in_both_places(self):
        short = LADDER.findall(self.docs[ROOT / "SKILL.md"])
        full = LADDER.findall(self.docs[ROOT / "references" / "routing.md"])
        self.assertTrue(short and full, "the Codex ladder is stated in SKILL.md (Tiers) and references/routing.md")
        self.assertEqual(short[0], full[0])


if __name__ == "__main__":
    unittest.main()
