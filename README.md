# Quiz Game (HTML/CSS/JS)

Simple static quiz you can run locally. Place your questions into `questions.json`.

Files:
- `index.html` - entry page
- `style.css` - styles
- `app.js` - quiz logic
- `questions.json` - question data (edit this with your quiz from the PDF)

questions.json format:
[
  {
    "question": "Question text",
    "options": [{"text":"A"},{"text":"B"},{"text":"C"}],
    "answer": 0
  }
]

How to run:
Open `index.html` in a browser (double-click or serve the folder). No server is required.

Notes:
- The correct answers are identified by the `answer` index (0-based). In your PDF the highlighted text should be used as the correct option text.
- I can convert the entire PDF into this JSON for you if you want — tell me whether to extract full questions and which parts are the highlighted answers and I'll parse them into `questions.json`.
