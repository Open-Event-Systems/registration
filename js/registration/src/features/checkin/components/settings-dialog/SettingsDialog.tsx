import { StationSettings } from "#src/features/queue/types"
import {
  Button,
  Group,
  Modal,
  ModalProps,
  NumberInput,
  Select,
  Stack,
  TagsInput,
  TextInput,
} from "@mantine/core"
import { useLayoutEffect, useState } from "react"

export type SettingsDialogProps = {
  settings: StationSettings
  stationIds: string[]
  onChange?: (settings: StationSettings) => void
} & Omit<ModalProps, "children" | "onChange">

export const SettingsDialog = (props: SettingsDialogProps) => {
  const { settings, onChange, stationIds, ...other } = props

  const [workingSettings, setWorkingSettings] = useState<StationSettings>({
    ...settings,
  })

  useLayoutEffect(() => {
    setWorkingSettings({ ...settings })
  }, [settings])

  return (
    <Modal title="Settings" {...other}>
      <Stack>
        <NumberInput
          label="Max Queue Length"
          min={0}
          value={workingSettings.max_queue_length || 0}
          onChange={(v) => {
            if (typeof v == "number") {
              setWorkingSettings({ ...workingSettings, max_queue_length: v })
            }
          }}
        />
        <TagsInput
          label="Tags"
          value={workingSettings.tags}
          onChange={(tags) => {
            setWorkingSettings({ ...workingSettings, tags: tags })
          }}
        />
        <Select
          label="Delegate Printing"
          value={workingSettings.delegate_print_station || null}
          data={stationIds.map((id) => ({
            label: `Station ${id}`,
            value: id,
          }))}
          onChange={(e) => {
            setWorkingSettings({
              ...workingSettings,
              delegate_print_station: e ?? undefined,
            })
          }}
        />
        <TextInput
          label="Auto Print URL"
          value={workingSettings.auto_print_url || ""}
          onChange={(e) => {
            const value = e.target.value
            setWorkingSettings({
              ...workingSettings,
              auto_print_url: value || undefined,
            })
          }}
        />
        <Group justify="flex-end">
          <Button
            onClick={() => {
              onChange && onChange({ ...workingSettings })
            }}
          >
            Save
          </Button>
        </Group>
      </Stack>
    </Modal>
  )
}
