import {
  Box,
  createStyles,
  DefaultProps,
  Selectors,
  useComponentDefaultProps,
} from "@mantine/core"
import {
  createState,
  FieldState,
  FormValues,
  Schema,
} from "@open-event-systems/interview-lib"
import { action, runInAction } from "mobx"
import { observer, useLocalObservable } from "mobx-react-lite"
import {
  createContext,
  FormHTMLAttributes,
  ReactNode,
  useCallback,
} from "react"

const formStyles = createStyles(() => ({
  root: {},
}))

export interface InterviewFormState {
  submitting: boolean
  fieldState: FieldState
  formEl: HTMLFormElement | null
}

export type InterviewFormProps = {
  /**
   * The question schema.
   */
  schema: Schema

  /**
   * An object of initial values for the fields.
   */
  initialValues?: FormValues

  /**
   * The submit handler.
   */
  onSubmit: (values: FormValues) => Promise<void>

  children?: ReactNode
} & DefaultProps<Selectors<typeof formStyles>> &
  Omit<FormHTMLAttributes<HTMLFormElement>, "onSubmit" | "children">

/**
 * A component that manages the state of fields in an interview question.
 *
 * Renders children inside a <form> and manages its submit events.
 *
 * Provides the state as {@link InterviewFormContext}.
 */
export const InterviewForm = observer((props: InterviewFormProps) => {
  const {
    styles,
    unstyled,
    className,
    classNames,
    schema,
    initialValues,
    onSubmit,
    children,
    ...other
  } = useComponentDefaultProps("InterviewForm", {}, props)

  const { classes, cx } = formStyles(undefined, {
    name: "InterviewForm",
    classNames,
    styles,
    unstyled,
  })

  const state = useLocalObservable((): InterviewFormState => {
    const fieldState = createState(schema)

    fieldState.value = initialValues ?? {}

    return {
      submitting: false,
      fieldState,
      formEl: null as HTMLFormElement | null,
    }
  })

  const setRef = useCallback(
    action((ref: HTMLFormElement | null) => {
      state.formEl = ref
    }),
    [state],
  )

  const handleSubmit = action(async () => {
    // set state to touched
    state.fieldState.touched = true

    if (state.submitting || !state.fieldState.isValid) {
      return
    }

    state.submitting = true

    try {
      await onSubmit(state.fieldState.validValue as FormValues)
    } catch (_e) {
      runInAction(() => {
        state.submitting = false
      })
    }
  })

  return (
    <Box
      component="form"
      className={cx(classes.root, className)}
      {...other}
      onSubmit={(e) => {
        e.preventDefault()
        handleSubmit()
      }}
      ref={setRef}
    >
      <InterviewFormContext.Provider value={state}>
        {children}
      </InterviewFormContext.Provider>
    </Box>
  )
})

InterviewForm.displayName = "InterviewForm"

export const InterviewFormContext = createContext<InterviewFormState | null>(
  null,
)
