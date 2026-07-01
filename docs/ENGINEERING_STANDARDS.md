# AURA Engineering Standards Handbook

This handbook defines the coding conventions, folder layout standards, API guidelines, state management rules, and testing philosophies for the AURA codebase.

---

## 1. Naming Conventions

Consistency in naming helps developers read and understand files across backend and frontend boundaries.

### Python (Backend)
* **Classes**: PascalCase (e.g. `BriefingService`, `ExtractionResult`).
* **Variables & Functions**: snake_case (e.g. `user_id`, `generate_brief`).
* **Database Models**: PascalCase matching table name (e.g. `Context`, `ExecutiveBrief`).
* **Database Columns**: snake_case (e.g. `is_active`, `created_at`).

### TypeScript / React (Frontend)
* **React Components**: PascalCase matching the file name (e.g. `CaptureSession.tsx`, `Dashboard.tsx`).
* **Zustand Store hooks**: camelCase starting with `use` (e.g. `useAuraStore`).
* **Variables, Functions, & Properties**: camelCase (e.g. `chatInput`, `setMessages`).
* **CSS classes**: kebab-case (e.g. `capture-session-container`, `extraction-chip-btn`).

---

## 2. Folder structure conventions

AURA organizes applications logically by responsibility:

### Frontend (`apps/web/`)
- `src/components/`: Reusable, layout-agnostic presentational React components.
- `src/__tests__/`: Frontend vitest unit and component tests.
- `src/store/`: Zustand global state manager implementations.
- `src/index.css`: Root styling, design tokens, utility classes, and glassmorphic designs.

### Backend (`apps/api/`)
- `app/models/`: SQLAlchemy declarative ORM database models.
- `app/routers/`: FastAPI router endpoints grouping functional APIs together.
- `app/services/`: Core business logic layers (e.g. Briefing service, LLM wrapper).
- `app/extraction/`: Cognitive extraction logic, schemas, and contract rules.
- `alembic/`: Database migrations.
- `tests/`: Pytest integration and mock service validation tests.

---

## 3. API Guidelines

FastAPI routers must maintain these architectural guards:
- **Pydantic Schemas**: Every endpoint must define and validate input parameters and output responses via Pydantic models (e.g. `BriefResponse`).
- **Dependencies**: Use FastAPI dependency injection (`Depends`) to inject database sessions (`AsyncSession`) and current user context (`get_current_user`).
- **HTTP status codes**: Use semantic status codes (e.g. `status.HTTP_201_CREATED` for resource creation, `status.HTTP_404_NOT_FOUND` when missing).

---

## 4. Component Conventions (Frontend)

To build premium, responsive UIs with high performance:
- **Single Responsibility**: Keep components focused. If a file exceeds 400 lines, extract presentational child subcomponents.
- **Glassmorphic Aesthetics**: Standard interactive layouts must leverage:
  * Sleek semi-transparent borders: `border border-white/10`
  * High-end backdrop blur: `backdrop-blur-md`
  * Soft gradient overlays: `bg-gradient-to-br from-white/5 to-white/10`
- **Responsiveness**: All pages must scale seamlessly from mobile devices (`sm:`, `md:`) to large desktops.
- **Accessibility (a11y)**: Use semantic elements (`<button>`, `<main>`), configure clear focus rings, and provide appropriate alt attributes or screen-reader descriptions.

---

## 5. State Management Rules

We use **Zustand** as the primary state manager:
- **Selectors**: Always import store slices via specific selectors (e.g. `const messages = useAuraStore(state => state.messages)`) instead of destructured states. This prevents unnecessary component re-renders.
- **Actions**: Always define mutate actions inside the store (e.g. `apps/web/src/store/auraStore.ts`) rather than modifying store properties directly inside components.
- **Asynchronous Actions**: Use async/await for network requests inside actions and manage a central `loading` and `error` state.

---

## 6. Testing Philosophy

Testing is a core release gate, not an afterthought:
- **Backend (Pytest)**:
  * Write unit tests for services using mocks (like `llm.py` mocking).
  * Write integration tests for API endpoints checking JSON response payloads.
  * Run database tests with cascading delete assertions.
- **Frontend (Vitest)**:
  * Write component tests to verify user interactions (click events, input typing).
  * Ensure updates inside tests are wrapped in `act(...)` where appropriate to prevent React state console warnings.

---

## 7. Documentation Requirements

Maintain documentation parity:
* **Database migrations** = Update `ARCHITECTURE.md` database schemas diagram.
* **API routers** = Update `ARCHITECTURE.md` core routing sections.
* **Environment variables** = Update `docs/DEVELOPER_GUIDE.md` environment setup.
* **Architectural patterns** = Create a new **ADR** in `docs/adr/`.
