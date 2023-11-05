import { Stack, StackProps, useProps } from "@mantine/core"
import clsx from "clsx"

export type StackLayoutProps = StackProps

export const StackLayout = (props: StackLayoutProps) => {
  const { className, children, ...other } = useProps("StackLayout", {}, props)

  return (
    <Stack className={clsx("StackLayout-root", className)} {...other}>
      {children}
    </Stack>
  )
}
