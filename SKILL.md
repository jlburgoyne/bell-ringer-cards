---
name: bell-ringer-cards
description: Make a set of 20 printable bell ringer cards with a teacher answer key for high school ELA (9th, 10th, and 11th grade; NYS Regents), tagged with NYS Next Generation ELA standards and Regents skills. Use when asked for bell ringers, warm-ups, do-now cards, or skill cards on any ELA skill (grammar, vocabulary, citing evidence, inference, argument, literary techniques).
---

# Bell ringer cards

You're making a set of bell ringer cards for a high school English teacher in New York State. Read `references/teacher-profile.md` first: it has the teacher's grades, which grades share a set, class length, how the cards are printed and used, house rules for written responses and pronoun agreement, and where files live. Everything below applies to every teacher; the profile fills in the local details.

The cards are cut apart and handed out one at a time, so every card has to be right the first time: a card the teacher has to fix or reprint costs more than any other mistake.

## What to deliver

One Word file, built by `scripts/build_cards.py`:

1. **Cards:** 20 cards, 8 to a page, in a grid with dashed cut lines. Each card is headed "Card 7: Colon before a list" (the word Card, its number, and what it practices), then the passage (if any), the task, and the choices (if multiple choice). Standards and Regents tags appear only in the key.
2. **Teacher key:** one table: card, skill and standard (both grade bands, with the plain-language label), Regents tags, answer, and why / what to accept.

Don't lay out the file yourself. Write the set as JSON and run the script; it checks the set and builds the layout. Then send the file, with a sentence or two on what's in it.

## The working folder and the log

The teacher's working folder and the `Bell Ringer Sets` folder are named in the profile.

