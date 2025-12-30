# Todo Application Frontend

Phase II Next.js frontend with React, TypeScript, and Better Auth.

## Prerequisites

- Node.js 18.x or 20.x (LTS)
- npm, pnpm, or yarn

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
# or
pnpm install
# or
yarn install
```

### 2. Configure Environment Variables

Create `.env.local` file from template:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` and set:
- `NEXT_PUBLIC_API_URL`: Backend API URL (e.g., `http://localhost:8000`)
- `BETTER_AUTH_SECRET`: Generate with `openssl rand -hex 32` (must match backend)
- `BETTER_AUTH_URL`: Frontend URL (e.g., `http://localhost:3000`)

**CRITICAL**: `BETTER_AUTH_SECRET` must be identical in both frontend and backend.

## Running Locally

```bash
cd frontend
npm run dev
```

App will start on: http://localhost:3000

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm run type-check` - TypeScript type checking

## Testing

```bash
npm test
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── (auth)/          # Auth pages (signin, signup)
│   │   ├── dashboard/       # Dashboard page
│   │   ├── layout.tsx       # Root layout
│   │   └── page.tsx         # Home page
│   ├── components/
│   │   └── ui/              # Reusable UI components
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utilities, config
│   └── types/               # TypeScript types
├── public/                  # Static assets
└── tests/                   # Vitest tests
```

## Features

### Phase II MVP (Current)
- ✅ User authentication (signup, signin, logout)
- ✅ JWT-based session management
- ✅ Route protection (middleware)
- ✅ Responsive design (Tailwind CSS)

### Coming in Phase 4-7
- Task creation and viewing
- Task editing
- Task completion toggle
- Task deletion

## Development

### Type Safety

All API calls are fully typed with TypeScript interfaces from `/types/task.ts`.

### State Management

- React Query (TanStack Query) for server state
- React hooks for local UI state
- Optimistic updates for immediate feedback

### Styling

- Tailwind CSS utility-first approach
- Mobile-first responsive design
- Dark mode ready (CSS variables)

## Deployment

See root README.md for Vercel deployment instructions.
