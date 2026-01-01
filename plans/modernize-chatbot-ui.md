# Plan: Modernize Chatbot UI and Display Tool Calls

The user reported that "create a hello todo" creates no visible change in the UI. Investigation revealed the backend successfully creates tasks but the frontend ignores the `tool_calls` results in the response.

## 1. Objectives
- Update frontend `Message` type to support `tool_calls`.
- Implement a modern UI for the `ChatWindow` using existing `shadcn/ui` components.
- Render tool execution results (like task creation) visually in the chat.
- Add "modern" touches like animations and better message bubbles.

## 2. Proposed Changes

### Frontend
- **`frontend/src/components/ChatWindow.tsx`**:
    - Update `Message` interface to include optional `tool_calls` field.
    - Modify `sendMessage` to save `tool_calls` from the backend response into the message state.
    - Refactor the render loop to use `Card`, `Badge`, and `Button` components.
    - Create a `ToolCallResult` sub-component to render tool results (e.g., "Task Created: hello").
    - Improve message bubbles with better padding, shadows, and alignment.
- **`frontend/src/app/chat/page.tsx`**: (Optional) Ensure layout matches the new modern chat window.

### Backend
- (No changes needed as backend is already returning the correct data)

## 3. Implementation Steps
1. **Prepare Types**: Update the `Message` interface in `ChatWindow.tsx`.
2. **Handle Tool Data**: Update the state management to store tool call results.
3. **Refactor UI**: Replace raw Tailwind divs with `Card` and `Button` components from `src/components/ui/`.
4. **Implement Tool Rendering**: Add logic to render tool calls below the assistant's message.
5. **Add Polishing**: Check for animations in `globals.css` and apply them to new messages.

## 4. Acceptance Criteria
- [ ] Chatting still works as before (text responses).
- [ ] Asking "create a todo" shows a visual confirmation (Card/Badge) in the chat window.
- [ ] The UI looks more professional/modern using shadcn components.
- [ ] No regression in authentication or chat history loading.
