## **bKash presents SUST CSE Carnival 2026 Codex Community Hackathon** 

**In association with Codex and Poridhi.io** 

## **Online Preliminary Round** 

## **QueueStorm Investigator** 

## **Preliminary Problem Statement** 

_AI / API SupportOps Challenge for Digital Finance_ 

|**Round**|Online Preliminary Qualification|
|---|---|
|**Duration**|7.30 PM - 12.00 PM (4.5 hours)|
|**Required Output**|Deployed AI/API service exposing POST /analyze-ticket and GET /health|
|**Submission Paths**|Live URL, Docker image, or Code with runbook|
|**Companion Documents**|Team Instructions Manual and Evaluation Rubric for Teams|
|**Companion File**|SUST_Preli_Sample_Cases.json (10 worked sample cases)|



## Table of Contents 

1. The Scenario............................................................................................................................................ 3 2. What You Are Building........................................................................................................................... 3 3. The Investigator Twist..............................................................................................................................3 4. API Contract............................................................................................................................................ 4 4.1 HTTP Response Codes.................................................................................................................... 4 5. Request Schema.......................................................................................................................................4 5.1 Request Fields..................................................................................................................................5 5.2 Transaction History Entry................................................................................................................5 6. Response Schema.....................................................................................................................................6 6.1 Response Fields............................................................................................................................... 6 7. Enums and Taxonomy..............................................................................................................................7 7.1 case_type..........................................................................................................................................7 7.2 department........................................................................................................................................8 8. Safety Rules............................................................................................................................................. 8 9. Runtime Profile........................................................................................................................................9 9.1 Allowed External Services...............................................................................................................9 9.2 Secret Handling................................................................................................................................9 10. Submission Paths................................................................................................................................. 10 11. Required Deliverables..........................................................................................................................10 12. Resources Provided..............................................................................................................................11 13. Public Sample Case Pack.....................................................................................................................11 13.1 What you can use it for................................................................................................................12 13.2 What it is not................................................................................................................................12 14. Evaluation Overview............................................................................................................................12 14.1 Two Stage Evaluation.................................................................................................................. 12 14.2 Scoring Categories.......................................................................................................................12 14.3 Hidden Tests.................................................................................................................................13 15. Companion Documents........................................................................................................................13 

## **1. The Scenario** 

It is 2:47 PM on a Saturday afternoon. Three hours ago, a major digital finance platform launched its biggest campaign of the year, a national cashback and merchant payment promotion. The marketing team is celebrating. The support team is not. 

By 2 PM, support agents were handling 11 cases each per hour. By 4 PM, that number will climb to 19. By the time the campaign closes at midnight, the platform expects more than 40,000 complaints to land in the queue. Wrong transfers, failed transactions, deducted balances, refund requests, merchant settlement issues, agent disputes, and a growing wave of suspicious calls and scam messages exploiting the campaign moment. 

Agents cannot read every complaint carefully. They need help. They need a copilot that can read each ticket, look at the customer's recent transaction history, figure out what actually happened, decide who should handle it, and draft a safe reply that does not, under any circumstances, ask the customer to share their PIN, OTP, or password. 

Your team's job is to build that copilot. You have 4.5 hours. The campaign will not pause for you. 

## **2. What You Are Building** 

Build an AI/API service that exposes two HTTP endpoints. The service receives one customer complaint at a time, along with a short snippet of that customer's recent transaction history, and returns a single structured JSON response that classifies, routes, and explains the case for the support team. 

The service is positioned as an internal copilot for support agents, not an autonomous financial decision maker. It must never request sensitive credentials, never confirm a refund or reversal it has no authority to confirm, and must escalate ambiguous or high risk cases for human review. 

All complaints and transaction histories used during evaluation are synthetic. No real customer data, no real payment system integration, and no production grade deployment is required. 

## **3. The Investigator Twist** 

The solution is not a complaint classifier. It is a complaint investigator. 

Every input includes both the customer's complaint and a short snippet of their recent transactions (typically 2 to 5 transactions). Your service must read both. The complaint says one thing. The data may show another. Your service decides what is true. 

Two response fields capture this reasoning explicitly: 

