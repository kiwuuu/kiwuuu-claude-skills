# Skill Router

The routing map for every skill in this library. Claude reads this to pick the right skill *and* the right workflow inside it, without loading each `SKILL.md` first.

The index, route table, and health report below are generated from the skills themselves. Regenerate after adding or editing a skill:

```bash
python3 scripts/build_router.py skills/ --out ROUTER.md
```

Everything outside the `BEGIN/END GENERATED` markers is hand-written and survives regeneration.

---

## How routing actually works

Claude only sees **`name` + `description`** from each skill's YAML frontmatter at startup — roughly 100 tokens per skill. The body loads only after the skill is picked; bundled files load only when read.

Two consequences that shape everything here:

1. **Trigger keywords must live inside `description`.** A separate `keywords:` YAML field is never read at selection time. Every keyword below is also present in the skill's real `description`, which is what makes it fire.
2. **This file is the second layer.** With 92 skills, descriptions collide constantly. The hand-written sections below resolve the collisions and encode the chains — the judgment a generator can't extract.

The `route` skill is this file's runtime counterpart: it's the pre-flight picker that reads the installed-skills list when a task is complex. When `route` runs, it should consult this file — `route` decides *per task*, ROUTER.md records *the standing rules*.

---

<!-- BEGIN GENERATED -->

## Skill index (92 skills)

### `algorithmic-art`

Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. Use this when users request creating art using code, generative art, algorithmic art, flow fields, or particle systems. Create original algorithmic art rather than copying existing artists' work to avoid copyright violations.

### `brand-guidelines`

Applies Anthropic's official brand colors and typography to any sort of artifact that may benefit from having Anthropic's look-and-feel. Use it when brand colors or style guidelines, visual formatting, or company design standards apply.

### `canvas-design`

Create beautiful visual art in .png and .pdf documents using design philosophy. You should use this skill when the user asks to create a poster, piece of art, design, or other static piece. Create original visual designs, never copying existing artists' work to avoid copyright violations.

### `character-animation-qa`

Review and QA character animation output: schema checks, Playwright browser previews, frame sampling, and FFmpeg/ffprobe checks on final renders.

### `character-rigging`

Build data-driven 2D character rigs for local animation: parts, pivots, layers, constraints, views, and reusable rig packages.

### `churn-prevention`

When the user wants to reduce churn, build cancellation flows, set up save offers, recover failed payments, or implement retention strategies. Also use when the user mentions 'churn,' 'cancel flow,' 'offboarding,' 'save offer,' 'dunning,' 'failed payment recovery,' 'win-back,' 'retention,' 'exit survey,' 'pause subscription,' 'involuntary churn,' 'people keep canceling,' 'churn rate is too high,' 'how do I keep users,' or 'customers are leaving.' Use this whenever someone is losing subscribers or wants to build systems to prevent it. For post-cancel win-back email sequences, see emails. For in-app upgrade paywalls, see paywalls.

### `cold-email`

Write B2B cold emails and follow-up sequences that get replies. Use when the user wants to write cold outreach emails, prospecting emails, cold email campaigns, sales development emails, or SDR emails. Also use when the user mentions "cold outreach," "prospecting email," "outbound email," "email to leads," "reach out to prospects," "sales email," "follow-up email sequence," "nobody's replying to my emails," or "how do I write a cold email." Covers subject lines, opening lines, body copy, CTAs, personalization, and multi-touch follow-up sequences. For warm/lifecycle email sequences, see emails. For sales collateral beyond emails, see sales-enablement.

### `cold-outreach`

B2B cold outreach for SaaS founders. USE WHEN writing cold email sequences, LinkedIn outreach, WhatsApp business prospecting, or building a first-customer pipeline. Covers ICP targeting, personalization frameworks, sequence structure, follow-up cadence, and reply handling for AI/SaaS products.

### `competitor-intel`

Competitive intelligence for SaaS positioning. USE WHEN analyzing competitors, tracking moves, finding differentiation gaps, preparing for sales objections, or doing positioning work. Covers the WhatsApp AI/chatbot competitive landscape, pricing intelligence, feature gap analysis, and win/loss patterns.

### `content-factory` — 1.0.0 · production

Social content production pipeline: pillar-weighted LLM generation, FLUX images and LTX cinematic video via fal.ai, ffmpeg text-overlay and ElevenLabs voiceover video, a 1-10 quality gate, and rate-limited posting to X, LinkedIn, Instagram and TikTok. Writes to a SQLite queue, spends API credits, and publishes publicly — confirm before running generate, run_due, or run_slot.

- `Workflows/Generate.md` — Step-by-step execution of the full content creation cycle: brief → generation → quality gate → queue.
- `Workflows/Report.md` — Check pipeline status, diagnose failures, and pull engagement data.

### `cro`

When the user wants to optimize, improve, or increase conversions on any marketing page or form — including homepage, landing pages, pricing pages, feature pages, lead capture forms, or contact forms. Also use when the user says 'CRO,' 'conversion rate optimization,' 'this page isn't converting,' 'improve conversions,' 'why isn't this page working,' 'my landing page sucks,' 'form abandonment,' 'nobody's converting,' 'low conversion rate,' or 'this page needs work.' Use this even if the user just shares a URL and asks for feedback. For signup/registration flows, see signup. For post-signup activation, see onboarding. For popups/modals, see popups.

### `dispatching-kiwuuu-squad`

Use when a Kiwuuu task spans 3+ files or 2+ subsystems (souls audit, landing batch, multi-tenant migration, content factory). Splits work into independent units, fans out parallel Task sub-agents with explicit deliverable contracts, then runs one synthesizer to merge results and log to the ops log (PHONE_LOG.md — resolve its location per the Ops log section; machine-dependent). Compresses 30-min serial passes into ~5-min parallel ones.

### `doc-coauthoring`

Guide users through a structured workflow for co-authoring documentation. Use when user wants to write documentation, proposals, technical specs, decision docs, or similar structured content. This workflow helps users efficiently transfer context, refine content through iteration, and verify the doc works for readers. Trigger when user mentions writing docs, creating proposals, drafting specs, or similar documentation tasks.

### `docx`

Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files). Triggers include: any mention of "Word doc", "word document", ".docx", or requests to produce professional documents with formatting like tables of contents, headings, page numbers, or letterheads. Also use when extracting or reorganizing content from .docx files, inserting or replacing images in documents, performing find-and-replace in Word files, working with tracked changes or comments, or converting content into a polished Word document. If the user asks for a "report", "memo", "letter", "template", or similar deliverable as a Word or .docx file, use this skill. Do NOT use for PDFs, spreadsheets, Google Docs, or general coding tasks unrelated to document generation.

### `dub-co`

Link management and attribution for Kiwuuu. USE WHEN creating short links, tracking UTM campaigns, managing branded links, pulling click analytics, or building attribution reports. Requires DUB_API_KEY in environment.

