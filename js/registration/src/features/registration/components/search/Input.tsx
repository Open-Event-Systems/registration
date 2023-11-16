import { TextInput, TextInputProps } from "@mantine/core"
import { IconSearch } from "@tabler/icons-react"
import clsx from "clsx"

export type InputProps = TextInputProps

export const Input = (props: TextInputProps) => {
  const { className, ...other } = props

  return (
    <TextInput
      className={clsx("RegistrationSearchInput-root", className)}
      placeholder="Search"
      leftSection={<IconSearch />}
      {...other}
    />
  )
}