- **Save every set in `Bell Ringer Sets`** (create it if it's missing), and build with `--log` so the set is recorded in `Bell Ringer Sets/Bell ringer log.csv` (see Step 6). The log is how you know what the teacher has already done; each set's `.json` is saved beside its Word file so it can be reprinted or tweaked later.
- **Read the log before suggesting or planning a set.** Don't repeat a skill from the last four weeks unless the teacher asks for it, and notice gaps ("nothing on argument yet for 10th and 11th"). A date in the Used column means the set was taught.
- **When the teacher says a set was used,** put the date in that set's Used cell. Change nothing else in the log.
- **To reprint or tweak a set,** open its `.json`, make the change, and rebuild without `--log`, so the log doesn't count it twice.
- **If the folder isn't connected** (for example, the teacher is on a phone), build the set as usual, send the file, and say in one sentence that this set isn't in the log.

### Curriculum PDFs

If the profile lists curriculum PDFs, they are teacher's editions, one per unit, in one subfolder per grade. When a set should use a text from what the class is reading, open only that grade's unit. Teacher's edition pages mix the selection with teacher notes and suggested answers: quote only the selection itself, exactly as printed, never the teacher notes.

## Suggesting what to work on

`references/priorities.md` summarizes the teacher's most recent class-level assessment. When the teacher asks what to do next, or the request is broad, read the log first, then suggest two or three options from the priorities for the grade the set is for (for the Regents grades, skills weak in both grades and worth the most on the Regents first; for 9th, skills weak in all sections first), with a short reason for each, and let the teacher choose. These are suggestions: the teacher knows the students better than the test does. Don't bring the data up otherwise, and don't suggest more testing.

## Step 1: Get the request straight

You need four things. Use what the teacher gave you and ask only about what's missing, in one short question at most:

- **The grade.** A set is either for 10th and 11th grade together, or for 9th grade. If the request doesn't say and nothing points to 9th grade, assume 10th and 11th.
- **The skill.** "Commas," "citing evidence," "tone vs. mood." If it's broad ("grammar"), pick a coherent focus and say what you picked.
- **Scaffolding.** Cards are open response by default. Use multiple choice only when the teacher says students are very weak on this skill or asks for scaffolding or multiple choice. It may be wanted on all 20 or only some; if the teacher doesn't say, put it on all 20. If it hasn't come up and `references/priorities.md` shows the skill as very weak, say so in one sentence and offer multiple choice, but leave the decision to the teacher. If the teacher has already said what they want, just do that.
- **The text.** If the teacher names a selection or unit, find it in the curriculum PDFs (see above); if they paste or upload a text, use that. Quote it exactly. Otherwise write short original passages.

## Step 2: Plan the 20 cards

- **Exactly 20 cards.** Always.
- **Build in order.** Start with recognizing the skill, move to using it, end with harder or applied cases.
- **Every card stands alone.** Cards are cut apart and used one at a time, so a card can't point to another card ("Using the sentence from Card 3..."). If two cards use the same passage or sentence, print it on both. The build script stops if a card mentions another card.
- **Reuse a passage across two or three cards** for reading skills, printing it on each: an explicit-evidence card, then an inference card, then a question for further exploration on the same text. The 11-12 version of R1 adds noticing where a text is ambiguous; use that sometimes.
- **Vary the contexts.** Sentences and passages about things 14-to-17-year-olds in the teacher's community know or would find interesting. No two cards should test the same item with different wording.
- **Fit the card.** A card is 4 by 2.4 inches at 10 point. In practice:
  - Open response with a passage: passage up to about 55 words, task up to 2 sentences.
  - Multiple choice with four choices: passage up to about 25 words, or none, and short choices.
  - Multiple choice with two choices: two full sentences are fine.
  The script stops with a message if a card is too long; shorten it and run again.

### Written responses

When cards practice written responses or citing evidence, use the written-response framework named in the profile (RACES in the example profile), with its terms used exactly the way the teacher uses them.

### Multiple choice

- **Reading and vocabulary questions:** four choices, A to D, like Regents Part 1. Wrong answers should be plausible: the kind of mistake a student who half-understands would make, not throwaways.
- **"Which sentence is correct" grammar items:** two choices, A and B, are fine.
- Exactly one choice is correct. Vary which letter it is across the set.

## Step 3: Tag every card

Read `references/standards.md` and `references/regents-vocabulary.md` before tagging.

- **Standard:** give the anchor only (R1, W5, L2). For a 10th and 11th grade set, the key shows it for both grade bands ("9-10R1, 11-12R1: Evidence and inference"); R3 and R7 have different labels in each band, so for those also give `label_band`, the band whose version the card practices. For a 9th grade set, the key shows the 9-10 standard only, and `label_band` isn't needed.
- **Standard for evidence cards:** use R1 when students find, choose, or infer from evidence while reading; use W5 when they write a response that uses evidence (most written-response cards).
- **Regents tags:** tag 9th grade sets too; the skills carry over to the Regents later. Use only the IDs in `regents-vocabulary.md`, and only where the connection is real. Don't invent terms, and don't tag a card just to tag it. Typical tags:
  - Grammar, usage, punctuation: `CC` (Control of Conventions).
  - Citing evidence: `CE`. Add `P1-EVID` when students choose the quote that best supports an idea, `P1` for other Part 1-style reading questions, or `P2-CITE` when citing by source and line number.
  - Claims and counterclaims: `P2-CLAIM`, `P2-COUNTER`.
  - Central idea or theme: `P3-CENTRAL`. A literary technique named on NYSED's Part 3 list (tone, mood, irony, symbolism...): its `WS-` tag.
  - Formal vs. casual wording: `FORMAL`.
  - Vocabulary in context: `P1`.

## Step 4: Write the JSON

```json
{
  "title": "Parallel Structure",
  "grades": "10-11",
  "cards": [
    {
      "focus": "Correlative conjunctions",
      "standard": "L1",
      "regents": ["CC"],
      "prompt": "Choose the sentence with correct parallel structure.",
      "choices": [
        "You can either finish the lab in class or complete it at home.",
        "You can either finish the lab in class or it can be completed at home."
      ],
      "answer": "A",
      "accept": "Both halves after either/or are verb phrases (finish... / complete...)."
    }
  ]
}
```

A complete 20-card set (semicolons and colons, all multiple choice) is in `references/example-set.json`.

Fields for the set:

| Field | Required | What goes in it |
|---|---|---|
| `title` | yes | The skill, as it should appear on the key ("Citing Evidence with RACES"). |
| `grades` | yes | `"10-11"` for a set shared by 10th and 11th grade, or `"9"` for 9th grade. |
| `cards` | yes | The 20 cards. |

Fields for each card:

| Field | Required | What goes in it |
|---|---|---|
| `focus` | yes | A few words naming what this card practices (it follows "Card 7:" on one line, so about 35 characters at most). |
| `standard` | yes | Anchor code: R1 to R9, W1, W2, W5, W7, L1 to L6. |
| `label_band` | R3 and R7, 10th and 11th grade sets only | `"9-10"` or `"11-12"`. |
| `regents` | no | List of Regents IDs. Empty list if none fit. |
| `passage` | no | The text students read. A line break (`\n`) starts a new line on the card: put each labeled part ("Question:", "Student:", "Quote 1:") on its own line. Numbered items like (1), (2) go on their own lines automatically. The card leaves a blank line between the passage and the task. |
| `prompt` | yes | What students do. |
| `choices` | no | 2 to 4 choices, without letters. Leave out for open response. |
| `answer` | yes | For multiple choice, the letter. For fix-it cards, the corrected sentence. For open response, an exemplar answer, about 50 words at most. |
| `accept` | yes | For the teacher: why the answer is right, and for open response, what else to accept. One or two sentences. |

## Step 5: Check before you build

Read every card and its key entry as a careful English teacher would. Fix anything wrong before building. In particular:

- **The answer is right and is the only right answer.** For multiple choice, read each wrong choice and confirm it really is wrong. For fix-it cards, confirm the corrected sentence has no other error.
- **Everything is answerable from the card.** An "explicit" question's answer is stated in the passage. An inference question has clues in the passage that support the exemplar.
- **Terms are used correctly.** A root is not a prefix. Words fit their meaning (an excuse is *incredible*, a listener is *incredulous*). Labels for clauses, phrases, and parts of speech are accurate.
- **Facts in passages are true.** Write passages about real topics accurately. Don't invent statistics, studies, or quotations and present them as real.
- **House rules from the profile are followed,** including the pronoun agreement rule. Teach and key them that way.
- **No leftovers** from drafting: "(Replacement)," "the same sentence from Card 2" when it isn't, numbering gaps, stray formatting marks like "- [ ]" or "**".
- **Grade level:** challenging for the grade the set is for (9th, or 10th and 11th), with nothing that would embarrass a student to read aloud.

## Step 6: Build

```bash
python3 scripts/build_cards.py set.json "<working folder>/Bell Ringer Sets/Bell Ringers - Parallel Structure.docx" --log "<working folder>/Bell Ringer Sets/Bell ringer log.csv"
```

Give the full path to the script if you're not in the skill folder. If it prints "Not built," fix what it lists and run it again; nothing is logged until the build succeeds. Without the working folder connected, leave off `--log`, save the file where the teacher can download it, and send it.

In your reply, keep it short: what the set covers, whether it uses multiple choice, and a reminder that the card pages are the ones to print for students and the key pages are the teacher's.
