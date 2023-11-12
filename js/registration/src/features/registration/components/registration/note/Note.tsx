import { Textarea, TextareaProps, useProps } from "@mantine/core"
import {
  Markdown,
  MarkdownProps,
} from "@open-event-systems/interview-components"
import clsx from "clsx"

export type NoteProps = {
  value?: string
  onChange?: (v: string) => void
}

export const Note = (props: NoteProps) => {
  const { value, onChange } = useProps("Note", {}, props)

  if (onChange) {
    return (
      <Note.Edit
        value={value}
        onChange={(e) => {
          onChange(e.target.value)
        }}
      />
    )
  } else {
    return <Note.View content={value} />
  }
}

export type NoteViewProps = MarkdownProps

const NoteView = (props: NoteViewProps) => {
  const { className, ...other } = useProps("NoteView", {}, props)

  return <Markdown className={clsx("NoteView-view", className)} {...other} />
}

export type NoteEditProps = TextareaProps

const NoteEdit = (props: NoteEditProps) => {
  const { className, ...other } = useProps("NoteEdit", {}, props)

  return (
    <Textarea
      className={clsx("NoteEdit-edit", className)}
      minRows={2}
      maxRows={10}
      autosize
      {...other}
    />
  )
}

Note.View = NoteView
Note.Edit = NoteEdit
