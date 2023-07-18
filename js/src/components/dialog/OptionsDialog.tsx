import { Dialog, DialogProps } from "#src/components/dialog/Dialog.js"
import {
  DialogMenu,
  DialogMenuItem,
} from "#src/components/dialog/DialogMenu.js"
import { ComponentPropsWithRef, ElementType } from "react"

export interface OptionsDialogOption {
  id: string
  label?: string
  itemProps?: Partial<ComponentPropsWithRef<typeof DialogMenuItem<ElementType>>>
}

export type OptionsDialogProps = {
  children?: OptionsDialogOption[]
  onSelect?: (id: string, option: OptionsDialogOption) => void
} & Omit<DialogProps, "children">

export const OptionsDialog = (props: OptionsDialogProps) => {
  const { children = [], onSelect, ...other } = props

  return (
    <Dialog noPadding {...other}>
      <DialogMenu>
        {children.map((opt) => (
          <DialogMenuItem<ElementType>
            key={opt.id}
            label={opt.label || opt.id}
            onClick={() => {
              onSelect && onSelect(opt.id, opt)
            }}
            {...opt.itemProps}
          />
        ))}
      </DialogMenu>
    </Dialog>
  )
}
