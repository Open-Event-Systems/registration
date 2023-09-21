import { FieldProps } from "#src/types.js"
import { getComponentForField } from "#src/components/componentTypes.js"

/**
 * Renders the appropriate component for a field.
 */
export const Field = (props: FieldProps) => {
  try {
    const Component = getComponentForField(props.state.schema)
    return Component ? <Component {...props} /> : null
  } catch (_) {
    return null
  }
}