### `fabric`

Intelligent prompt pattern system with 240+ specialized patterns for content analysis, extraction, and transformation. USE WHEN user says 'use fabric', 'fabric pattern', 'run fabric', 'update fabric', 'update patterns', 'sync fabric', 'extract wisdom', 'summarize with fabric', 'create threat model', 'analyze with fabric', OR any request to apply Fabric patterns to content.

- `Workflows/ExecutePattern.md` — Execute Fabric patterns natively without spawning the fabric CLI. Patterns are applied directly from local storage for faster, more integrated execution.
- `Workflows/UpdatePatterns.md` — Update Fabric patterns from the upstream repository to keep patterns current with latest improvements and additions.

### `frontend-design`

Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters, or applications (examples include websites, landing pages, dashboards, React components, HTML/CSS layouts, or when styling/beautifying any web UI). Generates creative, polished code and UI design that avoids generic AI aesthetics.

### `general-video`

Author or edit a custom HyperFrames composition when no specialized workflow fits, or when BRIEF.md sets flow: companion. Use for longer or multi-scene pieces, brand and sizzle reels, montages, static loops, static title cards, footage remixes, and freeform builds. Use motion-graphics instead for a short unnarrated motion-first unit, including an animated title. Route fresh creation through hyperframes before using this skill.

### `humanizer`

Remove signs of AI-generated writing from text. Use when editing or reviewing text to make it sound more natural and human-written. Based on Wikipedia's comprehensive "Signs of AI writing" guide. Detects and fixes patterns including: inflated symbolism, promotional language, superficial -ing analyses, vague attributions, em dash overuse, rule of three, AI vocabulary words, passive voice, negative parallelisms, and filler phrases.

### `hyperframes`

Mandatory entry point: read this first for any request to make, create, edit, animate, or render a video, animation, or motion graphic, including a promo, explainer, captioned clip, title card, overlay, slideshow or interactive deck, Remotion port, or any HyperFrames HTML composition. Also use it to inspect, diagnose, validate, preview, publish, or batch-render an existing HyperFrames project. Inputs may be a website URL, GitHub PR, Figma design or URL, text or brief, existing footage, or music. It resumes project state, captures intent when applicable, selects and installs the owning workflow, and routes domain capabilities. HyperFrames is the default output framework unless the user explicitly chooses another framework for the deliverable or asks only to record a browser session.

### `hyperframes-animation`

All animation knowledge for HyperFrames — atomic motion rules, multi-phase scene blueprints, scene transitions, broader motion-design techniques, AND the seven runtime adapters (GSAP default, plus Lottie, Three.js, Anime.js, CSS keyframes, Web Animations API, TypeGPU). Use for any motion or animation task: pick 2-4 rules and compose, or load a blueprint, or look up runtime-specific API (e.g. GSAP eases / Lottie player / Three.js mixer). Also covers auditing an existing composition's choreography (animation map) and 24 named text-animation effects. HyperFrames-native: single paused timeline, seek-safe, deterministic.

### `hyperframes-cli`

Use the HyperFrames CLI development loop: init, add, catalog, capture, lint, check, snapshot, compare, grade-compare, preview, play, present, beats, keyframes, single or batch render, publish, cloud, cloudrun, feedback, lambda, doctor, browser, info, upgrade, skills, compositions, docs, benchmark, telemetry, transcribe, auth, tts, and remove-background. Also use when diagnosing build or render failures. validate, inspect, and layout are deprecated aliases; use check. Covers local, HeyGen-hosted cloud, AWS Lambda, and Google Cloud Run rendering.

### `hyperframes-core`

The HyperFrames composition contract — build one renderable project. Use for composition structure, the `data-*` timing attributes, `class="clip"`, tracks, sub-compositions, variables, framework-owned media playback, deterministic-render rules, and validation. Also covers Tailwind projects and the STORYBOARD.md / SCRIPT.md plan formats. Read before writing composition HTML.

### `hyperframes-creative`

Non-animation creative direction for HyperFrames videos. Use for design spec (frame.md / design.md) handling, palettes, typography, narration, beat planning, audio-reactive visuals, composition patterns, and brand / style decisions. For atomic motion patterns and scene blueprints, use `hyperframes-animation`.

### `hyperframes-keyframes`

Use when a HyperFrames composition needs seek-safe 2D/3D keyframes, GSAP timelines, CSS keyframes, Anime.js, WAAPI, FLIP, paths, masks, SVG morph/draw, text trails, 3D depth, or `hyperframes keyframes` diagnostics. Don't use for broad scene strategy, brand design, media sourcing, captions, or general video planning.

### `hyperframes-media`

Audio and media assets for HyperFrames compositions, produced by one shared audio engine (`scripts/audio.mjs`) — multi-provider TTS (HeyGen / ElevenLabs / Kokoro local), background music + sound effects (HeyGen audio-library retrieval by default, with local Lyria / MusicGen BGM generation and a bundled SFX library as the no-credential fallback), Whisper transcription, background removal, and caption authoring. Use for voiceover / TTS, BGM, SFX / sound effects, transcription, captions / subtitles / lyrics / karaoke / per-word styling, voice + provider selection, and music-mood prompting.

### `hyperframes-registry`

Install, discover, and wire registry blocks and components into HyperFrames compositions. Use when running hyperframes add or hyperframes catalog, installing one item or every block matching a tag, wiring an installed item into index.html, or working with hyperframes.json. Covers discovery, install locations, block sub-composition wiring, component snippet merging, and authoring a new block or component to contribute upstream (idea → scaffold → validate → PR).

### `internal-comms`

A set of resources to help me write all kinds of internal communications, using the formats that my company likes to use. Claude should use this skill whenever asked to write some sort of internal communications (status reports, leadership updates, 3P updates, company newsletters, FAQs, incident reports, project updates, etc.).

### `kallaway-method`

The Kallaway short-form doctrine — hooks, re-hooks, story arc, script order, packaging, idea mining, and the comment-keyword lead machine, reverse-engineered from 53 TikToks + 35 YouTube videos. USE WHEN writing any hook, script, caption, carousel, video plan, or social post; when a video underperforms and you need a diagnosis; when picking what to make next; or when the user says "hook", "re-hook", "retention", "script structure", "why did this flop", "kallaway". Calls kiwuuu-brand-voice, kiwuuu-analyze, kiwuuu-carousel, kiwuuu-video-factory and kiwuuu-youtube-director as the execution layer.

### `kiwuuu-analyze`

Reverse-engineer any social video (TikTok/Reel/Short/YouTube) into a replicable viral breakdown — hook, story structure, CTA, on-screen text — and batch-synthesize trends across many. USE WHEN the user pastes a video URL and asks to analyze/break down/"what makes it work"/study a competitor, do content research, or find what's trending. Supadata-first (transcript from URL, no download); pulls frames only when the payload is on-screen.

### `kiwuuu-brand-voice`

