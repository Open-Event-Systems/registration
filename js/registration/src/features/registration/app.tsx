import { MantineProvider } from "@mantine/core"
import { RouterProvider } from "react-router-dom"
import { makeApp } from "#src/util/react"
import { router } from "#src/features/registration/routes/Router"
import theme from "#src/config/theme"

import "@mantine/core/styles.css"
import "@open-event-systems/interview-components/styles.css"
import "#src/components/styles.css"
import "#src/features/auth/styles.css"
import "#src/features/interview/styles.css"
import "#src/features/cart/styles.css"
import "#src/features/registration/components/search/Results.scss"
import "#src/features/registration/components/registration/fields/RegistrationFields.scss"

makeApp(() => (
  <MantineProvider theme={theme}>
    <RouterProvider router={router} />
  </MantineProvider>
))
