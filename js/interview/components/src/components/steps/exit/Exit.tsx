import { Markdown, MarkdownProps } from "#src/components/markdown/Markdown.js"
import { Box, BoxProps, Button, ButtonProps, useProps } from "@mantine/core"
import clsx from "clsx"
import { ComponentPropsWithoutRef } from "react"

export type ExitProps = {
  content?: string
  classNames?: {
    root?: string
    text?: string
    button?: string
  }
  onClose?: () => void
} & ExitRootProps

export const Exit = (props: ExitProps) => {
  const { className, classNames, content, onClose, ...other } = useProps(
    "OESIExit",
    {},
    props,
  )

  return (
    <Exit.Root className={clsx(classNames?.root, className)} {...other}>
      <Exit.Text className={classNames?.text} content={content} />
      <Exit.Button
        className={classNames?.button}
        onClick={() => onClose && onClose()}
      />
    </Exit.Root>
  )
}

export type ExitRootProps = BoxProps & ComponentPropsWithoutRef<"div">

const ExitRoot = (props: ExitRootProps) => {
  const { className, children, ...other } = useProps("OESIExitRoot", {}, props)

  return (
    <Box className={clsx(className, "OESIExit-root")} {...other}>
      {children}
    </Box>
  )
}

export type ExitTextProps = MarkdownProps

const ExitText = (props: ExitTextProps) => {
  const { className, ...other } = useProps("OESIExitText", {}, props)

  return <Markdown className={clsx(className, "OESIExit-text")} {...other} />
}

export type ExitButtonProps = ButtonProps & ComponentPropsWithoutRef<"button">

const ExitButton = (props: ExitButtonProps) => {
  const { className, ...other } = useProps("OESIExitButton", {}, props)

  return (
    <Button
      className={clsx(className, "OESIExit-button")}
      variant="outline"
      {...other}
    >
      Exit
    </Button>
  )
}

Exit.Root = ExitRoot
Exit.Text = ExitText
Exit.Button = ExitButton
