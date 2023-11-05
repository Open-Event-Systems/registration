import { Container, ContainerProps, useProps } from "@mantine/core"
import clsx from "clsx"

export type ContainerLayoutProps = ContainerProps

export const ContainerLayout = (props: ContainerLayoutProps) => {
  const { className, children, ...other } = useProps(
    "ContainerLayout",
    {},
    props,
  )

  return (
    <Container
      className={clsx("ContainerLayout-root", className)}
      size="lg"
      {...other}
    >
      {children}
    </Container>
  )
}
