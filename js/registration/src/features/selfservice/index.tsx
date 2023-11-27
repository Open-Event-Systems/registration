import { makeApp } from "#src/utils/react"
import { RouterProvider } from "react-router-dom"
import { router } from "#src/features/selfservice/routes/Router"
import { MantineProvider } from "@mantine/core"
import theme from "#src/config/theme"

import "@mantine/core/styles.css"
import "@open-event-systems/interview-components/styles.css"
import "#src/components/styles.css"
import "#src/features/auth/styles.css"
import "#src/features/interview/styles.css"
import "#src/features/cart/styles.css"

makeApp(() => (
  <MantineProvider theme={theme}>
    <RouterProvider router={router} />
  </MantineProvider>
))