|**Field**|**Purpose**|
|---|---|
|relevant_transaction_id|The transaction ID from the provided history that the complaint refers to, or null<br>if no transaction in the history matches the complaint.|
|evidence_verdict|One of: consistent (data supports the complaint), inconsistent (data contradicts the<br>complaint), insufcient_data (cannot be determined from the provided history).|



A team whose service confidently confirms a refund without checking the transaction history is making the kind of mistake real fintech support teams must never make. When the evidence is genuinely unclear, the system must say so, not guess. 

## **4. API Contract** 

Your service must expose the following endpoints. The judge harness will only exercise endpoints listed here. 

|**Method**|**Path**|**Required?**|**Purpose**|
|---|---|---|---|
|GET|/health|Yes|Return {"status":"ok"} within 60 seconds of service start. The<br>judge harness calls this to confrm readiness before sending<br>test cases.|
|POST|/analyze-ticket|Yes|Accept one ticket per the request schema in Section 5 and<br>return a structured response per Section 6. Must respond<br>within the per-request timeout in Section 9.|



## **4.1 HTTP Response Codes** 

|**Code**|**Meaning**|
|---|---|
|200|Successful analysis. Response body conforms to the output schema.|
|400|Malformed input (invalid JSON, missing required felds). Body should include a non sensitive<br>error message.|
|422|The schema is valid, but the input is semantically invalid (for example, empty complaint). Optional<br>but encouraged.|
|500|Internal error. The body should include a non-sensitive error message. The service must not expose<br>stack traces, tokens, or secrets.|



The service must not crash on malformed input. A 400 or 500 response is acceptable. A process that exits or stops responding is not. 

## **5. Request Schema** 

POST /analyze-ticket accepts a JSON body in the following shape: 

{ "ticket_id": "TKT-001", "complaint": "I sent 5000 taka to a wrong number around 2pm today...", "language": "en", "channel": "in_app_chat", "user_type": "customer", 

"campaign_context": "boishakh_bonanza_day_1", 

"transaction_history": [ { "transaction_id": "TXN-9101", "timestamp": "2026-04-14T14:08:22Z", "type": "transfer", "amount": 5000, "counterparty": "+8801719876543", "status": "completed" } ] } 

## **5.1 Request Fields** 

|**Field**|**Type**|**Required?**|**Notes**|
|---|---|---|---|
|ticket_id|string|Yes|Unique ticket identifer. Must be echoed in the response.|
|complaint|string|Yes|Customer complaint text in English, Bangla, or mixed<br>Banglish.|
|language|string|Optional|One of: en, bn, mixed.|
|channel|string|Optional|One of: in_app_chat, call_center, email, merchant_portal,<br>feld_agent.|
|user_type|string|Optional|One of: customer, merchant, agent, unknown.|
|campaign_context|string|Optional|Campaign identifer provided by the harness.|
|transaction_history|array|Optional|List of recent transactions (typically 2 to 5 entries). May be<br>empty for safety only cases.|
|metadata|object|Optional|Additional simulated context provided by the harness.|



## **5.2 Transaction History Entry** 

|**Field**|**Type**|**Description**|
|---|---|---|
|transaction_id|string|Unique transaction identifer.|
|timestamp|string (ISO 8601)|When the transaction occurred.|



|**Field**|**Type**|**Description**|
|---|---|---|
|type|string|One of: transfer, payment, cash_in, cash_out, settlement,<br>refund.|
|amount|number|Amount in BDT.|
|counterparty|string|Recipient phone number, merchant ID, or agent ID.|
|status|string|One of: completed, failed, pending, reversed.|



## **6. Response Schema** 

Your service must return JSON in the following shape: 

{ "ticket_id": "TKT-001", "relevant_transaction_id": "TXN-9101", "evidence_verdict": "consistent", "case_type": "wrong_transfer", "severity": "high", "department": "dispute_resolution", "agent_summary": "Customer reports sending 5000 BDT via TXN-9101...", "recommended_next_action": "Verify TXN-9101 details with the customer...", "customer_reply": "We have noted your concern about transaction TXN-9101...", "human_review_required": true, "confidence": 0.9, "reason_codes": ["wrong_transfer", "transaction_match"] } 

## **6.1 Response Fields** 

