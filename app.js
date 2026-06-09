// Quiz app with updated layout
const DATA_URL = 'questions.json';

let questions = [];
let current = 0;
const answers = new Map();

const quizArea = document.getElementById('quiz-area');
const questionTitle = document.getElementById('questionTitle');
const totalQEl = document.getElementById('totalQ');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const submitBtn = document.getElementById('submitBtn');
const resultModal = document.getElementById('result');
const scoreText = document.getElementById('scoreText');
const wrongList = document.getElementById('wrongList');
const retryBtn = document.getElementById('retryBtn');
const reviewBtn = document.getElementById('reviewBtn');
const restartBtn = document.getElementById('restartBtn');
const questionsGrid = document.getElementById('questions-grid');

function fetchQuestions(){
  return fetch(DATA_URL).then(r=>r.json());
}

function updateGridButtons(){
  const btns = document.querySelectorAll('.q-btn');
  btns.forEach((btn, idx)=>{
    btn.classList.remove('active', 'answered', 'wrong');
    if(idx === current) btn.classList.add('active');
    if(answers.has(idx)){
      btn.classList.add('answered');
      // Mark as wrong if incorrect
      if(answers.get(idx) !== questions[idx].answer){
        btn.classList.add('wrong');
      }
    }
  });
}

function renderGrid(){
  questionsGrid.innerHTML = '';
  questions.forEach((q, idx)=>{
    const btn = document.createElement('button');
    btn.className = 'q-btn';
    btn.textContent = idx + 1;
    if(idx === current) btn.classList.add('active');
    if(answers.has(idx)){
      btn.classList.add('answered');
      if(answers.get(idx) !== q.answer) btn.classList.add('wrong');
    }
    btn.addEventListener('click', ()=>{
      current = idx;
      render();
      updateGridButtons();
    });
    questionsGrid.appendChild(btn);
  });
}

