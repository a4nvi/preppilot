import { useState, useEffect } from 'react';

const API = import.meta.env.VITE_API_URL || '';
const ring =
  'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#9db8ff]';
const surface = 'rounded-2xl border border-[#243152] bg-[#121a2f] p-6';
const input =
  'w-full rounded-xl border border-[#2c3a5f] bg-[#0c1222] p-3 text-[#e6ecff] placeholder:text-[#6f7fa8] outline-none transition focus:border-[#4f7cff] focus:ring-2 focus:ring-[#4f7cff]/40';
const primary = `rounded-xl bg-[#4f7cff] px-5 py-2.5 font-semibold text-white transition hover:bg-[#6a92ff] active:scale-[.98] disabled:cursor-not-allowed disabled:opacity-40 ${ring}`;
const ghost = `rounded-xl border border-[#2c3a5f] px-5 py-2.5 font-semibold text-[#cdd8ff] transition hover:bg-[#1a2540] disabled:cursor-not-allowed disabled:opacity-40 ${ring}`;
const muted = 'text-[#8fa0c7]';
const errText = 'text-sm text-[#ff9a9a]';
const tone = (v) => (v >= 75 ? '#2dd4bf' : v >= 50 ? '#6a92ff' : '#fbbf24');

async function call(path, { token, body, form } = {}) {
  const res = await fetch(API + path, {
    method: body || form ? 'POST' : 'GET',
    headers: {
      ...(token && { Authorization: 'Bearer ' + token }),
      ...(body && { 'Content-Type': 'application/json' }),
    },
    body: form || (body && JSON.stringify(body)),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || 'Something went wrong. Try again.');
  return data;
}

const Logo = () => (
  <span className="grid h-9 w-9 place-items-center rounded-xl bg-[#4f7cff]" aria-hidden="true">
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="white">
      <path d="M3 11.5 21 3l-6.5 18-3-7.5z" />
    </svg>
  </span>
);

function Gauge({ value }) {
  const [v, setV] = useState(0);
  useEffect(() => {
    const t = setTimeout(() => setV(value), 60);
    return () => clearTimeout(t);
  }, [value]);
  const r = 52,
    c = 2 * Math.PI * r,
    col = tone(value);
  return (
    <div className="relative grid h-44 w-44 shrink-0 place-items-center">
      <svg
        viewBox="0 0 120 120"
        className="absolute inset-0 -rotate-90"
        role="img"
        aria-label={`Match score ${value} percent`}
      >
        <circle
          cx="60"
          cy="60"
          r="58"
          fill="none"
          stroke="#33426b"
          strokeWidth="2"
          strokeDasharray="1 5.1"
        />
        <circle cx="60" cy="60" r={r} fill="none" stroke="#1c2744" strokeWidth="9" />
        <circle
          cx="60"
          cy="60"
          r={r}
          fill="none"
          stroke={col}
          strokeWidth="9"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={c * (1 - v / 100)}
          style={{
            transition: 'stroke-dashoffset 1s ease-out',
            filter: `drop-shadow(0 0 6px ${col}88)`,
          }}
        />
      </svg>
      <div className="text-center">
        <div className="text-4xl font-extrabold" style={{ color: col }}>
          {value}%
        </div>
        <div className={`text-xs ${muted}`}>resume match</div>
      </div>
    </div>
  );
}

const Chips = ({ items, cls }) => (
  <div className="flex flex-wrap gap-2">
    {items.length ? (
      items.map((s) => (
        <span key={s} className={`rounded-full border px-3 py-1 text-sm ${cls}`}>
          {s}
        </span>
      ))
    ) : (
      <span className={`text-sm ${muted}`}>None</span>
    )}
  </div>
);
const good = 'border-[#14584a] bg-[#10372f] text-[#5eead4]';
const gap = 'border-[#5a4513] bg-[#3a2d10] text-[#fbbf24]';

function Auth({ onToken }) {
  const [mode, setMode] = useState('login');
  const [f, setF] = useState({ email: '', password: '' });
  const [err, setErr] = useState('');
  const submit = async (e) => {
    e.preventDefault();
    try {
      onToken((await call('/api/' + mode, { body: f })).token);
    } catch (x) {
      setErr(x.message);
    }
  };
  return (
    <main className="grid min-h-screen place-items-center p-4">
      <form onSubmit={submit} className={`${surface} w-full max-w-sm space-y-4`}>
        <div className="flex items-center gap-3">
          <Logo />
          <h1 className="text-2xl font-extrabold">PrepPilot</h1>
        </div>
        <p className={`text-sm leading-relaxed ${muted}`}>
          Match your resume to a job, then practise the interview.
        </p>
        <input
          className={input}
          type="email"
          placeholder="Email"
          value={f.email}
          onChange={(e) => setF({ ...f, email: e.target.value })}
          required
        />
        <input
          className={input}
          type="password"
          placeholder="Password (6+ characters)"
          value={f.password}
          onChange={(e) => setF({ ...f, password: e.target.value })}
          required
        />
        {err && (
          <p role="alert" className={errText}>
            {err}
          </p>
        )}
        <button className={primary + ' w-full'}>
          {mode === 'login' ? 'Log in' : 'Create account'}
        </button>
        <button
          type="button"
          className={`w-full text-sm ${muted} hover:text-white ${ring}`}
          onClick={() => {
            setMode(mode === 'login' ? 'register' : 'login');
            setErr('');
          }}
        >
          {mode === 'login' ? 'New here? Create an account' : 'Have an account? Log in'}
        </button>
      </form>
    </main>
  );
}

function Analyze({ token, result, onDone, onPractice }) {
  const [file, setFile] = useState(null),
    [jd, setJd] = useState(''),
    [busy, setBusy] = useState(false),
    [err, setErr] = useState('');
  const run = async () => {
    setBusy(true);
    setErr('');
    try {
      const form = new FormData();
      form.append('resume', file);
      form.append('jd', jd);
      onDone(await call('/api/analyze', { token, form }));
    } catch (x) {
      setErr(x.message);
    }
    setBusy(false);
  };
  const download = async () => {
    const r = await fetch(`${API}/api/report/${result.id}`, {
      headers: { Authorization: 'Bearer ' + token },
    });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(await r.blob());
    a.download = `prep-report-${result.id}.txt`;
    a.click();
  };
  return (
    <div className="space-y-5">
      <section className={`${surface} space-y-4`}>
        <label className="block cursor-pointer rounded-xl border border-dashed border-[#3a4a78] p-5 text-center transition hover:border-[#4f7cff] hover:bg-[#162040] has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-[#9db8ff]">
          <input
            className="sr-only"
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files[0])}
          />
          <span className="font-semibold">{file ? file.name : 'Choose your resume (PDF)'}</span>
          <span className={`mt-1 block text-sm ${muted}`}>
            {file ? 'Click to choose a different file' : 'Text-based PDFs only, not scans'}
          </span>
        </label>
        <label className="block text-sm font-semibold">
          Job description
          <textarea
            className={input + ' mt-2 h-44 font-normal'}
            value={jd}
            onChange={(e) => setJd(e.target.value)}
            placeholder="Paste the full job description here"
          />
        </label>
        {err && (
          <p role="alert" className={errText}>
            {err}
          </p>
        )}
        <button className={primary} disabled={!file || !jd.trim() || busy} onClick={run}>
          {busy ? 'Analyzing…' : 'Analyze resume'}
        </button>
      </section>
      {result && (
        <section className={`${surface} flex flex-col gap-6 md:flex-row`}>
          <Gauge value={result.score} />
          <div className="min-w-0 flex-1 space-y-4">
            <div className="space-y-2">
              <h2 className="font-semibold">Skills you have</h2>
              <Chips items={result.matched} cls={good} />
            </div>
            <div className="space-y-2">
              <h2 className="font-semibold">Skills to add</h2>
              <Chips items={result.missing} cls={gap} />
            </div>
            <div className="space-y-2">
              <h2 className="font-semibold">How to improve</h2>
              <p className={`whitespace-pre-line text-sm leading-relaxed ${muted}`}>
                {result.tips}
              </p>
            </div>
            <div className="flex flex-wrap gap-3 pt-1">
              <button className={primary} onClick={onPractice}>
                Practise interview
              </button>
              <button className={ghost} onClick={download}>
                Download report
              </button>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}

function Practice({ token, analysis }) {
  const [qs, setQs] = useState([]),
    [i, setI] = useState(0),
    [ans, setAns] = useState(''),
    [fb, setFb] = useState(null),
    [busy, setBusy] = useState(false),
    [err, setErr] = useState('');
  if (!analysis)
    return (
      <p className={`${surface} ${muted}`}>
        Analyze a resume first to get questions for that role.
      </p>
    );
  const wrap = async (fn) => {
    setBusy(true);
    setErr('');
    try {
      await fn();
    } catch (x) {
      setErr(x.message);
    }
    setBusy(false);
  };
  const load = () =>
    wrap(async () => {
      setQs(
        (await call('/api/questions', { token, body: { analysis_id: analysis.id } })).questions
      );
      setI(0);
      setAns('');
      setFb(null);
    });
  const send = () =>
    wrap(async () =>
      setFb(
        await call('/api/feedback', {
          token,
          body: { analysis_id: analysis.id, question: qs[i].q, answer: ans },
        })
      )
    );
  return (
    <section className={`${surface} space-y-4`}>
      {!qs.length ? (
        <div className="space-y-3">
          <p className={muted}>Get interview questions tailored to this job and your resume.</p>
          <button className={primary} disabled={busy} onClick={load}>
            {busy ? 'Generating…' : 'Generate questions'}
          </button>
        </div>
      ) : (
        <>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="rounded-full bg-[#1c2a52] px-3 py-1 font-semibold text-[#9db8ff]">
                {qs[i].type}
              </span>
              <span className={muted}>
                Question {i + 1} of {qs.length}
              </span>
            </div>
            <div className="h-1.5 rounded-full bg-[#1c2744]">
              <div
                className="h-full rounded-full bg-[#4f7cff] transition-all"
                style={{ width: `${((i + 1) / qs.length) * 100}%` }}
              />
            </div>
          </div>
          <p className="text-xl font-semibold leading-snug">{qs[i].q}</p>
          <textarea
            className={input + ' h-40'}
            value={ans}
            onChange={(e) => setAns(e.target.value)}
            placeholder="Type your answer"
          />
          <div className="flex flex-wrap gap-3">
            <button className={primary} disabled={!ans.trim() || busy} onClick={send}>
              {busy ? 'Evaluating…' : 'Get feedback'}
            </button>
            <button
              className={ghost}
              disabled={i + 1 >= qs.length}
              onClick={() => {
                setI(i + 1);
                setAns('');
                setFb(null);
              }}
            >
              Next question
            </button>
          </div>
          {fb && (
            <div
              className="rounded-xl border border-[#243152] bg-[#0c1222] p-4"
              style={{ borderLeft: `4px solid ${tone(fb.score * 10)}` }}
            >
              <p className="text-lg font-extrabold" style={{ color: tone(fb.score * 10) }}>
                {fb.score}/10
              </p>
              <p className={`mt-1 text-sm leading-relaxed ${muted}`}>{fb.feedback}</p>
            </div>
          )}
        </>
      )}
      {err && (
        <p role="alert" className={errText}>
          {err}
        </p>
      )}
    </section>
  );
}

function History({ token, onPractice }) {
  const [h, setH] = useState(null);
  useEffect(() => {
    call('/api/history', { token })
      .then((d) => setH(d.history))
      .catch(() => setH([]));
  }, [token]);
  if (!h) return <p className={muted}>Loading…</p>;
  if (!h.length)
    return <p className={`${surface} ${muted}`}>No sessions yet. Analyze a resume to start.</p>;
  return (
    <div className="space-y-3">
      {h.map((a) => {
        const avg = a.answers.length
          ? (a.answers.reduce((s, x) => s + x.score, 0) / a.answers.length).toFixed(1)
          : null;
        return (
          <details key={a.id} className={`${surface} group`}>
            <summary
              className={`flex cursor-pointer list-none items-center gap-4 rounded-lg ${ring}`}
            >
              <span
                className="rounded-full px-3 py-1 text-sm font-extrabold"
                style={{ background: tone(a.score) + '22', color: tone(a.score) }}
              >
                {a.score}%
              </span>
              <span className="min-w-0 flex-1">
                <span className="block truncate text-sm font-semibold">{a.jd}</span>
                <span className={`text-xs ${muted}`}>
                  {a.created.slice(0, 10)} ·{' '}
                  {avg ? `avg answer score ${avg}/10` : 'no answers practised'}
                </span>
              </span>
              <span className={`${muted} transition group-open:rotate-180`} aria-hidden="true">
                ▾
              </span>
            </summary>
            <ul className="mt-4 space-y-3 border-t border-[#243152] pt-4 text-sm">
              {a.answers.map((x, k) => (
                <li key={k}>
                  <b>{x.question}</b> <span className="text-[#9db8ff]">({x.score}/10)</span>
                  <p className={`mt-1 ${muted}`}>{x.feedback}</p>
                </li>
              ))}
              {!a.answers.length && (
                <li className={muted}>Nothing practised for this analysis yet.</li>
              )}
            </ul>
            <button className={primary + ' mt-4'} onClick={() => onPractice(a.id)}>
              Practise this job
            </button>
          </details>
        );
      })}
    </div>
  );
}

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('pp_token'));
  const [tab, setTab] = useState('analyze'),
    [result, setResult] = useState(null),
    [active, setActive] = useState(null);
  const save = (t) => {
    t ? localStorage.setItem('pp_token', t) : localStorage.removeItem('pp_token');
    setToken(t);
  };
  if (!token) return <Auth onToken={save} />;
  return (
    <div className="mx-auto max-w-3xl space-y-6 p-4 sm:p-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Logo />
          <h1 className="text-xl font-extrabold">PrepPilot</h1>
        </div>
        <div className="flex items-center gap-3">
          <nav className="flex gap-1 rounded-xl border border-[#243152] bg-[#121a2f] p-1">
            {[
              ['analyze', 'Analyze'],
              ['practice', 'Practise'],
              ['history', 'History'],
            ].map(([k, l]) => (
              <button
                key={k}
                onClick={() => setTab(k)}
                aria-current={tab === k ? 'page' : undefined}
                className={`rounded-lg px-3 py-1.5 text-sm font-semibold transition ${ring} ${tab === k ? 'bg-[#4f7cff] text-white' : `${muted} hover:text-white`}`}
              >
                {l}
              </button>
            ))}
          </nav>
          <button
            className={`text-sm ${muted} hover:text-white ${ring} rounded`}
            onClick={() => save(null)}
          >
            Log out
          </button>
        </div>
      </header>
      {tab === 'analyze' && (
        <Analyze
          token={token}
          result={result}
          onDone={(r) => {
            setResult(r);
            setActive(r.id);
          }}
          onPractice={() => setTab('practice')}
        />
      )}
      {tab === 'practice' && (
        <Practice key={active} token={token} analysis={active && { id: active }} />
      )}
      {tab === 'history' && (
        <History
          token={token}
          onPractice={(id) => {
            setActive(id);
            setTab('practice');
          }}
        />
      )}
    </div>
  );
}