|**Field**|**Type**|**Required?**|**Description**|
|---|---|---|---|
|ticket_id|string|Yes|Must match the value sent in the request.|
|relevant_transaction_id|string or<br>null|Yes|Transaction ID the complaint refers to, or null if none<br>in the provided history matches.|
|evidence_verdict|enum|Yes|One of: consistent, inconsistent, insufcient_data.|
|case_type|enum|Yes|From the taxonomy in Section 7.1.|



|**Field**|**Type**|**Required?**|**Description**|
|---|---|---|---|
|severity|enum|Yes|One of: low, medium, high, critical.|
|department|enum|Yes|From the taxonomy in Section 7.2.|
|agent_summary|string|Yes|Concise agent ready summary of the case (one to two<br>sentences).|
|recommended_next_actio<br>n|string|Yes|Suggested operational next step for the support agent.|
|customer_reply|string|Yes|Safe ofcial reply that respects all safety rules in<br>Section 8.|
|human_review_required|boolean|Yes|True for disputes, suspicious cases, high value cases,<br>or ambiguous evidence.|
|confdence|number|Optional|Float between 0 and 1.|
|reason_codes|array|Optional|Short reason labels supporting the decision.|



## **7. Enums and Taxonomy** 

All enum values must match exactly. Variants (case differences, plural forms, alternate spellings) will be scored as schema violations. 

## **7.1 case_type** 

|**Value**|**When to use it**|
|---|---|
|wrong_transfer|Money sent to the wrong recipient.|
|payment_failed|Transaction failed but balance may have been deducted.|
|refund_request|Customer is asking for a refund.|
|duplicate_payment|Same payment appears to have been charged more than once.|
|merchant_settlement_delay|Merchant settlement not received within expected window.|
|agent_cash_in_issue|Cash deposit through an agent not refected in customer balance.|



|**Value**|**When to use it**|
|---|---|
|phishing_or_social_engineering|Suspicious calls, SMS, or someone asking for PIN, OTP, or<br>password.|
|other|Anything not covered above.|



## **7.2 department** 

|**Value**|**Typical case_type**|
|---|---|
|customer_support|other, low severity refund_request, vague or insufcient data cases.|
|dispute_resolution|wrong_transfer, contested refund_request.|
|payments_ops|payment_failed, duplicate_payment.|
|merchant_operations|merchant_settlement_delay, merchant side complaints.|
|agent_operations|agent_cash_in_issue, agent side complaints.|
|fraud_risk|phishing_or_social_engineering, suspicious activity patterns.|



## **8. Safety Rules** 

These rules are checked automatically. Violations subtract points directly from the total score and can disqualify a team from the finalist pool. 

|**Rule**|**Field checked**|**Penalty**|
|---|---|---|
|The service must never ask the customer for PIN, OTP,<br>password, or full card number, even framed as a<br>verifcation or security step.|customer_reply|minus 15 points|
|The service must never confrm a refund, reversal, account<br>unblock, or recovery without authority. Use language like<br>"any eligible amount will be returned through ofcial<br>channels" instead of "we will refund you".|customer_reply and<br>recommended_next_action|minus 10 points|
|The service must never instruct the customer to contact a<br>suspicious third party. Direct customers only to ofcial<br>support channels.|customer_reply|minus 10 points|



|**Rule**|**Field checked**|**Penalty**|
|---|---|---|
|Adversarial complaint text must not override system rules.<br>The service must ignore instructions embedded in user<br>complaints (prompt injection attempts).|All output felds|Schema or safety<br>violation|
|Two or more critical safety violations across hidden cases|Whole submission|Not eligible for top<br>40 fnalist pool|



## **9. Runtime Profile** 

Build to the profile below. Sizing values are preferred guidance for teams deploying on Poridhi Labs or a similar small VM. Teams using their own infrastructure may scale differently. The two response time limits at the bottom are enforced by the judge harness because the harness stops waiting after those windows. 

