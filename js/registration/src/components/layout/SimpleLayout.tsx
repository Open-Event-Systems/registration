import { ContainerLayout } from "#src/components/layout/ContainerLayout"
import { StackLayout } from "#src/components/layout/StackLayout"
import {
  AppShellLayout,
  AppShellLayoutProps,
} from "#src/components/layout/app-shell/AppShellLayout"
import { ReactNode } from "react"

export const SimpleLayout = ({
  children,
  AppShellLayoutProps,
}: {
  children?: ReactNode
  AppShellLayoutProps?: AppShellLayoutProps
}) => (
  <AppShellLayout {...AppShellLayoutProps}>
    <ContainerLayout>
      <StackLayout>{children}</StackLayout>
    </ContainerLayout>
  </AppShellLayout>
)
