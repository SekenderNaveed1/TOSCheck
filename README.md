<p align="center">
  <img src="images/TOSCheck_logo.png" alt="TOSCheck Logo" width="200"/>
</p>

# TOSCheck

TOSCheck exists because reading the Terms of Service is important, and most people simply don’t do it.

I’d been bored for a while and wanted something new to build, but this idea stuck after reading a story about a chess player who won $1000 just by reading the Terms and Conditions that everyone else ignored. It’s a funny story, but also a reminder that nobody actually reads the fine print, even though it quietly decides how companies can use your data and what rights you sign away without realizing it.

TOSCheck is my way of doing something about that. It’s a project meant to actually read what people skip. It scans Terms of Service and Privacy Policies, highlights the parts that stand out, and tries to make sense of the text that’s usually written to be ignored. The goal is to make this process easier, fairer, and a little more honest.

I’ve worked on other projects before, like Equigrade, which tried to make grading fairer in education. It was finished in fall 2023 but never really had any users. By then, LLMs had changed how programming classes worked. Students could use AI to write simple loops or even full assignments, so most professors switched to test-based grading instead.

TOSCheck comes from the same motivation as Equigrade did: wanting to build something that gives people more clarity and control. The difference is that this one is smaller, simpler, and more personal. It’s not about creating something huge, it’s about building something that should have existed already.

And hopefully, unlike Equigrade, TOSCheck actually ends up with a few users who aren’t just me testing it at random hours and pretending I’m doing research.

Most people don’t read the fine print because it’s long, dull, and often written to be unreadable. But the words matter. They always have. This project is a reminder that understanding what you agree to shouldn’t feel impossible.

If this tool helps even one person stop and actually read what they’re signing, I’ll count that as a win. No promises that it’ll help you win any money like that chess story, though.

Also, I bet most of you won’t even read this README, which is kind of funny considering that’s literally the point of this entire project.

And just to set expectations, TOSCheck isn’t really meant for people who haven’t spent time setting up projects, programming, or using GitHub. It’s all CLI for now, and let’s be honest, the command line tends to scare off anyone who isn’t from a CS background. It’s not that it’s hard, it just looks like it is. But it’s 2025, so if typing `python main.py` feels intimidating, an LLM somewhere will probably walk you through it anyway.


---

### Why now
Everyone’s using AI tools, but nobody’s reading the fine print that comes with them.  
New apps, new APIs, new “we value your privacy” pop-ups — all of them say something you probably shouldn’t ignore.  
TOSCheck is just a small push toward paying attention again.

---

### What it might flag

**Input**
> “We may change these terms at any time without notice. We may share your information with partners. Disputes will be handled by binding arbitration.”

**Output**  
Unilateral changes, Data sharing, Arbitration.  
That’s it. Short, direct, and exactly what you need to know.

TOSCheck doesn’t just summarize at random. It uses an LLM (via Ollama or your configured model) to read through the text line by line, score each sentence for keywords and legal patterns, and then cite the lines that triggered a flag.  

It looks for things like:
- **Unilateral authority:** phrases that mean the company can change the rules whenever they want.  
- **Data collection and sharing:** anything involving “third parties,” “partners,” or “affiliates.”  
- **Binding arbitration or waiver of rights:** clauses that remove your ability to sue or join a class action.  
- **Undefined or vague permissions:** lines that say things like “we may use your information for purposes deemed appropriate.”  
- **Opt-out tricks:** sections that technically let you refuse something but hide how.  

When it flags something, TOSCheck shows the reason (like “Data sharing”) and where in the text it found it, so you can read it yourself instead of trusting a summary.  

It doesn’t editorialize or make moral judgments. It just points at the weird parts so you can decide what matters.

---

### Privacy
No uploads, no tracking, no servers.  
TOSCheck runs entirely on your device.  
If you share something by accident, that’s on you, not the app.

---

## For developers

If you’re reading this section, you probably already read the terms before agreeing to GitHub’s API policy. Congratulations — you’re already ahead of 99% of people.  
If you didn’t, that’s fine too. You’ll fit right in here.

## How It Works (Technical Overview)

TOSCheck runs on a local Retrieval-Augmented Generation (RAG) pipeline. It takes a Terms of Service or Privacy Policy, breaks it into meaningful pieces, embeds them, and uses a local model to compare what it finds against known legal risk patterns. Everything happens on your machine.

