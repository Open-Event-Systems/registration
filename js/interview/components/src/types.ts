import { FormPath, FormState } from "@open-event-systems/interview-lib"

export type FieldProps = {
  state: FormState
  path: FormPath
  required?: boolean
}
