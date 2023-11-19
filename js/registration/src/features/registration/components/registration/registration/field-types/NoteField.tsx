import { createField } from "#src/features/registration/components/registration/registration/field-types/Base"
import { Textarea } from "@mantine/core"
import { Markdown } from "@open-event-systems/interview-components"

export const NoteField = createField<string>(
  ({ label, value, setValue }) => {
    return (
      <Textarea
        aria-label={label}
        minRows={1}
        maxRows={10}
        autosize
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
    )
  },
  ({ value }) => <Markdown content={value} />,
)