Apply Kiwuuu and TraficShop brand voice rules — Pragmatic Futurist tone, direct/confident/no-fluff style — to any public-facing copy. Use when writing social posts, website copy, emails, ads, product descriptions, or when the user says "brand voice", "on-brand", or "in our style".

### `kiwuuu-business`

Business advisory for Kiwu, solo founder of Kiwuuu (Belgrade) - covers finance/runway (CFO lens), structured decisions with reversibility scoring, weekly and quarterly reviews, and founder-bottleneck coaching. Use when the user asks for business advice, a decision framework, a weekly/quarterly review, runway or unit-economics math, or says CFO, decide, review the business, am I the bottleneck.

### `kiwuuu-carousel`

Produces TikTok/IG photo-mode carousel posts (10-12 slides) in the proven save-bait listicle format — hook slide, numbered item slides with "START WITH" action pills, save-CTA closer — styled per Kiwuuu channel brand. Use when the user asks for a carousel, slide post, photo-mode post, listicle post, or a zero-video content drop for Absurdity/REKT/BLACK BOX/THE MACHINE or Kiwuuu main.

### `kiwuuu-competitor-scraper`

Scrape WhatsApp BSP and AI agent competitor websites every 24h, diff against yesterday, and emit a content brief JSON/MD that the kiwuuu-video-factory and content-factory skills can consume. USE WHEN the user asks to "check what competitors are doing", "run the competitor scrape", "produce a competitive content brief", or wants a daily digest of pricing/positioning moves at ManyChat, Wati, Respond.io, Tidio, Trengo, Sintra, Lindy, Sierra, AiSensy, Chatarmin. Output lands in {data,briefs}/ next to the skill (deploy target: T1 cron — historical data archived in _quarantine/competitor-scraper-data/).

- `Workflows/Daily.md` — End-to-end: scrape 10 competitors → diff vs yesterday → produce a content brief. Target wall-clock: ~3 minutes.

### `kiwuuu-debate`

Runs multi-perspective deliberation for Kiwuuu decisions in one of three modes - council (collaborative 5-voice debate), adversarial (steelman + counter-argument stress test), or peer (agents challenge each other directly). Use when the user says council, debate, red team, stress test, poke holes, perspectives, or when a strategic/architectural decision needs structured challenge before commitment.

- `Workflows/Debate.md` — Full structured multi-agent debate with 3 rounds and visible transcript.
- `Workflows/Quick.md` — Fast single-round perspective check. Use for sanity checks and quick feedback.

### `kiwuuu-design-kit`

Premium UI building blocks for React/Next.js + shadcn projects. USE WHEN building or restyling a landing page, marketing section, dashboard, or app screen (hero, pricing, CTA, footer, features, testimonials) and you want production-grade components instead of generic AI markup. Pulls real source from the Efferd shadcn registry and applies the Kiwuuu DESIGN.md system. Web/app UI only — NOT video/motion.

### `kiwuuu-experiment-loop`

Runs an autonomous propose-measure-keep/discard experiment loop over any Kiwuuu asset with a single numeric benchmark, using git commits as memory (Karpathy AutoResearch pattern). Use when the user wants to optimize something measurable overnight or unattended — scanner signals, script pacing, landing conversion copy, SFX timing — or says "experiment loop", "autoresearch", "optimize while I sleep".

### `kiwuuu-video-factory`

Generate, voice, caption, and deploy short vertical demo videos for Kiwuuu social (TikTok / IG Reels / Threads / X). USE WHEN the user asks to "make a video for kiwuuu", "create a TikTok demo", "generate social videos", or wants to produce vertical 9:16 cinematic clips with voiceover and burned captions. Outputs land at /var/www/kiwuuu/media/content/ and serve at https://kiwuuu.com/media/content/.

### `kiwuuu-youtube-director`

Director layer for faceless YouTube videos on the Higgsfield MCP — preset gallery pick, one-pass questionnaire, story beats, a DETAILED script pass (hook workshop, 10s-block word budgets, retention edit, fix loop with Kiwu), then a hard credit gate before any generation. USE WHEN the user says "make a youtube video", "video questionnaire", wants to plan/script an explainer, history, kids or story video, or asks to restart the youtube engine. Wraps faceless-channel-video — never generates until the script is LOCKED and credits approved.

### `last30days` — "3.3.2" # long-body: third-party execution-ordered prompt pipeline (steps 0-2.5 with # embedded shell contracts); splitting it would break upstream sync and step order.

Research what people actually say about any topic in the last 30 days — pulls posts and engagement from Reddit, X, YouTube, TikTok, Hacker News, Polymarket, GitHub, and the web, then clusters and ranks them.

### `launch`

When the user wants to plan a product launch, feature announcement, or release strategy. Also use when the user mentions 'launch,' 'Product Hunt,' 'feature release,' 'announcement,' 'go-to-market,' 'beta launch,' 'early access,' 'waitlist,' 'product update,' 'how do I launch this,' 'launch checklist,' 'GTM plan,' or 'we're about to ship.' Use this whenever someone is preparing to release something publicly. For ongoing marketing after launch, see marketing-ideas. For the offer being launched (bonuses, guarantees, scarcity, naming), see offers.

### `marketing-psychology`

When the user wants to apply psychological principles, mental models, or behavioral science to marketing. Also use when the user mentions 'psychology,' 'mental models,' 'cognitive bias,' 'persuasion,' 'behavioral science,' 'why people buy,' 'decision-making,' 'consumer behavior,' 'anchoring,' 'social proof,' 'scarcity,' 'loss aversion,' 'framing,' or 'nudge.' Use this whenever someone wants to understand or leverage how people think and make decisions in a marketing context. For applying psychology to specific pages, see cro; for pricing tactics, see pricing; for copy framing, see copywriting.

### `mcp-builder`

Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).

### `media-use`

Agent Media OS, the single skill for every media need in a HyperFrames project. Resolve BGM, SFX, image, icon, brand logo, voice, color grade, or LUT into a frozen local file or paste-ready block + ledger record (one verb, `resolve`); generate via TTS / music / image models when the catalog misses; produce voiceover, transcription, captions, and background removal through one shared audio engine; operate on media (cut / reframe / transform); and reuse assets across projects. Also use for vague feedback that real footage looks dark, flat, boring, should feel retro/camcorder/print/ASCII, needs privacy, or needs a media reveal.

### `n8n-agents`

Design n8n AI agents the right way. Use when building or editing any @n8n/n8n-nodes-langchain.* AI node — an AI Agent, LLM chain, Text Classifier, or Information Extractor — and whenever the user mentions AI agents, LLM with tools, tool calling, $fromAI, system prompts, agent memory, sessionId, structured/JSON output, output parser, RAG, vector store, a chat assistant/bot, or human-in-the-loop review. Covers Agent-vs-chain-vs-classifier choice, the model/memory/tools/outputParser slots, tool names/descriptions as prompt, structured output with autoFix, memory, RAG, human review, and chat topologies.

