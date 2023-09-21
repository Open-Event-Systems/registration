import {
  Box,
  createStyles,
  DefaultProps,
  Selectors,
  TypographyStylesProvider,
  useComponentDefaultProps,
} from "@mantine/core"
import { createContext, useContext } from "react"
import markdown from "markdown-it"

const markdownStyles = createStyles({
  root: {},
})

export type MarkdownProps = {
  children?: string
} & DefaultProps<Selectors<typeof markdownStyles>>

/**
 * Component that renders markdown formatted text.
 *
 * Use {@link MarkdownContext} to customize the markdown-it object used.
 */
export const Markdown = (props: MarkdownProps) => {
  const { styles, unstyled, className, classNames, children, ...other } =
    useComponentDefaultProps("OESIMarkdown", {}, props)

  const { classes, cx } = markdownStyles(undefined, {
    name: "OESIMarkdown",
    classNames,
    styles,
    unstyled,
  })

  const markdownInst = useContext(MarkdownContext)

  const html = children ? markdownInst.render(children) : ""

  return (
    <TypographyStylesProvider>
      <Box
        className={cx(classes.root, className)}
        {...other}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </TypographyStylesProvider>
  )
}

export const MarkdownContext = createContext(
  markdown({
    linkify: true,
  }),
)
