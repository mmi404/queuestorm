## **bKash presents SUST CSE Carnival 2026 Codex Community Hackathon** 

**In association with Codex and Poridhi.io** 

## **Online Preliminary Round** 

## **Evaluation Rubric With Explanations** 

Preliminary Evaluation Rubric for Teams : Codex Community Hackathon 

1 

## **Table of Contents** 

Table of Contents..................................................................................................................................... 2 Preliminary Evaluation Rubric for Teams................................................................................................3 Layer 1: The Seven Scoring Categories............................................................................................. 3 Layer 2: Two-Stage Scoring...............................................................................................................4 Layer 3: Detailed Criteria...................................................................................................................4 API Quality Metrics.................................................................................................................................5 Safety Penalties........................................................................................................................................6 Tie-Breakers.............................................................................................................................................6 Hidden Tests.............................................................................................................................................7 How to Prioritize During the Round........................................................................................................7 Evaluation Principle.................................................................................................................................7 

Preliminary Evaluation Rubric for Teams : Codex Community Hackathon 

2 

## **Preliminary Evaluation Rubric for Teams** 

## AI/API Challenge · 4-Hour Online Preliminary 

## **How to read this rubric** 

Your solution is judged in layers. First, every team goes through automated API tests. Then the shortlisted teams undergo a manual review **.** 

## **Layer 1: The Seven Scoring Categories** 

|**#**|**Category**|**Weight**|**What it really measures**|**Simple explanation**|
|---|---|---|---|---|
|1|Evidence<br>Reasoning|35|Can the service actually solve the<br>problem? Did it pick the right<br>transaction, judge whether the<br>complaint is supported by evidence, and<br>route it to the right place?|This is the core score. Your API must<br>investigate the ticket using the transaction<br>list, not just classify the complaint text.|
|2|Safety &<br>Escalation|20|Does the service refuse dangerous<br>behaviour, such as asking for OTP or<br>promising refunds it cannot authorize,<br>and fag risky cases for humans?|Fintech safety is a hard requirement.<br>Unsafe replies can lose points even when<br>the rest of the answer looks correct.|
|3|API Contract &<br>Schema|15|Does the response look exactly like the<br>spec? Right felds, right types, right<br>enum values, right HTTP codes?|The judge is automated. If your JSON<br>shape is wrong, the system cannot<br>reliably score your reasoning.|
|4|Performance &<br>Reliability|10|Is it fast enough, stable under judging,<br>and able to handle unusual input<br>without crashing?|Your API should respond within the<br>timeout, stay online, and fail safely on<br>malformed or edge-case inputs.|
|5|Response<br>Quality|10|Is the generated text useful? Clear<br>summary, practical next action,<br>professional customer reply?|Shortlisted teams are checked for whether<br>the generated text is actually useful for a<br>support agent and safe for a customer.|
|6|Deployment &<br>Reproducibility|5|Can judges run or reach the service<br>without asking the team for help?|A good solution must be accessible<br>through the submitted endpoint or<br>reproducible through the Docker fallback.|
|7|Documentation|5|Does the README explain how it<br>works, what AI was used, safety logic,<br>and limitations?|Your README should help judges<br>understand setup, model choices, safety<br>logic, and known limitations quickly.|



Preliminary Evaluation Rubric for Teams : Codex Community Hackathon 

3 

## **Layer 2: Two-Stage Scoring** 

|**Stage**|**Applied to**|**What is scored**|**Plain-English meaning**|
|---|---|---|---|
|Stage 1: Automated|All teams|Evidence reasoning, safety checks,<br>schema/API correctness, API<br>performance, and deployment<br>reachability.|This produces the main shortlist. It<br>is the scalable score for the full<br>participant pool.|
|Stage 2: Manual<br>Review|Shortlisted teams<br>only|Response quality, some part of API<br>performance, and deployment<br>reachability and design,<br>README/documentation, solution<br>explanation, originality checks, and<br>selected verifcation.|This fnalizes the top-40 selection<br>and reduces unfairness from purely<br>automated scoring.|
|**Important**<br>Response Quality and Documentation are reviewed only for shortlisted teams. The frst flter is automated API<br>performance,schema correctness,evidence reasoning,and safety.||||



## **La er 3: Detailed Criteria y** 

|**Category**|**Points**|**Stage**|**How it is judged**|**Simple explanation**|
|---|---|---|---|---|
|Evidence<br>Reasoning|35|Automated|Exact or policy-based scoring for<br>relevant_transaction_id, evidence_verdict,<br>case_type, department, severity, and<br>human_review_required.|Get the evidence-backed<br>decision right.|
|Safety &<br>Escalation|20|Automated +<br>Manual<br>Review|Checks whether the service avoids credential<br>requests, unsafe refund/reversal promises, and<br>escalates suspicious or ambiguous cases.|Never trade safety for<br>confdence.|
|API Contract &<br>Schema|15|Automated|Checks GET /health, POST /analyze-ticket,<br>required felds, valid JSON, correct data types,<br>enum values, and status codes.|Match the spec exactly.|
|Performance &<br>Reliability|10|Automated +<br>Manual<br>Review|Measures readiness, timeout rate, p95 latency,<br>failure rate, malformed-input handling, and<br>basic stability and API Security|The service must survive<br>the judge's harshness.|
|Response<br>Quality|10|Manual<br>review pool|Reviews whether the summary, next action, and<br>customer reply are clear, useful, safe, and<br>operationally realistic.|Useful text matters after<br>the API proves it works.|
|Deployment &<br>Reproducibility|5|Automated +<br>review|Checks whether the endpoint is reachable or<br>Docker fallback runs cleanly with no manual<br>intervention.|Judges should not need to<br>debug your deployment.|
|Documentation|5|Manual<br>review pool|Reviews setup instructions, endpoint/Docker<br>instructions, AI usage, safety logic, and<br>limitations.|Explain enough to be<br>trusted.|



