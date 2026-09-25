<purpose>
Pairwise "same thing?" checks. Two texts in, a probability out that they refer to the same company, person, or campaign, and a second that they ask for the same deal. For collapsing duplicates before anyone answers twice.
</purpose>

<user-story>
As an operator whose inbox gets the same brand through five agencies, I want the duplicates grouped before drafting, so that one reply and one number go out per brand.
</user-story>

<when-to-use>
- "Are these the same company", "dedupe these", "group by brand"
- Before a drafting pass over a queue
- Matching records across two systems by description rather than by id
</when-to-use>

<context>
@context/install.md
</context>

<references>
@presets/match-entity.json (two noul questions: same_entity, same_ask)
@frameworks/primitives.md
</references>

<steps>

<step name="build_pairs" priority="first">
Candidate pairs, not all pairs. Block first by something cheap (same domain, shared brand word, same week), then build one item per candidate pair with fields `a` and `b`, each a short description: sender, subject, first lines. `_id` is `<idA>__<idB>`. Say how many pairs were built and the cost estimate at roughly 300 tokens each.
</step>

<step name="run">
    python3 <skill-dir>/scripts/jev.py match --preset match-entity --input pairs.json --out match.jsonl
</step>

<step name="cluster">
Treat `same_entity` at or above 0.85 as a link and connect components. Each component is one brand. Inside a component, `same_ask` at or above 0.8 means one reply covers both threads; below that, the same brand wants two different things. Present the groups with their member subjects.
</step>

<step name="report" priority="last">
Show groups of two or more, the singletons count, and the pairs inside the band (0.15 to 0.85) for a person to eyeball. Hand the groups to whatever drafts next, with one representative thread per group.
</step>

</steps>

<output>
- `match.jsonl` with both probabilities per pair
- Groups of matching items, plus the unsure pairs for review
</output>

<acceptance-criteria>
- [ ] Pairs were blocked before matching, not all-against-all
- [ ] Links used the high edge of the band, never 0.5
- [ ] Unsure pairs were surfaced rather than silently split or merged
</acceptance-criteria>
