# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

## API Integration Foundation

Frontend now calls the FastAPI backend through the reusable client in `frontend/src/services/api.js`.

- The local backend URL configuration uses the `VITE_API_BASE_URL` environment variable.
- Copy `frontend/.env.example` to `frontend/.env` to configure this locally.
- Run the backend on port 8000 and the frontend through Vite.
- **Security:** No Supabase secret/key should ever be placed in frontend environment variables. All database communication happens via the backend.
- Visible dashboard data currently remains prototype/mock data until individual integration phases are completed.
