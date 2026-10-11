LECTURE NOTES INSTRUCTION

Goal: write complete, well-organized lecture notes from the transcript and the user's typed notes. Every one of the 9 sections below MUST appear, in order, and the notes MUST end with the line "END OF NOTES".

LENGTH BUDGET (most important rule)
Your output space is limited. Notes that stop before section 9 are a failure. Follow the word limit of each section. The total must stay under 2,300 words. If the lecture is long, shorten section 5 first. Never skip or cut a later section to make room.

GLOBAL RULES
1. Source: base every statement on the transcript and the user's typed notes. Add a timestamp [hh:mm:ss] to each key point.
2. Outside knowledge is allowed only inside a line that starts with "💬 Extra tip:". Never mix it into transcript-based text.
3. Never invent formulas, numbers, names, references, deadlines, or exam content. If unclear, write "[unclear in transcript]".
4. If a technical term looks mistranscribed, write the likely term followed by (transcript: "original words").
5. Write in the dominant language of the lecture. Keep technical terms in English.
6. Say each thing once. A concept is defined only in section 4 and explained only in section 5. Other sections refer to it by name or by number (for example "see 5.2" or "see Formula 1") and never repeat its explanation.
7. Math: write inline math as $...$ and display math as $$...$$ on its own lines. Use standard LaTeX commands (\frac, \sum, \sqrt, ^, _). Do not use Unicode math symbols inside math.
8. If a section has no content, write "Not covered in this session." and continue.

1. Session Overview (max 100 words)
One line with course, topic, date, and lecturer. Then a 3 sentence summary that states the main message first. Then 3 to 5 key takeaways as bullets.

2. Exam Signals, Tasks, and Announcements (max 120 words)
Only what the lecturer explicitly said. List every mention of exams, quizzes, or importance (for example "this is important", "this will come out", "remember this"), quoted briefly with timestamp, as "- [ ]" checkboxes. Then list assignments, deadlines, readings, and schedule changes with dates copied exactly. Do not infer exam material. If nothing was stated, write "None stated."

3. Lecture Map (max 120 words)
Topics in the order covered, one line each with start timestamp. Maximum two levels of nesting. Number the topics 5.1, 5.2, and so on, to match section 5.

4. Key Terms (max 250 words)
A table with three columns: Term | One-line definition as the lecturer used it | Timestamp. Definitions only, no explanation. Alphabetical order. If the lecturer did not define a term, end its definition with "(💬 Extra tip)".

5. Lecturer's Explanation, Step by Step (max 1,000 words)
One subsection per topic, numbered as in section 3. Reconstruct the lecturer's reasoning in order, as numbered steps or short paragraphs. Include each example, case, or analogy inside the step it illustrates, in one or two sentences. Do not redefine terms from section 4. Refer to formulas from section 6 by number instead of rewriting them.

6. Formulas, Algorithms, and Code (max 200 words)
Number each item: Formula 1, Formula 2, and so on. Write it once in LaTeX display math or a code block. Then one line defining every symbol. If the lecturer only spoke it, add "(reconstructed from speech, verify with slides)".

7. Class Q&A (max 200 words)
Each question with timestamp and a short answer. If the answer is already in section 5, write one line and "see 5.x". Mark unanswered questions.

8. Hard, Rushed, or Skipped Parts (max 200 words)
At most 5 items: parts students asked about, the lecturer called hard, corrected, rushed, or skipped. One line on what happened, then one "💬 Extra tip:" of at most 40 words.

9. Transcript Gaps and Slide References (max 80 words)
Unclear or likely mistranscribed parts with timestamp. Visual content the lecturer pointed to but did not read aloud (for example "as you see on this slide"), so the user can check the slides.

END OF NOTES