function render(){
  const q = questions[current];
  questionTitle.textContent = `Câu ${current + 1} / ${questions.length}`;
  totalQEl.textContent = questions.length;
  quizArea.innerHTML = '';

  const container = document.createElement('div');

  const title = document.createElement('h2');
  // Render question: if it contains code-like patterns, split prefix (Vietnamese) and code part
  function looksLikeCode(s){
    if(!s) return false;
    const codeHints = ['#include', 'cout', 'cin', '->', '::', '{', '}', ';', 'int ', 'float ', 'return ', 'printf', 'scanf', 'using namespace', 'cout <<', 'std::'];
    return codeHints.some(h=> s.indexOf(h) !== -1) || /\bfor\b|\bwhile\b|\bif\b/.test(s);
  }

  if(looksLikeCode(q.question)){
    // find first hint index to split human text and code
    const hints = ['#include','using namespace','int main','cout','cin','return',';','{','}'];
    let idx = -1;
    for(const h of hints){
      const i = q.question.indexOf(h);
      if(i>=0 && (idx === -1 || i < idx)) idx = i;
    }
    let prefix = '';
    let codePart = q.question;
    if(idx > 0){
      prefix = q.question.slice(0, idx).trim();
      codePart = q.question.slice(idx).trim();
    }

    if(prefix){
      const p = document.createElement('div');
      p.innerHTML = prefix;
      title.appendChild(p);
    }

    const pre = document.createElement('pre');
    pre.className = 'code-block';
    const code = document.createElement('code');
    // try to make code readable by adding newlines after semicolons and around braces
    let text = codePart.replace(/\\n/g,'\n');
    text = text.replace(/;\s*/g, ';\n');
    text = text.replace(/\{\s*/g, '{\n');
    text = text.replace(/\s*\}/g, '\n}\n');
    text = text.replace(/using namespace/g, '\nusing namespace');
    text = text.replace(/#include\s*/g, '#include ');
    // ensure trimmed
    text = text.replace(/\n{2,}/g,'\n');
    code.textContent = text.trim();
    pre.appendChild(code);
    title.appendChild(pre);
  } else {
    title.innerHTML = q.question;
  }
  container.appendChild(title);

  const opts = document.createElement('div');
  opts.className = 'options';

  q.options.forEach((opt, i) =>{
    const el = document.createElement('label');
    el.className = 'option';
    if(answers.get(current)===i) el.classList.add('selected');

    const radio = document.createElement('input');
    radio.type = 'radio';
    radio.name = 'opt';
    radio.checked = answers.get(current)===i;
    radio.addEventListener('change', ()=>{
      answers.set(current, i);
      document.querySelectorAll('.option').forEach(o=>o.classList.remove('selected'));
      el.classList.add('selected');
      updateGridButtons();
      if(current === questions.length-1) submitBtn.style.display = 'inline-block';
      // Immediate feedback: mark options correct/wrong and show explanation
      showImmediateFeedback(q, i, opts);
    });

    const letter = document.createElement('div');
    letter.className = 'option-letter';
    letter.textContent = String.fromCharCode(65 + i);

    const spanLabel = document.createElement('div');
    spanLabel.className = 'label';
    // Keep option text unchanged (plain text/HTML)
    spanLabel.innerHTML = opt.text;

    el.appendChild(radio);
    el.appendChild(letter);
    el.appendChild(spanLabel);
    opts.appendChild(el);
  });

  container.appendChild(opts);
  // Feedback area (hidden until selection)
  const feedback = document.createElement('div');
  feedback.className = 'immediate-feedback';
  feedback.style.marginTop = '12px';
  container.appendChild(feedback);
  quizArea.appendChild(container);

  prevBtn.disabled = current === 0;
  nextBtn.disabled = current === questions.length-1;
  submitBtn.style.display = current === questions.length-1 ? 'inline-block' : 'none';
}

function showImmediateFeedback(q, givenIndex, optsContainer){
  // Remove existing feedback highlights
  const optionEls = optsContainer.querySelectorAll('.option');
  optionEls.forEach((el, idx)=>{
    el.classList.remove('correct','incorrect');
    // append note area removal if exists
    const note = el.querySelector('.feedback-note');
    if(note) note.remove();
  });

  // Mark correct option
  const correctIdx = q.answer;
  if(optionEls[correctIdx]) optionEls[correctIdx].classList.add('correct');

  // If user selected wrong option, mark it
  if(givenIndex != null && givenIndex !== correctIdx){
    if(optionEls[givenIndex]) optionEls[givenIndex].classList.add('incorrect');
  }

  // Build explanation text
  let explanationText = '';
  if(q.explanation){
    explanationText = q.explanation;
  } else {
    // Default explanation: show which letter is correct and the text
    const letter = String.fromCharCode(65 + correctIdx);
    const ansText = q.options[correctIdx] ? q.options[correctIdx].text : '';
    explanationText = `Đáp án đúng: ${letter}. ${ansText}`;
  }

  // Show a shared feedback area beneath options
  const shared = optsContainer.parentElement.querySelector('.immediate-feedback');
  if(shared){
    shared.innerHTML = '';
    const box = document.createElement('div');
    box.style.padding = '10px';
    box.style.border = '1px solid #e0e0e0';
    box.style.borderRadius = '8px';
    box.style.background = '#fff8e1';

    const title = document.createElement('div');
    title.style.fontWeight = 'bold';
    title.style.marginBottom = '6px';
    if(givenIndex === correctIdx){
      title.textContent = 'Bạn chọn đúng ✔️';
      title.style.color = 'var(--success)';
    } else {
      title.textContent = 'Bạn chọn sai ✖️';
      title.style.color = 'var(--error)';
    }

    const text = document.createElement('div');
    text.innerHTML = explanationText;

    box.appendChild(title);
    box.appendChild(text);
    shared.appendChild(box);
  }
}

function showResult(){
  let correct = 0;
  const wrong = [];
  questions.forEach((q, idx)=>{
    const ans = answers.get(idx);
    if(ans === q.answer) correct++;
    else wrong.push({idx, q, given: ans});
  });

  scoreText.textContent = `Bạn đạt: ${correct} / ${questions.length}`;
  wrongList.innerHTML = '';
  if(wrong.length===0){
    wrongList.innerHTML = '<p style="color:#4caf50;font-weight:bold">✓ Chúc mừng! Không có câu sai.</p>';
  } else {
    wrong.forEach(w=>{
      const d = document.createElement('div');
      d.className = 'wrong-item';
      const qn = document.createElement('div');
      qn.innerHTML = `<strong>Câu ${w.idx+1}:</strong> ${w.q.question}`;
      const your = document.createElement('div');
      your.innerHTML = `<strong>Bạn chọn:</strong> ${w.given!=null? w.q.options[w.given].text : '<span style="color:#f44336">(Không chọn)</span>'}`;
      const correct = document.createElement('div');
      correct.innerHTML = `<strong style="color:#4caf50">Đáp án đúng:</strong> ${w.q.options[w.q.answer].text}`;
      d.appendChild(qn);
      d.appendChild(your);
      d.appendChild(correct);
      wrongList.appendChild(d);
    });
  }

  resultModal.style.display = 'flex';
}

function reset(){
  answers.clear();
  current = 0;
  resultModal.style.display = 'none';
  render();
  renderGrid();
}

prevBtn.addEventListener('click', ()=>{
  if(current>0){ current--; render(); updateGridButtons(); }
});
nextBtn.addEventListener('click', ()=>{
  if(current<questions.length-1){ current++; render(); updateGridButtons(); }
});
submitBtn.addEventListener('click', ()=>{
  showResult();
});
retryBtn.addEventListener('click', ()=>{
  reset();
});
restartBtn.addEventListener('click', ()=>{
  reset();
});
reviewBtn.addEventListener('click', ()=>{
  resultModal.style.display = 'none';
  const firstWrong = questions.findIndex((q,idx)=> answers.get(idx)!==q.answer);
  if(firstWrong>=0){ current = firstWrong; render(); updateGridButtons(); }
});

fetchQuestions().then(data=>{
  questions = data;
  if(!questions || questions.length===0){
    quizArea.innerHTML = '<p>Không có câu hỏi. Hãy cập nhật file <code>questions.json</code> với dữ liệu từ PDF.</p>';
    return;
  }
  render();
  renderGrid();
}).catch(err=>{
  quizArea.innerHTML = '<p>Lỗi khi tải câu hỏi: '+err.message+'</p>';
});
