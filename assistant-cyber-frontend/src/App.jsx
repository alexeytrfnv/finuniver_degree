import "./App.css"

import { ThemeProvider } from "styled-components"
import { LIGHT_THEME } from "@sg/uikit"
import { AdminPage } from "./pages/ChatPage"

import {
  createBrowserRouter,
  createRoutesFromElements,
  Route,
  RouterProvider,
} from "react-router-dom"

const router = createBrowserRouter(
  createRoutesFromElements(
      <Route
        path="/chat"
        element={
          <ThemeProvider theme={LIGHT_THEME}>
            <AdminPage />
          </ThemeProvider>
        }
      />
    </Route>
  )
)

function App() {
  return <RouterProvider router={router} />
}

export default App
