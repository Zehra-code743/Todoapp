# ADR-001: MCP Architecture and AI Integration Stack

> **Scope**: Document decision cluster for AI chatbot architecture, combining MCP tool design, conversation state management, and OpenAI integration as an integrated technical solution.

- **Status:** Accepted
- **Date:** 2025-12-31
- **Feature:** 003-phase-iii-ai-chatbot
- **Context:** Phase III transforms the todo web application from traditional UI interactions (buttons, forms) to natural language conversation. This requires choosing an AI integration architecture that maintains our constitutional principles (stateless, tool-driven, MCP as control plane) while delivering conversational task management capabilities.

<!-- Significance checklist (ALL must be true to justify this ADR)
     ✅ 1) Impact: Long-term consequence - defines how AI interacts with system, affects all future AI features
     ✅ 2) Alternatives: Multiple viable options considered (LangChain, custom implementation, different state patterns)
     ✅ 3) Scope: Cross-cutting - affects frontend, backend, database, AI layer, and operational patterns
-->

## Decision

We will implement the AI chatbot using an **integrated MCP-based architecture** with the following components working together as a cohesive solution:

### AI Integration Layer
- **Framework**: OpenAI Agents SDK (official library)
- **Model**: gpt-4o-mini ($0.15/1M input, $0.60/1M output tokens)
- **Agent Configuration**: Temperature 0.7, auto tool choice, 128k context window
- **Tool Integration**: MCP tools registered with agent for task operations

### MCP Control Plane
- **MCP Server**: Official MCP Python SDK (`mcp` package)
- **Tools Exposed**: 5 task operations (add_task, list_tasks, complete_task, delete_task, update_task)
- **Tool Pattern**: Stateless, auditable, deterministic with JSON schema validation
- **Transport**: stdio mode integrated with FastAPI process

### Conversation State Management
- **Architecture**: Fully stateless server with database-backed conversation persistence
- **Storage**: PostgreSQL tables (conversations, messages)
- **Context Loading**: Last 50 messages loaded from database per request
- **Retention**: 90 days active + 1 year archived before deletion
- **Pagination**: 50 messages per batch, infinite scroll for history

### Chat Interface
- **UI Framework**: OpenAI ChatKit React components
- **Integration**: Next.js 16 App Router page
- **Authentication**: JWT tokens from Better Auth (existing Phase II)
- **API Communication**: REST endpoint `/api/{user_id}/chat`

### Reliability Mechanisms
- **Rate Limiting**: Request queue with exponential backoff (1s, 2s, 4s, 8s, 16s)
- **Error Handling**: Graceful degradation with user-friendly error messages
- **Retry Strategy**: Max 5 retries for transient failures, 30s timeout
- **Observability**: Structured JSON logs with correlation IDs, 1% sampling for success

## Consequences

### Positive

**Architectural Benefits:**
- ✅ **Constitutional Compliance**: Fully stateless (Principle III), MCP as control plane (Principle VI), tool-driven actions (Principle V)
- ✅ **Horizontal Scalability**: No in-memory state enables multiple server instances without synchronization
- ✅ **Fault Tolerance**: Server restarts don't lose conversations; state always in database
- ✅ **Auditability**: All AI actions logged via MCP tool invocations with correlation IDs
- ✅ **Determinism**: Same MCP tool inputs produce same outputs; reproducible behavior

**Development Benefits:**
- ✅ **Official SDKs**: OpenAI Agents SDK + MCP SDK provide stable, maintained libraries
- ✅ **Type Safety**: TypeScript (frontend) + Python type hints (backend) with schema validation
- ✅ **Fast Iteration**: ChatKit UI component eliminates custom chat UI development
- ✅ **Existing Integration**: Reuses Phase II infrastructure (FastAPI, PostgreSQL, Better Auth, Next.js)
- ✅ **Clear Boundaries**: MCP abstraction separates AI decision-making from state mutations

**Operational Benefits:**
- ✅ **Cost-Effective**: gpt-4o-mini pricing ~80% cheaper than gpt-4 with sufficient capabilities
- ✅ **Observability**: Structured logging with correlation IDs enables end-to-end request tracing
- ✅ **Reliability**: Exponential backoff handles OpenAI rate limits gracefully without request loss
- ✅ **Performance**: 50-message pagination prevents unbounded query sizes; indexes optimize lookups

**User Benefits:**
- ✅ **Context Preservation**: Conversations survive logout/restart; users can resume naturally
- ✅ **Responsive UX**: ChatKit streaming responses provide instant feedback
- ✅ **Natural Language**: Agent understands task intents without command syntax
- ✅ **Error Recovery**: Queue + retry ensures messages eventually processed even during rate limits

### Negative

**Vendor Dependencies:**
- ⚠️ **OpenAI Lock-in**: Agents SDK and ChatKit tie us to OpenAI ecosystem
  - Mitigation: MCP abstraction layer makes switching AI providers easier (tools stay same, swap agent implementation)
  - Risk: Pricing changes or service degradation require migration effort

- ⚠️ **ChatKit Customization**: Limited to component's capabilities; custom UI features may be constrained
  - Mitigation: ChatKit supports Tailwind styling; can extend with custom components if needed
  - Risk: May need custom chat UI if requirements exceed ChatKit capabilities

