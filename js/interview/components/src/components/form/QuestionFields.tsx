import {
  Box,
  BoxProps,
  createStyles,
  DefaultProps,
  Selectors,
  useComponentDefaultProps,
} from "@mantine/core"
import { observer } from "mobx-react-lite"
import { useContext } from "react"
import { InterviewFormContext } from "#src/components/form/Form.js"
import { ObjectField } from "#src/components/fields/ObjectField.js"

const questionFieldsStyles = createStyles((theme) => ({
  root: {
    display: "grid",
    gridTemplateColumns: "1fr",
    rowGap: theme.spacing.sm,
  },
  item: {},
}))

export type QuestionFieldsProps = DefaultProps<
  Selectors<typeof questionFieldsStyles>
> &
  Omit<BoxProps, "children">

/**
 * Displays the input fields for a question.
 *
 * Must have a {@link InterviewFormContext} available.
 */
export const QuestionFields = observer((props: QuestionFieldsProps) => {
  const { styles, unstyled, className, classNames, ...other } =
    useComponentDefaultProps("OESIQuestionFields", {}, props)

  const form = useContext(InterviewFormContext)

  const { classes, cx } = questionFieldsStyles(undefined, {
    name: "OESIQuestionFields",
    classNames,
    styles,
    unstyled,
  })

  if (!form) {
    return
  }

  return (
    <Box className={cx(classes.root, className)} {...other}>
      <ObjectField
        state={form.fieldState}
        renderField={(name, child) => (
          <Box key={name} className={classes.item}>
            {child}
          </Box>
        )}
        required
      />
    </Box>
  )
})
