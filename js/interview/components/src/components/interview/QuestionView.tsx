import {
  createStyles,
  DefaultProps,
  Selectors,
  Stack,
  StackProps,
  useComponentDefaultProps,
} from "@mantine/core"
import {
  AskResult,
  FormValues,
  Schema,
} from "@open-event-systems/interview-lib"
import { InterviewForm } from "#src/components/form/Form.js"
import {
  FormButtons,
  FormButtonsProps,
} from "#src/components/form/FormButtons.js"
import {
  QuestionFields,
  QuestionFieldsProps,
} from "#src/components/form/QuestionFields.js"
import { Markdown } from "#src/components/Markdown.js"

const questionStyles = createStyles((theme) => ({
  root: {
    display: "grid",
    grid: `
      "description" auto
      "fields" auto
      "." 1fr
      "buttons" auto
      / 1fr
    `,
    justifyItems: "stretch",
    rowGap: theme.spacing.sm,
  },
  markdown: {
    gridArea: "description",
  },
  questionFields: {
    gridArea: "fields",
  },
  buttons: {
    gridArea: "buttons",
  },
}))

export type QuestionViewProps = {
  /**
   * The {@link AskResult} to display.
   */
  content: AskResult

  /**
   * Initial values.
   */
  initialValues?: FormValues

  /**
   * Props passed to the {@link QuestionFields} component.
   */
  QuestionFieldsProps?: Partial<QuestionFieldsProps>

  /**
   * Props passed to the {@link FormButtons} component.
   */
  FormButtonsProps?: Partial<FormButtonsProps>

  /**
   * The submit handler for the form.
   */
  onSubmit: (values: FormValues) => Promise<void>
} & DefaultProps<Selectors<typeof questionStyles>>

/**
 * Display the form, description, inputs, and buttons for a {@link AskResult}.
 */
export const QuestionView = (props: QuestionViewProps) => {
  const {
    styles,
    unstyled,
    className,
    classNames,
    content,
    initialValues,
    QuestionFieldsProps,
    FormButtonsProps,
    onSubmit,
    ...other
  } = useComponentDefaultProps("OESIQuestionView", {}, props)

  const { classes, cx } = questionStyles(undefined, {
    name: "OESIQuestionView",
    styles,
    unstyled,
    classNames,
  })

  const schema = content.schema as Schema

  return (
    <InterviewForm
      className={cx(classes.root, className)}
      schema={schema}
      initialValues={initialValues}
      {...other}
      onSubmit={onSubmit}
    >
      <Markdown className={classes.markdown}>
        {schema.description || ""}
      </Markdown>
      <QuestionFields
        className={classes.questionFields}
        {...QuestionFieldsProps}
      />
      <FormButtons className={classes.buttons} {...FormButtonsProps} />
    </InterviewForm>
  )
}
