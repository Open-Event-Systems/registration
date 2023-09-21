import {
  Box,
  BoxProps,
  Button,
  ButtonProps,
  createStyles,
  DefaultProps,
  Selectors,
  useComponentDefaultProps,
} from "@mantine/core"
import { ExitResult } from "@open-event-systems/interview-lib"
import { Markdown } from "#src/components/Markdown.js"

const exitStyles = createStyles((theme) => ({
  root: {
    display: "grid",
    grid: `
      "description" auto
      "." 1fr
      "button" auto
      / 1fr
    `,
    justifyItems: "stretch",
    rowGap: theme.spacing.sm,
  },
  markdown: {
    gridArea: "description",
  },
  button: {
    justifySelf: "end",
    gridArea: "button",
  },
}))

export type ExitViewProps = {
  /**
   * The {@link ExitResult}.
   */
  content: ExitResult

  /**
   * Handler to call when the close/exit button is clicked.
   */
  onClose?: () => void

  /**
   * Props passed to the close/exit button.
   */
  ButtonProps?: Partial<ButtonProps>
} & BoxProps &
  DefaultProps<Selectors<typeof exitStyles>>

/**
 * Display the content for a {@link ExitResult}.
 */
export const ExitView = (props: ExitViewProps) => {
  const {
    styles,
    unstyled,
    className,
    classNames,
    content,
    onClose,
    ButtonProps,
    ...other
  } = useComponentDefaultProps("OESIExitView", {}, props)

  const { classes, cx } = exitStyles(undefined, {
    name: "OESIExitView",
    styles,
    unstyled,
    classNames,
  })

  return (
    <Box className={cx(classes.root, className)} {...other}>
      <Markdown className={classes.markdown}>
        {content.description || ""}
      </Markdown>
      <Button
        variant="outline"
        className={classes.button}
        {...ButtonProps}
        onClick={() => onClose && onClose()}
      >
        Close
      </Button>
    </Box>
  )
}
