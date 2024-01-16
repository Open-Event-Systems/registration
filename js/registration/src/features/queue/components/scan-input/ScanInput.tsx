import { TextInput } from "@mantine/core"
import { ComponentPropsWithoutRef, Ref, useState } from "react"

export type ScanInputProps = Omit<
  ComponentPropsWithoutRef<"form">,
  "onSubmit"
> & {
  onScan?: (value: string) => void
  inputRef?: Ref<HTMLInputElement>
}

export const ScanInput = (props: ScanInputProps) => {
  const { onScan, inputRef, ...other } = props
  const [scanValue, setScanValue] = useState("")
  const [value, setValue] = useState("")
  return (
    <form
      className="ScanInput-root"
      onSubmit={(e) => {
        e.preventDefault()
        const newScanValue = scanValue + value + "\n"
        setScanValue(newScanValue)
        setValue("")

        const isIdStr = newScanValue.slice(0, 1) == "@"
        const finished =
          !isIdStr || (newScanValue.length > 4 && newScanValue.endsWith("\n\n"))
        if (finished) {
          onScan && onScan(newScanValue)
          setScanValue("")
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
        }}
        ref={inputRef}
      />
      <button type="submit" className="ScanInput-submit"></button>
    </form>
  )
}
