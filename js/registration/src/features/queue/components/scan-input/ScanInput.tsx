import { TextInput } from "@mantine/core"
import { ComponentPropsWithoutRef, Ref, useRef, useState } from "react"

export type ScanInputProps = Omit<
  ComponentPropsWithoutRef<"form">,
  "onSubmit"
> & {
  onScan?: (value: string) => void
  inputRef?: Ref<HTMLInputElement>
}

export const ScanInput = (props: ScanInputProps) => {
  const { onScan, inputRef, ...other } = props
  const buffer = useRef("")
  const timeout = useRef<number | null>(null)
  const [value, setValue] = useState("")
  return (
    <form
      className="ScanInput-root"
      onSubmit={(e) => {
        e.preventDefault()

        let curValue = value

        if (curValue.startsWith("@") && buffer.current) {
          onScan && onScan(buffer.current)
          buffer.current = ""
        }

        buffer.current = buffer.current + "\n" + curValue

        if (
          buffer.current.startsWith("@") &&
          buffer.current.length > 4 &&
          buffer.current.endsWith("\n\n")
        ) {
          onScan && onScan(buffer.current)
          buffer.current = ""
        }
      }}
      {...other}
    >
      <TextInput
        size="xs"
        value={value}
        autoFocus
        placeholder="Scan..."
        onChange={(e) => {
          setValue(e.target.value)
          if (timeout.current) {
            window.clearTimeout(timeout.current)
          }

          timeout.current = window.setTimeout(() => {
            if (buffer.current.startsWith("@")) {
              onScan && onScan(buffer.current)
              buffer.current = ""
            }
          }, 200)
        }}
        ref={inputRef}
      />
      <button type="submit" className="ScanInput-submit"></button>
    </form>
  )
}
