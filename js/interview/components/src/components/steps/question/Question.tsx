import {
  ButtonField,
  ButtonFieldProps,
} from "#src/components/fields/button/ButtonField.js"
import {
  ObjectField,
  ObjectFieldProps,
} from "#src/components/fields/object/ObjectField.js"
import { Markdown, MarkdownProps } from "#src/components/markdown/Markdown.js"
import { useProps } from "@mantine/core"
import { FieldState, ObjectFieldState } from "@open-event-systems/interview-lib"
import clsx from "clsx"

export type QuestionProps = {
  fieldsState: ObjectFieldState
  buttonsState: FieldState<string>
  classNames?: {
    root?: string
    text?: string
    fields?: string
    buttons?: string
  }
} & Omit<QuestionRootProps, "children">

export const Question = (props: QuestionProps) => {
  const { fieldsState, buttonsState, classNames, ...other } = useProps(
    "OESIQuestion",
    {},
    props,
  )

  return (
    <Question.Root className={classNames?.root} {...other}>
      <Question.Text
        className={classNames?.text}
        content={fieldsState.schema.description}
      />
      <Question.Fields className={classNames?.fields} state={fieldsState} />
      <Question.Buttons className={classNames?.buttons} state={buttonsState} />
    </Question.Root>
  )
}

export type QuestionRootProps = JSX.IntrinsicElements["form"]

const QuestionRoot = (props: QuestionRootProps) => {
  const { className, children, ...other } = useProps(
    "OESIQuestionRoot",
    {},
    props,
  )
  return (
    <form className={clsx(className, "OESIQuestion-root")} {...other}>
      {children}
    </form>
  )
}

export type QuestionTextProps = MarkdownProps

const QuestionText = (props: QuestionTextProps) => {
  const { className, ...other } = useProps("OESIQuestionText", {}, props)

  return (
    <Markdown className={clsx(className, "OESIQuestion-text")} {...other} />
  )
}

export type QuestionFieldsProps = ObjectFieldProps

export const QuestionFields = (props: QuestionFieldsProps) => {
  const { className, ...other } = useProps("OESIQuestionFields", {}, props)

  return (
    <ObjectField
      className={clsx(className, "OESIQuestion-fields")}
      {...other}
    />
  )
}

export type QuestionButtonsProps = ButtonFieldProps

const QuestionButtons = (props: ButtonFieldProps) => {
  const { className, ...other } = useProps("OESIQuestionButtons", {}, props)

  return (
    <ButtonField
      className={clsx(className, "OESIQuestion-buttons")}
      {...other}
    />
  )
}

Question.Root = QuestionRoot
Question.Text = QuestionText
Question.Fields = QuestionFields
Question.Buttons = QuestionButtons