### `n8n-binary-and-data`

Handle files and binary data in n8n correctly. Use when working with files, images, PDFs, attachments, uploads or downloads, base64, vision/multimodal input, or when an AI agent needs a file as tool input or output — and whenever the user mentions $binary, binaryPropertyName, "read the PDF", "attach the file", "send the image", Merge losing binary, or a CDN for chat images. Covers the $binary vs $json split, reading/writing binary, keeping binary alive across transforms with Merge, the agent-tool binary boundary, and the CDN/URL requirement for chat surfaces.

### `n8n-code-javascript`

Write JavaScript code in n8n Code nodes. Use when writing JavaScript in n8n, using $input/$json/$node syntax, making HTTP requests with this.helpers / the $helpers global, working with dates using DateTime, troubleshooting Code node errors, choosing between Code node modes, or doing any custom data transformation in n8n. Always use this skill when a workflow needs a Code node — whether for data aggregation, filtering, API calls, format conversion, batch processing logic, or any custom JavaScript. Covers SplitInBatches loop patterns, cross-iteration data, pairedItem, and real-world production patterns. Also use when asked why a Code node or workflow is slow, which execution mode is faster, or how to cut per-item overhead on large datasets. EXCEPTION — for the AI-agent-callable Custom Code Tool (@n8n/n8n-nodes-langchain.toolCode, a tool attached to an AI Agent), use the n8n-code-tool skill instead; it has a different runtime contract.

### `n8n-code-python`

Write Python code in n8n Code nodes. Use when writing Python in n8n, using _input/_json/_node syntax, working with standard library, or need to understand Python limitations in n8n Code nodes. Use this skill when the user specifically requests Python for an n8n Code node. Note — JavaScript is recommended for 95% of use cases — only use Python when the user explicitly prefers it or the task requires Python-specific standard library capabilities (regex, hashlib, statistics). EXCEPTION — for Python in the AI-agent-callable Custom Code Tool (@n8n/n8n-nodes-langchain.toolCode), use the n8n-code-tool skill instead (input is _query, return must be a string).

### `n8n-code-tool`

Write JavaScript or Python for the n8n Custom Code Tool (@n8n/n8n-nodes-langchain.toolCode) — the AI-agent-callable tool, NOT the workflow Code node. Use when building a Code Tool attached to an AI Agent, writing code that an LLM will invoke, parsing the `query` input, returning a string result, defining an input schema for structured arguments (specifyInputSchema, jsonSchemaExample, DynamicStructuredTool), or troubleshooting errors like "Wrong output type returned", "No execution data available", "The response property should be a string, but it is an object", "Cannot assign to read only property 'name'", or an AI agent that refuses to call the tool. Covers the critical differences between Code node and Code Tool: return format (string vs `[{json:{...}}]`), unavailability of `$fromAI`/`$input`/`$helpers` in the Code Tool sandbox, naming rules for AI invocation, and when to use `toolWorkflow`/HTTP Request Tool instead.

### `n8n-error-handling`

Wire n8n error handling so failures are loud, structured, and recoverable. Use when building any webhook/API workflow, a scheduled or unattended workflow, or any path where a silent failure would drop user-visible work — and whenever the user mentions error handling, onError, continueErrorOutput, error branches/outputs, retries, retryOnFail, Respond to Webhook status codes, 4xx/5xx, Error Trigger, or "my workflow fails silently". Covers per-node error outputs and wiring, retry/self-healing, error-trigger workflows, and 4xx/5xx response shapes.

### `n8n-expression-syntax`

Validate n8n expression syntax and fix common errors. Use when writing n8n expressions, using {{}} syntax, accessing $json/$node variables, troubleshooting expression errors, mapping data between nodes, or referencing webhook data in workflows. Use this skill whenever configuring node fields that reference data from previous nodes — expressions are how n8n passes data between nodes, and getting the syntax wrong is the most common source of workflow errors. Also use when asked whether a complex expression hurts performance.

### `n8n-mcp-tools-expert`

Expert guide for using n8n-mcp MCP tools effectively. Use when searching for nodes, validating configurations, accessing templates, managing workflows, managing credentials, auditing instance security, or using any n8n-mcp tool. Provides tool selection guidance, parameter formats, and common patterns. IMPORTANT — Always consult this skill before calling any n8n-mcp tool — it prevents common mistakes like wrong nodeType formats, incorrect parameter structures, and inefficient tool usage. If the user mentions n8n, workflows, nodes, or automation and you have n8n MCP tools available, use this skill first.

### `n8n-multi-instance`

Use when an n8n-mcp account targets more than one n8n instance — i.e. the `n8n_instances` tool is available, the user mentions multiple n8n instances or environments (prod vs staging, several teams or clients), a workflow / datatable / credential / execution call returns an unexpected NOT_FOUND or reads data you don't recognize, or a credential create/update/delete is refused with an `INSTANCE_AMBIGUOUS` error. Covers choosing and switching which instance this MCP session targets, verifying the target before high-stakes work — credential writes above all — and recovering from misroutes and ambiguous-write fail-closes. Always consult this skill before operating on a specific instance, before any credential create/update/delete on a multi-instance account, or when a call hits the wrong/empty data or an `INSTANCE_AMBIGUOUS` error.

### `n8n-node-configuration`

Operation-aware node configuration guidance. Use when configuring nodes, understanding property dependencies, determining required fields, choosing between get_node detail levels, or learning common configuration patterns by node type. Always use this skill when setting up node parameters — it explains which fields are required for each operation, how displayOptions control field visibility, and when to use patchNodeField for surgical edits vs full node updates.

### `n8n-self-hosting`

Deploy a production self-hosted n8n end-to-end to a fresh Linux VM over SSH, using Docker Compose behind a Caddy reverse proxy with automatic HTTPS. Use whenever the user wants to self-host, install, set up, provision, or deploy n8n on their own server/VPS/box (Hetzner, DigitalOcean, AWS EC2, bare metal, etc.) — in either single/regular mode or queue mode with workers — or to update, back up, restore, or harden such an instance. This is for SELF-HOSTED n8n (Docker), not n8n Cloud and not building workflows. The skill makes the agent ask single-vs-queue first, collect the domain/SSH/timezone inputs, generate fresh secrets on the box, and bring the stack up with TLS. Trigger on "deploy n8n", "self-host n8n", "install n8n on my server", "n8n docker compose", "n8n queue mode / workers / scaling", "n8n reverse proxy / SSL", or "back up / update my n8n".

### `n8n-subworkflows`

Build reusable, composable n8n sub-workflows. Use when extracting shared logic, building anything multi-step or reused across workflows, or any workflow over ~10 nodes — and whenever the user mentions sub-workflows, Execute Workflow, reuse, shared/common logic, modular workflows, "Define Below" inputs, waitForSubWorkflow, mode each vs all, or exposing a workflow as an agent tool. Covers typed sub-workflow inputs, all-vs-each execution, verb-first naming for discovery, stateless vs stateful design, and splitting by input shape.

