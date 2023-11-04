import { Box, BoxProps, useProps } from "@mantine/core"
import { ComponentPropsWithoutRef, createContext, useContext } from "react"
import markdown from "markdown-it"
import clsx from "clsx"

export type MarkdownProps = {
  content?: string
} & Omit<BoxProps & ComponentPropsWithoutRef<"div">, "children">

/**
 * Component that renders markdown formatted text.
 *
 * Use {@link MarkdownContext} to customize the markdown-it object used.
 */
export const Markdown = (props: MarkdownProps) => {
  const { className, content, ...other } = useProps("OESIMarkdown", {}, props)

  const markdownInst = useContext(MarkdownContext)

  const html = content ? markdownInst.render(content) : ""

  return (
    <Box
      className={clsx(className, "OESIMarkdown-root")}
      {...other}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}

export const MarkdownContext = createContext(
  markdown({
    linkify: true,
  }),
)
