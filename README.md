<p align="center">
  <img src="images/TOSCheck_logo.png" alt="TOSCheck Logo" width="200"/>
</p>

# TOSCheck

TOSCheck exists because reading the Terms of Service is important, and most people simply don’t do it.

I’d been bored for a while and wanted something new to build, but this idea stuck after reading a story about a chess player who won $1000 just by reading the Terms and Conditions that everyone else ignored. It’s a funny story, but also a reminder that nobody actually reads the fine print, even though it quietly decides how companies can use your data and what rights you sign away without realizing it.

TOSCheck is my way of doing something about that. It scans Terms of Service and Privacy Policies, highlights the parts that stand out, and tries to make sense of the text that’s usually written to be ignored. The goal is to make this process easier, fairer, and a little more honest.

I’ve worked on other projects before, like Equigrade — which tried to make grading fairer in education. It was finished in fall 2023 but never really had any users. By then, LLMs had changed how programming classes worked. Students could use AI to write assignments, so professors switched to test-based grading instead.

TOSCheck comes from the same motivation as Equigrade did: wanting to build something that gives people more clarity and control. The difference is that this one’s smaller, simpler, and more personal. It’s not about creating something huge — it’s about building something that should’ve existed already.

And hopefully, unlike Equigrade, TOSCheck ends up with a few users who aren’t just me at 2 a.m. pretending I’m doing research.

Most people don’t read the fine print because it’s long, dull, and often written to be unreadable. But the words matter. They always have. This project is a reminder that understanding what you agree to shouldn’t feel impossible.

If this tool helps even one person stop and actually read what they’re signing, I’ll count that as a win. No promises that it’ll help you win any money like that chess story, though.

Also, I bet most of you won’t even read this README — which is kind of funny considering that’s literally the point of the entire project.

---

## Why now

Everyone’s using AI tools, but nobody’s reading the fine print that comes with them.  
New apps, new APIs, new “we value your privacy” pop-ups — all of them say something you probably shouldn’t ignore.  
TOSCheck is just a small push toward paying attention again.

---

## What it might flag

**Input:**  
> “We may change these terms at any time without notice. We may share your information with partners. Disputes will be handled by binding arbitration.”

**Output:**  
Unilateral changes, Data sharing, Arbitration.  
Short, direct, and exactly what you need to know.

TOSCheck doesn’t just summarize at random — it uses a local LLM (via Ollama or your configured model) to read the text line by line, score each sentence for legal patterns, and cite the lines that triggered each flag.

It looks for things like:
- Unilateral authority: “we can change this whenever we want”
- Data sharing: “third parties,” “affiliates,” “partners”
- Binding arbitration or waiver of rights
- Vague permissions: “for purposes deemed appropriate”
- Opt-out tricks hidden in the text

It doesn’t editorialize or moralize — it just points at the weird stuff so you can decide what matters.

---

## Privacy

No uploads. No tracking. No servers.  
Everything runs entirely on your machine.  
If you accidentally share something, that’s on you, not the app.

---

## For Developers

If you’re reading this section, you probably already read GitHub’s API Terms before agreeing to them. Congratulations — you’re already ahead of 99% of people.  
If you didn’t, that’s fine too. You’ll fit right in here.

As of right now, I’d recommend this for people who are actually comfortable with the command line and know a bit of coding.  
You don’t need to be a 10x engineer or whatever, but you should at least know how to `cd` into a folder without Googling it.  

## For Developers

If you’re reading this section, you probably already read GitHub’s API Terms before agreeing to them. Congratulations — you’re already ahead of 99% of people.  
If you didn’t, that’s fine too. You’ll fit right in here.

As of right now, I’d recommend this for people who are actually comfortable with the command line and know a bit of coding.  
You don’t need to be some terminal wizard, but you should at least know how to `cd` into a folder without opening Stack Overflow.  

I love people who don’t code (the majority of my friends and family don’t) — seriously — but for your own sanity, this probably isn’t the place to start.  
Everything here is CLI-based for now, and while it’s not *hard*, it definitely *looks* intimidating if you’ve never done it before.  
You can totally figure it out with some patience (and maybe an LLM holding your hand through it), but yeah — this is a dev-friendly zone for now.  
If that changes someday, great. Until then, if the terminal scares you, maybe sit this one out or just hang around for moral support.



---

## How It Works

TOSCheck runs on a local Retrieval-Augmented Generation (RAG) pipeline. It takes a Terms of Service or Privacy Policy, breaks it into meaningful chunks, embeds them, and compares what it finds against a set of known legal risk patterns — all locally.

### 1. Text Extraction and Normalization
Feed it a `.txt`, `.pdf`, or URL. The `read_text()` function cleans it up — removing junk and leaving clean, readable text ready for analysis.

### 2. Clause-Aware Chunking
Instead of cutting text into random lengths, it splits at natural points (periods, semicolons, etc.), keeping meaning intact.

### 3. Embedding and Indexing
Each chunk is embedded locally using `nomic-embed-text` via Ollama. Results go into `.ragcache` — keeping both your TOS embeddings (`tos_rag`) and the legal pattern knowledge base (`kb_rag`).

### 4. Retrieval
Each clause gets matched against known legal patterns via cosine similarity — if it says “You waive any right to a jury trial,” it maps to the Arbitration category instantly.

### 5. Contextual Explanation
The model summarizes each clause, labels risks (“Data Sharing,” “Arbitration,” etc.), and explains them in plain English.

