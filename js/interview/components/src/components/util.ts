import { FormPath, FormState } from "@open-event-systems/interview-lib"
import { useReducer } from "react"

export const useValue = <T>(
  formState: FormState,
  path: FormPath,
): [T | null | undefined, (newValue: unknown) => void] => {
  const reducer = (
    curValue: [FormState, FormPath, unknown],
    action: unknown,
  ): [FormState, FormPath, unknown] => {
    const [formState, path] = curValue

    formState.setValue(path, action)

    return [formState, path, action]
  }

  const getInitialValue = (
    action: [FormState, FormPath, unknown],
  ): [FormState, FormPath, unknown] => {
    const [formState, path] = action
    return [formState, path, formState.getValue(path)]
  }

  const [curValue, dispatch] = useReducer(
    reducer,
    [formState, path, undefined],
    getInitialValue,
  )
  const [_f, _p, val] = curValue
  return [val as T | null | undefined, dispatch]
}
