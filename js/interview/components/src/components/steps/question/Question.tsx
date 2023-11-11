import {
  ButtonField,
  ButtonFieldProps,
} from "#src/components/fields/button/ButtonField"
import {
  ObjectField,
  ObjectFieldProps,
} from "#src/components/fields/object/ObjectField"
import { Markdown, MarkdownProps } from "#src/components/markdown/Markdown"
import { Button, ButtonProps, useProps } from "@mantine/core"
import { FieldState, ObjectFieldState } from "@open-event-systems/interview-lib"
import clsx from "clsx"
import { ComponentPropsWithoutRef } from "react"

export type QuestionProps = {
  fieldsState: ObjectFieldState
  buttonsState?: FieldState<string>
  onSubmit?: () => void
  classNames?: {
    root?: string
    text?: string
    fields?: string
    defaultButton?: string
    buttons?: string
  }
} & Omit<QuestionRootProps, "children" | "onSubmit">

export const Question = (props: QuestionProps) => {
  const {
    fieldsState,
    buttonsState,
    className,
    classNames,
    onSubmit,
    ...other
  } = useProps("OESIQuestion", {}, props)

  return (
    <Question.Root
      className={clsx(classNames?.root, className)}
      {...other}
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit && onSubmit()
      }}
    >
      <Question.Text
        className={classNames?.text}
        content={fieldsState.schema.description}
      />
      <Question.Fields className={classNames?.fields} state={fieldsState} />
      {buttonsState ? (
        <Question.Buttons
          className={classNames?.buttons}
          state={buttonsState}
          onClick={() => {
            onSubmit && onSubmit()
          }}
        />
      ) : (
        <Question.DefaultButton className={classNames?.defaultButton} />
      )}
    </Question.Root>
  )
}

export type QuestionRootProps = ComponentPropsWithoutRef<"form">

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

export type QuestionDefaultButtonProps = ButtonProps &
  ComponentPropsWithoutRef<"button">

const QuestionDefaultButton = (props: QuestionDefaultButtonProps) => {
  const { className, ...other } = useProps(
    "OESIQuestionDefaultButton",
    {},
    props,
  )

  return (
    <Button
      className={clsx(className, "OESIQuestion-defaultButton")}
      type="submit"
      variant="filled"
      {...other}
    >
      Next
    </Button>
  )
}

export type QuestionButtonsProps = ButtonFieldProps

const QuestionButtons = (props: ButtonFieldProps) => {
  const { className, ...other } = useProps("OESIQuestionButtons", {}, props)

  return (
    <ButtonField
      className={clsx(className, "OESIQuestion-buttons")}
      justify="flex-end"
      {...other}
    />
  )
}

Question.Root = QuestionRoot
Question.Text = QuestionText
Question.Fields = QuestionFields
Question.DefaultButton = QuestionDefaultButton
Question.Buttons = QuestionButtons