### `n8n-validation-expert`

Interpret validation errors and guide fixing them. Use when encountering validation errors, validation warnings, false positives, operator structure issues, or need help understanding validation results. Also use when asking about validation profiles, error types, the validation loop process, or auto-fix capabilities. Consult this skill whenever a validate_node or validate_workflow call returns errors or warnings — it knows which warnings are false positives and which errors need real fixes.

### `n8n-workflow-patterns`

Proven workflow architectural patterns from real n8n workflows. Use when building new workflows, designing workflow structure, choosing workflow patterns, planning workflow architecture, or asking about webhook processing, HTTP API integration, database operations, AI agent workflows, batch processing, or scheduled tasks. Always consult this skill when the user asks to create, build, or design an n8n workflow, automate a process, or connect services — even if they don't explicitly mention 'patterns'. Covers webhook, API, database, AI, batch processing, and scheduled automation architectures. Also use when optimizing a slow workflow or speeding up large-item-count processing (node count, batchSize, all-items vs per-item).

### `nextjs-best-practices`

Next.js best practices: file conventions, RSC boundaries, data patterns, async APIs, metadata, error handling, route handlers, image/font optimization, bundling.

### `nextjs-seo`

Next.js SEO optimization guide. Use when building Next.js apps, optimizing for search engines, fixing Google indexing issues, implementing metadata, sitemaps, robots.txt, JSON-LD, or auditing SEO.

### `nextjs-shadcn`

Creates Next.js 16 frontends with shadcn/ui. Use when building React UIs, components, pages, or applications with shadcn, Tailwind, or modern frontend patterns.

### `pdf`

Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs apart, rotating pages, adding watermarks, creating new PDFs, filling PDF forms, encrypting/decrypting PDFs, extracting images, and OCR on scanned PDFs to make them searchable. If the user mentions a .pdf file or asks to produce one, use this skill.

### `pose-library-design`

Design reusable 2D character pose libraries, action cycles, and expression states for data-driven animation, so rigged characters ship with consistent composable poses.

### `pptx`

Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions "deck," "slides," "presentation," or references a .pptx filename, regardless of what they plan to do with the content afterward. If a .pptx file needs to be opened, created, or touched, use this skill.

### `pricing`

When the user wants help with pricing decisions, packaging, or monetization strategy. Also use when the user mentions 'pricing,' 'pricing tiers,' 'freemium,' 'free trial,' 'packaging,' 'price increase,' 'value metric,' 'Van Westendorp,' 'willingness to pay,' 'monetization,' 'how much should I charge,' 'my pricing is wrong,' 'pricing page,' 'annual vs monthly,' 'per seat pricing,' or 'should I offer a free plan.' Use this whenever someone is figuring out what to charge or how to structure their plans. For in-app upgrade screens, see paywalls. For offer construction (bonuses, guarantees, value framing, naming) on services/courses/coaching/high-ticket B2B, see offers.

### `product-marketing`

When the user wants to create or update their product marketing context document. Also use when the user mentions 'product context,' 'marketing context,' 'set up context,' 'positioning,' 'who is my target audience,' 'describe my product,' 'ICP,' 'ideal customer profile,' or wants to avoid repeating foundational information across marketing tasks. Use this at the start of any new project before using other marketing skills — it creates `.agents/product-marketing.md` that all other skills reference for product, audience, and positioning context.

### `react-best-practices`

React and Next.js performance optimization guidelines from Vercel Engineering. This skill should be used when writing, reviewing, or refactoring React/Next.js code to ensure optimal performance patterns. Triggers on tasks involving React components, Next.js pages, data fetching, bundle optimization, or performance improvements.

### `remotion-best-practices`

Umbrella reference for building videos in Remotion: composition markup, captions, docs lookup, rendering, SaaS player embedding, upgrades.

### `remotion-captions`

Captions in Remotion: transcribe audio to captions, import SRT files, and display word-timed captions in compositions.

### `remotion-create`

Scaffold a new Remotion video project: layout patterns, Tailwind setup, and composition structure.

### `remotion-docs`

Search and fetch Remotion documentation pages for exact API signatures and options.

### `remotion-render`

Render Remotion videos correctly: render commands, codec choices, transparent video output, performance.

### `route`

Pre-flight skill picker for complex tasks. Reads the user's request, the installed-skills list (already in system prompt), and emits a 3-pick routing decision with one-line justifications. USE WHEN task contains action verbs (build/refactor/audit/research/design/migrate/ship) AND is >40 words OR has 2+ comma-separated subtasks OR user explicitly types /route. SKIP for trivial requests (<10 words, pure Q&A, continuations of in-flight work, or when user already named a specific skill).

### `saas-metrics`

SaaS metrics framework for founders. USE WHEN calculating MRR, ARR, churn rate, LTV, CAC, NPS, activation rate, or building investor-ready dashboards. Covers cohort analysis, revenue forecasting, unit economics, and growth accounting. Includes Kiwuuu-specific metric targets and SQL queries.

### `sales-enablement`

When the user wants to create sales collateral, pitch decks, one-pagers, objection handling docs, or demo scripts. Also use when the user mentions 'sales deck,' 'pitch deck,' 'one-pager,' 'leave-behind,' 'objection handling,' 'deal-specific ROI analysis,' 'demo script,' 'talk track,' 'sales playbook,' 'proposal template,' 'buyer persona card,' 'help my sales team,' 'sales materials,' or 'what should I give my sales reps.' Use this for any document or asset that helps a sales team close deals. For competitor comparison pages and battle cards, see competitors. For marketing website copy, see copywriting. For cold outreach emails, see cold-email. For the offer being sold (bonuses, guarantees, pricing structure), see offers.

### `send-to-my-whatsapp`

Send a file (video, image, PDF, any document) or a text message to Kiwu's own WhatsApp via the Kiwuuu Cloud API number. USE WHEN Kiwu says "send it to my whatsapp", "send me that on whatsapp", "whatsapp me the video/file", or asks for any deliverable on his phone. Handles credential lookup, auto-compression to WhatsApp's real media caps, the correct recipient, and the 24-hour-window failure mode.

### `seo-audit`

When the user wants to audit, review, or diagnose SEO issues on their site. Also use when the user mentions "SEO audit," "technical SEO," "why am I not ranking," "SEO issues," "on-page SEO," "meta tags review," "SEO health check," "my traffic dropped," "lost rankings," "not showing up in Google," "site isn't ranking," "Google update hit me," "page speed," "core web vitals," "crawl errors," or "indexing issues." Use this even if the user just says something vague like "my SEO is bad" or "help with SEO" — start with an audit. For building pages at scale to target keywords, see programmatic-seo. For adding structured data, see schema. For AI search optimization, see ai-seo.

