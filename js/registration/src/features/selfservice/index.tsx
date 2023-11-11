import { makeApp } from "#src/util/react"
import { RouterProvider } from "react-router-dom"
import { router } from "#src/features/selfservice/routes/Router"
import { MantineProvider } from "@mantine/core"
import "@mantine/core/styles.css"
import "@open-event-systems/interview-components/styles.css"
import "#src/components/styles.css"
import "#src/features/auth/styles.css"
import "#src/features/interview/styles.css"
import theme from "#src/config/theme"

makeApp(() => (
  <MantineProvider theme={theme}>
    <RouterProvider router={router} />
  </MantineProvider>
))
