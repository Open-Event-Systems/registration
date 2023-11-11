import { getOptions } from "#src/components/fields/select/util"
import { Button, ButtonProps, Group, GroupProps, useProps } from "@mantine/core"
import { FieldState } from "@open-event-systems/interview-lib"
import { observer } from "mobx-react-lite"

export type ButtonFieldProps = {
  state: FieldState<string>
  onClick?: (value: string) => void
  ButtonProps?: Partial<ButtonProps>
} & Omit<GroupProps, "children" | "onClick">

export const ButtonField = observer((props: ButtonFieldProps) => {
  const { state, onClick, ButtonProps, ...other } = useProps(
    "OESIButtonField",
    {},
    props,
  )

  const options = getOptions(state.schema)

  const buttons = options.map((opt) => (
    <Button
      key={opt.value}
      classNames={{
        root: "OESIButtonField-button",
      }}
      variant={opt.primary ? "filled" : "outline"}
      type={opt.default ? "submit" : "button"}
      {...ButtonProps}
      onClick={(e) => {
        e.preventDefault()

        state.setValue(opt.value)

        onClick && onClick(opt.value)
      }}
    >
      {opt.label}
    </Button>
  ))

  return (
    <Group
      classNames={{
        root: "OESIButtonField-root",
      }}
      {...other}
    >
      {buttons}
    </Group>
  )
})

ButtonField.displayName = "ButtonField"