### `session-state` — 1.0.0 · production

Writes the current session's state into the vault's _now.md so the next session — any machine, any tool — starts with zero catchup. Updates the Active/Waiting/Parked thread tables, stamps dates, deletes finished rows, and commits. Ships now_doctor.py (mechanical rot checks plus a Stop-hook guard that blocks ending a session with unsaved state) and a SessionEnd breadcrumb hook that records facts even when no handoff happens. The write-side counterpart to ultimate-loop CatchUp, which reads _now.md at session start.

### `skill-creator`

Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.

### `slack-gif-creator`

Knowledge and utilities for creating animated GIFs optimized for Slack. Provides constraints, validation tools, and animation concepts. Use when users request animated GIFs for Slack like "make me a GIF of X doing Y for Slack."

### `stripe-best-practices`

Guides Stripe integration decisions across API selection (Checkout Sessions vs PaymentIntents), Connect platform setup (Accounts v2, controller properties), billing/subscriptions, tax and registrations (Stripe Tax, automatic_tax, product tax codes), Treasury financial accounts, integration options (Checkout, Payment Element), migrating from deprecated Stripe APIs, and security best practices (API key management, restricted keys, webhooks, OAuth). Use when building, modifying, or reviewing any Stripe integration, including accepting payments, building marketplaces, integrating Stripe, processing payments, setting up subscriptions, collecting sales tax, VAT, or GST, creating connected accounts, or implementing secure key handling.

### `stripe-saas-billing`

Stripe subscription billing for SaaS. USE WHEN implementing Stripe subscriptions, handling webhook events, managing proration, building dunning logic, or debugging billing issues. Covers subscription lifecycle, invoice handling, trial periods, upgrade/downgrade, failed payment recovery, and Stripe Python SDK patterns.

### `svg-character-animation`

Animate SVG character rigs with GSAP, CSS transforms, Remotion frame control, and HyperFrames- compatible browser previews.

### `theme-factory`

Toolkit for styling artifacts (slides, docs, reports, HTML landing pages) with one of 10 pre-set color/font themes, or a theme generated on the fly.

### `ultimate-loop` — 2.2.0 · production

Read-only verification for VPS-hosted stacks. Checks HTTP endpoints, PM2 process counts, SSH keys, disk/RAM/swap thresholds, and media asset inventory in parallel, then prints a scored PASS/FAIL report with failures itemized. Never fixes, deploys, restarts, or generates anything — every operation is a check, so a wrong invocation costs only seconds.

- `Workflows/CatchUp.md` — Get fully up to speed from zero context in under 60 seconds. Read project state, check what changed, verify everything works.
- `Workflows/Content.md` — Verify all content assets exist, are correctly sized, and are publicly accessible.
- `Workflows/Full.md` — Complete system, content, and infrastructure verification.
- `Workflows/Quick.md` — Fast endpoints + PM2 check only. Use for quick session-start verification.

### `upgrade-stripe`

Guide for upgrading Stripe API versions and SDKs safely — changelogs, breaking changes, migration order.

### `using-n8n-mcp-skills`

Use when building, editing, validating, testing, or debugging an n8n workflow through the n8n-mcp MCP server — designing a flow, configuring a node, writing an expression or Code node, wiring credentials, or fixing one that misbehaves. The entry-point skill for the n8n-mcp-skills pack: it routes you to the right specialist skill, gives working knowledge of every n8n-mcp tool from turn one, and states the rules that keep workflows from breaking in production. Always consult it first on any n8n, workflow, node, or automation task — even a quick one-off, and even when the user names no skill — because n8n's surface drifts between versions and the specialist skills prevent silent failures.

### `web-artifacts-builder`

Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX artifacts.

### `web-design-guidelines`

Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".

### `webapp-testing`

Toolkit for interacting with and testing local web applications using Playwright: verify frontend functionality, debug UI behavior, capture browser screenshots, view browser logs.

### `whatsapp-cloud-api`

Official WhatsApp Cloud API reference for building messaging integrations. Covers sending messages (text, media, templates, interactive), receiving webhooks, conversation lifecycle, phone number management, and error handling. Use when building WhatsApp integrations, sending messages, processing webhooks, or working with the Meta WhatsApp Business Platform API.

### `xlsx`

Use this skill any time a spreadsheet file is the primary input or output. This means any task where the user wants to: open, read, edit, or fix an existing .xlsx, .xlsm, .csv, or .tsv file (e.g., adding columns, computing formulas, formatting, charting, cleaning messy data); create a new spreadsheet from scratch or from other data sources; or convert between tabular file formats. Trigger especially when the user references a spreadsheet file by name or path — even casually (like "the xlsx in my downloads") — and wants something done to it or produced from it. Also trigger for cleaning or restructuring messy tabular data files (malformed rows, misplaced headers, junk data) into proper spreadsheets. The deliverable must be a spreadsheet file. Do NOT trigger when the primary deliverable is a Word document, HTML report, standalone Python script, database pipeline, or Google Sheets API integration, even if tabular data is involved.

## Route table — keyword → skill → workflow

