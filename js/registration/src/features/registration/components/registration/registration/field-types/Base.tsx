import { Event } from "#src/features/event/types"
import { Registration } from "#src/features/registration"
import { action } from "mobx"
import { observer } from "mobx-react-lite"
import { ComponentType, createContext, useContext } from "react"

export type FieldProps = {
  name: string
  label?: string
  editable?: boolean
}

export type FieldEditProps<T> = {
  label?: string
  event?: Event
  value?: T
  setValue: (value: T | undefined) => void
}

export type FieldViewProps<T> = {
  event?: Event
  value?: T
}

export const createField = <T,>(
  EditComponent: ComponentType<FieldEditProps<T>>,
  ViewComponent: ComponentType<FieldViewProps<T>>,
): ComponentType<FieldProps> => {
  const View = observer((props: { name: string }) => {
    const { name } = props
    const [registration, event] = useContext(RegistrationFieldsContext)
    const value = registration && (registration[name] as T)
    return <ViewComponent value={value} event={event} />
  })
  View.displayName = "FieldView"

  const Edit = observer((props: { name: string; label?: string }) => {
    const { name, label } = props
    const [registration, event] = useContext(RegistrationFieldsContext)
    const value = registration && (registration[name] as T)

    const setValue = action((value: T | undefined) => {
      if (registration) {
        if (value !== undefined) {
          registration[name] = value
        } else {
          delete registration[name]
        }
      }
    })

    return (
      <EditComponent
        value={value}
        label={label}
        event={event}
        setValue={setValue}
      />
    )
  })
  Edit.displayName = "FieldEdit"

  const Component = (props: FieldProps) => {
    const { name, label, editable } = props

    if (editable) {
      return <Edit name={name} label={label} />
    } else {
      return <View name={name} />
    }
  }

  return Component
}

export const RegistrationFieldsContext = createContext<
  [Registration, Event | undefined] | [undefined, undefined]
>([undefined, undefined])
