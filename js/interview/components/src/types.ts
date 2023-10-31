import { FieldState } from "@open-event-systems/interview-lib"

export type FieldProps<T> = {
  state: FieldState<T>
  required?: boolean
}