| Trigger keywords | Skill | Workflow |
|---|---|---|
| `review the animation`, `QA the character animation`, `check the rig animation`, `animation looks wrong`, `verify frames`, `preview the animation`, `validate render output` | `character-animation-qa` | _(single mode)_ |
| `rig a character`, `build a character rig`, `set up pivots`, `rig package`, `prepare a character for animation`, `2D puppet` | `character-rigging` | _(single mode)_ |
| `generate content`, `generate posts`, `create posts`, `write a post`, `fill the queue`, `new content`, `caption`, `carousel`, `reel`, `generate an image`, `FLUX`, `generate a video`, `LTX`, `cinematic`, `voiceover` | `content-factory` | `Workflows/Generate.md` |
| `content stats`, `what posted today`, `pipeline status`, `engagement`, `content queue`, `approve post`, `why didn't it post`, `posting failed`, `debug content`, `check the logs`, `rate limit`, `quality gate failed`, `empty queue` | `content-factory` | `Workflows/Report.md` |
| `verify assets are live`, `is the media accessible` | `content-factory` | `/ultimate-loop content` |
| `Workflow` | `fabric` | `Trigger` |
| `**ExecutePattern**` | `fabric` | `"use fabric", "run pattern", "apply pattern", "extract wisdom", "summarize", "analyze with fabric"` |
| `**UpdatePatterns**` | `fabric` | `"update fabric", "update patterns", "sync fabric", "pull patterns"` |
| `run the competitor scrape`, `check what competitors are doing`, `competitive content brief`, `daily digest`, `what changed at competitors` | `kiwuuu-competitor-scraper` | `Workflows/Daily.md` |
| `council`, `debate`, `perspectives on X`, `red team`, `stress test`, `poke holes`, `counterargument`, `challenge each other` | `kiwuuu-debate` | `Workflows/Debate.md` |
| `quick council`, `quick take`, `sanity check this decision` | `kiwuuu-debate` | `Workflows/Quick.md` |
| `what are people saying about`, `recent sentiment`, `social listening`, `last 30 days`, `trending discussions`, `research this on social`, `what's the buzz`, `scan Reddit and X` | `last30days` | _(single mode)_ |
| `writing or reviewing Next.js code`, `App Router questions`, `server components`, `hydration errors`, `next/image`, `next/font`, `route handlers`, `Next.js build issues` | `nextjs-best-practices` | _(single mode)_ |
| `pose library`, `character poses`, `action cycle`, `walk cycle`, `expression states`, `idle set`, `pose presets` | `pose-library-design` | _(single mode)_ |
| `working in a Remotion project and no narrower remotion-* skill fits`, `Remotion questions`, `React video code`, `@remotion packages. NOT for HyperFrames compositions — hyperframes is its own entry point` | `remotion-best-practices` | _(single mode)_ |
| `add captions in Remotion`, `subtitles in a Remotion video`, `import SRT`, `transcribe for captions`, `word-by-word captions` | `remotion-captions` | _(single mode)_ |
| `create a Remotion video`, `new Remotion project`, `start a React video`, `scaffold a composition` | `remotion-create` | _(single mode)_ |
| `look up Remotion docs`, `Remotion API reference`, `how does a @remotion package work`, `check the Remotion documentation` | `remotion-docs` | _(single mode)_ |
| `render the Remotion video`, `export the video`, `transparent background video`, `Remotion render fails`, `codec settings` | `remotion-render` | _(single mode)_ |
| `handoff`, `save state`, `update now`, `wrap up`, `end session`, `ending for today`, `closing up`, `before you go`, `park this`, `record where we are`, `save progress`, `update the now file`, `sync state`, `now doctor`, `state doctor`, `check state health`, `stale threads`, `install handoff hooks` | `session-state` | _(single mode)_ |
| `animate the character`, `SVG character animation`, `animate the rig`, `character motion`, `bring the character to life` | `svg-character-animation` | _(single mode)_ |
| `apply a theme`, `style this artifact`, `pick a color scheme`, `theme the slides or doc or landing page`, `match a look`, `generate a new theme` | `theme-factory` | _(single mode)_ |
| `ultimate loop`, `run checks`, `verify everything`, `full check`, `health check`, `system check`, `smoke test`, `sanity check`, `after deploy`, `did anything break`, `regression check` | `ultimate-loop` | `Workflows/Full.md` |
| `quick check`, `fast check`, `is the site up`, `is everything running`, `are services online`, `uptime`, `ping endpoints`, `pm2 status` | `ultimate-loop` | `Workflows/Quick.md` |
| `catch up`, `catch me up`, `where were we`, `what changed`, `session start`, `zero context`, `brief me`, `get up to speed` | `ultimate-loop` | `Workflows/CatchUp.md` |
| `check assets`, `asset inventory`, `are the videos there`, `is the media live`, `content check`, `queue depth` | `ultimate-loop` | `Workflows/Content.md` |
| `upgrade Stripe`, `bump the Stripe API version`, `Stripe SDK migration`, `pinned Stripe version is old` | `upgrade-stripe` | _(single mode)_ |
| `test the web app`, `click through the UI`, `browser screenshot`, `check the frontend in a real browser`, `debug UI behavior`, `read browser console logs` | `webapp-testing` | _(single mode)_ |

## Routing health

All skills carry a description, trigger keywords, and a routing table.

<!-- END GENERATED -->

---

## Disambiguation — the collisions that actually bite

### Video — the biggest family (15 skills)

**`hyperframes` is the mandatory entry point** for any "make/edit/animate/render a video, animation, or motion graphic" request. It routes internally to its sub-skills — `hyperframes-core` (composition contract), `-animation` (motion rules), `-creative` (design direction), `-keyframes` (seek-safe keyframes), `-media` (audio/assets), `-cli` (build loop), `-registry` (components) — and to `general-video` as its fallback route. **Never select a `hyperframes-*` sub-skill directly from a fresh user request**; they assume you're already inside a HyperFrames project.

Exceptions, by name:

| The request names… | Skill |
|---|---|
| Remotion, React video code, an existing Remotion project | `remotion-best-practices` (umbrella) → narrower `remotion-captions` / `-create` / `-docs` / `-render` by sub-topic |
| Kiwuuu social demo videos (TikTok/Reels/Threads) end-to-end | `kiwuuu-video-factory` |
| faceless YouTube videos | `kiwuuu-youtube-director` |
| the VPS posting pipeline, the queue, scheduled posts | `content-factory` |
| BGM, SFX, TTS, voiceover, LUTs, image assets for a composition | `media-use` |

Note the duplicate: `remotion-captions`/`-create`/`-docs`/`-render` exist both standalone and as folders inside `remotion-best-practices`. The standalone ones win selection; the umbrella's copies are its references. Candidates for merging.

### Character animation — a pipeline, not four competitors

`character-rigging` → `pose-library-design` → `svg-character-animation` → `character-animation-qa`. Route on the verb: **rig/build** → rigging, **poses/cycles** → pose-library, **animate/move** → svg-character-animation, **review/QA/looks wrong** → animation-qa. A full "animate this character" request starts at rigging only if no rig exists yet.

### Cold email — near-duplicates

`cold-email` is generic B2B email *craft* (subject lines, sequences, deep references). `cold-outreach` is the Kiwuuu/SaaS-founder *pipeline* (ICP, LinkedIn, WhatsApp prospecting, first customers). Multi-channel or Kiwuuu-specific → `cold-outreach`; pure email writing → `cold-email`.

### Research — four different questions

| Question | Skill |
|---|---|
| "What are people saying about X lately?" (any topic, broad) | `last30days` |
| "Break down why *this specific video* worked" | `kiwuuu-analyze` |
| "How do we position against competitors?" (analysis, judgment) | `competitor-intel` |
| "What did the named competitors change since yesterday?" (automated diff) | `kiwuuu-competitor-scraper` |

### n8n — 15 skills, one entry rule

