import {
  Button,
  ButtonProps,
  createStyles,
  DefaultProps,
  Group,
  GroupProps,
  Selectors,
  useComponentDefaultProps,
} from "@mantine/core"
import { observer } from "mobx-react-lite"
import { MouseEvent, useContext } from "react"
import { InterviewFormContext } from "#src/components/form/Form.js"
import {
  FieldState,
  ObjectFieldState,
  Schema,
} from "@open-event-systems/interview-lib"
import { action } from "mobx"

const buttonStyles = createStyles({
  root: {},
  primary: {},
  default: {},
})

export type FormButtonProps = {
  /**
   * The field state for the button group.
   */
  state?: FieldState

  /**
   * The individual button schema.
   */
  schema: Schema

  /**
   * Override whether this is the default button.
   */
  default?: boolean
} & DefaultProps<Selectors<typeof buttonStyles>> &
  Omit<ButtonProps, "children">

/**
 * A button in an interview question form.
 */
export const FormButton = observer((props: FormButtonProps) => {
  const {
    styles,
    unstyled,
    className,
    classNames,
    state,
    schema,
    default: default_,
    ...other
  } = useComponentDefaultProps("OESIFormButton", {}, props)

  const { classes, cx } = buttonStyles(undefined, {
    name: "OESIFormButton",
    classNames,
    styles,
    unstyled,
  })

  const isDefault =
    default_ ||
    (!!state?.schema.default && schema.const == state.schema.default)

  const form = useContext(InterviewFormContext)

  return (
    <Button
      className={cx(
        classes.root,
        isDefault && classes.default,
        !!schema["x-primary"] && classes.primary,
        className,
      )}
      variant={schema["x-primary"] ? "filled" : "outline"}
      disabled={!!form && form.submitting}
      {...other}
      type={isDefault ? "submit" : "button"}
      onClick={action((e: MouseEvent) => {
        if (state) {
          state.value = schema.const
        }

        const formEl = form?.formEl

        if (!isDefault) {
          e.preventDefault()

          if (formEl) {
            triggerSubmit(formEl)
          }
        }
      })}
    >
      {schema.title}
    </Button>
  )
})

FormButton.displayName = "FormButton"

// workaround to trigger form's onSubmit
const triggerSubmit = (el: HTMLElement) => {
  const buttonEl = document.createElement("button")
  buttonEl.style.display = "none"
  buttonEl.setAttribute("type", "submit")
  el.appendChild(buttonEl)
  buttonEl.click()
  el.removeChild(buttonEl)
}

const buttonsStyles = createStyles({
  root: {
    justifyContent: "flex-end",
  },
})

export type FormButtonsProps = DefaultProps<Selectors<typeof buttonStyles>> &
  Omit<GroupProps, "children">

/**
 * Display the button(s) in an interview question form.
 */
export const FormButtons = (props: FormButtonsProps) => {
  const { styles, unstyled, className, classNames, ...other } =
    useComponentDefaultProps("OESIFormButtons", {}, props)

  const { classes, cx } = buttonsStyles(undefined, {
    name: "OESIFormButtons",
    styles,
    unstyled,
    classNames,
  })

  const form = useContext(InterviewFormContext)
  const fieldState = form?.fieldState as ObjectFieldState | undefined

  const fields = form?.fieldState.schema.properties
  const buttons = fields
    ? Object.entries(fields).filter(([_k, f]) => f["x-type"] == "button")
    : []

  const button = buttons[0]
  const buttonField = button ? button[0] : undefined
  const buttonSchema = button ? button[1] : undefined
  const buttonState =
    buttonField && fieldState?.properties
      ? fieldState.properties[buttonField]
      : undefined

  let content

  if (buttonState && buttonSchema) {
    content = buttonSchema.oneOf?.map((b) => (
      <FormButton key={`${b.const}`} schema={b} state={buttonState} />
    ))
  } else {
    content = (
      <FormButton
        schema={{
          const: "1",
          title: "Next",
          "x-primary": true,
        }}
        default
      />
    )
  }

  return (
    <Group className={cx(classes.root, className)} {...other}>
      {content}
    </Group>
  )
}
