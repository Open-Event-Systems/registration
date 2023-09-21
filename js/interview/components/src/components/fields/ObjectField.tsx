import { getComponentForField } from "#src/components/componentTypes.js"
import { FieldProps } from "#src/types.js"
import { Box } from "@mantine/core"
import { ObjectFieldState, Schema } from "@open-event-systems/interview-lib"
import { observer } from "mobx-react-lite"
import { ReactNode } from "react"

export type ObjectFieldProps = FieldProps & {
  renderField?: (name: string, child: ReactNode, schema: Schema) => ReactNode
}

export const ObjectField = observer((props: ObjectFieldProps) => {
  const { renderField = defaultRenderField } = props

  const state = props.state as ObjectFieldState

  const required = state.schema.required ?? []

  if (state.properties == null) {
    return null
  } else {
    return Object.entries(state.properties)
      .map(([key, propState]) => {
        const Component = getComponentForField(propState.schema)

        if (!Component) {
          return null
        }

        return renderField(
          key,
          <Component state={propState} required={required.includes(key)} />,
          propState.schema,
        )
      })
      .filter((obj) => obj != null)
  }
})

ObjectField.displayName = "ObjectField"

const defaultRenderField = (
  name: string,
  child: ReactNode,
  schema: Schema,
): ReactNode => <Box key={name}>{child}</Box>