Working through the n8n-mcp server → start at `using-n8n-mcp-skills` (it's the meta-guide). Then by symptom: building a workflow → `n8n-workflow-patterns`; `{{}}` expression broken → `n8n-expression-syntax`; validation errors → `n8n-validation-expert`; configuring a node → `n8n-node-configuration`; Code node JS/Python → `n8n-code-javascript`/`-python` (agent-callable tool code → `n8n-code-tool`); AI agent nodes → `n8n-agents`; files/binary → `n8n-binary-and-data`; error handling → `n8n-error-handling`; sub-workflows → `n8n-subworkflows`; deploying n8n itself → `n8n-self-hosting`; multiple instances → `n8n-multi-instance`; the MCP tools themselves → `n8n-mcp-tools-expert`.

### Frontend & design — build vs review vs brand

| Intent | Skill |
|---|---|
| Aesthetic direction for new UI ("make it distinctive") | `frontend-design` |
| Review existing UI for guideline/accessibility compliance | `web-design-guidelines` |
| Kiwuuu-branded landing/UI blocks | `kiwuuu-design-kit` |
| Scaffold Next.js + shadcn app | `nextjs-shadcn` |
| Next.js correctness questions | `nextjs-best-practices` |
| React/Next performance | `react-best-practices` |
| SEO built into a Next app | `nextjs-seo` · diagnosing an existing site's SEO → `seo-audit` |
| claude.ai artifacts specifically | `web-artifacts-builder` |

### ⚠ Brand hazard

`brand-guidelines` applies **Anthropic's** brand. `kiwuuu-brand-voice` applies **Kiwuuu/TraficShop's**. Any Kiwuuu asset routed to `brand-guidelines` comes out in the wrong company's colors. Default for this library's owner: `kiwuuu-brand-voice`.

### Stripe — three lifecycle stages

Design decisions (which API, Connect, tax) → `stripe-best-practices`. Implementing subscriptions/webhooks → `stripe-saas-billing`. Migrating API versions → `upgrade-stripe`.

### WhatsApp — reference vs trigger

`whatsapp-cloud-api` is documentation for building integrations. `send-to-my-whatsapp` **actually sends** to Kiwu's phone — it's an action with a side effect, not a reference.

### Marketing set — route on the noun

`cro` (page won't convert) · `pricing` (what to charge) · `saas-metrics` (calculate MRR/LTV/CAC) · `launch` (plan a release) · `churn-prevention` (keep subscribers) · `sales-enablement` (decks, one-pagers, objections) · `product-marketing` (positioning context doc) · `marketing-psychology` (behavioral principles) · `humanizer` (de-AI the text) · `kallaway-method` (short-form hooks/scripts) · `kiwuuu-carousel` (photo-mode carousels) · `dub-co` (short links/UTM).

### Deliberation vs advice

Decision needs structured challenge (council, red team, stress test) → `kiwuuu-debate`. Finance/runway/founder advice as a direct answer → `kiwuuu-business`. Peer mode of `kiwuuu-debate` costs 3-4× tokens — it confirms with the founder first, honor that.

### Orchestration

Task spans 3+ files or 2+ subsystems → `dispatching-kiwuuu-squad` (parallel fan-out). Iterating one asset against a single metric → `kiwuuu-experiment-loop`. These compose: squad for breadth, loop for depth.

### Documents — by extension, then by activity

`.docx` → `docx` · `.pdf` → `pdf` · `.pptx` → `pptx` · `.xlsx`/CSV → `xlsx`. Writing a doc *together* (specs, proposals) → `doc-coauthoring`. Company-internal formats (status, incident, newsletter) → `internal-comms`. Themed styling of any artifact → `theme-factory`.

### Session state & verification (this repo's own three)

Asking *what* the state is ("catch up", "where were we") → `ultimate-loop/CatchUp.md`, which reads the vault's `_now.md` first. Asking to *save* it ("handoff", "wrap up") → `session-state`. "Check/verify content" → `ultimate-loop/Content.md`; "make/post content" → `content-factory`. When ambiguous between check and act, check first — it's free.

---

## Cost of a wrong route

Route conservatively down this table — a wrong pick in tier 1 is free, in tier 4 it's public.

| Tier | Skills | Why |
|---|---|---|
| 1 · Read-only references | all `n8n-*`, `nextjs-*`, `react-best-practices`, `stripe-best-practices`, `whatsapp-cloud-api`, `remotion-docs`, marketing set, `fabric`, `ultimate-loop` | No side effects. Wrong route costs seconds. |
| 2 · Local writes | character pipeline, `remotion-*`, `hyperframes-*`, `session-state`, `skill-creator`, document skills | Files and commits; `git revert` undoes anything. |
| 3 · Spends money / heavy compute | `kiwuuu-video-factory`, `kiwuuu-youtube-director`, `media-use` (TTS/BGM providers), `kiwuuu-debate` peer mode, `dispatching-kiwuuu-squad`, `kiwuuu-experiment-loop`, `last30days` (long scrape) | API credits and tokens. Confirm scale before running. |
| 4 · Publishes / sends externally | `content-factory` (`run_due`/`run_slot` post publicly), `send-to-my-whatsapp` (messages a real phone), `dub-co` (creates live links), `kiwuuu-video-factory` deploy step | Visible to the world or another human. Confirm first, always. |

---

## Chains

```
session start        →  ultimate-loop CatchUp (reads _now.md)  →  (failures) ultimate-loop Full
session end          →  session-state (writes _now.md)  →  next session starts warm
daily content        →  kiwuuu-competitor-scraper Daily  →  kallaway-method (script)
                        →  kiwuuu-video-factory / kiwuuu-carousel  →  content-factory queue
                        →  ultimate-loop Content (verify assets live)
video build          →  hyperframes (route)  →  hyperframes-core  →  -animation/-keyframes
                        →  media-use (assets)  →  hyperframes-cli (lint, render)
                        →  character-animation-qa (if characters)
research → content   →  last30days  →  kiwuuu-analyze (standout video)  →  kallaway-method
big decision         →  kiwuuu-debate  →  record in mempalace decisions/  →  session-state
new skill            →  skill-creator  →  build_router.py  →  fix Routing health findings
```

---

## Known issues

- **`last30days` reads browser cookies** (`chrome_cookies.py`, `safari_cookies.py`, X/Twitter auth) — same caveat as the Agent-Reach review: only feed it accounts you'd accept losing, and its scrapes of X/Instagram/TikTok carry ToS and ban risk.
- **`last30days` body is 1713 lines by design** — a third-party, execution-ordered prompt pipeline with embedded shell contracts. It carries `router-allow: long-body` so the lint accepts it deliberately instead of flagging it forever; don't split it, it would break upstream sync and step order.
- **remotion layout is intentional, not duplication** — the standalone `remotion-captions`/`-create`/`-docs`/`-render` skills are the selectable entry points; `remotion-best-practices` keeps identical copies internally as its own one-level-deep references (upstream Remotion skill design). Keep both; when editing content, edit both or neither.

---

## Adding a skill

1. Write `skills/<name>/SKILL.md`. The `description` states **what it does** in third person, then `USE WHEN:` followed by dense, comma-separated trigger phrases — the literal words a user would type, not a category label.
2. Put multi-mode logic in `skills/<name>/Workflows/*.md` and add a `## Workflow Routing` table to `SKILL.md`. Comma-separate the triggers; the generator emits one row per phrase.
3. Run `python3 scripts/build_router.py skills/ --out ROUTER.md` and fix anything the **Routing health** table flags.
4. Add the skill to the right Disambiguation cluster above — or create one if it collides with nothing yet. That part is judgment; the generator can't write it.
