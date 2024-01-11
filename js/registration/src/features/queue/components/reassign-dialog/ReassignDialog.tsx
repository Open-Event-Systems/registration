import { Modal, ModalProps, Select } from "@mantine/core"

export type ReassignDialogProps = Omit<ModalProps, "onSelect"> & {
  options: string[]
  onSelect?: (id: string) => void
}

export const ReassignDialog = (props: ReassignDialogProps) => {
  const { options, onSelect, ...other } = props

  return (
    <Modal title="Reassign" {...other}>
      <Select
        label="Station"
        data={options.map((o) => ({
          label: o,
          value: o,
        }))}
        onChange={(v) => {
          !!v && onSelect && onSelect(v)
        }}
      />
    </Modal>
  )
}