### 1. Text Extraction and Normalization
You can feed it a raw text file, a PDF, or even a URL. The `read_text()` function handles the cleanup — removing markup, whitespace, and the usual junk that gets in the way — and turns it into clean, readable text ready for analysis.

### 2. Dynamic Clause-Aware Chunking
Instead of cutting the text into random equal pieces, TOSCheck uses a dynamic tokenizer that understands clauses. The algorithm (in `chunk.py`) looks for natural breaks like sentence endings, semicolons, or empty lines. Each chunk usually represents one clause or paragraph, which keeps the meaning intact while still being small enough for embedding.

### 3. Embedding and Vector Indexing
Each chunk is embedded using a local model (`nomic-embed-text` through Ollama). The results are stored in `.ragcache` folders as lightweight JSON files.  
TOSCheck keeps two separate spaces:

**TOS Index (`tos_rag`)** — your document’s embeddings.  
**Knowledge Base Index (`kb_rag`)** — a curated collection of legal patterns like arbitration, data collection, or unilateral changes.

### 4. Retrieval (Step One)
When you analyze a document, each clause is compared to the knowledge base. A cosine similarity search pulls up the most relevant patterns. So if the text says “You waive any right to a jury trial,” it immediately links that to the arbitration category in the KB.

### 5. Contextual Explanation (Step Two)
Each clause and its matched patterns are combined into a structured prompt for your local or remote LLM. The model then:
- Summarizes what the clause actually says in plain English  
- Identifies possible risks or implications  
- Labels it with a category like “Arbitration,” “Data Sharing,” or “Refunds”  
- Optionally adds a severity level or relevant tags

### 6. Dual-RAG Integration
Unlike single-pass systems, TOSCheck runs a dual-RAG setup.  
First it retrieves the most relevant patterns from the knowledge base.  
Then it retrieves supporting evidence from within the same document when multiple clauses talk about the same thing.  
This double grounding keeps explanations accurate and prevents the model from making things up.

### 7. Reporting
The results are saved in Markdown and JSON.  
The Markdown file gives you an easy-to-read summary with highlighted risks and quotes from the text.  
The JSON file is more structured — good if you want to build a UI or another tool around it.

### 8. Fully Local and Privacy-Safe
Everything happens on your computer. No uploads, no tracking, no hidden API calls.  
If you want to use a cloud model, you have to turn it on yourself.  
Otherwise, TOSCheck runs entirely offline, making it safe for private or confidential documents.

## System Flow

TOSCheck works like a conveyor belt: it takes your text in one end and spits out a clear explanation on the other, all without phoning home.

Each run goes through a few key steps:

**Input Layer**  
Takes `.txt`, `.pdf`, or URLs (via `trafilatura`), cleans and normalizes everything for consistent parsing.

**Clause-Aware Chunking**  
Splits the document into logical units instead of random lengths, adapting chunk size to sentence complexity.

**Embedding and Indexing**  
Turns every chunk into a vector embedding using `nomic-embed-text` through Ollama. Stores both the document and the knowledge base embeddings locally.

**Knowledge Base Comparison**  
Matches each clause against predefined legal patterns stored in `rag_patterns/`. Uses cosine similarity to find the closest examples.

**Dual-RAG Reasoning**  
The model looks at both the document and the KB matches at once, explaining why a clause was flagged and what it means.

**Output Generation**  
Creates Markdown and JSON reports with flagged clauses, matched patterns, summaries, risk levels, and confidence scores.

## System Architecture

### TOSCheck System Flowchart
This diagram shows how the whole thing fits together — from text extraction and embedding to pattern matching, reasoning, and report generation.

<p align="center">
  <img src="images/Diagram_for_TOS_Check.png" alt="TOSCheck System Flowchart" width="600"/>
</p>


## Installation & Setup

