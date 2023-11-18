import { SearchContext } from "#src/features/registration/stores/search2"
import {
  Checkbox,
  CheckboxProps,
  Grid,
  GridProps,
  Select,
  SelectProps,
  TextInput,
  TextInputProps,
} from "@mantine/core"
import { IconSearch } from "@tabler/icons-react"
import { action } from "mobx"
import { observer } from "mobx-react-lite"
import { useContext } from "react"

export type InputProps = {
  TextInputProps?: Partial<TextInputProps>
  SelectProps?: Partial<SelectProps>
  CheckboxProps?: Partial<CheckboxProps>
} & GridProps

export const Input = (props: InputProps) => {
  const { TextInputProps, SelectProps, CheckboxProps, ...other } = props
  return (
    <Grid align="center" {...other}>
      <Grid.Col span={{ base: 12, sm: "auto" }} order={{ base: 3, sm: 1 }}>
        <Input.Query {...TextInputProps} />
      </Grid.Col>
      <Grid.Col span={{ base: 6, sm: "content" }} order={{ base: 1, sm: 2 }}>
        <Input.EventSelect {...SelectProps} />
      </Grid.Col>
      <Grid.Col span="content" order={{ base: 2, sm: 3 }}>
        <Input.ShowAll {...CheckboxProps} />
      </Grid.Col>
    </Grid>
  )
}

Input.Query = observer((props: TextInputProps) => {
  const ctx = useContext(SearchContext)

  return (
    <TextInput
      title="Search"
      placeholder="Search"
      leftSection={<IconSearch />}
      value={ctx?.query}
      onChange={action((e) => ctx && (ctx.query = e.target.value))}
      {...props}
    />
  )
})

Input.Query.displayName = "RegistrationSearchQuery"

Input.EventSelect = observer((props: SelectProps) => {
  const ctx = useContext(SearchContext)
  return (
    <Select
      title="Event"
      placeholder="Event"
      value={ctx?.eventId}
      onChange={action((v) => ctx && (ctx.eventId = v))}
      {...props}
    />
  )
})

Input.EventSelect.displayName = "RegistrationSearchEventSelect"

Input.ShowAll = observer((props: CheckboxProps) => {
  const ctx = useContext(SearchContext)
  return (
    <Checkbox
      label="Show All"
      title="Show pending and canceled registrations"
      checked={ctx?.showAll}
      onChange={action((e) => ctx && (ctx.showAll = e.target.checked))}
      {...props}
    />
  )
})

Input.ShowAll.displayName = "RegistrationSearchShowAll"