### 6. Dual-RAG Integration
First pass: find legal patterns from the KB.  
Second pass: find supporting context inside the same document.  
That double grounding keeps explanations real and prevents hallucinations.

### 7. Reporting
You get both `report.md` and `report.json` with all flagged clauses, patterns, and summaries.

### 8. Privacy-Safe
No uploads, no hidden calls, no tracking. Runs fully local — or connect your own API key if you want to go cloud.

---

## Installation & Setup

Alright, let’s get this thing running.  
All you need is Python and [Ollama](https://ollama.ai), because we like our models where we can see them — on our own machines.

### 1. Clone the repo
```bash
git clone https://github.com/SekenderNaveed1/TOSCheck.git
cd TOSCheck
```

### 2. Set up your environment
```bash
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

### 3. Install Ollama
TOSCheck runs best with [Ollama](https://ollama.ai) — your own mini LLM factory that keeps everything local.  
Pull a model:
```bash
ollama pull llama3
```

**Hardware tip:** Run it on a GPU if you can.  
If you use your CPU, your laptop might sound like it’s about to take off — which is fine if you miss flying.  
(I have a love-hate relationship with flights, so hearing my fans spin at Mach 3 feels nostalgic.)  

### 4. Create your `.env`
```
MODEL=llama3
EMBED_MODEL=nomic-embed-text
RAG_CACHE_DIR=.ragcache
```
If you want to use a cloud model:
```
OPENAI_API_KEY=sk-yourkeyhere
```

### 5. Run it
```bash
python -m toscheck.app sample.txt
```

It’ll read, clean, chunk, match, and flag — then give you Markdown and JSON reports:
```
report.md
report.json
```

Example output:
```
[🔍] Analyzing Terms of Service...
Found 3 flagged clauses:
 - "We may change these terms at any time..." → Unilateral Changes
 - "We may share your information with partners." → Data Sharing
 - "Disputes will be handled by binding arbitration." → Arbitration
Report saved to scan_report.md
```

TOSCheck caches embeddings in `.ragcache`, so reruns are instant.  
If things get messy:
```bash
rm -rf .ragcache kb_rag tos_rag
```

---

## FAQ

**Does this replace a lawyer?**  
No. It just helps you figure out what to ask a lawyer about — assuming you can afford one.

**Will it make me $1000 for reading terms?**  
Probably not. But it might save you from giving away the rights to your data, your ideas, and your soul.

**Why does it run locally?**  
Because privacy tools that send data away make zero sense.  
No servers, no telemetry, no “research analytics.” Everything stays on your machine.

**Can I run this without knowing how to code?**  
Technically yes, practically no.  
If you can type `python -m toscheck.app sample.txt`, you’re good.

**Why the name “TOSCheck”?**  
Because everything cooler was taken. And I refused to name it something with “AI” in it.

**What models does it use?**  
Whatever you point it to — local via Ollama or API if you’re fancy. It doesn’t care.

**Is this giving me legal advice?**  
Absolutely not. It just flags suspicious stuff so you can decide what actually matters.

**Does it store or send my data anywhere?**  
Nope. Everything happens locally.  
If you drag your tax returns in here, that’s on you.

**How accurate is it?**  
Pretty solid.  
It’s not perfect, but it catches the big-ticket stuff — arbitration, vague language, “we may change these terms,” and data sharing.  
I didn’t test it with F1 scores or benchmarks or any of that academic stuff — this isn’t a paper.  
But on real-world docs? It did surprisingly well. Like “wait, that actually worked” levels of good.

**Why make this at all?**  
Because people scroll through “I agree” like muscle memory, and companies count on that.  
And it’s not just tech — people don’t read anything.  
It’s the same energy as when someone brags, “DUDE, I got a good deal on a 2016 Audi RS4 — only $400 a month!”  
Then you find out it’s for 84 months at 12% interest. You didn’t get a deal. You got a down payment plan.  
People see a small number and stop asking questions — this project exists to make reading the details less painful before it bites you.

**Can I contribute?**  
Sure. PRs, issues, chaos welcome. If you break something, at least tell me how.

**Will this ever have a UI?**  
Maybe. Right now, CLI only — fast, quiet, hacker-core. A web UI might come later.

**Can I use it at work?**  
If your job lets you use open-source, yes. If not, maybe read the tech policy. (See? Reading helps.)

**Will it yell at me for not reading the TOS?**  
No, it’ll just silently judge you. Which hurts more.

**Does it work on Privacy Policies too?**  
Yes. That’s actually where the real chaos hides.

**Does it have plans for updates?**  
Yeah — maybe prettier reports, more pattern types, maybe a UI if I get bored again.

**Is this an “AI startup”?**  
No. It’s not a company. It’s just a project that should’ve existed already.

**What’s the goal?**  
Clarity.  
If one person stops and actually reads before hitting “I agree,” that’s a win.  
If not, at least I read the terms this time.

---

## Final Note

This project isn’t meant to be a big deal. It’s just something small that probably should’ve existed already.  
If it makes even one person stop and read before hitting “I agree,” it did its job.  
And if not, at least this time I read the terms.

Also, yeah I didn’t name this some “AI” thing on purpose.  
“AI” is overhyped and slapped on everything like glitter on a school project.  
This isn’t hype. It’s not pretending to be magic. It’s just a thing that reads the stuff nobody does.  
Testing LLMs literally paid my bills junior year of college, but I still don’t think AI is a solution to everything.  
This is just one small tool that helps make sense of the fine print — because someone had to build it.