Alright, let’s get this thing running. TOSCheck is fully local — no cloud, no tracking, no "trust us with your data" nonsense.  
All you need is Python and [Ollama](https://ollama.ai) because we like our models where we can see them — on our own machines.

### 1. Clone the repo
```bash
git clone https://github.com/SekenderNaveed1/TOSCheck.git
cd TOSCheck
```

### 2. Set up your environment
Make a virtual environment (you don’t have to, but it keeps things clean):
```bash
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows
```

Then install everything:
```bash
pip install -r requirements.txt
```

### 3. Install Ollama (the local model thing)
TOSCheck runs best with [Ollama](https://ollama.ai).  
It’s basically your own mini-LLM factory that doesn’t send your data to the cloud. Perfect for people with trust issues (me included).

If you don’t already have it, grab it and pull a model:
```bash
ollama pull llama3
```

**Hardware note (a.k.a. reality check):**  
Run this on a GPU if you can. Seriously.  
If you use your CPU, your laptop might sound like it’s trying to take off — which is fine if you miss flying.  
(I have a love-hate relationship with flights, so hearing my fans spin at Mach 3 is... nostalgic.)

Basically:  
- Gaming laptop or PC = buttery smooth  
- Office laptop or old MacBook = prepare for lift-off

### 4. Set up your `.env`
Make a `.env` file in the project folder and toss this in:
```
MODEL=llama3
EMBED_MODEL=nomic-embed-text
RAG_CACHE_DIR=.ragcache
```

If you want to use a cloud model (no judgment, just side-eye), add:
```
OPENAI_API_KEY=sk-yourkeyhere
```

### 5. Run it
Now the fun part.  
You can throw in a `.txt`, `.pdf`, or even a URL — TOSCheck will read it, break it down, and tell you what’s sketchy.

Example:
```bash
python -m toscheck.app sample.txt
```

It’ll:
1. Read and clean the text  
2. Split it into real clauses (not random tokens like some AI nonsense)  
3. Match clauses against known shady patterns  
4. Tell you what’s weird, in plain English  
5. Save the results for you to read while questioning humanity

You’ll get:
```
report.md
report.json
```

### Example run
```bash
$ python -m toscheck.app sample.txt
[🔍] Analyzing Terms of Service...
Found 3 flagged clauses:
 - "We may change these terms at any time..." → Unilateral Changes
 - "We may share your information with partners." → Data Sharing
 - "Disputes will be handled by binding arbitration." → Arbitration

Report saved to scan_report.md
```

### Reusing cache
TOSCheck caches all your embeddings so you don’t redo the same work twice.  
They live here:
```
.ragcache/
kb_rag/
tos_rag/
```
So if you re-run the same doc, it skips straight to the analysis.  
Basically, it remembers your pain so you don’t have to.

### Cleaning up
If things get messy or you just feel like deleting stuff:
```bash
rm -rf .ragcache kb_rag tos_rag
```

### Where to put this section
You can drop all this right after your "System Flow" or "How It Works (Technical Overview)" part of the README.  
That way it flows naturally — story → tech → how to actually use the damn thing.

That’s it.  
Now go make your computer read the fine print so you don’t have to.



## Design Notes

TOSCheck is completely local — nothing leaves your computer.  
The dynamic chunking system balances accuracy with speed.  
The dual-RAG setup means every result is traceable back to both the original text and a matching legal pattern.  
It’s model-agnostic, so you can run it with any LLM connected through Ollama or your own API endpoint.


## FAQ

**Does this replace a lawyer?**  
No. It just helps you figure out what to ask a lawyer about — assuming you can afford one in this economy.

**Will it make me $1000 for reading terms?**  
Probably not. But it might save you from giving away the rights to your data, your ideas, and your soul. Small wins.

**Why does it run locally?**  
Because privacy tools that phone home are an oxymoron.  
No servers, no telemetry, no “for research purposes” analytics.  
It runs on your machine and stays there. Simple as that.

**Can I run this without knowing how to code?**  
Technically yes, practically no.  
You’ll need to know how to run a Python script.  
But let’s be real — if you found this repo, you can probably type `python -m toscheck.app sample.txt` without having an existential crisis.

**Why the name “TOSCheck”?**  
Because everything else that sounded cooler was taken.  
And because I didn’t want to slap “AI” or “LLM” in the name like it’s a startup pitch deck.  
It’s just a tool that reads the fine print. No buzzwords needed.

**What models does it use?**  
Whatever you point it to.  
You can use a local model through Ollama, or an API one if you’re okay with the cloud.  
TOSCheck doesn’t care — it just reads, embeds, and calls it like it sees it.

**Is this giving me legal advice?**  
Absolutely not.  
It just flags the stuff that looks odd so you can decide what actually matters.  
If you still sign it after seeing “binding arbitration,” that’s between you and your conscience.

**Does it store or send my data anywhere?**  
Nope. Everything happens locally.  
If you accidentally drag in your tax returns, that’s on you, not the app.

**How accurate is it?**  
Pretty solid.  
It’s not perfect, but it catches the big-ticket stuff — arbitration clauses, vague permissions, “we may change these terms at any time,” and the usual data-sharing fine print.  
It’s not GPT-lawyer, but it’s not guessing either.  
I didn’t test it on fancy F1 scores or benchmark datasets or any of that academic stuff yet — this isn’t a paper, it’s a project.  
But on the small set of real-world docs I ran it on, it did surprisingly well.  
Like, “huh, that actually worked” levels of good.

**Why make this at all?**  
Because everyone scrolls through “I agree” like it’s a reflex, and companies count on that.  
And honestly, it’s not just tech terms — people don’t read anything. Like, ever.  
It’s the same energy as when someone gets “finessed” by a car dealership and brags,  
“Bro, I got a good deal — only $400 a month!” and then you find out it’s for 84 months at 12% interest.  
Like, dude… you didn’t get a deal, you got a payment plan for a down payment.  
People just see a small number and stop asking questions. That’s kind of the whole point of this project — to make reading stuff less painful before it bites you.

**Can I contribute?**  
Sure thing.  
Open a pull request, file an issue, or suggest a better name for half the functions.  
If you break something, open an issue and tell me how — I’ll probably thank you for finding it.

**Will this ever have a UI?**  
Maybe.  
Right now it’s command-line only, fast, quiet, and hacker-vibes only.  
If you’re allergic to terminals, just wait. A simple web UI might happen once the core stuff’s bulletproof.

**How long does it take to run?**  
Depends on the model and the length of the doc.  
Usually under a minute unless you’re using a potato, or you decided to run a 175B model on your laptop for science.

**Can I use it at work?**  
If your job lets you use open-source tools, yes.  
If not, maybe read your employer’s tech policy.  
(Yes, that’s irony. You’ll fit right in here.)

**Will it yell at me for not reading the TOS?**  
No. It’ll just quietly judge you. Which somehow hurts more.

**Can I run it on random apps just for fun?**  
Absolutely.  
It’s borderline therapeutic once you start seeing how ridiculous some of these policies are.

**Does it work on Privacy Policies too?**  
Yes, and those are usually where the real nonsense hides.  
Half the time, the Privacy Policy is just a polite way of saying “we sell your data, but nicely.”

**Why is it local and not a web app?**  
Because not everything needs to be SaaS with subscriptions, analytics, and a “Pro” tier.  
You own the tool. You run it when you want. End of story.

**Does this use OpenAI or cloud APIs by default?**  
No. It’s wired for Ollama first.  
If you really want to use a cloud model, you can — just drop your API key in `.env`.  
But it won’t do that unless you tell it to.

**Why not just use ChatGPT for this?**  
You could — but you’d be manually pasting your TOS into a chatbot that saves your data to train more chatbots.  
So yeah, you could… but maybe don’t.

**How big is this thing?**  
Lightweight.  
No massive dependencies, no weird container setup, no Docker hell.  
It’s just Python, a couple folders, and a working Ollama install.

**Can it summarize PDFs too?**  
Yep.  
You can feed it `.txt`, `.pdf`, or even URLs — it’ll clean and normalize everything for you.  
No need for manual copy-pasting chunks of text like it’s 2010.

**Does it have plans for updates?**  
Probably, yeah.  
The plan is to make the reports prettier, maybe build a tiny UI, and add more pattern coverage — like refund policies, hidden subscriptions, or data retention clauses.  
If you’ve got ideas, drop them in Issues.

**Is this one of those “AI-powered startups”?**  
No.  
This isn’t trying to be a company.  
It’s just a project that should have existed already — built because I was tired of nobody reading the fine print.

**What’s the real goal here?**  
Just clarity.  
If one person stops and actually reads before hitting “I agree,” that’s a win.  
If not, well, at least I read the terms this time.



## Final Note

This project isn’t meant to be a big deal. It’s just something small that probably should’ve existed already.  
If it makes even one person stop and read before hitting “I agree,” then it did its job.  
And if not, well, at least this time I read the terms.

Also, yeah — I didn’t on purpose name this some “AI” thing.  
I feel like “AI” gets thrown around way too much right now, and not everything needs that label.  
This isn’t about hype or pretending it’s magic; it’s just about building something that’s useful.  
Testing LLMs literally paid the bills for me my junior year of college, but I still don’t think it’s a solution to everything.  
This is just one small tool that helps make sense of the stuff we all agree to without thinking.

