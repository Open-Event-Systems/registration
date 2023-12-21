import { useCheckout } from "#src/features/checkout/hooks"
import { Box, Button, Stack, Text } from "@mantine/core"
import { observer } from "mobx-react-lite"
import { FormEvent } from "react"

export const SquareTerminalCheckoutComponent = observer(() => {
  const { update } = useCheckout()

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    update()
  }

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Stack>
        <Text component="p">
          Complete the transaction on the connected Square Terminal, then click
          Complete.
        </Text>
        <Button type="submit" variant="filled">
          Complete
        </Button>
      </Stack>
    </Box>
  )
})

SquareTerminalCheckoutComponent.displayName = "SquareTerminalCheckoutComponent"
