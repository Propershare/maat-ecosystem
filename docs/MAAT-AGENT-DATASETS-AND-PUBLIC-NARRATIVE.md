# Agent datasets, sovereign stacks, and a public narrative

This note records, in one place, a working line of thought from the lab: what actually matters when you hunt for “agent” training data, how that plugs into MaatLangChain and the MCP spine, and a draft you might use on a surface like Facebook without sounding like a press release written by a model.

## Why trajectory data is not “just more LLM data”

Most open datasets are built for chat: prompt in, answer out. Agents are different. What you want for fine-tuning or for replay in a bench is **trajectories**: ordered steps, tool calls, failures, retries, and what the environment gave back. Without that sequence, you are polishing wording, not teaching a system to **act**. That distinction is the whole game if you mean “expert agents” rather than “expert paragraphs.”

People often share curated lists with names that sound authoritative. Treat them as **leads**, not citations, until you have opened the real model card or license on Hugging Face (or the paper) and confirmed you may use them for your purpose, especially anything commercial. The space moves quickly and second-hand lists recycle names that are wrong, renamed, or gated.

The categories that actually matter map cleanly to what you are building. **Trajectory-style corpora** (multi-step research, PR or coding-agent traces, structured planning scenarios) are the closest thing to “expert behavior in bulk” for seeding skills. **Evaluation corpora** (harm pressure-tests, security-style multi-step tasks) are less often good as **training** gold; they are better as **MaatBench-style gates** so you do not accidentally tune toward the failure modes you are trying to forbid. **General collections** of tool-use and reasoning examples are still useful as raw material if you normalize them into one schema.

None of that replaces your own logs. External datasets are **borrowed skill memory**. Traces from agents that already run on your spine, with tools and memory under Maat, are **internal skill memory**. Long term, the second pile is the one that fits your constitution, your tools, and your failures. Fine-tuning is how you **embody** patterns from both piles; MaatLangChain and gitMaat are how you execute, audit, and decide what gets reinforced.

## How this ties to Maat without MCP becoming the brain

The architecture we have been cleaning up says the same thing in plumbing terms. Contracts and doctrine live in the constitutional layer. Continuity and orchestration live in the MaatLangChain spine. MCP carries capability across clients and hosts; it is not where identity or policy truth should drift. Datasets and LoRA adapters improve the **workers**; they do not replace the spine. When you normalize traces for training, aligning fields later with your **event** and **task** shapes will make replay, benchmarking, and learning rollback honest instead of a pile of JSON that only “looks like” agent data.

## A Facebook-ready post (essay form, human voice)

You can trim or sharpen this for your own tone. It avoids markdown gimmicks and the kind of mechanical section breaks that read as “AI pause.”

OpenClaw landing the way it did, from the open source community, was a real moment. Whether or not you call it the biggest open source launch in history, it is already one of the loudest around **personal AI** that people can actually run and shape. My worry is not that “open source dies.” My worry is that the **center of gravity** moves: fewer people stay dependent on a single closed API when they can own models, tools, memory, and the loops that refine them.

That is the fork I care about. On one side is convenience: a slick product, someone else’s terms, someone else’s memory. On the other is slower work: your stack, your dataset as curriculum, long-horizon memory you operate on while you build. Most folks do not want to zoom out; they want the weekly drop and the meme. Builders already feel the difference—**tool reality**, **trajectories**, **fine-tunes that match how your lab actually behaves**, not how a generic model guesses.

So no, this is not a eulogy for open source. It is a read on what kind of open source wins: the kind that lets a serious operator **compound** instead of rent. Governance still matters—Tehuti Guard and Maat are not optional decoration if you do not want your “sovereign” stack to turn into chaos. Data quality matters. The tooling is here. The next fight is whether you sell your future memory cheap or keep it trainable on your own terms.

## Closing

Keep verifying names and licenses before you name public datasets in a post that might get argued under in the comments. Keep investing in **canonical events** and **internal traces** so your corpus is not only imports from the internet but evidence from your own body. This file is documentation for the lab and for future you, not a promise that every third-party dataset mentioned in passing elsewhere was audited here.

**Last updated:** 2026-04-08 (Tehuti Lab / Imhotep workspace).