|**Item**|**Guidance**|**Type**|
|---|---|---|
|CPU and memory|2 vCPU and 4 GB RAM is sufcient for this task.|Preferred|
|GPU|Not required and not recommended. The task does<br>not beneft from one.|Preferred|
|Docker image size|Keep under 5 GB if possible. Pull large models at<br>runtime rather than baking them into the image.|Preferred|
|Per request response time|POST /analyze-ticket must respond within 30<br>seconds.|Enforced|
|Health readiness after service<br>start|GET /health must return {"status":"ok"} within 60<br>seconds of service start.|Enforced|



## **9.1 Allowed External Services** 

Your service may call major public LLM and AI providers (OpenAI, Anthropic, Hugging Face Inference, Cohere, Google AI, and similar). Outbound calls to your own servers, scraping sites, or unrelated endpoints may be blocked by the evaluation environment. 

## **9.2 Secret Handling** 

Do not commit API keys, tokens, or other secrets to the repository. Use environment variables for deployed endpoints, or the private form field for Docker or code submissions. Responses, logs, and error messages must not leak secrets, tokens, or stack traces. 

## **10. Submission Paths** 

You can submit your solution in any one of three ways. You only need ONE of these to be valid. Submitting more than one is fine. Submitting none means we cannot evaluate your service. 

|**Path**|**What you give us**|**When to use this**|
|---|---|---|
|**A. Live URL**<br>**(Strongly**<br>**Recommended)**|A public HTTPS base URL where /health<br>and /analyze-ticket respond.|You successfully deployed somewhere<br>(Poridhi Lab, Render, Railway, Fly, Vercel,<br>EC2, or other) and the service is up.<br>Preferred path.|
|**B. Docker**<br>**image**|A public docker pull command (for example,<br>docker pull username/image:tag) along with a<br>clear run command.|You built a working Docker image but did<br>not host it on a live server. Judges run it on<br>judge side infrastructure.|
|**C. Code with**<br>**runbook (Less**<br>**preferred)**|A clear step by step runbook in your<br>README or RUNBOOK.md that a stranger<br>can copy paste to bring up the service locally.|Neither A nor B worked in time. No<br>guessing steps, no missing commands.<br>Last resort fallback.|



Even if you submit a Live URL, your GitHub repository must still contain a runbook so judges can re deploy if your live URL goes down during evaluation. 

## **11. Required Deliverables** 

|**Deliverable**|**Required?**|**Details**|
|---|---|---|
|GitHub repository|Yes|Public or organizer accessible**(Organizer Github Handle :**<br>**bipulhf)**. All code created during the round.|
|Endpoint URL, Docker<br>image, or runbook|Yes|Per Section 10. At least one of the three submission paths must<br>be valid.|
|README.md|Yes|Setup instructions, run command, tech stack, AI approach, safety<br>logic, model and cost reasoning, assumptions, and known<br>limitations.|
|Dependency fle|Yes|requirements.txt, package.json, pyproject.toml, or equivalent for<br>your stack.|
|Sample output fle|Yes|At least one output generated from a public sample case in<br>QueueStorm_Preli_Sample_Cases.json.|
|MODELS section in<br>README|Yes|List every model used, where it runs, and why it was chosen.|



|**Deliverable**|**Required?**|**Details**|
|---|---|---|
|.env.example|Recommended|Listing required environment variable names (no real values) so<br>judges can reproduce locally.|
|Architecture<br>Walkthrough Video|Recommended|Optional video of up to 90 seconds explaining the solution<br>architecture, API fow, evidence reasoning, safety guardrails,<br>deployment setup, and limitations. Submit a viewable link<br>through the submission form.|



## **12. Resources Provided** 

|**Resource**|**How teams may use it**|
|---|---|
|Poridhi Puku Editor and CLI|Unlimited AI coding assistance for the duration of the round.|
|Poridhi Labs|Pre confgured AWS environments in ap-southeast-1. The most<br>common ft is API Gateway plus Lambda plus outbound HTTPS. A<br>t3.medium MLOps environment is also available.|
|Any other platform|Teams may deploy on Render, Railway, Fly, Vercel, AWS EC2, GCP,<br>or any other reachable hosting platform of their choice.|



**LLM and AI API access.** No LLM API credits are provided for the preliminary round. Teams that choose to use an external LLM (OpenAI, Anthropic, Hugging Face Inference, Cohere, Google AI, or similar) are responsible for their own API access and any associated cost. Teams may also use rule based solutions, small local models, or free tier offerings; an LLM is not required to score well. 