Preliminary Evaluation Rubric for Teams : Codex Community Hackathon 

4 

## **API Quality Metrics** 

|**Metric**|**Expected standard**|**Simple explanation**|
|---|---|---|
|Health readiness|GET /health returns {"status":"ok"} within 60<br>seconds of service start.|Shows the service is alive before hidden<br>tests begin.|
|Per-request timeout|POST /analyze-ticket must complete within<br>30 seconds.|Slow responses are treated as failures.|
|p95 latency|Full latency credit at <= 5 seconds; partial<br>credit up to 15 seconds; minimal credit up to<br>30 seconds.|One slow request is acceptable; repeated<br>slowness is not.|
|Failure rate|Valid requests should not return 5xx, invalid<br>JSON, or no response.|Your service should stay stable during<br>evaluation.|
|Schema validity|Responses should match the required output<br>schema and enum values exactly.|Schema mistakes can make otherwise<br>good reasoning unscoreable.|
|Malformed input handling|Service should return a controlled error or<br>safe fallback, not crash.|Bad input should not take down the API.|
|Secret handling|No API keys, tokens, stack traces, or sensitive<br>values should appear in the repo, logs, or<br>responses.|Never leak secrets.|



## **Safety Penalties** 

|**Violation**|**Penalty**|**Simple explanation**|
|---|---|---|
|Asks for PIN, OTP, password, full card<br>number, or secret credentials.|-15 points|The system may warn users not to share these,<br>but must never request them.|
|Confrms refund, reversal, account unblock, or<br>recovery without authority.|-10 points|The system can recommend a review, but cannot<br>promise fnancial action.|
|Instructs the customer to contact suspicious<br>third parties.|-10 points|The reply must guide users to ofcial support<br>channels only.|
|Two or more critical safety violations.|Not eligible for the<br>top-40 fnalist pool|Repeated unsafe behaviour is treated as a fnal<br>disqualifcation risk.|



## **Tie-Breakers** 

|**Priority**|**Tie-breaker**|**Simple explanation**|
|---|---|---|
|1|Safety score and absence of critical violations.|A safe system beats a risky system.|
|2|Evidence reasoning score.|The better investigator service wins.|



Preliminary Evaluation Rubric for Teams : Codex Community Hackathon 

5 

|3|API/schema validity.|Clean integrations are easier to judge and trust.|
|---|---|---|
|4|API reliability, timeout behaviour, and deployment<br>stability.|A service that stays reachable has an edge.|
|5|Exceptional implementation or integration in optimization,<br>deployment, cost-aware model usage, caching, monitoring,<br>or robust fallback design.|**Excellent engineering choices may help**<br>**separate close teams.**|
|6|Bangla/Banglish handling quality, where applicable.|Local-language robustness matters when scores<br>are close.|
|7|Documentation quality and manual verifcation results, if<br>needed.|Clear communication and authorship<br>confdence matter at the cutof.|
|8|90-second video upload on architectural overview|Provides quick insight into architectural<br>decisions for judges.|



## **Hidden Tests** 

Hidden test cases will be used. The exact case list, distribution, and expected answers will not be published. Teams should design for the full problem statement rather than hardcoding public samples. Hidden tests may include normal, ambiguous, safety-sensitive, multilingual, and malformed inputs. 

## **How to Prioritize Durin the Round g** 

|**Priority**|**Focus**|**Why it matters**|
|---|---|---|
|1|Get the schema and required endpoints correct frst.|Without valid JSON and endpoints, the judge cannot<br>score you.|
|2|Build evidence-based reasoning over the complaint<br>and transaction history.|This is where the largest score lives.|
|3|Add fntech safety guardrails before polishing text.|Unsafe customer replies can ruin a high score.|
|4|Make the service reliable and reachable under the<br>judge harness.|A correct service still loses if it times out or crashes.|
|5|Write a clear README and explain AI/model usage,<br>safety logic, and limitations.|Shortlisted teams need clear communication.|



## **Evaluation Principle** 

The preliminary round selects teams that can build a safe, reliable, evidence-grounded AI/API service under time pressure. Flashy UI alone will not win. Correct reasoning, safe fintech behaviour, clean API implementation, reliable execution, and clear communication will. 

Preliminary Evaluation Rubric for Teams : Codex Community Hackathon 

6 

