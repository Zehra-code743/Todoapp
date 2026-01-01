---
id: 004
title: ADR MCP Architecture AI Integration
stage: plan
date: 2025-12-31
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-phase-iii-ai-chatbot
branch: 003-phase-iii-ai-chatbot
user: pc
command: /sp.adr
labels: ["adr", "architecture", "mcp", "openai", "stateless", "decision-record"]
links:
  spec: specs/003-phase-iii-ai-chatbot/spec.md
  ticket: null
  adr: history/adr/001-mcp-architecture-and-ai-integration.md
  pr: null
files:
 - history/adr/001-mcp-architecture-and-ai-integration.md
tests:
 - ADR validation checklist (7/7 items passed)
---

## Prompt

/sp.adr mcp-architecture-and-ai-integration

## Response snapshot

Created Architecture Decision Record documenting the integrated technical approach for Phase III AI chatbot feature.

**Decision Cluster Analysis:**

Identified 3 related architectural decisions that work together as an integrated solution:
1. MCP Tool Architecture for task operations
2. Stateless Server with Database-Backed Conversations
3. OpenAI Agents SDK vs Alternative AI Frameworks

**Clustering Rationale:**
- These decisions are interdependent and would change together
- MCP tools require agent framework that supports tool registration
- Stateless architecture requires conversation persistence strategy
- All three components form the core AI integration pattern
- Separating into individual ADRs would lose the integration context

**ADR-001 Contents:**

**Decision**: Integrated MCP-based architecture with 5 components:
1. AI Integration Layer (OpenAI Agents SDK + gpt-4o-mini)
2. MCP Control Plane (Official MCP Python SDK + 5 tools)
3. Conversation State Management (Stateless server + PostgreSQL)
4. Chat Interface (OpenAI ChatKit React components)
5. Reliability Mechanisms (Request queue + exponential backoff + structured logging)

**Consequences Documented:**

Positive (11 benefits):
- Constitutional compliance (Principles III, V, VI)
- Horizontal scalability and fault tolerance
- Official SDK stability and maintenance
- Type safety and schema validation
- Cost-effectiveness (gpt-4o-mini pricing)
- Fast iteration (reuse Phase II infrastructure)
- Clear architectural boundaries
- End-to-end observability
- Graceful error handling
- Context preservation across sessions
- Natural language understanding

Negative (8 risks with mitigations):
- OpenAI vendor lock-in (mitigated by MCP abstraction)
- ChatKit customization limits (mitigated by Tailwind + extensibility)
- MCP learning curve (mitigated by examples in research.md)
- Distributed system complexity (mitigated by stateless design)
- OpenAI API usage costs (mitigated by gpt-4o-mini + monitoring)
- Database storage growth (mitigated by 90-day retention policy)
- External API latency (mitigated by streaming + <3s acceptable)
- Context window limits (mitigated by 50-message pagination)

**Alternatives Evaluated (3 stacks):**

Alternative A: LangChain + Anthropic Claude + Redis Cache
- Rejected: Redis violates stateless principle, LangChain adds complexity, spec requires OpenAI

Alternative B: Direct OpenAI API + In-Memory Sessions
- Rejected: No agent abstractions, in-memory violates stateless, no MCP standardization

Alternative C: Custom MCP + Self-Hosted LLM
- Rejected: Maintenance burden, GPU infrastructure needs, lower AI quality, custom UI cost

**Why Our Decision Wins:**
- Only option satisfying all 7 constitutional principles
- Fastest time to market with official SDKs
- Production-ready scalability and reliability
- Cost-effective balance vs self-hosted complexity
- Integrated ecosystem cohesion

**Validation Checklist:**
- ✅ Impact: Long-term architectural pattern
- ✅ Alternatives: 3 alternative stacks with detailed tradeoffs
- ✅ Scope: Cross-cutting (frontend, backend, database, AI, ops)
- ✅ Clustered: Combines related decisions as integrated solution
- ✅ Consequences: 11 positive + 8 negative with mitigations
- ✅ References: Links to spec, plan, research, data model, PHR
- ✅ Testable: Validatable against constitutional principles

## Outcome

- ✅ Impact: Created ADR-001 documenting integrated MCP + OpenAI + stateless architecture as cohesive technical solution
- 🧪 Tests: Validation checklist PASS (7/7 items), significance test PASS (impact + alternatives + scope)
- 📁 Files: Created history/adr/001-mcp-architecture-and-ai-integration.md
- 🔁 Next prompts: `/sp.tasks` to generate implementation task breakdown now that architectural decisions are documented
- 🧠 Reflection: Successfully clustered 3 related decisions into single ADR capturing the integrated nature of the technical solution. Avoided over-granular ADRs by recognizing that MCP, stateless architecture, and OpenAI integration are interdependent components of the AI chatbot pattern. Documented both benefits and risks with specific mitigations. ADR provides clear reference for future engineers questioning why these choices were made together.

## Evaluation notes (flywheel)

- Failure modes observed: None - decision clustering appropriate, all validation checks passed
- Graders run and results (PASS/FAIL): ADR validation checklist PASS (7/7), significance test PASS (all 3 criteria met)
- Prompt variant (if applicable): Clustered ADR approach (3 decisions into 1 integrated ADR)
- Next experiment (smallest change to try): N/A - ADR creation successful, clustering strategy effective