**Technical Complexity:**
- ⚠️ **MCP Protocol Learning Curve**: Team must learn MCP concepts (tools, schemas, transport)
  - Mitigation: Official SDK simplifies with decorator pattern; research.md provides examples
  - Risk: Initial slower development until team familiar with MCP patterns

- ⚠️ **Distributed System Complexity**: Stateless architecture requires careful state management
  - Mitigation: All state in database; no distributed locks or synchronization needed
  - Risk: Must ensure conversation loading doesn't create race conditions

**Operational Costs:**
- ⚠️ **OpenAI API Costs**: Usage-based pricing scales with user activity
  - Mitigation: gpt-4o-mini cost-effective; implement monitoring and alerts for budget control
  - Risk: Viral growth could cause unexpected cost spike (add rate limiting per user if needed)

- ⚠️ **Database Storage Growth**: Conversation history accumulates over time
  - Mitigation: 90-day retention + archival policy prevents unbounded growth
  - Risk: Archive storage costs increase linearly with user base

**Performance Considerations:**
- ⚠️ **External API Latency**: OpenAI API adds 1-2s latency to response time
  - Mitigation: Streaming responses provide instant feedback; target <3s total acceptable
  - Risk: OpenAI service degradation directly impacts user experience

- ⚠️ **Context Window Limits**: 50-message limit may truncate long conversations
  - Mitigation: Covers 90%+ of conversations; user can paginate if needed
  - Risk: Very long conversations may lose context for AI (can summarize older messages if needed)

## Alternatives Considered

### Alternative Stack A: LangChain + Anthropic Claude + Custom State

**Components:**
- AI Framework: LangChain for orchestration
- Model: Anthropic Claude 3.5 Sonnet
- State: Redis for conversation cache + PostgreSQL for persistence
- UI: Custom React chat components

**Tradeoffs:**
- **Pros**: More flexibility, potentially better AI performance, avoid OpenAI lock-in
- **Cons**: LangChain adds abstraction complexity, Redis violates stateless principle, custom UI development time
- **Why Rejected**: Violates Constitution Principle III (stateless), spec requires OpenAI ecosystem, higher initial development cost

### Alternative Stack B: Direct OpenAI API + In-Memory Sessions

**Components:**
- AI: Direct OpenAI Chat Completions API (no agent SDK)
- State: In-memory session store (user session objects)
- Tools: Direct function calls in endpoint handler
- UI: OpenAI ChatKit

**Tradeoffs:**
- **Pros**: Simpler initial implementation, fewer dependencies
- **Cons**: No agent abstractions, in-memory state prevents scaling, sessions lost on restart, no MCP standardization
- **Why Rejected**: Violates Principle III (stateless) and Principle VI (MCP as control plane), doesn't survive restarts

### Alternative Stack C: Custom MCP Implementation + Local LLM

**Components:**
- MCP: Custom protocol implementation
- Model: Self-hosted LLaMA or Mistral
- State: PostgreSQL (stateless)
- UI: Custom chat UI

**Tradeoffs:**
- **Pros**: No external AI service dependency, full control, zero API costs
- **Cons**: MCP protocol maintenance burden, LLM hosting infrastructure, lower AI quality, custom UI development
- **Why Rejected**: Dramatically increases complexity and maintenance burden; self-hosted LLMs require GPU infrastructure; MCP protocol complexity not worth avoiding official SDK

### Why Our Decision Wins

The chosen stack (OpenAI Agents SDK + Official MCP SDK + Database State + ChatKit) provides:

1. **Constitutional Compliance**: Only option that satisfies all 7 principles without violations
2. **Time to Market**: Reuses Phase II infrastructure; official SDKs accelerate development
3. **Production-Ready**: Stateless architecture enables scaling; queue + retry handles failures
4. **Cost-Effective Balance**: gpt-4o-mini pricing acceptable vs self-hosted complexity
5. **Integration Cohesion**: All components from OpenAI/MCP ecosystems work together seamlessly

## References

- Feature Spec: [specs/003-phase-iii-ai-chatbot/spec.md](../../specs/003-phase-iii-ai-chatbot/spec.md)
- Implementation Plan: [specs/003-phase-iii-ai-chatbot/plan.md](../../specs/003-phase-iii-ai-chatbot/plan.md)
- Research: [specs/003-phase-iii-ai-chatbot/research.md](../../specs/003-phase-iii-ai-chatbot/research.md)
- Data Model: [specs/003-phase-iii-ai-chatbot/data-model.md](../../specs/003-phase-iii-ai-chatbot/data-model.md)
- Related ADRs: None (first ADR for this project)
- Evaluator Evidence: [history/prompts/003-phase-iii-ai-chatbot/003-phase-iii-architectural-plan.plan.prompt.md](../prompts/003-phase-iii-ai-chatbot/003-phase-iii-architectural-plan.plan.prompt.md)

## Decision Validation Checklist

- [x] Impact: Long-term architectural pattern (MCP + stateless + AI agent integration)
- [x] Alternatives: 3 alternative stacks evaluated with detailed tradeoffs
- [x] Scope: Cross-cutting (affects all layers: frontend, backend, database, AI, operations)
- [x] Clustered: Combines 3 related decisions that work together as integrated solution
- [x] Consequences: Both positive (11 benefits) and negative (8 risks with mitigations) documented
- [x] References: Links to spec, plan, research, data model, and PHR evaluation
- [x] Testable: Architecture can be validated against constitutional principles and performance requirements