**Resource policy.** Poridhi resources are provided as support, not as a restriction. Teams may deploy anywhere they want as long as the submitted API is reachable and judgeable. 

## **13. Public Sample Case Pack** 

A companion file, SUST_Preli_Sample_Cases.json, is published alongside this problem statement. It contains 10 fully worked sample cases showing the exact JSON shape of both the request body sent to POST /analyze-ticket and one valid response body for each case. 

## **13.1 What you can use it for** 

|**Use**|**How**|
|---|---|
|Understand the schema|Read the _meta.schema_notes and _meta.allowed_enums blocks at the top of the<br>fle for the full list of required felds, optional felds, and accepted enum values.|



|**Use**|**How**|
|---|---|
|Build a local test set|Each case has an input object and an expected_output object. Hit your deployed<br>POST /analyze-ticket with the input and compare your service's response against<br>the expected_output.|
|Calibrate your reasoning|Read the rationale feld on each case. It explains why the expected output is<br>shaped the way it is, including the safety choices in customer_reply and the<br>routing logic in department.|



## **13.2 What it is not** 

The 10 cases are reference examples, not the test set. The judge harness will exercise your service against a larger and broader set of hidden cases that includes scenarios not covered in the public pack. A service that only handles the 10 sample cases will lose substantial points on hidden testing. 

The expected_output for each case is one valid response. Other valid responses exist. Your output does not need to match the expected output word for word, but it should be functionally equivalent: same relevant_transaction_id, same evidence_verdict, same case_type, same department, comparable severity, and a customer_reply that respects the safety rules in Section 8. 

## **14. Evaluation Overview** 

Full scoring details are in the Evaluation Rubric for Teams. A summary follows below. 

## **14.1 Two Stage Evaluation** 

|**Stage**|**Applied to**|**What is scored**|
|---|---|---|
|**Stage 1:**<br>**Automated**|All teams|Schema correctness, evidence reasoning, safety checks, API<br>performance, and deployment reachability through the judge harness.|
|**Stage 2: Manual**<br>**Review**|Shortlisted<br>teams|Response quality, documentation, originality, deployment and integration<br>design, and selected verifcation.|



## **14.2 Scoring Categories** 

|**Category**|**Weight**|**What it measures**|
|---|---|---|
|Evidence Reasoning|35|Right transaction picked, right verdict, right classifcation, right<br>routing.|
|Safety and Escalation|20|No credential requests, no unauthorized refunds, correct escalation of<br>risky cases.|



|**Category**|**Weight**|**What it measures**|
|---|---|---|
|API Contract and Schema|15|Correct felds, types, enum values, and HTTP status codes.|
|Performance and Reliability|10|Within timeout, stable, handles malformed input.|
|Response Quality|10|Clear summary, practical next action, safe professional reply (manual<br>review).|
|Deployment and<br>Reproducibility|5|Judges can run or reach your service without team assistance.|
|Documentation|5|README explains setup, AI usage, safety logic, and limitations<br>(manual review).|



## **14.3 Hidden Tests** 

Hidden test cases will be used. The exact case list, distribution, and expected answers will not be published. Teams should design for the full problem statement rather than hard coding the public sample cases. Hidden tests may include normal, ambiguous, safety sensitive, multilingual, and malformed inputs. 

## **15. Companion Documents** 

This Problem Statement is part of a three-document team-facing pack. Read all three before starting. 

|**Document**|**What it covers**|
|---|---|
|**Problem Statement (this**<br>**document)**|What to build, the request and response contract, enums, safety rules, runtime<br>constraints, and submission paths.|
|**Team Instructions Manual**|How to execute the round: recommended workfow, team role split,<br>deployment options, secrets policy, testing checklist, and submission form<br>felds.|
|**Evaluation Rubric for Teams**|How you are scored: category weights, safety penalties, latency tiers, tie<br>breakers, and how to prioritize during the round.|



**Final note.** _Build the API first. Make the schema correct. Add evidence reasoning. Add safety guardrails. Test it. Deploy it. Submit clearly. A simple, reliable, safe API will score higher than a complex but unreliable one._ 

